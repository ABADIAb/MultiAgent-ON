"""QoT Validation node for the V5 Neurosymbolic Intent Pipeline.

Exp 3.1 (Batch 2): Replaces the Sprint 2 placeholder with real GN-model
physics. For each candidate path from the Symbolic Solver, calls the
qot_bridge to convert path dicts into models.FiberLink objects, then
runs assess_qot() to compute GSNR and receiver power.

This is Phase 5 in Architecture V5.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage

from src.core.models import FiberLink
from src.core.qot_calculator import assess_qot
from src.core.state import AgentState

logger = logging.getLogger(__name__)


def qot_validation_node(state: AgentState) -> dict:
    """Validate candidate paths using the GN-model QoT physics engine.

    For each candidate path from the Symbolic Solver:
    1. Instantiates models.FiberLink objects directly from candidate physics data.
    2. Calls assess_qot() to compute GSNR and receiver power.
    3. Records feasibility verdict (GSNR >= threshold AND power >= threshold).

    Paths that fail conversion (e.g. missing physics data) are marked
    infeasible with an error note — the RADG gate handles the outcome.

    Args:
        state: AgentState with candidate_paths populated by symbolic_solver.

    Returns:
        Partial state update with qot_results (list of dicts per path).
    """
    candidates = state.get("candidate_paths") or []

    qot_results = []
    for candidate in candidates:
        path_nodes = candidate.get("nodes", [])
        path_label = " → ".join(path_nodes) if path_nodes else "unknown"

        try:
            link_physics_list = candidate.get("link_physics", [])
            fiber_links = [FiberLink(**physics) for physics in link_physics_list]

            if not fiber_links:
                qot_results.append({
                    "path": path_nodes,
                    "feasible": False,
                    "snr_dB": 0.0,
                    "power_dBm": -99.0,
                    "snr_threshold_dB": 0.0,
                    "error": "No fiber links to evaluate.",
                })
                continue

            result = assess_qot(fiber_links, bitrate_gbps=100)
            qot_results.append({
                "path": path_nodes,
                "feasible": result.feasible,
                "snr_dB": round(result.snr_dB, 3),
                "power_dBm": round(result.power_dBm, 3),
                "snr_threshold_dB": result.snr_threshold_dB,
                "error": None,
            })
            logger.debug(
                "QoT %s: %s | SNR=%.2f dB (thresh=%.1f) | P_rx=%.2f dBm",
                "PASS" if result.feasible else "FAIL",
                path_label,
                result.snr_dB,
                result.snr_threshold_dB,
                result.power_dBm,
            )

        except (KeyError, ValueError) as exc:
            logger.warning("QoT evaluation failed for path %s: %s", path_label, exc)
            qot_results.append({
                "path": path_nodes,
                "feasible": False,
                "snr_dB": 0.0,
                "power_dBm": -99.0,
                "snr_threshold_dB": 0.0,
                "error": str(exc),
            })

    feasible_count = sum(1 for r in qot_results if r["feasible"])
    total = len(qot_results)

    summary = (
        f"QoT validation (GN model): {feasible_count}/{total} paths feasible."
    )

    return {
        "qot_results": qot_results,
        "messages": [
            AIMessage(content=summary, name="qot_validation")
        ],
    }
