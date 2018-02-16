"""Rheingold implementation of Magenta Pipelines."""
import tensorflow as tf

from magenta.pipelines import pipeline
from magenta.pipelines import note_sequence_pipelines
from magenta.pipelines import melody_pipelines
from magenta.pipelines import dag_pipeline
from magenta.models.melody_rnn import melody_rnn_create_dataset
from magenta.protobuf import music_pb2
from magenta.music import melodies_lib

class TestExtractor(pipeline.Pipeline):
    def __init__(self):
        super(TestExtractor, self).__init__(
            input_type=int,
            output_type=str,
            name='TestExtractor')

    def transform(self, int_object):
        return str(int_object)

class MelodyToProtoConverter(pipeline.Pipeline):
    """Convert a list of melodies to a sequence proto.

    Right now this takes the FIRST melody from the list, converts and returns it.
    """
    def __init__(self):
        super(MelodyToProtoConverter, self).__init__(
            input_type=melodies_lib.Melody,
            output_type=music_pb2.NoteSequence,
            name='MelodyToProtoConverter')

    def transform(self, melody):
        #try:
        print(melody)
        # melody = melodies[0]
        # print(melody)
        sequence = melody.to_sequence(velocity=100,
                                      instrument=0,
                                      program=0,
                                      sequence_start_time=0.0,
                                      qpm=120.0) 
        #except:
        #     tf.logging.warning('Skipped melody')
        
        return sequence


class TopMelodyExtractor(pipeline.Pipeline):
    """Extracts the top monophonic melody from a quantized NoteSequence.

    This corresponds to the melody that is played in the highest register
    of the right hand on a piano.

    This is a modification of magenta.pipelines.melody_pipelines.MelodyExtractor
    """

    def __init__(self, min_bars=7, max_steps=512, min_unique_pitches=5,
                 gap_bars=1.0, ignore_polyphonic_notes=False, filter_drums=True,
                 name=None):
        super(TopMelodyExtractor, self).__init__(
            input_type=music_pb2.NoteSequence,
            output_type=melodies_lib.Melody,
            name=name)
        self._min_bars = min_bars
        self._max_steps = max_steps
        self._min_unique_pitches = min_unique_pitches
        self._gap_bars = gap_bars
        self._ignore_polyphonic_notes = ignore_polyphonic_notes
        self._filter_drums = filter_drums

    def transform(self, quantized_sequence):
        melodies, stats = melodies_lib.extract_melodies(
            quantized_sequence,
            min_bars=self._min_bars,
            max_steps_truncate=self._max_steps,
            min_unique_pitches=self._min_unique_pitches,
            gap_bars=self._gap_bars,
            ignore_polyphonic_notes=self._ignore_polyphonic_notes,
            filter_drums=self._filter_drums)

        print(melodies)
        print('there')
        self._set_stats(stats)

        return melodies 

    
def get_midi_to_melody_proto_pipeline(config):
    """Returns a DAGPipeline that creates a melody NoteSequence from a MIDI file.

    Args:
        config: A MelodyRnnConfig object.

    Returns:
        dag_pipeline.DAGPipeline object.
    """
    # TimeChangeSplitter is useful for an MVP
    time_change_splitter = note_sequence_pipelines.TimeChangeSplitter(
        name='TimeChangeSplitter')
    quantizer = note_sequence_pipelines.Quantizer(
        steps_per_quarter=config.steps_per_quarter, name='Quantizer')
    # Same MelodyExtractor parameters as melody_rnn_create_dataset
    melody_extractor = melody_pipelines.MelodyExtractor(
    # melody_extractor = TopMelodyExtractor(
        min_bars=7, max_steps=512, min_unique_pitches=5,
        gap_bars=1.0, ignore_polyphonic_notes=True,
        name='MelodyExtractor')
    melody_to_proto_converter = MelodyToProtoConverter()
        # velocity=100, instrumnet=0, program=0, sequence_start_time=0.0,
        # qpm=120.0)
        
    # encoder_pipeline = melody_rnn_create_dataset.EncoderPipeline(config, name='EncodePipeline')

    dag = {time_change_splitter: dag_pipeline.DagInput(music_pb2.NoteSequence),
           quantizer: time_change_splitter,
           melody_extractor: quantizer,
           dag_pipeline.DagOutput('melodies'): melody_extractor}
           # melody_to_proto_converter: melody_extractor,
           # dag_pipeline.DagOutput('melody_sequence'): melody_to_proto_converter}
           # Need to convert Melody back to NoteSequence
           # Use the below for melody encoding! (model specific)
           # encoder_pipeline: melody_extractor,
           # dag_pipeline.DagOutput('melodies'): encoder_pipeline}
    # Sometimes this returns an empty array
    return dag_pipeline.DAGPipeline(dag)
