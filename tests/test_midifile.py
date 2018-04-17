"""Tests of Standard Midi File parsing."""

import pytest

from rheingoldgraph.elements import Note
from rheingoldgraph.midifile import PerformanceNote, TimeSignature, convert_performance_note_to_symbolic_note

class TestPerformanceToSymbolicNoteConversion:
    def test_6_8_time(self):
        time_sig_6_8 = TimeSignature(numerator=6, denominator=8)

        ### Test non-dotted, non-tied notes
        # 0.125 beat -> 1 32nd 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.125)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_notes == [Note(name='C4', length=32, dot=0)]

        # 0.25 beat -> 1 sixteenth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.25)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_notes == [Note(name='C4', length=16, dot=0)]

        # 0.5 beat -> 1 eighth
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.5)
        actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_note == [Note(name='C4', length=8, dot=0)]

        # 1.0 beat -> 1 quarter 
        performance_note = PerformanceNote(pitch='C4', beat_duration=1)
        actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_note == [Note(name='C4', length=4, dot=0)]
       
        ### Test dotted notes 
        # 0.375 beat -> Dotted Sixteenth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.375)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_notes == [Note(name='C4', length=16, dot=1)]

        # 0.75 beat -> Dotted Eighth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.75)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_notes == [Note(name='C4', length=8, dot=1)]
    
        # 1.5 beat -> 1 quarter, dot
        performance_note = PerformanceNote(pitch='C4', beat_duration=1.5)
        actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        assert actual_note == [Note(name='C4', length=4, dot=1)]
    
        ### Test tied notes 
        # # TODO(ryan): This fails, fix it!
        # 1.75 beat -> Dotted quarter tied to Sixteenth 
        # performance_note = PerformanceNote(pitch='C4', beat_duration=1.75)
        # actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        # assert actual_notes == [Note(name='C4', length=4, dot=1),
        #                         Note(name='C4', length=16, dot=0)]

        # # 2.0 beats -> Dotted quarter tied to Eighth 
        # performance_note = PerformanceNote(pitch='C4', beat_duration=2.0)
        # actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        # assert actual_notes == [Note(name='C4', length=4, dot=1),
        #                         Note(name='C4', length=8, dot=0)]
    
        # # 3.0 beats -> 2 tied dotted quarters
        # performance_note = PerformanceNote(pitch='C4', beat_duration=3.0)
        # actual_note = convert_performance_note_to_symbolic_note(performance_note, time_sig_6_8)
        # assert actual_note == [Note(name='C4', length=4, dot=1),
        #                        Note(name='C4', length=4, dot=1)]
    

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
 
        # 3.0 beat -> Dotted half 
        performance_note = PerformanceNote(pitch='C4', beat_duration=3.0)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=1)]
 
        ### Test double-dotted, non-tied notes
        # 0.875 beat -> Double-dotted Eighth 
        performance_note = PerformanceNote(pitch='C4', beat_duration=0.875)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=8, dot=2)]
    
        # 1.75 beat -> Double-dotted quarter 
        performance_note = PerformanceNote(pitch='C4', beat_duration=1.75)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=4, dot=2)]
 
        # 3.5 beat ->  Double-dotted half 
        performance_note = PerformanceNote(pitch='C4', beat_duration=3.5)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=2)]
 
        ### Test tied notes
        # 2.5 beat -> Half and eigth note 
        performance_note = PerformanceNote(pitch='C4', beat_duration=2.5)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=0),
                                Note(name='C4', length=8, dot=0)]

        # 2.25 beat -> Half and 16th note 
        performance_note = PerformanceNote(pitch='C4', beat_duration=2.25)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=0),
                                Note(name='C4', length=16, dot=0)]
    
        # 1.25 beat -> Quarter and sixteenth note 
        performance_note = PerformanceNote(pitch='C4', beat_duration=1.25)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=4, dot=0),
                                Note(name='C4', length=16, dot=0)]
 
        # 3.25 beat -> Dotted half and sixteenth note 
        performance_note = PerformanceNote(pitch='C4', beat_duration=3.25)
        actual_notes = convert_performance_note_to_symbolic_note(performance_note, time_sig_4_4)
        assert actual_notes == [Note(name='C4', length=2, dot=1),
                                Note(name='C4', length=16, dot=0)]
 

