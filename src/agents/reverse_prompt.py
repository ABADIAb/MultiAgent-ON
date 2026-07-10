"""Reverse Prompting HITL node for the Neurosymbolic Intent Pipeline.

Sprint 2 (Exp 2.2) will implement:
- Inverse LLM call to reconstruct PDDL → natural language
- Full HITL approval/refine/reject flow

Current: Placeholder that uses LangGraph interrupt() to pause
for operator approval, testing the HITL infrastructure.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langgraph.types import interrupt

from src.core.state import AgentState


def reverse_prompt_node(state: AgentState) -> dict:
    """HITL Reverse Prompting node.

    Pauses execution and presents the PDDL constraints to the operator
    for approval. Uses LangGraph interrupt() for durable pause.

    The operator can:
    - approve: Continue to Symbolic Solver
    - refine: Loop back to PDDL Parser with feedback
    - reject: Abort the pipeline

    Returns:
        Partial state update with hitl_approved and hitl_reconstruction.
    """
    pddl = state.get("pddl_constraints", "No constraints generated")

    # Present reconstruction to operator and pause
    response = interrupt({
        "reconstruction": f"I understand your intent as: {pddl}",
        "options": ["approve", "refine", "reject"],
        "message": "Please review the parsed constraints and choose an action.",
    })

    action = response.get("action", "reject") if isinstance(response, dict) else "reject"
    approved = action == "approve"
    feedback = response.get("feedback", "") if isinstance(response, dict) else ""

    return {
        "hitl_approved": approved,
        "hitl_reconstruction": pddl,
        "messages": [
            AIMessage(
                content=f"HITL decision: {action}" + (f" — {feedback}" if feedback else ""),
                name="reverse_prompt",
            )
        ],
        "error_context": feedback if action == "refine" else None,
    }


def hitl_route(state: AgentState) -> str:
    """Conditional edge: route based on HITL approval status.

    Returns:
        - "symbolic_solver" if approved
        - "pddl_parser" if refinement requested
        - "__end__" if rejected or no decision
    """
    approved = state.get("hitl_approved")

    if approved is True:
        return "symbolic_solver"

    # Check if refinement was requested (error_context has feedback)
    if approved is False and state.get("error_context"):
        return "pddl_parser"

    return "__end__"
