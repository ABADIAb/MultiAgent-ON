"""Topology fetching tool for LangGraph agents.

Wraps the TestbedClient interface as a LangChain @tool so agents
can invoke it through standard tool-calling patterns.
"""

from __future__ import annotations

from langchain_core.tools import tool

from src.services.testbed_client import TestbedClient

# Module-level client reference, set during graph initialization.
_client: TestbedClient | None = None


def set_testbed_client(client: TestbedClient) -> None:
    """Configure the testbed client used by the fetch_topology tool."""
    global _client  # noqa: PLW0603
    _client = client


def get_testbed_client() -> TestbedClient:
    """Retrieve the configured testbed client or raise if not set."""
    if _client is None:
        msg = (
            "TestbedClient not configured. "
            "Call set_testbed_client() before using fetch_topology."
        )
        raise RuntimeError(msg)
    return _client


@tool
def fetch_topology() -> dict:
    """Fetch the current network topology from the SDON testbed.

    Returns a structured dictionary with nodes, links, and a timestamp.
    Each node includes its ID, name, and interface list.
    Each link includes source/target nodes, fiber length, amplifier count,
    and active channel count.
    """
    client = get_testbed_client()
    topology = client.get_topology()
    return topology.model_dump()
