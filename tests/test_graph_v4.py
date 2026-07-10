"""Tests for the V4 Neurosymbolic Intent Pipeline graph.

Validates graph structure, node registration, edge wiring,
and compilation with checkpointer.
"""

from __future__ import annotations

import pytest


class TestBuildGraph:
    """Test the V4 graph builder."""

    def test_build_graph_returns_state_graph(self):
        from src.core.graph import build_graph
        from langgraph.graph import StateGraph

        builder = build_graph()
        assert isinstance(builder, StateGraph)

    def test_graph_has_all_v4_nodes(self):
        from src.core.graph import build_graph

        builder = build_graph()
        node_names = set(builder.nodes.keys())
        expected = {
            "intent_ingest",
            "pddl_parser",
            "reverse_prompt",
            "symbolic_solver",
            "qot_validation",
            "plan_synthesizer",
        }
        assert expected.issubset(node_names), f"Missing nodes: {expected - node_names}"

    def test_graph_does_not_have_v3_nodes(self):
        from src.core.graph import build_graph

        builder = build_graph()
        node_names = set(builder.nodes.keys())
        assert "supervisor" not in node_names
        assert "topology_agent" not in node_names


class TestCompileGraph:
    """Test graph compilation."""

    def test_compile_graph_without_checkpointer(self):
        from src.core.graph import compile_graph

        graph = compile_graph()
        assert graph is not None

    def test_compile_graph_with_checkpointer(self):
        from langgraph.checkpoint.memory import InMemorySaver
        from src.core.graph import compile_graph

        checkpointer = InMemorySaver()
        graph = compile_graph(checkpointer=checkpointer)
        assert graph is not None


class TestHitlRoute:
    """Test the HITL conditional routing function."""

    def test_approved_routes_to_symbolic_solver(self):
        from src.agents.reverse_prompt import hitl_route

        state = {"hitl_approved": True, "error_context": None}
        assert hitl_route(state) == "symbolic_solver"

    def test_refine_routes_to_pddl_parser(self):
        from src.agents.reverse_prompt import hitl_route

        state = {"hitl_approved": False, "error_context": "Please add latency constraint"}
        assert hitl_route(state) == "pddl_parser"

    def test_reject_routes_to_end(self):
        from src.agents.reverse_prompt import hitl_route

        state = {"hitl_approved": False, "error_context": None}
        assert hitl_route(state) == "__end__"

    def test_none_approved_routes_to_end(self):
        from src.agents.reverse_prompt import hitl_route

        state = {"hitl_approved": None, "error_context": None}
        assert hitl_route(state) == "__end__"
