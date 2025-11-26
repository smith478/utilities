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
```
