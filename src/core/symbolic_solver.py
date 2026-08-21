"""Symbolic Solver node for the V5 Neurosymbolic Intent Pipeline.

Implements deterministic constraint-based path finding using:
- Mock GraphRAG for k-hop neighborhood extraction (prevents token saturation)
- Yen's K-Shortest Paths algorithm for candidate path enumeration
- PDDL constraint enforcement (avoid-links, max-hops)

No LLM calls — this is the purely symbolic half of the neurosymbolic
architecture (Architecture V5, Phase 4). The LLM is strictly forbidden
from deciding routes; this module does it deterministically.
"""

from __future__ import annotations

import re

import networkx as nx
from langchain_core.messages import AIMessage

from src.core.mock_graphrag import (
    build_adjacency_graph,
    extract_k_hop_neighborhood,
)
from src.core.state import AgentState, TopologySnapshot


# ---------------------------------------------------------------------------
# PDDL constraint parsing
# ---------------------------------------------------------------------------


def _parse_pddl_constraints(pddl_text: str) -> dict:
    """Extract routing constraints from a PDDL problem string.

    Parses the simplified optical network PDDL subset used by this system:
      - Combined route goals: (route <src> <dst>), (routed <src> <dst>), (path <src> <dst>)
      - Individual predicates: (source <node>), (destination <node>), (target <node>), (sink <node>)
      - (avoid-link <link-id>) → added to avoid_links list
      - (max-hops <n>) → max_hops integer
      - (min-gsnr <value>) → min_gsnr float

    Args:
        pddl_text: The raw PDDL problem string from AgentState.

    Returns:
        Dict with keys: source (str), destination (str),
        avoid_links (list[str]), max_hops (int | None), min_gsnr (float | None).
    """
    constraints: dict = {
        "source": None,
        "destination": None,
        "avoid_links": [],
        "max_hops": None,
        "min_gsnr": None,
    }

    if not pddl_text:
        return constraints

    # 1. Parse combined route predicates in goal, e.g. (route Munich Cologne), (routed src dst), (path src dst)
    route_match = re.search(
        r"\((?:route|routed|path|route-traffic|service|connect)\s+([^\s)]+)\s+([^\s)]+)\)",
        pddl_text,
        re.IGNORECASE,
    )
    if route_match:
        constraints["source"] = route_match.group(1).strip()
        constraints["destination"] = route_match.group(2).strip()

    # 2. Parse individual source predicates: (source <name>) or (src <name>)
    if not constraints["source"]:
        source_match = re.search(
            r"\((?:source|src)\s+([^\s)]+)\)", pddl_text, re.IGNORECASE
        )
        if source_match:
            constraints["source"] = source_match.group(1).strip()

    # 3. Parse individual destination predicates: (destination <name>), (target <name>), (sink <name>), (dst <name>)
    if not constraints["destination"]:
        dest_match = re.search(
            r"\((?:destination|target|sink|dst)\s+([^\s)]+)\)",
            pddl_text,
            re.IGNORECASE,
        )
        if dest_match:
            constraints["destination"] = dest_match.group(1).strip()

    # 4. Parse (avoid-link <link-id>) or (avoid-link <src> <dst>) — multiple occurrences allowed
    avoid_matches = re.findall(
        r"\(avoid-link\s+([^\s)]+(?:\s+[^\s)]+)?)\)", pddl_text, re.IGNORECASE
    )
    constraints["avoid_links"] = [m.strip().strip("'\"") for m in avoid_matches]

    # 5. Parse (max-hops <n>)
    hops_match = re.search(
        r"\((?:max-hops|max_hops|hops)\s+(\d+)\)", pddl_text, re.IGNORECASE
    )
    if hops_match:
        constraints["max_hops"] = int(hops_match.group(1))

    # 6. Parse (min-gsnr <value>) / (min-snr <value>) / (target-snr <value>)
    snr_match = re.search(
        r"\((?:min-gsnr|min-snr|target-snr|min_gsnr|target_snr)\s+([\d.]+)\)",
        pddl_text,
        re.IGNORECASE,
    )
    if snr_match:
        constraints["min_gsnr"] = float(snr_match.group(1))

    return constraints


# ---------------------------------------------------------------------------
# Constraint filtering
# ---------------------------------------------------------------------------


def _resolve_node_id(graph: nx.Graph, name: str | None) -> str | None:
    """Find a node ID by its 'name' attribute or node_id in the graph (case-insensitive).

    Args:
        graph: Adjacency graph with 'name' node attributes.
        name: Human-readable node name (e.g. 'Munich') or node ID (e.g. 'node_7').

    Returns:
        The node ID string, or None if not found.
    """
    if not name:
        return None

    cleaned = name.strip().strip("'\"()")

    # 1. Exact node_id match
    if cleaned in graph.nodes:
        return cleaned

    # 2. Case-insensitive node_id match
    for node_id in graph.nodes:
        if str(node_id).lower() == cleaned.lower():
            return node_id

    # 3. Exact name attribute match
    for node_id, attrs in graph.nodes(data=True):
        if attrs.get("name") == cleaned:
            return node_id

    # 4. Case-insensitive name attribute match
    for node_id, attrs in graph.nodes(data=True):
        node_name = attrs.get("name", "")
        if str(node_name).lower() == cleaned.lower():
            return node_id

    return None


def _path_uses_avoided_links(
    graph: nx.Graph,
    path_nodes: list[str],
    avoid_links: list[str],
) -> bool:
    """Check whether a path traverses any of the avoided links.

    Args:
        graph: The adjacency graph (with link_id edge attributes).
        path_nodes: Ordered list of node IDs in the path.
        avoid_links: Link IDs or node-pair strings that must not be used.

    Returns:
        True if the path uses at least one avoided link.
    """
    if not avoid_links:
        return False

    avoid_set = {a.strip("'\"").lower() for a in avoid_links}

    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        edge_data = graph.get_edge_data(u, v) or {}
        link_id = str(edge_data.get("link_id", "")).lower()
        u_name = str(graph.nodes[u].get("name", u)).lower()
        v_name = str(graph.nodes[v].get("name", v)).lower()

        # Check direct link ID match
        if link_id in avoid_set:
            return True

        # Check node pair patterns (e.g. "Munich Ulm" or "Munich-Ulm")
        for avoid_entry in avoid_set:
            tokens = [t.strip("'\"") for t in re.split(r"[\s\-_]+", avoid_entry) if t.strip("'\"")]
            if len(tokens) == 2:
                t1, t2 = tokens[0], tokens[1]
                if (u_name == t1 and v_name == t2) or (u_name == t2 and v_name == t1):
                    return True
                if (u.lower() == t1 and v.lower() == t2) or (u.lower() == t2 and v.lower() == t1):
                    return True

    return False


def _build_path_dict(graph: nx.Graph, path_nodes: list[str]) -> dict:
    """Construct a structured path dict from an ordered list of node IDs.

    Includes all physics data needed for QoT validation: link identifiers,
    fiber geometry, and EDFA amplifier configurations.

    Args:
        graph: The adjacency graph.
        path_nodes: Ordered list of node IDs.

    Returns:
        Dict with: nodes (list of names), links (list of link_ids),
        total_length_km (float), hops (int), link_physics (list of dicts).
        Each entry in link_physics has: link_id, length_km, port_loss_dB,
        amplifiers (list of dicts matching models.Amplifier schema).
    """
    node_names = [graph.nodes[n].get("name", n) for n in path_nodes]
    link_ids = []
    total_length = 0.0
    link_physics: list[dict] = []

    for u, v in zip(path_nodes[:-1], path_nodes[1:]):
        edge_data = graph.get_edge_data(u, v) or {}
        link_id = edge_data.get("link_id", f"{u}-{v}")
        length = edge_data.get("length_km", 0.0)
        link_ids.append(link_id)
        total_length += length
        link_physics.append({
            "link_id": link_id,
            "length_km": length,
            "port_loss_dB": edge_data.get("port_loss_dB", 0.0),
            "amplifiers": edge_data.get("amplifiers", []),
        })

    return {
        "nodes": node_names,
        "links": link_ids,
        "total_length_km": total_length,
        "hops": len(path_nodes) - 1,
        "link_physics": link_physics,
    }


# ---------------------------------------------------------------------------
# LangGraph node
# ---------------------------------------------------------------------------

_K_PATHS = 5  # Maximum candidate paths (Yen's K-Shortest Paths)
_K_HOP = 2    # Neighborhood radius for Mock GraphRAG


def symbolic_solver_node(state: AgentState) -> dict:
    """Deterministic path-finding node for the V5 pipeline.

    Reads PDDL constraints and topology from state, builds a networkx
    graph, extracts a k-hop neighborhood via Mock GraphRAG, then runs
    Yen's K-Shortest Paths with PDDL constraint filtering.

    Args:
        state: Current AgentState with pddl_constraints and topology_snapshot.

    Returns:
        Partial state update with candidate_paths and a summary message.
    """
    pddl_text = state.get("pddl_constraints") or ""
    # Reuses subtopology_snapshot extracted by Phase 1 (Optical RAG) if available,
    # avoiding redundant graph extraction. Falls back to full topology_snapshot.
    topology: TopologySnapshot | None = (
        state.get("subtopology_snapshot") or state.get("topology_snapshot")
    )

    # Parse constraints from PDDL
    constraints = _parse_pddl_constraints(pddl_text)
    source_name = constraints["source"]
    dest_name = constraints["destination"]
    avoid_links: list[str] = constraints["avoid_links"]
    max_hops: int | None = constraints["max_hops"]

    # Fallback to enriched_intent if PDDL did not contain source/target
    if source_name is None or dest_name is None:
        enriched = state.get("enriched_intent") or ""
        if source_name is None:
            src_m = re.search(r"Source:\s*([^\s|]+)", enriched, re.IGNORECASE)
            if src_m:
                source_name = src_m.group(1).strip()
                constraints["source"] = source_name
        if dest_name is None:
            dst_m = re.search(r"Target:\s*([^\s|]+)", enriched, re.IGNORECASE)
            if dst_m:
                dest_name = dst_m.group(1).strip()
                constraints["destination"] = dest_name

    # Guard: no topology available
    if topology is None or not topology.nodes:
        return {
            "candidate_paths": [],
            "pddl_parsed_constraints": constraints,
            "messages": [
                AIMessage(
                    content="Symbolic solver: no topology available in state.",
                    name="symbolic_solver",
                )
            ],
        }

    # Guard: endpoints completely missing (no silent arbitrary default nodes)
    if source_name is None or dest_name is None:
        return {
            "candidate_paths": [],
            "pddl_parsed_constraints": constraints,
            "messages": [
                AIMessage(
                    content="Symbolic solver: source or destination not specified in PDDL constraints or intent.",
                    name="symbolic_solver",
                )
            ],
        }

    # Build graph and extract k-hop neighborhood
    full_graph = build_adjacency_graph(topology)

    # Resolve node names to IDs
    source_id = _resolve_node_id(full_graph, source_name)
    dest_id = _resolve_node_id(full_graph, dest_name)

    # Guard: disconnected or missing nodes
    if source_id is None or dest_id is None:
        missing = []
        if source_id is None:
            missing.append(f"source '{source_name}'")
        if dest_id is None:
            missing.append(f"destination '{dest_name}'")
        return {
            "candidate_paths": [],
            "pddl_parsed_constraints": constraints,
            "messages": [
                AIMessage(
                    content=f"Symbolic solver: {' and '.join(missing)} not found in topology.",
                    name="symbolic_solver",
                )
            ],
        }

    if source_id == dest_id:
        return {
            "candidate_paths": [],
            "pddl_parsed_constraints": constraints,
            "messages": [
                AIMessage(
                    content=f"Symbolic solver: source and destination are the same node ('{source_name}').",
                    name="symbolic_solver",
                )
            ],
        }

    # Extract k-hop neighborhood (Mock GraphRAG)
    subgraph = extract_k_hop_neighborhood(full_graph, source_id, dest_id, k=_K_HOP)

    # Guard: source and dest not connected in subgraph
    if not nx.has_path(subgraph, source_id, dest_id):
        # Fall back to full graph if k-hop cutoff disconnected a valid route
        if nx.has_path(full_graph, source_id, dest_id):
            subgraph = full_graph
        else:
            return {
                "candidate_paths": [],
                "pddl_parsed_constraints": constraints,
                "messages": [
                    AIMessage(
                        content=f"Symbolic solver: no physical path found between '{source_name}' and '{dest_name}'.",
                        name="symbolic_solver",
                    )
                ],
            }

    # Run Yen's K-Shortest Paths
    try:
        raw_paths = list(
            nx.shortest_simple_paths(subgraph, source_id, dest_id, weight="length_km")
        )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        raw_paths = []

    # Apply PDDL constraint filters
    candidate_paths = []
    for path_nodes_raw in raw_paths:
        if len(candidate_paths) >= _K_PATHS:
            break

        path_nodes: list[str] = [str(n) for n in path_nodes_raw]
        hops = len(path_nodes) - 1

        # Enforce max-hops constraint
        if max_hops is not None and hops > max_hops:
            continue

        # Enforce avoid-link constraint
        if _path_uses_avoided_links(subgraph, path_nodes, avoid_links):
            continue

        candidate_paths.append(_build_path_dict(subgraph, path_nodes))

    summary = (
        f"Symbolic solver found {len(candidate_paths)} candidate path(s) "
        f"from '{source_name}' to '{dest_name}'."
    )

    return {
        "candidate_paths": candidate_paths,
        "pddl_parsed_constraints": constraints,
        "messages": [AIMessage(content=summary, name="symbolic_solver")],
    }
