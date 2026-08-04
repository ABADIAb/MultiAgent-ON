"""Tests for testbed client abstraction and mock implementation."""

from src.core.state import TopologySnapshot
from src.services.testbed_client import MockTestbedClient, TestbedClient


class TestTestbedClientInterface:
    """Verify the MockTestbedClient satisfies the abstract interface."""

    def test_mock_is_testbed_client(self) -> None:
        client = MockTestbedClient()
        assert isinstance(client, TestbedClient)


class TestMockTestbedClient:
    """Verify the mock returns realistic ECOC topology data."""

    def test_get_topology_returns_snapshot(self) -> None:
        client = MockTestbedClient()
        result = client.get_topology()
        assert isinstance(result, TopologySnapshot)

    def test_topology_has_four_nodes(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert len(topology.nodes) == 4

    def test_topology_has_three_links(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert len(topology.links) == 3

    def test_node_names_match_ecoc_testbed(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        names = [n.name for n in topology.nodes]
        assert names == ["Milano-A", "Milano-B", "Milano-C", "Milano-D"]

    def test_links_form_linear_chain(self) -> None:
        """Verify links connect nodes sequentially: A-B, B-C, C-D."""
        client = MockTestbedClient()
        topology = client.get_topology()
        connections = [
            (link.source_node, link.target_node) for link in topology.links
        ]
        assert ("node_1", "node_2") in connections
        assert ("node_2", "node_3") in connections
        assert ("node_3", "node_4") in connections

    def test_fiber_lengths_are_positive(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        for link in topology.links:
            assert link.length_km > 0

    def test_nodes_have_interfaces(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        for node in topology.nodes:
            assert len(node.interfaces) >= 2

    def test_interior_nodes_have_more_interfaces(self) -> None:
        """Interior nodes (B, C) should have more interfaces than edge nodes (A, D)."""
        client = MockTestbedClient()
        topology = client.get_topology()
        edge_interfaces = len(topology.nodes[0].interfaces)
        interior_interfaces = len(topology.nodes[1].interfaces)
        assert interior_interfaces > edge_interfaces

    def test_timestamp_is_populated(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert topology.timestamp != ""

    def test_health_check_returns_true(self) -> None:
        client = MockTestbedClient()
        assert client.health_check() is True

    def test_topology_serialization_roundtrip(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        data = topology.model_dump()
        restored = TopologySnapshot.model_validate(data)
        assert restored.nodes == topology.nodes
        assert restored.links == topology.links
