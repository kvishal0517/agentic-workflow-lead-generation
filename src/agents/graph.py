from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.nodes.discovery import discovery_node
from src.agents.nodes.enrichment import enrichment_node
from src.agents.nodes.validation import validation_node
from src.agents.nodes.scoring import scoring_node
from src.agents.nodes.drafting import drafting_node
from src.agents.nodes.pushing import pushing_node

def create_lead_hunter_graph():
    workflow = StateGraph(AgentState)

    # Add Nodes
    workflow.add_node("discover", discovery_node)
    workflow.add_node("enrich", enrichment_node)
    workflow.add_node("validate", validation_node)
    workflow.add_node("score", scoring_node)
    workflow.add_node("draft", drafting_node)
    workflow.add_node("push", pushing_node)

    # Set Entry Point
    workflow.set_entry_point("discover")

    # Add Edges
    workflow.add_edge("discover", "enrich")
    workflow.add_edge("enrich", "validate")
    workflow.add_edge("validate", "score")
    workflow.add_edge("score", "draft")
    workflow.add_edge("draft", "push")
    workflow.add_edge("push", END)

    return workflow.compile()
