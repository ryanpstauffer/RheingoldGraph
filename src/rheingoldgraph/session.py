"""RheingoldGraph session."""
import sys
from lxml import etree
import librosa
import pretty_midi

from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
from gremlin_python import statics

import magenta
from magenta.protobuf import music_pb2

from rheingoldgraph.elements import Vertex, Note
from rheingoldgraph.midi import MIDIEngine
from rheingoldgraph.musicxml import get_parts_from_xml

# Load gremlin_python statics
statics.load_statics(globals())

DEFAULT_GREMLIN_URI = 'ws://localhost:8182/gremlin'
DEFAULT_MIDI_PORT = 'IAC Driver MidoPython'

# Exceptions
class LineDoesNotExist(Exception):
    pass

class LineExists(Exception):
    pass

class RheingoldGraphIntegrityError(Exception):
    pass

# Classes
class Session:
    """A RheingoldGraph Session."""
    def __init__(self, server_uri=None):
        """Instantiate a new RheingoldGraph Session."""
        if server_uri is None:
            server_uri = DEFAULT_GREMLIN_URI

        self.graph = Graph()
        self.g = self.graph.traversal().withRemote(DriverRemoteConnection(server_uri, 'g'))


    def _add_line(self, line_name):
        """Add a line to the graph and return it.

        Args:
            line_name: Name of the line to add
        Returns:
            line: new Line object added to the graph
        """

        raw_line = self.g.addV('Line').property('name', line_name).next()
        
        # Get full line object and properties
        line = self.get_vertex_by_id(raw_line.id)

        return line


    # def add_line(self, note_list, line_name):
    #     """Add a series of Notes to the graph.

    #     We iterate through the list of notes and add each note
    #     with a separate execution.

    #     It is possible to add an iterable of Notes (such as a list)
    #     in a a single traversal, IF the list isn't too long.
    #     For now, we're using this simpler implementation,
    #     where we iterate through a list of notes and add each note
    #     with a separate traversal execution.

    #     note_list: list of Notes (ordered by time)
    #     line_name: name to be applied to the musical line
    #     """
    #     # Create a new line iff it doesn't already exist
    #     line = self.find_line(line_name)
    #     if line:
    #         print("Line already exists")
    #         return
    #     else:
    #         # TODO(ryan): This should return a line object
    #         line = self.g.addV('Line').property('name', line_name).next()

    #     # Add notes to the line
    #     note_counter = 0
    #     prev_note = None
    #     for note in note_list:
    #         # print(note)
    #         # print(prev_note)
    #         # Different traversal depending if this is the first note of the line
    #         if prev_note is None:
    #             traversal = self.g.V(line.id).as_('l')
    #             traversal = self._add_note_to_traversal(traversal, note)
    #             traversal = traversal.addE('start').from_('l').to('new')
    #         else:
    #             traversal = self.g.V(prev_note.id).as_('prev').out('in_line').as_('l')
    #             traversal = self._add_note_to_traversal(traversal, note)
    #             traversal = traversal.addE('next').from_('prev').to('new')

    #         traversal = traversal.addE('in_line').from_('new').to('l')

    #         # Get recently added note
    #         # This should be a full Note object
    #         prev_note = traversal.select('new').next()
    #         note_counter += 1

    #     print('Line {0} ({1} notes) added'.format(line_name, note_counter))


    @staticmethod
    def _add_note_to_traversal(traversal, note):
        """Add Note and all its property to a traversal."""
        traversal = traversal.addV(note.label).as_('new')
        for prop, value in note.property_dict().items():
            traversal = traversal.property(prop, value)

        return traversal


    def get_vertex_by_id(self, vertex_id):
        """Get a Vertex element from the graph.

        Args:
            vertex_id: graph ID of note.
            Note that this must correspond to the type of identifier used by the graph engine
        Returns:
            object of Vertex label type (Note, Line, etc) if the id is found
            Otherwise, returns None
        """
        try:
            result = self.g.V(vertex_id).as_('v') \
                         .properties().as_('p').select('v', 'p').toList()

            if result == []:
                return None
            vertex_list = self._build_vertex_list_from_result(result)
            # Ensure only one vertex with that id exists
            if len(vertex_list) > 1:
                raise RheingoldGraphIntegrityError

            return self._build_object_from_props(vertex_list[0])
        except StopIteration:
            return None


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
            vertex_list = self._build_vertex_list_from_result(result)

            # Ensure only one line with that name exists
            if len(vertex_list) > 1:
                raise RheingoldGraphIntegrityError

            return self._build_object_from_props(vertex_list[0])
        except StopIteration:
            return None


    def _build_object_from_props(self, props_dict):
        """Build object from vertex properties.

        Dynamically build an object with the properties and type retrieved from the graph.
        Searches the rheingoldgraph.elements module for a class definition of the
        element type specified by the graph 'label'.
        If found, returns an object of that type.
        If not found, creates a generic Vertex object
        # TODO(Ryan): If not found, dynamically create a new object of new class
        # with type that matches the label foundin the props_dict

        Args:
            prop_dict: dictionary of vertex properties
        Returns:
            obj: new instance of the object described by the props_dict
        """
        cls = getattr(sys.modules['rheingoldgraph.elements'],
                      props_dict['label'], Vertex)
        obj = cls.from_dict(props_dict)

        return obj


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
            raise LineDoesNotExist

        self.g.V().hasLabel('Line').has('name', line_name).in_('in_line').drop().iterate()
        self.g.V().hasLabel('Line').has('name', line_name).drop().iterate()

        # Confirm that Line has been deleted
        if not self.find_line(line_name):
            print('Line {0} dropped from graph'.format(line_name))
        else:
            print('Line {0} not dropped.'.format(line_name))
            raise LineExists

    @staticmethod
    def _build_prop_dict_from_result(result):
        # Build our note dict of properties
        vertex = result[0]['v']
        prop_dict = {prop['p'].key: prop['p'].value for prop in result}

        prop_dict['id'] = vertex.id
        prop_dict['label'] = vertex.label
        # print(prop_dict)

        return prop_dict


    @staticmethod
    def _build_vertex_list_from_result(result):
        """Create a list of vertices and properties from a traversal result.

        Current implementation does not keep ordering in the result.
        If order of result matters, use a generator traversal method instead.

        Args:
            result: traversal result
                list of dicts in form, {'v': gremlin.Vertex, 'p': gremlin.VertexProperty}
        Returns:
            vertex: list of dicts describing vertices from the graph
                ex: [{'id': 15, 'label': 'Note', 'name': 'bach', other_props...}, {}]
        """
        # Create list of tuples from result
        tuples = [(row['v'].id, row['p']) for row in result]
        # Get unique vertices from result
        verts = set(row['v'] for row in result)
        # Create the vertex dict
        vertex_dict = {v.id: [] for v in verts}
        for x in tuples:
            vertex_dict[x[0]].append(x[1])
        # Add properties and create final list
        vertex_list = []
        for v in verts:
            part = {'id': v.id, 'label': v.label}
            part.update({prop.key: prop.value for prop in vertex_dict[v.id]})
            vertex_list.append(part)

        return vertex_list


    def add_lines_from_xml(self, filename, piece_name=None):
        """Add lines in graph from an xml file.

        Currently supports monophonic parts

        Args:
            filename: XML filename
            piece_name: Name to give the piece of music,
                        used for constructing line names
        """
        parts = get_parts_from_xml(filename)

        for part in parts:
            # TODO(ryan): Make this more robust
            if len(parts) == 1:
                line_name = piece_name
            else:
                line_name = '{0}_{1}'.format(piece_name, part.id)

            print(line_name)

            # Check if line already exists
            if self.find_line(line_name):
                print("Line already exists")
                raise LineExists

            line = self._add_line(line_name)
            # print(line)

            # Add notes to the line
            note_counter = 0
            prev_note = None
            tie_flag = False
            # Can I generalize this more?
            for note, tied_to_next in part.notes:
                prev_note = self._add_note(line, note, prev_note, tie_flag)

                if tied_to_next:
                    tie_flag = True
                else:
                    tie_flag = False 

                note_counter += 1

            print('Line {0} ({1} notes) added'.format(line_name, note_counter))


    def _add_note(self, line, note, prev_note=None, tied_to_prev=False):
        if prev_note is None:
            traversal = self.g.V(line.id).as_('l')
            traversal = self._add_note_to_traversal(traversal, note)
            traversal = traversal.addE('start').from_('l').to('new')
        else:
            traversal = self.g.V(prev_note.id).as_('prev').out('in_line').as_('l')
            traversal = self._add_note_to_traversal(traversal, note)
            traversal = traversal.addE('next').from_('prev').to('new')

            if tied_to_prev:
                traversal = traversal.addE('tie').from_('prev').to('new')

        traversal = traversal.addE('in_line').from_('new').to('l')

        raw_note = traversal.select('new').next()

        # Get full line object and properties
        added_note = self.get_vertex_by_id(raw_note.id)

        return added_note
        

    def get_playable_line(self, line_name, bpm, *, excerpt_len=None):
        """Iterate through a notation line and return a playable representation.

        Args:
            line_name: Name of the musical line
        returns:
            generator object of protobuf Notes
        """
        # Check if line exists
        line = self.find_line(line_name)
        if not line:
            print("Line {0} does not exist".format(line_name))
            raise LineDoesNotExist 

        ticks_per_beat = 480

        result = self.g.V().hasLabel('Line').has('name', line_name).out('start') \
                     .as_('v').properties().as_('p').select('v', 'p').toList()

        play_duration = 0
        num_notes_returned = 0
        excerpt_complete = False
        default_velocity = 100
        last_end_time = 0
        while result != [] and not excerpt_complete:
            vertex_list = self._build_vertex_list_from_result(result)
            note = self._build_object_from_props(vertex_list[0])

            play_duration += 1/note.length * \
                             (2 - (1 / 2**note.dot)) * \
                             4 * ticks_per_beat

            print(note)
            try:
                print(note.id) 
                # Check if the note is tied
                unk = self.g.V(note.id).out('tie').next()
                print(unk) 
                print('tie')
            except StopIteration:
                # If the note is not tied, ...
                note_length_in_sec = (60 / bpm) * (play_duration / ticks_per_beat)
                if note.name != 'R':
                    pb_note = music_pb2.NoteSequence.Note()
                    pb_note.pitch = pretty_midi.note_name_to_number(note.name)
                    pb_note.velocity = default_velocity

                    # Calc start and end times
                    pb_note.start_time = last_end_time
                    pb_note.end_time = pb_note.start_time + note_length_in_sec
                    yield pb_note

                    last_end_time = pb_note.end_time

                    # Flag if the excerpt is complete to stop iteration
                    num_notes_returned += 1
                    if num_notes_returned == excerpt_len:
                        excerpt_complete = True

                elif note.name == 'R':
                    last_end_time += note_length_in_sec
                    print('REST')
                play_duration = 0

            result = self.g.V(('id', note.id)).out('next') \
                           .as_('v').properties().as_('p').select('v', 'p').toList()


    def play_line(self, line_name, tempo, midi_port=DEFAULT_MIDI_PORT):
        """Play a line with MIDI instrument.

        This method streams protobuf Notes to a MIDI player

        Args:
            line_name: Name of the line to play
            tempo: tempo in bpm
        """
        m = MIDIEngine(midi_port, ticks_per_beat=480)

        notes = self.get_playable_line(line_name, tempo)
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
        sequence = self.get_line_as_sequence_proto(line_name, tempo,
                                                   excerpt_len=excerpt_len)
        pm = magenta.music.sequence_proto_to_pretty_midi(sequence)

        fs = 100
        librosa.display.specshow(pm.get_piano_roll(fs), hop_length=1,
                                 sr=fs, x_axis='time',
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
        if self.find_line(line_name):
            raise LineExists
        else:
            # Should return a line object, but getting there...
            line = self.g.addV('Line').property('name', line_name).next()

        # Add notes to the line
        note_counter = 0
        prev_note = None
        for note in sequence.notes:
            # Need to handle RESTS!
            # print(note)

            note_length_in_sec = note.end_time - note.start_time

            # For now we just handle a single tempo
            bpm = sequence.tempos[0].qpm

            percent_of_whole = round((bpm * note_length_in_sec) / 240, 5)

            # Converting note to note & dots
            possible_values = [1, 0.5, 0.25, 0.125, 0.0625]

            tied_notes = []
            remainder = percent_of_whole
            for val in possible_values:
                if val <= remainder:
                    tied_notes.append(val)
                    remainder -= val
                    if remainder == 0:
                        break

            # Need additional algo to calc dots
            # dot = np.log2(4 / (8 - (main_value * note_length_in_sec * bpm / 60)))
            dot = 0
            tie_flag = False
            while len(tied_notes) > 0:
                t_note = tied_notes.pop(0)
                note_length = int(1 / t_note)
                graph_note = Note(name=pretty_midi.note_number_to_name(note.pitch),
                                  length=note_length, dot=0)

                print(graph_note)

                prev_note = self._add_note(line, graph_note, prev_note, tie_flag)

                note_counter += 1

                if len(tied_notes) > 0:
                    tie_flag = True

            print('Line {0} ({1} notes) added'.format(line_name, note_counter))


if __name__ == '__main__':
    session = Session('ws://localhost:8189/gremlin')
    session.add_lines_from_xml('scores/BachCelloSuiteDminPrelude.xml', 'tester_bach')
    session.graph_summary()
    session.play_line('tester_bach', 120, 'IAC Driver MidoPython')
    session.drop_line('tester_bach')
