"""Core state schema for the MultiAgentON LangGraph pipeline.

Defines the AgentState TypedDict used as the shared state across all nodes
in the StateGraph, plus Pydantic models for structured domain data.
"""

from __future__ import annotations

import operator
from enum import Enum
from typing import Annotated, TypedDict

from pydantic import BaseModel, Field, AliasChoices


# ---------------------------------------------------------------------------
# Domain Models (Pydantic)
# ---------------------------------------------------------------------------


class TaskType(str, Enum):
    """Types of tasks the supervisor can delegate."""

    TOPOLOGY_QUERY = "topology_query"
    ROUTE_REQUEST = "route_request"
    LIGHTPATH_PROVISION = "lightpath_provision"
    MEASUREMENT = "measurement"
    UNKNOWN = "unknown"


class TaskItem(BaseModel):
    """A single task in the supervisor's delegation plan."""

    task_type: TaskType = Field(
        description="The type of task to execute. Must be one of the TaskType enum values.",
        validation_alias=AliasChoices("task_type", "type"),
    )
    description: str = Field(
        default="",
        description="Detailed description of what this task step involves.",
    )
    source_node: str | None = Field(
        default=None,
        description="Optional source node name if applicable.",
    )
    sink_node: str | None = Field(
        default=None,
        description="Optional sink/target node name if applicable.",
    )


class TaskPlan(BaseModel):
    """Structured output from the Supervisor's intent parsing."""

    intent_summary: str = Field(
        description="One-sentence summary of what the operator wants."
    )
    tasks: list[TaskItem] = Field(
        default_factory=list,
        description="Ordered list of tasks to execute.",
    )


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
# LangGraph State
# ---------------------------------------------------------------------------


class AgentState(TypedDict):
    """Shared state for the MultiAgentON LangGraph pipeline.

    Fields:
        messages: Append-only message list (uses add reducer).
        task_plan: Parsed intent from the Supervisor.
        topology_snapshot: Current testbed topology from the Topology Agent.
        current_agent: Name of the currently active agent.
        error_context: Error details for retry loops.
    """

    messages: Annotated[list, operator.add]
    task_plan: TaskPlan | None
    topology_snapshot: TopologySnapshot | None
    current_agent: str | None
    error_context: str | None
