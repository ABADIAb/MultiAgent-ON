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
1. OPERATOR INTENT: The operator's natural language request, including any subsequent clarifications or refinements provided by the operator.
2. RECONSTRUCTION: A system's reverse-prompting reconstruction of what it parsed.

Your task: Rate how faithfully the reconstruction captures the OPERATOR INTENT.

Key evaluation rules:
- If the operator provided clarifications, constraint adjustments, or relaxations (e.g., avoiding specific nodes/links, relaxing GSNR, or modifying endpoints), the reconstruction MUST reflect those adjustments. This is faithful adherence to operator instructions, NOT divergence (score near 0.0).
- Penalize ONLY unprompted hallucinations (constraints neither in the base intent nor in the operator's refinements) or omitted constraints that were explicitly requested.

Output ONLY a single decimal number between 0.0 and 1.0, where:
  0.0 = The reconstruction faithfully matches the operator's current intent and refinements.
  1.0 = The reconstruction is completely wrong, contradicts operator feedback, or has severe hallucinated constraints.
  0.2 = Minor paraphrasing differences but all active constraints match operator intent.
  0.5 = Some requested constraints are missing or contradictory constraints were introduced.

No explanation, no other text — just the number."""


def _score_semantic_agreement(intent: str, reconstruction: str) -> float:
    """Call the LLM to score semantic divergence between intent and reconstruction.

    Args:
        intent: The effective operator intent (base + clarifications/refinements).
        reconstruction: The LLM reverse-prompt reconstruction from Phase 3.

    Returns:
        d_sem in [0.0, 1.0]. Higher = more divergence.
    """
    llm = get_llm()
    messages = [
        SystemMessage(content=_AGREEMENT_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"OPERATOR INTENT (with clarifications):\n{intent}\n\n"
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
    between effective operator intent (base enriched_intent + refinement_history)
    and hitl_reconstruction (Layer 2).

    Args:
        state: AgentState with pddl_valid, enriched_intent, hitl_reconstruction,
            and optional refinement_history.

    Returns:
        Partial state update with usem_score, usem_passed, error_context, and summary message.
    """
    v_struct: bool = state.get("pddl_valid") or False
    intent: str = state.get("enriched_intent") or ""
    reconstruction: str = state.get("hitl_reconstruction") or ""
    refinement_history: list[str] = state.get("refinement_history") or []

    # Layer 2: only meaningful if Layer 1 passed and we have a reconstruction
    if v_struct and reconstruction:
        if refinement_history:
            refinements_block = "\n".join(f"- {r}" for r in refinement_history)
            effective_intent = (
                f"{intent}\n\n"
                f"Operator Clarifications & Refinements:\n{refinements_block}"
            )
        else:
            effective_intent = intent
        d_sem = _score_semantic_agreement(effective_intent, reconstruction)
    elif not v_struct:
        # Structural failure — Layer 1 already sets U_sem = 1
        d_sem = 0.0  # compute_usem will return 1.0
    else:
        d_sem = 0.0

    usem = compute_usem(v_struct=v_struct, d_sem=d_sem)
    passed = evaluate_semantic_gate(usem=usem, tau_sem=DEFAULT_TAU_SEM)

    gate_result = "PASS" if passed else "FAIL (clarify)"
    summary = (
        f"Semantic Gate [{gate_result}]: U_sem={usem:.3f} "
        f"(structural={'OK' if v_struct else 'FAIL'}, d_sem={d_sem:.3f}, "
        f"tau={DEFAULT_TAU_SEM})"
    )
    logger.info(summary)

    err_ctx = state.get("error_context")
    if not passed and not err_ctx:
        if not v_struct:
            err_ctx = "PDDL Context-Free Grammar (CFG) structural validation failed."
        else:
            err_ctx = f"High semantic divergence (d_sem={d_sem:.2f} > tau={DEFAULT_TAU_SEM})."

    return {
        "usem_score": usem,
        "usem_passed": passed,
        "error_context": err_ctx if not passed else None,
        "messages": [AIMessage(content=summary, name="semantic_gate")],
    }


def semantic_gate_route(state: AgentState) -> str:
    """Conditional edge: route based on Semantic Gate outcome.

    Returns:
        - ``"symbolic_solver"`` if U_sem <= tau_sem (gate passes).
        - ``"hitl_clarify"`` if U_sem > tau_sem (clarify via Phase 3b HITL loop).
    """
    if state.get("usem_passed"):
        return "symbolic_solver"
    return "hitl_clarify"

