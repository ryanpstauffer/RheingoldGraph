"""RheingoldGraph gRPC Client."""

# import asyncio
# import websockets

from __future__ import print_function

import grpc

import rheingoldgraph.protobuf.rheingoldgraph_pb2 as rgpb
import rheingoldgraph.protobuf.rheingoldgraph_pb2_grpc as rgrpc

from rheingoldgraph.elements import Line, Note, Header

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

        # TODO(ryan): handle Header
        line = Line(name=pb_line.name)
        notes_list = [Note(
            name=n.name, length=n.length, dot=n.dot, tied=n.tied) for n in pb_line.notes] 
        line.notes = notes_list

        return line


    def drop_line(self, line_name):
        """Drop a line."""
        drop_request = rgpb.LineRequest(name=line_name)
        return self.stub.DropLine(drop_request)


    def search_lines(self, *, created_date=None, composer=None, session_id=None):
        """Search lines by header metadata."""
        header = rgpb.HeaderMetadata()
        if created_date:
            header.created_date = created_date
        if composer:
            header.composer = composer
        if session_id:
            header.session_id = session_id

        return list(self.stub.SearchLines(header))


    def add_line(self, line):
        """Add a line with notes and optional header metadata)."""
        pb_line = rgpb.Line(name=line.name)
        # TODO(ryan): Add back in header support
        # if line.header:
        #     header = rgpb.HeaderMetadata(created_date=line.header.created_date,
        #                                  composer=line.header.composer,
        #                                  session_id=line.header.session_id)
        #     pb_line.header = header
        # Serialize notes
        for note in line.notes:
            pb_line.notes.add(name=note.name, length=note.length, dot=note.dot)      
        
        line_summary = self.stub.AddLine(pb_line) 
        print(line_summary)


if __name__ == '__main__':
    server_uri = 'localhost:50051'
    client = RheingoldGraphClient(server_uri)

