"""Graph constructor for the LLM-Only baseline.

Ablation baseline where Phase 3 Semantic Gate has NO human-in-the-loop (HITL)
filter, allowing unverified and ambiguous configurations to reach the physical layer
(surrogate for the network controller). The Physical Gate detects controller-level
failures and triggers an operator replan interrupt.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import interrupt

from src.core.radg import evaluate_radg
from src.core.state import AgentState
from src.core.symbolic_solver import symbolic_solver_node
from src.nodes.intent_ingest import intent_ingest_node
from src.nodes.pddl_parser import pddl_parser_node
from src.nodes.plan_synthesizer import plan_synthesizer_node
from src.nodes.qot_validation import qot_validation_node
from src.nodes.radg_node import radg_route
from src.nodes.reverse_prompt import reverse_prompt_node
from src.nodes.semantic_gate_node import semantic_gate_node

from pathlib import Path

logger = logging.getLogger(__name__)

MOCK_ERROR_FILE = Path(__file__).resolve().parent / "mock_restconf_error.json"


def bypassed_semantic_gate_node(state: AgentState) -> dict:
    """Semantic Gate without HITL clarification.

    Evaluates U_sem for diagnostic logging, but unconditionally sets usem_passed = True
    so no operator clarification is ever triggered at Phase 3.
    """
    res = semantic_gate_node(state)
    res["usem_passed"] = True
    res["error_context"] = None
    summary = "Semantic Gate (LLM-Only): Bypassed HITL filter — forwarding directly to controller."
    res["messages"] = [AIMessage(content=summary, name="semantic_gate")]
    return res


def controller_surrogate_radg_node(state: AgentState) -> dict:
    """Physical Gate acting as a surrogate for the network controller.

    Reaching this node represents that the configuration has arrived at the controller.
    - Turn 1:
        * Class I (Nominal): Passes through if feasible -> auto-approve -> Phase 7 Synthesis.
        * Non-nominal (Class II, III, IV): Controller rejects deployment. Does NOT interrupt.
          Injects raw RFC 8040 RESTConf error payload into state messages and loops back to
          Phase 2 (PDDL Parsing) for autonomous blind retry (hallucination & token penalty).
    - Turn 2:
        * If blind retry fails again (expected for unfeasible/ambiguous demands), fires HITL
          operator interrupt requiring incident response intervention.
    - Turn 3+ (Incident Response Recovery):
        * Evaluates operator-provided nominal recovery intent and approves when feasible.
    """
    qot_results: list[dict] = state.get("qot_results") or []
    intent_class: str | None = state.get("intent_class")
    refinement_count: int = state.get("refinement_count") or 0

    # Turn 1 handling (Initial Deployment Attempt)
    if refinement_count == 0:
        is_nominal = (intent_class == "I_Nominal") if intent_class else None

        # If unclassified (e.g. interactive mode), infer from physics and pddl
        if is_nominal is None:
            v_struct = state.get("pddl_valid", False)
            has_feasible = any(r.get("feasible") for r in qot_results)
            is_nominal = v_struct and has_feasible

        if is_nominal:
            decision = evaluate_radg(qot_results)
            if decision == "approve":
                summary = "Controller (Physical Gate): Deployment APPROVED and provisioned."
                return {
                    "radg_decision": "approve",
                    "error_context": None,
                    "controller_reached": True,
                    "controller_error": False,
                    "controller_verdict": "approve",
                    "messages": [AIMessage(content=summary, name="radg")],
                }

        # Non-nominal intent (Class II, III, IV) reached controller in Turn 1:
        # Simulate controller deployment error, inject raw RESTConf error log, DO NOT interrupt.
        if MOCK_ERROR_FILE.exists():
            with open(MOCK_ERROR_FILE, "r", encoding="utf-8") as f:
                raw_restconf_error = f.read().strip()
        else:
            raw_restconf_error = (
                '{"ietf-restconf:errors": {"error": [{"error-message": "Deployment aborted. Physical impairment validation failed."}]}}'
            )

        summary = (
            "Controller Deployment Rejection (RFC 8040 RESTCONF Error Log):\n"
            f"{raw_restconf_error}"
        )
        logger.warning(
            "Controller rejected deployment in Turn 1. Injecting raw RESTConf error log into state "
            "and looping back to Phase 2 (PDDL Parsing) for autonomous blind retry."
        )

        refinement_history = list(state.get("refinement_history") or [])
        refinement_history.append(summary)

        return {
            "radg_decision": "replan",
            "error_context": summary,
            "controller_reached": True,
            "controller_error": True,
            "controller_verdict": "replan",
            "refinement_history": refinement_history,
            "refinement_count": 1,
            "messages": [AIMessage(content=summary, name="controller")],
        }

    # Turn 2 handling (Autonomous Blind Retry Evaluation)
    if refinement_count == 1:
        has_feasible = any(r.get("feasible") for r in qot_results)
        is_nominal = (intent_class == "I_Nominal") if intent_class else has_feasible

        if is_nominal and evaluate_radg(qot_results) == "approve":
            summary = "Controller (Physical Gate): Autonomous repair successfully APPROVED."
            return {
                "radg_decision": "approve",
                "error_context": None,
                "controller_reached": True,
                "controller_error": False,
                "controller_verdict": "approve",
                "messages": [AIMessage(content=summary, name="radg")],
            }

        # If blind retry failed in Turn 2, trigger human operator incident response interrupt
        summary = (
            "Controller Deployment Error (Turn 2 Blind Retry Failed): "
            "Autonomous recovery failed to resolve physical/semantic violations. "
            "Operator incident response required."
        )
        logger.warning(summary)

        response = interrupt({
            "decision": "replan",
            "reason": summary,
            "suggestion": (
                "The LLM attempted autonomous blind recovery from the RESTCONF error log, "
                "but physical and semantic constraints remain violated. "
                "Operator intervention required: provide a refined, feasible intent to recover."
            ),
            "qot_results": qot_results,
            "controller_error": True,
            "options": ["replan"],
        })

        feedback = ""
        if isinstance(response, str):
            feedback = response.strip()
        elif isinstance(response, dict):
            fb = response.get("feedback") or response.get("refinement")
            if fb:
                feedback = str(fb).strip()
            elif "action" in response and response["action"] not in ("refine", "replan", "approve"):
                feedback = str(response["action"]).strip()

        resolved_fb = feedback if feedback else summary
        refinement_history = list(state.get("refinement_history") or [])
        refinement_history.append(resolved_fb)

        return {
            "radg_decision": "replan",
            "error_context": resolved_fb,
            "controller_reached": True,
            "controller_error": True,
            "controller_verdict": "replan",
            "refinement_history": refinement_history,
            "refinement_count": 2,
            "messages": [AIMessage(content=summary, name="controller")],
        }

    # Turn 3+ (Human Incident Response Recovery)
    decision = evaluate_radg(qot_results)
    if decision == "approve":
        summary = "Controller (Physical Gate): Incident response recovery intent successfully APPROVED."
        return {
            "radg_decision": "approve",
            "error_context": None,
            "controller_reached": True,
            "controller_error": False,
            "controller_verdict": "approve",
            "messages": [AIMessage(content=summary, name="radg")],
        }

    # If recovery failed for any reason
    summary = "Controller (Physical Gate): Replan required on recovery."
    return {
        "radg_decision": "replan",
        "error_context": summary,
        "controller_reached": True,
        "controller_error": True,
        "controller_verdict": "replan",
        "messages": [AIMessage(content=summary, name="radg")],
    }


def build_llm_only_graph() -> StateGraph:
    """Construct the StateGraph for LLM-Only baseline."""
    builder = StateGraph(AgentState)  # type: ignore

    builder.add_node("intent_ingest", intent_ingest_node)
    builder.add_node("pddl_parser", pddl_parser_node)
    builder.add_node("reverse_prompt", reverse_prompt_node)
    builder.add_node("semantic_gate", bypassed_semantic_gate_node)
    builder.add_node("symbolic_solver", symbolic_solver_node)
    builder.add_node("qot_validation", qot_validation_node)
    builder.add_node("radg", controller_surrogate_radg_node)
    builder.add_node("plan_synthesizer", plan_synthesizer_node)

    builder.add_edge(START, "intent_ingest")
    builder.add_edge("intent_ingest", "pddl_parser")
    builder.add_edge("pddl_parser", "reverse_prompt")
    builder.add_edge("reverse_prompt", "semantic_gate")

    # Semantic Gate forwards unconditionally to symbolic solver (no HITL clarify edge)
    builder.add_edge("semantic_gate", "symbolic_solver")

    builder.add_edge("symbolic_solver", "qot_validation")
    builder.add_edge("qot_validation", "radg")
    builder.add_conditional_edges("radg", radg_route)
    builder.add_edge("plan_synthesizer", END)

    return builder


def compile_llm_only_graph(*, checkpointer=None) -> CompiledStateGraph:
    """Compile the LLM-Only graph with an optional checkpointer."""
    builder = build_llm_only_graph()
    kwargs: dict = {}
    if checkpointer:
        kwargs["checkpointer"] = checkpointer
    return builder.compile(**kwargs)
