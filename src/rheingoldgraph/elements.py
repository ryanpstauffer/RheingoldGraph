# RheingoldGraph elements module 
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
# Hopefully can eventually inherit from goblin?
# import goblin

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
        note = music_pb2.NoteSequence.Note() 
        note.pitch = 50
        note.denominator = self.length
        
        return note


class PlayableNote:
    """A Note Vertex.
    Properties:
        name: Concatenated Pitch Class and Octave, ex: 'C4' or 'R' if a rest
        duration: Number of ticks a note is held for
    """
    label = 'PlayableNote' 

    name = PropertyDescriptor('name')
    duration = PropertyDescriptor('duration')

    _properties = ['name', 'duration']

    def __init__(self, name=None, duration=None):
        self.name = name
        self.duration = duration
        self._id = None


    @property
    def id(self):
        return self._id
 

    def __repr__(self):
        return "PlayableNote(name={0!r}, duration={1!r})".format(self.name, self.duration)

    
    def __eq__(self, other):
        # Equality does not depend on ID within the Database 
        # Ex: PlayableNote('D3', , 0) == Note('D3', 4.0, 0) REGARDLESS of ID in the database
        if isinstance(other, PlayableNote):
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
        play  = PlayableNote()
        play._id  = mapping.pop('id', None)
        # There's a more elegant way to build new notes w/ error handling, but I'll add it later
        for key, value in mapping.items():
            setattr(play, key, value)

        return play


    @classmethod
    def from_note(cls, note_dict, ticks_per_beat):
        note_dict = note_dict.copy()
        play = PlayableNote()
        # No ID
        play.name = note_dict['name']
        play.duration = 1/note_dict['length'] * (2 - (1 / 2**note_dict['dot'])) * 4 * ticks_per_beat 

        return play

    #  def get_midi_playable_line(self, line_name):
    #     """Get all notes in a given line in Midi-playable format.

    #     This method converts all ties to single notes of consistent length.

    #     Args:
    #         line_name: name of the line to get
    #     Returns:
    #         list of 
    #     """
    #     # Check if line exists
    #     if not self.get_node_by_name(line_name, 'Line'):
    #         print("Line {0} does not exist".format(line_name))
    #         return

    #     # Note that 'Binding relationships to a list in a variable length pattern is deprecated.'
    #     # TODO(Ryan): Rewrite using new Neo4j canonical form
    #     query = """MATCH (line:Line {name:{line_name}})-[r:START_PLAY|NEXT*]->(note:PlayableNote)
    #                 RETURN note, size(r) AS Dist
    #                 ORDER BY Dist"""

    #     args = {'line_name': line_name}
    #     results = self._cypher(query, args)

    #     return [PlayableNote(from_properties=record["note"].properties) for record in results]


 
