"""RheingoldGraph gRPC Client."""

# import asyncio
# import websockets

from __future__ import print_function

import grpc

import rheingoldgraph.protobuf.rheingoldgraph_pb2 as rgpb
import rheingoldgraph.protobuf.rheingoldgraph_pb2_grpc as rgrpc

from rheingoldgraph.elements import Line, Note, Header
# for testing only
from rheingoldgraph.musicxml import XmlReader

class RheingoldGraphClient:
    """Remote client of RheingoldGraph."""
    def __init__(self, server_uri):
        channel = grpc.insecure_channel(server_uri) 
        self.stub = rgrpc.RheingoldGraphStub(channel)


    def get_summary(self):
        """Get a summary of the complete graph."""
        # TODO: Allow for subgraph summaries as well 
        summary_request = rgpb.SummaryRequest(line='bach_cello')

        return self.stub.GetSummary(summary_request) 

    
    def get_line(self, line_name): 
        """Get a logical Line with Notes""" 
        line_request = rgpb.LineRequest(name=line_name)
        pb_line = self.stub.GetLine(line_request)

        # Deserialize to Line, Notes, and Header objects
        # Build Header
        header = Header()
        if pb_line.header.created > 0:
            header.created = pb_line.header.created
        if pb_line.header.composer != '':
            header.composer = pb_line.header.composer 
        # Build Line and Notes
        line = Line(name=pb_line.name, header=header)
        notes_list = [Note(
            name=n.name, length=n.length, dot=n.dot, tied=n.tied) for n in pb_line.notes] 
        line.notes = notes_list

        return line


    def drop_line(self, line_name):
        """Drop a line."""
        drop_request = rgpb.LineRequest(name=line_name)
        return self.stub.DropLine(drop_request)


    def search_lines(self, *, created=None, composer=None):
        """Search lines by header metadata."""
        header = rgpb.HeaderMetadata()
        if created:
            header.created = created
        if composer:
            header.composer = composer

        return list(self.stub.SearchLines(header))


    def add_line(self, line):
        """Add a Line with Notes and optional Header metadata to the graph.

        Args:
            line: logical Line object with Notes and optional Header
        """
        pb_line = rgpb.Line(name=line.name)
        if line.header:
            header = rgpb.HeaderMetadata(created=line.header.created,
                                                 composer=line.header.composer)
            pb_line = rgpb.Line(name=line.name, header=header)
        # Serialize notes
        for note in line.notes:
            pb_line.notes.add(name=note.name, length=note.length, dot=note.dot)      
        
        line_summary = self.stub.AddLine(pb_line) 
        print(line_summary)


if __name__ == '__main__':
    server_uri = 'localhost:50051'
    client = RheingoldGraphClient(server_uri)
    # filename = '/Users/ryan/Projects/Rheingold/RheingoldGraph/scores/BachCelloSuiteDminPrelude.xml'
    # r = XmlReader(filename, 'bach_cello_xml_7')
    # client.add_line(r.lines[0])
