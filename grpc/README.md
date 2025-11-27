# gRPC Examples

This repository contains simple gRPC service examples implemented in both Python and Go.

## Project Structure

```
.
├── service.proto          # Shared Protocol Buffers definition
├── taskfile.yaml         # Task runner configuration
├── python/               # Python implementation
│   ├── server.py
│   ├── client.py
│   ├── service_pb2.py    # Generated protobuf code
│   └── service_pb2_grpc.py
└── go/                   # Go implementation
    ├── server/
    │   └── main.go
    ├── client/
    │   └── main.go
    └── proto/            # Generated protobuf code
        ├── service.pb.go
        └── service_grpc.pb.go
```

## Prerequisites

### For Python
- [uv](https://astral.sh/uv) package manager
- Python 3.12+

### For Go
- Go 1.21+
- Protocol Buffers compiler (protoc)

### Common
- [Task](https://taskfile.dev) runner (optional but recommended)

## Setup

### Python Setup

```bash
# 1. Install uv (if you haven't)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. The python directory already has pyproject.toml configured
# Dependencies will be installed automatically when running tasks
```

### Go Setup

```bash
# 1. Install protoc (macOS)
brew install protobuf

# 2. Install Go protobuf plugins
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# 3. Make sure protoc plugins are in your PATH
export PATH="$PATH:$(go env GOPATH)/bin"

# 4. Install Go dependencies
cd go
go mod tidy
```

## Protocol Buffers Definition

The `service.proto` file defines the API contract shared between both implementations:

```protobuf
syntax = "proto3";

package users;

option go_package = "github.com/danielsmith/utilities/grpc/proto";

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

Note on tags: The `= 1`, `= 2` are not values; they are unique binary tags used for serialization. Once assigned, you should not change them to maintain backward compatibility.

## Running the Examples

### Using Task Runner (Recommended)

#### Python

```bash
# Terminal 1 - Start Python server
task py:server

# Terminal 2 - Run Python client
task py:client
```

#### Go

```bash
# Terminal 1 - Start Go server
task go:server

# Terminal 2 - Run Go client
task go:client
```

### Manual Execution

#### Python

```bash
# Generate Python code
cd python
uv run python -m grpc_tools.protoc -I.. --python_out=. --grpc_python_out=. ../service.proto
sed -i '' 's/import service_pb2/from . import service_pb2/' service_pb2_grpc.py

# Run server
uv run server.py

# In another terminal, run client
uv run client.py
```

#### Go

```bash
# Generate Go code (from project root)
export PATH=$PATH:$(go env GOPATH)/bin
protoc --go_out=go/proto --go_opt=paths=source_relative \
       --go-grpc_out=go/proto --go-grpc_opt=paths=source_relative \
       service.proto

# Run server
cd go/server
go run main.go

# In another terminal, run client
cd go/client
go run main.go
```

## Available Tasks

View all available tasks:
```bash
task --list
```

Output:
```
task: Available tasks for this project:
* generate:      Generates gRPC code for both Python and Go
* go:client:     Runs the Go gRPC client
* go:generate:   Generates Go gRPC code from proto files
* go:server:     Runs the Go gRPC server
* py:client:     Runs the Python gRPC client
* py:generate:   Generates Python gRPC code from proto files
* py:server:     Runs the Python gRPC server
```

## What's Happening?

Both implementations demonstrate the same simple UserLookup service:

1. The server listens on port 50051
2. The client connects and requests user data for ID 1
3. The server responds with mock user data
4. If requesting a non-existent user ID, the server returns a NOT_FOUND error

### Python Implementation

- **Server** (`python/server.py`): Implements the `UserLookupServicer` class
- **Client** (`python/client.py`): Creates a stub and makes RPC calls

### Go Implementation

- **Server** (`go/server/main.go`): Implements the `userLookupServer` struct
- **Client** (`go/client/main.go`): Creates a client and makes RPC calls with context and timeout

## Next Steps

- Try modifying the proto file to add new fields or methods
- Implement streaming RPCs (server streaming, client streaming, or bidirectional)
- Add authentication/authorization
- Implement error handling and retries
- Add tests for both implementations
