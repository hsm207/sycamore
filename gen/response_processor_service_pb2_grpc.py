# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from gen import response_processor_service_pb2 as gen_dot_response__processor__service__pb2


class RemoteProcessorServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ProcessResponse = channel.unary_unary(
                '/RemoteProcessorService/ProcessResponse',
                request_serializer=gen_dot_response__processor__service__pb2.ProcessResponseRequest.SerializeToString,
                response_deserializer=gen_dot_response__processor__service__pb2.ProcessResponseResponse.FromString,
                )


class RemoteProcessorServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ProcessResponse(self, request, context):
        """Processes a search response
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RemoteProcessorServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ProcessResponse': grpc.unary_unary_rpc_method_handler(
                    servicer.ProcessResponse,
                    request_deserializer=gen_dot_response__processor__service__pb2.ProcessResponseRequest.FromString,
                    response_serializer=gen_dot_response__processor__service__pb2.ProcessResponseResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'RemoteProcessorService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class RemoteProcessorService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ProcessResponse(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/RemoteProcessorService/ProcessResponse',
            gen_dot_response__processor__service__pb2.ProcessResponseRequest.SerializeToString,
            gen_dot_response__processor__service__pb2.ProcessResponseResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
