"""Tests for the RADG — Risk-Adaptive Decision Gate physical risk logic.

Validates the decision function D(U_sem, QoT_valid) from ProblemStatement_v5.
The RADG operates AFTER the Semantic Gate has passed, so it only handles
the QoT feasibility dimension (approve vs. replan).

All tests are offline — no LLM calls.
"""

from __future__ import annotations

import pytest

from src.core.radg import evaluate_radg


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FEASIBLE_RESULT = {
    "path": ["Milano-A", "Milano-B"],
    "feasible": True,
    "snr_dB": 12.5,
    "power_dBm": -14.0,
    "snr_threshold_dB": 8.6,
    "error": None,
}

INFEASIBLE_RESULT = {
    "path": ["Milano-A", "Milano-B", "Milano-C"],
    "feasible": False,
    "snr_dB": 5.0,
    "power_dBm": -25.0,
    "snr_threshold_dB": 8.6,
    "error": None,
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestEvaluateRadg:
    """Validate RADG decisions for all QoT outcome combinations."""

    def test_all_feasible_returns_approve(self) -> None:
        result = evaluate_radg([FEASIBLE_RESULT])
        assert result == "approve"

    def test_all_infeasible_returns_replan(self) -> None:
        result = evaluate_radg([INFEASIBLE_RESULT])
        assert result == "replan"

    def test_mixed_paths_returns_approve(self) -> None:
        """At least one feasible path → approve (best path can be deployed)."""
        result = evaluate_radg([INFEASIBLE_RESULT, FEASIBLE_RESULT])
        assert result == "approve"

    def test_empty_results_returns_replan(self) -> None:
        """No candidate paths at all → replan (nothing to approve)."""
        result = evaluate_radg([])
        assert result == "replan"

    def test_multiple_feasible_returns_approve(self) -> None:
        result = evaluate_radg([FEASIBLE_RESULT, FEASIBLE_RESULT])
        assert result == "approve"

    def test_multiple_infeasible_returns_replan(self) -> None:
        result = evaluate_radg([INFEASIBLE_RESULT, INFEASIBLE_RESULT])
        assert result == "replan"

    def test_return_value_is_string(self) -> None:
        result = evaluate_radg([FEASIBLE_RESULT])
        assert isinstance(result, str)

    def test_result_is_valid_action(self) -> None:
        """RADG must only return valid RADG actions."""
        valid_actions = {"approve", "replan"}
        assert evaluate_radg([FEASIBLE_RESULT]) in valid_actions
        assert evaluate_radg([INFEASIBLE_RESULT]) in valid_actions
        assert evaluate_radg([]) in valid_actions

    def test_error_path_treated_as_infeasible(self) -> None:
        """Paths with errors (feasible=False) are treated as infeasible."""
        error_result = {
            "path": ["A", "B"],
            "feasible": False,
            "snr_dB": 0.0,
            "power_dBm": -99.0,
            "snr_threshold_dB": 0.0,
            "error": "Missing physics data",
        }
        result = evaluate_radg([error_result])
        assert result == "replan"
