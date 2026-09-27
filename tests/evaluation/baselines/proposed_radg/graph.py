"""Graph constructor for the Proposed Neurosymbolic RADG baseline."""

from __future__ import annotations

from langgraph.graph.state import CompiledStateGraph

from src.core.graph import compile_graph


def compile_proposed_graph(*, checkpointer=None) -> CompiledStateGraph:
    """Compile the standard V5 pipeline graph with active fail-fast RADGs."""
    return compile_graph(checkpointer=checkpointer)
