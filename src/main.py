"""CLI entrypoint for the Neurosymbolic Intent Orchestrator (V4).

Usage:
    uv run python src/main.py "Route from Milano-A to Milano-D"
    uv run python src/main.py  # Interactive mode

The pipeline uses interrupt() for HITL approval at the Reverse Prompting
stage. When running interactively, the CLI handles the interrupt/resume loop.
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from src.core.graph import compile_graph
from src.core.llm import create_kimi_llm, set_llm


def main(user_input: str | None = None) -> None:
    """Run the Neurosymbolic Intent Pipeline with a user query."""
    load_dotenv()

    # --- Configure LLM ---
    api_key = os.getenv("KIMI_API_KEY", "")
    base_url = os.getenv("KIMI_BASE_URL", "")

    if not api_key:
        print("ERROR: KIMI_API_KEY not set in environment or .env file.")
        print("Create a .env file with:")
        print('  KIMI_API_KEY="your-api-key-here"')
        print('  KIMI_BASE_URL="https://your-kimi-endpoint"')
        sys.exit(1)

    llm = create_kimi_llm(api_key=api_key, base_url=base_url or None)
    set_llm(llm)

    # --- Build and run graph ---
    # InMemorySaver is REQUIRED for interrupt() to work
    checkpointer = InMemorySaver()
    graph = compile_graph(checkpointer=checkpointer)

    if user_input is None:
        user_input = input("\n🔮 Neurosymbolic Intent Orchestrator (V4)\nOperator > ")

    print(f"\n--- Processing: {user_input!r} ---\n")

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "enriched_intent": None,
        "pddl_constraints": None,
        "pddl_valid": None,
        "hitl_reconstruction": None,
        "hitl_approved": None,
        "topology_snapshot": None,
        "candidate_paths": None,
        "qot_results": None,
        "planning_report": None,
        "error_context": None,
    }

    config = {"configurable": {"thread_id": "main-session"}}

    # --- HITL interrupt/resume loop ---
    stream_input = initial_state

    while True:
        result = graph.invoke(stream_input, config=config)

        # Check if graph is interrupted (waiting for HITL approval)
        state = graph.get_state(config)
        if state.next:
            # Graph is paused at an interrupt
            print("\n" + "=" * 60)
            print("HITL APPROVAL REQUIRED")
            print("=" * 60)

            # Show the interrupt payload
            if state.tasks:
                for task in state.tasks:
                    if hasattr(task, "interrupts") and task.interrupts:
                        for intr in task.interrupts:
                            print(f"\n{intr.value}")

            print("\nOptions: approve / refine / reject")
            action = input("Your decision > ").strip().lower()

            if action == "refine":
                feedback = input("Feedback > ").strip()
                resume_value = {"action": "refine", "feedback": feedback}
            elif action == "approve":
                resume_value = {"action": "approve"}
            else:
                resume_value = {"action": "reject"}

            stream_input = Command(resume=resume_value)
            continue

        # Graph completed — show results
        break

    # --- Display results ---
    print("\n" + "=" * 60)
    print("ORCHESTRATOR RESPONSE")
    print("=" * 60)

    for msg in result.get("messages", []):
        role = getattr(msg, "name", None) or getattr(msg, "type", "unknown")
        print(f"\n[{role}] {msg.content}")

    if result.get("planning_report"):
        print(f"\n📋 Planning Report:\n{result['planning_report']}")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    main(query)
