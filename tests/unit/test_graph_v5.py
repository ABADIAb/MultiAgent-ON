"""Tests for the V5 Risk-Adaptive Neurosymbolic Intent Pipeline graph.

Validates graph structure, node registration, edge wiring,
and V5 conditional routing functions (semantic_gate_route, radg_route).
"""

from __future__ import annotations

from typing import cast

import pytest

from src.core.state import AgentState


class TestBuildGraph:
    """Test the V5 graph builder."""

    def test_build_graph_returns_state_graph(self):
        from langgraph.graph import StateGraph

        from src.core.graph import build_graph

        builder = build_graph()
        assert isinstance(builder, StateGraph)

    def test_graph_has_all_v5_nodes(self):
        from src.core.graph import build_graph

        builder = build_graph()
        node_names = set(builder.nodes.keys())
        expected = {
            "intent_ingest",
            "pddl_parser",
            "reverse_prompt",
            "semantic_gate",
            "hitl_clarify",
            "symbolic_solver",
            "qot_validation",
            "radg",
            "plan_synthesizer",
        }
        assert expected.issubset(node_names), f"Missing nodes: {expected - node_names}"

    def test_graph_has_semantic_gate_node(self):
        """semantic_gate must be in the V5 graph."""
        from src.core.graph import build_graph

        builder = build_graph()
        assert "semantic_gate" in builder.nodes

    def test_graph_has_hitl_clarify_node(self):
        """hitl_clarify must be in the V5 graph."""
        from src.core.graph import build_graph

        builder = build_graph()
        assert "hitl_clarify" in builder.nodes

    def test_graph_has_radg_node(self):
        """radg must be in the V5 graph."""
        from src.core.graph import build_graph

        builder = build_graph()
        assert "radg" in builder.nodes

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


class TestSemanticGateRoute:
    """Test the V5 Semantic Gate conditional routing function."""

    def test_usem_passed_routes_to_symbolic_solver(self):
        from src.nodes.semantic_gate_node import semantic_gate_route

        state = cast(AgentState, {"usem_passed": True, "usem_score": 0.1})
        assert semantic_gate_route(state) == "symbolic_solver"

    def test_usem_failed_routes_to_hitl_clarify(self):
        from src.nodes.semantic_gate_node import semantic_gate_route

        state = cast(AgentState, {"usem_passed": False, "usem_score": 0.8})
        assert semantic_gate_route(state) == "hitl_clarify"

    def test_usem_none_routes_to_hitl_clarify(self):
        """None (not yet evaluated) → clarify via Phase 3b HITL."""
        from src.nodes.semantic_gate_node import semantic_gate_route

        state = cast(AgentState, {"usem_passed": None, "usem_score": None})
        assert semantic_gate_route(state) == "hitl_clarify"


class TestRadgRoute:
    """Test the V5 RADG conditional routing function."""

    def test_approve_routes_to_plan_synthesizer(self):
        from src.nodes.radg_node import radg_route

        state = cast(AgentState, {"radg_decision": "approve"})
        assert radg_route(state) == "plan_synthesizer"

    def test_replan_routes_to_pddl_parser(self):
        from src.nodes.radg_node import radg_route

        state = cast(AgentState, {"radg_decision": "replan"})
        assert radg_route(state) == "pddl_parser"

    def test_none_decision_routes_to_pddl_parser(self):
        """None decision (edge case) defaults to replan."""
        from src.nodes.radg_node import radg_route

        state = cast(AgentState, {"radg_decision": None})
        assert radg_route(state) == "pddl_parser"
