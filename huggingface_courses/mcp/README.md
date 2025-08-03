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