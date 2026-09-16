"""Reverse Prompting & HITL Clarification nodes for the V5 Pipeline.

Exp 2.2 / 3.2: Implements the formal Human-in-the-Loop convergence mechanism
for PDDL validation via natural language reconstruction.

Architecture V5 flow:
  pddl_parser → reverse_prompt → semantic_gate
    → (U_sem <= tau) → symbolic_solver (0 interrupts)
    → (U_sem >  tau) → hitl_clarify (interrupt for operator feedback) → pddl_parser
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

CRITICAL INSTRUCTIONS:
- Focus ONLY on the (:goal ...) section of the PDDL to identify the routing request and operator constraints.
- NEVER mention or list topology facts, available links, or connected nodes from (:init ...) or (:objects ...). Do not discuss network infrastructure.
- Start with "I understand you want to..."
- Mention the source and target nodes explicitly.
- State all active constraints (e.g., minimum GSNR in dB, required bandwidth, avoided nodes, avoided links, waypoints via a node) clearly.
- STRICT NEGATIVE INSTRUCTION: NEVER mention or invent any node name that is NOT explicitly written in the PDDL below! If the PDDL does not have (avoid-node ...), DO NOT state that any node is avoided!
- If the PDDL contains (via <node>), express it as "via <node>" or "using <node> as a transit waypoint". DO NOT invent any avoided nodes!
- If the PDDL contains (max-hops 1), express it as "over a single direct span". If (max-hops <N>) with N > 1, express it as "a maximum of <N> hops".
- Do NOT report dummy or zero-value constraints (e.g., min-gsnr 0, bandwidth 1). Only report genuine operational constraints.
- Flag any evident inconsistencies or missing endpoints in the PDDL.
- Output ONLY plain English — no PDDL syntax, no code blocks, no filler.

Target format:
"I understand you want to route traffic from <source> to <target> with <constraints>."

EXAMPLES:
Example 1 (Bandwidth constraint):
PDDL goal: (and (route Hamburg Berlin) (bandwidth 100))
Reconstruction: I understand you want to route traffic from Hamburg to Berlin with a required bandwidth of 100.

Example 2 (Waypoint with GSNR):
PDDL goal: (and (route Munich Stuttgart) (min-gsnr 15) (via Ulm))
Reconstruction: I understand you want to route traffic from Munich to Stuttgart via Ulm with a minimum GSNR of 15 dB.

Example 3 (Avoidance constraint):
PDDL goal: (and (route Frankfurt Cologne) (min-gsnr 14) (avoid-node Mannheim))
Reconstruction: I understand you want to route traffic from Frankfurt to Cologne with a minimum GSNR of 14 dB, avoiding node Mannheim.

Example 4 (Single direct span / hop limit):
PDDL goal: (and (route Berlin Frankfurt) (min-gsnr 28) (max-hops 1))
Reconstruction: I understand you want to route traffic from Berlin to Frankfurt over a single direct span with a minimum GSNR of 28 dB.\
"""


def _clean_pddl_for_reverse_prompt(pddl: str) -> str:
    """Filter out verbose topology predicates (connected, link-active) to prevent LLM attention leakage."""
    if not pddl or not isinstance(pddl, str):
        return pddl
    lines = []
    for line in pddl.splitlines():
        stripped = line.strip().lower()
        if (
            stripped.startswith("(connected ")
            or stripped.startswith("(link-active ")
            or stripped.startswith("(link-capacity ")
        ):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def reverse_prompt_node(state: AgentState) -> dict:
    """Automated Reverse Prompting node (Phase 3a: PDDL → English reconstruction).

    Translates the formal PDDL specification into a natural language paragraph
    without pausing execution. This reconstruction is passed to the Semantic Gate
    to evaluate semantic divergence (d_sem) and uncertainty (U_sem).

    Args:
        state: AgentState with pddl_constraints.

    Returns:
        Partial state update with hitl_reconstruction and messages.
    """
    pddl = state.get("pddl_constraints", "No constraints generated")
    clean_pddl = _clean_pddl_for_reverse_prompt(pddl)

    # Inverse LLM call: PDDL → English reconstruction
    llm = get_llm()
    messages = [
        SystemMessage(content=REVERSE_PROMPT_SYSTEM),
        HumanMessage(content=clean_pddl),
    ]
    reconstruction_response = llm.invoke(messages)
    reconstruction = (
        reconstruction_response.content
        if isinstance(reconstruction_response.content, str)
        else str(reconstruction_response.content)
    )

    return {
        "hitl_reconstruction": reconstruction,
        "messages": [
            AIMessage(
                content=f"Reconstructed intent: {reconstruction}",
                name="reverse_prompt",
            )
        ],
    }


MAX_REFINEMENTS: int = 3


def hitl_clarify_node(state: AgentState) -> dict:
    """HITL Clarification node (Phase 3b: Ambiguity Disambiguation).

    Invoked strictly when Semantic Gate fails (U_sem > tau_sem or structural failure).
    Suspends execution via interrupt(), presenting the system's ambiguous understanding
    and validation errors to the operator to gather targeted refinement feedback.

    Args:
        state: AgentState with hitl_reconstruction, usem_score, and error_context.

    Returns:
        Partial state update with hitl_approved, error_context, and messages.
    """
    reconstruction = state.get("hitl_reconstruction") or "No reconstruction available"
    usem_score = state.get("usem_score")
    error_context = state.get("error_context")
    pddl_valid = state.get("pddl_valid")
    refinement_count = state.get("refinement_count") or 0
    refinement_history = list(state.get("refinement_history") or [])

    # Guard: Bounded loop (N_max = 3) to prevent context window saturation
    if refinement_count >= MAX_REFINEMENTS:
        abort_msg = (
            f"Maximum refinement attempts (N_max={MAX_REFINEMENTS}) reached. "
            "Execution suspended to protect against model context window saturation and token budget exhaustion."
        )
        interrupt({
            "status": "aborted",
            "reason": abort_msg,
            "options": ["cancel"],
            "reconstruction": reconstruction,
            "refinement_history": refinement_history,
            "message": abort_msg,
        })
        return {
            "hitl_approved": False,
            "error_context": f"Aborted: {abort_msg}",
            "messages": [
                AIMessage(
                    content=f"HITL Clarification: Aborted — {abort_msg}",
                    name="hitl_clarify",
                )
            ],
        }

    options = ["approve", "refine", "cancel"] if pddl_valid else ["refine", "cancel"]

    response = interrupt({
        "status": "clarification_required",
        "reconstruction": reconstruction,
        "usem_score": usem_score,
        "pddl_valid": pddl_valid,
        "error_context": error_context,
        "options": options,
        "message": (
            "Semantic uncertainty is high or intent requires clarification. "
            "Please review the system's understanding and provide refined instructions."
        ),
    })

    feedback = ""
    action = "refine"
    if isinstance(response, str):
        feedback = response.strip()
    elif isinstance(response, dict):
        action = response.get("action", "refine")
        fb = response.get("feedback") or response.get("refinement")
        if fb:
            feedback = str(fb).strip()
        elif action not in ("refine", "cancel", "clarify", "approve"):
            feedback = str(action).strip()

    # Operator explicitly approved the current understanding
    if action == "approve" and pddl_valid:
        return {
            "hitl_approved": True,
            "usem_passed": True,
            "error_context": None,
            "messages": [
                AIMessage(
                    content=(
                        f"HITL Clarification: Operator approved understanding — "
                        f"proceeding to solver: {reconstruction}"
                    ),
                    name="hitl_clarify",
                )
            ],
        }

    resolved_feedback = feedback if feedback else (error_context or "Refinement requested by operator")

    updated_history = list(refinement_history)
    updated_history.append(resolved_feedback)
    new_count = refinement_count + 1

    return {
        "hitl_approved": False,
        "error_context": resolved_feedback,
        "refinement_history": updated_history,
        "refinement_count": new_count,
        "messages": [
            AIMessage(
                content=f"HITL Clarification: {action}" + (f" — {feedback}" if feedback else ""),
                name="hitl_clarify",
            )
        ],
    }


def hitl_clarify_route(state: AgentState) -> str:
    """Conditional edge: route based on operator clarification decision.

    Returns:
        - "symbolic_solver" if operator approved the understanding (hitl_approved=True).
        - "__end__" if aborted or cancelled.
        - "pddl_parser" if operator requested refinement (loop back).
    """
    if state.get("hitl_approved"):
        return "symbolic_solver"
    err = state.get("error_context") or ""
    if err.startswith("Aborted:") or err == "cancel":
        return "__end__"
    return "pddl_parser"

