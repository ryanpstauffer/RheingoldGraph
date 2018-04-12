"""RheingoldGraph gRPC Client."""

# import asyncio
# import websockets

from __future__ import print_function

import grpc

import rheingoldgraph.proto.rheingoldgraph_pb2 as rgpb
import rheingoldgraph.proto.rheingoldgraph_pb2_grpc as rgrpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = rgrpc.RheingoldGraphStub(channel)
    
    summary_request = rgpb.SummaryRequest(line='bach_cello')
    summary = stub.GetSummary(summary_request) 
    print(summary)

    line_request = rgpb.LineRequest(name='bach_cello')
    notes = stub.GetPlayableLine(line_request)
    print(type(notes))
    for note in notes:
        print(note)
# async def get_summary(uri):
#     async with websockets.connect(uri) as ws:
#         msg = 'summary'
#         await ws.send(msg)
#         print('> {0}'.format(msg)) 
# 
#         summary = await ws.recv()
#         print('<\n{0}'.format(summary))

if __name__ == '__main__':
    run() 
#     asyncio.get_event_loop().run_until_complete(
#         get_summary('ws://localhost:8765')) 
