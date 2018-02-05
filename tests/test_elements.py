"""Tests of Basic Music Graph Elements"""

import pytest
from rheingoldgraph.elements import Note, Line 

# Fixtures
@pytest.fixture
def note():
    return Note(name='D3', length=4, dot=0)

@pytest.fixture
def line():
    return Line(name='bach_cello')

# Tests
class TestNote(object):
    def test_type(self, note):
        assert type(note) == Note
    
    #### Properties
    # Test get properties
    def test_get_name(self, note):
        assert note.name == 'D3'

    def test_get_length(self, note):
        assert note.length == 4

    def test_get_dot(self, note):
        assert note.dot == 0

    # Test set properties
    def test_set_name(self, note):
        note.name = 'E4'
        assert note.name == 'E4'
    
    def test_set_length(self, note):
        note.length = 8
        assert note.length == 8
        
    def test_set_dot(self, note):
        note.dot = 1
        assert note.dot == 1 

    # Other property tests
    def test_property_dict(self, note):
        expected_dict = {'name': 'D3', 'length': 4, 'dot': 0}
        assert note.property_dict() == expected_dict

    # Test id
    def test_default_id_is_None(self, note):
        assert note.id is None  

    def test_cant_set_id(self, note):
        with pytest.raises(AttributeError):
            note.id = 5

    
    #### Test alternate constructor
    def test_alt_constr_no_id(self):
        note_dict = {'name': 'D3', 'length': 4, 'dot': 0, 'label': 'Note'}
        new = Note.from_dict(note_dict)
        assert new.name == 'D3'
        assert new.length == 4
        assert new.dot == 0
        assert type(new) == Note
        assert new.id is None

    def test_alt_constr_w_id(self):
        note_dict = {'name': 'D3', 'length': 4, 'dot': 0, 'label': 'Note', 'id': 15}
        new = Note.from_dict(note_dict)
        assert new.name == 'D3'
        assert new.length == 4
        assert new.dot == 0
        assert type(new) == Note
        assert new.id == 15 


    #### Special methods
    def test_reflexive(self, note):
        assert eval(repr(note)) == note

    def test_eq_no_id(self, note):
        other = Note('D3', 4, 0)
        assert note == other

    def test_eq_w_id(self, note):
        """Equality shouldn't be impacted by id. Use 'is' to determine identity."""
        other_dict = {'name': 'D3', 'length': 4, 'dot': 0, 'id': 15, 'label': 'Note'}
        other = Note.from_dict(other_dict)
        assert note == other



class TestLine(object):
    def test_type(self, line):
        assert type(line) == Line 
 
    #### Properties
    # Test get properties
    def test_get_name(self, line):
        assert line.name == 'bach_cello'

    # Test set properties
    def test_set_name(self, line):
        line.name = 'wagner_piano'
        assert line.name == 'wagner_piano'
    
    # Other property tests
    def test_property_dict(self, line):
        expected_dict = {'name': 'bach_cello'}
        assert line.property_dict() == expected_dict

    # Test id
    def test_default_id_is_None(self, line):
        assert line.id is None  

    def test_cant_set_id(self, line):
        with pytest.raises(AttributeError):
            line.id = 5

    
    #### Test alternate constructor
    def test_alt_constr_no_id(self):
        line_dict = {'name': 'bach_cello', 'label': 'Line'}
        new = Line.from_dict(line_dict)
        assert new.name == 'bach_cello'
        assert type(new) == Line
        assert new.id is None

    def test_alt_constr_w_id(self):
        line_dict = {'name': 'bach_cello', 'label': 'Line', 'id': 21}
        new = Line.from_dict(line_dict)
        assert new.name == 'bach_cello'
        assert type(new) == Line
        assert new.id == 21 


    #### Special methods
    def test_reflexive(self, line):
        assert eval(repr(line)) == line

    def test_eq_no_id(self, line):
        other = Line('bach_cello')
        assert line == other

    def test_eq_w_id(self, line):
        """Equality shouldn't be impacted by id. Use 'is' to determine identity."""
        other_dict = {'name': 'bach_cello', 'id': 15, 'label': 'Line'}
        other = Line.from_dict(other_dict)
        assert line == other


