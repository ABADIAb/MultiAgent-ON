"""LangGraph StateGraph definition for the V5 Risk-Adaptive Neurosymbolic Pipeline.

Exp 3.0 / 3.2: Wires the complete V5 fail-fast conditional pipeline:

  START → intent_ingest → pddl_parser → reverse_prompt → semantic_gate
    → (U_sem <= tau) → symbolic_solver → qot_validation → radg
        → (approve) → plan_synthesizer → END
        → (replan)  → [HITL interrupt in radg_node] → pddl_parser (loop)
    → (U_sem >  tau) → [HITL refine in reverse_prompt] → pddl_parser (loop)

V5 Changes from V4:
  - semantic_gate node added between reverse_prompt and symbolic_solver.
  - HITL routing now owned by semantic_gate_route (not hitl_route).
  - radg node added between qot_validation and plan_synthesizer.
  - radg_route replaces the direct qot_validation → plan_synthesizer edge.
"""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.core.radg import evaluate_radg  # noqa: F401 — imported for test introspection
from src.core.state import AgentState
from src.core.symbolic_solver import symbolic_solver_node
from src.nodes.intent_ingest import intent_ingest_node
from src.nodes.pddl_parser import pddl_parser_node
from src.nodes.plan_synthesizer import plan_synthesizer_node
from src.nodes.qot_validation import qot_validation_node
from src.nodes.radg_node import radg_node, radg_route
from src.nodes.reverse_prompt import hitl_clarify_node, reverse_prompt_node
from src.nodes.semantic_gate_node import semantic_gate_node, semantic_gate_route


def build_graph() -> StateGraph:
    """Construct the V5 Risk-Adaptive Neurosymbolic Intent Pipeline.

    Returns:
        A StateGraph builder (not yet compiled).

    Graph topology:
        START → intent_ingest → pddl_parser → reverse_prompt → semantic_gate
          → (pass)    → symbolic_solver → qot_validation → radg
              → (approve) → plan_synthesizer → END
              → (replan)  → pddl_parser (HITL loop via interrupt in radg_node)
          → (clarify) → hitl_clarify (HITL interrupt in Phase 3b) → pddl_parser
    """
    builder = StateGraph(AgentState)  # type: ignore

    # -----------------------------------------------------------------------
    # Register all V5 pipeline nodes
    # -----------------------------------------------------------------------
    builder.add_node("intent_ingest", intent_ingest_node)
    builder.add_node("pddl_parser", pddl_parser_node)
    builder.add_node("reverse_prompt", reverse_prompt_node)
    builder.add_node("semantic_gate", semantic_gate_node)
    builder.add_node("hitl_clarify", hitl_clarify_node)
    builder.add_node("symbolic_solver", symbolic_solver_node)
    builder.add_node("qot_validation", qot_validation_node)
    builder.add_node("radg", radg_node)
    builder.add_node("plan_synthesizer", plan_synthesizer_node)

    # -----------------------------------------------------------------------
    # Linear pipeline: START → NL parsing → automated Reverse Prompt reconstruction
    # -----------------------------------------------------------------------
    builder.add_edge(START, "intent_ingest")
    builder.add_edge("intent_ingest", "pddl_parser")
    builder.add_edge("pddl_parser", "reverse_prompt")
    builder.add_edge("reverse_prompt", "semantic_gate")

    # -----------------------------------------------------------------------
    # Semantic Gate conditional routing (Phase 3 → 3b / Phase 4)
    # Routes:
    #   semantic_gate_route → "symbolic_solver"  (U_sem <= tau, gate passes -> 0 interrupts)
    #   semantic_gate_route → "hitl_clarify"     (U_sem > tau, triggers Phase 3b HITL)
    # -----------------------------------------------------------------------
    builder.add_conditional_edges("semantic_gate", semantic_gate_route)
    builder.add_edge("hitl_clarify", "pddl_parser")

    # -----------------------------------------------------------------------
    # Symbolic solver → QoT validation → RADG physical risk gate
    # -----------------------------------------------------------------------
    builder.add_edge("symbolic_solver", "qot_validation")
    builder.add_edge("qot_validation", "radg")

    # -----------------------------------------------------------------------
    # RADG conditional routing (Phase 6)
    # Routes:
    #   radg_route → "plan_synthesizer"  (approve)
    #   radg_route → "pddl_parser"       (replan loop — refined by operator)
    # -----------------------------------------------------------------------
    builder.add_conditional_edges("radg", radg_route)

    # -----------------------------------------------------------------------
    # Terminal edge
    # -----------------------------------------------------------------------
    builder.add_edge("plan_synthesizer", END)

    return builder


def compile_graph(*, checkpointer=None) -> CompiledStateGraph:
    """Build and compile the V5 graph with an optional checkpointer.

    Note: A checkpointer is REQUIRED for interrupt() to work in both
    the reverse_prompt and radg_node HITL checkpoints.
    Use InMemorySaver for development, SqliteSaver for persistence.

    Args:
        checkpointer: LangGraph checkpointer for state persistence.

    Returns:
        A compiled graph ready for .invoke() or .stream().
    """
    builder = build_graph()
    kwargs: dict = {}
    if checkpointer:
        kwargs["checkpointer"] = checkpointer
    return builder.compile(**kwargs)
