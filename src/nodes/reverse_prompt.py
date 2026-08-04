"""Reverse Prompting HITL node for the Neurosymbolic Intent Pipeline.

Exp 2.2: Implements the formal Human-in-the-Loop convergence mechanism.

1. Takes the PDDL constraints from the parser.
2. Uses an inverse LLM call to reconstruct them as plain English.
3. Presents the reconstruction to the operator via interrupt().
4. The operator can approve, refine (with feedback), or reject.

This prevents semantic drift by forcing the operator to approve
a precise natural language reconstruction of what the system parsed,
not the raw PDDL.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import interrupt

from src.core.llm import get_llm
from src.core.state import AgentState

REVERSE_PROMPT_SYSTEM = """\
You are the Reverse Prompting module of a Neurosymbolic Orchestrator \
for a Software-Defined Optical Network (SDON).

Your job is to read a PDDL problem string that describes an optical \
network routing request, and rewrite it as a clear, human-readable \
English paragraph that a network operator can verify.

Rules:
- Start with "I understand you want to..."
- Mention source and target nodes explicitly.
- List ALL constraints (GSNR, latency, avoid links, etc.) clearly.
- Do NOT add information that is not in the PDDL.
- Do NOT include the PDDL syntax itself — only plain English.
- Be concise but complete.\
"""


def reverse_prompt_node(state: AgentState) -> dict:
    """HITL Reverse Prompting node with LLM reconstruction.

    1. Calls the LLM to reconstruct PDDL → natural language.
    2. Presents the reconstruction to the operator via interrupt().
    3. Processes approve/refine/reject response.

    Returns:
        Partial state update with hitl_approved, hitl_reconstruction,
        error_context, and messages.
    """
    pddl = state.get("pddl_constraints", "No constraints generated")

    # Inverse LLM call: PDDL → English reconstruction
    llm = get_llm()
    messages = [
        SystemMessage(content=REVERSE_PROMPT_SYSTEM),
        HumanMessage(content=pddl),
    ]
    reconstruction_response = llm.invoke(messages)
    reconstruction = reconstruction_response.content

    # Present reconstruction to operator and pause
    response = interrupt({
        "reconstruction": reconstruction,
        "options": ["approve", "refine", "reject"],
        "message": "Please review the parsed constraints and choose an action.",
    })

    action = response.get("action", "reject") if isinstance(response, dict) else "reject"
    approved = action == "approve"
    feedback = response.get("feedback", "") if isinstance(response, dict) else ""

    return {
        "hitl_approved": approved,
        "hitl_reconstruction": reconstruction,
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
