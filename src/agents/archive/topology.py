"""Topology Agent node for the LangGraph pipeline.

Responsible for querying the testbed and updating the shared state
with a structured topology snapshot.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from src.core.state import AgentState, TopologySnapshot
from src.tools.fetch_topology import fetch_topology


def topology_node(state: AgentState) -> dict:
    """Execute the topology query and update the state.

    Invokes the fetch_topology tool directly (deterministic, no LLM needed)
    and converts the result into a TopologySnapshot for the shared state.

    Returns:
        Partial state update with topology_snapshot, messages, and current_agent.
    """
    raw_topology = fetch_topology.invoke({})
    snapshot = TopologySnapshot.model_validate(raw_topology)

    node_names = [n.name for n in snapshot.nodes]
    link_count = len(snapshot.links)
    total_fiber_km = sum(link.length_km for link in snapshot.links)

    summary = (
        f"Topology fetched successfully. "
        f"Network has {len(snapshot.nodes)} nodes ({', '.join(node_names)}), "
        f"{link_count} fiber links, "
        f"total fiber length: {total_fiber_km:.1f} km."
    )

    return {
        "topology_snapshot": snapshot,
        "messages": [AIMessage(content=summary, name="topology_agent")],
        "current_agent": "supervisor",
    }
