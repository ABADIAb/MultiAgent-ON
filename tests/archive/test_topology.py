"""Tests for the Topology Agent node and fetch_topology tool."""

import pytest

from src.core.state import AgentState, TopologySnapshot
from src.agents.topology import topology_node
from src.services.testbed_client import MockTestbedClient
from src.tools.fetch_topology import (
    fetch_topology,
    get_testbed_client,
    set_testbed_client,
)


@pytest.fixture(autouse=True)
def _setup_mock_client() -> None:
    """Ensure the mock client is configured before each test."""
    set_testbed_client(MockTestbedClient())


# ---------------------------------------------------------------------------
# fetch_topology tool tests
# ---------------------------------------------------------------------------


class TestFetchTopologyTool:
    def test_returns_dict(self) -> None:
        result = fetch_topology.invoke({})
        assert isinstance(result, dict)

    def test_result_has_nodes_key(self) -> None:
        result = fetch_topology.invoke({})
        assert "nodes" in result

    def test_result_has_links_key(self) -> None:
        result = fetch_topology.invoke({})
        assert "links" in result

    def test_result_deserializes_to_snapshot(self) -> None:
        result = fetch_topology.invoke({})
        snapshot = TopologySnapshot.model_validate(result)
        assert len(snapshot.nodes) == 4

    def test_raises_without_client(self) -> None:
        set_testbed_client(None)  # type: ignore[arg-type]
        # Reset to trigger the error
        from src.tools import fetch_topology as ft_mod

        ft_mod._client = None
        with pytest.raises(RuntimeError, match="TestbedClient not configured"):
            get_testbed_client()


# ---------------------------------------------------------------------------
# topology_node tests
# ---------------------------------------------------------------------------


class TestTopologyNode:
    def test_returns_topology_snapshot(self) -> None:
        state: AgentState = {
            "messages": [],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": "topology_agent",
            "error_context": None,
        }
        result = topology_node(state)
        assert result["topology_snapshot"] is not None
        assert isinstance(result["topology_snapshot"], TopologySnapshot)

    def test_snapshot_has_four_nodes(self) -> None:
        state: AgentState = {
            "messages": [],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": "topology_agent",
            "error_context": None,
        }
        result = topology_node(state)
        assert len(result["topology_snapshot"].nodes) == 4

    def test_returns_summary_message(self) -> None:
        state: AgentState = {
            "messages": [],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": "topology_agent",
            "error_context": None,
        }
        result = topology_node(state)
        messages = result["messages"]
        assert len(messages) == 1
        assert "Topology fetched successfully" in messages[0].content

    def test_summary_contains_node_names(self) -> None:
        state: AgentState = {
            "messages": [],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": "topology_agent",
            "error_context": None,
        }
        result = topology_node(state)
        content = result["messages"][0].content
        assert "Milano-A" in content
        assert "Milano-D" in content

    def test_routes_back_to_supervisor(self) -> None:
        state: AgentState = {
            "messages": [],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": "topology_agent",
            "error_context": None,
        }
        result = topology_node(state)
        assert result["current_agent"] == "supervisor"
