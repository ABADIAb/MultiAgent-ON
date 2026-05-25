from src.core.state import AgentState

def topology_agent_node(state: AgentState) -> AgentState:
    """
    Topology Agent fetches physical testbed data via RESTConf.
    """
    # Mock RESTConf GET request
    state["topology"] = {"nodes": ["A", "B", "C"], "edges": [("A", "B"), ("B", "C")]}
    return state
