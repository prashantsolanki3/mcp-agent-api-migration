# Agents Folder

This folder contains the agent logic and components used by the MCP FastAPI server.

## Contents

- `discovery_agent.py`: Main agent for analyzing Java Spring Boot code and generating OpenAPI specs and documentation.
- `components/`: Utilities and vector store management for agent operations.

## Usage

Agents are imported and invoked by the FastAPI server in `mcp-server`. See the [mcp-server/README.md](../mcp-server/README.md) for integration details.
