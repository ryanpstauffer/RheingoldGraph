"""Standard MIDI File (SMF) parsing."""

from collections import namedtuple

import mido
import pretty_midi

from rheingoldgraph.elements import Note

PerformanceNote = namedtuple('PlayNote', ['pitch', 'beat_duration'])
TimeSignature = namedtuple('TimeSignature', ['numerator', 'denominator'])

def convert_performance_note_to_symbolic_note(perf_note, time_signature):
    """Convert a beat_duration to a note length.
    Args:
        perf_note: a Performance Note 
        time_signature: numerator, denominator
    Returns:
        notes: One or more symbolic Note objects (more than one means they're tied)
    """ 
    notes = []
    # note = Note(name=play_note.pitch)
    # Handle 6/8
    base_duration = 1.5 
    num_base = perf_note.beat_duration // base_duration
    rem = perf_note.beat_duration % base_duration
    if num_base == 0:
        length = 8 / rem
    if num_base == 1:
        length = 4
        # dot = 
    elif num_base == 2:
        length = 2 

    # return Note(name='C4', length=length, dot=0)

    # Handle 4/4
    possible_duration = [4, 2, 1, 0.5, 0.25, 0.125, 0.01625] 
    complete = False 
    split_notes = []
    remainder = perf_note.beat_duration
    while not complete:
        for d in possible_duration:
            print(remainder, d)
            if d <= remainder:
                split_notes.append(d)
                remainder -= d
                if remainder == 0:
                    complete = True
                    break

    print(split_notes)
    # Split note are ordered by duration based on the above algo

    new_notes = []
    cur_dur = None
    next_dur = None
    if len(split_notes) == 1:
        cur_dur = split_notes.pop(0)
        length = int(4 / cur_dur)
        new_note = Note(name=perf_note.pitch, length=length, dot=0) 
        new_notes.append(new_note)
        return new_notes

    elif len(split_notes) == 2:
        cur_dur = split_notes.pop(0)
        length = int(4 / cur_dur)
        new_note = Note(name=perf_note.pitch, length=length, dot=0) 
        next_dur = split_notes.pop()
        if next_dur == cur_dur/2:
            new_note.dot = 1 
            new_notes.append(new_note)
        else:
            new_notes.append(new_note)
            length = int(4 / next_dur)
            another_new_note = Note(name=perf_note.pitch, length=length, dot=0)
            new_notes.append(another_new_note)
        return new_notes

    # TODO: fix this garbage, then make it all correct
    for x in range(len(split_notes)): 
        cur_dur = split_notes.pop(0)
        print(cur_dur)
        length = int(4 / cur_dur)
        new_note = Note(name=perf_note.pitch, length=length, dot=0) 
        try:
            next_dur = split_notes.pop()
            if next_dur == cur_dur/2:
                 
        except IndexError:
            new_notes.append(new_note)

    return new_notes



class MIDIFileParser:
    """Parser for MIDI performance Notes to symbolic Notes."""
    def __init__(self, filename, debug=False):
        self.debug = debug
        self.tracks = []

        md = mido.MidiFile(filename, debug=self.debug)
        self.ticks_per_beat = md.ticks_per_beat   

        # Iterate through tracks and create PerformanceNotes
        # Assume one track for now
        for track in md.tracks[0:1]:
            track_notes = [] 
            tick_loc = 0
            current_time_signature = None
            for message in track:
                # print(message.type)
                # print(message)
                # Track-global tick locator
                tick_loc += message.time 
                # print(tick_loc)

                # Handle Meta Messages
                # Set time signature if possible
                if message.type == 'time_signature':
                    current_time_signature = message

                # Handle Note Messages
                # TODO(ryan): Handle Rests
                elif message.type == 'note_on':
                    # print('New Note')
                    pitch_name = pretty_midi.note_number_to_name(message.note)
               
                elif message.type == 'note_off':
                    # print('Close Note')
                    beat_duration = message.time / self.ticks_per_beat  
                    note = PerformanceNote(pitch=pitch_name, beat_duration=beat_duration)
                    print(note) 
                    track_notes.append(note) 

                # Beat calcs
                global_beat = tick_loc / self.ticks_per_beat
                # print(global_beat)

        # Convert track PerformanceNotes to symbolic Note
        symbolic_notes = []
        for performance_note in track_notes:
            new_notes = convert_performance_note_to_symbolic_note(
                performance_note, current_time_signature)
            symbolic_notes.extend(new_notes)
        print(symbolic_notes)

if __name__ == '__main__':
    print('MIDI parser test')
    filename = '/Users/ryan/Projects/Rheingold/nottingham_melodies/jigs1.mid'
    md = MIDIFileParser(filename) 
