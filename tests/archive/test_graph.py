"""Integration tests for the full LangGraph pipeline.

Tests the complete flow: operator message → supervisor → topology agent → response.
All LLM calls are mocked to avoid external API dependencies.
"""

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from src.agents.supervisor import set_supervisor_llm
from src.core.graph import build_graph, compile_graph
from src.core.state import TaskItem, TaskPlan, TaskType
from src.services.testbed_client import MockTestbedClient
from src.tools.fetch_topology import set_testbed_client


@pytest.fixture(autouse=True)
def _setup_dependencies() -> None:
    """Configure mock dependencies for integration tests."""
    # Mock testbed client
    set_testbed_client(MockTestbedClient())

    # Mock LLM
    mock_llm = MagicMock()

    # First call: structured output for intent parsing
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TaskPlan(
        intent_summary="The operator wants to see the current testbed topology",
        tasks=[
            TaskItem(
                task_type=TaskType.TOPOLOGY_QUERY,
                description="Fetch current network topology",
            )
        ],
    )
    mock_llm.with_structured_output.return_value = mock_structured

    # Second call: synthesis response
    mock_response = MagicMock()
    mock_response.content = (
        "The testbed has 4 nodes (Milano-A, Milano-B, Milano-C, Milano-D) "
        "connected in a linear topology with 3 fiber links totaling 95 km."
    )
    mock_llm.invoke.return_value = mock_response

    set_supervisor_llm(mock_llm)


# ---------------------------------------------------------------------------
# Graph structure tests
# ---------------------------------------------------------------------------


class TestGraphStructure:
    def test_build_graph_returns_state_graph(self) -> None:
        builder = build_graph()
        assert builder is not None

    def test_compile_graph_returns_compiled(self) -> None:
        graph = compile_graph()
        assert graph is not None

    def test_graph_has_supervisor_node(self) -> None:
        builder = build_graph()
        assert "supervisor" in builder.nodes

    def test_graph_has_topology_node(self) -> None:
        builder = build_graph()
        assert "topology_agent" in builder.nodes


# ---------------------------------------------------------------------------
# End-to-end integration tests
# ---------------------------------------------------------------------------


class TestTopologyQueryFlow:
    """Test the complete topology query flow end-to-end."""

    def test_full_topology_query_flow(self) -> None:
        """Operator asks about topology → supervisor → topology agent → response."""
        graph = compile_graph()
        initial_state = {
            "messages": [
                HumanMessage(content="What is the current topology of the testbed?")
            ],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": None,
            "error_context": None,
        }

        result = graph.invoke(initial_state)

        # Verify topology was fetched
        assert result["topology_snapshot"] is not None
        assert len(result["topology_snapshot"].nodes) == 4

        # Verify task plan was created
        assert result["task_plan"] is not None
        assert result["task_plan"].tasks[0].task_type == TaskType.TOPOLOGY_QUERY

    def test_messages_accumulate_through_pipeline(self) -> None:
        """Verify messages from each node are preserved in the final state."""
        graph = compile_graph()
        initial_state = {
            "messages": [HumanMessage(content="Show me the network")],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": None,
            "error_context": None,
        }

        result = graph.invoke(initial_state)

        # Should have: user msg + supervisor parse + topology summary + supervisor synthesis
        assert len(result["messages"]) >= 3

        # First message should be the original user message
        assert result["messages"][0].content == "Show me the network"

    def test_topology_snapshot_has_correct_structure(self) -> None:
        """Verify the topology snapshot contains ECOC testbed data."""
        graph = compile_graph()
        initial_state = {
            "messages": [HumanMessage(content="Display topology")],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": None,
            "error_context": None,
        }

        result = graph.invoke(initial_state)
        snapshot = result["topology_snapshot"]

        # 4 nodes
        node_names = [n.name for n in snapshot.nodes]
        assert "Milano-A" in node_names
        assert "Milano-D" in node_names

        # 3 links
        assert len(snapshot.links) == 3

        # Links have positive fiber lengths
        for link in snapshot.links:
            assert link.length_km > 0

    def test_final_message_is_from_supervisor(self) -> None:
        """The last message should be the supervisor's synthesis."""
        graph = compile_graph()
        initial_state = {
            "messages": [HumanMessage(content="What nodes are connected?")],
            "task_plan": None,
            "topology_snapshot": None,
            "current_agent": None,
            "error_context": None,
        }

        result = graph.invoke(initial_state)
        last_message = result["messages"][-1]

        assert isinstance(last_message, AIMessage)
        assert last_message.name == "supervisor"
