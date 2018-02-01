# Music Graph process prototype 
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph

from lxml import etree

from rheingoldgraph.musicxml import get_part_information_from_music_xml, get_part_notes
from rheingoldgraph.elements import Line, Note, PlayableNote
from rheingoldgraph.midi import GraphMidiPlayer

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
            print(result)
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

     
    def get_playable_line(self, line_name):
        """Iterate through a notation line and return a playable representation.
        Args:
            line_name: Name of the musical line
        returns:
            generator object of PlayableNotes
        """
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
        while result != []:
            note_dict = self._build_prop_dict_from_result(result)
            last_id = note_dict['id']
            
            play_duration += 1/note_dict['length'] * (2 - (1 / 2**note_dict['dot'])) * 4 * ticks_per_beat

            try:
                self.g.V(last_id).out('tie').next() 
                # print('tie')
            except StopIteration:
                play_dict = {'label': 'PlayableNote', 'name': note_dict['name']}
                play_dict['duration'] = play_duration
                yield PlayableNote.from_dict(play_dict) 

                play_duration = 0
                
            result = self.g.V(('id', last_id)).out('next') \
                           .as_('v').properties().as_('p').select('v', 'p').toList()    

 
    def play_line(self, line_name, tempo):
        """Play a line with MIDI instrument.
        Args:
            line_name: Name of the line to play
            tempo: tempo in bpm 
        """
        notes = self.get_playable_line(line_name)

        midi_port = 'IAC Driver MidoPython'
        # We pass a generator of PlayableNotes (notes) to the GraphMidiPlayer
        m = GraphMidiPlayer(notes, tempo)
        m.play(midi_port)


    def save_line_to_midi(self, line_name, tempo, filename, *, excerpt_len=None):
        """Save a music line to a .mid file.

        Args:
            line_name: Name of the line to save
            tempo: Tempo
            filename: name of the MIDI file to create, ex: my_midi.mid
            excerpt_len: a integer number of notes to include
        """
        notes = self.get_playable_line(line_name)

        if excerpt_len is not None:
            notes = list(notes)[0:excerpt_len]

        # We pass a generator (notes) to the GraphMidiPlayer
        m = GraphMidiPlayer(notes, tempo)
        m.save_to_file(filename)


if __name__ == "__main__":
    print('Test of Gremlin graph build.')
    server_uri = 'ws://localhost:8182/gremlin'
    
    session = Session(server_uri)

    # Build a line from an xml file
    filename = 'scores/BachCelloSuiteDminPrelude.xml'
    session.build_lines_from_xml_iterative(filename, 'bach_cello')

    play_bach = session.get_playable_line('test')
    # session.drop_line('bach_cello')
    # session.play_line('bach_cello', 60)
