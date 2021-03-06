"""Tests of RheingoldGraph session."""

import pytest

from gremlin_python.structure.graph import Vertex, VertexProperty

from rheingoldgraph.elements import Line, Note
from rheingoldgraph.session import Session

# TODO(ryan): Launch and query a standalone test TinkerGraph instance

# Fixtures
@pytest.fixture
def session():
    server_uri = 'ws://localhost:8189/gremlin'
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

@pytest.fixture
def traversal_mult_note_result():
    vert_0 = Vertex(id=7700, label='Note')
    vert_1 = Vertex(id=7800, label='Note')

    result = [{'p': VertexProperty(id=7701, label='name', value='D3', vertex=None),
               'v': vert_0},
              {'p': VertexProperty(id=7702, label='length', value=16, vertex=None),
               'v': vert_0},
              {'p': VertexProperty(id=7703, label='dot', value=0, vertex=None),
               'v': vert_0},
              {'p': VertexProperty(id=7710, label='name', value='F3', vertex=None),
               'v': vert_1},
              {'p': VertexProperty(id=7712, label='length', value=8, vertex=None),
               'v': vert_1},
              {'p': VertexProperty(id=7713, label='dot', value=1, vertex=None),
               'v': vert_1}]

    return result

@pytest.fixture
def line_props():
    return {'id': 4602, 'label': 'Line', 'name': 'bach_cello'}

@pytest.fixture
def note_props():
    return {'id': 7700, 'label': 'Note', 'name': 'D3', 'length': 16, 'dot': 0}


@pytest.fixture
def note_list():
    return [Note('D3', 8, 0), Note('F3', 8, 0), Note('A3', 4, 0)]


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
        
    
    def test_line_from_props(self, session, line_props):
        line = session._build_object_from_props(line_props)
        assert type(line) == Line
        assert line.name == 'bach_cello'
        assert line.id == 4602 


    def test_note_from_props(self, session, note_props):
        note = session._build_object_from_props(note_props)
        assert type(note) == Note
        assert note.name == 'D3'
        assert note.length == 16
        assert note.dot == 0
        assert note.id == 7700


    def test_build_vertex_list_from_result_1v_1p(self, session, traversal_line_result):
        vertex_list = session._build_vertex_list_from_result(traversal_line_result)
        assert len(vertex_list) == 1
        assert vertex_list[0]['id'] == 4602
        assert vertex_list[0]['label'] == 'Line'
        assert vertex_list[0]['name'] == 'bach_cello'
        

    def test_build_vertex_list_from_result_1v_3p(self, session, traversal_note_result):
        vertex_list = session._build_vertex_list_from_result(traversal_note_result)
        assert len(vertex_list) == 1
        assert vertex_list[0]['id'] == 7700
        assert vertex_list[0]['label'] == 'Note'
        assert vertex_list[0]['name'] == 'D3'
        assert vertex_list[0]['length'] == 16
        assert vertex_list[0]['dot'] == 0
        

    def test_build_vertex_list_from_result_2v_3p(self, session, traversal_mult_note_result):
        vertex_list = session._build_vertex_list_from_result(traversal_mult_note_result)
        assert len(vertex_list) == 2

        # Since we don't know the order of note information,
        # we search for our expected dicts in the vertex_list
        vertex_0_dict = {'id': 7700, 'label': 'Note', 'name': 'D3', 'length': 16, 'dot': 0}
        vertex_1_dict = {'id': 7800, 'label': 'Note', 'name': 'F3', 'length': 8, 'dot': 1}

        assert vertex_0_dict in vertex_list
        assert vertex_1_dict in vertex_list

# Functional tests
class TestAddDropLine:
    def test_add_then_drop_line(self, session, note_list):
        # Line doesn't exist to begin with 
        line_name = 'tester'
        assert session.find_line(line_name) is None
        
        # Line is added and exists 
        session._add_line('tester')
        line = session.find_line(line_name)
        assert type(line) is Line
        assert line.name == 'tester'

        # Drop line and it doesn't exist
        session.drop_line(line_name)    
        assert session.find_line(line_name) is None

class TestAddNote:
    def test_add_first_note(self, session):
        # note = self._add_note(line, 
        pass 

    def test_add_second_note(self, session):
        pass

    def test_add_note_fails_if_line_doesnt_exist(self, session):
        pass
