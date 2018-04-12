"""RheingoldGraph elements module."""

import pretty_midi
from rheingoldgraph.proto import music_pb2
# from magenta.protobuf import music_pb2

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


class Vertex:
    """Generic RheingoldGraph OGM Vertex element."""
 
    @property
    def id(self):
        return self._id


    def __repr__(self):
        property_list = ['{0}={1!r}'.format(key, getattr(self, key, None))
                         for key in self._properties]
        return '{0}({1})'.format(self.label, ', '.join(property_list))


    def __eq__(self, other):
        """Equality does not depend on ID within the Database
        Ex: Note('D3', 4.0, 0) == Note('D3', 4.0, 0)
        regardless of ID in the database
        """
        if isinstance(other, self.__class__):
            return self.property_dict() == other.property_dict()
        else:
            return False


    def property_dict(self):
        return {key: getattr(self, key, None) for key in self._properties}


    @classmethod
    def from_dict(cls, mapping):
        """Alternate constructor for Vertex classes."""
        mapping = mapping.copy()
        mapping.pop('label')

        vertex = cls.__new__(cls)
        vertex._id = mapping.pop('id', None)
        for key, value in mapping.items():
            setattr(vertex, key, value)

        return vertex


class Line(Vertex):
    """A Line Vertex."""
    label = 'Line'
    name = PropertyDescriptor('name')

    _properties = ['name']

    def __init__(self, name=None):
        self.name = name
        self._id = None


    def __repr__(self):
        return "Line(name={0!r})".format(self.name)


class Note(Vertex):
    """A Note Vertex.
    """
    label = 'Note'

    name = PropertyDescriptor('name')
    length = PropertyDescriptor('length')
    dot = PropertyDescriptor('dot')

    _properties = ['name', 'length', 'dot']

    def __init__(self, name=None, length=None, dot=None):
        self.name = name
        self.length = length
        self.dot = dot
        self._id = None


    def to_protobuf(self):
        """Protocol Buffer output."""
        # TODO(ryanstauffer): Confirm that we need this
        note = music_pb2.NoteSequence.Note()
        note.pitch = pretty_midi.note_name_to_number(self.name)
        note.denominator = self.length

        return note
