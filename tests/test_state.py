from src.core.state import AgentState

def test_agent_state_keys():
    state: AgentState = {
        "messages": [],
        "intent": "test intent",
        "sla_matrix": {},
        "task_list": [],
        "is_authorized": False,
        "current_path": [],
        "is_feasible": False,
        "topology": {},
        "error": ""
    }
    assert "messages" in state
    assert "intent" in state
    assert "sla_matrix" in state
    assert "task_list" in state
