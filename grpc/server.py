import grpc
from concurrent import futures
import time

# Import the generated code
import service_pb2
import service_pb2_grpc

# 1. Implement the service logic
class UserLookupServicer(service_pb2_grpc.UserLookupServicer):

    def GetUser(self, request, context):
        print(f"Server received request for User ID: {request.id}")

        # Mock database lookup
        if request.id == 1:
            # We return the Protobuf message object defined in Step 1
            return service_pb2.UserResponse(
                id=1,
                username="john_doe",
                email="john_doe@example.com",
                is_active=True
            )
        else:
            # Handling errors in gRPC
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('User not found')
            return service_pb2.UserResponse()
        
# 2. Boilerplate to start the server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_UserLookupServicer_to_server(UserLookupServicer(), server)
    server.add_insecure_port('[::]:50051')
    print("Starting gRPC server on port 50051...")
    server.start()
    print("gRPC server is running on port 50051...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
            