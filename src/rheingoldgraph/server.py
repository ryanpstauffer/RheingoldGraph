"""RheingoldGraph gRPC Server."""
from concurrent import futures
import time


# import asyncio
# import os
# import signal
# import websockets

import grpc

import rheingoldgraph.proto.rheingoldgraph_pb2 as rgpb
import rheingoldgraph.proto.rheingoldgraph_pb2_grpc as rgrpc
from rheingoldgraph.session import Session


class RheingoldGraphService(rgrpc.RheingoldGraphServicer):

    def __init__(self):
        gremlin_server_uri = 'ws://localhost:8189/gremlin'
        self.session = Session(gremlin_server_uri)


    def GetSummary(self, request, context):
        summary = self.session.graph_summary() 

        return summary


    def GetPlayableLine(self, request, context):
        # TODO(ryan): We currently have stacked generators
        # Clean this up!
        notes = self.session.get_playable_line(request.name) 
        for note in notes:
            yield note 


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rgrpc.add_RheingoldGraphServicer_to_server(RheingoldGraphService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(1200)
    except KeyboardInterrupt:
        server.stop(0)

     

# async def command_loop(ws, path):
#     gremlin_server_uri = 'ws://localhost:8189/gremlin'
#     session = Session(gremlin_server_uri)
#     # Start with string messages, then move on to serialized protobuf...
#     while True:
#         try:
#             msg = await ws.recv()
#             print('< {0}'.format(msg))
#             if msg == 'summary':
#                 print('View Summary')
#                 session.graph_summary()
#         except websockets.ConnectionClosed:
#             pass
#         else:
#             await ws.send(msg)
#             print('> {0}'.format(msg))
# 
# 
# async def rheingoldgraph_server(stop):
#     async with websockets.serve(command_loop, 'localhost', 8765):
#         await stop
#         print('Shutting down server')


if __name__ == '__main__':
    serve()
#     loop = asyncio.get_event_loop()
# 
#     print('RheingoldGraph command loop running, press Ctrl+C to interrupt.')
#     print('pid {0}: send SIGTERM to exit.'.format(os.getpid())) 
#     # Stop condition is set when receiving SIGTERM
#     stop = asyncio.Future()
#     loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)
# 
#     # Run the server until the stop condition is met.
#     loop.run_until_complete(rheingoldgraph_server(stop))
