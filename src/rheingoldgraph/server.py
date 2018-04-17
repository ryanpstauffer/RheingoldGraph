"""RheingoldGraph gRPC Server."""
from concurrent import futures
import time

import grpc
from absl import app
from absl import flags

import rheingoldgraph.protobuf.rheingoldgraph_pb2 as rgpb
import rheingoldgraph.protobuf.rheingoldgraph_pb2_grpc as rgrpc
from rheingoldgraph.elements import Header, Note, Line
from rheingoldgraph.session import Session

flags.DEFINE_string(
    'gremserv_uri', 'ws://localhost:8189/gremlin',
    'URI of a running gremlin server instance.')
flags.DEFINE_string(
    'port', '50051',
    'Port on which to receive RheingoldGraphServer connections.')

FLAGS = flags.FLAGS

class RheingoldGraphService(rgrpc.RheingoldGraphServicer):

    def __init__(self, gremserv_uri):
        self.gremserv_uri = gremserv_uri
        self.session = Session(self.gremserv_uri)
        print('Connected to Gremlin Server at {0}'.format(self.gremserv_uri))


    def GetSummary(self, request, context):
        summary = self.session.graph_summary() 

        return summary


    def GetLine(self, request, context):
        graph_line = self.session.get_line(line_name=request.name) 

        header = rgpb.HeaderMetadata(
            created=graph_line.header.created, composer=graph_line.header.composer) 
        pb_line = rgpb.Line(name=graph_line.name, header=header)
        for n in graph_line.notes:
            pb_line.notes.add(name=n.name, length=n.length, dot=n.dot, tied=n.tied)

        return pb_line


    def DropLine(self, request, context):
        drop_response = self.session.drop_line(line_name=request.name) 

        return drop_response


    def SearchLines(self, request, context):
        # TODO(ryan): better serde for ProtoBuf to graph
        search_header = Header()
        if request.created != 0:
            search_header.created = request.created
        if request.composer != '':
            search_header.composer = request.composer 
        lines = self.session.search_lines_by_header_data(search_header) 
        for line in lines:
            yield rgpb.Line(name=line.name)


    def AddLine(self, request, context):
        # Deserialize pb notes to Note objects
        notes_list = [Note(name=n.name, length=n.length, dot=n.dot) for n in request.notes]

        # Populate header
        header = Header()
        if request.header.created != 0:
            header.created = request.header.created
        if request.header.composer != '':
            header.composer = request.header.composer 

        line = Line(name=request.name, notes=notes_list, header=header)
        num_notes_added = self.session.add_line(line)
        summary = rgpb.LineSummary(name=line.name, vertices=num_notes_added)

        return summary


def main(_):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rgrpc.add_RheingoldGraphServicer_to_server(
        RheingoldGraphService(FLAGS.gremserv_uri), server)
    server.add_insecure_port('[::]:{0}'.format(FLAGS.port))
    server.start()
    print('Running RheingoldGraphServer on localhost:{0}'.format(FLAGS.port))
    try:
        while True:
            time.sleep(1200)
    except KeyboardInterrupt:
        print('Shutting down RheingoldGraphServer')
        server.stop(0)

     
if __name__ == '__main__':
    app.run(main)
