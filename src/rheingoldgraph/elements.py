# Music Graph build test in Gremlin
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
# import goblin

# #class Line):
#     """A Line Vertex.
#     """
#     # name = goblin.Property(goblin.String)
# 
#     def __repr__(self):
#         return "Line(name={0!r}".format(self.name)
# 

# I need to make progres, so I'm building out my own classes
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


def add_note(g, note, prev_note=None, line_name=None):
    """Add a Note vertex to the graph.

    Args:
        g: graph traversal source
        note: a Note object
        prev_note: a Note object
        line_name: name of the line to add notes to
    """

    if prev_note is None and line_name is None:
        traversal = g.addV(note.label)
        for prop, value in note.__dict__.items():
            if prop != 'id':
                traversal = traversal.property(prop, value)

        added_note = traversal.next()

    return added_note


def add_line(g, note_list):
    """Add a series of Notes to the graph

    g: GraphTraversalSource
    note_list: list of Notes (ordered)
    """
    traversal = g.addV(note_list[0].label)
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
    for n0, n1 in zip(new_notes, new_notes[1:]):
        traversal.addE('next').from_(n0).to(n1)
    
    traversal.next()
    print('Line {0} and {1} notes added'.format('Test', len(new_notes)))


def get_note(g, note):
    """get a Note vertex from the graph.
    """
    traversal = g.V(10).hasLabel(note.label)
    vertex = traversal.next()
    result = g.V(vertex.id).as_('v').properties().as_('p').select('v', 'p').toList() 
   
    print(result)

    # Build our note dict of properties
    vertex = result[0]['v']
    
    prop_dict = {prop['p'].key: prop['p'].value for prop in result}

    prop_dict['id'] = vertex.id

    print(prop_dict)

    # There's a more elegant way to build new notes, but I'll add it later
    note = Note()
    for key, value in prop_dict.items():
        setattr(note, key, value)
        print(note)

    return note
   
     
if __name__ == "__main__":
    print('Test of Gremlin graph build.')
    graph = Graph()
    server_uri = 'ws://localhost:8182/gremlin'
    g = graph.traversal().withRemote(DriverRemoteConnection(server_uri, 'g'))
    
    n0 = Note('D4', 3, 0)
    n1 = Note(name='D5')
 
    new_note = add_note(g, n0)
    returned_note = get_note(g, n0)

    add_line(g, [Note('D3', 4, 0),  Note('F3', 4, 0), Note('A3', 2, 0)])

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
