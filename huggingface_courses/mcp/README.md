Course [link](https://huggingface.co/learn/mcp-course/unit0/introduction)

## Introduction to Model Context Protocol (MCP)

MCP enables AI models to connect with external data sources, tools, and environments, allowing for the seamless transfer of information and capabilities between AI systems and the broader digital world. 

MCP is often described as the “USB-C for AI applications.” Just as USB-C provides a standardized physical and logical interface for connecting various peripherals to computing devices, MCP offers a consistent protocol for linking AI models to external capabilities.

**Components**

Just like client server relationships in HTTP, MCP has a client and a server.
- Host: The user-facing AI application that end-users interact with directly. Examples include Anthropic’s Claude Desktop, AI-enhanced IDEs like Cursor, inference libraries like Hugging Face Python SDK, or custom applications built in libraries like LangChain or smolagents. Hosts initiate connections to MCP Servers and orchestrate the overall flow between user requests, LLM processing, and external tools.

- Client: A component within the host application that manages communication with a specific MCP Server. Each Client maintains a 1:1 connection with a single Server, handling the protocol-level details of MCP communication and acting as an intermediary between the Host’s logic and the external Server.

- Server: An external program or service that exposes capabilities (Tools, Resources, Prompts) via the MCP protocol.

**Capabilities**

Capabilities are the most important part of the AI application. Here are a few common capabilities that are used for many AI applications:
- Tools: Executable functions the LLM can invoke to perform actions. E.g. a weather application function that returns the weather given a location.
- Resources: Read-only data sources that provide context. E.g. a researcher assistant might have a resource for scientific papers.
- Prompts: Pre-defined templates or workflows that guide interactions between users, AI models, and the available capabilities. E.g. a summarization prompt.
- Sampling: Server-initiated requests for the Client/Host to perform LLM interactions, enabling recursive actions where the LLM can review generated content and make further decisions. E.g. A writing application reviewing its own output and decides to refine it further.

### Architectural Components of MCP

The MCP architecture consists of three primary components, each with well-defined roles and responsibilities: Host, Client, and Server.

**Host**

The Host is the user-facing AI application that end-users interact with directly.

**Client**

The Client is a component within the Host application that manages communication with a specific MCP Server. Each Client maintains a 1:1 connection with a single Server and handles the protocol-level details of MCP communication.

**Server**

The Server is an external program or service that exposes capabilities to AI models via the MCP protocol.

### The Communication Protocol

**JSON-RPC: The Foundation**

MCP uses JSON-RPC 2.0 as the message format for all communication between Clients and Servers. The protocol defines three types of messages:
1. Requests

Sent from Client to Server to initiate an operation. Example Request:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "weather",
    "arguments": {
      "location": "San Francisco"
    }
  }
}
```

2. Responses

Sent from Server to Client in reply to a Request. Example Success Response:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "temperature": 62,
    "conditions": "Partly cloudy"
  }
}
```

3. Notifications

One-way messages that don’t require a response. Typically sent from Server to Client to provide updates or notifications about events. Example Notification:
```json
{
  "jsonrpc": "2.0",
  "method": "progress",
  "params": {
    "message": "Processing data...",
    "percent": 50
  }
}
```

**Transport Mechanisms**

JSON-RPC defines the message format, but MCP also specifies how these messages are transported between Clients and Servers. Two primary transport mechanisms are supported:

- stdio (Standard Input/Output): The stdio transport is used for local communication, where the Client and Server run on the same machine.
- HTTP + SSE (Server-Sent Events) / Streamable HTTP: The HTTP+SSE transport is used for remote communication, where the Client and Server might be on different machines.

### Understanding MCP Capabilities

MCP Servers expose a variety of capabilities to Clients through the communication protocol. These capabilities fall into four main categories.

- Tools
- Resources
- Prompts
- Sampling

**Discover Process**

One of MCP’s key features is dynamic capability discovery. When a Client connects to a Server, it can query the available Tools, Resources, and Prompts through specific list methods:

- `tools/list`
- `resources/list`
- `prompts/list`

### MCP SDK

The Model Context Protocol provides official SDKs for both JavaScript, Python and other languages. This makes it easy to implement MCP clients and servers in your applications. These SDKs handle the low-level protocol details, allowing you to focus on building your application’s capabilities.

Here's example code for a simple MCP server:
```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Weather Service")

# Tool implementation
@mcp.tool()
def get_weather(location: str) -> str:
    """Get the current weather for a specified location."""
    return f"Weather in {location}: Sunny, 72°F"

# Resource implementation
@mcp.resource("weather://{location}")
def weather_resource(location: str) -> str:
    """Provide weather data as a resource."""
    return f"Weather data for {location}: Sunny, 72°F"

# Prompt implementation
@mcp.prompt()
def weather_report(location: str) -> str:
    """Create a weather report prompt."""
    return f"""You are a weather reporter. Weather report for {location}?"""


# Run the server
if __name__ == "__main__":
    mcp.run()
```

In order to run this script/server we need a Python environment with `mcp`. For example:
```bash
uv init
uv venv
source .venv/bin/activate
uv pip install "mcp[cli]"
```

This server can be started with:
```bash
mcp dev simple_server.py
```

You can then open the MCP Inspector at http://127.0.0.1:6274 to see the server’s capabilities and interact with them.

### MCP Clients

**Understanding MCP Clients**

MCP Clients are crucial components that act as the bridge between AI applications (Hosts) and external capabilities provided by MCP Servers. Think of the Host as your main application (like an AI assistant or IDE) and the Client as a specialized module within that Host responsible for handling MCP communications.

We start by exploring the user interface clients that are available for the MCP.
- Chat Interface Clients: Anthropic’s Claude Desktop stands as one of the most prominent MCP Clients, providing integration with various MCP Servers.
- Interactive Development Clients: Cursor’s MCP Client implementation enables AI-powered coding assistance through direct integration with code editing capabilities. It supports multiple MCP Server connections and provides real-time tool invocation during coding, making it a powerful tool for developers.

**Configuring MCP Clients**

MCP hosts use configuration files to manage server connections. These files define which servers are available and how to connect to them.

The standard configuration file for MCP is named `mcp.json`. Here’s the basic structure (which can be passed to applications like Claude Desktop, Cursor, or VS Code):

```json
{
  "servers": [
    {
      "name": "Server Name",
      "transport": {
        "type": "stdio|sse",
        // Transport-specific configuration
      }
    }
  ]
}
```

Configuration for stdio Transport:

```json
{
  "servers": [
    {
      "name": "File Explorer",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/file_explorer_server.py"] // This is an example, we'll use a real server in the next unit
      }
    }
  ]
}
```

Configuration for HTTP+SSE Transport:

```json
{
  "servers": [
    {
      "name": "Remote API Server",
      "transport": {
        "type": "sse",
        "url": "https://example.com/mcp-server"
      }
    }
  ]
}
```

Environment variables can be passed to server processes using the `env` field. Here’s how to access them in your server code:

```python
import os

# Access environment variables
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is required")

# Use the token in your server code
def make_github_request():
    headers = {"Authorization": f"Bearer {github_token}"}
    # ... rest of your code
```

The corresponding configuration in `mcp.json` would look like this:

```json
{
  "servers": [
    {
      "name": "GitHub API",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/github_server.py"], // This is an example, we'll use a real server in the next unit
        "env": {
          "GITHUB_TOKEN": "your_github_token"
        }
      }
    }
  ]
}
```

**Tiny Agents Clients**

You can use tiny agents as MCP Clients to connect directly to MCP servers from your code. Tiny agents provide a simple way to create AI agents that can use tools from MCP servers.

Tiny Agent can run MCP servers with a command line environment. To do this, we will need to install `npm` and run the server with `npx`.

Setup

First, we will need to install `npx`:
```bash
npm install -g npx
```

Then, we will need to install the `huggingface_hub` package with the MCP support. This will allow us to run MCP servers and clients.
```bash
uv pip install "huggingface_hub[mcp]>=0.32.0"
```

Connecting to MCP Servers

Let’s create an agent configuration file `agent.json`. This is an MCP server that can control a browser with Playwright:
```json
{
    "model": "Qwen/Qwen2.5-72B-Instruct",
    "provider": "nebius",
    "servers": [
        {
            "type": "stdio",
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        }
    ]
}
```
 
The agent can be run with
```bash
tiny-agents run agent.json
# OR you may need: python -m huggingface_hub.inference._mcp.cli run agent.json
```

### Gradio MCP Integration

Gradio allows developers to create UIs for their models with just a few lines of Python code.  It’s particularly useful for:

- Creating demos and prototypes
- Sharing models with non-technical users
- Testing and debugging model behavior

With the addition of MCP support, Gradio now offers a straightforward way to expose AI model capabilities through the standardized MCP protocol.

Install Gradio with MCP support:
```bash
uv pip install "gradio[mcp]"
```

**Creating an MCP Server with Gradio**

Here is a basic example of creating an MCP Server using Gradio:

```python
import gradio as gr

def letter_counter(word: str, letter: str) -> int:
    """
    Count the number of occurrences of a letter in a word or text.

    Args:
        word (str): The input text to search through
        letter (str): The letter to search for

    Returns:
        int: The number of times the letter appears in the text
    """
    word = word.lower()
    letter = letter.lower()
    count = word.count(letter)
    return count

# Create a standard Gradio interface
demo = gr.Interface(
    fn=letter_counter,
    inputs=["textbox", "textbox"],
    outputs="number",
    title="Letter Counter",
    description="Enter text and a letter to count how many times the letter appears in the text."
)

# Launch both the Gradio web interface and the MCP server
if __name__ == "__main__":
    demo.launch(mcp_server=True)
```

With this setup, your letter counter function is now accessible through:

1. A traditional Gradio web interface for direct human interaction
2. An MCP Server that can be connected to compatible clients
The MCP server will be accessible at:
```bash
http://your-server:port/gradio_api/mcp/sse
```

When you set mcp_server=True in launch(), several things happen:

1. Gradio functions are automatically converted to MCP Tools
2. Input components map to tool argument schemas
3. Output components determine the response format
4. The Gradio server now also listens for MCP protocol messages
5. JSON-RPC over HTTP+SSE is set up for client-server communication

