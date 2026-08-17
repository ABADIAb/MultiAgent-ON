"""Tests for testbed client abstraction and mock implementation."""

from src.core.state import TopologySnapshot
from src.services.testbed_client import MockTestbedClient, TestbedClient


class TestTestbedClientInterface:
    """Verify the MockTestbedClient satisfies the abstract interface."""

    def test_mock_is_testbed_client(self) -> None:
        client = MockTestbedClient()
        assert isinstance(client, TestbedClient)


class TestMockTestbedClient:
    """Verify the mock returns realistic Nobel-Germany 17-node topology data."""

    def test_get_topology_returns_snapshot(self) -> None:
        client = MockTestbedClient()
        result = client.get_topology()
        assert isinstance(result, TopologySnapshot)

    def test_topology_has_seventeen_nodes(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert len(topology.nodes) == 17

    def test_topology_has_twenty_six_links(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        assert len(topology.links) == 26

    def test_node_names_match_nobel_germany_cities(self) -> None:
        client = MockTestbedClient()
        topology = client.get_topology()
        names = [n.name for n in topology.nodes]
        expected_names = [
            "Hannover", "Frankfurt", "Hamburg", "Norden", "Bremen", "Berlin",
            "Munich", "Ulm", "Nuremberg", "Stuttgart", "Karlsruhe", "Mannheim",
            "Essen", "Dortmund", "Dusseldorf", "Cologne", "Leipzig",
        ]
        assert names == expected_names

    def test_key_connections_exist(self) -> None:
        """Verify standard Nobel-Germany links exist in the topology."""
        client = MockTestbedClient()
        topology = client.get_topology()
        connections = {
            (link.source_node, link.target_node) for link in topology.links
        }
        # e.g., Hannover (node_1) <-> Berlin (node_6), Frankfurt (node_2) <-> Cologne (node_16)
        assert ("node_1", "node_6") in connections
        assert ("node_2", "node_16") in connections
        assert ("node_7", "node_9") in connections  # Munich <-> Nuremberg

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

    def test_high_degree_nodes_have_more_interfaces(self) -> None:
        """High-degree hub nodes (Hannover, Frankfurt) have more interfaces than degree-2 nodes."""
        client = MockTestbedClient()
        topology = client.get_topology()
        hannover = next(n for n in topology.nodes if n.name == "Hannover")
        norden = next(n for n in topology.nodes if n.name == "Norden")
        assert len(hannover.interfaces) > len(norden.interfaces)

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

    def test_short_link_has_booster_and_preamp(self) -> None:
        """Short links (<= 55km, e.g. Essen-Dortmund 44.4km) should have 2 amplifiers."""
        topology = MockTestbedClient().get_topology()
        link = next(lk for lk in topology.links if lk.link_id == "link_essen_dortmund")
        assert len(link.amplifiers) == 2
        assert link.amplifiers[0]["amp_type"] == "booster"
        assert link.amplifiers[-1]["amp_type"] == "preamp"

    def test_long_link_has_ilas(self) -> None:
        """Long links (> 55km, e.g. Frankfurt-Leipzig 381.9km) should have ILAs."""
        topology = MockTestbedClient().get_topology()
        link = next(lk for lk in topology.links if lk.link_id == "link_frankfurt_leipzig")
        assert len(link.amplifiers) >= 3
        amp_types = [a["amp_type"] for a in link.amplifiers]
        assert "booster" in amp_types
        assert "ila" in amp_types
        assert "preamp" in amp_types

    def test_first_amp_is_always_booster(self) -> None:
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            assert link.amplifiers[0]["amp_type"] == "booster"
            assert link.amplifiers[0]["position_km"] == 0.0

    def test_last_amp_is_always_preamp(self) -> None:
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            assert link.amplifiers[-1]["amp_type"] == "preamp"
            assert link.amplifiers[-1]["position_km"] == round(link.length_km, 1)

    def test_all_links_have_positive_port_loss(self) -> None:
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            assert link.port_loss_dB >= 0.0

    def test_amplifier_gains_are_positive(self) -> None:
        topology = MockTestbedClient().get_topology()
        for link in topology.links:
            for amp in link.amplifiers:
                assert amp["gain_dB"] > 0

