"""Core state schema for the V5 Risk-Adaptive Neurosymbolic Intent Pipeline.

Defines the AgentState TypedDict used as the shared state across all nodes
in the V5 StateGraph, plus Pydantic models for structured domain data.

V5 changes from V4:
  - state.FiberLink enriched with amplifiers (list[dict]) and port_loss_dB
    so physics data flows from MockTestbedClient through to the QoT calculator.
  - Added V5 Semantic Gate fields: usem_score, usem_passed.
  - Added V5 RADG field: radg_decision.
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Domain Models (Pydantic) — Topology layer, preserved from V3
# ---------------------------------------------------------------------------


class NetworkNode(BaseModel):
    """A node in the optical network topology."""

    node_id: str
    name: str
    interfaces: list[int] = Field(
        default_factory=list,
        description="List of Logical Termination Point (LTP) IDs.",
    )


class FiberLink(BaseModel):
    """A fiber link connecting two nodes in the topology.

    The ``amplifiers`` field carries the full EDFA configuration for each
    span so the QoT calculator can run without a separate bridge lookup.
    Each amplifier dict matches the ``models.Amplifier`` schema:
      {position_km, gain_dB, amp_type, nf_dB (optional), att_dB (optional)}.
    """

    link_id: str
    source_node: str
    target_node: str
    length_km: float
    num_amplifiers: int = 0
    active_channels: int = 0
    port_loss_dB: float = 0.0
    amplifiers: list[dict] = Field(default_factory=list)


class TopologySnapshot(BaseModel):
    """Structured representation of the testbed topology."""

    nodes: list[NetworkNode] = Field(default_factory=list)
    links: list[FiberLink] = Field(default_factory=list)
    timestamp: str = ""


# ---------------------------------------------------------------------------
# LangGraph State — V4 Neurosymbolic Intent Pipeline
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    """Shared state for the V5 Risk-Adaptive Neurosymbolic Intent Pipeline.

    Fields:
        messages: Append-only message list (uses add reducer).
        enriched_intent: Operator intent after Optical RAG enrichment.
        pddl_constraints: PDDL constraint string from the parser.
        pddl_valid: Whether the PDDL passed CFG validation.
        pddl_parsed_constraints: Structured dict extracted from PDDL for downstream nodes.
            Keys: source (str), destination (str), avoid_links (list[str]), max_hops (int | None).
        hitl_reconstruction: Natural language reconstruction of PDDL.
        hitl_approved: Whether the operator approved via Reverse Prompting.
        topology_snapshot: Current testbed topology.
        candidate_paths: 3-5 paths from the Symbolic Solver.
        qot_results: QoT assessment results per candidate path.
        planning_report: Final synthesized planning report.
        error_context: Error details for debugging.
        usem_score: Semantic Uncertainty score U_sem ∈ [0, 1] from the Semantic Gate.
        usem_passed: Whether U_sem ≤ τ_sem (gate passed → proceed to solver).
        radg_decision: RADG physical gate outcome — "approve" | "replan".
    """

    messages: Annotated[list, operator.add]
    enriched_intent: str | None
    pddl_constraints: str | None
    pddl_valid: bool | None
    pddl_parsed_constraints: dict | None
    hitl_reconstruction: str | None
    hitl_approved: bool | None
    topology_snapshot: TopologySnapshot | None
    candidate_paths: list | None
    qot_results: list | None
    planning_report: str | None
    error_context: str | None
    usem_score: float | None
    usem_passed: bool | None
    radg_decision: str | None

