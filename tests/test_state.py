"""Tests for core state schema and Pydantic domain models."""

import operator

from src.core.state import (
    AgentState,
    FiberLink,
    NetworkNode,
    TaskItem,
    TaskPlan,
    TaskType,
    TopologySnapshot,
)


# ---------------------------------------------------------------------------
# TaskType enum
# ---------------------------------------------------------------------------


class TestTaskType:
    def test_topology_query_value(self) -> None:
        assert TaskType.TOPOLOGY_QUERY == "topology_query"

    def test_all_variants_are_strings(self) -> None:
        for member in TaskType:
            assert isinstance(member.value, str)

    def test_unknown_variant_exists(self) -> None:
        assert TaskType.UNKNOWN == "unknown"


# ---------------------------------------------------------------------------
# TaskItem model
# ---------------------------------------------------------------------------


class TestTaskItem:
    def test_minimal_creation(self) -> None:
        item = TaskItem(task_type=TaskType.TOPOLOGY_QUERY)
        assert item.task_type == TaskType.TOPOLOGY_QUERY
        assert item.description == ""
        assert item.source_node is None
        assert item.sink_node is None

    def test_full_creation(self) -> None:
        item = TaskItem(
            task_type=TaskType.ROUTE_REQUEST,
            description="Find path from A to D",
            source_node="node_a",
            sink_node="node_d",
        )
        assert item.task_type == TaskType.ROUTE_REQUEST
        assert item.source_node == "node_a"
        assert item.sink_node == "node_d"

    def test_serialization_roundtrip(self) -> None:
        item = TaskItem(
            task_type=TaskType.LIGHTPATH_PROVISION,
            description="Provision lightpath",
        )
        data = item.model_dump()
        restored = TaskItem.model_validate(data)
        assert restored == item


# ---------------------------------------------------------------------------
# TaskPlan model
# ---------------------------------------------------------------------------


class TestTaskPlan:
    def test_empty_plan(self) -> None:
        plan = TaskPlan(intent_summary="Check topology")
        assert plan.intent_summary == "Check topology"
        assert plan.tasks == []

    def test_plan_with_tasks(self) -> None:
        plan = TaskPlan(
            intent_summary="Query and provision",
            tasks=[
                TaskItem(task_type=TaskType.TOPOLOGY_QUERY),
                TaskItem(task_type=TaskType.LIGHTPATH_PROVISION),
            ],
        )
        assert len(plan.tasks) == 2
        assert plan.tasks[0].task_type == TaskType.TOPOLOGY_QUERY
        assert plan.tasks[1].task_type == TaskType.LIGHTPATH_PROVISION

    def test_serialization_roundtrip(self) -> None:
        plan = TaskPlan(
            intent_summary="Test",
            tasks=[TaskItem(task_type=TaskType.MEASUREMENT, description="OSNR check")],
        )
        data = plan.model_dump()
        restored = TaskPlan.model_validate(data)
        assert restored == plan


# ---------------------------------------------------------------------------
# TopologySnapshot model
# ---------------------------------------------------------------------------


class TestNetworkNode:
    def test_minimal_creation(self) -> None:
        node = NetworkNode(node_id="n1", name="Milano-A")
        assert node.node_id == "n1"
        assert node.name == "Milano-A"
        assert node.interfaces == []

    def test_with_interfaces(self) -> None:
        node = NetworkNode(node_id="n1", name="Milano-A", interfaces=[101, 102, 103])
        assert len(node.interfaces) == 3


class TestFiberLink:
    def test_creation(self) -> None:
        link = FiberLink(
            link_id="l1",
            source_node="n1",
            target_node="n2",
            length_km=25.0,
            num_amplifiers=2,
            active_channels=4,
        )
        assert link.length_km == 25.0
        assert link.num_amplifiers == 2

    def test_defaults(self) -> None:
        link = FiberLink(
            link_id="l1", source_node="n1", target_node="n2", length_km=10.0
        )
        assert link.num_amplifiers == 0
        assert link.active_channels == 0


class TestTopologySnapshot:
    def test_empty_snapshot(self) -> None:
        snap = TopologySnapshot()
        assert snap.nodes == []
        assert snap.links == []
        assert snap.timestamp == ""

    def test_populated_snapshot(self) -> None:
        snap = TopologySnapshot(
            nodes=[
                NetworkNode(node_id="n1", name="Milano-A"),
                NetworkNode(node_id="n2", name="Milano-B"),
            ],
            links=[
                FiberLink(
                    link_id="l1",
                    source_node="n1",
                    target_node="n2",
                    length_km=25.0,
                )
            ],
            timestamp="2026-06-01T10:00:00Z",
        )
        assert len(snap.nodes) == 2
        assert len(snap.links) == 1

    def test_serialization_roundtrip(self) -> None:
        snap = TopologySnapshot(
            nodes=[NetworkNode(node_id="n1", name="A")],
            links=[
                FiberLink(
                    link_id="l1",
                    source_node="n1",
                    target_node="n2",
                    length_km=5.0,
                )
            ],
        )
        data = snap.model_dump()
        restored = TopologySnapshot.model_validate(data)
        assert restored == snap


# ---------------------------------------------------------------------------
# AgentState TypedDict
# ---------------------------------------------------------------------------


class TestAgentState:
    def test_state_creation(self) -> None:
        state: AgentState = {
            "messages": [],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": None,
            "error_context": None,
        }
        assert state["messages"] == []
        assert state["task_plan"] is None

    def test_state_with_populated_fields(self) -> None:
        plan = TaskPlan(
            intent_summary="Topology query",
            tasks=[TaskItem(task_type=TaskType.TOPOLOGY_QUERY)],
        )
        snap = TopologySnapshot(
            nodes=[NetworkNode(node_id="n1", name="Milano-A")],
        )
        state: AgentState = {
            "messages": [{"role": "user", "content": "Show topology"}],
            "task_plan": plan,
            "topology_snapshot": snap,
            "current_agent": "topology_agent",
            "error_context": None,
        }
        assert state["task_plan"] is not None
        assert state["task_plan"].tasks[0].task_type == TaskType.TOPOLOGY_QUERY
        assert state["topology_snapshot"] is not None
        assert len(state["topology_snapshot"].nodes) == 1

    def test_messages_reducer_annotation(self) -> None:
        """Verify the messages field uses operator.add as reducer."""
        import typing

        hints = typing.get_type_hints(AgentState, include_extras=True)
        assert hasattr(hints["messages"], "__metadata__")
        assert operator.add in hints["messages"].__metadata__
