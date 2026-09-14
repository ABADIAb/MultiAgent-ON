"""Intent Reconciler module for the Neurosymbolic Intent Pipeline.

Implements LLM-assisted intent reconciliation and refinement reasoning:
Analyzes operator feedback in Phase 3b (clarification) and Phase 6 (replan)
loops, distinguishes between full intent replacements vs partial constraint
updates, and synthesizes a single, non-contradictory operational active_intent.
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any

import networkx as nx
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.core.llm import get_llm
from src.core.mock_graphrag import (
    build_adjacency_graph,
    extract_k_hop_neighborhood,
    graph_to_context_string,
)
from src.core.state import AgentState, TopologySnapshot

logger = logging.getLogger(__name__)


class IntentUpdateType(str, Enum):
    """Scope of modification requested by operator refinement."""

    FULL_REPLACEMENT = "full_replacement"
    PARTIAL_UPDATE = "partial_update"


class RefinedIntentAnalysis(BaseModel):
    """Structured output from the Intent Reconciliation module."""

    update_type: IntentUpdateType = Field(
        description=(
            "Classification of update scope: 'full_replacement' if the operator "
            "aborts/discards the prior intent in favor of an entirely new request, "
            "or 'partial_update' if the operator adjusts, relaxes, adds, or removes "
            "specific constraints or endpoints."
        ),
    )
    reasoning: str = Field(
        description=(
            "Detailed step-by-step reasoning explaining the differences, what constraints "
            "changed, what was retained, and what was discarded."
        ),
    )
    updated_intent: str = Field(
        description=(
            "The comprehensive, unified, and grammatically complete natural language intent "
            "statement. Must contain NO contradictions, NO conversational filler, and NO "
            "meta-language like 'the operator said' or 'cancel that'."
        ),
    )
    source_node: str | None = Field(
        default=None,
        description="Active source node if specified or retained (e.g., 'Hamburg').",
    )
    target_node: str | None = Field(
        default=None,
        description="Active target/destination node if specified or retained (e.g., 'Berlin').",
    )
    modified_constraints: list[str] = Field(
        default_factory=list,
        description="List of specific constraints modified, added, relaxed, or removed.",
    )


INTENT_RECONCILIATION_PROMPT = """\
You are the Intent Reconciliation module of a Neurosymbolic Orchestrator for a \
Software-Defined Optical Network (SDON) testbed.

Your task is to analyze an operator's refinement feedback and systematically update \
the previous operational intent.

### CLASSIFICATION TAXONOMY:
1. FULL_REPLACEMENT ("full_replacement"):
   - Triggers when the operator explicitly cancels, aborts, resets, or replaces the \
entire request with a brand new objective (e.g. "Cancel that. Route from Cologne to \
Frankfurt", "Forget Munich, establish a path from Leipzig to Hamburg").
   - Action: Discard all prior constraints, endpoints, and exclusions. Formulate the \
new intent strictly from the latest instructions.

2. PARTIAL_UPDATE ("partial_update"):
   - Triggers when the operator modifies, adds, relaxes, or deletes specific constraints \
while maintaining the general request context.
   - Sub-types:
     * Constraint Relaxation: e.g. "Lower GSNR to 12 dB" -> update min-gsnr from 15 dB to 12 dB; \
keep source, target, and node exclusions.
     * Constraint Addition: e.g. "Also avoid node Hanover" -> retain existing exclusions and add Hanover.
     * Constraint Removal: e.g. "Remove the latency limit" -> drop latency constraint.
     * Endpoint Redirection: e.g. "Change destination to Berlin instead of Munich" -> update destination \
to Berlin; preserve source and compatible constraints.

### RULES:
- Output a single, clean, declarative natural language sentence in updated_intent.
- NEVER include conversational filler ("The operator says...", "I have updated...", "Here is the new intent...").
- NEVER retain contradictory constraints (e.g. cannot have both 15 dB and 12 dB; cannot have both Munich and Berlin as target).
- Explicitly identify active source_node and target_node whenever available.
- Always provide step-by-step reasoning explaining the differences and constraint delta.
"""


def _resolve_node_id(graph: nx.Graph, name_or_id: str) -> str | None:
    """Resolve a node name or ID to a node ID in the graph."""
    if name_or_id in graph.nodes:
        return name_or_id
    for node_id, attrs in graph.nodes(data=True):
        if attrs.get("name") == name_or_id:
            return node_id
    return None


def reconcile_operator_intent(
    current_intent: str,
    feedback: str,
    refinement_history: list[str] | None = None,
) -> RefinedIntentAnalysis:
    """Reconcile previous active intent with operator refinement feedback using LLM.

    Args:
        current_intent: The natural language intent active prior to this turn.
        feedback: The latest operator feedback / clarification string.
        refinement_history: Optional cumulative history of previous feedback turns.

    Returns:
        RefinedIntentAnalysis containing update_type, reasoning, and unified updated_intent.
    """
    history_block = ""
    if refinement_history and len(refinement_history) > 1:
        history_block = "\nCumulative Refinement History:\n" + "\n".join(
            f"- Turn {i}: {fb}" for i, fb in enumerate(refinement_history[:-1], 1)
        )

    user_content = (
        f"Previous Active Intent:\n{current_intent}\n"
        f"{history_block}\n"
        f"Latest Operator Refinement Feedback:\n{feedback}\n\n"
        "Please analyze the differences, classify the update scope, and synthesize the updated operational intent."
    )

    try:
        llm = get_llm()
        structured_llm = llm.with_structured_output(RefinedIntentAnalysis)
        messages = [
            SystemMessage(content=INTENT_RECONCILIATION_PROMPT),
            HumanMessage(content=user_content),
        ]
        result = structured_llm.invoke(messages)
        if isinstance(result, RefinedIntentAnalysis):
            return result
        # Fallback if structured_llm returned dict
        if isinstance(result, dict):
            return RefinedIntentAnalysis(**result)
    except Exception as exc:
        logger.warning(
            "Intent reconciliation LLM structured output failed (%s). Applying safe fallback.",
            exc,
        )
        fallback_intent = f"{current_intent} (Refined: {feedback})"
        return RefinedIntentAnalysis(
            update_type=IntentUpdateType.PARTIAL_UPDATE,
            reasoning=f"Fallback applied due to LLM error: {exc}",
            updated_intent=fallback_intent,
            modified_constraints=[feedback],
        )

    # Safe fallback if result was not recognized
    fallback_intent = f"{current_intent} (Refined: {feedback})"
    return RefinedIntentAnalysis(
        update_type=IntentUpdateType.PARTIAL_UPDATE,
        reasoning="Fallback applied: LLM response could not be parsed as RefinedIntentAnalysis.",
        updated_intent=fallback_intent,
        modified_constraints=[feedback],
    )


def reconcile_and_enrich_intent(state: AgentState) -> dict[str, Any]:
    """Execute intent reconciliation and update state with refreshed GraphRAG context.

    Evaluates whether the operator refinement changed endpoints; if so, re-extracts
    the k-hop subtopology from topology_snapshot.

    Args:
        state: AgentState with active_intent (or enriched_intent), error_context,
            and refinement_history.

    Returns:
        Partial state dictionary with active_intent, intent_update_type,
        intent_update_reasoning, enriched_intent, and refreshed subtopology fields.
    """
    raw_intent = state.get("active_intent") or state.get("enriched_intent") or ""
    # Strip subtopology context if present in raw_intent
    clean_intent = raw_intent.split("\nTopology Context:")[0].strip()
    clean_intent = clean_intent.split("Topology Context:")[0].strip()

    feedback = state.get("error_context") or ""
    refinement_history = state.get("refinement_history") or []
    if not feedback and refinement_history:
        feedback = refinement_history[-1]

    analysis = reconcile_operator_intent(
        current_intent=clean_intent,
        feedback=feedback,
        refinement_history=refinement_history,
    )

    # Check if endpoints changed to refresh GraphRAG subtopology
    topology_snapshot = state.get("topology_snapshot")
    topology_context = state.get("topology_context")
    subtopology_snapshot = state.get("subtopology_snapshot")

    if topology_snapshot and topology_snapshot.nodes and (analysis.source_node or analysis.target_node):
        graph = build_adjacency_graph(topology_snapshot)
        source_id = _resolve_node_id(graph, analysis.source_node) if analysis.source_node else None
        target_id = _resolve_node_id(graph, analysis.target_node) if analysis.target_node else None

        if source_id and target_id and nx.has_path(graph, source_id, target_id):
            subgraph = extract_k_hop_neighborhood(graph, source_id, target_id, k=2)
            topology_context = graph_to_context_string(subgraph)

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

    # Reconstruct enriched_intent with updated active_intent + topology_context
    enriched = analysis.updated_intent
    if topology_context:
        enriched = f"{enriched}\nTopology Context:\n{topology_context}"

    return {
        "active_intent": analysis.updated_intent,
        "intent_update_type": analysis.update_type.value,
        "intent_update_reasoning": analysis.reasoning,
        "enriched_intent": enriched,
        "subtopology_snapshot": subtopology_snapshot,
        "topology_context": topology_context,
    }
