"""Tests of RheingoldGraph session."""

import pytest

from rheingoldgraph.elements import Line, Note
from rheingoldgraph.session import Session

# TODO(ryan): Launch and query a standalone test TinkerGraph instance

# Fixtures
@pytest.fixture
def session():
    server_uri = 'ws://localhost:8182/gremlin'
    return Session(server_uri)

# Tests
class TestFindLine:
    def test_return_none_if_no_line(self, session):
        line = session.find_line('no_strauss_here') 
        assert line is None

    def test_return_line_where_exists(self, session):
        line = session.find_line('bach_cello') 
        assert type(line) == Line
        assert line.name == 'bach_cello'
        assert line.id is not None

class TestDropLine:
    pass

class TestAddLine:
    pass

class TestAddSequenceProtoToGraph:
    pass
  
