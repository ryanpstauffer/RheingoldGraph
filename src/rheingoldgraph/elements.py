# Music Graph build test in Gremlin
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
# import goblin

from lxml import etree
from musicxml import get_part_information_from_music_xml, get_part_notes


# I need to make progress, so I'm building out my own classes
# I will add complexity as I go, and hopefully can eventually inherit from goblin?

class PropertyDescriptor:
    def __init__(self, name):
        self.name = name


    def __get__(self, instance, objtype):
        if instance is None:
            return self
        return instance.__dict__[self.name]


    def __set__(self, instance, value):
        # Add validate here
        instance.__dict__[self.name] = value


    def __delete__(self, instance):
        del instance.__dict__[self.name] 


class Line:
    """A Line Vertex."""
    label = 'Line'
    name = PropertyDescriptor('name')
    # name = goblin.Property(goblin.String)

    def __repr__(self):
        return "Line(name={0!r})".format(self.name)



class Note:
    """A Note Vertex.
    """
    label = 'Note' 

    name = PropertyDescriptor('name')
    length = PropertyDescriptor('length')
    dot = PropertyDescriptor('dot')

    # name = goblin.Property(goblin.String)
    # length = goblin.Property(goblin.Float) 
    # dot = goblin.Property(goblin.Integer, default=0)
    

    def __init__(self, name=None, length=None, dot=None):
        self.name = name
        self.length = length
        self.dot = dot
        self.id = None
 
    def __repr__(self):
        return "Note(name={0!r}, length={1!r}, dot={2!r})".format(self.name, self.length, self.dot)

    
    def __eq__(self, other):
        # TODO(Ryan): This should be modified to take into account equality EXCLUDING DB ID
        # Desired behavior: Note('D3', 4.0, 0) == Note('D3', 4.0, 0) REGARDLESS of ID in the database
        if isinstance(other, Note):
            return self.to_dict() == other.to_dict() 
        else:
            return False


    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, mapping):
        mapping = mapping.copy()
        label = mapping.pop('label')
        vid = mapping.pop('id')
    
        # There's a more elegant way to build new notes w/ error handling, but I'll add it later
        note = Note()
        for key, value in mapping.items():
            setattr(note, key, value)
        #        print(note)

        return note
   
 

def add_note(g, note, prev_note=None, line_name=None):
    """Add a Note vertex to the graph.

    Args:
        g: graph traversal source
        note: a Note object
        prev_note: a Note object
        line_name: name of the line to add notes to
    """
    if prev_note is None and line_name is None:
        traversal = g.addV(note.label).as_('new')
        for prop, value in note.__dict__.items():
            if prop != 'id':
                traversal = traversal.property(prop, value)

        added_note = traversal.next()

    elif prev_note is None:
        traversal = g.addV(note.label).as_('new')
        for prop, value in note.__dict__.items():
            if prop != 'id':
                traversal = traversal.property(prop, value)
        # Add note to line
        # jtraversal = traversal.
        # traversal = traversal.addE('in_line').

    traversal = g.V(prev_note.id).as_('prev').out('in_line').as_('line')
    traversal = traversal.addV(note.label).as_('new')
    for prop, value in note.__dict__.items():
        if prop != 'id':
            traversal = traversal.property(prop, value)
    # Add edge to previous note
    traversal = traversal.addE('next').from_('prev').to('new')
    # Add edge to line
    traversal = traversal.addE('in_line').from_('new').to('line')

    return added_note


def add_line_iterative(g, note_list, line_name):
    """Add a series of Notes to the graph.
    
    Instead of adding the notes in one traversal, 
    we iterate through the list of notes and add each note
    with a separate execution.

    This works better for now, but takes twice the time as the one-shot traversal.

    g: GraphTraversalSource
    note_list: list of Notes (ordered)
    line_name
    """
    # Create a new line if it doesn't already exist
    line = find_line(g, line_name)
    if line:
        print("Line already exists")
        return
    else:
        # Should return a line object, but getting there...
        line = g.addV('Line').property('name', line_name).next()

    # Add notes to the line 
    note_counter = 0
    prev_note = None
    for note in note_list:
        print(note)
        print(prev_note)
        # Slightly different traversals depending on if this is the first note of the line
        if prev_note is None:
            traversal = g.V(line.id).as_('l')
            traversal = _add_note_to_traversal(traversal, note)
            traversal = traversal.addE('start').from_('l').to('new')
        else:
            traversal = g.V(prev_note.id).as_('prev').out('in_line').as_('l')
            traversal = _add_note_to_traversal(traversal, note)
            traversal = traversal.addE('next').from_('prev').to('new')

        traversal = traversal.addE('in_line').from_('new').to('l')

        # Get recently added note
        # This should be a full Note object
        prev_note = traversal.select('new').next() 
        note_counter += 1

    print('Line {0} ({1} notes) added'.format(line_name, note_counter))


def _add_note_to_traversal(traversal, note):
    """Add Note and all its property to a traversal."""
    traversal = traversal.addV(note.label).as_('new')
        for prop, value in note.__dict__.items():
            if prop != 'id':
                traversal = traversal.property(prop, value)
    
    return traversal 


def add_line(g, note_list, line_name):
    """Add a series of Notes to the graph

    g: GraphTraversalSource
    note_list: list of Notes (ordered)
    """
    # Create a new line
    traversal = g.addV('Line').property('name', line_name).as_('l')
    
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
    
    traversal.next()
    print('Line {0} ({1} notes) added'.format('Test', len(new_notes)))


def get_note_by_id(g, note_id):
    """get a Note vertex from the graph.
    """
    # This is still suboptimal 
    result = g.V(note_id).as_('v').properties().as_('p').select('v', 'p').toList() 
   
    prop_dict = build_prop_dict_from_result(result)

    return Note.from_dict(prop_dict)


def find_line(g, line_name):
    """Returns a Line vertex if it exists, otherwise return None.""" 
    try:
        result = g.V().hasLabel('Line').has('name', line_name) \
                  .as_('v').properties().as_('p').select('v', 'p').toList() 
        if result == []:
            return None
        print(result)
        prop_dict = build_prop_dict_from_result(result)
        # TODO(Ryan): Use an alternate constructor
        line = Line()
        line.id = prop_dict['id']
        line.name = prop_dict['name'] 
        return line
    except StopIteration:
        return None


def get_line_and_notes(g, line_name):
    """Get all notes in a musical line from the graph.

    Use multiple traversals for generator functionality.
    This ensures that even a very large music line can be efficiently iterated.
    """
    result = g.V().hasLabel('Line').has('name', line_name).out('start') \
              .as_('v').properties().as_('p').select('v', 'p').toList() 

    while result != []:
        prop_dict = build_prop_dict_from_result(result)
        last_id = prop_dict['id']
        yield Note.from_dict(prop_dict)

        result = g.V(('id', last_id)).out('next') \
                  .as_('v').properties().as_('p').select('v', 'p').toList()    


def drop_line(g, line_name):
    """Remove a line and all associated musical content.
    """
    # g.V().hasLabel('Line').has('name', line_name).as_('l').out('in_line') \
    #      .as_('n').select('l', 'n').drop().next()

    g.V().hasLabel('Line').has('name', line_name).out('in_line').drop().iterate()
    g.V().hasLabel('Line').has('name', line_name).drop().iterate()

    # Confirm that Line has been deleted
    if not find_line(g, line_name):
        print('Line {0} dropped from graph'.format(line_name))
    else:
        # TODO(Ryan): Raise NotDropped Error?
        print('Line {0} not dropped.'.format(line_name))    


def build_prop_dict_from_result(result):
    # Build our note dict of properties
    vertex = result[0]['v']
    prop_dict = {prop['p'].key: prop['p'].value for prop in result}

    prop_dict['id'] = vertex.id
    prop_dict['label'] = vertex.label
    print(prop_dict)
    
    return prop_dict



def execute_traversal(traversal):
    """Execute a traversal, including breaking it down into manageable parts."""
    print(len(traversal))
    traversal.next()


def build_lines_from_xml_iterative(graph_client, filename, piece_name=None):
    """Build a lines in graph from an xml file.

    Currently supports:
        - Single voice
        - Ties
        - Dots
    """
    #    start_time = timer()
    # TODO(Ryan): A traversal should only be broken up into parts IFF it is longer than the minimum length
    # Question of LENGTH of traversal vs Execution time
    # Question of SIZE of graph and indexing time

    doc = etree.parse(filename)

    part_list = get_part_information_from_music_xml(doc)

    for part in part_list:
        part.notes = get_part_notes(part.id, doc)

        print(part.notes)

        # TODO(Ryan): Make this more robust
        line_name = piece_name
        
        # TODO(Ryan): The MVP part of this just adds a single line from the piece...
        # This will eventually add ALL lines from the XML file
        # if line_name:
        #     new_line = graph_client.add_line(line_name)
        #     if not new_line:
        #         return
        
        # Create a new line
        line_vertex = g.addV('Line').property('name', line_name).next()
     
        note_counter = 0
        new_notes = []

        last_note = None
        tie_flag = False

        for xml_note in part.notes:
            # raw_note_info = line.strip('\n').split(' ')?
            
            note = Note(xml_note.name, xml_note.length, xml_note.dot)
            print(note)

            traversal = traversal.addV(note.label)
            for prop, value in note.__dict__.items():
                if prop != 'id':
                    traversal = traversal.property(prop, value)

            # Create alias for each new note so we can add edges
            note_alias = 'n_{0}'.format(note_counter)
            traversal = traversal.as_(note_alias)
            new_notes.append(note_alias)
            note_counter += 1
            
            if tie_flag:
                print("Add tie")
                traversal = traversal.addE('tie').from_(new_notes[-2]).to(note_alias)
                print(traversal)
                tie_flag = False

            if xml_note.tied:
                tie_flag = True
                print(xml_note.tied)

        # Add edges
        traversal = traversal.addE('start').from_('l').to('n_0') \
                         .addE('in_line').from_('l').to('n_0') 

        for n0, n1 in zip(new_notes, new_notes[1:]):
            traversal = traversal.addE('next').from_(n0).to(n1) \
                                 .addE('in_line').from_('l').to(n1)
    
        # ISSUE: NEED to deal w/ max frame length of 65536!!!!
        print(traversal)
        print(len(new_notes))
    #        execute_traversal(traversal)

        print('Line {0} ({1} notes) added'.format('Test', len(new_notes)))


def build_lines_from_xml(graph_client, filename, piece_name=None):
    """Build a lines in graph from an xml file.

    Currently supports:
        - Single voice
        - Ties
        - In process (Dots)
    """
    #    start_time = timer()
    # TODO(Ryan): A traversal should only be broken up into parts IFF it is longer than the minimum length
    # Question of LENGTH of traversal vs Execution time
    # Question of SIZE of graph and indexing time

    doc = etree.parse(filename)

    part_list = get_part_information_from_music_xml(doc)

    for part in part_list:
        part.notes = get_part_notes(part.id, doc)

        print(part.notes)

        # TODO(Ryan): Make this more robust
        line_name = piece_name
        
        # TODO(Ryan): The MVP part of this just adds a single line from the piece...
        # This will eventually add ALL lines from the XML file
        # if line_name:
        #     new_line = graph_client.add_line(line_name)
        #     if not new_line:
        #         return
        
        # Create a new line
        traversal = g.addV('Line').property('name', line_name).as_('l')
     
        note_counter = 0
        new_notes = []

        last_note = None
        tie_flag = False

        for xml_note in part.notes:
            # raw_note_info = line.strip('\n').split(' ')?
            
            note = Note(xml_note.name, xml_note.length, xml_note.dot)
            print(note)

            traversal = traversal.addV(note.label)
            for prop, value in note.__dict__.items():
                if prop != 'id':
                    traversal = traversal.property(prop, value)

            # Create alias for each new note so we can add edges
            note_alias = 'n_{0}'.format(note_counter)
            traversal = traversal.as_(note_alias)
            new_notes.append(note_alias)
            note_counter += 1
            
            if tie_flag:
                print("Add tie")
                
                traversal = traversal.addE('tie').from_(new_notes[-2]).to(note_alias)
                print(traversal)
                tie_flag = False

            if xml_note.tied:
                tie_flag = True
                print(xml_note.tied)

        # Add edges
        traversal = traversal.addE('start').from_('l').to('n_0') \
                         .addE('in_line').from_('l').to('n_0') 

        for n0, n1 in zip(new_notes, new_notes[1:]):
            traversal = traversal.addE('next').from_(n0).to(n1) \
                                 .addE('in_line').from_('l').to(n1)
    
        # ISSUE: NEED to deal w/ max frame length of 65536!!!!
        print(traversal)
        print(len(new_notes))
    #        execute_traversal(traversal)

        print('Line {0} ({1} notes) added'.format('Test', len(new_notes)))
        return traversal


def add_tie_to_prev_note(g, current_note):
    """Tie the current note to the previous note in the line."""
    g.V(current_note.id).as_('end').in_('next').addE('tie').to('end').next()
    print('Added tie')  



if __name__ == "__main__":
    print('Test of Gremlin graph build.')
    graph = Graph()
    server_uri = 'ws://localhost:8182/gremlin'
    g = graph.traversal().withRemote(DriverRemoteConnection(server_uri, 'g'))
    
    # n0 = Note('D4', 3, 0)
    # n1 = Note(name='D5')
 
    # new_note = add_note(g, n0)
    # returned_note = get_note(g, n0)

    note_list = [Note('D3', 4, 0),  Note('F3', 4, 0), Note('A3', 2, 0)]
    test = add_line_iterative(g, note_list, 'test')
    # x = get_line_and_notes(g, 'test')    

    # drop_line(g, 'test')
    # y = get_line(g, 'test')

    # Build a line from an xml file
    # filename = 'scores/BachCelloSuiteDminPrelude.xml'
    # traversal = build_lines_from_xml(g, filename, 'bach_cello')


    # C
    # # This logic isnt' perfect, but should work for now
    # # TODO(Ryan): Make more robust Line creation and matching logic
    # args = {'new_name': note.name,
    #         'new_length': note.length,
    #         'new_dot': note.dot,
    #         'new_pitch_class': note.pitch_class,
    #         'new_octave': note.octave,
    #         'new_uuid': note.uuid}

    # if prev_note and not line_name:
    #     query = """MATCH (prev:Note {uuid: {prev_uuid}})
    #                MERGE (prev)-[rel:NEXT]->(new:Note {name: {new_name},
    #                                      length: {new_length},
    #                                      dot: {new_dot},
    #                                      pitch_class: {new_pitch_class},
    #                                      octave: {new_octave},
    #                                      uuid: {new_uuid}})
    #                RETURN prev, rel, new"""

    #     args['prev_uuid'] = prev_note.uuid

    # elif not line_name:
    #     query = """CREATE (new:Note {name: {new_name},
    #                        length: {new_length},
    #                        dot: {new_dot},
    #                        pitch_class: {new_pitch_class},
    #                        octave: {new_octave},
    #                        uuid: {new_uuid}})
    #                RETURN new"""

    # elif prev_note and line_name:
    #     query = """MATCH (prev:Note {uuid: {prev_uuid}}), (line:Line {name: {line_name}})
    #                MERGE (prev)-[rel:NEXT]->(new:Note {name: {new_name},
    #                                      length: {new_length},
    #                                      dot: {new_dot},
    #                                      pitch_class: {new_pitch_class},
    #                                      octave: {new_octave},
    #                                      uuid: {new_uuid}})-[l:IN_LINE]->(line)
    #                RETURN prev, rel, new, l, line"""

    #     args['prev_uuid'] = prev_note.uuid
    #     args['line_name'] = line_name

    # elif line_name:
    #     query = """ MATCH (line:Line {name: {line_name}})
    #                 MERGE (new:Note {name: {new_name}, 
    #                                length: {new_length},
    #                                dot: {new_dot},
    #                                pitch_class: {new_pitch_class},
    #                                octave: {new_octave},
    #                                uuid: {new_uuid}})-[l:IN_LINE]->(line)-[:START]->(new)
    #                 RETURN new"""
    #                            
    #     args['line_name'] = line_name

    # results = self._cypher(query, args)

    # # Get more specific about these results I think...
    # if not results.peek():
    #     print("Nothing added")
    #     return

    # for record in results:
    #     print("Note {0} added".format(record["new"]["name"]))
    #     return Note(from_properties=record["new"].properties)



# if __name__ == "__main__":
#     print('Test of Gremlin graph build.')
#     graph = Graph()
#     server_uri = 'ws://localhost:8182/gremlin'
#     g = graph.traversal().withRemote(DriverRemoteConnection(server_uri, 'g'))
# 
#     # l0 = g.V().next()
# 
#     print("Building sample graph.")
# 
#     n0 = build_note('D4', 3, 0)
#     
#     n1 = Note(name='D5')
# 
#     new_note = add_note(g, n0)
    # Create notes
    # n0 = g.addV('Note').property('name', 'D3').\
    #                     property('pitchClass', 'D').\
    #                     property('octave', 3).\
    #                     property('length', 8).\
    #                     property('dot', 0).next()

    # n1 = g.addV('Note').property('name', 'F3').\
    #                     property('pitchClass', 'F').\
    #                     property('octave', 3).\
    #                     property('length', 8).\
    #                     property('dot', 0).next()

#    n2 = g.addV('Note').property('name', 'A3').
#                        property('pitchClass', 'A').
#                        property('octave', 3).
#                        property('length', 4).
#                        property('dot', 0).next()
#
#    n3 = g.addV('Note').property('name', 'A3').
#                        property('pitchClass', 'A').
#                        property('octave', 3).
#                        property('length', 1).
#                        property('dot', 0).next()
#
#    n4 = g.addV('Note').property('name', 'F3').
#                        property('pitchClass', 'F').
#                        property('octave', 3).
#                        property('length', 16).
#                        property('dot', 0).next()
#
#    n5 = g.addV('Note').property('name', 'E3').
#                        property('pitchClass', 'E').
#                        property('octave', 3).
#                        property('length', 16).
#                        property('dot', 0).next()
#
#    n6 = g.addV('Note').property('name', 'D3').
#                        property('pitchClass', 'D').
#                        property('octave', 3).
#                        property('length', 16).
#                        property('dot', 0).next()
#
#    # Create ordering relationships
#    g.addE('start').from(l0).to(n0).next()
#    g.addE('next').from(n0).to(n1).next()
#    g.addE('next').from(n1).to(n2).next()
#    g.addE('next').from(n2).to(n3).next()
#    g.addE('next').from(n3).to(n4).next()
#    g.addE('next').from(n4).to(n5).next()
#    g.addE('next').from(n5).to(n6).next()
#
#    # Add ties
#    g.addE('tie').from(n2).to(n3).next()
#
#    print('MVP Graph loaded')
#
#    # Get the notes in order for our line
#    temp1 = g.V().hasLabel('Line').has('name', 'bachCello').out('start').next()
#    temp2 = g.V(temp1).out('next').next()
#    
