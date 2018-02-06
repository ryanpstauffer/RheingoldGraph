"""Tests of RheingoldGraph session."""

import pytest

from gremlin_python.structure.graph import Vertex, VertexProperty

from rheingoldgraph.elements import Line, Note
from rheingoldgraph.session import Session

# TODO(ryan): Launch and query a standalone test TinkerGraph instance

# Fixtures
@pytest.fixture
def session():
    server_uri = 'ws://localhost:8182/gremlin'
    return Session(server_uri)

@pytest.fixture
def traversal_line_result():
    result = [{'p': VertexProperty(id=4603, label='name', value='bach_cello', vertex=None),
               'v': Vertex(id=4602, label='Line')}]
    return result

@pytest.fixture
def traversal_note_result():
    vert = Vertex(id=7700, label='Note')
    result = [{'p': VertexProperty(id=7701, label='name', value='D3', vertex=None),
               'v': vert},
              {'p': VertexProperty(id=7702, label='length', value=16, vertex=None),
               'v': vert},
              {'p': VertexProperty(id=7703, label='dot', value=0, vertex=None),
               'v': vert}]
    return result


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

class TestElementsFromTraversal:
    def test_line_result_is_well_formed(self, traversal_line_result):
        """Make sure we're dealing with an appropriate test result."""
        result_property = traversal_line_result[0]['p']
        assert result_property.id == 4603
        assert result_property.label == 'name'
        assert result_property.value == 'bach_cello' 
        assert result_property.vertex is None

        result_vertex = traversal_line_result[0]['v']
        assert result_vertex.id == 4602
        assert result_vertex.label == 'Line'


    def test_note_result_is_well_formed(self, traversal_note_result):
        p0 = traversal_note_result[0]['p']
        p1 = traversal_note_result[1]['p']
        p2 = traversal_note_result[2]['p']
        vert = traversal_note_result[0]['v']
    
        assert p0.id == 7701
        assert p0.label == 'name'
        assert p0.value == 'D3'
        assert p0.vertex is None

        assert p1.id == 7702
        assert p1.label == 'length'
        assert p1.value == 16
        assert p1.vertex is None

        assert p2.id == 7703
        assert p2.label == 'dot'
        assert p2.value == 0
        assert p2.vertex is None

        assert vert.id == 7700
        assert vert.label == 'Note'


    def test_build_line_prop_dict(self, session, traversal_line_result):
        prop_dict = session._build_prop_dict_from_result(traversal_line_result)
        assert prop_dict['id'] == 4602
        assert prop_dict['label'] == 'Line'
        assert prop_dict['name'] == 'bach_cello'
        

    def test_build_note_prop_dict(self, session, traversal_note_result):
        prop_dict = session._build_prop_dict_from_result(traversal_note_result)
        assert prop_dict['id'] == 7700
        assert prop_dict['label'] == 'Note'
        assert prop_dict['name'] == 'D3'
        assert prop_dict['length'] == 16
        assert prop_dict['dot'] == 0
        
    
    def test_line_from_result(self, session, traversal_line_result):
        line = session.get_object_from_result(traversal_line_result)
        assert type(line) == Line
        assert line.name == 'bach_cello'
        assert line.id == 4602 


    def test_note_from_result(self, session, traversal_note_result):
        note = session.get_object_from_result(traversal_note_result)
        assert type(note) == Note
        assert note.name == 'D3'
        assert note.length == 16
        assert note.dot == 0
        assert note.id == 7700


