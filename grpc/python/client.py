import grpc
import service_pb2
import service_pb2_grpc

def run():
    # 1. Open a channel to the server
    with grpc.insecure_channel('localhost:50051') as channel:

        # 2. Create a stub (client)
        stub = service_pb2_grpc.UserLookupStub(channel)

        # 3. Create a valid request message
        request_payload = service_pb2.UserRequest(id=1)

        print(f"Client sending request for User ID: {request_payload.id}")

        try:
            # 4. Make the call
            response = stub.GetUser(request_payload)

            # 5. Process the response
            print("Client received response:")
            print(f"User ID: {response.id}")
            print(f"Username: {response.username}")
            print(f"Email: {response.email}")
            print(f"Is Active: {response.is_active}")
        except grpc.RpcError as e:
            print(f"gRPC Error: {e.code()} - {e.details()}")

if __name__ == '__main__':
    run()