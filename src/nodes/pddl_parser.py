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
      <constraints: (min-gsnr <value>), (max-latency <value>), (avoid-link <src> <dst>), etc.>
    )
  )
)

The testbed has 4 nodes in a linear topology:
Milano-A <-> Milano-B <-> Milano-C <-> Milano-D

Rules:
- Output ONLY the PDDL string, no explanations or markdown.
- Include ALL nodes and links in :objects and :init even if not all are \
mentioned in the intent.
- Extract specific constraints (GSNR, latency, avoid links) from the intent.
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

    1. Sends the enriched intent to Kimi with PDDL generation prompt.
    2. Strips any markdown code fences from the response.
    3. Validates structural syntax via CFG regex validator.
    4. Sets pddl_valid and error_context accordingly.

    Returns:
        Partial state update with pddl_constraints, pddl_valid,
        error_context, and messages.
    """
    enriched = state.get("enriched_intent") or "No intent provided"
    previous_pddl = state.get("pddl_constraints")
    feedback = state.get("error_context")

    if previous_pddl and feedback:
        user_content = (
            f"Original Intent: {enriched}\n\n"
            f"Previous PDDL constraints:\n{previous_pddl}\n\n"
            f"Operator refinement feedback: {feedback}\n\n"
            "Please generate the updated and corrected PDDL constraints incorporating the operator's feedback."
        )
    else:
        user_content = enriched

    llm = get_llm()
    messages = [
        SystemMessage(content=PDDL_SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]

    response = llm.invoke(messages)
    raw_pddl = response.content

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

    return {
        "pddl_constraints": pddl,
        "pddl_valid": is_valid,
        "error_context": error_ctx,
        "messages": [
            AIMessage(content=msg_content, name="pddl_parser"),
        ],
    }
