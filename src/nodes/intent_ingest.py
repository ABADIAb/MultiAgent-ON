"""Intent Ingest node for the Neurosymbolic Intent Pipeline.

Exp 1.0: Verifies the LLM connection by parsing the operator's natural
language intent into a structured IntentSummary using Kimi's structured
output capability.

Future iterations will add Optical RAG enrichment (ITU-T standards,
transponder specs) before the LLM call.
"""

from __future__ import annotations

import networkx as nx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.core.llm import get_llm
from src.core.mock_graphrag import (
    build_adjacency_graph,
    extract_k_hop_neighborhood,
    graph_to_context_string,
)
from src.core.state import AgentState, TopologySnapshot

INTENT_SYSTEM_PROMPT = """\
You are the Intent Ingestion module of a Neurosymbolic Orchestrator for a \
Software-Defined Optical Network (SDON) testbed.

Your job is to parse the operator's natural language request and extract:
1. A one-sentence summary of the intent.
2. The source node (if mentioned).
3. The target/sink node (if mentioned).

Be precise. If the operator mentions specific nodes, extract them exactly.
If no specific nodes are mentioned, leave source_node and target_node as null.\
"""


class IntentSummary(BaseModel):
    """Structured output from the Intent Ingest node."""

    summary: str = Field(
        description="One-sentence summary of the operator's intent.",
    )
    source_node: str | None = Field(
        default=None,
        description="Source node name if mentioned (e.g., 'Berlin').",
    )
    target_node: str | None = Field(
        default=None,
        description="Target/sink node name if mentioned (e.g., 'Munich').",
    )


def _resolve_node_id(graph: nx.Graph, name_or_id: str) -> str | None:
    """Resolve a node name or ID to a node ID in the graph."""
    if name_or_id in graph.nodes:
        return name_or_id
    for node_id, attrs in graph.nodes(data=True):
        if attrs.get("name") == name_or_id:
            return node_id
    return None


def intent_ingest_node(state: AgentState) -> dict:
    """Ingest operator intent and enrich with Optical RAG context.

    Parses the operator's NL intent into a structured IntentSummary using the
    LLM with structured output, then extracts a k-hop topology neighborhood
    using Mock GraphRAG to populate topology_context and enriched_intent.

    Returns:
        Partial state update with enriched_intent, topology_context, and messages.
    """
    # Extract the last human message
    user_messages = [
        msg
        for msg in state["messages"]
        if isinstance(msg, HumanMessage)
        or (isinstance(msg, dict) and msg.get("role") == "user")
    ]

    if not user_messages:
        return {
            "enriched_intent": None,
            "topology_context": None,
            "messages": [
                AIMessage(
                    content="No operator message received. Awaiting input.",
                    name="intent_ingest",
                )
            ],
            "error_context": "No user messages found in state.",
        }

    llm = get_llm()
    structured_llm = llm.with_structured_output(IntentSummary)

    messages = [
        SystemMessage(content=INTENT_SYSTEM_PROMPT),
        *state["messages"],
    ]

    intent = structured_llm.invoke(messages)
    assert isinstance(intent, IntentSummary)

    # Perform Optical RAG enrichment if topology_snapshot is available
    topology_snapshot = state.get("topology_snapshot")
    topology_context: str | None = None
    subtopology_snapshot: TopologySnapshot | None = None

    if topology_snapshot and topology_snapshot.nodes:
        graph = build_adjacency_graph(topology_snapshot)
        source_id = _resolve_node_id(graph, intent.source_node) if intent.source_node else None
        target_id = _resolve_node_id(graph, intent.target_node) if intent.target_node else None

        if source_id is None and graph.nodes:
            source_id = list(graph.nodes)[0]
        if target_id is None and graph.nodes:
            target_id = list(graph.nodes)[-1]

        if source_id and target_id and nx.has_path(graph, source_id, target_id):
            subgraph = extract_k_hop_neighborhood(graph, source_id, target_id, k=2)
        else:
            subgraph = graph

        topology_context = graph_to_context_string(subgraph)

        # Build structured subtopology snapshot for downstream symbolic solver
        sub_node_ids = set(subgraph.nodes)
        sub_nodes = [n for n in topology_snapshot.nodes if n.node_id in sub_node_ids]
        sub_links = [
            link for link in topology_snapshot.links
            if link.source_node in sub_node_ids and link.target_node in sub_node_ids
        ]
        subtopology_snapshot = TopologySnapshot(
            nodes=sub_nodes,
            links=sub_links,
            timestamp=topology_snapshot.timestamp,
        )

    # Build enriched intent string
    parts = [f"Intent: {intent.summary}"]
    if intent.source_node:
        parts.append(f"Source: {intent.source_node}")
    if intent.target_node:
        parts.append(f"Target: {intent.target_node}")
    enriched = " | ".join(parts)

    if topology_context:
        enriched = f"{enriched}\nTopology Context:\n{topology_context}"

    return {
        "enriched_intent": enriched,
        "topology_context": topology_context,
        "subtopology_snapshot": subtopology_snapshot,
        "messages": [
            AIMessage(
                content=f"Intent parsed: {enriched}",
                name="intent_ingest",
            )
        ],
    }
