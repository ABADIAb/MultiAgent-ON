"""Semantic Gate — pure decision logic for U_sem computation.

Implements the fail-fast Semantic Uncertainty gate from Architecture V5,
Phase 3. Evaluates intent clarity BEFORE running the expensive Symbolic
Solver and QoT physics, saving computation when the intent is ambiguous.

Mathematical formulation (ProblemStatement_v5, Section 4.2):

    U_sem = 1          if v_struct = 0  (PDDL CFG structural failure)
    U_sem = d_sem      if v_struct = 1  (semantic divergence score)

    Gate passes (proceed to solver) iff U_sem <= tau_sem.

Placement: core/ — pure deterministic logic, no LLM calls, no framework deps.
"""

from __future__ import annotations

#: Default threshold tau_sem for the semantic gate.
#: Tunable hyperparameter — 0.3 means >30% divergence triggers clarification.
DEFAULT_TAU_SEM: float = 0.3


def compute_usem(v_struct: bool, d_sem: float) -> float:
    """Compute the Semantic Uncertainty score U_sem.

    Implements the piecewise formula from ProblemStatement_v5 Section 4.2:

        U_sem = 1       if v_struct = 0 (PDDL CFG structural failure)
        U_sem = d_sem   if v_struct = 1 (semantic divergence)

    Args:
        v_struct: Whether the PDDL string passed CFG structural validation.
            True = structurally valid, False = structural failure.
        d_sem: Semantic divergence score in [0, 1]. 0 = perfect agreement,
            1 = complete divergence. Sourced from the LLM-scored agreement
            between original intent and reverse-prompt reconstruction.

    Returns:
        U_sem in [0, 1]. Lower is better (less uncertain).
    """
    if not v_struct:
        # Layer 1: structural failure → maximum uncertainty
        return 1.0

    # Layer 2: semantic divergence drives uncertainty
    return float(d_sem)


def evaluate_semantic_gate(usem: float, tau_sem: float = DEFAULT_TAU_SEM) -> bool:
    """Evaluate whether the semantic gate passes (intent is sufficiently clear).

    The gate passes (True) when U_sem <= tau_sem, meaning the operator's
    intent is clear enough to proceed to the Symbolic Solver without
    triggering HITL clarification.

    Args:
        usem: Semantic Uncertainty score from compute_usem(), in [0, 1].
        tau_sem: Threshold for acceptable uncertainty. Default: 0.3.
            U_sem <= tau_sem → pass (proceed).
            U_sem >  tau_sem → fail (clarify via HITL).

    Returns:
        True if the gate passes (low uncertainty → proceed to solver).
        False if the gate fails (high uncertainty → clarify via HITL).
    """
    return usem <= tau_sem
