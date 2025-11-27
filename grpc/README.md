## Setup

```bash
# 1. Install uv (if you haven't)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Initialize the current directory
# This creates a pyproject.toml and a .python-version file
uv init . 

# 3. Add the dependencies
# This creates/updates uv.lock and installs into a .venv automatically
uv add grpcio grpcio-tools
```

## Simple gRPC Service

### Step 1: Protocol Buffers

Create a file called `service.proto`. This will define the API.

```protobuf
syntax = "proto3";

package users;

// The service definition (like an Interface/Abstract Base Class)
service UserLookup {
    // A standard unary RPC (one request, one response)
    rpc GetUser (UserRequest) returns (UserResponse);
}

// The data structures
message UserRequest {
    int32 id = 1;
}

message UserResponse {
    int32 id = 1;
    string username = 2;
    string email = 3;
    bool is_active = 4;
}
```

Note on tags: The = 1, = 2 are not values; they are unique binary tags used for serialization. Once assigned, you should not change them to maintain backward compatibility.

### Step 2: The Automation (`taskfile.yaml`)

Our taskfile will help us define commonly used commands and simplify aspects like compiling gRPC in Python.

```yaml
version: '3'

tasks:
    generate:
        desc: Generates Python gRPC code from proto files
        cmds:
            # We use `uv run` to execute the module within the uv environment
            - uv run python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. service.proto
            - sed -i '' 's/import service_pb2/from . import service_pb2/' service_pb2_grpc.py

    server:
        desc: Runs the gRPC server
        deps: [generate]
        cmds:
            - uv run server.py

    client:
        desc: Runs the gRPC client
        deps: [generate]
        cmds:
            - uv run client.py
```

Now we can run the generator to create `service_pb2.py` (the data types) and `service_pb2_grpc.py` (the client/server wiring).

```bash
task generate
```

## Step 3: The Server (`server.py`)

## Step 4: The Client (`client.py`)

## Step 5: Running the Service

```bash
# Terminal 1
task server

# Terminal 2
task client
```