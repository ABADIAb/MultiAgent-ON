"""CLI entrypoint for the MultiAgentON orchestrator.

Usage:
    uv run python src/main.py "What is the current topology of the testbed?"
    uv run python src/main.py  # Interactive mode
"""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from src.agents.supervisor import create_default_llm, set_supervisor_llm
from src.core.graph import compile_graph
from src.services.testbed_client import MockTestbedClient
from src.tools.fetch_topology import set_testbed_client


def main(user_input: str | None = None) -> None:
    """Run the MultiAgentON pipeline with a user query."""
    load_dotenv()

    # --- Configure testbed client ---
    set_testbed_client(MockTestbedClient())

    # --- Configure LLM ---
    api_key = os.getenv("KIMI_API_KEY", "")
    base_url = os.getenv("KIMI_BASE_URL", "")

    if not api_key:
        print("ERROR: KIMI_API_KEY not set in environment or .env file.")
        print("Create a .env file with:")
        print('  KIMI_API_KEY="your-api-key-here"')
        print('  KIMI_BASE_URL="https://your-kimi-endpoint"')
        sys.exit(1)

    llm = create_default_llm(api_key=api_key, base_url=base_url or None)
    set_supervisor_llm(llm)

    # --- Build and run graph ---
    graph = compile_graph()

    if user_input is None:
        user_input = input("\n🔮 MultiAgentON Orchestrator\nOperator > ")

    print(f"\n--- Processing: {user_input!r} ---\n")

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "task_plan": None,
        "topology_snapshot": None,
        "current_agent": None,
        "error_context": None,
    }

    result = graph.invoke(initial_state)

    # --- Display results ---
    print("=" * 60)
    print("ORCHESTRATOR RESPONSE")
    print("=" * 60)

    for msg in result["messages"]:
        role = getattr(msg, "name", None) or getattr(msg, "type", "unknown")
        print(f"\n[{role}] {msg.content}")

    if result.get("topology_snapshot"):
        snap = result["topology_snapshot"]
        print(f"\n📊 Topology: {len(snap.nodes)} nodes, {len(snap.links)} links")


if __name__ == "__main__":
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    main(query)
