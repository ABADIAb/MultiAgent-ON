from langgraph.graph import StateGraph, START, END
from src.core.state import AgentState
from src.agents.supervisor import supervisor_node, hitl_node
from src.agents.topology import topology_agent_node
from src.agents.routing import routing_agent_node
from src.agents.lightpath import lightpath_agent_node

def create_orchestrator_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("hitl", hitl_node)
    builder.add_node("topology_agent", topology_agent_node)
    builder.add_node("routing_agent", routing_agent_node)
    builder.add_node("lightpath_agent", lightpath_agent_node)
    
    # Edges
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "hitl")
    
    # Simplified flow for scaffolding
    builder.add_edge("hitl", "topology_agent")
    builder.add_edge("topology_agent", "routing_agent")
    builder.add_edge("routing_agent", "lightpath_agent")
    builder.add_edge("lightpath_agent", END)
    
    return builder.compile()
