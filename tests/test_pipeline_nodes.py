"""Tests for the V4 production pipeline nodes.

Covers:
- Exp 2.1: PDDL Parser node (LLM-mocked, CFG validation)
- Exp 2.2: Reverse Prompt HITL node (LLM-mocked, interrupt)
- Placeholder tests for Symbolic Solver, QoT Validation, Plan Synthesizer
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


VALID_PDDL_RESPONSE = (
    "(define (problem optical-route-001)\n"
    "  (:domain optical-network)\n"
    "  (:objects\n"
    "    Milano-A Milano-D - node\n"
    "  )\n"
    "  (:init\n"
    "    (connected Milano-A Milano-B)\n"
    "    (connected Milano-B Milano-C)\n"
    "    (connected Milano-C Milano-D)\n"
    "  )\n"
    "  (:goal\n"
    "    (and\n"
    "      (route Milano-A Milano-D)\n"
    "      (min-gsnr 15)\n"
    "    )\n"
    "  )\n"
    ")"
)

INVALID_PDDL_RESPONSE = "(define (problem broken (:domain optical-network)"

REVERSE_PROMPT_RECONSTRUCTION = (
    "I understand you want to establish a lightpath from Milano-A to Milano-D, "
    "with a minimum GSNR of 15 dB."
)


# ---------------------------------------------------------------------------
# Exp 2.1: PDDL Parser Node
# ---------------------------------------------------------------------------


class TestPddlParserNode:
    """Test the PDDL parser with mocked LLM."""

    @patch("src.agents.pddl_parser.get_llm")
    def test_valid_llm_response_sets_pddl_valid_true(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Route from Milano-A to Milano-D | min GSNR 15 dB")
        result = pddl_parser_node(state)

        assert result["pddl_valid"] is True
        assert result["pddl_constraints"] is not None

    @patch("src.agents.pddl_parser.get_llm")
    def test_valid_response_contains_pddl_structure(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Route from A to D")
        result = pddl_parser_node(state)

        assert "(define" in result["pddl_constraints"]
        assert "(problem" in result["pddl_constraints"]
        assert ":goal" in result["pddl_constraints"]

    @patch("src.agents.pddl_parser.get_llm")
    def test_invalid_llm_response_sets_pddl_valid_false(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=INVALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Route from A to B")
        result = pddl_parser_node(state)

        assert result["pddl_valid"] is False
        assert result["error_context"] is not None
        assert len(result["error_context"]) > 0

    @patch("src.agents.pddl_parser.get_llm")
    def test_enriched_intent_included_in_prompt(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        intent = "Route from Milano-A to Milano-D avoiding link B-C"
        state = _make_state(enriched_intent=intent)
        pddl_parser_node(state)

        # Verify the LLM was called with messages containing the intent
        call_args = mock_llm.invoke.call_args[0][0]
        message_contents = " ".join(msg.content for msg in call_args)
        assert intent in message_contents

    @patch("src.agents.pddl_parser.get_llm")
    def test_handles_none_enriched_intent(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent=None)
        result = pddl_parser_node(state)

        # Should still produce a result (LLM gets "No intent provided")
        assert result["pddl_constraints"] is not None

    @patch("src.agents.pddl_parser.get_llm")
    def test_strips_markdown_code_fences(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        fenced = f"```pddl\n{VALID_PDDL_RESPONSE}\n```"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=fenced)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)

        assert "```" not in result["pddl_constraints"]
        assert result["pddl_valid"] is True

    @patch("src.agents.pddl_parser.get_llm")
    def test_returns_ai_message(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)

        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "pddl_parser"

    @patch("src.agents.pddl_parser.get_llm")
    def test_error_context_contains_validation_errors(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=INVALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)

        # error_context should describe what's wrong
        assert result["error_context"] is not None
        assert isinstance(result["error_context"], str)


    @patch("src.agents.pddl_parser.get_llm")
    def test_refinement_incorporates_error_context_and_previous_pddl(self, mock_get_llm):
        from src.agents.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        feedback = "I want route from B to D instead"
        previous_pddl = "(define (problem old-pddl) ...)"
        state = _make_state(
            enriched_intent="Route from A to B",
            pddl_constraints=previous_pddl,
            error_context=feedback
        )
        pddl_parser_node(state)

        # Verify the LLM was called with messages containing the feedback and old PDDL
        call_args = mock_llm.invoke.call_args[0][0]
        message_contents = " ".join(msg.content for msg in call_args)
        assert feedback in message_contents
        assert previous_pddl in message_contents


# ---------------------------------------------------------------------------
# Exp 2.2: Reverse Prompt HITL Node
# ---------------------------------------------------------------------------


class TestReversePromptNode:
    """Test the Reverse Prompting node with mocked LLM and interrupt."""

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_reconstruction_uses_llm_output(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert result["hitl_reconstruction"] == REVERSE_PROMPT_RECONSTRUCTION

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_interrupt_called_with_reconstruction(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        reverse_prompt_node(state)

        # interrupt() should be called with a payload containing the reconstruction
        mock_interrupt.assert_called_once()
        payload = mock_interrupt.call_args[0][0]
        assert REVERSE_PROMPT_RECONSTRUCTION in payload["reconstruction"]

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_approve_sets_hitl_approved_true(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert result["hitl_approved"] is True

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_reject_sets_hitl_approved_false(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "reject"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert result["hitl_approved"] is False

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_refine_sets_feedback_in_error_context(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "refine", "feedback": "Add latency constraint"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert result["hitl_approved"] is False
        assert "latency" in result["error_context"].lower()

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_pddl_constraints_included_in_prompt(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        reverse_prompt_node(state)

        # Verify the LLM was called with messages containing the PDDL
        call_args = mock_llm.invoke.call_args[0][0]
        message_contents = " ".join(msg.content for msg in call_args)
        assert "define" in message_contents

    @patch("src.agents.reverse_prompt.interrupt")
    @patch("src.agents.reverse_prompt.get_llm")
    def test_returns_ai_message(self, mock_get_llm, mock_interrupt):
        from src.agents.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm
        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "reverse_prompt"


# ---------------------------------------------------------------------------
# Symbolic Solver (placeholder — unchanged)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# QoT Validation (placeholder — unchanged)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Plan Synthesizer (placeholder — unchanged)
# ---------------------------------------------------------------------------


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
