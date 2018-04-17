"""RheingoldGraph MusicXML Parser - Prototype

This module currently supports parsing of monophonic lines from Music XML files.
"""
from collections import namedtuple
from lxml import etree
import time

from rheingoldgraph.elements import Note, Line, Header
from rheingoldgraph.session import Session

### Define namedtuples and global variables
XMLNote = namedtuple('XMLNote', ['note', 'tied'])

# Note: Breve support is currently weak.  This should not affect the playability of most scores
XML_LENGTH = {'1024th': 1024,
              '512th': 512,
              '256th': 256,
              '128th': 128,
              '64th': 64,
              '32nd': 32,
              '16th': 16,
              'eighth': 8, 
              'quarter': 4, 
              'half': 2, 
              'whole': 1, 
              'breve': 1/2}

### Define classes
class XmlPart:
    """MusicXML Part representation."""
    def __init__(self, part_id, name):
        self.id = part_id
        self.name = name
        self.notes = []

class XmlReader:
    """Music XML Reader."""
    def __init__(self, filename, piece_name):
        self.filename = filename
        self.piece_name = piece_name
        self.composer = None
        self.parts = []
        self.lines = []

        # Read xml contents from string
        with open(filename, 'rb') as f:
            xml_string = f.read() 

        self.doc = etree.fromstring(xml_string)
        print(self.doc)

        # TODO(ryan): Simplify iteration here...
        self.parts = [XmlPart(p.get('id'), p.find('part-name').text) for p \
                      in self.doc.find('part-list').findall('score-part')]

        # Append notes to parts
        for part in self.parts:
            part.notes = self.get_part_notes(part.id) 

        # Build Logical lines
        self.lines = self.build_logical_lines(self.parts)
    

    def build_logical_lines(self, parts):
        lines = []
        for part in parts:
            line = Line()
            # TODO(ryan): Make this more robust
            if len(parts) == 1:
                line.name = self.piece_name
            else:
                line.name = '{0}_{1}'.format(piece_name, part.id)

            print(line.name)

            # Hardcode Header for testing
            created = int(time.time())
            composer = 'bach'
            line.header = Header(created, composer) 
          
            # Add notes to line 
            notes = []
            for note, tied_to_next in part.notes:
                new_note = note
                new_note.tied = tied_to_next
                notes.append(new_note)
            line.notes = notes

            # Finish line
            lines.append(line)            
 
        return lines 


    @classmethod
    def from_string(cls, xml_string):
        pass 
       

    def get_part_notes(self, part_id):
        """Get a list of all notes from a specific part."""
        part_data = self.doc.find("part[@id='{0}']".format(part_id))

        # Set the division of the quarter
        # Technically, the divisions for each part could change after the first measure
        # Our initial parser assumes they remain constant
        divisions = int(part_data.find('measure/attributes/divisions').text)
        note_list = []

        for note in part_data.findall('measure/note'):
            # Build note name
            if note.find('rest') is None:
                # Get pitch_class_base 
                pitch_class_base = note.find('pitch/step').text

                # Get accidental
                try:
                    alter = int(note.find('pitch/alter').text)
                    if alter == -1:
                        accidental = 'b'
                    elif alter == 1:
                        accidental = '#'
                except AttributeError:
                    accidental = ''

                # Get octave
                octave = note.find('pitch/octave').text

                note_name = pitch_class_base + accidental + octave

            else:
                note_name = 'R'

            # Build length
            # Length is interpreted from the note type, not the XML duration 
            length = XML_LENGTH[note.find('type').text]

            # Get dots
            dot = len(note.findall('dot'))

            # Check for tie
            if note.find("tie[@type='start']") is not None:
                tied = True
            else:
                tied = False

            note_list.append(XMLNote(Note(note_name, length, dot), tied))

        return note_list


    def get_parts_from_xml_string(xml_string):
        """Get a list of XmlParts from an XML string.

        Each part has an id, name and generator of XmlNotes, which include a Note object and tied flad
        """
        print(xml_string)
        doc = etree.fromstring(xml_string)
        print(doc)
        parts = get_part_information_from_music_xml(doc)

        for part in parts:
            part.notes = get_part_note_generator(part.id, doc) 

        return parts 


    def get_parts_from_xml(filename):
        """Get a list of XmlParts from an XML file.

        Each part has an id, name and generator of XmlNotes, which include a Note object and tied flad
        """
        doc = etree.parse(filename)
        parts = get_part_information_from_music_xml(doc)

        for part in parts:
            part.notes = get_part_note_generator(part.id, doc) 

        return parts 

 
    def add_lines_from_xml(self, xml_string):
        """Add lines in graph from an xml string.

        Currently supports monophonic parts

        Args:
            xml_string: byte string of XML 
            piece_name: Name to give the piece of music,
                        used for constructing line names
        """
        parts = get_parts_from_xml_string(xml_string)

        for part in parts:
            # TODO(ryan): Make this more robust
            if len(parts) == 1:
                line_name = piece_name
            else:
                line_name = '{0}_{1}'.format(piece_name, part.id)

            print(line_name)

            # Hardcode Header for testing
            # TODO(ryan): We should add notes to a local representation of our line
            # THEN add the line ot the graph
            header = Header('2018-04-12', 'bach', 1859)
            line = Line(name=line_name, header=header)
            line = self._add_line(line)
            # line = self._add_line(line_name, header)
            # print(line)

            # Add notes to the line
            note_counter = 0
            prev_note = None
            tie_flag = False
            # Can I generalize this more?
            for note, tied_to_next in part.notes:
                prev_note = self._add_note(line, note, prev_note, tie_flag)

                tie_flag = tied_to_next
                note_counter += 1

            print('Line {0} ({1} notes) added'.format(line_name, note_counter))
            return rgpb.AddResponse(name=line_name, success=True, notes_added=note_counter)


if __name__ == '__main__':
    filename = '/Users/ryan/Projects/Rheingold/RheingoldGraph/scores/BachCelloSuiteDminPrelude.xml'
    r = XmlReader(filename, 'bach_cello_xml_3')
    sess = Session('ws://localhost:8189/gremlin')
    # sess.add_line_and_notes(
