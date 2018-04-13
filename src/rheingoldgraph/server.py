"""RheingoldGraph gRPC Server."""
from concurrent import futures
import time

import grpc
from absl import app
from absl import flags

import rheingoldgraph.protobuf.rheingoldgraph_pb2 as rgpb
import rheingoldgraph.protobuf.rheingoldgraph_pb2_grpc as rgrpc
from rheingoldgraph.elements import Header
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
        # TODO(ryan): We currently have stacked generators
        # Clean this up!
        notes = self.session.get_playable_line_new(request.name) 
        for note in notes:
            yield note 


    def DropLine(self, request, context):
        drop_response = self.session.drop_line(line_name=request.name) 

        return drop_response


    def AddLinesFromXML(self, request, context):
        add_response = self.session.add_lines_from_xml(request.xml, request.piece_name) 

        return add_response


    def SearchLines(self, request, context):
        # TODO(ryan): better serde for ProtoBuf to graph
        search_header = Header()
        if request.created_date != '':
            search_header.created_date = request.created_date
        if request.composer != '':
            search_header.composer = request.composer 
        if request.session_id > 0:
            search_header.session_id = request.session_id
        lines = self.session.search_lines_by_header_data(search_header) 
        for line in lines:
            yield rgpb.Line(name=line.name)


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
