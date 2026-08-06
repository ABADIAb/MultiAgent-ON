"""Reverse Prompting HITL node for the V5 Neurosymbolic Intent Pipeline.

Exp 2.2 / 3.2: Implements the formal Human-in-the-Loop convergence mechanism
for PDDL validation via natural language reconstruction.

V5 Changes from V4:
  - The node no longer owns the approve/refine/reject routing decision.
  - The Semantic Gate (semantic_gate_node) now evaluates U_sem and decides
    whether to loop back for clarification or proceed to the Symbolic Solver.
  - This node still performs the LLM reconstruction and the interrupt(), but
    the routing decision belongs to the Semantic Gate conditional edge.
  - A simplified response schema: approve (continue) or refine (provide feedback).

Architecture V5 flow:
  pddl_parser → reverse_prompt → semantic_gate
    → (U_sem <= tau) → symbolic_solver
    → (U_sem >  tau) → reverse_prompt  (clarification loop)
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

    Performs two actions:
    1. Calls the LLM to reconstruct PDDL → natural language.
    2. Presents the reconstruction to the operator via interrupt().

    After the interrupt, control returns to the graph. The Semantic Gate
    (next node) evaluates U_sem and decides whether to loop back here
    for further clarification or proceed to the Symbolic Solver.

    Args:
        state: AgentState with pddl_constraints.

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

    # Present reconstruction to operator and pause for review
    # V5: simplified schema — the gate decides the routing, not this node
    response = interrupt({
        "reconstruction": reconstruction,
        "options": ["approve", "refine"],
        "message": (
            "Please review my understanding of your request. "
            "If accurate, approve to proceed. "
            "If not, choose 'refine' and provide feedback."
        ),
    })

    action = response.get("action", "approve") if isinstance(response, dict) else "approve"
    approved = action == "approve"
    feedback = response.get("feedback", "") if isinstance(response, dict) else ""

    return {
        "hitl_approved": approved,
        "hitl_reconstruction": reconstruction,
        "messages": [
            AIMessage(
                content=f"HITL: {action}" + (f" — {feedback}" if feedback else ""),
                name="reverse_prompt",
            )
        ],
        "error_context": feedback if action == "refine" else None,
    }
