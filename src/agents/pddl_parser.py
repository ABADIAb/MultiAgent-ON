"""PDDL Parser node for the Neurosymbolic Intent Pipeline.

Sprint 2 (Exp 2.1) will implement:
- LLM prompt engineering to translate NL → PDDL constraints
- CFG (Context-Free Grammar) regex validator for structural correctness

Current: Pass-through placeholder that copies enriched_intent
to pddl_constraints with a dummy PDDL string.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from src.core.state import AgentState


def pddl_parser_node(state: AgentState) -> dict:
    """Parse enriched intent into PDDL constraints.

    Placeholder: passes the enriched intent through as a dummy PDDL string.
    Sprint 2 will implement real NL → PDDL translation with CFG validation.

    Returns:
        Partial state update with pddl_constraints and pddl_valid.
    """
    enriched = state.get("enriched_intent") or "No intent provided"

    # Placeholder: wrap intent in a dummy PDDL-like structure
    pddl = f"(define (problem optical-intent) (:intent {enriched}))"

    return {
        "pddl_constraints": pddl,
        "pddl_valid": True,  # Placeholder: always valid
        "messages": [
            AIMessage(
                content=f"PDDL constraints generated (placeholder): {pddl}",
                name="pddl_parser",
            )
        ],
    }
