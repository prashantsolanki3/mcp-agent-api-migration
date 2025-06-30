

import os
from langgraph.graph import StateGraph, END, START
from langchain.chat_models.base import BaseChatModel
from typing import TypedDict
from agents.components.vectorstore_manager import VectorStoreManager

# Define a minimal state schema as a TypedDict for StateGraph


# Input state for the graph
class DiscoveryState(TypedDict, total=False):
    input_dir: str
    output_dir: str
    vectorstore_k: int
    java_code: str  # Java code to analyze, provided by the MCP server or as part of the state

# Output state for the graph
class DiscoveryOutputState(TypedDict, total=False):
    success: bool
    error: str
    result: str
    openapi_spec_path: str
    api_docs_path: str
    message: str




def discovery_node(state: DiscoveryState, llm: BaseChatModel) -> dict:
    input_dir = state.get("input_dir")
    output_dir = state.get("output_dir")
    k = state.get("vectorstore_k", 5)  # Allow override of k
    new_state = dict(state)
    if not input_dir or not output_dir:
        return {
            "success": False,
            "error": "Both 'input_dir' and 'output_dir' must be provided in the state.",
            "result": "",
            "openapi_spec_path": "",
            "api_docs_path": "",
            "message": ""
        }

    # The agent no longer scans Java files directly. It expects the Java code to be provided by the MCP server or as part of the state.
    # If you need to fetch Java code, call the MCP server and pass the result in the state.
    java_code = state.get("java_code")
    if not java_code:
        return {
            "success": False,
            "error": "No Java code provided in the state. The agent expects the MCP server to supply the Java code.",
            "result": "",
            "openapi_spec_path": "",
            "api_docs_path": "",
            "message": ""
        }

    try:
        varstore_manager = VectorStoreManager()
        vectorstore_context = varstore_manager.get_relevant_docs(java_code, k=k) if java_code else ""
        openapi_prompt = (
            "Analyze the following Java Spring Boot code and generate a detailed OpenAPI specification (YAML or JSON). "
            "You may also use the following relevant ingested project context if helpful:\n"
            f"{vectorstore_context}\n\n"
            f"Java code:\n{java_code}"
        )
        openapi_spec = llm.invoke(openapi_prompt)
        openapi_path = os.path.join(output_dir, "openapi_spec.yaml")
        with open(openapi_path, 'w', encoding='utf-8') as f:
            f.write(str(openapi_spec))

        doc_prompt = (
            "Based on the following Java Spring Boot code and the relevant ingested project context, generate detailed API documentation (in Markdown):\n"
            f"{vectorstore_context}\n\n"
            f"Java code:\n{java_code}"
        )
        api_docs = llm.invoke(doc_prompt)
        docs_path = os.path.join(output_dir, "api_documentation.md")
        with open(docs_path, 'w', encoding='utf-8') as f:
            f.write(str(api_docs))

        return {
            "success": True,
            "openapi_spec_path": openapi_path,
            "api_docs_path": docs_path,
            "message": "OpenAPI spec and documentation generated successfully.",
            "error": "",
            "result": ""
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "result": "",
            "openapi_spec_path": "",
            "api_docs_path": "",
            "message": ""
        }

def create_discovery_agent(llm: BaseChatModel):
    """
    Returns a callable that, when invoked, returns only the output of the last node (discovery_node), not the full state.
    """
    app = StateGraph(DiscoveryState, output_schema=DiscoveryOutputState)
    app.add_node("discovery", lambda state: discovery_node(state, llm))
    app.add_edge(START, "discovery")
    app.add_edge("discovery", END)
    compiled = app.compile()
    return compiled
