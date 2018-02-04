# Rheingold Graph session
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
from gremlin_python import statics
statics.load_statics(globals())

import pretty_midi
from lxml import etree
import numpy as np

import magenta
from magenta.protobuf import music_pb2


from rheingoldgraph.musicxml import get_part_information_from_music_xml, get_part_notes
from rheingoldgraph.elements import Line, Note
from rheingoldgraph.midi import MIDIEngine

class Session:
    def __init__(self, server_uri):
        self.graph = Graph()
        self.g = self.graph.traversal().withRemote(DriverRemoteConnection(server_uri, 'g'))

 
    def add_line_iterative(self, note_list, line_name):
        """Add a series of Notes to the graph.
        
        Instead of adding the notes in one traversal, 
        we iterate through the list of notes and add each note
        with a separate execution.

        This works better for now, but takes twice the time as the one-shot traversal.

        note_list: list of Notes (ordered)
        line_name
        """
        # Create a new line if it doesn't already exist
        line = self.find_line(line_name)
        if line:
            print("Line already exists")
            return
        else:
            # Should return a line object, but getting there...
            line = self.g.addV('Line').property('name', line_name).next()

        # Add notes to the line 
        note_counter = 0
        prev_note = None
        for note in note_list:
            print(note)
            print(prev_note)
            # Slightly different traversals depending on if this is the first note of the line
            if prev_note is None:
                traversal = self.g.V(line.id).as_('l')
                traversal = self._add_note_to_traversal(traversal, note)
                traversal = traversal.addE('start').from_('l').to('new')
            else:
                traversal = self.g.V(prev_note.id).as_('prev').out('in_line').as_('l')
                traversal = self._add_note_to_traversal(traversal, note)
                traversal = traversal.addE('next').from_('prev').to('new')

            traversal = traversal.addE('in_line').from_('new').to('l')

            # Get recently added note
            # This should be a full Note object
            prev_note = traversal.select('new').next() 
            note_counter += 1

        print('Line {0} ({1} notes) added'.format(line_name, note_counter))

    @staticmethod
    def _add_note_to_traversal(traversal, note):
        """Add Note and all its property to a traversal."""
        traversal = traversal.addV(note.label).as_('new')
        for prop, value in note.property_dict().items():
            traversal = traversal.property(prop, value)
        
        return traversal 


    def add_line(self, note_list, line_name):
        """Add a series of Notes to the graph

        g: GraphTraversalSource
        note_list: list of Notes (ordered)
        """
        # Create a new line
        traversal = self.g.addV('Line').property('name', line_name).as_('l')
        
        # Add notes to the line
        note_counter = 0
        new_notes = []
        for note in note_list:
            traversal = traversal.addV(note.label)
            for prop, value in note.__dict__.items():
                if prop != 'id':
                    traversal = traversal.property(prop, value)

            # Create alias for each new note so we can add edges
            note_alias = 'n_{0}'.format(note_counter)
            new_notes.append(note_alias)
            traversal = traversal.as_(note_alias)
            note_counter += 1
        
        # Add edges
        traversal = traversal.addE('start').from_('l').to('n_0') \
                             .addE('in_line').from_('l').to('n_0') 
        for n0, n1 in zip(new_notes, new_notes[1:]):
            traversal = traversal.addE('next').from_(n0).to(n1) \
                                 .addE('in_line').from_('l').to(n1)

        # Execute the traversal 
        traversal.next()
        print('Line {0} ({1} notes) added'.format('Test', len(new_notes)))


    def get_note_by_id(self, note_id):
        """Get a Note vertex from the graph.
        
        Args:
            note_id: graph ID of note.  
                Note that this must correspond to the type of identifier used by the graph engine
        """
        # This is still suboptimal 
        result = self.g.V(note_id).as_('v').properties().as_('p').select('v', 'p').toList() 
        prop_dict = self._build_prop_dict_from_result(result)

        return Note.from_dict(prop_dict)


    def find_line(self, line_name):
        """Returns a Line vertex if it exists, otherwise return None.

        Args:
            line_name: Name of line to find
        """ 
        try:
            result = self.g.V().hasLabel('Line').has('name', line_name) \
                         .as_('v').properties().as_('p').select('v', 'p').toList() 
            if result == []:
                return None
            prop_dict = self._build_prop_dict_from_result(result)
            # TODO(Ryan): Use an alternate constructor
            line = Line()
            line.id = prop_dict['id']
            line.name = prop_dict['name'] 
            return line
        except StopIteration:
            return None


    def get_line_and_notes(self, line_name):
        """Get all notes in a musical line from the graph.

        Use multiple traversals for generator functionality.
        This ensures that even a very large music line can be efficiently iterated.

        Args:
            line_name: Name of line to retrieve
        """
        result = self.g.V().hasLabel('Line').has('name', line_name).out('start') \
                     .as_('v').properties().as_('p').select('v', 'p').toList() 

        while result != []:
            prop_dict = self._build_prop_dict_from_result(result)
            last_id = prop_dict['id']
            yield Note.from_dict(prop_dict)

            result = self.g.V(('id', last_id)).out('next') \
                         .as_('v').properties().as_('p').select('v', 'p').toList()    


    def drop_line(self, line_name):
        """Remove a line and all associated musical content.
        
        Args:
            line_name: line name to drop
        """
        # Check that line exists
        line = self.find_line(line_name)
        if not line:
            print("Line {0} does not exist".format(line_name))
            return

        self.g.V().hasLabel('Line').has('name', line_name).in_('in_line').drop().iterate()
        self.g.V().hasLabel('Line').has('name', line_name).drop().iterate()

        # Confirm that Line has been deleted
        if not self.find_line(line_name):
            print('Line {0} dropped from graph'.format(line_name))
        else:
            # TODO(Ryan): Raise NotDropped Error?
            print('Line {0} not dropped.'.format(line_name))    


    @staticmethod
    def _build_prop_dict_from_result(result):
        # Build our note dict of properties
        vertex = result[0]['v']
        prop_dict = {prop['p'].key: prop['p'].value for prop in result}

        prop_dict['id'] = vertex.id
        prop_dict['label'] = vertex.label
        # print(prop_dict)
        
        return prop_dict


    def build_lines_from_xml_iterative(self, filename, piece_name=None):
        """Build a lines in graph from an xml file.

        Currently supports:
            - Single voice
            - Ties
            - Dots
        
        Args:
            filename: XML filename
            piece_name: Name to give the piece of music, used for constructing line names (in current prototype)
        """
        #    start_time = timer()
        # TODO(Ryan): A traversal should only be broken up into parts IFF it is longer than the minimum length
        # Question of LENGTH of traversal vs Execution time
        # Question of SIZE of graph and indexing time

        # Fully separate out XML parsing into separate module
        doc = etree.parse(filename)

        part_list = get_part_information_from_music_xml(doc)

        for part in part_list:
            part.notes = get_part_notes(part.id, doc)

            # TODO(Ryan): Make this more robust
            line_name = piece_name
            
            # Create a new line if it doesn't already exist
            line = self.find_line(line_name)
            if line:
                # TODO(Ryan): Should return error
                print("Line already exists")
                return
            else:
                # Should return a line object, but getting there...
                line = self.g.addV('Line').property('name', line_name).next()

            # Add notes to the line 
            note_counter = 0
            prev_note = None
            tie_flag = False
            for xml_note in part.notes:
                note = Note(xml_note.name, xml_note.length, xml_note.dot)

                # Slightly different traversals depending on if this is the first note of the line
                if prev_note is None:
                    traversal = self.g.V(line.id).as_('l')
                    traversal = self._add_note_to_traversal(traversal, note)
                    traversal = traversal.addE('start').from_('l').to('new')
                else:
                    traversal = self.g.V(prev_note.id).as_('prev').out('in_line').as_('l')
                    traversal = self._add_note_to_traversal(traversal, note)
                    traversal = traversal.addE('next').from_('prev').to('new')

                    if tie_flag:
                        traversal = traversal.addE('tie').from_('prev').to('new')
                        tie_flag = False

                traversal = traversal.addE('in_line').from_('new').to('l')

                # Get recently added note
                # This should be a full Note object
                prev_note = traversal.select('new').next() 
                note_counter += 1
        
                if xml_note.tied:
                    tie_flag = True

            print('Line {0} ({1} notes) added'.format(line_name, note_counter))

     
    def get_playable_line(self, line_name, bpm, *, excerpt_len=None):
        """Iterate through a notation line and return a playable representation.
        Args:
            line_name: Name of the musical line
        returns:
            generator object of protobuf Notes 
        """
        # TODO(ryanpstauffer) This should yield protobuffers
        # Check if line exists
        line = self.find_line(line_name)
        if not line:
            # TODO(Ryan): Should return error
            print("Line {0} does not exist".format(line_name))
            return

        ticks_per_beat = 480

        result = self.g.V().hasLabel('Line').has('name', line_name).out('start') \
                     .as_('v').properties().as_('p').select('v', 'p').toList() 

        play_duration = 0
        num_notes_returned = 0
        excerpt_complete = False
        default_velocity = 100
        last_end_time = 0
        while result != [] and not excerpt_complete:
            note_dict = self._build_prop_dict_from_result(result)
            last_id = note_dict['id']
            
            play_duration += 1/note_dict['length'] * (2 - (1 / 2**note_dict['dot'])) * 4 * ticks_per_beat

            try:
                self.g.V(last_id).out('tie').next() 
                # print('tie')
            except StopIteration:
                note_length_in_sec = (60 / bpm) * (play_duration / ticks_per_beat)
                if note_dict['name'] != 'R':
                    note = music_pb2.NoteSequence.Note()
                    note.pitch = pretty_midi.note_name_to_number(note_dict['name']) 
                    note.velocity = default_velocity

                    # Calc start and end times
                    note.start_time = last_end_time
                    note.end_time = note.start_time + note_length_in_sec

                    yield note 

                    last_end_time = note.end_time
                    num_notes_returned += 1 
                    if num_notes_returned == excerpt_len:
                        excerpt_complete = True
                
                elif note_dict['name'] == 'R':
                    last_end_time += note_length_in_sec 
                    print('REST')
                play_duration = 0
                
            result = self.g.V(('id', last_id)).out('next') \
                           .as_('v').properties().as_('p').select('v', 'p').toList()    

 
    def play_line(self, line_name, tempo):
        """Play a line with MIDI instrument.

        This method streams protobuf Notes to a MIDI player

        Args:
            line_name: Name of the line to play
            tempo: tempo in bpm 
        """
        notes = self.get_playable_line(line_name, tempo)

        midi_port = 'IAC Driver MidoPython'
        # We pass a generator of protobuf Notes to the GraphMidiPlayer
        # TODO(MIDI Player doesn't currently support protobuf notes!
        m = MIDIEngine(midi_port, ticks_per_beat=480)
        m.play_protobuf(notes)


    def save_line_to_midi(self, line_name, tempo, filename, *, excerpt_len=None):
        """Save a music line to a .mid file.

        Args:
            line_name: Name of the line to save
            tempo: Tempo
            filename: name of the MIDI file to create, ex: my_midi.mid
            excerpt_len: a integer number of notes to include
        """
        sequence = self.get_line_as_sequence_proto(line_name, tempo, excerpt_len=excerpt_len)
        magenta.music.sequence_proto_to_midi_file(sequence, filename)


    def get_line_as_sequence_proto(self, line_name, bpm, *, excerpt_len=None):
        """Return a line from the graph as a protobuf NoteSequence.

        This method returns the entire line (or an excerpt as a single NoteSequence.
        This means that the entire line is ready to be processed in batch,
        as opposed to streamed.
        
        """
        print("Returning line {0} as NoteSequence protobuf".format(line_name))
        notes = self.get_playable_line(line_name, bpm, excerpt_len=excerpt_len)

        sequence = music_pb2.NoteSequence()

        # Populate header
        ticks_per_beat = 480
        sequence.ticks_per_quarter = ticks_per_beat
        sequence.tempos.add(qpm=bpm) 

        sequence.notes.extend([n for n in notes]) 
        sequence.total_time = sequence.notes[-1].end_time 
 
        return sequence

    
    def visualize_line(self, line_name, tempo, *, excerpt_len=None):
        """Visualize a line in a piano roll.
        
        TODO: This method doesn't work!
        """
        sequence = self.get_line_as_sequence_proto(line_name, tempo, excerpt_len=excerpt_len)
        pm = magenta.music.sequence_proto_to_pretty_midi(sequence)
      
        fs = 100 
        librosa.display.specshow(pm.get_piano_roll(fs), hop_length=1, sr=fs, x_axis='time', 
                                 y_axis='cqt_note') 
        
        return pm


    def graph_summary(self):
        """Print a summary of musical information in our graph.
        """
        # Get graph summary stats
        total_vertices = self.g.V().count().next()
        total_edges = self.g.E().count().next()
        num_lines = self.g.V().hasLabel('Line').count().next()
        line_summary = self.g.V().hasLabel('Line').group().by('name') \
                              .by(inE('in_line').count()).next() 

        # Print graph summary
        print("Total Vertices: {0}".format(total_vertices))
        print("Total Edges: {0}".format(total_edges))
        print("Number of Lines: {0}\n----------------".format(num_lines))
        for key, val in line_summary.items():
            print("{0}: {1}".format(key, val))
  

    def add_sequence_proto_to_graph(self, sequence, line_name):
        """Add a Protocol Buffer Note Sequence to the graph.

        Args:
            sequence: protobuf NoteSequence
            line_name: name of the new line to be added to the graph
        """
        print("Adding protobuf sequence to RheingoldGraph line {0}".format(line_name))
        # Create a new line if it doesn't already exist
        line = self.find_line(line_name)
        if line:
            # TODO(Ryan): Should return error
            print("Line already exists")
            return
        else:
            # Should return a line object, but getting there...
            line = self.g.addV('Line').property('name', line_name).next()

        # Add notes to the line 
        note_counter = 0
        prev_note = None
        for note in sequence.notes:
            # Need to handle RESTS!
            print(note)
            
            note_length_in_sec = note.end_time - note.start_time     
            # print(note_length_in_sec)
            
            # Start by handling a single tempo
            bpm = sequence.tempos[0].qpm

            percent_of_whole = round((bpm * note_length_in_sec) / 240, 5)
            # print(percent_of_whole)

            # Converting note to note & dots
            possible_values = [1, 0.5, 0.25, 0.125, 0.0625]
        
            tied_notes = []
            remainder = percent_of_whole
            for val in possible_values:
                # print(val)
                if val <= remainder:
                    tied_notes.append(val)
                    remainder -= val 
                    # print(remainder)
                    if remainder == 0:
                        break 
             
            # Need additional algo to calc dots            
            # dot = np.log2(4 / (8 - (main_value * note_length_in_sec * bpm / 60))) 
            dot = 0
            tie_flag = False
            while len(tied_notes) > 0:
                t_note = tied_notes.pop(0)
                note_length = int(1 / t_note)
                graph_note = Note(name=pretty_midi.note_number_to_name(note.pitch), length=note_length, dot=0)
            
                print(graph_note)
                
                # Slightly different traversals depending on if this is the first note of the line
                if prev_note is None:
                    traversal = self.g.V(line.id).as_('l')
                    traversal = self._add_note_to_traversal(traversal, graph_note)
                    traversal = traversal.addE('start').from_('l').to('new')
                else:
                    traversal = self.g.V(prev_note.id).as_('prev').out('in_line').as_('l')
                    traversal = self._add_note_to_traversal(traversal, graph_note)
                    traversal = traversal.addE('next').from_('prev').to('new')

                    if tie_flag:
                        traversal = traversal.addE('tie').from_('prev').to('new')
                        tie_flag = False

                traversal = traversal.addE('in_line').from_('new').to('l')

                # Get recently added note
                # This should be a full Note object
                prev_note = traversal.select('new').next() 
                note_counter += 1
        
                if len(tied_notes) > 0:
                    tie_flag = True
                    # print(tie_flag)

            print('Line {0} ({1} notes) added'.format(line_name, note_counter))


if __name__ == "__main__":
    print('Test of Gremlin graph build.')
    server_uri = 'ws://localhost:8182/gremlin'
    
    session = Session(server_uri)

    # Build a line from an xml file
    # filename = 'scores/BachCelloSuiteDminPrelude.xml'
    #     session.build_lines_from_xml_iterative(filename, 'bach_cello')
    
    # play_bach = session.get_line_as_sequence_proto('bach_cello', 120, excerpt_len=11)
    # pm = session.visualize_line('bach_cello', 120, excerpt_len=10)
    # session.play_line('bach_cello', 120)
     
    # play_bach_2 = session.get_playable_line('bach_cello', 120)# , excerpt_len=25) 
    # Test of add protobuf to grapg
    # session.add_protobuf_to_graph(play_bach, 'magenta_bach')


    # session.drop_line('bach_cello')
    # session.play_line('bach_cello', 60)
