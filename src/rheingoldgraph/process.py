# Music Graph process prototype 
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
# import goblin

from lxml import etree
from musicxml import get_part_information_from_music_xml, get_part_notes

from rheingoldgraph.elements import Line, Note

 
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


def build_lines_from_xml_iterative(g, filename, piece_name=None):
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

        # TODO(Ryan): Make this more robust
        line_name = piece_name
        
        # Create a new line if it doesn't already exist
        line = find_line(g, line_name)
        if line:
            # TODO(Ryan): Should return error
            print("Line already exists")
            return
        else:
            # Should return a line object, but getting there...
            line = g.addV('Line').property('name', line_name).next()

        # Add notes to the line 
        note_counter = 0
        prev_note = None
        tie_flag = False
        for xml_note in part.notes:
            note = Note(xml_note.name, xml_note.length, xml_note.dot)
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

                if tie_flag:
                    print("Add tie")
                    traversal = traversal.addE('tie').from_('prev').to('new')
                    tie_flag = False

            traversal = traversal.addE('in_line').from_('new').to('l')

            # Get recently added note
            # This should be a full Note object
            prev_note = traversal.select('new').next() 
            note_counter += 1
    
            if xml_note.tied:
                tie_flag = True
                print(xml_note.tied)

        print('Line {0} ({1} notes) added'.format(line_name, note_counter))


if __name__ == "__main__":
    print('Test of Gremlin graph build.')
    graph = Graph()
    server_uri = 'ws://localhost:8182/gremlin'
    g = graph.traversal().withRemote(DriverRemoteConnection(server_uri, 'g'))
    
    # n0 = Note('D4', 3, 0)
    # n1 = Note(name='D5')
 
    # new_note = add_note(g, n0)
    # returned_note = get_note(g, n0)

    # note_list = [Note('D3', 4, 0),  Note('F3', 4, 0), Note('A3', 2, 0)]
    # test = add_line_iterative(g, note_list, 'test')
    # x = get_line_and_notes(g, 'test')    

    # drop_line(g, 'test')
    # y = get_line(g, 'test')

    # Build a line from an xml file
    filename = 'scores/BachCelloSuiteDminPrelude.xml'
    traversal = build_lines_from_xml_iterative(g, filename, 'bach_cello')


