"""Note object parsing."""

import unittest

from music_graph import Note

class NoteTestCase(unittest.TestCase):
    """Tests Note class functionality"""
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_split_name(self):
        """Test that a Note object properly splits a name into pitch and octave."""
        test_name = 'C4'
        test_duration = 8

        expected_pitch_class = 'C'
        expected_octave = 4

        # Act
        test_note = Note(test_name, test_duration)

        self.assertEqual(expected_pitch_class, test_note.pitch_class, 
                         msg="Note name C4 should be split into pitch class C")
        self.assertEqual(expected_octave, test_note.octave, 
                         msg="Note name C4 should be split into octave 4")


if __name__ == '__main__':
    unittest.main()
