"""Pytest configuration for RheingoldGraph."""

import os
import pytest

# import tensorflow as tf
# from magenta.music import Melody
# from magenta.pipelines import pipeline as magenta_pipeline

from rheingoldgraph.protobuf import music_pb2
from rheingoldgraph.session import Session

# Define common test filenames fixtures
# @pytest.fixture
# def midi_single_note_filename(scope='module'):
#     return os.path.join(
#         tf.resource_loader.get_data_files_path(), 'testdata/single_note.mid')
# 
# 
# @pytest.fixture
# def magenta_melody_rnn_sequence_filename(scope='module'):
#     return os.path.join(
#         tf.resource_loader.get_data_files_path(), 
#         'testdata/magenta_melody_rnn_sequence.tfrecord')
# 
# 
# @pytest.fixture
# def magenta_melody_rnn_one_hot_filename(scope='module'):
#     return os.path.join(
#         tf.resource_loader.get_data_files_path(), 
#         'testdata/magenta_melody_rnn_one_hot.tfrecord')


# Define common fixture objects

@pytest.fixture
def session(scope='module'):
    server_uri = 'ws://localhost:8189/gremlin'
    return Session(server_uri)

# 
# @pytest.fixture
# def magenta_melody_rnn_sequence(magenta_melody_rnn_sequence_filename,
#                                 scope='module'):
#     sequence_gen = magenta_pipeline.tf_record_iterator(
#         magenta_melody_rnn_sequence_filename,
#         music_pb2.NoteSequence) 
#     
#     return next(sequence_gen)
# 
# 
# @pytest.fixture
# def magenta_melody_rnn_one_hot(magenta_melody_rnn_one_hot_filename,
#                                 scope='module'):
#     one_hot_gen = magenta_pipeline.tf_record_iterator(
#         magenta_melody_rnn_one_hot_filename,
#         tf.train.SequenceExample) 
#     
#     return next(one_hot_gen)
# 
# 
# @pytest.fixture
# def single_note_seq(scope='module'):
#     """Creates a single NoteSequence consisting of a quarter note middle C."""
#     mel = Melody([60]) 
#     return mel.to_sequence()
# 

