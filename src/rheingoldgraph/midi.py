"""RheingoldGraph Midi module."""

import itertools
import time
from collections import namedtuple

import mido
from mido import Message, bpm2tempo, open_output, MidiFile, MidiTrack
mido.set_backend('mido.backends.rtmidi')

MidiNote = namedtuple('MidiNote', ['value', 'time'], verbose=False)

def build_midi_notes(num_octaves=9, naming='standard', middle_c_name='C4', middle_c_note_num=60):
    """Generate a dictionary of midi notes given parameters.
    """
    octaves = [x for x in range(num_octaves)]
    if naming == 'standard':
        note_names = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    else:
        print('Note naming parameter: {0} is unknown'.format(naming))
        return False

    note_name_list = [''.join((x[1], str(x[0]))) for x in itertools.product(octaves, note_names)]
    midi_note = {}

    # Iteratively name all notes
    # Middle C and above
    note_num = middle_c_note_num
    for n in range(note_name_list.index(middle_c_name), len(note_name_list)):
        midi_note[note_name_list[n]] = note_num
        note_num += 1
        # print(n)

    # Below middle C
    note_num = middle_c_note_num - 1
    for n in range(note_name_list.index(middle_c_name)-1, -1, -1):
        midi_note[note_name_list[n]] = note_num
        note_num -= 1
        # print(n)

    # Add enharmonic conversions
    enharmonic_mapping = {'Db': 'C#',
                          'Eb': 'D#',
                          'Gb': 'F#',
                          'Ab': 'G#',
                          'Bb': 'A#'}

    for n in [x for x in midi_note if x[0:2] in enharmonic_mapping]:
        midi_note[enharmonic_mapping[n[0:2]] + n[-1]] = midi_note[n]

    return midi_note


class GraphMidiPlayer(object):
    """Midi support to play notes from a music graph database."""
    def __init__(self, notes, tempo):
        """Args:
            notes: notes to play
            tempo: tempo in bpm
        """
        self.midi_note = build_midi_notes()

        # Hardcoded ticks per beat
        self.ticks_per_beat = 480

        self.microseconds_per_beat = bpm2tempo(tempo)
        self.notes = notes


    def play(self, midi_port):
        """Play the music over a MIDI port."""
        with open_output(midi_port) as outport:

            outport.send(Message('program_change', program=12))

            try:
                for n in self.notes:
                    sleep_time = (self.microseconds_per_beat * n.duration / self.ticks_per_beat) / 1000000
                    if n.name == 'R':
                        print("Rest {0} sec".format(sleep_time))
                        time.sleep(sleep_time)
                    else:
                        note_value = self.midi_note[n.name]
                        outport.send(Message('note_on', note=note_value, velocity=100))
                        print("Note {0}, {1} sec".format(n.name, sleep_time))
                        time.sleep(sleep_time)
                        outport.send(Message('note_off', note=note_value, velocity=100))

            except KeyboardInterrupt:
                print()
                outport.reset()
                outport.panic()


    def save_to_file(self, filename):
        mid = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        mid.tracks.append(track)

        elapsed = 0
        for n in self.notes:
            if n.name == 'R':
                elapsed += int(n.duration) 
            else:
                note_value = self.midi_note[n.name]
                track.append(Message('note_on', note=note_value, velocity=100, time=elapsed))
                track.append(Message('note_off', note=note_value, velocity=127, time=int(n.duration)))
                elapsed = 0
        
        mid.save(filename)
