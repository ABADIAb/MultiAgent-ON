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

from src.core.state import AgentState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_state(**overrides) -> AgentState:
    """Create a minimal V5 AgentState dict with optional overrides."""
    base: AgentState = {
        "messages": [HumanMessage(content="Test intent")],
        "enriched_intent": None,
        "pddl_constraints": None,
        "pddl_valid": None,
        "pddl_parsed_constraints": None,
        "hitl_reconstruction": None,
        "hitl_approved": None,
        "topology_snapshot": None,
        "candidate_paths": None,
        "qot_results": None,
        "planning_report": None,
        "error_context": None,
        "usem_score": None,
        "usem_passed": None,
        "radg_decision": None,
        "topology_context": None,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
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

    @patch("src.nodes.pddl_parser.get_llm")
    def test_valid_llm_response_sets_pddl_valid_true(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Route from Milano-A to Milano-D | min GSNR 15 dB")
        result = pddl_parser_node(state)

        assert result["pddl_valid"] is True
        assert result["pddl_constraints"] is not None

    @patch("src.nodes.pddl_parser.get_llm")
    def test_valid_response_contains_pddl_structure(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Route from A to D")
        result = pddl_parser_node(state)

        assert "(define" in result["pddl_constraints"]
        assert "(problem" in result["pddl_constraints"]
        assert ":goal" in result["pddl_constraints"]

    @patch("src.nodes.pddl_parser.get_llm")
    def test_invalid_llm_response_sets_pddl_valid_false(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=INVALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Route from A to B")
        result = pddl_parser_node(state)

        assert result["pddl_valid"] is False
        assert result["error_context"] is not None
        assert len(result["error_context"]) > 0

    @patch("src.nodes.pddl_parser.get_llm")
    def test_enriched_intent_included_in_prompt(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

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

    @patch("src.nodes.pddl_parser.get_llm")
    def test_handles_none_enriched_intent(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent=None)
        result = pddl_parser_node(state)

        # Should still produce a result (LLM gets "No intent provided")
        assert result["pddl_constraints"] is not None

    @patch("src.nodes.pddl_parser.get_llm")
    def test_strips_markdown_code_fences(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        fenced = f"```pddl\n{VALID_PDDL_RESPONSE}\n```"
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=fenced)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)

        assert "```" not in result["pddl_constraints"]
        assert result["pddl_valid"] is True

    @patch("src.nodes.pddl_parser.get_llm")
    def test_returns_ai_message(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=VALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)

        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "pddl_parser"

    @patch("src.nodes.pddl_parser.get_llm")
    def test_error_context_contains_validation_errors(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=INVALID_PDDL_RESPONSE)
        mock_get_llm.return_value = mock_llm

        state = _make_state(enriched_intent="Test")
        result = pddl_parser_node(state)

        # error_context should describe what's wrong
        assert result["error_context"] is not None
        assert isinstance(result["error_context"], str)


    @patch("src.nodes.pddl_parser.get_llm")
    def test_refinement_incorporates_error_context_and_previous_pddl(self, mock_get_llm):
        from src.nodes.pddl_parser import pddl_parser_node

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

    def test_no_hardcoded_topology_in_system_prompt(self):
        """PDDL_SYSTEM_PROMPT must not have hardcoded testbed nodes/topology."""
        from src.nodes.pddl_parser import PDDL_SYSTEM_PROMPT

        assert "Milano-A <-> Milano-B" not in PDDL_SYSTEM_PROMPT
        assert "The network topology is provided in the enriched intent" in PDDL_SYSTEM_PROMPT


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Exp 2.2: Reverse Prompting & HITL Clarification Nodes
# ---------------------------------------------------------------------------


class TestReversePromptNode:
    """Test the automated Reverse Prompting node with mocked LLM (Phase 3a)."""

    @patch("src.nodes.reverse_prompt.get_llm")
    def test_reconstruction_uses_llm_output(self, mock_get_llm):
        from src.nodes.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert result["hitl_reconstruction"] == REVERSE_PROMPT_RECONSTRUCTION

    @patch("src.nodes.reverse_prompt.get_llm")
    def test_pddl_constraints_included_in_prompt(self, mock_get_llm):
        from src.nodes.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        reverse_prompt_node(state)

        # Verify the LLM was called with messages containing the PDDL
        call_args = mock_llm.invoke.call_args[0][0]
        message_contents = " ".join(msg.content for msg in call_args)
        assert "define" in message_contents

    @patch("src.nodes.reverse_prompt.get_llm")
    def test_returns_ai_message(self, mock_get_llm):
        from src.nodes.reverse_prompt import reverse_prompt_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content=REVERSE_PROMPT_RECONSTRUCTION)
        mock_get_llm.return_value = mock_llm

        state = _make_state(pddl_constraints=VALID_PDDL_RESPONSE)
        result = reverse_prompt_node(state)

        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "reverse_prompt"


class TestHitlClarifyNode:
    """Test the Phase 3b HITL clarification node with mocked interrupt."""

    @patch("src.nodes.reverse_prompt.interrupt")
    def test_interrupt_called_with_clarification_payload(self, mock_interrupt):
        from src.nodes.reverse_prompt import hitl_clarify_node

        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(
            hitl_reconstruction=REVERSE_PROMPT_RECONSTRUCTION,
            usem_score=0.75,
            pddl_valid=True,
            error_context="Ambiguous intent",
        )
        hitl_clarify_node(state)

        mock_interrupt.assert_called_once()
        payload = mock_interrupt.call_args[0][0]
        assert payload["status"] == "clarification_required"
        assert payload["reconstruction"] == REVERSE_PROMPT_RECONSTRUCTION
        assert payload["usem_score"] == 0.75

    @patch("src.nodes.reverse_prompt.interrupt")
    def test_unsupported_action_sets_hitl_approved_false(self, mock_interrupt):
        from src.nodes.reverse_prompt import hitl_clarify_node

        # "approve" is no longer a supported action in V5 Phase 3b.
        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(hitl_reconstruction=REVERSE_PROMPT_RECONSTRUCTION)
        result = hitl_clarify_node(state)

        assert result["hitl_approved"] is False

    @patch("src.nodes.reverse_prompt.interrupt")
    def test_refine_sets_feedback_in_error_context(self, mock_interrupt):
        from src.nodes.reverse_prompt import hitl_clarify_node

        mock_interrupt.return_value = {"action": "refine", "feedback": "Add latency constraint"}

        state = _make_state(hitl_reconstruction=REVERSE_PROMPT_RECONSTRUCTION)
        result = hitl_clarify_node(state)

        assert result["hitl_approved"] is False
        assert "latency" in result["error_context"].lower()

    @patch("src.nodes.reverse_prompt.interrupt")
    def test_returns_ai_message(self, mock_interrupt):
        from src.nodes.reverse_prompt import hitl_clarify_node

        mock_interrupt.return_value = {"action": "refine", "feedback": "Fixed route"}

        state = _make_state(hitl_reconstruction=REVERSE_PROMPT_RECONSTRUCTION)
        result = hitl_clarify_node(state)

        assert len(result["messages"]) == 1
        assert isinstance(result["messages"][0], AIMessage)
        assert result["messages"][0].name == "hitl_clarify"

    @patch("src.nodes.reverse_prompt.interrupt")
    def test_approve_action_with_pddl_valid_sets_hitl_approved_true(self, mock_interrupt):
        """When operator chooses 'Continúa con lo que entendiste' and PDDL is valid, approve passes."""
        from src.nodes.reverse_prompt import hitl_clarify_node

        mock_interrupt.return_value = {"action": "approve"}

        state = _make_state(
            hitl_reconstruction=REVERSE_PROMPT_RECONSTRUCTION,
            pddl_valid=True,
            usem_score=0.4,
        )
        result = hitl_clarify_node(state)

        assert result["hitl_approved"] is True
        assert result["usem_passed"] is True
        assert result["error_context"] is None
        assert "Operator approved understanding" in result["messages"][0].content

    def test_hitl_clarify_route_branching(self):
        """Route to symbolic_solver when approved, loop to pddl_parser when not approved."""
        from src.nodes.reverse_prompt import hitl_clarify_route

        approved_state = _make_state(hitl_approved=True)
        assert hitl_clarify_route(approved_state) == "symbolic_solver"

        unapproved_state = _make_state(hitl_approved=False)
        assert hitl_clarify_route(unapproved_state) == "pddl_parser"



# ---------------------------------------------------------------------------
# Symbolic Solver (real implementation — Exp 2.3)
# ---------------------------------------------------------------------------


class TestSymbolicSolverNode:
    """Test the Symbolic Solver node (real implementation).

    With no topology_snapshot in state, the solver returns empty paths.
    Full path-finding behavior is tested in test_symbolic_solver.py.
    """

    def test_returns_candidate_paths_key(self):
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state()
        result = symbolic_solver_node(state)
        assert "candidate_paths" in result

    def test_returns_empty_without_topology(self):
        """No topology in state → no paths (correct behavior for real solver)."""
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state()  # topology_snapshot=None
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] == []

    def test_returns_ai_message(self):
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state()
        result = symbolic_solver_node(state)
        assert isinstance(result["messages"][0], AIMessage)


# ---------------------------------------------------------------------------
# QoT Validation (placeholder — unchanged)
# ---------------------------------------------------------------------------


class TestQotValidationNode:
    """Test the QoT Validation node with real GN-model physics (Sprint 3)."""

    # A minimal path with realistic ECOC amplifier data (link_ab: 20 km)
    FEASIBLE_PATH = {
        "nodes": ["Milano-A", "Milano-B"],
        "links": ["link_ab"],
        "total_length_km": 20.0,
        "hops": 1,
        "link_physics": [
            {
                "link_id": "link_ab",
                "length_km": 20.0,
                "port_loss_dB": 0.5,
                "amplifiers": [
                    {"position_km": 0.0, "gain_dB": 13.0, "amp_type": "booster", "att_dB": 0.0},
                    {"position_km": 20.0, "gain_dB": 15.0, "amp_type": "preamp", "att_dB": 0.0},
                ],
            }
        ],
    }

    def test_returns_qot_results(self):
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=[self.FEASIBLE_PATH])
        result = qot_validation_node(state)
        assert result["qot_results"] is not None
        assert len(result["qot_results"]) == 1

    def test_result_has_required_fields(self):
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=[self.FEASIBLE_PATH])
        result = qot_validation_node(state)
        entry = result["qot_results"][0]
        assert "feasible" in entry
        assert "snr_dB" in entry
        assert "power_dBm" in entry
        assert "snr_threshold_dB" in entry
        assert "path" in entry

    def test_snr_is_numeric_float(self):
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=[self.FEASIBLE_PATH])
        result = qot_validation_node(state)
        snr = result["qot_results"][0]["snr_dB"]
        assert isinstance(snr, float)

    def test_missing_link_physics_returns_infeasible(self):
        """Paths without link_physics are infeasible and error is recorded."""
        from src.nodes.qot_validation import qot_validation_node

        bad_path = {"nodes": ["A", "B"], "hops": 1}  # no link_physics
        state = _make_state(candidate_paths=[bad_path])
        result = qot_validation_node(state)
        assert result["qot_results"][0]["feasible"] is False
        assert result["qot_results"][0]["error"] is not None

    def test_handles_empty_candidates(self):
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=[])
        result = qot_validation_node(state)
        assert result["qot_results"] == []

    def test_handles_none_candidates(self):
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=None)
        result = qot_validation_node(state)
        assert result["qot_results"] == []

    def test_message_reports_feasible_count(self):
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(candidate_paths=[self.FEASIBLE_PATH])
        result = qot_validation_node(state)
        msg = result["messages"][0].content
        assert "QoT validation" in msg
        assert "/1" in msg

    def test_custom_min_gsnr_makes_path_infeasible(self):
        """When min_gsnr in pddl_parsed_constraints is 40.0 dB, FEASIBLE_PATH (SNR ~20dB) should evaluate to feasible=False."""
        from src.nodes.qot_validation import qot_validation_node

        state = _make_state(
            candidate_paths=[self.FEASIBLE_PATH],
            pddl_parsed_constraints={"min_gsnr": 40.0},
        )
        result = qot_validation_node(state)
        entry = result["qot_results"][0]
        assert entry["feasible"] is False
        assert entry["snr_threshold_dB"] == 40.0



# ---------------------------------------------------------------------------
# Plan Synthesizer (placeholder — unchanged)
# ---------------------------------------------------------------------------


class TestPlanSynthesizerNode:
    """Test the Plan Synthesizer placeholder."""

    def test_returns_planning_report(self):
        from src.nodes.plan_synthesizer import plan_synthesizer_node

        state = _make_state(
            enriched_intent="Route from A to B",
            qot_results=[{"path": ["A", "B"], "feasible": True, "snr_dB": 15.0, "power_dBm": -10.0}],
        )
        result = plan_synthesizer_node(state)
        assert result["planning_report"] is not None
        assert "Planning Report" in result["planning_report"]

    def test_report_includes_feasible_paths(self):
        from src.nodes.plan_synthesizer import plan_synthesizer_node

        state = _make_state(
            qot_results=[{"path": ["A", "B"], "feasible": True, "snr_dB": 12.0, "power_dBm": -8.0}],
        )
        result = plan_synthesizer_node(state)
        assert "A → B" in result["planning_report"]

    def test_report_handles_no_feasible_paths(self):
        from src.nodes.plan_synthesizer import plan_synthesizer_node

        state = _make_state(qot_results=[])
        result = plan_synthesizer_node(state)
        assert "No feasible paths" in result["planning_report"]

    def test_returns_ai_message(self):
        from src.nodes.plan_synthesizer import plan_synthesizer_node

        state = _make_state(qot_results=[])
        result = plan_synthesizer_node(state)
        assert isinstance(result["messages"][0], AIMessage)
