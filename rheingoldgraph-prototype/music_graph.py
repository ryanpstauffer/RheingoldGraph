"""RheingoldGraph API on top of Neo4j."""

import getpass
from collections import namedtuple
import os
import uuid
import re
from timeit import default_timer as timer
import pandas as pd

from lxml import etree

from neo4j.v1 import GraphDatabase, basic_auth

from midi import GraphMidiPlayer
from musicxml_parser import get_part_information_from_music_xml, get_part_notes

#### TODO
# TODO(Ryan): Add chord support
# TODO(Ryan): Add in concurrent pitch support (chords, multiple voices, etc)

### Module helper definitions
ALLOWED_NODE_TYPES = ['Line']
TICKS_PER_BEAT = 480

### Module Exceptions
class Error(Exception):
    """Base class for module exceptions."""
    pass


class NoteNameError(Error):
    """Exception raised if specified source format is not supported."""
    def __init__(self, note_name):
        self.expression = note_name
        self.message = '{0} not a valid note name'


class InvalidNoteError(Error):
    """Exception raised if Note is not instantiated correctly."""
    def __init__(self, note_name, length):
        self.expression = (note_name, length)
        self.message = 'Not a valid Note instantiation'


class NodeTypeError(Error):
    """Exception raised if Note is not instantiated correctly."""
    def __init__(self, node_type):
        self.expression = (node_type)
        self.message = 'Node type not supported'


### Representations of Graph nodes

class Note(object):
    """A primitive Note Class."""
    def __init__(self, name=None, length=None, dot=0, from_properties=None):
        """A representation of a Note.

        name: Concatenated Pitch Class and Octave, ex: 'C4', or 'R' if a rest
        length: Number of this note per whole note, or the inverse of the note name
            ex: Sixteenth note => 16
        dot: Number of dots assigned to the rhythm (0, 1, 2, etc)
        from_properties: a properties dictionary to create all Note properties at once.
        """
        if from_properties:
            # If Note is built from existing Database data
            self.name = from_properties['name']
            self.length = from_properties['length']
            self.dot = dot
            self.pitch_class = from_properties['pitch_class']
            self.octave = from_properties['octave']
            self.uuid = from_properties['uuid']

        elif name and length:
            # If Note is instantiated as a new object
            self.name = name
            self.length = int(length)
            self.pitch_class, self.octave = self._split_name()
            self.dot = dot
            self.uuid = str(uuid.uuid4())

        else:
            raise InvalidNoteError(name, length)


    def _split_name(self):
        """Split a name into a pitch class and octave."""
        # Check if rest first:
        if self.name == 'R':
            return 'Rest', 0

        match = re.match(r"([A-Za-z#]+)([0-9]+)", self.name, re.I)
        if match:
            items = match.groups()
            return items[0], int(items[1])
        else:
            raise NoteNameError(self.name)


    def __repr__(self):
        return "Note(name={0}, length={1}, pitch_class={2}, octave={3}, uuid={4})".format(self.name, self.length,
                                                                                          self.pitch_class, self.octave, 
                                                                                          self.uuid)


    def __eq__(self, other):
        if self.uuid == other.uuid and self.name == other.name and self.length == other.length \
        and self.dot == other.dot and self.pitch_class == other.pitch_class \
        and self.octave == other.octave:
            return True
        else:
            return False


class PlayableNote(object):
    """A primitive Note Class."""
    def __init__(self, name=None, duration=None, pitch_class=None, octave=None, from_properties=None):
        """A representation of a Note.

        name: Concatenated Pitch Class and Octave, ex: 'C4', or 'R' if a rest
        duration: Number of ticks a note is held for
        dot: Number of dots assigned to the rhythm (0, 1, 2, etc)
        from_properties: a properties dictionary to create all Note properties at once.
        """

        if from_properties:
            # If PlayableNote is built from existing Database data
            self.name = from_properties['name']
            self.duration = from_properties['duration']
            self.pitch_class = from_properties['pitch_class']
            self.octave = from_properties['octave']

        elif name and duration and pitch_class:
            # If PlayableNote is instantiated as a new object
            self.name = name
            self.duration = float(duration)
            self.pitch_class = pitch_class
            self.octave = octave

        else:
            raise InvalidNoteError(name, duration)


    def _split_name(self):
        """Split a name into a pitch class and octave."""
        # Check if rest first:
        if self.name == 'R':
            return 'Rest', 0

        match = re.match(r"([A-Za-z#]+)([0-9]+)", self.name, re.I)
        if match:
            items = match.groups()
            return items[0], int(items[1])
        else:
            raise NoteNameError(self.name)


    def __repr__(self):
        return "Note(name={0}, duration={1}, pitch_class={2}, octave={3})".format(self.name, self.duration,
                                                                                  self.pitch_class, self.octave)


    def __eq__(self, other):
        if self.name == other.name and self.duration == other.duration \
        and self.pitch_class == other.pitch_class \
        and self.octave == other.octave:
            return True
        else:
            return False


class Line(object):
    """A primitive Line class."""
    def __init__(self, name=None, from_properties=None):
        if from_properties:
            self.name = from_properties["name"]
        else:
            self.name = name


    def __repr__(self):
        return "Line(name={0})".format(self.name)


### Main GraphAPI class

class GraphAPI(object):
    def __init__(self, ipaddress='localhost'):
        self.client = self._neo4j_connect(ipaddress)


    def _neo4j_connect(self, ipaddress, manual_password=False):
        """Connect to a Neo4j instance."""
        connection_uri = "bolt://{0}:7687".format(ipaddress)
        if manual_password:
            password = getpass.getpass("Neo4j Password: ")
        else:
            password = self._get_password()

        return GraphDatabase.driver(connection_uri, auth=basic_auth("neo4j", password))


    def _get_password(self, search_path=None):
        """Retrieve Neo4j password."""
        if not search_path:
            search_path = os.path.abspath(os.path.join('/','auth'))

        auth_filename = os.path.join(search_path, 'neo4j')

        with open(auth_filename, 'r') as f:
            pwd = f.readline().strip('\n')

        return pwd


    def _cypher(self, query, arguments=None):
        """Execute arbitrary Cypher query."""
        with self.client.session() as sess:
            results = sess.run(query, arguments)

        return results


    def add_line(self, line_name):
        """Add a Line node to the graph.

        Args:
            line_name: name of the line to add notes to
        """
        # Check if line exists
        if self.get_node_by_name(line_name, 'Line'):
            print("Line {0} already exists".format(line_name))
            return

        query = """MERGE (line:Line {name: {line_name}})
                   RETURN line"""

        args = {'line_name': line_name}

        results = self._cypher(query, args)

        # Get more specific about these results I think...
        if not results.peek():
            print("Nothing added")
            return

        for record in results:
            print("Line {0} added".format(record["line"]["name"]))
            return Line(from_properties=record["line"].properties)


    def get_node_by_name(self, name, node_type):
        """Get a node from the graph by name.

        Args:
            name: name of the node to check for existence
            node_type: type of node (Ex: Line)
        Returns:
            node if it exists, None if not
        """
        # Check if note_type is allowed
        if node_type not in ALLOWED_NODE_TYPES:
            print("Node type {0} not supported".format(node_type))
            raise NodeTypeError(node_type)

        query = """MATCH (found:%s {name: {name}})
                   RETURN found""" % node_type
        args = {'name': name}
        results = self._cypher(query, args)

        if not results.peek():
            print("{0} {1} does not exist".format(node_type, name))
            return

        for record in results:
            print("{0} {1} found".format(node_type, name))
            if node_type == 'Line':
                found_node = Line(from_properties=record["found"].properties)
            
            return found_node


    def add_note(self, note, prev_note=None, line_name=None):
        """Add a Node node to the graph.

        Args:
            note: a Note object
            prev_note: a Note object
            line_name: name of the line to add notes to
        """

        # This logic isnt' perfect, but should work for now
        # TODO(Ryan): Make more robust Line creation and matching logic
        args = {'new_name': note.name,
                'new_length': note.length,
                'new_dot': note.dot,
                'new_pitch_class': note.pitch_class,
                'new_octave': note.octave,
                'new_uuid': note.uuid}

        if prev_note and not line_name:
            query = """MATCH (prev:Note {uuid: {prev_uuid}})
                       MERGE (prev)-[rel:NEXT]->(new:Note {name: {new_name},
                                             length: {new_length},
                                             dot: {new_dot},
                                             pitch_class: {new_pitch_class},
                                             octave: {new_octave},
                                             uuid: {new_uuid}})
                       RETURN prev, rel, new"""

            args['prev_uuid'] = prev_note.uuid

        elif not line_name:
            query = """CREATE (new:Note {name: {new_name},
                               length: {new_length},
                               dot: {new_dot},
                               pitch_class: {new_pitch_class},
                               octave: {new_octave},
                               uuid: {new_uuid}})
                       RETURN new"""

        elif prev_note and line_name:
            query = """MATCH (prev:Note {uuid: {prev_uuid}}), (line:Line {name: {line_name}})
                       MERGE (prev)-[rel:NEXT]->(new:Note {name: {new_name},
                                             length: {new_length},
                                             dot: {new_dot},
                                             pitch_class: {new_pitch_class},
                                             octave: {new_octave},
                                             uuid: {new_uuid}})-[l:IN_LINE]->(line)
                       RETURN prev, rel, new, l, line"""

            args['prev_uuid'] = prev_note.uuid
            args['line_name'] = line_name

        elif line_name:
            query = """ MATCH (line:Line {name: {line_name}})
                        MERGE (new:Note {name: {new_name}, 
                                       length: {new_length},
                                       dot: {new_dot},
                                       pitch_class: {new_pitch_class},
                                       octave: {new_octave},
                                       uuid: {new_uuid}})-[l:IN_LINE]->(line)-[:START]->(new)
                        RETURN new"""
                                   
            args['line_name'] = line_name

        results = self._cypher(query, args)

        # Get more specific about these results I think...
        if not results.peek():
            print("Nothing added")
            return

        for record in results:
            print("Note {0} added".format(record["new"]["name"]))
            return Note(from_properties=record["new"].properties)


    def add_tie(self, note_0, note_1):
        """Add a tie between two notes."""
        query = """MATCH (n0:Note {uuid: {n0_uuid}}), (n1:Note {uuid: {n1_uuid}})
                       MERGE (n0)-[tie:TIE]->(n1)
                       RETURN n0, tie, n1"""

        args = {'n0_uuid': note_0.uuid, 'n1_uuid': note_1.uuid}
        results = self._cypher(query, args)

        if not results.peek():
            print("No Tie added".format(search_uuid))
            return

        for record in results:
            print("Tie added between {0} and {1}".format(record["n0"]["name"], record["n1"]["name"]))


    def get_note_by_uuid(self, search_uuid):
        """Return a Note object by its uuid."""
        query = """MATCH (n:Note {uuid: {uuid}})
                   RETURN n;"""

        args = {'uuid': search_uuid}
        results = self._cypher(query, args)

        # Get more specific about these results I think...
        if not results.peek():
            print("No Note w/ uuid {0} found".format(search_uuid))
            return

        for record in results:
            print("Note {0} found".format(record["n"]["name"]))
            return Note(from_properties=record["n"].properties)


    def delete_line(self, line_name):
        """Delete a line and all its musical content.

        Args:
            line_name
        """
        query = """MATCH (line:Line {name: {line_name}})
                   OPTIONAL MATCH (line)<-[l:IN_LINE]-(n:Note)
                   OPTIONAL MATCH (n)-[r]-(o)
                   DETACH DELETE n, l, r, o, line"""
        args = {'line_name': line_name}
        results = self._cypher(query, args)

        # TODO(Ryan): Create a better way to check and test this
        print("Line {0} removed".format(line_name))


    def get_midi_playable_line(self, line_name):
        """Get all notes in a given line in Midi-playable format.

        This method converts all ties to single notes of consistent length.

        Args:
            line_name: name of the line to get
        Returns:
            list of 
        """
        # Check if line exists
        if not self.get_node_by_name(line_name, 'Line'):
            print("Line {0} does not exist".format(line_name))
            return

        # Note that 'Binding relationships to a list in a variable length pattern is deprecated.'
        # TODO(Ryan): Rewrite using new Neo4j canonical form
        query = """MATCH (line:Line {name:{line_name}})-[r:START_PLAY|NEXT*]->(note:PlayableNote)
                    RETURN note, size(r) AS Dist
                    ORDER BY Dist"""

        args = {'line_name': line_name}
        results = self._cypher(query, args)

        return [PlayableNote(from_properties=record["note"].properties) for record in results]


    def get_midi_playable_line_chords(self, line_name):
        """Get all notes in a given line in Midi-playable format.

        This method converts all ties to single notes of consistent length.

        TODO(Ryan): This is imperfect still, but getting better
        Should we be explicity determining note duration here, separate from note legnth?

        Args:
            line_name: name of the line to get
        Returns:
            note_list

        TODO(Ryan): This is not efficient.
            What is a better way to return all musical information from a line
        """
        # Check if line exists
        if not self.get_node_by_name(line_name, 'Line'):
            print("Line {0} does not exist".format(line_name))
            return

        # Note that 'Binding relationships to a list in a variable length pattern is deprecated.'
        # TODO(Ryan): Rewrite using new canonical form
        query = """MATCH (line:Line {name:{line_name}})-[r:START_PLAY|NEXT*]->(note:PlayableNote)
                   OPTIONAL MATCH (note)-[:CHORD]-(chord_notes)
                    RETURN note, chord_notes, size(r) AS Dist
                    ORDER BY Dist"""

        args = {'line_name': line_name}
        results = self._cypher(query, args)

        return [PlayableNote(from_properties=record["note"].properties) for record in results]


    def build_playable_line(self, line_name):
        """Iterate through a notation line and build a playable representation in place."""
        # Check if line exists
        if not self.get_node_by_name(line_name, 'Line'):
            print("Line {0} does not exist".format(line_name))
            return

        # Start by creating the playable representation as a copy of the notation graph
        # Want to avoid the need to have external caching and index scans.
        # We should be able to handle our graph ops with a simple pointer.
        args = {'line_name': line_name}

        next_relationship_query = """//MATCH and add NEXT to non-tie notes
                        //START by Replicating the existing line, ties and all
                        //TODO(Ryan): This should calculate duration w/ Python script help
                        MATCH (line:Line {name:{line_name}})<-[:IN_LINE]-(note_0:Note)-[:NEXT]->(note_1:Note)
                        OPTIONAL MATCH (note_0:Note)-[t:TIE]->(note_1:Note)
                        MERGE (note_0)-[:PLAY_AS]->(play_0:PlayableNote {name: note_0.name,
                                                          duration: (1/toFloat(note_0.length)) * (2-(1/2^note_0.dot)) * 4 * %d,
                                                          pitch_class: note_0.pitch_class,
                                                          octave: note_0.octave})
                        MERGE (play_0)-[:IN_LINE]->(line)
                        MERGE (note_1)-[:PLAY_AS]->(play_1:PlayableNote {name: note_1.name,
                                                          duration: (1/toFloat(note_1.length)) * (2-(1/2^note_1.dot)) * 4 * %d,
                                                          pitch_class: note_1.pitch_class,
                                                          octave: note_1.octave})
                        MERGE (play_1)-[:IN_LINE]->(line)
                        MERGE (play_0)-[:NEXT]->(play_1)
                        WITH note_0, note_1, play_0, play_1, t WHERE t IS NOT NULL
                        MERGE (play_0)-[:TIE]->(play_1)
                        RETURN note_0, note_1, play_0, play_1""" % (TICKS_PER_BEAT,TICKS_PER_BEAT)


        start_pointer_query = """// Add a START pointer
                                MATCH (line:Line {name:{line_name}})-[:START]->(start_note:Note)
                                MATCH (start_note)-[:PLAY_AS]->(play)
                                MERGE (line)-[:START_PLAY]->(play)
                                RETURN line, start_note, play"""

        self._cypher(next_relationship_query, args)
        self._cypher(start_pointer_query, args)

        # How many times do we iterate through
        num_ties_query = """MATCH (line:Line {name:{line_name}})<-[:IN_LINE]-(p:PlayableNote)
                            MATCH (p)-[t:TIE]->()
                            RETURN COUNT(t) AS num_ties"""

        results_2 = self._cypher(num_ties_query, args)

        for record in results_2:
            num_ties = record["num_ties"]

        merge_query = """MATCH (line:Line {name:{line_name}})-[:START_PLAY|NEXT*]->(play_0:PlayableNote)
                        MATCH (play_0)-[:TIE]->(play_1:PlayableNote)
                        WITH play_0, play_1 LIMIT 1
                        MATCH (play_1)<-[:PLAY_AS]-(source_1:Note)
                        OPTIONAL MATCH (play_1)-[:NEXT]->(successor:PlayableNote)
                        OPTIONAL MATCH (play_1)-[t:TIE]->(successor)
                        SET play_0.duration = play_0.duration + play_1.duration
                        MERGE (source_1)-[:PLAY_AS]->(play_0)
                        DETACH DELETE play_1
                        WITH play_0, t, successor WHERE successor IS NOT NULL
                        MERGE (play_0)-[:NEXT]->(successor)
                        WITH play_0, t, successor 
                            WHERE successor IS NOT NULL
                            AND t IS NOT NULL
                        MERGE (play_0)-[:TIE]->(successor)"""

        for x in range(num_ties):
            results = self._cypher(merge_query, args)
            # for record in results:
            #     print(record['play_0'])

        print("Playable Line complete")


    def play_line(self, line_name, tempo):
        """Play a line with MIDI instrument."""
        notes = self.get_midi_playable_line(line_name)
        print(notes)

        midi_port = 'IAC Driver MidoPython'
        m = GraphMidiPlayer(notes, tempo)
        m.play(midi_port)


    def clear_playable_line(self, line_name):
        """Clear all playable information than has been added to a line.
        Args:
            line_name
        """
        query = """MATCH (line:Line {name: {line_name}})
                   MATCH (line)<-[l:IN_LINE]-(p:PlayableNote)
                   DETACH DELETE p"""
        args = {'line_name': line_name}
        results = self._cypher(query, args)

        # TODO(Ryan): Create a better way to check and test this
        print("PlayableLine {0} removed".format(line_name))


def parse_note_file_with_ties(filename):
    """Parse a note file for note name, note length and ties.

    This function expects a newline-delimited file, with space-delimited lines.
    Each line represents a single note.

    F3 8
    A3 4 T
    A3 16
    """
    notes = []
    tie = False

    with open(filename) as f:
        for line in f:
            # print(line)
            new_note = line.strip('\n').upper().split(' ')

            name = new_note[0]

            length = int(new_note[1])

            # If a tie is found in a line
            if len(new_note) > 2:
                tie = True
                print(new_note[2])

            notes.append([Note(name, length), tie])

            # Reset tied flag
            tie = False

    print(notes)
    return notes


def build_single_line(graph_client, filename, line_name=None):
    """Build a single line from a list of note lists.

    Notes are parsed in form:
    [note (tuple (name, length)), tie]
    """
    start_time = timer()

    if line_name:
        new_line = graph_client.add_line(line_name)
        if not new_line:
            return

    note_counter = 0
    last_note = None
    tie_flag = False

    with open(filename) as f:
        for line in f:
            # print(line)
            raw_note_info = line.strip('\n').split(' ')

            current_note = Note(raw_note_info[0], raw_note_info[1], dot=0)

            # graph_client.add_note(current_note, last_note, tied_to_last_note, line_name)
            graph_client.add_note(current_note, last_note, line_name)
            if tie_flag:
                print("Add old tie")
                graph_client.add_tie(last_note, current_note)
                tie_flag = False

            # print("Adding {0}".format(current_note.name))
            note_counter += 1

            if len(raw_note_info) > 2:
                tie_flag = True
                print(raw_note_info[2])

            last_note = current_note

    print("Added {0} notes to DB in {1:0.3} sec".format(note_counter, timer()-start_time))


def build_lines_from_xml(graph_client, filename, piece_name=None):
    """Build a lines in graph from an xml file.

    Currently supports:
        - Single voice
        - Ties
        - In process (Dots)
    """
    start_time = timer()

    doc = etree.parse(filename)

    part_list = get_part_information_from_music_xml(doc)

    for part in part_list:
        part.notes = get_part_notes(part.id, doc)

        print(part.notes)

        # TODO(Ryan): Make this more robust
        line_name = piece_name
        
        # TODO(Ryan): The MVP part of this just adds a single line from the piece...
        # This will eventually add ALL lines from the XML file
        if line_name:
            new_line = graph_client.add_line(line_name)
            if not new_line:
                return

        note_counter = 0
        last_note = None
        tie_flag = False

        for xml_note in part.notes:
            # raw_note_info = line.strip('\n').split(' ')?

            current_note = Note(xml_note.name, xml_note.length, xml_note.dot)

            # graph_client.add_note(current_note, last_note, tied_to_last_note, line_name)
            graph_client.add_note(current_note, last_note, line_name)
            if tie_flag:
                print("Add tie")
                graph_client.add_tie(last_note, current_note)
                tie_flag = False

            # print("Adding {0}".format(current_note.name))
            note_counter += 1

            if xml_note.tied:
                tie_flag = True
                print(xml_note.tied)

            last_note = current_note

    print("Added {0} notes to DB in {1:0.3} sec".format(note_counter, timer()-start_time))


if __name__ == '__main__':
    graph_client = GraphAPI('localhost')


    # Try to play back a chord


    # notes = parse_note_file('bach_cello_duration_in_names.csv')

    # graph_client.delete_line('tie_test')
    # notes = parse_note_file('note_pair_test.csv')
    # build_single_line(graph_client, notes, 'tie_test')

    # test = graph_client.get_midi_playable_line('new_bach')
    # play_line(test)

    # graph_client.play_line('new_bach', 60)

    # build_single_line_with_ties(graph_client, 'bach_cello_with_ties.txt', 'new_bach_4')

    #### Workflow Walkthrough
    # Build a line from a test file (with ties)
    # graph_client.delete_line('rest_test_6')
    # build_single_line(graph_client, 'rest_test_3.txt', 'rest_test_6')
    # graph_client.build_playable_line('new_bach_4')
    # graph_client.play_line('new_bach_4', 60)


    # ## We can also build this from an xml file
    # filename = '../../xml/BachCelloSuiteDminPrelude.xml'
    # build_lines_from_xml(graph_client, filename, 'bach_xml_3')

    # # graph_client.clear_playable_line('bach_xml_3')
    # graph_client.build_playable_line('bach_xml_3')

    # TODO(Ryan): Simplify midi playing of line duration
    graph_client.play_line('bach_xml_3', 60)

    # Retrieve the line and play it
    # test = graph_client.get_midi_playable_line('new_bach')
    # play_line(test)


