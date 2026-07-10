"""Tests for the Supervisor Agent node (LLM mocked)."""

from unittest.mock import MagicMock

import pytest
from langchain_core.messages import HumanMessage

from src.agents.supervisor import (
    get_supervisor_llm,
    route_by_task,
    set_supervisor_llm,
    supervisor_node,
)
from src.core.state import (
    AgentState,
    FiberLink,
    NetworkNode,
    TaskItem,
    TaskPlan,
    TaskType,
    TopologySnapshot,
)


def _make_state(**overrides) -> AgentState:
    """Create a default AgentState with optional overrides."""
    base: AgentState = {
        "messages": [],
        "task_plan": None,
        "topology_snapshot": None,
        "current_agent": None,
        "error_context": None,
    }
    base.update(overrides)
    return base


@pytest.fixture(autouse=True)
def _setup_mock_llm() -> None:
    """Provide a mock LLM for all tests."""
    mock_llm = MagicMock()
    # Default: return a TaskPlan for topology queries
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = TaskPlan(
        intent_summary="Query the current testbed topology",
        tasks=[TaskItem(task_type=TaskType.TOPOLOGY_QUERY, description="Fetch topology")],
    )
    mock_llm.with_structured_output.return_value = mock_structured
    # For synthesis pass
    mock_response = MagicMock()
    mock_response.content = "The network has 4 nodes in a linear topology."
    mock_llm.invoke.return_value = mock_response
    set_supervisor_llm(mock_llm)


# ---------------------------------------------------------------------------
# LLM configuration tests
# ---------------------------------------------------------------------------


class TestSupervisorLLMConfig:
    def test_raises_without_llm(self) -> None:
        set_supervisor_llm(None)  # type: ignore[arg-type]
        from src.agents import supervisor as sv_mod

        sv_mod._llm = None
        with pytest.raises(RuntimeError, match="Supervisor LLM not configured"):
            get_supervisor_llm()


# ---------------------------------------------------------------------------
# supervisor_node tests (intent parsing)
# ---------------------------------------------------------------------------


class TestSupervisorNodeIntentParsing:
    def test_parses_topology_query(self) -> None:
        state = _make_state(
            messages=[HumanMessage(content="What is the current topology?")]
        )
        result = supervisor_node(state)
        assert result["task_plan"] is not None
        assert result["task_plan"].tasks[0].task_type == TaskType.TOPOLOGY_QUERY

    def test_returns_summary_message(self) -> None:
        state = _make_state(
            messages=[HumanMessage(content="Show me the network")]
        )
        result = supervisor_node(state)
        messages = result["messages"]
        assert len(messages) == 1
        assert "Intent parsed" in messages[0].content

    def test_handles_empty_messages(self) -> None:
        state = _make_state(messages=[])
        result = supervisor_node(state)
        assert "Awaiting input" in result["messages"][0].content

    def test_returns_task_count_in_summary(self) -> None:
        state = _make_state(
            messages=[HumanMessage(content="Check the network")]
        )
        result = supervisor_node(state)
        assert "1 task(s)" in result["messages"][0].content


# ---------------------------------------------------------------------------
# supervisor_node tests (synthesis pass)
# ---------------------------------------------------------------------------


class TestSupervisorNodeSynthesis:
    def test_synthesizes_when_topology_available(self) -> None:
        topology = TopologySnapshot(
            nodes=[
                NetworkNode(node_id="n1", name="Milano-A"),
                NetworkNode(node_id="n2", name="Milano-B"),
            ],
            links=[
                FiberLink(
                    link_id="l1",
                    source_node="n1",
                    target_node="n2",
                    length_km=25.0,
                )
            ],
        )
        plan = TaskPlan(
            intent_summary="Topology query",
            tasks=[TaskItem(task_type=TaskType.TOPOLOGY_QUERY)],
        )
        state = _make_state(
            messages=[HumanMessage(content="Show topology")],
            task_plan=plan,
            topology_snapshot=topology,
        )
        result = supervisor_node(state)
        # Should use the synthesis path (calls llm.invoke, not with_structured_output)
        assert result["current_agent"] is None  # Flow complete

    def test_synthesis_produces_message(self) -> None:
        topology = TopologySnapshot(
            nodes=[NetworkNode(node_id="n1", name="A")],
            links=[],
        )
        plan = TaskPlan(
            intent_summary="Query topology",
            tasks=[TaskItem(task_type=TaskType.TOPOLOGY_QUERY)],
        )
        state = _make_state(
            messages=[HumanMessage(content="Show topology")],
            task_plan=plan,
            topology_snapshot=topology,
        )
        result = supervisor_node(state)
        assert len(result["messages"]) == 1
        assert result["messages"][0].content != ""


# ---------------------------------------------------------------------------
# route_by_task tests
# ---------------------------------------------------------------------------


class TestRouteByTask:
    def test_routes_topology_query(self) -> None:
        plan = TaskPlan(
            intent_summary="Topology",
            tasks=[TaskItem(task_type=TaskType.TOPOLOGY_QUERY)],
        )
        state = _make_state(task_plan=plan)
        assert route_by_task(state) == "topology_agent"

    def test_routes_to_end_for_unknown(self) -> None:
        plan = TaskPlan(
            intent_summary="Unknown",
            tasks=[TaskItem(task_type=TaskType.UNKNOWN)],
        )
        state = _make_state(task_plan=plan)
        assert route_by_task(state) == "__end__"

    def test_routes_to_end_when_no_plan(self) -> None:
        state = _make_state()
        assert route_by_task(state) == "__end__"

    def test_routes_to_end_when_empty_tasks(self) -> None:
        plan = TaskPlan(intent_summary="Nothing", tasks=[])
        state = _make_state(task_plan=plan)
        assert route_by_task(state) == "__end__"

    def test_routes_to_end_when_topology_already_fetched(self) -> None:
        """After topology is fetched, route to END for synthesis."""
        plan = TaskPlan(
            intent_summary="Topology",
            tasks=[TaskItem(task_type=TaskType.TOPOLOGY_QUERY)],
        )
        topology = TopologySnapshot(nodes=[], links=[])
        state = _make_state(task_plan=plan, topology_snapshot=topology)
        assert route_by_task(state) == "__end__"

    def test_routes_to_end_for_unimplemented_tasks(self) -> None:
        plan = TaskPlan(
            intent_summary="Provision",
            tasks=[TaskItem(task_type=TaskType.LIGHTPATH_PROVISION)],
        )
        state = _make_state(task_plan=plan)
        assert route_by_task(state) == "__end__"
