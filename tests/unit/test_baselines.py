"""Unit tests for the Sprint 4 evaluation baselines and polymorphic contract.

Tests coverage:
  1. Baseline registry and instantiation (get_baseline, list_baselines, invalid IDs).
  2. BaseBaseline token counting and optical verification helpers.
  3. Baseline A (LLM-Only): Direct prompting, hallucination check, zero HITL.
  4. Baseline B (Always-On HITL): Mandatory interruptions (>= 2 per nominal intent).
  5. Baseline C (Always-Off HITL): Gates bypassed, zero HITL.
  6. Baseline D (Traditional SDON): Zero tokens, 100% manual authoring (N_hitl=1), rejection on ambiguous/adversarial.
  7. Proposed RADG Baseline: Single-pass auto-approval with 0 interrupts on nominal intents.
  8. Polymorphic run_baseline() helper returning standardized BaselineResult schema.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage

from src.core.llm import set_llm
from src.nodes.intent_ingest import IntentSummary
from tests.evaluation.baselines import (
    AlwaysOffHITLBaseline,
    AlwaysOnHITLBaseline,
    BaselineResult,
    LLMOnlyBaseline,
    ProposedRADGBaseline,
    TraditionalSDONBaseline,
    get_baseline,
    list_baselines,
    run_baseline,
)
from tests.evaluation.baselines.llm_only import LLMOnlyOutput


@pytest.fixture(autouse=True)
def _cleanup_llm():
    """Reset LLM singleton after each test."""
    yield
    set_llm(None)  # type: ignore


@pytest.fixture
def sample_nominal_intent() -> dict[str, Any]:
    return {
        "id": "test_nom_01",
        "class": "I_Nominal",
        "intent_text": "Route from Berlin to Frankfurt with at least 12 dB GSNR.",
        "source_node": "Berlin",
        "target_node": "Frankfurt",
        "ground_truth_constraints": {
            "min_gsnr": 12.0,
        },
        "expected_pddl_valid": True,
        "expected_usem_action": "pass",
        "expected_qot_valid": True,
        "expected_radg_action": "approve",
    }


@pytest.fixture
def sample_ambiguous_intent() -> dict[str, Any]:
    return {
        "id": "test_amb_01",
        "class": "II_Ambiguous",
        "intent_text": "Connect Berlin to the north region with high capacity.",
        "source_node": "Berlin",
        "target_node": None,
        "ground_truth_constraints": {},
        "expected_pddl_valid": False,
        "expected_usem_action": "clarify",
        "expected_qot_valid": False,
        "expected_radg_action": "clarify",
    }


@pytest.fixture
def sample_adversarial_intent() -> dict[str, Any]:
    return {
        "id": "test_adv_01",
        "class": "IV_Adversarial",
        "intent_text": "Route from Atlantis to ElDorado with 0 hops.",
        "source_node": "Atlantis",
        "target_node": "ElDorado",
        "ground_truth_constraints": {},
        "expected_pddl_valid": False,
        "expected_usem_action": "clarify",
        "expected_qot_valid": False,
        "expected_radg_action": "clarify",
    }


# ---------------------------------------------------------------------------
# 1. Registry & Dispatch Tests
# ---------------------------------------------------------------------------


class TestBaselineRegistry:
    """Test registry indexing and dynamic baseline instantiation."""

    def test_list_baselines_contains_all_systems(self):
        registered = list_baselines()
        expected = [
            "llm_only",
            "always_on",
            "always_off",
            "traditional_sdon",
            "proposed_radg",
        ]
        for key in expected:
            assert key in registered

    def test_get_baseline_instantiates_correct_classes(self):
        assert isinstance(get_baseline("llm_only"), LLMOnlyBaseline)
        assert isinstance(get_baseline("always_on"), AlwaysOnHITLBaseline)
        assert isinstance(get_baseline("always_off"), AlwaysOffHITLBaseline)
        assert isinstance(get_baseline("traditional_sdon"), TraditionalSDONBaseline)
        assert isinstance(get_baseline("proposed_radg"), ProposedRADGBaseline)

    def test_get_baseline_raises_key_error_on_unknown(self):
        with pytest.raises(KeyError, match="Unknown baseline_id"):
            get_baseline("non_existent_baseline")


# ---------------------------------------------------------------------------
# 2. Base Utilities Tests
# ---------------------------------------------------------------------------


class TestBaseBaselineUtilities:
    """Test shared token counting and optical physics verification in BaseBaseline."""

    def test_count_tokens(self):
        baseline = get_baseline("traditional_sdon")
        assert baseline.count_tokens("") == 0
        assert baseline.count_tokens("Hello world from optical network") > 0

    def test_verify_optical_path_valid(self):
        baseline = get_baseline("traditional_sdon")
        # Berlin <-> Hannover <-> Frankfurt is a connected path in Nobel-Germany
        path = ["Berlin", "Hannover", "Frankfurt"]
        snr, feasible = baseline.verify_optical_path(path, min_gsnr_dB=10.0)
        assert snr is not None
        assert snr > 0
        assert feasible is True

    def test_verify_optical_path_invalid_short(self):
        baseline = get_baseline("traditional_sdon")
        snr, feasible = baseline.verify_optical_path(["Berlin"], min_gsnr_dB=10.0)
        assert snr is None
        assert feasible is False


# ---------------------------------------------------------------------------
# 3. Baseline D: Traditional SDON / PCE Tests
# ---------------------------------------------------------------------------


class TestTraditionalSDONBaseline:
    """Validate Baseline D (Traditional SDON / PCE without LLM)."""

    def test_traditional_sdon_nominal_intent(self, sample_nominal_intent):
        baseline = get_baseline("traditional_sdon")
        result = baseline.run(sample_nominal_intent)

        assert result["baseline_id"] == "traditional_sdon"
        assert result["action"] == "approve"
        assert result["qot_feasible"] is True
        assert result["prompt_tokens"] == 0
        assert result["completion_tokens"] == 0
        assert result["hitl_interrupts"] == 1  # 100% manual authoring setup
        assert result["selected_path"] is not None
        assert result["selected_path"][0] == "Berlin"
        assert result["selected_path"][-1] == "Frankfurt"

    def test_traditional_sdon_ambiguous_intent(self, sample_ambiguous_intent):
        baseline = get_baseline("traditional_sdon")
        result = baseline.run(sample_ambiguous_intent)

        assert result["action"] == "replan"
        assert result["selected_path"] is None
        assert "underspecified" in (result["planning_report"] or "")

    def test_traditional_sdon_adversarial_intent(self, sample_adversarial_intent):
        baseline = get_baseline("traditional_sdon")
        result = baseline.run(sample_adversarial_intent)

        assert result["action"] == "replan"
        assert result["selected_path"] is None


# ---------------------------------------------------------------------------
# 4. Baseline A: Monolithic LLM Tests
# ---------------------------------------------------------------------------


class TestLLMOnlyBaseline:
    """Validate Baseline A (LLM-Only / Direct Prompting)."""

    def test_llm_only_with_structured_mock(self, sample_nominal_intent):
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = LLMOnlyOutput(
            source_node="Berlin",
            destination_node="Frankfurt",
            route=["Berlin", "Hannover", "Frankfurt"],
            estimated_gsnr_dB=18.5,
            action="approve",
            reasoning="Valid shortest path along German backbone",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        set_llm(mock_llm)

        baseline = get_baseline("llm_only")
        result = baseline.run(sample_nominal_intent)

        assert result["baseline_id"] == "llm_only"
        assert result["action"] == "approve"
        assert result["hitl_interrupts"] == 0
        assert result["prompt_tokens"] > 50  # Contains full topology
        assert result["selected_path"] == ["Berlin", "Hannover", "Frankfurt"]
        assert result["computed_gsnr_dB"] is not None
        assert result["qot_feasible"] is True

    def test_llm_only_hallucinated_infeasible_path(self, sample_nominal_intent):
        # LLM outputs a disconnected route
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = LLMOnlyOutput(
            source_node="Berlin",
            destination_node="Frankfurt",
            route=["Berlin", "Munich", "Frankfurt"],  # Might fail or be disconnected
            estimated_gsnr_dB=30.0,  # Hallucinated impossible GSNR
            action="approve",
            reasoning="Hallucinated physics",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        set_llm(mock_llm)

        baseline = get_baseline("llm_only")
        result = baseline.run(sample_nominal_intent)

        assert result["action"] == "approve"
        assert result["hitl_interrupts"] == 0


# ---------------------------------------------------------------------------
# 5. Baseline B: Always-On HITL Tests
# ---------------------------------------------------------------------------


class TestAlwaysOnHITLBaseline:
    """Validate Baseline B (Mandatory human intervention at every stage)."""

    def test_always_on_nominal_triggers_multiple_interrupts(
        self, sample_nominal_intent
    ):
        valid_pddl = (
            "(define (problem route-berlin-frankfurt)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Frankfurt Hannover - node)\n"
            "  (:init (connected Berlin Hannover) (connected Hannover Frankfurt))\n"
            "  (:goal (and (route Berlin Frankfurt) (min-gsnr 12.0)))\n"
            ")"
        )
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Route from Berlin to Frankfurt with min GSNR 12 dB",
            source_node="Berlin",
            target_node="Frankfurt",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_llm.invoke.return_value = AIMessage(content=valid_pddl)
        set_llm(mock_llm)

        baseline = get_baseline("always_on")
        result = baseline.run(sample_nominal_intent)

        assert result["baseline_id"] == "always_on"
        assert result["hitl_interrupts"] >= 2  # Mandatory Phase 3 & Phase 6
        assert result["action"] == "approve"
        assert result["qot_feasible"] is True

    def test_always_on_ambiguous_intent_clarifies(self, sample_ambiguous_intent):
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Connect Berlin to north",
            source_node="Berlin",
            target_node=None,
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_llm.invoke.return_value = AIMessage(
            content="(define (problem incomplete))"
        )
        set_llm(mock_llm)

        baseline = get_baseline("always_on")
        result = baseline.run(sample_ambiguous_intent)

        assert result["action"] == "clarify"
        assert result["hitl_interrupts"] >= 1


# ---------------------------------------------------------------------------
# 6. Baseline C: Always-Off HITL Tests
# ---------------------------------------------------------------------------


class TestAlwaysOffHITLBaseline:
    """Validate Baseline C (Decision gates bypassed, strictly zero interrupts)."""

    def test_always_off_bypasses_gates_zero_hitl(self, sample_nominal_intent):
        valid_pddl = (
            "(define (problem route-berlin-frankfurt)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Frankfurt Hannover - node)\n"
            "  (:init (connected Berlin Hannover) (connected Hannover Frankfurt))\n"
            "  (:goal (and (route Berlin Frankfurt) (min-gsnr 12.0)))\n"
            ")"
        )
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Route from Berlin to Frankfurt with min GSNR 12 dB",
            source_node="Berlin",
            target_node="Frankfurt",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_llm.invoke.return_value = AIMessage(content=valid_pddl)
        set_llm(mock_llm)

        baseline = get_baseline("always_off")
        result = baseline.run(sample_nominal_intent)

        assert result["baseline_id"] == "always_off"
        assert result["hitl_interrupts"] == 0  # Strictly zero
        assert result["metadata"].get("gates_bypassed") is True


# ---------------------------------------------------------------------------
# 7. Proposed RADG Baseline Tests
# ---------------------------------------------------------------------------


class TestProposedRADGBaseline:
    """Validate Proposed Architecture (Neurosymbolic RADG with selective HITL)."""

    def test_proposed_radg_nominal_zero_interrupts(self, sample_nominal_intent):
        valid_pddl = (
            "(define (problem route-berlin-frankfurt)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Frankfurt Hannover - node)\n"
            "  (:init (connected Berlin Hannover) (connected Hannover Frankfurt))\n"
            "  (:goal (and (route Berlin Frankfurt) (min-gsnr 12.0)))\n"
            ")"
        )
        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Route from Berlin to Frankfurt with min GSNR 12 dB",
            source_node="Berlin",
            target_node="Frankfurt",
        )
        mock_llm.with_structured_output.return_value = mock_structured

        def _dispatcher(messages, *args, **kwargs):
            first_msg = messages[0] if messages else None
            system_prompt = getattr(first_msg, "content", "")
            if "PDDL Parser module" in system_prompt:
                return AIMessage(content=valid_pddl)
            elif "Reverse Prompting module" in system_prompt:
                return AIMessage(
                    content="Route from Berlin to Frankfurt with min GSNR 12.0 dB"
                )
            elif "semantic similarity evaluator" in system_prompt:
                return AIMessage(content="0.05")
            return AIMessage(content="OK")

        mock_llm.invoke.side_effect = _dispatcher
        set_llm(mock_llm)

        baseline = get_baseline("proposed_radg")
        result = baseline.run(sample_nominal_intent)

        assert result["baseline_id"] == "proposed_radg"
        assert result["action"] == "approve"
        assert (
            result["hitl_interrupts"] == 0
        )  # Selective HITL: 0 interrupts on nominal intent
        assert result["qot_feasible"] is True
        assert result["selected_path"] is not None


# ---------------------------------------------------------------------------
# 8. Polymorphic Runner Contract Verification
# ---------------------------------------------------------------------------


class TestPolymorphicContract:
    """Ensure run_baseline() helper returns identical dictionary keys across all baselines."""

    @pytest.mark.parametrize(
        "baseline_id",
        ["traditional_sdon", "llm_only", "always_on", "always_off", "proposed_radg"],
    )
    def test_standardized_keys_present_in_result(
        self, baseline_id, sample_nominal_intent
    ):
        valid_pddl = (
            "(define (problem route-berlin-frankfurt)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Frankfurt Hannover - node)\n"
            "  (:init (connected Berlin Hannover) (connected Hannover Frankfurt))\n"
            "  (:goal (and (route Berlin Frankfurt) (min-gsnr 12.0)))\n"
            ")"
        )
        mock_llm = MagicMock()

        def _structured_dispatcher(schema, *args, **kwargs):
            mock_struct = MagicMock()
            if schema == IntentSummary:
                mock_struct.invoke.return_value = IntentSummary(
                    summary="Route from Berlin to Frankfurt with min GSNR 12 dB",
                    source_node="Berlin",
                    target_node="Frankfurt",
                )
            else:
                mock_struct.invoke.return_value = LLMOnlyOutput(
                    source_node="Berlin",
                    destination_node="Frankfurt",
                    route=["Berlin", "Hannover", "Frankfurt"],
                    estimated_gsnr_dB=15.0,
                    action="approve",
                )
            return mock_struct

        mock_llm.with_structured_output.side_effect = _structured_dispatcher

        def _dispatcher(messages, *args, **kwargs):
            first_msg = messages[0] if messages else None
            system_prompt = getattr(first_msg, "content", "")
            if "PDDL Parser module" in system_prompt:
                return AIMessage(content=valid_pddl)
            elif "Reverse Prompting module" in system_prompt:
                return AIMessage(
                    content="Route from Berlin to Frankfurt with min GSNR 12.0 dB"
                )
            elif "semantic similarity evaluator" in system_prompt:
                return AIMessage(content="0.05")
            return AIMessage(content=valid_pddl)

        mock_llm.invoke.side_effect = _dispatcher
        set_llm(mock_llm)

        result: BaselineResult = run_baseline(baseline_id, sample_nominal_intent)

        required_keys = [
            "intent_id",
            "baseline_id",
            "action",
            "hitl_interrupts",
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "execution_time_s",
        ]
        for key in required_keys:
            assert key in result, (
                f"Key '{key}' missing from baseline {baseline_id} output"
            )
