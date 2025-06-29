from langgraph.graph import StateGraph, END
from langchain.chat_models.base import BaseChatModel
from typing import TypedDict

# Define a minimal state schema as a TypedDict for StateGraph
class DiscoveryState(TypedDict, total=False):
    # Add any state fields here if needed
    pass

def discovery_node(state: DiscoveryState, llm: BaseChatModel) -> dict:
    response = llm.invoke("Analyze Spring Boot source and generate OpenAPI spec.")
    # Ensure the node returns a dict as required by langgraph
    return {"result": str(response)}

def create_discovery_agent(llm: BaseChatModel) -> StateGraph:
    app = StateGraph(DiscoveryState)
    app.add_node("discovery", lambda state: discovery_node(state, llm))
    app.set_entry_point("discovery")
    app.add_edge("discovery", END)
    return app