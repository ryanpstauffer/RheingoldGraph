"""RheingoldGraph MusicXML Parser - Prototype

This module currently supports parsing of monophonic lines from Music XML files.
"""
from collections import namedtuple
from lxml import etree

from rheingoldgraph.elements import Note

### Define namedtuples and global variables

# An XML note that is interpretable on a stand-alone basis
# XMLNote = namedtuple('XMLNote', ['name', 'length', 'dot', 'tied'])
# Trying this...
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

### Define additional functions
def get_part_information_from_music_xml(doc):
    """Get part information from a MusicXML file.

    Finds Part names and IDs from the the MusicXML part-list element.

    Args:
        doc: lxml Element Tree from xml file
    Returns:
        part_list: list of XMLPart objects
    """
    parts = [XmlPart(p.get('id'), p.find('part-name').text) for p \
                     in doc.find('part-list').findall('score-part')]

    return parts


def parse_xml(filename):
    doc = etree.parse(filename)

    part_list = get_part_information_from_music_xml(doc)

    for part in part_list:
        part.notes = get_part_notes(part.id, doc)

        print(part.notes)


def get_part_note_generator(part_id, doc):
    """Get the notes for a specific part."""
    part_data = doc.find("part[@id='{0}']".format(part_id))

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

        yield XMLNote(Note(note_name, length, dot), tied)


def get_parts_from_xml(filename):
    """Get a list of XmlParts from an XML file.

    Each part has an id, name and generator of XmlNotes, which include a Note object and tied flad
    """     
    doc = etree.parse(filename)
    parts = get_part_information_from_music_xml(doc)

    for part in parts:
        part.notes = get_part_note_generator(part.id, doc) 

    return parts 


if __name__ == '__main__':
    filename = 'scores/BachCelloSuiteDminPrelude.xml'

    parts = get_parts_from_xml(filename) 

    # Consolidate this next from generator
    # for part in part_list:
    #     part.notes = get_part_notes(part.id, doc)

    #     print(part.notes)

    #     # start_time = timer()
    #     # Fully separate out XML parsing into separate module
    #     doc = etree.parse(filename)

    #     part_list = get_part_information_from_music_xml(doc)

    #     for part in part_list:
    #         part.notes = get_part_notes(part.id, doc)

    #         # TODO(ryan): Make this more robust
    #         if len(part_list) == 1:
    #             line_name = piece_name
    #         else:
    #             line_name = '{0}_{1}'.format(piece_name, part.id)

    #         # Check if line already exists
    #         if self.find_line(line_name):
    #             print("Line already exists")
    #             raise LineAlreadyExists

    #         # TODO(ryan): Should return a line object, but getting there...
    #         line = self.g.addV('Line').property('name', line_name).next()

    #         # Add notes to the line
    #         note_counter = 0
    #         prev_note = None
    #         tie_flag = False
    #         for xml_note in part.notes:
    #             note = Note(xml_note.name, xml_note.length, xml_note.dot)

    #             # Different traversal depending if this is the first note of the line
    #             if prev_note is None:
    #                 traversal = self.g.V(line.id).as_('l')
    #                 traversal = self._add_note_to_traversal(traversal, note)
    #                 traversal = traversal.addE('start').from_('l').to('new')
    #             else:
    #                 traversal = self.g.V(prev_note.id).as_('prev').out('in_line').as_('l')
    #                 traversal = self._add_note_to_traversal(traversal, note)
    #                 traversal = traversal.addE('next').from_('prev').to('new')

    #                 if tie_flag:
    #                     traversal = traversal.addE('tie').from_('prev').to('new')
    #                     tie_flag = False

    #             traversal = traversal.addE('in_line').from_('new').to('l')

    #             # Get recently added note
    #             # This should be a full Note object
    #             prev_note = traversal.select('new').next()
    #             note_counter += 1

    #             if xml_note.tied:
    #                 tie_flag = True

    #         print('Line {0} ({1} notes) added'.format(line_name, note_counter))


