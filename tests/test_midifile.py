"""Tests of Standard Midi File parsing."""

import pytest

from rheingoldgraph.elements import Note
from rheingoldgraph.midifile import PerformanceNote, TimeSignature, convert_performance_note_to_symbolic_note

class TestPerformanceToSymbolicNoteConversion:
    # def test_6_8_time(self):
    #     time_sig_6_8 = TimeSignature(numerator=6, denominator=8)

    #     # 0.5 beat -> 1 eighth
    #     performance_note = PerformanceNote(pitch='C4', beat_duration=1)
    #     actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
    #     assert actual_note == Note(name='C4', length=8, dot=0)

    #     # 1.0 beat -> 1 quarter 
    #     performance_note = PerformanceNote(pitch='C4', beat_duration=2)
    #     actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
    #     assert actual_note == Note(name='C4', length=4, dot=0)
    #     
    #     # 1.5 beat -> 1 quarter, dot
    #     performance_note = PerformanceNote(pitch='C4', beat_duration=1)
    #     actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
    #     assert actual_note == Note(name='C4', length=8, dot=0)

    def test_4_4_time(self):
        time_sig_4_4 = TimeSignature(numerator=4, denominator=4)

        ### Test non-dotted, non-tied notes
        # 0.125 beat -> 1 32nd 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.125)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=32, dot=0)]

        # 0.25 beat -> 1 sixteenth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.25)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=16, dot=0)]

        # 0.5 beat -> 1 eighth
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.5)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=8, dot=0)]
    
        # 1.0 beat -> 1 quarter 
        performance_note = PerformanceNote(pitch='C4', beat_duration=1.0)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=4, dot=0)]
 
        # 2.0 beat -> 1 half 
        performance_note = PerformanceNote(pitch='C4', beat_duration=2.0)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=0)]

        # 4.0 beat -> 1 whole 
        performance_note = PerformanceNote(pitch='C4', beat_duration=4.0)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=1, dot=0)]
        
        ### Test single dotted, non-tied notes
        # 0.375 beat -> Dotted Sixteenth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.375)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=16, dot=1)]

        # 0.75 beat -> Dotted Eighth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.75)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=8, dot=1)]
    
        # 1.5 beat -> Dotted quarter 
        performance_note = PerformanceNote(pitch='C4', beat_duration=1.5)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=4, dot=1)]
 
        # 3.0 beat -> 1 half 
        performance_note = PerformanceNote(pitch='C4', beat_duration=3.0)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=1)]

        assert False
