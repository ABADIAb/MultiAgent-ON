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
import re

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

Your task: Rate the semantic divergence (d_sem) between the RECONSTRUCTION and the OPERATOR INTENT on a scale from 0.0 to 1.0.

Key evaluation rules:
- Focus strictly on meaning and constraint alignment, NOT literal wording:
  * Do NOT penalize the reconstruction for natural phrasing differences (e.g. "I understand you want to route..." vs "Route...").
  * Do NOT penalize technical equivalence, such as "single direct span" or "direct link" being expressed as "maximum of 1 hop" or "1 hop".
  * Do NOT penalize fixing obvious typos or mapping location names to canonical topological names (e.g. "Frankort" -> "Frankfurt").
  * If the endpoints and all requested constraints (GSNR, bandwidth, avoid nodes/links, hops) match the intent, score 0.0 or 0.1.
- If the operator provided refinements or constraint updates, the reconstruction MUST reflect those adjustments (score near 0.0).
- Penalize ONLY genuine discrepancies:
  * Hallucinated constraints: Constraints stated in the reconstruction that the operator never requested.
  * Omitted constraints: Constraints explicitly requested by the operator that the reconstruction dropped.
  * Inconsistencies: Contradictory endpoints or flagged syntax/resolution errors (score 1.0).

Scoring scale:
  0.0 = Complete semantic match: Endpoints and all requested constraints match faithfully.
  0.1 = Minor natural language paraphrasing, but identical constraints and endpoints.
  0.2 = Slight wording variations, preserving all active constraints.
  0.5 = Meaningful discrepancy: A requested constraint was omitted, or an unprompted constraint was added.
  1.0 = Wrong endpoints, contradictory constraints, or unresolved errors.

Output ONLY a single decimal number between 0.0 and 1.0 (e.g., 0.0, 0.1, 0.2, 0.5, 1.0). No explanation, no other text."""


def _clean_intent_for_evaluation(intent: str) -> str:
    """Extract clean natural language statement without metadata pipes or topology dumps."""
    clean = intent.split("\nTopology Context:")[0].strip()
    clean = clean.split("Topology Context:")[0].strip()
    if " | Source:" in clean or " | Target:" in clean:
        clean = clean.split(" | Source:")[0].split(" | Target:")[0].strip()
    if clean.lower().startswith("intent:"):
        clean = clean[len("intent:") :].strip()
    return clean.strip()


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

    # Robust multi-stage extraction
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # 1. Direct float parse if the model simply replied with a number
    try:
        score = float(cleaned)
        return max(0.0, min(1.0, score))
    except ValueError:
        pass

    # 2. Keyed pattern match (e.g. "Score: 0.1", "divergence: 0.0", "d_sem = 0.2")
    key_match = re.search(
        r"(?:d_sem|score|divergence|rating|agreement)\s*[:=]?\s*(0(?:\.\d+)?|1(?:\.0+)?)\b",
        cleaned,
        re.IGNORECASE,
    )
    if key_match:
        return max(0.0, min(1.0, float(key_match.group(1))))

    # 3. Explicit standalone line with just a number
    line_match = re.search(r"(?:^|\n)\s*(0(?:\.\d+)?|1(?:\.0+)?)\s*(?:$|\n)", cleaned)
    if line_match:
        return max(0.0, min(1.0, float(line_match.group(1))))

    # 4. Find all explicit decimal floats in [0.0, 1.0] (prefer decimals over bare integers '1' or '0')
    decimal_matches = re.findall(r"\b(0\.\d+|1\.0+)\b", cleaned)
    if decimal_matches:
        return max(0.0, min(1.0, float(decimal_matches[-1])))

    # 5. Any valid float or int in [0.0, 1.0], taking the last occurrence
    all_matches = re.findall(r"\b(0(?:\.\d+)?|1(?:\.0+)?)\b", cleaned)
    if all_matches:
        return max(0.0, min(1.0, float(all_matches[-1])))

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
    active_intent: str | None = state.get("active_intent")
    reconstruction: str = state.get("hitl_reconstruction") or ""
    refinement_history: list[str] = state.get("refinement_history") or []

    # Layer 2: only meaningful if Layer 1 passed and we have a reconstruction
    if v_struct and reconstruction:
        if active_intent:
            effective_intent = _clean_intent_for_evaluation(active_intent)
        elif refinement_history:
            clean_base = _clean_intent_for_evaluation(intent)
            refinements_block = "\n".join(f"- {r}" for r in refinement_history)
            effective_intent = (
                f"{clean_base}\n\n"
                f"Operator Clarifications & Refinements:\n{refinements_block}"
            )
        else:
            effective_intent = _clean_intent_for_evaluation(intent)
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

