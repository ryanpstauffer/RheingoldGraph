"""Standard MIDI File (SMF) parsing."""

from collections import namedtuple

import mido
import pretty_midi

from rheingoldgraph.elements import Note

PerformanceNote = namedtuple('PlayNote', ['name', 'beat_duration'])
TimeSignature = namedtuple('TimeSignature', ['numerator', 'denominator'])

def convert_performance_note_to_logical_note(perf_note, time_signature):
    """Convert a beat_duration to a note length.
    Args:
        perf_note: a Performance Note 
        time_signature: numerator, denominator
    Returns:
        notes: One or more symbolic Note objects (more than one means they're tied)
    """ 
    # Set possible note durations
    # TODO(ryan): Improve 6/8 handling
    # TODO(ryan): Improve nonstandard numerator handling
    if time_signature.denominator == 4:
        possible_duration = [4, 2, 1, 0.5, 0.25, 0.125, 0.01625] 
    elif time_signature.denominator == 8:
        possible_duration = [1, 0.5, 0.25, 0.125, 0.01625] 

    complete = False 
    split_notes = []
    remainder = perf_note.beat_duration
    while not complete:
        for d in possible_duration:
            print(remainder, d)
            if d <= remainder:
                split_notes.append(d)
                remainder -= d
                if round(remainder, 6) == 0:
                    complete = True
                break

    print(split_notes)
    # Split note are ordered by duration based on the above algo
    print('Split Notes Complete')
    new_notes = []
    note_dur = split_notes.pop(0)
    cur_dur = note_dur
    dot = 0
    while True:
        print(cur_dur)
        try:
            print(split_notes[0])
            if cur_dur == 2 * split_notes[0]:
                # Use a dot
                dot += 1
                print('Dot ++')
                cur_dur = split_notes.pop(0)
            else:
                new_notes.append(
                    Note(name=perf_note.name, length=int(4 / note_dur), dot=dot)) 
                print(new_notes)
                # Begin writing next note (reset dot counter and note_dur)
                note_dur = split_notes.pop(0)
                cur_dur = note_dur 
                dot = 0
        except IndexError:
            new_notes.append(
                Note(name=perf_note.name, length=int(4 / note_dur), dot=dot)) 
            print(new_notes)
            break

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

        self.performance_notes = track_notes
        # Convert track PerformanceNotes to symbolic Note
        symbolic_notes = []
        for performance_note in track_notes:
            new_notes = convert_performance_note_to_symbolic_note(
                performance_note, current_time_signature)
            symbolic_notes.extend(new_notes)
        print(symbolic_notes)

        self.symbolic_notes = symbolic_notes


if __name__ == '__main__':
    print('MIDI parser test')
    filename = '/Users/ryan/Projects/Rheingold/nottingham_melodies/jigs1.mid'
    md = MIDIFileParser(filename) 
