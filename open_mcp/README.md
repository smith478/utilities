## Open MCP

The idea here is to play around with MCP using open source models, most likely with ollama. There are a few tools to help with this:
- [oterm](https://github.com/ggozad/oterm)
- [ollama-mcp-bridge](https://github.com/patruff/ollama-mcp-bridge)
- [open-webui](https://docs.openwebui.com/openapi-servers/mcp/)

MCP servers:
[awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)

### Setup

Create virtual environment
```bash
uv venv
```

Install required packages
```bash
uv init
uv add pydantic-ai mcp
```

Configure `mcp_config.json`. Examples of how to connect with different servers can be found [here](https://github.com/modelcontextprotocol/servers?tab=readme-ov-file).