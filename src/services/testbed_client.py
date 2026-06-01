"""Testbed client abstraction and mock implementation.

Provides a clean interface for testbed communication that can be swapped
between a mock (for development) and a real RESTConf client (for production).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone

from src.core.state import FiberLink, NetworkNode, TopologySnapshot


class TestbedClient(ABC):
    """Abstract interface for testbed communication."""

    @abstractmethod
    def get_topology(self) -> TopologySnapshot:
        """Fetch the current network topology from the testbed."""
        ...

    @abstractmethod
    def health_check(self) -> bool:
        """Check if the testbed is reachable."""
        ...


class MockTestbedClient(TestbedClient):
    """Mock testbed client returning realistic ECOC 4-node topology.

    Based on the ECOC 2024 paper's testbed at Politecnico di Milano:
    4 nodes in a linear topology with fiber spans and OAs.
    """

    def get_topology(self) -> TopologySnapshot:
        """Return a hardcoded but realistic 4-node linear topology."""
        nodes = [
            NetworkNode(
                node_id="node_1",
                name="Milano-A",
                interfaces=[101, 102],
            ),
            NetworkNode(
                node_id="node_2",
                name="Milano-B",
                interfaces=[201, 202, 203, 204],
            ),
            NetworkNode(
                node_id="node_3",
                name="Milano-C",
                interfaces=[301, 302, 303, 304],
            ),
            NetworkNode(
                node_id="node_4",
                name="Milano-D",
                interfaces=[401, 402],
            ),
        ]

        links = [
            FiberLink(
                link_id="link_ab",
                source_node="node_1",
                target_node="node_2",
                length_km=25.0,
                num_amplifiers=1,
                active_channels=4,
            ),
            FiberLink(
                link_id="link_bc",
                source_node="node_2",
                target_node="node_3",
                length_km=40.0,
                num_amplifiers=2,
                active_channels=6,
            ),
            FiberLink(
                link_id="link_cd",
                source_node="node_3",
                target_node="node_4",
                length_km=30.0,
                num_amplifiers=1,
                active_channels=2,
            ),
        ]

        return TopologySnapshot(
            nodes=nodes,
            links=links,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def health_check(self) -> bool:
        """Mock always returns True."""
        return True
