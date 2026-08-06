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

    def test_topology_has_three_nodes(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert len(topology.nodes) == 3

    def test_topology_has_two_links(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert len(topology.links) == 2

    def test_node_names_match_ecoc_testbed(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        names = [n.name for n in topology.nodes]
        assert names == ["Milano-A", "Milano-B", "Milano-C"]

    def test_links_form_linear_chain(self) -> None:
        """Verify links connect nodes sequentially: A-B, B-C."""
        client = MockTestbedClient()
        topology = client.get_topology()
        connections = [
            (link.source_node, link.target_node) for link in topology.links
        ]
        assert ("node_1", "node_2") in connections
        assert ("node_2", "node_3") in connections

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


class TestMockTopologyAmplifierPhysics:
    """Verify that MockTestbedClient supplies realistic EDFA physics on each link."""

    def test_link_ab_has_two_amplifiers(self) -> None:
        topology = MockTestbedClient().get_topology()
        link_ab = next(lk for lk in topology.links if lk.link_id == "link_ab")
        assert len(link_ab.amplifiers) == 2

    def test_link_bc_has_three_amplifiers(self) -> None:
        topology = MockTestbedClient().get_topology()
        link_bc = next(lk for lk in topology.links if lk.link_id == "link_bc")
        assert len(link_bc.amplifiers) == 3

    def test_link_ab_first_amp_is_booster(self) -> None:
        topology = MockTestbedClient().get_topology()
        link_ab = next(lk for lk in topology.links if lk.link_id == "link_ab")
        assert link_ab.amplifiers[0]["amp_type"] == "booster"

    def test_link_ab_last_amp_is_preamp(self) -> None:
        topology = MockTestbedClient().get_topology()
        link_ab = next(lk for lk in topology.links if lk.link_id == "link_ab")
        assert link_ab.amplifiers[-1]["amp_type"] == "preamp"

    def test_link_bc_has_ila_at_midspan(self) -> None:
        topology = MockTestbedClient().get_topology()
        link_bc = next(lk for lk in topology.links if lk.link_id == "link_bc")
        amp_types = [a["amp_type"] for a in link_bc.amplifiers]
        assert "ila" in amp_types

    def test_all_links_have_positive_port_loss(self) -> None:
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            assert link.port_loss_dB >= 0.0

    def test_amplifier_gains_are_positive(self) -> None:
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            for amp in link.amplifiers:
                assert amp["gain_dB"] > 0

    def test_preamp_position_equals_link_length(self) -> None:
        """Preamp should sit at the end of the span (at link length km)."""
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            preamps = [a for a in link.amplifiers if a["amp_type"] == "preamp"]
            for preamp in preamps:
                assert preamp["position_km"] == link.length_km

