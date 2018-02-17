"""Rheingold implementation of Magenta Pipelines."""
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
                 sequence_start_time=0.0, qpm=120.0):
        super(MelodyToProtoConverter, self).__init__(
            input_type=melodies_lib.Melody,
            output_type=music_pb2.NoteSequence,
            name='MelodyToProtoConverter')
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
    midi_to_proto_converter = MidiToProtoConverter(name='MidiToProtoConverter')
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
    melody_to_proto_converter = MelodyToProtoConverter(
        velocity=100, instrument=0, program=0, sequence_start_time=0.0,
        qpm=120.0)

    dag = {midi_to_proto_converter: dag_pipeline.DagInput(bytes),
           time_change_splitter: midi_to_proto_converter,
           quantizer: time_change_splitter,
           melody_extractor: quantizer,
           melody_to_proto_converter: melody_extractor,
           dag_pipeline.DagOutput('melody_sequence'): melody_to_proto_converter}

    # Sometimes this returns an empty array
    return dag_pipeline.DAGPipeline(dag)
