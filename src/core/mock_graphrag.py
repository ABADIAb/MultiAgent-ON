"""Mock GraphRAG: Topology graph construction and k-hop neighborhood extraction.

Prevents token saturation by extracting only the relevant subgraph for a
given source-destination pair, instead of dumping the full topology into
the LLM context (see Architecture V5, Phase 4).

The "mock" qualifier reflects that this is a lightweight Python/networkx
implementation rather than a full vector-database GraphRAG system.
"""

from __future__ import annotations

import networkx as nx

from src.core.state import TopologySnapshot


def build_adjacency_graph(topology: TopologySnapshot) -> nx.Graph:
    """Convert a TopologySnapshot into a networkx undirected graph.

    Each graph node stores the NE name as an attribute.
    Each graph edge stores all fiber link attributes (length_km,
    num_amplifiers, active_channels, link_id) for downstream use.

    Args:
        topology: The network topology snapshot from the testbed client.

    Returns:
        An undirected networkx.Graph with node and edge attributes.
    """
    graph: nx.Graph = nx.Graph()

    # Add nodes with name attribute for human-readable identification
    for node in topology.nodes:
        graph.add_node(node.node_id, name=node.name)

    # Add undirected edges with all fiber parameters as attributes
    for link in topology.links:
        graph.add_edge(
            link.source_node,
            link.target_node,
            link_id=link.link_id,
            length_km=link.length_km,
            num_amplifiers=link.num_amplifiers,
            active_channels=link.active_channels,
        )

    return graph


def extract_k_hop_neighborhood(
    graph: nx.Graph,
    source_node: str,
    target_node: str,
    k: int = 2,
) -> nx.Graph:
    """Extract a k-hop subgraph centered on source and target nodes.

    The subgraph contains all nodes reachable within k hops from source
    OR within k hops from target. Source and target are always included
    even if k=0. This bounds the topology injected into LLM context.

    Args:
        graph: Full adjacency graph from build_adjacency_graph().
        source_node: Starting node ID of the desired route.
        target_node: Ending node ID of the desired route.
        k: Maximum hop distance from source or target. Default: 2.

    Returns:
        A subgraph (view) containing the relevant neighborhood.
    """
    # Nodes within k hops from source
    source_neighbors = nx.single_source_shortest_path_length(graph, source_node, cutoff=k)
    # Nodes within k hops from target
    target_neighbors = nx.single_source_shortest_path_length(graph, target_node, cutoff=k)

    # Union: nodes relevant to either source or target
    relevant_nodes = set(source_neighbors.keys()) | set(target_neighbors.keys())

    return graph.subgraph(relevant_nodes).copy()


def graph_to_context_string(graph: nx.Graph) -> str:
    """Serialize a graph into a compact string for LLM context injection.

    Produces a human-readable, token-efficient representation of the
    network topology subgraph. Format:
        Nodes: Node-A (n1), Node-B (n2), ...
        Links:
          - Node-A → Node-B | 20.0 km | 1 amp(s) | link_id: l1
          ...

    Args:
        graph: Subgraph to serialize (typically from extract_k_hop_neighborhood).

    Returns:
        A compact multi-line string suitable for LLM context.
    """
    if graph.number_of_nodes() == 0:
        return "Network topology: empty (no nodes or links in scope)."

    # Node summary
    node_parts = []
    for node_id, attrs in graph.nodes(data=True):
        name = attrs.get("name", node_id)
        node_parts.append(f"{name} ({node_id})")
    nodes_str = "Nodes: " + ", ".join(node_parts)

    # Edge/link summary
    link_lines = []
    for u, v, attrs in graph.edges(data=True):
        src_name = graph.nodes[u].get("name", u)
        dst_name = graph.nodes[v].get("name", v)
        length = attrs.get("length_km", "?")
        amps = attrs.get("num_amplifiers", "?")
        link_id = attrs.get("link_id", "?")
        link_lines.append(
            f"  - {src_name} ↔ {dst_name} | {length} km | {amps} amp(s) | link_id: {link_id}"
        )

    links_str = "Links:\n" + "\n".join(link_lines) if link_lines else "Links: none"

    return f"{nodes_str}\n{links_str}"
