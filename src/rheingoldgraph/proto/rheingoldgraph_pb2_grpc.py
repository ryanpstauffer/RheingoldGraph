# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import rheingoldgraph.proto.music_pb2 as music__pb2
import rheingoldgraph.proto.rheingoldgraph_pb2 as rheingoldgraph__pb2


class RheingoldGraphStub(object):
  """RheingoldGraph service definition.
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetSummary = channel.unary_unary(
        '/rheingoldgraph.RheingoldGraph/GetSummary',
        request_serializer=rheingoldgraph__pb2.SummaryRequest.SerializeToString,
        response_deserializer=rheingoldgraph__pb2.GraphSummary.FromString,
        )
    self.GetPlayableLine = channel.unary_stream(
        '/rheingoldgraph.RheingoldGraph/GetPlayableLine',
        request_serializer=rheingoldgraph__pb2.LineRequest.SerializeToString,
        response_deserializer=music__pb2.Note.FromString,
        )


class RheingoldGraphServicer(object):
  """RheingoldGraph service definition.
  """

  def GetSummary(self, request, context):
    """Get a summary of musical information stored in our graph.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def GetPlayableLine(self, request, context):
    """Get a sequence of ProtoBuf Notes for a playable line
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_RheingoldGraphServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetSummary': grpc.unary_unary_rpc_method_handler(
          servicer.GetSummary,
          request_deserializer=rheingoldgraph__pb2.SummaryRequest.FromString,
          response_serializer=rheingoldgraph__pb2.GraphSummary.SerializeToString,
      ),
      'GetPlayableLine': grpc.unary_stream_rpc_method_handler(
          servicer.GetPlayableLine,
          request_deserializer=rheingoldgraph__pb2.LineRequest.FromString,
          response_serializer=music__pb2.Note.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'rheingoldgraph.RheingoldGraph', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))