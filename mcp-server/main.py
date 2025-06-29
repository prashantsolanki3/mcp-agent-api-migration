from fastapi import FastAPI
from pydantic import BaseModel
from fastapi_mcp import FastApiMCP
from dotenv import load_dotenv
import os
from agents.discovery_agent import create_discovery_agent
from agents.components.utils import get_llm
from langgraph.graph import StateGraph
# Import the ingest function
from .ingest import ingest_files_to_vectorstore



load_dotenv()

ingest_files_to_vectorstore("./knowledge_base")

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




# Endpoint to ingest files into the vector store
@app.post("/ingest_files", summary="Ingest project files into the vector store for knowledge base")
async def ingest_files(root_dir: str = "./knowledge_base"):
    """Ingest all supported files into the vector store for knowledge base."""
    result = ingest_files_to_vectorstore(root_dir)
    return {"status": "completed" if result else "failed"}

# Endpoint to show all content in the vector store
@app.get("/vectorstore_content", operation_id="show_vectorstore_content", summary="Show all content in the vector store")
async def vectorstore_content():
    from langchain_chroma import Chroma
    vectordb = Chroma(persist_directory="./vectorstore", embedding_function=None)
    # Get all documents (as texts)
    docs = vectordb.get()['documents']
    # Flatten and join for display
    all_content = [item for sublist in docs for item in sublist]
    return {"documents": all_content}

mcp = FastApiMCP(
    app,
    name="Addition MCP",
    description="Simple API exposing adding operation",
)
mcp.mount()