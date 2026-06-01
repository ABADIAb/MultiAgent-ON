"""LangGraph StateGraph definition for the MultiAgentON pipeline.

Wires together the Supervisor and Topology Agent nodes with
conditional edges for task-based routing.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agents.supervisor import route_by_task, supervisor_node
from src.agents.topology import topology_node
from src.core.state import AgentState


def build_graph() -> StateGraph:
    """Construct the MultiAgentON StateGraph.

    Returns:
        A compiled StateGraph ready for invocation.

    Graph topology:
        START → supervisor → (conditional) → topology_agent → supervisor → END
                                           → END (if no actionable task)
    """
    builder = StateGraph(AgentState)

    # Add nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("topology_agent", topology_node)

    # Edges
    builder.add_edge(START, "supervisor")
    builder.add_conditional_edges("supervisor", route_by_task)
    builder.add_edge("topology_agent", "supervisor")

    return builder


def compile_graph(*, checkpointer=None) -> object:
    """Build and compile the graph with an optional checkpointer.

    Args:
        checkpointer: LangGraph checkpointer for state persistence.

    Returns:
        A compiled graph ready for .invoke() or .stream().
    """
    builder = build_graph()
    kwargs = {}
    if checkpointer:
        kwargs["checkpointer"] = checkpointer
    return builder.compile(**kwargs)
