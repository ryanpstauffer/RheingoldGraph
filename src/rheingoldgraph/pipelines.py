"""RheingoldGraph Pipelines.

This file extends the existing Pipelines from the Magenta Project.
The intent is to separate out and support the following:
- Process source data to protocol buffer NoteSequences.
- Process and encode sequences from the graph so they can be immediately
  used by a TensorFlow model
"""
import tensorflow as tf

from magenta.pipelines import pipeline
from magenta.pipelines import note_sequence_pipelines
from magenta.pipelines import melody_pipelines
from magenta.pipelines import dag_pipeline
from magenta.models.melody_rnn import melody_rnn_create_dataset
from magenta.protobuf import music_pb2
from magenta.music import melodies_lib
from magenta.music import midi_io

class TestExtractor(pipeline.Pipeline):
    def __init__(self):
        super(TestExtractor, self).__init__(
            input_type=int,
            output_type=str,
            name='TestExtractor')

    def transform(self, int_object):
        return str(int_object)

class MelodyToProtoConverter(pipeline.Pipeline):
    """Converts a melody to a sequence proto."""
    def __init__(self, velocity=100, instrument=0, program=0,
                 sequence_start_time=0.0, qpm=120.0, name=None):
        super(MelodyToProtoConverter, self).__init__(
            input_type=melodies_lib.Melody,
            output_type=music_pb2.NoteSequence,
            name=name)
        self._velocity = velocity
        self._instrument = instrument
        self._program = program
        self._sequence_start_time = sequence_start_time
        self._qpm = qpm


    def transform(self, melody):
        try:
            sequence = melody.to_sequence(velocity=self._velocity,
                                          instrument=self._instrument,
                                          program=self._program,
                                          sequence_start_time=self._sequence_start_time,
                                          qpm=self._qpm) 
        except:
             tf.logging.warning('Skipped melody')
        # TODO(ryan): add stats        
        return [sequence]


class MidiToProtoConverter(pipeline.Pipeline):
    """Converts MIDI bytes to NoteSequence protobufs.

    Utilizes code found in magenta.scripts.convert_dir_to_note_sequences.convert_midi()
    """

    def __init__(self, name=None):
        super(MidiToProtoConverter, self).__init__(
            input_type=bytes,
            output_type=music_pb2.NoteSequence,
            name=name)
    
    def transform(self, midi_bytes):
        try:
            sequence = [midi_io.midi_to_sequence_proto(midi_bytes)]
        except midi_io.MIDIConversionError as e:
            tf.logging.warning('Could not parse MIDI bytes. Error was: %s', e)
            sequence = []
       # TODO(ryan): add stats
        return sequence  

# I don't think I need this anymore...
def get_sequence_to_seq_example_pipeline(config):
    """Returns a DAGPipeline that creates a sequence example from a NoteSequence.

    Args:
        config: A MelodyRnnConfig object.

    Returns:
        dag_pipeline.DAGPipeline object.
    """
    # Need to figure out how to handle partitions....
    time_change_splitter = note_sequence_pipelines.TimeChangeSplitter(
        name='TimeChangeSplitter')
    quantizer = note_sequence_pipelines.Quantizer(
        steps_per_quarter=config.steps_per_quarter, name='Quantizer')
    # Same MelodyExtractor parameters as melody_rnn_create_dataset
    melody_extractor = melody_pipelines.MelodyExtractor(
        min_bars=7, max_steps=512, min_unique_pitches=5,
        gap_bars=1.0, ignore_polyphonic_notes=True,
        name='MelodyExtractor')
    encoder_pipeline = melody_rnn_create_dataset.EncoderPipeline(config, name='EncoderPipeline')

    dag = {time_change_splitter: dag_pipeline.DagInput(music_pb2.NoteSequence),
           quantizer: time_change_splitter,
           melody_extractor: quantizer,
           encoder_pipeline: melody_extractor,
           dag_pipeline.DagOutput('sequence_example'): encoder_pipeline}

    return dag_pipeline.DAGPipeline(dag)

    
def get_midi_to_melody_proto_pipeline(config):
    """Returns a DAGPipeline that creates a melody NoteSequence from a MIDI file.

    Args:
        config: A MelodyRnnConfig object.

    Returns:
        dag_pipeline.DAGPipeline object.
    """
    # TimeChangeSplitter is useful for an MVP
    midi_to_proto_converter = MidiToProtoConverter(name='MidiToProtoConverter')
    time_change_splitter = note_sequence_pipelines.TimeChangeSplitter(
        name='TimeChangeSplitter')
    quantizer = note_sequence_pipelines.Quantizer(
        steps_per_quarter=config.steps_per_quarter, name='Quantizer')
    # Same MelodyExtractor parameters as melody_rnn_create_dataset
    melody_extractor = melody_pipelines.MelodyExtractor(
        min_bars=7, max_steps=512, min_unique_pitches=5,
        gap_bars=1.0, ignore_polyphonic_notes=True,
        name='MelodyExtractor')
    melody_to_proto_converter = MelodyToProtoConverter(
        velocity=100, instrument=0, program=0, sequence_start_time=0.0,
        qpm=120.0, name='MelodyToProtoConverter')

    dag = {midi_to_proto_converter: dag_pipeline.DagInput(bytes),
           time_change_splitter: midi_to_proto_converter,
           quantizer: time_change_splitter,
           melody_extractor: quantizer,
           melody_to_proto_converter: melody_extractor,
           dag_pipeline.DagOutput('melody_sequence'): melody_to_proto_converter}

    return dag_pipeline.DAGPipeline(dag)
