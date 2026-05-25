from typing import TypedDict, Annotated, List, Dict, Any
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    intent: str
    sla_matrix: Dict[str, Any]
    task_list: List[str]
    is_authorized: bool
    current_path: List[str]
    is_feasible: bool
    topology: Dict[str, Any]
    error: str
