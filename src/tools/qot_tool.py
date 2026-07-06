"""QoT LangChain Tool — Quality of Transmission Check.

Thin @tool wrapper around the qot_calculator physics engine.
Accepts a path description and returns feasibility assessment
compatible with the LangGraph orchestrator.
"""

from __future__ import annotations

from langchain_core.tools import tool

from src.core.models import Amplifier, FiberLink
from src.core.qot_calculator import assess_qot


@tool
def qot_check(
    path: list[dict],
    bitrate_gbps: int = 100,
) -> dict:
    """Check Quality of Transmission (QoT) feasibility for an optical path.

    Evaluates whether a candidate lightpath meets the physical-layer
    constraints (SNR threshold and receiver power threshold) using the
    GN model for nonlinear interference estimation.

    Args:
        path: List of fiber link descriptions. Each link is a dict with:
            - link_id (int): Unique link identifier.
            - src_node_id (int): Source node ID.
            - dst_node_id (int): Destination node ID.
            - length_km (float): Fiber length in km.
            - port_loss_dB (float, optional): Node port insertion loss in dB.
            - amplifiers (list[dict], optional): EDFAs on the link, each with:
                - position_km (float): Distance from link start in km.
                - gain_dB (float): EDFA gain in dB.
                - amp_type (str): "booster", "ila", or "preamp".
                - nf_dB (float, optional): Noise figure in dB (auto-computed if omitted).
                - att_dB (float, optional): Attenuator loss in dB.
        bitrate_gbps: Demand bitrate — 10, 100, or 200 Gbps. Default: 100.

    Returns:
        Dict with keys: feasible (bool), snr_dB (float), power_dBm (float).
        On error, returns dict with key: error (str).
    """
    try:
        fiber_links = [FiberLink(**link_data) for link_data in path]
        result = assess_qot(fiber_links, bitrate_gbps=bitrate_gbps)
        return {
            "feasible": result.feasible,
            "snr_dB": result.snr_dB,
            "power_dBm": result.power_dBm,
        }
    except (ValueError, TypeError) as e:
        return {"error": str(e)}
