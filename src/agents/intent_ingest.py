"""Intent Ingest node for the Neurosymbolic Intent Pipeline.

Exp 1.0: Verifies the LLM connection by parsing the operator's natural
language intent into a structured IntentSummary using Kimi's structured
output capability.

Future iterations will add Optical RAG enrichment (ITU-T standards,
transponder specs) before the LLM call.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.core.llm import get_llm
from src.core.state import AgentState

INTENT_SYSTEM_PROMPT = """\
You are the Intent Ingestion module of a Neurosymbolic Orchestrator for a \
Software-Defined Optical Network (SDON) testbed.

Your job is to parse the operator's natural language request and extract:
1. A one-sentence summary of the intent.
2. The source node (if mentioned).
3. The target/sink node (if mentioned).

The testbed has 4 nodes in a linear topology:
Milano-A ↔ Milano-B ↔ Milano-C ↔ Milano-D

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
        description="Source node name if mentioned (e.g., 'Milano-A').",
    )
    target_node: str | None = Field(
        default=None,
        description="Target/sink node name if mentioned (e.g., 'Milano-D').",
    )


def intent_ingest_node(state: AgentState) -> dict:
    """Ingest operator intent and verify LLM connection.

    Exp 1.0: Parses the operator's NL intent into a structured
    IntentSummary using the Kimi LLM with structured output.

    Returns:
        Partial state update with enriched_intent and messages.
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

    # Build enriched intent string (future: add RAG context here)
    parts = [f"Intent: {intent.summary}"]
    if intent.source_node:
        parts.append(f"Source: {intent.source_node}")
    if intent.target_node:
        parts.append(f"Target: {intent.target_node}")
    enriched = " | ".join(parts)

    return {
        "enriched_intent": enriched,
        "messages": [
            AIMessage(
                content=f"Intent parsed: {enriched}",
                name="intent_ingest",
            )
        ],
    }
