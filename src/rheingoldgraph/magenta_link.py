"""Initial work on linking Magenta/TF with RheingoldGraph."""
from collections import namedtuple

import tensorflow as tf
import magenta
from magenta.protobuf import generator_pb2
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator

from rheingoldgraph.data_processing import convert_midi_dir_to_melody_sequences
from rheingoldgraph.data_processing import _melody_name_and_note_sequence_to_note_sequence_only
from rheingoldgraph.data_processing import encode_sequence_for_melody_rnn


# TODO(ryan): This module may eventually be altered to run off FLAGS,
# Or a protobuf similar to generator options
# But for simplicity right now just using namedtuple
RheingoldMagentaConfig = namedtuple('RheingoldMagentaConfig',
                                    ['num_outputs',
                                     'qpm',
                                     'num_steps'])


def run_with_config(generator, config, primer_sequence=None):
    """Generates melodies and adds them to a RheingoldGraph instance.

    TF & Magenta interaction based on Magenta melody_rnn_generate.py

    Args:
        generator: The MelodyRnnSequenceGenerator to use for melody generation
        config: RheingoldMagentaConfig
        primer_sequence: ProtoBuf NoteSequece
    """
    if not primer_sequence:
        tf.logging.warning(
            'No priming sequence specified. Defaulting to a single middle C.')
        primer_melody = magenta.music.Melody([60])
        primer_sequence = primer_melody.to_sequence(config.qpm)

    # Derive the total number of seconds to generate based on the QPM of the
    # priming sequence and the num_steps flag
    seconds_per_step = 60.0 / config.qpm / generator.steps_per_quarter
    total_seconds = config.num_steps * seconds_per_step

    # Specify start/stop time for generation based on starting generation at the
    # end of the priming sequence and continuing until the sequence is num_steps
    # long.
    generator_options = generator_pb2.GeneratorOptions()
    last_end_time = (max(n.end_time for n in primer_sequence.notes)
                     if primer_sequence.notes else 0)
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    if generate_section.start_time >= generate_section.end_time:
        tf.logging.fatal(
            'Priming sequence is longer than the total number of step '
            'requested: Priming sequence length: %s, Generation length '
            'requested: %s',
            generate_section.start_time, total_seconds)
        return

    generator_options.args['temperature'].float_value = 1.0
    generator_options.args['beam_size'].int_value = 1
    generator_options.args['branch_factor'].int_value = 1
    generator_options.args['steps_per_iteration'].int_value = 1
    tf.logging.debug('primer_sequence: %s', primer_sequence)
    tf.logging.debug('generator_options: %s', generator_options)

    # Make the generate request num_outputs times and return the output
    # to RheingoldGraph
    for i in range(config.num_outputs):
        generated_sequence = generator.generate(primer_sequence, generator_options)
        yield generated_sequence

    tf.logging.info('Generated %d sequences.' % config.num_outputs)


def configure_sequence_generator(trained_model_name, bundle_file):
    """Configure and return a trained sequence generator.

    Additional models will be supported in the future,
    and this configuration tool will become more generalized.

    Args:
        trained_model_name: name of trained model
        bundle_file: filename of magenta bundle file (.mag)
    Returns:
        sequence_generator: a sequence generator to execute
    """
    bundle = magenta.music.read_bundle_file(bundle_file)

    # Model and generator selection
    if trained_model_name == 'melody_rnn_generator':
        melody_rnn_config = melody_rnn_model.default_configs['basic_rnn']
        model = melody_rnn_model.MelodyRnnModel(melody_rnn_config)

        sequence_generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
            model=model,
            details=melody_rnn_config.details,
            steps_per_quarter=melody_rnn_config.steps_per_quarter,
            bundle=bundle)

    else:
        print("Model {0} not supported.".format(trained_model_name))
        return

    return sequence_generator


if __name__ == '__main__':
    input_dir = '/Users/ryan/Projects/Rheingold/midi/new_single_test'

    # midi_file_iterator(input_dir)
    gen = convert_midi_dir_to_melody_sequences(input_dir, False)
    
    # note_sequence_list = [n[1] for n in gen]
    note_sequence_gen = _melody_name_and_note_sequence_to_note_sequence_only(gen)

    # This produces a list of SequenceExamples
    res = encode_sequence_for_melody_rnn(note_sequence_gen, 0.0) 

    seq_example = res[0]
 
    # Putting together code to link SequenceExample w/ Dataset
    melody_rnn_config = melody_rnn_model.default_configs['basic_rnn']
    encoder_decoder = melody_rnn_config.encoder_decoder
    hparams = melody_rnn_config.hparams
    print(hparams)
 
    input_size = encoder_decoder.input_size
    num_classes = encoder_decoder.num_classes
    no_event_label = encoder_decoder.default_event_label

    print(input_size, num_classes, no_event_label) 

    # get_padded_batch() replacement BELOW
    sequence_features = {
        'inputs': tf.FixedLenSequenceFeature(shape=[input_size],
                                             dtype=tf.float32),
        'labels': tf.FixedLenSequenceFeature(shape=[],
                                             dtype=tf.int64)}
    
    _, sequence = tf.parse_single_sequence_example(
        seq_example.SerializeToString(), sequence_features=sequence_features)

    length = tf.shape(sequence['inputs'])[0] 
    input_tensors = [sequence['inputs'], sequence['labels'], length] 
    
    # Note that we obviously only have a single training example here!!!
    # FOR NOW...
    features = sequence['inputs']
    labels = sequence['labels']

    # Convert old QueueRunner technique to Dataset API usage
    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    iterator = dataset.make_one_shot_iterator()
    next_element = iterator.get_next()

    # Iterate through the dataset elements (as an ex)
    with tf.Session() as sess:
        for _ in range(1): 
            print(sess.run(next_element))

    # NEXT STEPS:
    # create new get_padded_batch fn
    # add shuffle, batch


