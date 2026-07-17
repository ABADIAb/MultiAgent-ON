"""Core state schema for the Neurosymbolic Intent Pipeline.

Defines the AgentState TypedDict used as the shared state across all nodes
in the V4 StateGraph, plus Pydantic models for structured domain data.

V4 changes from V3:
  - Removed TaskType, TaskItem, TaskPlan (hub-and-spoke routing)
  - Removed current_agent field
  - Added neurosymbolic pipeline fields: enriched_intent, pddl_constraints,
    pddl_valid, hitl_reconstruction, hitl_approved, candidate_paths,
    qot_results, planning_report
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
    """A fiber link connecting two nodes."""

    link_id: str
    source_node: str
    target_node: str
    length_km: float
    num_amplifiers: int = 0
    active_channels: int = 0


class TopologySnapshot(BaseModel):
    """Structured representation of the testbed topology."""

    nodes: list[NetworkNode] = Field(default_factory=list)
    links: list[FiberLink] = Field(default_factory=list)
    timestamp: str = ""


# ---------------------------------------------------------------------------
# LangGraph State — V4 Neurosymbolic Intent Pipeline
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    """Shared state for the V4 Neurosymbolic Intent Pipeline.

    Fields:
        messages: Append-only message list (uses add reducer).
        enriched_intent: Operator intent after Optical RAG enrichment.
        pddl_constraints: PDDL constraint string from the parser.
        pddl_valid: Whether the PDDL passed CFG validation.
        hitl_reconstruction: Natural language reconstruction of PDDL.
        hitl_approved: Whether the operator approved via Reverse Prompting.
        topology_snapshot: Current testbed topology.
        candidate_paths: 3-5 paths from the Symbolic Solver.
        qot_results: QoT assessment results per candidate path.
        planning_report: Final synthesized planning report.
        error_context: Error details for debugging.
    """

    messages: Annotated[list, operator.add]
    enriched_intent: str | None
    pddl_constraints: str | None
    pddl_valid: bool | None
    hitl_reconstruction: str | None
    hitl_approved: bool | None
    topology_snapshot: TopologySnapshot | None
    candidate_paths: list | None
    qot_results: list | None
    planning_report: str | None
    error_context: str | None
