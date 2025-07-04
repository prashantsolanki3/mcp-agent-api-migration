# MCP FastAPI Server Setup

This project exposes an addition tool as an MCP server using FastAPI and fastapi-mcp.

## How to Run

1. **Activate your virtual environment** (if not already active):
   
   ```zsh
   source .venv/bin/activate
   ```

2. **Install requirements:**
   
   ```zsh
   pip install -r mcp-server/requirements.txt
   ```

3. **Start the FastAPI MCP server:**
   
   ```zsh
   # from the root folder
   uvicorn mcp-server.main:app --reload --host 127.0.0.1 --port 8000 --log-level debug
   ```

4. **(Optional) MCP Proxy for VS Code/Claude:**
   
   Use the `mcp_config.json` to configure your MCP client (e.g., Claude Desktop Agent or VS Code MCP extension) to connect via mcp-proxy.

```json
{
  "mcpServers": {
    "addition-tool-mcp": {
      "command": "<PATH_TO_MCP_PROXY>/mcp-agent-api-migration/.venv/bin/mcp-proxy",
      "args": ["http://127.0.0.1:8000/mcp"],
      "cwd": "<PATH_TO_MCP_PROXY>/mcp-agent-api-migration",
      "env": {}
    }
  }
}
```

## Setup in IDE

```json
{
  "mcpServers": {
    "mcp-agent-api-migration": {
                "url": "http://127.0.0.1:8000/mcp"
            }
  }
}
```

## Requirements
See `mcp-server/requirements.txt` for all dependencies.

---

For more, see the article: [Integrating MCP Servers with FastAPI](https://medium.com/@ruchi.awasthi63/integrating-mcp-servers-with-fastapi-2c6d0c9a4749)
