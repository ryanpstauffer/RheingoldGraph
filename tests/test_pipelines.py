"""Tests of RheingoldGraph Pipelines."""

import os
import pytest

import tensorflow as tf
from magenta.music import Melody
from magenta.models.melody_rnn import melody_rnn_model
from magenta.protobuf import music_pb2


from rheingoldgraph import pipelines

# Fixtures
@pytest.fixture
def basic_rnn_config():
    return melody_rnn_model.default_configs['basic_rnn']


@pytest.fixture
def midi_bytes(midi_single_note_filename):
    with open(midi_single_note_filename, 'rb') as f:
        m_bytes = f.read()

    return m_bytes 


# def midi_to_melody_proto_pipeline():
#    return get_midi_to_melody_proto_pipeline  


# Tests
class TestMidiToProtoConverter:
    """Test conversion of MIDI bytes to NoteSequence protobuf."""
    def test_init(self):
        midi_to_proto_converter = pipelines.MidiToProtoConverter(
                                       name='MidiToProtoConverter')
        assert midi_to_proto_converter.name == 'MidiToProtoConverter'
        assert midi_to_proto_converter.input_type == bytes
        assert midi_to_proto_converter.output_type == music_pb2.NoteSequence


    def test_transform(self, midi_bytes, single_note_seq):
        midi_to_proto_converter = pipelines.MidiToProtoConverter()
        actual = midi_to_proto_converter.transform(midi_bytes)[0]

        expected = single_note_seq
        
        assert expected.tempos == actual.tempos
        assert expected.notes == actual.notes
        assert expected.ticks_per_quarter == actual.ticks_per_quarter
        assert expected.total_time == actual.total_time


class TestMelodyToProtoConverter:
    """Test conversion of Melody to NoteSequence protobuf."""
    def test_init(self):
        melody_to_proto_converter = pipelines.MelodyToProtoConverter(
                                        velocity=100,
                                        instrument=0,
                                        program=0,
                                        sequence_start_time=0.0,
                                        qpm=120.0,
                                        name='MelodyToProtoConverter')

        assert melody_to_proto_converter.name == 'MelodyToProtoConverter'
        assert melody_to_proto_converter.input_type == Melody
        assert melody_to_proto_converter.output_type == music_pb2.NoteSequence

        assert melody_to_proto_converter._velocity == 100
        assert melody_to_proto_converter._instrument == 0
        assert melody_to_proto_converter._program == 0
        assert melody_to_proto_converter._sequence_start_time == 0.0
        assert melody_to_proto_converter._qpm == 120.0


    def test_transform(self, single_note_seq):
        single_note_mel = Melody([60])
        melody_to_proto_converter = pipelines.MelodyToProtoConverter(
                                        velocity=100,
                                        instrument=0,
                                        program=0,
                                        sequence_start_time=0.0,
                                        qpm=120.0,
                                        name='MelodyToProtoConverter')

        actual = melody_to_proto_converter.transform(single_note_mel)[0]

        expected = single_note_seq

        assert expected.tempos == actual.tempos
        assert expected.notes == actual.notes
        assert expected.ticks_per_quarter == actual.ticks_per_quarter
        assert expected.total_time == actual.total_time

# TODO
class TestMidiToMelodyProtoPipeline:
    def test_get_pipelines(self, basic_rnn_config):
        pass   

    def test_transform(self, basic_rnn_config):
        pass
        # actual = pipeline_instance.transform(test_bytes)
        # assert expected == actual

