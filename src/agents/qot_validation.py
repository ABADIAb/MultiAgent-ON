"""QoT Validation node for the Neurosymbolic Intent Pipeline.

Sprint 3 will integrate the real QoT calculator for each candidate path.

Current: Pass-through placeholder that marks all candidates as feasible.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from src.core.state import AgentState


def qot_validation_node(state: AgentState) -> dict:
    """Validate candidate paths using the QoT physics engine.

    Placeholder: marks all candidate paths as feasible with dummy SNR values.
    Sprint 3 will call qot_calculator.assess_qot() for each candidate.

    Returns:
        Partial state update with qot_results.
    """
    candidates = state.get("candidate_paths") or []

    # Placeholder: all paths are "feasible"
    qot_results = [
        {
            "path": candidate.get("path", []),
            "feasible": True,
            "snr_dB": 15.0,
            "power_dBm": -10.0,
        }
        for candidate in candidates
    ]

    feasible_count = sum(1 for r in qot_results if r["feasible"])

    return {
        "qot_results": qot_results,
        "messages": [
            AIMessage(
                content=f"QoT validation: {feasible_count}/{len(qot_results)} paths feasible (placeholder).",
                name="qot_validation",
            )
        ],
    }
