"""RheingoldGraph MusicXML Parser"""

from collections import namedtuple
import os
import uuid
import re
from timeit import default_timer as timer

from lxml import etree

# XMLPart = namedtuple('Part', ['id', 'name'])
# XMLNote = namedtuple('Note', ['step', 'octave', 'alter'])

# An XML note that is interpretable on a stand-alone basis
XMLNote = namedtuple('Note', ['name', 'length', 'dot', 'tied'])

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


# TODO(Ryan): Write chord support
# TODO(Ryan): Write backup support

class XMLPart(object):
    """MusicXML Part representation."""
    def __init__(self, part_id, name):
        self.id = part_id
        self.name = name
        self.notes = []


def get_part_information_from_music_xml(doc):
    """Get part information from a MusicXML file.

    Finds Part names and IDs from the the MusicXML part-list element.

    Args:
        doc: lxml Element Tree from xml file
    Returns:
        part_list: list of XMLPart objects
    """
    # part_list = []

    # for p in doc.find('part-list').findall('score-part'):
    #     temp_part = XMLPart(p.get('id'), p.find('part-name').text)
    #     part_list.append(temp_part)

    part_list = [XMLPart(p.get('id'), p.find('part-name').text) for p \
                 in doc.find('part-list').findall('score-part')]

    return part_list


def get_part_notes(part_id, doc):
    """Get the notes for a specific part."""
    # TODO(Ryan): remove all xml references fro this module

    part_data = doc.find("part[@id='{0}']".format(part_id))

    # Set the division of the quarter
    # Technically, the divisions for each part could change after the first measure
    # Our initial parser assumes they remain constant
    divisions = int(part_data.find('measure/attributes/divisions').text)

    note_list = []

    for note in part_data.findall('measure/note'):

        # pitch_class = note_0.find('pitch/step').text
        # octave = int(note_0.find('pitch/octave').text)

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
        # Length is now interpreted from the note type, not the XML duration 
        # length = divisions * 4 / int(note.find('duration').text)
        # print(note.find('type').text)
        length = XML_LENGTH[note.find('type').text]
        # print(length)

        # Get dots
        dot = len(note.findall('dot'))

        # Check for tie
        if note.find("tie[@type='start']") is not None:
            tied = True
        else:
            tied = False

        note_list.append(XMLNote(note_name, length, dot, tied))

    return note_list


if __name__ == '__main__':
    filename = '../../xml/BachCelloSuiteDminPrelude.xml'
    doc = etree.parse(filename)

    part_list = get_part_information_from_music_xml(doc)

    for part in part_list:
        part.notes = get_part_notes(part.id, doc)

        print(part.notes)

    # print(part_list)

    # note_0 = part_data.find('measure/note')
    # print(note_0)

    # # pitch_class = note_0.find('pitch/step').text
    # # octave = int(note_0.find('pitch/octave').text)

    # length = int(divisions * 4 / int(note_0.find('duration').text))

    # note_name = note_0.find('pitch/step').text + note_0.find('pitch/octave').text

    # print(note_name, length)



    # This should pull the part by the previously defined part id
    # for part in parts:
    #     print(part.id)
    #     part_data = doc.find("part[@id='{0}']".format(part.id))
    #     print(part_data)


    #     # Set the division of the quarter
    #     # Technically, the divisions for each part could change after the first measure
    #     # Our initial parser assumes they remain constant
    #     divisions = int(part_data.find('measure/attributes/divisions').text)

    #     print(divisions)

    #     # Get all notes
    #     # notes = part_data.findall('measure/note')
    #     # print(notes)

    #     # Test this for a single note
    #     note_0 = part_data.find('measure/note')
    #     print(note_0)

    #     # pitch_class = note_0.find('pitch/step').text
    #     # octave = int(note_0.find('pitch/octave').text)

    #     length = int(divisions * 4 / int(note_0.find('duration').text))

    #     note_name = note_0.find('pitch/step').text + note_0.find('pitch/octave').text

    #     print(note_name, length)



    # part_data = doc.findall('part')[0]



    # print(divisions)

    # for measure in part_data[0:1]:
    #     for x in measure.findall('note'):
    #         print(x)

