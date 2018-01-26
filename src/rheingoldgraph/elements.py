# Music Graph build test in Gremlin
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
# import goblin

# Hopefully can eventually inherit from goblin?

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
   
