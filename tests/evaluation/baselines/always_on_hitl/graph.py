"""Graph constructor for the Always-On HITL baseline.

Ablation baseline where the Semantic Gate unconditionally forces a HITL
clarification on Turn 1, regardless of semantic uncertainty or intent quality.
On Turn 2+, standard semantic gate evaluation resumes.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.core.state import AgentState
from src.core.symbolic_solver import symbolic_solver_node
from src.nodes.intent_ingest import intent_ingest_node
from src.nodes.pddl_parser import pddl_parser_node
from src.nodes.plan_synthesizer import plan_synthesizer_node
from src.nodes.qot_validation import qot_validation_node
from src.nodes.radg_node import radg_node, radg_route
from src.nodes.reverse_prompt import hitl_clarify_node, hitl_clarify_route, reverse_prompt_node
from src.nodes.semantic_gate_node import semantic_gate_node, semantic_gate_route


def always_on_semantic_gate_node(state: AgentState) -> dict:
    """Always-On HITL Semantic Gate node.

    - Turn 1 (refinement_count == 0): Unconditionally sets U_sem = 1.0 and usem_passed = False,
      forcing execution to route to hitl_clarify.
    - Turn 2+ (refinement_count > 0): Delegates to standard semantic_gate_node.
    """
    refinement_count = state.get("refinement_count") or 0
    if refinement_count == 0:
        summary = "Semantic Gate [FAIL (Always-On HITL forced clarify)]: Mandatory operator confirmation enforced on Turn 1."
        return {
            "usem_score": 1.0,
            "usem_passed": False,
            "error_context": "Always-On HITL policy: Mandatory operator confirmation required on initial intent submission.",
            "messages": [AIMessage(content=summary, name="semantic_gate")],
        }
    return semantic_gate_node(state)


def build_always_on_graph() -> StateGraph:
    """Construct the StateGraph for Always-On HITL."""
    builder = StateGraph(AgentState)  # type: ignore

    builder.add_node("intent_ingest", intent_ingest_node)
    builder.add_node("pddl_parser", pddl_parser_node)
    builder.add_node("reverse_prompt", reverse_prompt_node)
    builder.add_node("semantic_gate", always_on_semantic_gate_node)
    builder.add_node("hitl_clarify", hitl_clarify_node)
    builder.add_node("symbolic_solver", symbolic_solver_node)
    builder.add_node("qot_validation", qot_validation_node)
    builder.add_node("radg", radg_node)
    builder.add_node("plan_synthesizer", plan_synthesizer_node)

    builder.add_edge(START, "intent_ingest")
    builder.add_edge("intent_ingest", "pddl_parser")
    builder.add_edge("pddl_parser", "reverse_prompt")
    builder.add_edge("reverse_prompt", "semantic_gate")

    builder.add_conditional_edges("semantic_gate", semantic_gate_route)
    builder.add_conditional_edges("hitl_clarify", hitl_clarify_route)

    builder.add_edge("symbolic_solver", "qot_validation")
    builder.add_edge("qot_validation", "radg")
    builder.add_conditional_edges("radg", radg_route)
    builder.add_edge("plan_synthesizer", END)

    return builder


def compile_always_on_graph(*, checkpointer=None) -> CompiledStateGraph:
    """Compile the Always-On HITL graph with an optional checkpointer."""
    builder = build_always_on_graph()
    kwargs: dict = {}
    if checkpointer:
        kwargs["checkpointer"] = checkpointer
    return builder.compile(**kwargs)
