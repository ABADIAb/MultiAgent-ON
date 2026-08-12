"""Risk-Adaptive Decision Gate (RADG) — physical risk decision function.

Implements the Physical Risk Gate from Architecture V5, Phase 6.
This is the core contribution of the thesis: a deterministic decision function
that evaluates QoT feasibility outcomes and maps them to an action.

Mathematical formulation (ProblemStatement_v5, Section 4.3):
  Given U_sem <= tau_sem (already cleared by the Semantic Gate):

    D = "approve"  if any path has QoT_valid = 1  (at least one feasible route)
    D = "replan"   if all paths have QoT_valid = 0 (physics failed → HITL)

Note: The "clarify" action is handled upstream by the Semantic Gate.
The RADG only sees paths that already passed semantic validation.

Placement: core/ — pure deterministic decision function, no LLM calls.
"""

from __future__ import annotations


def evaluate_radg(qot_results: list[dict]) -> str:
    """Evaluate the Physical Risk Gate decision.

    Inspects the QoT feasibility results from Phase 5 and maps them
    to an action from the RADG action space {approve, replan}.

    Decision rule:
      - ``"approve"`` if at least one candidate path is feasible.
      - ``"replan"`` if no candidate path is feasible (or list is empty).

    Args:
        qot_results: List of QoT result dicts from qot_validation_node.
            Each dict must have a ``feasible`` key (bool).

    Returns:
        ``"approve"`` or ``"replan"``.
    """
    if not qot_results:
        return "replan"

    any_feasible = any(result.get("feasible", False) for result in qot_results)
    return "approve" if any_feasible else "replan"
