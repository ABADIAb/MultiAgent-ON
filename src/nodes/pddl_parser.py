"""PDDL Parser node for the Neurosymbolic Intent Pipeline.

Exp 2.1: Translates enriched natural language intent into formal PDDL
constraint strings using the Kimi LLM, then validates structural
correctness via the CFG regex validator.

The PDDL subset is simplified for the optical network domain:
  (define (problem <name>)
    (:domain optical-network)
    (:objects <nodes> - node)
    (:init <topology predicates>)
    (:goal <routing constraints>)
  )
"""

from __future__ import annotations

import re

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.core.llm import get_llm
from src.core.pddl_validator import validate_pddl_syntax
from src.core.state import AgentState
from src.nodes.intent_reconciler import reconcile_and_enrich_intent

PDDL_SYSTEM_PROMPT = """\
You are the PDDL Parser module of a Neurosymbolic Orchestrator for a \
Software-Defined Optical Network (SDON) testbed.

Your job is to translate the operator's enriched intent into a formal \
PDDL problem string. Use this exact structure:

(define (problem <descriptive-name>)
  (:domain optical-network)
  (:objects
    <node-names> - node
  )
  (:init
    <topology predicates: (connected <src> <dst>), (link-active <src> <dst>), etc.>
  )
  (:goal
    (and
      <routing goal: (route <source> <target>)>
      <constraints: (min-gsnr <value>), (bandwidth <value>), (avoid-node <node>), (avoid-link <src> <dst>), etc.>
    )
  )
)

The network topology is provided in the enriched intent below. Use ONLY \
the nodes and links described there for :objects and :init sections.

Rules:
- Output ONLY the PDDL string, no explanations or markdown.
- Include ALL nodes and links in :objects and :init even if not all are mentioned in the intent.
- Always use the human-readable node names (e.g. Berlin, Frankfurt, Munich, Hamburg) for node objects and routing goals in PDDL, NOT internal IDs like node_1.
- Extract specific constraints (GSNR, bandwidth, avoid nodes, avoid links, etc) from the intent.
- If no specific constraints are mentioned, use only the (route ...) goal.\
"""


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences if the LLM wraps the output."""
    # Match ```pddl\n...\n``` or ```\n...\n```
    pattern = r"```(?:\w+)?\s*\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def pddl_parser_node(state: AgentState) -> dict:
    """Parse enriched intent into PDDL constraints using the LLM.

    1. If refinement feedback exists, reconciles intent via LLM reasoning first.
    2. Sends the active intent to Kimi with PDDL generation prompt.
    3. Strips any markdown code fences from the response.
    4. Validates structural syntax via CFG regex validator.
    5. Sets pddl_valid and error_context accordingly.

    Returns:
        Partial state update with pddl_constraints, pddl_valid,
        error_context, active_intent, and messages.
    """
    enriched = state.get("enriched_intent") or "No intent provided"
    previous_pddl = state.get("pddl_constraints")
    feedback = state.get("error_context")
    refinement_history = state.get("refinement_history") or []
    active_intent = state.get("active_intent")

    reconciliation_updates: dict = {}

    if previous_pddl and (feedback or refinement_history):
        # Reconcile intent using LLM reasoning (full replacement vs partial update)
        reconciliation_updates = reconcile_and_enrich_intent(state)
        active_intent = reconciliation_updates.get("active_intent") or active_intent
        enriched = reconciliation_updates.get("enriched_intent") or enriched

        history_text = (
            "\n".join(f"- {r}" for r in refinement_history)
            if refinement_history
            else f"- {feedback}"
        )
        user_content = (
            f"Active Operational Intent:\n{active_intent}\n\n"
            f"Original Intent: {enriched}\n\n"
            f"Previous PDDL constraints:\n{previous_pddl}\n\n"
            f"Operator refinement feedback:\n{history_text}\n\n"
            "Please generate the updated and corrected PDDL constraints incorporating all operator feedback."
        )
    else:
        user_content = enriched
        if not active_intent and enriched != "No intent provided":
            # Extract clean active intent from enriched if missing
            active_intent = enriched.split("\nTopology Context:")[0].strip()

    llm = get_llm()
    messages = [
        SystemMessage(content=PDDL_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    raw_pddl = response.content if isinstance(response.content, str) else str(response.content)

    # Strip markdown code fences if present
    pddl = _strip_code_fences(raw_pddl)

    # Validate structural syntax
    is_valid, errors = validate_pddl_syntax(pddl)

    error_ctx = "; ".join(errors) if errors else None

    msg_content = (
        f"PDDL constraints generated (valid={is_valid}): {pddl[:200]}..."
        if len(pddl) > 200
        else f"PDDL constraints generated (valid={is_valid}): {pddl}"
    )

    result: dict = {
        "pddl_constraints": pddl,
        "pddl_valid": is_valid,
        "error_context": error_ctx,
        "active_intent": active_intent,
        "messages": [
            AIMessage(content=msg_content, name="pddl_parser"),
        ],
    }

    if reconciliation_updates:
        if "intent_update_type" in reconciliation_updates:
            result["intent_update_type"] = reconciliation_updates["intent_update_type"]
        if "intent_update_reasoning" in reconciliation_updates:
            result["intent_update_reasoning"] = reconciliation_updates["intent_update_reasoning"]
        if "enriched_intent" in reconciliation_updates:
            result["enriched_intent"] = reconciliation_updates["enriched_intent"]
        if "subtopology_snapshot" in reconciliation_updates and reconciliation_updates["subtopology_snapshot"]:
            result["subtopology_snapshot"] = reconciliation_updates["subtopology_snapshot"]
        if "topology_context" in reconciliation_updates and reconciliation_updates["topology_context"]:
            result["topology_context"] = reconciliation_updates["topology_context"]

    return result
