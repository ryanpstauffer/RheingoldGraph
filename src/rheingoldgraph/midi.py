"""RheingoldGraph Midi module."""

import itertools
import time
from collections import namedtuple

import mido
from mido import Message, bpm2tempo, open_output, MidiFile, MidiTrack
mido.set_backend('mido.backends.rtmidi')
import pretty_midi

# Let's try to remove this functionality right now...it's confusing for now and not strictly necessary
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

    # Below middle C
    note_num = middle_c_note_num - 1
    for n in range(note_name_list.index(middle_c_name)-1, -1, -1):
        midi_note[note_name_list[n]] = note_num
        note_num -= 1

    # Add enharmonic conversions
    enharmonic_mapping = {'Db': 'C#',
                          'Eb': 'D#',
                          'Gb': 'F#',
                          'Ab': 'G#',
                          'Bb': 'A#'}

    for n in [x for x in midi_note if x[0:2] in enharmonic_mapping]:
        midi_note[enharmonic_mapping[n[0:2]] + n[-1]] = midi_note[n]

    return midi_note


class MIDIEngine(object):
    """Midi Engine to play notes from Rheingold and Tensorflow."""
    def __init__(self, midi_port, ticks_per_beat=480):
        """Instance of RheingoldGraph MIDI Engine.

        Args:
            midi_port: Port on which to send MIDI data            
        """
        self.midi_port = midi_port
        self.ticks_per_beat = ticks_per_beat 


    def play_protobuf(self, notes):
        """Play protobuf Notes over a MIDI port.

        Args:
            notes: an iterable of Protocol Buffer Notes 

        """
        with open_output(self.midi_port) as outport:

            outport.send(Message('program_change', program=12))
            
            try:
                last_end_time = 0
                for n in notes:
                    # Calculate sleep time for rests
                    sleep_time = n.start_time - last_end_time
                    if sleep_time > 0:
                        print("Rest {0} sec".format(sleep_time))
                        time.sleep(sleep_time)

                    # Send note messages
                    note_duration = n.end_time - n.start_time
                    outport.send(Message('note_on', note=n.pitch, velocity=n.velocity))
                    print("Note {0}, {1} sec".format(n.pitch, note_duration))
                    time.sleep(note_duration)
                    outport.send(Message('note_off', note=n.pitch, velocity=n.velocity))
                    last_end_time = n.end_time

            except KeyboardInterrupt:
                print('Stopping MIDI output')
                outport.reset()
                outport.panic()


    # I can get rid of this method shortly
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
