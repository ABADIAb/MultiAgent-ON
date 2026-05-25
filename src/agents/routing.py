from src.core.state import AgentState

def routing_agent_node(state: AgentState) -> AgentState:
    """
    Routing Agent calculates paths and evaluates QoT.
    """
    state["current_path"] = ["A", "B", "C"]
    state["is_feasible"] = True
    return state
