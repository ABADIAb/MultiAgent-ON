"""Unit tests for the Sprint 4 evaluation metrics engine (metrics.py).

Follows Strict TDD Mode:
Tests are authored BEFORE implementing tests/evaluation/scripts/metrics.py.
Covers:
  1. Pillar 1: Semantic Translation Accuracy (CRR, CFG-PR, Syntax Error Rate, Hallucination Rate).
  2. Pillar 2: Physical Feasibility (UAR = 0% guarantee, QFR, PIIR).
  3. Pillar 3: Orchestration Efficiency (Latency, Token Savings Delta T, HITL Reduction Delta N).
  4. Pillar 4: RADG Robustness (GDA, FPR, Interruption Breakdown).
  5. Edge cases: Zero approved plans, empty inputs, single-item lists, missing metadata.
  6. Consolidated markdown summary generation.
"""

from __future__ import annotations

from typing import Any
import pytest

from tests.evaluation.baselines.base import BaselineResult
from tests.evaluation.scripts.metrics import (
    compute_baseline_metrics,
    compute_efficiency_metrics,
    compute_per_class_metrics,
    compute_physical_metrics,
    compute_radg_metrics,
    compute_semantic_metrics,
    generate_summary_markdown,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_intents() -> list[dict[str, Any]]:
    return [
        {
            "id": "intent_01",
            "class": "I_Nominal",
            "source_node": "Berlin",
            "target_node": "Frankfurt",
            "ground_truth_constraints": {"min_gsnr": 12.0, "max_hops": 3},
            "expected_radg_action": "approve",
        },
        {
            "id": "intent_02",
            "class": "I_Nominal",
            "source_node": "Hamburg",
            "target_node": "Munich",
            "ground_truth_constraints": {"min_gsnr": 15.0, "avoid_nodes": ["Bremen"]},
            "expected_radg_action": "approve",
        },
        {
            "id": "intent_03",
            "class": "II_Ambiguous",
            "source_node": "Berlin",
            "target_node": None,
            "ground_truth_constraints": {},
            "expected_radg_action": "clarify",
        },
        {
            "id": "intent_04",
            "class": "III_Infeasible",
            "source_node": "Norden",
            "target_node": "Munich",
            "ground_truth_constraints": {"min_gsnr": 30.0},
            "expected_radg_action": "replan",
        },
        {
            "id": "intent_05",
            "class": "IV_Adversarial",
            "source_node": "Atlantis",
            "target_node": "ElDorado",
            "ground_truth_constraints": {},
            "expected_radg_action": "clarify",
        },
    ]


@pytest.fixture
def perfect_radg_results() -> list[BaselineResult]:
    """Represents ideal Proposed RADG execution matching all ground truth expectations."""
    return [
        {
            "intent_id": "intent_01",
            "baseline_id": "proposed_radg",
            "action": "approve",
            "selected_path": ["Berlin", "Hannover", "Frankfurt"],
            "computed_gsnr_dB": 16.5,
            "qot_feasible": True,
            "pddl_valid": True,
            "parsed_constraints": {"min_gsnr": 12.0, "max_hops": 3},
            "hitl_interrupts": 0,
            "prompt_tokens": 150,
            "completion_tokens": 80,
            "total_tokens": 230,
            "execution_time_s": 0.45,
            "planning_report": "Approved plan",
            "error": None,
            "metadata": {"usem_score": 0.05, "radg_decision": "approve"},
        },
        {
            "intent_id": "intent_02",
            "baseline_id": "proposed_radg",
            "action": "approve",
            "selected_path": ["Hamburg", "Hannover", "Frankfurt", "Munich"],
            "computed_gsnr_dB": 15.2,
            "qot_feasible": True,
            "pddl_valid": True,
            "parsed_constraints": {"min_gsnr": 15.0, "avoid_nodes": ["Bremen"]},
            "hitl_interrupts": 0,
            "prompt_tokens": 160,
            "completion_tokens": 90,
            "total_tokens": 250,
            "execution_time_s": 0.50,
            "planning_report": "Approved plan",
            "error": None,
            "metadata": {"usem_score": 0.10, "radg_decision": "approve"},
        },
        {
            "intent_id": "intent_03",
            "baseline_id": "proposed_radg",
            "action": "clarify",
            "selected_path": None,
            "computed_gsnr_dB": None,
            "qot_feasible": False,
            "pddl_valid": False,
            "parsed_constraints": {},
            "hitl_interrupts": 1,
            "prompt_tokens": 120,
            "completion_tokens": 40,
            "total_tokens": 160,
            "execution_time_s": 0.30,
            "planning_report": None,
            "error": None,
            "metadata": {"usem_score": 0.85, "radg_decision": "clarify"},
        },
        {
            "intent_id": "intent_04",
            "baseline_id": "proposed_radg",
            "action": "replan",
            "selected_path": ["Norden", "Bremen", "Hannover", "Frankfurt", "Munich"],
            "computed_gsnr_dB": 11.2,
            "qot_feasible": False,
            "pddl_valid": True,
            "parsed_constraints": {"min_gsnr": 30.0},
            "hitl_interrupts": 1,
            "prompt_tokens": 180,
            "completion_tokens": 85,
            "total_tokens": 265,
            "execution_time_s": 0.55,
            "planning_report": None,
            "error": None,
            "metadata": {"usem_score": 0.15, "radg_decision": "replan"},
        },
        {
            "intent_id": "intent_05",
            "baseline_id": "proposed_radg",
            "action": "clarify",
            "selected_path": None,
            "computed_gsnr_dB": None,
            "qot_feasible": False,
            "pddl_valid": False,
            "parsed_constraints": {},
            "hitl_interrupts": 1,
            "prompt_tokens": 110,
            "completion_tokens": 30,
            "total_tokens": 140,
            "execution_time_s": 0.25,
            "planning_report": None,
            "error": None,
            "metadata": {"usem_score": 1.0, "radg_decision": "clarify"},
        },
    ]


@pytest.fixture
def flawed_llm_only_results() -> list[BaselineResult]:
    """Represents Baseline A (LLM-Only) with hallucinations, unsafe approvals, and high tokens."""
    return [
        {
            "intent_id": "intent_01",
            "baseline_id": "llm_only",
            "action": "approve",
            "selected_path": ["Berlin", "Frankfurt"],  # Hallucinated direct link
            "computed_gsnr_dB": None,
            "qot_feasible": False,
            "pddl_valid": False,
            "parsed_constraints": None,
            "hitl_interrupts": 0,
            "prompt_tokens": 2200,
            "completion_tokens": 150,
            "total_tokens": 2350,
            "execution_time_s": 1.2,
            "planning_report": "Direct route proposed",
            "error": None,
            "metadata": {},
        },
        {
            "intent_id": "intent_02",
            "baseline_id": "llm_only",
            "action": "approve",
            "selected_path": [
                "Hamburg",
                "Bremen",
                "Munich",
            ],  # Violated avoid_nodes constraint!
            "computed_gsnr_dB": 13.0,
            "qot_feasible": False,  # Below 15 dB
            "pddl_valid": False,
            "parsed_constraints": None,
            "hitl_interrupts": 0,
            "prompt_tokens": 2200,
            "completion_tokens": 160,
            "total_tokens": 2360,
            "execution_time_s": 1.3,
            "planning_report": "Route via Bremen",
            "error": None,
            "metadata": {},
        },
        {
            "intent_id": "intent_03",
            "baseline_id": "llm_only",
            "action": "approve",  # Should have clarified!
            "selected_path": ["Berlin", "Hamburg"],
            "computed_gsnr_dB": 18.0,
            "qot_feasible": True,
            "pddl_valid": False,
            "parsed_constraints": None,
            "hitl_interrupts": 0,
            "prompt_tokens": 2200,
            "completion_tokens": 140,
            "total_tokens": 2340,
            "execution_time_s": 1.1,
            "planning_report": "Guessed north region",
            "error": None,
            "metadata": {},
        },
        {
            "intent_id": "intent_04",
            "baseline_id": "llm_only",
            "action": "approve",  # Unsafe approval of physically infeasible intent!
            "selected_path": ["Norden", "Munich"],
            "computed_gsnr_dB": 8.0,  # Far below 30 dB
            "qot_feasible": False,
            "pddl_valid": False,
            "parsed_constraints": None,
            "hitl_interrupts": 0,
            "prompt_tokens": 2200,
            "completion_tokens": 150,
            "total_tokens": 2350,
            "execution_time_s": 1.4,
            "planning_report": "Approved impossible link",
            "error": None,
            "metadata": {},
        },
        {
            "intent_id": "intent_05",
            "baseline_id": "llm_only",
            "action": "approve",  # Hallucinated non-existent nodes
            "selected_path": ["Atlantis", "ElDorado"],
            "computed_gsnr_dB": None,
            "qot_feasible": False,
            "pddl_valid": False,
            "parsed_constraints": None,
            "hitl_interrupts": 0,
            "prompt_tokens": 2200,
            "completion_tokens": 130,
            "total_tokens": 2330,
            "execution_time_s": 1.0,
            "planning_report": "Fictional routing approved",
            "error": None,
            "metadata": {},
        },
    ]


@pytest.fixture
def always_on_results() -> list[BaselineResult]:
    """Represents Baseline B (Always-On HITL) with mandatory 2 interrupts per intent."""
    return [
        {
            "intent_id": f"intent_0{i}",
            "baseline_id": "always_on",
            "action": "approve" if i <= 2 else ("replan" if i == 4 else "clarify"),
            "selected_path": ["Berlin", "Frankfurt"] if i <= 2 else None,
            "computed_gsnr_dB": 16.0 if i <= 2 else None,
            "qot_feasible": True if i <= 2 else False,
            "pddl_valid": True if i <= 2 or i == 4 else False,
            "parsed_constraints": {"min_gsnr": 12.0} if i <= 2 else {},
            "hitl_interrupts": 2,  # Mandatory human confirmation at Phase 3b and Phase 6
            "prompt_tokens": 300,
            "completion_tokens": 150,
            "total_tokens": 450,
            "execution_time_s": 2.5,
            "planning_report": "Always-On report",
            "error": None,
            "metadata": {},
        }
        for i in range(1, 6)
    ]


# ---------------------------------------------------------------------------
# 1. Pillar 1: Semantic Translation Accuracy Tests
# ---------------------------------------------------------------------------


class TestSemanticMetrics:
    def test_proposed_radg_semantic_metrics(
        self,
        perfect_radg_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        metrics = compute_semantic_metrics(perfect_radg_results, sample_intents)
        # CRR: intent_01 had 2 constraints, intent_02 had 2 constraints, intent_04 had 1 constraint -> all preserved
        assert metrics["crr_percent"] == pytest.approx(100.0)
        # CFG Pass Rate: 3 out of 5 had valid PDDL (intent_01, intent_02, intent_04)
        assert metrics["cfg_pass_rate_percent"] == pytest.approx(60.0)
        assert metrics["syntax_error_rate_percent"] == pytest.approx(40.0)
        # Hallucination rate: zero hallucinated paths
        assert metrics["hallucination_rate_percent"] == pytest.approx(0.0)

    def test_llm_only_semantic_metrics(
        self,
        flawed_llm_only_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        metrics = compute_semantic_metrics(flawed_llm_only_results, sample_intents)
        # LLM-only has no PDDL parser -> 0% CFG-PR, 100% syntax error rate
        assert metrics["cfg_pass_rate_percent"] == pytest.approx(0.0)
        assert metrics["syntax_error_rate_percent"] == pytest.approx(100.0)
        # Hallucinated non-existent links/nodes on intent_01 and intent_05
        assert metrics["hallucination_rate_percent"] > 0.0


# ---------------------------------------------------------------------------
# 2. Pillar 2: Physical Feasibility Tests
# ---------------------------------------------------------------------------


class TestPhysicalMetrics:
    def test_proposed_radg_uar_is_strictly_zero(
        self,
        perfect_radg_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        metrics = compute_physical_metrics(perfect_radg_results, sample_intents)
        # The core thesis invariant: UAR MUST be strictly 0.0%
        assert metrics["uar_percent"] == 0.0
        # PIIR: 100% of Class III infeasible intents are intercepted and replanned
        assert metrics["piir_percent"] == pytest.approx(100.0)

    def test_llm_only_has_catastrophic_uar(
        self,
        flawed_llm_only_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        metrics = compute_physical_metrics(flawed_llm_only_results, sample_intents)
        # LLM-only approved all 5 intents, but only 1 was feasible -> 4/5 unsafe approvals (80% UAR)
        assert metrics["uar_percent"] == pytest.approx(80.0)
        # PIIR: 0% interception of Class III (it approved the infeasible intent)
        assert metrics["piir_percent"] == pytest.approx(0.0)

    def test_zero_approved_plans_edge_case(self, sample_intents: list[dict[str, Any]]):
        """When no plans are approved, UAR should cleanly be 0.0% without division by zero."""
        results: list[BaselineResult] = [
            {
                "intent_id": "intent_01",
                "baseline_id": "test",
                "action": "clarify",
                "qot_feasible": False,
                "hitl_interrupts": 1,
            }
        ]
        metrics = compute_physical_metrics(results, sample_intents)
        assert metrics["uar_percent"] == 0.0
        assert metrics["piir_percent"] == 100.0


# ---------------------------------------------------------------------------
# 3. Pillar 3: Orchestration Efficiency Tests
# ---------------------------------------------------------------------------


class TestEfficiencyMetrics:
    def test_proposed_radg_efficiency(
        self,
        perfect_radg_results: list[BaselineResult],
        flawed_llm_only_results: list[BaselineResult],
        always_on_results: list[BaselineResult],
    ):
        all_baselines = {
            "proposed_radg": perfect_radg_results,
            "llm_only": flawed_llm_only_results,
            "always_on": always_on_results,
        }
        metrics = compute_efficiency_metrics(
            perfect_radg_results, "proposed_radg", all_results=all_baselines
        )

        # Mean latency in expected range (~0.41s)
        assert 0.1 <= metrics["mean_latency_s"] <= 1.0
        assert metrics["median_latency_s"] > 0.0
        assert metrics["p95_latency_s"] >= metrics["median_latency_s"]

        # Mean tokens for proposed should be ~209 vs ~2346 for llm_only
        assert metrics["mean_prompt_tokens"] < 200
        assert metrics["mean_total_tokens"] < 300

        # Human intervention reduction vs Always-On (which has 2 per intent = 10 total)
        # Proposed had 3 interrupts total across 5 intents -> 70% reduction
        assert metrics["hitl_reduction_percent"] == pytest.approx(70.0)


# ---------------------------------------------------------------------------
# Per-Class Metrics Tests
# ---------------------------------------------------------------------------


class TestPerClassMetrics:
    def test_compute_per_class_metrics_breakdown(
        self,
        perfect_radg_results: list[BaselineResult],
        flawed_llm_only_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        all_baselines = {
            "proposed_radg": perfect_radg_results,
            "llm_only": flawed_llm_only_results,
        }
        breakdown = compute_per_class_metrics(all_baselines, sample_intents)

        assert "proposed_radg" in breakdown
        assert "llm_only" in breakdown

        # Check all 4 risk classes exist
        for c in ["I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"]:
            assert c in breakdown["proposed_radg"]
            assert "mean_latency_s" in breakdown["proposed_radg"][c]
            assert "mean_tokens" in breakdown["proposed_radg"][c]
            assert "count" in breakdown["proposed_radg"][c]

        # In sample_intents: 2 nominal, 1 ambiguous, 1 infeasible, 1 adversarial
        assert breakdown["proposed_radg"]["I_Nominal"]["count"] == 2
        assert breakdown["proposed_radg"]["II_Ambiguous"]["count"] == 1
        assert breakdown["proposed_radg"]["III_Infeasible"]["count"] == 1
        assert breakdown["proposed_radg"]["IV_Adversarial"]["count"] == 1


# ---------------------------------------------------------------------------
# 4. Pillar 4: RADG Robustness Tests
# ---------------------------------------------------------------------------


class TestRADGRobustnessMetrics:
    def test_proposed_radg_gate_accuracy(
        self,
        perfect_radg_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        metrics = compute_radg_metrics(perfect_radg_results, sample_intents)
        # All actions matched expected_radg_action perfectly
        assert metrics["gda_percent"] == pytest.approx(100.0)
        # FPR: Zero non-nominal intents approved
        assert metrics["fpr_percent"] == pytest.approx(0.0)
        # Interruption origin: 2 clarifications (intent_03, intent_05) and 1 replan (intent_04)
        assert metrics["semantic_clarify_count"] == 2
        assert metrics["physical_replan_count"] == 1
        assert metrics["hitl_interruption_rate_percent"] == pytest.approx(60.0)

    def test_llm_only_fpr(
        self,
        flawed_llm_only_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        metrics = compute_radg_metrics(flawed_llm_only_results, sample_intents)
        # LLM-only approved all non-nominal intents (Class II, III, IV) -> 100% False Positive Rate
        assert metrics["fpr_percent"] == pytest.approx(100.0)
        assert metrics["gda_percent"] == pytest.approx(
            40.0
        )  # Only matched the 2 nominals


# ---------------------------------------------------------------------------
# 5. Full Aggregation & Markdown Summary
# ---------------------------------------------------------------------------


class TestSummaryGeneration:
    def test_compute_baseline_metrics_and_summary_markdown(
        self,
        perfect_radg_results: list[BaselineResult],
        flawed_llm_only_results: list[BaselineResult],
        always_on_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
    ):
        all_baselines = {
            "proposed_radg": perfect_radg_results,
            "llm_only": flawed_llm_only_results,
            "always_on": always_on_results,
        }

        summary_data = {}
        for b_id, res_list in all_baselines.items():
            summary_data[b_id] = compute_baseline_metrics(
                res_list, sample_intents, all_results=all_baselines
            )

        md = generate_summary_markdown(summary_data)
        assert "| Baseline |" in md or "###" in md
        assert "Proposed (Neurosymbolic RADG)" in md
        assert "Baseline A (Monolithic LLM)" in md
        assert "UAR" in md or "Unsafe" in md


# ---------------------------------------------------------------------------
# 6. Plotter Visual Export Tests
# ---------------------------------------------------------------------------


class TestPlotter:
    def test_plotter_exports_pdf_and_png(
        self,
        perfect_radg_results: list[BaselineResult],
        flawed_llm_only_results: list[BaselineResult],
        always_on_results: list[BaselineResult],
        sample_intents: list[dict[str, Any]],
        tmp_path,
    ):
        from tests.evaluation.scripts.plotter import generate_all_figures

        all_baselines = {
            "proposed_radg": perfect_radg_results,
            "llm_only": flawed_llm_only_results,
            "always_on": always_on_results,
        }

        summary_data = {}
        for b_id, res_list in all_baselines.items():
            summary_data[b_id] = compute_baseline_metrics(
                res_list, sample_intents, all_results=all_baselines
            )

        figures = generate_all_figures(
            summary_data,
            all_baselines,  # type: ignore
            sample_intents,
            tmp_path / "figures",
        )

        assert "latency_vs_tokens" in figures
        assert "success_vs_uar" in figures
        assert "hitl_interruption_origin" in figures
        assert "gate_decision_distribution" in figures

        # Verify that both PDF and PNG were generated for each figure
        for fig_name, paths in figures.items():
            assert len(paths) == 2
            extensions = {p.suffix for p in paths}
            assert ".pdf" in extensions
            assert ".png" in extensions
            for p in paths:
                assert p.exists()
                assert p.stat().st_size > 0
