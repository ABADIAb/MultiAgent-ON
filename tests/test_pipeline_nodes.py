"""Tests for the V4 placeholder pipeline nodes.

Validates that each placeholder node correctly updates the state
with its expected fields, even in pass-through mode.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage, HumanMessage


def _make_state(**overrides) -> dict:
    """Create a minimal V4 AgentState dict with optional overrides."""
    base = {
        "messages": [HumanMessage(content="Test intent")],
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
    base.update(overrides)
    return base


class TestPddlParserNode:
    """Test the PDDL parser placeholder."""

    def test_returns_pddl_constraints(self):
        from src.agents.pddl_parser import pddl_parser_node

        state = _make_state(enriched_intent="Route from A to B")
        result = pddl_parser_node(state)
        assert result["pddl_constraints"] is not None
        assert "Route from A to B" in result["pddl_constraints"]

    def test_returns_pddl_valid_true(self):
        from src.agents.pddl_parser import pddl_parser_node

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)
        assert result["pddl_valid"] is True

    def test_returns_ai_message(self):
        from src.agents.pddl_parser import pddl_parser_node

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)
        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)

    def test_handles_none_enriched_intent(self):
        from src.agents.pddl_parser import pddl_parser_node

        state = _make_state(enriched_intent=None)
        result = pddl_parser_node(state)
        assert result["pddl_constraints"] is not None


class TestSymbolicSolverNode:
    """Test the Symbolic Solver placeholder."""

    def test_returns_candidate_paths(self):
        from src.agents.symbolic_solver import symbolic_solver_node

        state = _make_state()
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] is not None
        assert len(result["candidate_paths"]) >= 1

    def test_candidate_has_path_field(self):
        from src.agents.symbolic_solver import symbolic_solver_node

        state = _make_state()
        result = symbolic_solver_node(state)
        candidate = result["candidate_paths"][0]
        assert "path" in candidate

    def test_returns_ai_message(self):
        from src.agents.symbolic_solver import symbolic_solver_node

        state = _make_state()
        result = symbolic_solver_node(state)
        assert isinstance(result["messages"][0], AIMessage)


class TestQotValidationNode:
    """Test the QoT Validation placeholder."""

    def test_returns_qot_results(self):
        from src.agents.qot_validation import qot_validation_node

        state = _make_state(
            candidate_paths=[{"path": ["A", "B"], "hops": 1}]
        )
        result = qot_validation_node(state)
        assert result["qot_results"] is not None
        assert len(result["qot_results"]) == 1

    def test_placeholder_marks_all_feasible(self):
        from src.agents.qot_validation import qot_validation_node

        state = _make_state(
            candidate_paths=[
                {"path": ["A", "B"], "hops": 1},
                {"path": ["A", "C", "B"], "hops": 2},
            ]
        )
        result = qot_validation_node(state)
        assert all(r["feasible"] for r in result["qot_results"])

    def test_handles_empty_candidates(self):
        from src.agents.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=[])
        result = qot_validation_node(state)
        assert result["qot_results"] == []

    def test_handles_none_candidates(self):
        from src.agents.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=None)
        result = qot_validation_node(state)
        assert result["qot_results"] == []


class TestPlanSynthesizerNode:
    """Test the Plan Synthesizer placeholder."""

    def test_returns_planning_report(self):
        from src.agents.plan_synthesizer import plan_synthesizer_node

        state = _make_state(
            enriched_intent="Route from A to B",
            qot_results=[{"path": ["A", "B"], "feasible": True, "snr_dB": 15.0, "power_dBm": -10.0}],
        )
        result = plan_synthesizer_node(state)
        assert result["planning_report"] is not None
        assert "Planning Report" in result["planning_report"]

    def test_report_includes_feasible_paths(self):
        from src.agents.plan_synthesizer import plan_synthesizer_node

        state = _make_state(
            qot_results=[{"path": ["A", "B"], "feasible": True, "snr_dB": 12.0, "power_dBm": -8.0}],
        )
        result = plan_synthesizer_node(state)
        assert "A → B" in result["planning_report"]

    def test_report_handles_no_feasible_paths(self):
        from src.agents.plan_synthesizer import plan_synthesizer_node

        state = _make_state(qot_results=[])
        result = plan_synthesizer_node(state)
        assert "No feasible paths" in result["planning_report"]

    def test_returns_ai_message(self):
        from src.agents.plan_synthesizer import plan_synthesizer_node

        state = _make_state(qot_results=[])
        result = plan_synthesizer_node(state)
        assert isinstance(result["messages"][0], AIMessage)
