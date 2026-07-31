---
title: "Feature: Symbolic Solver & Mock GraphRAG"
date: 2026-07-31
tags: [feature, symbolic-solver, graphrag, networkx, pddl, phase4, core]
status: active
---

# Feature: Symbolic Solver & Mock GraphRAG

## 1. Architecture Placement
**Phase 4: Symbolic Solver & Mock GraphRAG** | [[Architecture_v5]]

This is the "System 2" deterministic engine — the LLM is strictly forbidden from touching this phase. Given validated PDDL constraints and a topology snapshot, it extracts 3–5 candidate paths that satisfy all topological constraints, preventing token saturation by working only on a locally compressed k-hop subgraph.

**Key architectural property**: Zero LLM calls. All computation is deterministic and reproducible.

## 2. Associated Files
- **Solver (LangGraph node)**: [src/core/symbolic_solver.py](file:///home/felipeab/MultiAgentON/src/core/symbolic_solver.py) — `symbolic_solver_node(state) -> dict`
- **GraphRAG utilities**: [src/core/mock_graphrag.py](file:///home/felipeab/MultiAgentON/src/core/mock_graphrag.py) — `build_adjacency_graph()`, `extract_k_hop_neighborhood()`, `graph_to_context_string()`
- **State fields read**: `pddl_constraints`, `topology_snapshot`
- **State fields written**: `candidate_paths: list | None`, `pddl_parsed_constraints: dict | None`
- **Tests**: [tests/unit/test_symbolic_solver.py](file:///home/felipeab/MultiAgentON/tests/unit/test_symbolic_solver.py), [tests/unit/test_mock_graphrag.py](file:///home/felipeab/MultiAgentON/tests/unit/test_mock_graphrag.py)

> **Note on placement**: `symbolic_solver.py` lives in `src/core/` (not `src/nodes/`) because it makes zero LLM calls and contains pure algorithm logic. Per the `src/` methodology, the deciding criterion is: "Would this module exist without LangGraph?" → Yes. It also exports a `symbolic_solver_node()` function that `graph.py` wires directly.

## 3. How it Works

### Step 1 — PDDL Constraint Parsing
`_parse_pddl_constraints(pddl_text)` extracts:
- `(source <name>)` → source node name
- `(destination <name>)` → destination node name
- `(avoid-link <id>)` → list of prohibited link IDs
- `(max-hops <n>)` → maximum hop count constraint

### Step 2 — Mock GraphRAG (Context Bounding)
`build_adjacency_graph(topology)` converts the `TopologySnapshot` into a `networkx.Graph` with node names and edge attributes (link_id, length_km, num_amplifiers, active_channels).

`extract_k_hop_neighborhood(graph, source_id, dest_id, k=2)` extracts the union of k-hop neighborhoods around source and destination, bounding the search space and preventing the full topology from being injected into LLM context.

### Step 3 — Yen's K-Shortest Paths
`nx.shortest_simple_paths(subgraph, source_id, dest_id, weight="length_km")` enumerates paths by ascending total fiber length. Up to `_K_PATHS=5` candidate paths are returned.

### Step 4 — PDDL Constraint Filtering
Each candidate path is checked against:
- **max-hops**: path hop count ≤ constraint
- **avoid-link**: no path edge matches any prohibited link ID

Only paths passing all constraints are added to `candidate_paths`.

## 4. Output Format
Each entry in `candidate_paths` is a dict:
```python
{
    "nodes": ["Milano-A", "Milano-B", "Milano-C"],  # human-readable names
    "links": ["link_ab", "link_bc"],                # link IDs traversed
    "total_length_km": 60.0,                        # total fiber length
    "hops": 2                                       # hop count
}
```

## 5. How to Test
```bash
uv run pytest tests/unit/test_symbolic_solver.py tests/unit/test_mock_graphrag.py -v
```

## 6. Cross-References
- [[Architecture_v5]] — Phase 4 description
- [[features/pddl_parser]] — Produces `pddl_constraints` consumed here
- [[features/qot_tool]] — Phase 5 will validate the `candidate_paths` produced here
- [[features/testbed_client]] — Produces `topology_snapshot` consumed here
