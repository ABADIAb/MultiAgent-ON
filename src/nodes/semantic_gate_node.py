"""Semantic Gate LangGraph node for the V5 Neurosymbolic Intent Pipeline.

Exp 3.1 (Phase 3): Evaluates the Semantic Uncertainty U_sem before
running the expensive Symbolic Solver and QoT validation. This is the
fail-fast mechanism of Architecture V5.

Two-layer evaluation:
  Layer 1 (Structural): Reads pddl_valid from state (set by pddl_parser).
  Layer 2 (Semantic): Calls the LLM to score agreement between the original
      enriched_intent and the reverse-prompt reconstruction (hitl_reconstruction).
      Returns a divergence score d_sem in [0.0, 1.0].

Placement: nodes/ — LangGraph node function with conditional routing.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.core.llm import get_llm
from src.core.semantic_gate import DEFAULT_TAU_SEM, compute_usem, evaluate_semantic_gate
from src.core.state import AgentState

logger = logging.getLogger(__name__)

_AGREEMENT_SYSTEM_PROMPT = """\
You are a semantic similarity evaluator for an optical network intent orchestrator.

You will be given:
1. ORIGINAL INTENT: The operator's original natural language request.
2. RECONSTRUCTION: A system's reverse-prompting reconstruction of what it parsed.

Your task: Rate how closely the reconstruction captures the ORIGINAL INTENT.

Output ONLY a single decimal number between 0.0 and 1.0, where:
  0.0 = The reconstruction perfectly matches the original intent (no divergence).
  1.0 = The reconstruction is completely wrong or missing critical constraints.
  0.3 = Minor paraphrasing differences but key constraints are intact.
  0.6 = Some constraints are missing or changed.

No explanation, no other text — just the number."""


def _score_semantic_agreement(intent: str, reconstruction: str) -> float:
    """Call the LLM to score semantic divergence between intent and reconstruction.

    Args:
        intent: The enriched operator intent from Phase 1.
        reconstruction: The LLM reverse-prompt reconstruction from Phase 3.

    Returns:
        d_sem in [0.0, 1.0]. Higher = more divergence.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content=_AGREEMENT_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"ORIGINAL INTENT:\n{intent}\n\n"
                f"RECONSTRUCTION:\n{reconstruction}"
            )
        ),
    ]
    response = llm.invoke(messages)
    raw = response.content.strip() if isinstance(response.content, str) else "0.5"

    try:
        score = float(raw)
        # Clamp to [0, 1] in case LLM returns out-of-range value
        return max(0.0, min(1.0, score))
    except ValueError:
        logger.warning(
            "Semantic agreement score parse failed for response '%s'. Defaulting to 0.5.",
            raw,
        )
        return 0.5  # Unknown → treat as borderline


def semantic_gate_node(state: AgentState) -> dict:
    """Evaluate Semantic Uncertainty U_sem and decide gate outcome.

    Reads pddl_valid (Layer 1) and calls the LLM to score agreement
    between enriched_intent and hitl_reconstruction (Layer 2).

    Args:
        state: AgentState with pddl_valid, enriched_intent, hitl_reconstruction.

    Returns:
        Partial state update with usem_score, usem_passed, and a summary message.
    """
    v_struct: bool = state.get("pddl_valid") or False
    intent: str = state.get("enriched_intent") or ""
    reconstruction: str = state.get("hitl_reconstruction") or ""

    hitl_approved: bool | None = state.get("hitl_approved")

    # Layer 2: only meaningful if Layer 1 passed and we have a reconstruction
    if v_struct and reconstruction:
        d_sem = _score_semantic_agreement(intent, reconstruction)
    elif not v_struct:
        # Structural failure — Layer 1 already sets U_sem = 1
        d_sem = 0.0  # irrelevant; compute_usem will return 1.0
    else:
        # No reconstruction yet (first pass before reverse_prompt)
        # Treat as low divergence — the reverse_prompt node will clarify
        d_sem = 0.0

    usem = compute_usem(v_struct=v_struct, d_sem=d_sem)
    passed = evaluate_semantic_gate(usem=usem, tau_sem=DEFAULT_TAU_SEM)

    # If operator explicitly requested refinement, enforce gate failure
    if hitl_approved is False:
        passed = False
        usem = max(usem, 1.0)

    gate_result = "PASS" if passed else "FAIL (clarify)"
    summary = (
        f"Semantic Gate [{gate_result}]: U_sem={usem:.3f} "
        f"(structural={'OK' if v_struct else 'FAIL'}, d_sem={d_sem:.3f}, "
        f"tau={DEFAULT_TAU_SEM})"
    )
    logger.info(summary)

    return {
        "usem_score": usem,
        "usem_passed": passed,
        "messages": [AIMessage(content=summary, name="semantic_gate")],
    }


def semantic_gate_route(state: AgentState) -> str:
    """Conditional edge: route based on Semantic Gate outcome.

    Returns:
        - ``"symbolic_solver"`` if U_sem <= tau_sem (gate passes).
        - ``"pddl_parser"`` if U_sem > tau_sem (clarify via refinement loop).
    """
    if state.get("usem_passed"):
        return "symbolic_solver"
    return "pddl_parser"

