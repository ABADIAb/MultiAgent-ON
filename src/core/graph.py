"""LangGraph StateGraph definition for the V4 Neurosymbolic Intent Pipeline.

Wires the linear neurosymbolic pipeline:
  Intent Ingest → PDDL Parser → Reverse Prompt (HITL) → Symbolic Solver
  → QoT Validation → Plan Synthesizer

The Reverse Prompt node uses interrupt() for HITL approval, with
conditional routing for approve/refine/reject.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from src.agents.intent_ingest import intent_ingest_node
from src.agents.pddl_parser import pddl_parser_node
from src.agents.plan_synthesizer import plan_synthesizer_node
from src.agents.qot_validation import qot_validation_node
from src.agents.reverse_prompt import hitl_route, reverse_prompt_node
from src.agents.symbolic_solver import symbolic_solver_node
from src.core.state import AgentState


def build_graph() -> StateGraph:
    """Construct the V4 Neurosymbolic Intent Pipeline.

    Returns:
        A StateGraph builder (not yet compiled).

    Graph topology:
        START → intent_ingest → pddl_parser → reverse_prompt
          → (approved) → symbolic_solver → qot_validation → plan_synthesizer → END
          → (refine)   → pddl_parser (loop)
          → (reject)   → END
    """
    builder = StateGraph(AgentState)

    # Add pipeline nodes
    builder.add_node("intent_ingest", intent_ingest_node)
    builder.add_node("pddl_parser", pddl_parser_node)
    builder.add_node("reverse_prompt", reverse_prompt_node)
    builder.add_node("symbolic_solver", symbolic_solver_node)
    builder.add_node("qot_validation", qot_validation_node)
    builder.add_node("plan_synthesizer", plan_synthesizer_node)

    # Linear pipeline edges
    builder.add_edge(START, "intent_ingest")
    builder.add_edge("intent_ingest", "pddl_parser")
    builder.add_edge("pddl_parser", "reverse_prompt")

    # HITL conditional routing
    builder.add_conditional_edges("reverse_prompt", hitl_route)

    # Post-HITL linear pipeline
    builder.add_edge("symbolic_solver", "qot_validation")
    builder.add_edge("qot_validation", "plan_synthesizer")
    builder.add_edge("plan_synthesizer", END)

    return builder


def compile_graph(*, checkpointer=None) -> object:
    """Build and compile the V4 graph with an optional checkpointer.

    Note: A checkpointer is REQUIRED for interrupt() to work.
    Use InMemorySaver for development, SqliteSaver for persistence.

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
