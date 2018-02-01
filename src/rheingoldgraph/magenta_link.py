"""Initial work on linking Magenta/TF with RheingoldGraph."""
import os

from rheingoldgraph.process import Session

import magenta
from magenta.protobuf import generator_pb2
from magenta.models.melody_rnn import melody_rnn_model
from magenta.models.melody_rnn import melody_rnn_sequence_generator

if __name__ == "__main__":
    print('Test of Gremlin/Magenta interface.')
    server_uri = 'ws://localhost:8182/gremlin'
    
    session = Session(server_uri)

    # Save a primer melody
    primer_midi = '/Users/ryanstauffer/Projects/Rheingold/RheingoldGraph/bach.mid'
    session.save_line_to_midi('bach_cello', 120, primer_midi, excerpt_len=11)

    # Magenta config build
    config = melody_rnn_model.default_configs['basic_rnn']
    
    model = melody_rnn_model.MelodyRnnModel(config)

    bundle_file = '/Users/ryanstauffer/Projects/Rheingold/magenta_data/mag/basic_rnn.mag'
    bundle = magenta.music.read_bundle_file(bundle_file)   

    output_dir = '/Users/ryanstauffer/Projects/Rheingold/magenta_data/melody_rnn/generated'

    primer_sequence = magenta.music.midi_file_to_sequence_proto(primer_midi)
    # Ignore additional tempo options for now...for simplicity  

    # Derive the total number of seconds to generate based on the QPM of the
    # priming sequence and num_steps

    # Standard default from README
    num_steps = 128

    # There seems to be a weird relationship between my primer QPM and the output...
    quarters_per_minute = 60.0
    seconds_per_step = 60.0 / quarters_per_minute / config.steps_per_quarter
    total_seconds = num_steps * seconds_per_step

    generator_options = generator_pb2.GeneratorOptions()

    # From melody_rnn_generate line 174
    input_sequence = primer_sequence
    # Set the start time to being on the next step after the last note ends
    last_end_time = (max(n.end_time for n in primer_sequence.notes)
                     if primer_sequence.notes else 0)
    generate_section = generator_options.generate_sections.add(
        start_time=last_end_time + seconds_per_step,
        end_time=total_seconds)

    # Don't worry about robust error handling now (ex: primer sequence longer than num steps
    generator_options.args['temperature'].float_value = 1.0
    generator_options.args['beam_size'].int_value = 1
    generator_options.args['branch_factor'].int_value = 1
    generator_options.args['steps_per_iteration'].int_value = 1
    
    # Start with generating and saving a single midi file!
    generator = melody_rnn_sequence_generator.MelodyRnnSequenceGenerator(
        model=melody_rnn_model.MelodyRnnModel(config),
        details=config.details,
        steps_per_quarter=config.steps_per_quarter,
        bundle=bundle)
    generated_sequence = generator.generate(input_sequence, generator_options)
   
    new_midi_output = 'magenta_test.mid' 
    midi_path = os.path.join(output_dir, new_midi_output) 

    magenta.music.sequence_proto_to_midi_file(generated_sequence, midi_path) 
