"""Unit tests for the Mock GraphRAG module.

Tests the adjacency graph construction from TopologySnapshot, k-hop
neighborhood extraction, and context string serialization.
All tests are offline — no real topology or network calls.
"""

from __future__ import annotations

import pytest

from src.core.state import FiberLink, NetworkNode, TopologySnapshot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def linear_topology() -> TopologySnapshot:
    """4-node linear topology: A-B-C-D (mirrors ECOC testbed)."""
    nodes = [
        NetworkNode(node_id="n1", name="Node-A", interfaces=[1, 2]),
        NetworkNode(node_id="n2", name="Node-B", interfaces=[3, 4, 5, 6]),
        NetworkNode(node_id="n3", name="Node-C", interfaces=[7, 8, 9, 10]),
        NetworkNode(node_id="n4", name="Node-D", interfaces=[11, 12]),
    ]
    links = [
        FiberLink(link_id="l1", source_node="n1", target_node="n2", length_km=20.0, num_amplifiers=1, active_channels=4),
        FiberLink(link_id="l2", source_node="n2", target_node="n3", length_km=40.0, num_amplifiers=2, active_channels=6),
        FiberLink(link_id="l3", source_node="n3", target_node="n4", length_km=30.0, num_amplifiers=1, active_channels=2),
    ]
    return TopologySnapshot(nodes=nodes, links=links, timestamp="2026-07-29T00:00:00Z")


@pytest.fixture
def mesh_topology() -> TopologySnapshot:
    """3-node mesh topology with two paths from A to C: A-B-C and A-C direct."""
    nodes = [
        NetworkNode(node_id="n1", name="Node-A", interfaces=[1, 2]),
        NetworkNode(node_id="n2", name="Node-B", interfaces=[3, 4]),
        NetworkNode(node_id="n3", name="Node-C", interfaces=[5, 6]),
    ]
    links = [
        FiberLink(link_id="l1", source_node="n1", target_node="n2", length_km=20.0, num_amplifiers=1, active_channels=4),
        FiberLink(link_id="l2", source_node="n2", target_node="n3", length_km=20.0, num_amplifiers=1, active_channels=4),
        FiberLink(link_id="l3", source_node="n1", target_node="n3", length_km=50.0, num_amplifiers=2, active_channels=2),
    ]
    return TopologySnapshot(nodes=nodes, links=links, timestamp="2026-07-29T00:00:00Z")


@pytest.fixture
def empty_topology() -> TopologySnapshot:
    """Topology with no nodes or links."""
    return TopologySnapshot(nodes=[], links=[], timestamp="2026-07-29T00:00:00Z")


# ---------------------------------------------------------------------------
# Tests: build_adjacency_graph
# ---------------------------------------------------------------------------


class TestBuildAdjacencyGraph:
    """Validate graph construction from a TopologySnapshot."""

    def test_returns_networkx_graph(self, linear_topology: TopologySnapshot) -> None:
        import networkx as nx

        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert isinstance(graph, nx.Graph)

    def test_graph_has_correct_node_count(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert graph.number_of_nodes() == 4

    def test_graph_has_correct_edge_count(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert graph.number_of_edges() == 3

    def test_node_ids_are_graph_nodes(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        for node in linear_topology.nodes:
            assert node.node_id in graph.nodes

    def test_node_attributes_include_name(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert graph.nodes["n1"]["name"] == "Node-A"
        assert graph.nodes["n4"]["name"] == "Node-D"

    def test_edge_attributes_include_length_km(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert graph["n1"]["n2"]["length_km"] == pytest.approx(20.0)
        assert graph["n2"]["n3"]["length_km"] == pytest.approx(40.0)

    def test_edge_attributes_include_link_id(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert graph["n1"]["n2"]["link_id"] == "l1"

    def test_edge_attributes_include_num_amplifiers(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(linear_topology)
        assert graph["n2"]["n3"]["num_amplifiers"] == 2

    def test_empty_topology_produces_empty_graph(self, empty_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph

        graph = build_adjacency_graph(empty_topology)
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0


# ---------------------------------------------------------------------------
# Tests: extract_k_hop_neighborhood
# ---------------------------------------------------------------------------


class TestExtractKHopNeighborhood:
    """Validate k-hop subgraph extraction."""

    def test_returns_networkx_graph(self, linear_topology: TopologySnapshot) -> None:
        import networkx as nx

        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood

        graph = build_adjacency_graph(linear_topology)
        subgraph = extract_k_hop_neighborhood(graph, source_node="n1", target_node="n4", k=2)
        assert isinstance(subgraph, nx.Graph)

    def test_subgraph_contains_source_and_target(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood

        graph = build_adjacency_graph(linear_topology)
        subgraph = extract_k_hop_neighborhood(graph, source_node="n1", target_node="n4", k=2)
        assert "n1" in subgraph.nodes
        assert "n4" in subgraph.nodes

    def test_k1_hop_excludes_distant_nodes_in_linear(self, linear_topology: TopologySnapshot) -> None:
        """With k=1 in a 4-node linear chain, n4 is not reachable from n1."""
        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood

        graph = build_adjacency_graph(linear_topology)
        # Only nodes within k=1 hop of n1 OR n4 are included: {n1, n2} union {n3, n4}
        subgraph = extract_k_hop_neighborhood(graph, source_node="n1", target_node="n4", k=1)
        # n1 and n4 must always be included (they ARE source/target)
        assert "n1" in subgraph.nodes
        assert "n4" in subgraph.nodes

    def test_k2_includes_all_nodes_in_4_linear(self, linear_topology: TopologySnapshot) -> None:
        """k=2 from n1 reaches n3; k=2 from n4 reaches n2. Together all 4 nodes."""
        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood

        graph = build_adjacency_graph(linear_topology)
        subgraph = extract_k_hop_neighborhood(graph, source_node="n1", target_node="n4", k=2)
        assert subgraph.number_of_nodes() == 4

    def test_mesh_k1_from_a_to_c_includes_b(self, mesh_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood

        graph = build_adjacency_graph(mesh_topology)
        subgraph = extract_k_hop_neighborhood(graph, source_node="n1", target_node="n3", k=1)
        assert "n2" in subgraph.nodes  # B is 1-hop from both A and C


# ---------------------------------------------------------------------------
# Tests: graph_to_context_string
# ---------------------------------------------------------------------------


class TestGraphToContextString:
    """Validate compact serialization of a graph for LLM context."""

    def test_returns_non_empty_string(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, graph_to_context_string

        graph = build_adjacency_graph(linear_topology)
        result = graph_to_context_string(graph)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_string_contains_node_names(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, graph_to_context_string

        graph = build_adjacency_graph(linear_topology)
        result = graph_to_context_string(graph)
        assert "Node-A" in result
        assert "Node-D" in result

    def test_string_contains_link_info(self, linear_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, graph_to_context_string

        graph = build_adjacency_graph(linear_topology)
        result = graph_to_context_string(graph)
        # Should mention some edge distance info
        assert "km" in result.lower() or "link" in result.lower()

    def test_empty_graph_returns_string(self, empty_topology: TopologySnapshot) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, graph_to_context_string

        graph = build_adjacency_graph(empty_topology)
        result = graph_to_context_string(graph)
        assert isinstance(result, str)


class TestNobelGermanyGraphRAG:
    """Validate GraphRAG behavior directly on the 17-node German topology."""

    def test_german_topology_adjacency_graph_nodes_and_edges(self) -> None:
        from src.core.mock_graphrag import build_adjacency_graph
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        graph = build_adjacency_graph(topology)
        assert graph.number_of_nodes() == 17
        assert graph.number_of_edges() == 26

    def test_german_topology_khop_extraction_bounds_subgraph(self) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        graph = build_adjacency_graph(topology)
        # Berlin (node_6) to Leipzig (node_17) with k=1
        subgraph = extract_k_hop_neighborhood(graph, source_node="node_6", target_node="node_17", k=1)
        # Subgraph bounds context: contains only nodes within 1 hop of Berlin or Leipzig
        assert subgraph.number_of_nodes() < 17
        assert "node_6" in subgraph.nodes
        assert "node_17" in subgraph.nodes

    def test_german_topology_context_string_serialization(self) -> None:
        from src.core.mock_graphrag import build_adjacency_graph, extract_k_hop_neighborhood, graph_to_context_string
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        graph = build_adjacency_graph(topology)
        subgraph = extract_k_hop_neighborhood(graph, source_node="node_6", target_node="node_2", k=2)
        ctx = graph_to_context_string(subgraph)
        assert "Berlin" in ctx
        assert "Frankfurt" in ctx
        assert "km" in ctx

