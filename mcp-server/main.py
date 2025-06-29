from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
import os
from agents.discovery_agent import create_discovery_agent
from agents.components.utils import get_llm
from langgraph.graph import StateGraph


load_dotenv()

app = FastAPI()

llm = get_llm()


@app.get(
    "/add", operation_id="add_two_numbers", summary="Add two numbers and return the sum"
)
async def add(a: int, b: int):
    """Add two numbers and return the sum."""
    result = a + b
    return {"sum": result}


@app.get(
    "/run_discovery",
    operation_id="run_discovery_agent",
    summary="Run the discovery agent to analyze Spring Boot source and generate OpenAPI spec",
)
async def run_discovery():
    """Run the discovery agent to analyze Spring Boot source and generate OpenAPI spec."""
    status_message = "Running discovery agent..."
    agent: StateGraph = create_discovery_agent(llm)
    compiled_agent = agent.compile()
    response = compiled_agent.invoke({})
    return {
        "status": status_message,
        "result": str(response)
    }


mcp = FastApiMCP(
    app,
    name="Addition MCP",
    description="Simple API exposing adding operation",
)
mcp.mount()
