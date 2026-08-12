"""RADG LangGraph node for the V5 Neurosymbolic Intent Pipeline.

Exp 3.1 (Phase 6): Implements the Physical Risk Gate that maps QoT
feasibility results to a final RADG decision: approve or replan.

This is Phase 6 in Architecture V5.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from src.core.radg import evaluate_radg
from src.core.state import AgentState

logger = logging.getLogger(__name__)


def radg_node(state: AgentState) -> dict:
    """Physical Risk Gate — map QoT results to a RADG decision.

    Reads qot_results from state, calls evaluate_radg(), and writes
    the decision to state. If the decision is "replan", triggers a
    HITL interrupt to notify the operator and collect refined constraints.

    Args:
        state: AgentState with qot_results from qot_validation_node.

    Returns:
        Partial state update with radg_decision and a summary message.
    """
    qot_results: list[dict] = state.get("qot_results") or []
    decision = evaluate_radg(qot_results)

    feasible_paths = [r for r in qot_results if r.get("feasible")]
    infeasible_count = len(qot_results) - len(feasible_paths)

    if decision == "approve":
        best_snr = max((r["snr_dB"] for r in feasible_paths), default=0.0)
        summary = (
            f"RADG Decision: AUTO-APPROVE | "
            f"{len(feasible_paths)}/{len(qot_results)} paths feasible | "
            f"Best SNR: {best_snr:.2f} dB"
        )
        logger.info(summary)

    else:  # replan
        summary = (
            f"RADG Decision: SUGGEST REPLAN | "
            f"0/{len(qot_results)} paths feasible | "
            f"All {infeasible_count} candidate(s) failed QoT thresholds. "
            f"Consider relaxing GSNR constraints or changing the route."
        )
        logger.warning(summary)

        # HITL interrupt: inform operator and request relaxed constraints
        response = interrupt({
            "decision": "replan",
            "reason": summary,
            "suggestion": (
                "All candidate paths failed physical-layer QoT validation. "
                "Please consider: (1) lowering the minimum GSNR threshold, "
                "(2) accepting a longer route with more amplification, "
                "or (3) splitting the demand into lower bitrate channels."
            ),
            "qot_results": qot_results,
        })

        feedback = ""
        if isinstance(response, str):
            feedback = response.strip()
        elif isinstance(response, dict):
            fb = response.get("feedback") or response.get("refinement")
            if fb:
                feedback = str(fb).strip()
            elif "action" in response and response["action"] not in ("refine", "replan", "approve", "reject"):
                feedback = str(response["action"]).strip()

        return {
            "radg_decision": decision,
            "error_context": feedback if feedback else summary,
            "messages": [AIMessage(content=summary, name="radg")],
        }

    return {
        "radg_decision": decision,
        "error_context": None,
        "messages": [AIMessage(content=summary, name="radg")],
    }


def radg_route(state: AgentState) -> str:
    """Conditional edge: route based on RADG decision.

    Returns:
        - ``"plan_synthesizer"`` if decision is "approve".
        - ``"pddl_parser"`` if decision is "replan" (loop back for refinement).
    """
    decision = state.get("radg_decision")
    if decision == "approve":
        return "plan_synthesizer"
    return "pddl_parser"
