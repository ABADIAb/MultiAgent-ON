"""Symbolic Solver node for the Neurosymbolic Intent Pipeline.

Sprint 2 (Exp 2.3) will implement:
- Mock GraphRAG k-hop neighborhood extraction
- Dijkstra/Yen's K-Shortest Paths with PDDL constraint validation
- 3-5 candidate path extraction

Current: Pass-through placeholder that generates dummy candidate paths.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from src.core.state import AgentState


def symbolic_solver_node(state: AgentState) -> dict:
    """Extract candidate paths using symbolic solving.

    Placeholder: returns a single dummy path through the linear topology.
    Sprint 2 will implement real GraphRAG + constraint-based path finding.

    Returns:
        Partial state update with candidate_paths.
    """
    # Placeholder: dummy linear path
    candidate_paths = [
        {"path": ["Milano-A", "Milano-B", "Milano-C", "Milano-D"], "hops": 3},
    ]

    return {
        "candidate_paths": candidate_paths,
        "messages": [
            AIMessage(
                content=f"Symbolic solver found {len(candidate_paths)} candidate path(s) (placeholder).",
                name="symbolic_solver",
            )
        ],
    }
