"""Initial work on linking Magenta/TF with RheingoldGraph."""
import os
import time
from collections import namedtuple

import tensorflow as tf
import magenta
from magenta.protobuf import generator_pb2
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator

from rheingoldgraph.session import Session


# TODO(ryan): This module may eventually be altered to run off FLAGS,
# Or a protobuf similar to generator options
# But for simplicity right now just using namedtuple 
RheingoldMagentaConfig = namedtuple('RheingoldMagentaConfig',
                                   ['primer_line_name',
                                    'primer_len',
                                    'num_outputs',
                                    'qpm',
                                    'num_steps'])

def run_with_config(generator, session, config):
    """Generates melodies and adds them to a RheingoldGraph instance.

    TF & Magenta interaction based on Magenta melody_rnn_generate.py

    Args:
        generator: The MelodyRnnSequencedGenerator to use for melody generation
    """
    # Define a primer line
    # config.primer_line_name = 'bach_cello' 
    # config.primer_len = 11 

    # config.qpm = 120

    primer_sequence = None
    if config.primer_line_name:
        primer_sequence = session.get_line_as_sequence_proto(config.primer_line_name,
                                                             config.qpm,
                                                             excerpt_len=config.primer_len)
    else:
        tf.logging.warning(
            'No priming sequence specified. Defaulting to a single middle C.')
        primer_melody = magenta.music.Melody([60])
        primer_sequence = primer_melody.to_sequence(qpm)

    # num_steps = 128 # FLAG?
    # Derive the total number of seconds to generate based on the QPM of the
    # priming sequence and the num_steps flag
    # TODO(ryan): is this the best way to do this w/ Rheingold Graph?
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

    # TODO(ryan): have these take FLAGS?
    generator_options.args['temperature'].float_value = 1.0
    generator_options.args['beam_size'].int_value = 1
    generator_options.args['branch_factor'].int_value = 1
    generator_options.args['steps_per_iteration'].int_value = 1
    tf.logging.debug('primer_sequence: %s', primer_sequence)
    tf.logging.debug('generator_options: %s', generator_options)

    # Make the generate request num_outputs times and save the output
    # to RheingoldGraph
    # num_outputs = 1
    date_and_time = time.strftime('%Y-%m-%d_%H%M%S')
    digits = len(str(config.num_outputs)) # Take FLAG?
    for i in range(config.num_outputs):   
        generated_sequence = generator.generate(primer_sequence, generator_options)

        line_name = 'magenta_{0}_{1}'.format(date_and_time,
                                             str(i + 1).zfill(digits)) 
        session.add_sequence_proto_to_graph(generated_sequence, line_name)
       
        # Remove play - only for debugging.. 
        session.play_line(line_name, 120)
    tf.logging.info('Wrote %d lines to the graph.' % config.num_outputs)
        

def generate_melody_from_trained_model(session, primer_line_name):
    melody_rnn_config = melody_rnn_model.default_configs['basic_rnn']
    
    bundle_file = '/Users/ryanstauffer/Projects/Rheingold/magenta_data/mag/basic_rnn.mag'
    bundle = magenta.music.read_bundle_file(bundle_file)   

    generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
            model=melody_rnn_model.MelodyRnnModel(melody_rnn_config),
            details=melody_rnn_config.details,
            steps_per_quarter=melody_rnn_config.steps_per_quarter,
            bundle=bundle)
    
    rheingold_magenta_config = RheingoldMagentaConfig(primer_line_name=primer_line_name,
                                                      primer_len=11, num_outputs=1, 
                                                      qpm=120, num_steps=150)    
    run_with_config(generator, session, rheingold_magenta_config)  
    

if __name__ == "__main__":
    print('Test of Gremlin/Magenta interface.')
    server_uri = 'ws://localhost:8182/gremlin'
    
    session = Session(server_uri)
    
    generate_melody_from_trained_model(session, 'bach_cello')
 
