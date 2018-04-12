"""Functional test to train TensorFlow model from graph."""

import pytest

from rheingoldgraph.session import Session

# Tests

class TestGetLinesForTraining:
    pass


class TestTrainModelWithLines:
    # temp test for now
    def test_stream_line_from_graph(self, session):
        """TEMP"""  
        line_names = ['bach_cello']
        bpm = 120
        session.train_model_with_lines_from_graph(line_names, bpm)
        assert False

