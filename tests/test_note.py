"""Tests of Basic Music Graph Elements"""

import pytest
from rheingoldgraph.elements import Note

@pytest.fixture
def note():
    return Note(name='D3', length=4, dot=0)

class TestNote(object):
    def test_type(self, note):
        assert type(note) == Note
    
    # Test properties
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

    
    # Test alternate constructor
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


    # special methods
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


# class NoteTestCase(unittest.TestCase):
#     """Tests Note class functionality"""
#     def setUp(self):
#         pass
# 
# 
#     def tearDown(self):
#         pass
# 
# 
#     def test_split_name(self):
#         """Test that a Note object properly splits a name into pitch and octave."""
#         test_name = 'C4'
#         test_duration = 8
# 
#         expected_pitch_class = 'C'
#         expected_octave = 4
# 
#         # Act
#         test_note = Note(test_name, test_duration)
# 
#         self.assertEqual(expected_pitch_class, test_note.pitch_class, 
#                          msg="Note name C4 should be split into pitch class C")
#         self.assertEqual(expected_octave, test_note.octave, 
#                          msg="Note name C4 should be split into octave 4")


# if __name__ == '__main__':
#     unittest.main()
