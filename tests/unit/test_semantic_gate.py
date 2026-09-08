"""Tests for the Semantic Gate — pure decision logic for U_sem computation.

Validates the mathematical formulation from ProblemStatement_v5:
  U_sem = 1              if v_struct = 0 (structural failure)
  U_sem = d_sem          if v_struct = 1 (semantic divergence)

All tests are offline — no LLM calls.
"""

from __future__ import annotations

import pytest

from src.core.semantic_gate import compute_usem, evaluate_semantic_gate


class TestComputeUsem:
    """Validate U_sem = f(v_struct, d_sem) piecewise formula."""

    def test_structural_failure_returns_one(self) -> None:
        """If PDDL CFG validation fails, U_sem must be 1.0 regardless of d_sem."""
        assert compute_usem(v_struct=False, d_sem=0.0) == pytest.approx(1.0)

    def test_structural_failure_ignores_d_sem(self) -> None:
        """d_sem value is irrelevant when v_struct is False."""
        assert compute_usem(v_struct=False, d_sem=0.1) == pytest.approx(1.0)
        assert compute_usem(v_struct=False, d_sem=0.9) == pytest.approx(1.0)

    def test_structural_pass_uses_d_sem(self) -> None:
        """If PDDL is structurally valid, U_sem = d_sem."""
        assert compute_usem(v_struct=True, d_sem=0.2) == pytest.approx(0.2)

    def test_structural_pass_zero_divergence(self) -> None:
        """Perfect semantic agreement gives U_sem = 0.0."""
        assert compute_usem(v_struct=True, d_sem=0.0) == pytest.approx(0.0)

    def test_structural_pass_full_divergence(self) -> None:
        """Full divergence gives U_sem = 1.0."""
        assert compute_usem(v_struct=True, d_sem=1.0) == pytest.approx(1.0)

    def test_d_sem_at_boundary(self) -> None:
        """d_sem = 0.3 returns 0.3 (at the threshold, should be used as-is)."""
        assert compute_usem(v_struct=True, d_sem=0.3) == pytest.approx(0.3)

    def test_result_is_float(self) -> None:
        result = compute_usem(v_struct=True, d_sem=0.5)
        assert isinstance(result, float)

    def test_result_is_in_unit_interval(self) -> None:
        for d in [0.0, 0.25, 0.5, 0.75, 1.0]:
            result = compute_usem(v_struct=True, d_sem=d)
            assert 0.0 <= result <= 1.0


class TestEvaluateSemanticGate:
    """Validate semantic gate pass/fail with tau_sem = 0.3."""

    def test_usem_zero_passes(self) -> None:
        """U_sem = 0.0 is well below threshold — gate must pass."""
        assert evaluate_semantic_gate(usem=0.0) is True

    def test_usem_below_threshold_passes(self) -> None:
        """U_sem = 0.29 < 0.3 — gate must pass."""
        assert evaluate_semantic_gate(usem=0.29) is True

    def test_usem_exactly_at_threshold_passes(self) -> None:
        """U_sem = 0.3 == tau_sem — boundary is inclusive (pass)."""
        assert evaluate_semantic_gate(usem=0.3) is True

    def test_usem_above_threshold_fails(self) -> None:
        """U_sem = 0.31 > 0.3 — gate must fail (clarify required)."""
        assert evaluate_semantic_gate(usem=0.31) is False

    def test_usem_one_fails(self) -> None:
        """U_sem = 1.0 (structural failure) — gate must fail."""
        assert evaluate_semantic_gate(usem=1.0) is False

    def test_custom_tau_sem(self) -> None:
        """Custom tau_sem is respected."""
        assert evaluate_semantic_gate(usem=0.5, tau_sem=0.6) is True
        assert evaluate_semantic_gate(usem=0.7, tau_sem=0.6) is False

    def test_returns_bool(self) -> None:
        result = evaluate_semantic_gate(usem=0.2)
        assert isinstance(result, bool)


class TestSemanticGateNode:
    """Validate semantic_gate_node behavior with refinement history and prompt instructions."""

    def test_gate_evaluates_with_refinement_history_included(self) -> None:
        """When refinement_history is present in state, it must be included in the evaluator prompt."""
        from unittest.mock import MagicMock, patch
        from langchain_core.messages import AIMessage
        from src.nodes.semantic_gate_node import semantic_gate_node

        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="0.10")

        state = {
            "pddl_valid": True,
            "enriched_intent": "Intent: Route Berlin to Frankfurt",
            "hitl_reconstruction": "I understand you want to route from Berlin to Frankfurt avoiding Munich with 12 dB GSNR.",
            "refinement_history": ["Avoid Munich", "Ensure min GSNR is 12 dB"],
        }

        with patch("src.nodes.semantic_gate_node.get_llm", return_value=mock_llm):
            result = semantic_gate_node(state)

        assert result["usem_passed"] is True
        assert result["usem_score"] == pytest.approx(0.10)

        # Inspect the message sent to the evaluator LLM
        mock_llm.invoke.assert_called_once()
        call_messages = mock_llm.invoke.call_args[0][0]
        human_msg_content = call_messages[1].content
        assert "Avoid Munich" in human_msg_content
        assert "Ensure min GSNR is 12 dB" in human_msg_content
