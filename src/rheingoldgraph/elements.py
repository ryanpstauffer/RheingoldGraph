# RheingoldGraph elements module 
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
# Hopefully can eventually inherit from goblin?
# import goblin
import pretty_midi
from magenta.protobuf import music_pb2

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

    _properties = ['name', 'length', 'dot']

    # name = goblin.Property(goblin.String)
    # length = goblin.Property(goblin.Float) 
    # dot = goblin.Property(goblin.Integer, default=0)
    

    def __init__(self, name=None, length=None, dot=None):
        self.name = name
        self.length = length
        self.dot = dot
        self._id = None


    @property
    def id(self):
        return self._id
 

    def __repr__(self):
        return "Note(name={0!r}, length={1!r}, dot={2!r})".format(self.name, self.length, self.dot)

    
    def __eq__(self, other):
        # Equality does not depend on ID within the Database 
        # Ex: Note('D3', 4.0, 0) == Note('D3', 4.0, 0) REGARDLESS of ID in the database
        if isinstance(other, Note):
            return self.property_dict() == other.property_dict() 
        else:
            return False


    # Is this method necessary?
    def to_dict(self):
        return self.__dict__


    def property_dict(self):
        return {key: getattr(self, key, None) for key in self._properties}        


    @classmethod
    def from_dict(cls, mapping):
        mapping = mapping.copy()
        label = mapping.pop('label')
        # TODO(Ryan): Type should be determined from label
        note = Note()
        note._id  = mapping.pop('id', None)
        # There's a more elegant way to build new notes w/ error handling, but I'll add it later
        for key, value in mapping.items():
            setattr(note, key, value)

        return note


    def to_protobuf(self):
        """MVP of Protocol Buffer output."""
        # TODO(ryanstauffer): Figure out if we need this!
        note = music_pb2.NoteSequence.Note() 
        note.pitch = pretty_midi.note_name_to_number(self.name) 
        note.denominator = self.length
        
        return note

