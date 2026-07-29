"""Integration test for the ONC REST API (SM Optics Optical Network Controller).

Validates live connectivity to the testbed at 10.79.26.48 via the ONC NBI.
Requires VPN access and network reachability to the controller.

Run with:
    uv run pytest tests/integration/test_onc_api.py -v -s -m integration

The -s flag shows diagnostic print output (NE names, connection count)
for exploratory validation on first run.
"""

from __future__ import annotations

import pytest

ONC_BASE_URL = "https://10.79.26.48:8443"
ONC_USERNAME = "admin"
ONC_PASSWORD = "admin"
NE_FILTER = "Qiaolun"


@pytest.mark.integration
class TestONCAPIConnectivity:
    """Live connectivity tests against the SM Optics ONC controller.

    All tests require VPN access to 10.79.26.48.
    They are excluded from the default test run (addopts = -m 'not integration').
    """

    @pytest.fixture(autouse=True, scope="class")
    def client(self):
        """Provide a shared RESTConfTestbedClient for all tests in this class.

        Scope is 'class' so CAS authentication happens once and the session
        cookie is shared across all test methods.
        """
        import warnings

        from src.services.testbed_client import RESTConfTestbedClient

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            c = RESTConfTestbedClient(
                base_url=ONC_BASE_URL,
                username=ONC_USERNAME,
                password=ONC_PASSWORD,
                ne_filter=NE_FILTER,
            )
        yield c
        c.close()

    def test_onc_health_check(self, client) -> None:
        """Verify the ONC controller responds to GET /ne."""
        result = client.health_check()
        print(f"\n[ONC] Health check result: {result}")
        assert result is True, (
            f"ONC health check failed. Is VPN connected to {ONC_BASE_URL}?"
        )

    def test_onc_list_network_elements(self, client) -> None:
        """Fetch NEs and verify at least one Qiaolun NE is returned."""
        nes = client.get_network_elements()
        print(f"\n[ONC] Network Elements found ({len(nes)} total):")
        for ne in nes:
            print(f"  - {ne.get('name')} | type={ne.get('neType')} | reach={ne.get('reachability')}")
        assert len(nes) >= 1, "Expected at least 1 Qiaolun NE from the ONC controller."

    def test_onc_ne_names_contain_qiaolun(self, client) -> None:
        """All returned NEs must have 'Qiaolun' in their name (filter working)."""
        nes = client.get_network_elements()
        for ne in nes:
            assert NE_FILTER in ne.get("name", ""), (
                f"NE '{ne.get('name')}' does not contain filter keyword '{NE_FILTER}'. "
                "Filtering may be broken."
            )

    def test_onc_qiaolun_topology_has_three_nodes(self, client) -> None:
        """The Qiaolun topology should have exactly 3 NEs (per professor's confirmation)."""
        nes = client.get_network_elements()
        print(f"\n[ONC] Qiaolun NE count: {len(nes)}")
        assert len(nes) == 3, (
            f"Expected 3 Qiaolun NEs, found {len(nes)}. "
            "If the topology changed, update this assertion."
        )

    def test_onc_list_connections(self, client) -> None:
        """Fetch infrastructure connections and verify the endpoint responds without error.

        NOTE: The Qiaolun testbed may have 0 provisioned connections of type
        'infrastructure-eth'. The ONC returns 400 in that case, which the
        client maps to []. This test validates the client handles it gracefully.
        """
        connections = client.get_connections("infrastructure-eth")
        print(f"\n[ONC] Connections found (infrastructure-eth): {len(connections)}")
        for conn in connections:
            name = conn.get("name", "?")
            state = conn.get("configurationState", "?")
            print(f"  - {name} | state={state}")
        # Validates the call completes without exception; count may be 0
        assert isinstance(connections, list)

    def test_onc_get_topology_returns_snapshot(self, client) -> None:
        """Verify full topology assembly produces a valid TopologySnapshot.

        NOTE: The Qiaolun testbed currently has 3 NEs but 0 provisioned
        infrastructure-eth connections. The topology snapshot will have 0 links.
        This is a valid observation — the physical DWDM links are not yet
        provisioned in the ONC's connection database.
        """
        from src.core.state import TopologySnapshot

        topology = client.get_topology()
        print(f"\n[ONC] Assembled topology:")
        print(f"  Nodes ({len(topology.nodes)}):")
        for node in topology.nodes:
            print(f"    - {node.name} ({node.node_id})")
        print(f"  Links ({len(topology.links)}):")
        for link in topology.links:
            print(f"    - {link.link_id}: {link.source_node} → {link.target_node} | {link.length_km} km")
        print(f"  Timestamp: {topology.timestamp}")

        assert isinstance(topology, TopologySnapshot)
        assert len(topology.nodes) == 3
        assert topology.timestamp != ""
        # Links may be 0 if no connections are provisioned in the ONC
        assert isinstance(topology.links, list)

    def test_onc_topology_node_names_contain_qiaolun(self, client) -> None:
        """All topology nodes should correspond to Qiaolun NEs."""
        topology = client.get_topology()
        for node in topology.nodes:
            assert NE_FILTER in node.name, (
                f"Node '{node.name}' does not belong to Qiaolun topology."
            )
