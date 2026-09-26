"""Unit tests for comparative evaluation baselines and common metrics (Strict TDD)."""

from __future__ import annotations

import pytest

from tests.evaluation.baselines.always_on_hitl import (
    compile_always_on_graph,
)
from tests.evaluation.baselines.always_on_hitl.graph import (
    always_on_semantic_gate_node,
    build_always_on_graph,
)
from tests.evaluation.baselines.common.metrics import (
    compute_constraint_retention,
    compute_pillar_metrics,
)
from tests.evaluation.baselines.common.runner import check_action_success
from tests.evaluation.baselines.llm_only import (
    compile_llm_only_graph,
)
from tests.evaluation.baselines.llm_only.graph import (
    build_llm_only_graph,
    bypassed_semantic_gate_node,
    controller_surrogate_radg_node,
)
from tests.evaluation.baselines.proposed_radg import (
    compile_proposed_graph,
)


class TestBaselineGraphCompilation:
    """Verify that all baseline graphs compile with valid StateGraph topology."""

    def test_proposed_radg_compiles(self) -> None:
        graph = compile_proposed_graph()
        assert graph is not None

    def test_always_on_hitl_compiles(self) -> None:
        builder = build_always_on_graph()
        assert "semantic_gate" in builder.nodes
        assert "hitl_clarify" in builder.nodes
        graph = compile_always_on_graph()
        assert graph is not None

    def test_llm_only_compiles(self) -> None:
        builder = build_llm_only_graph()
        assert "semantic_gate" in builder.nodes
        # In LLM-Only, hitl_clarify node is not present in graph topology
        assert "hitl_clarify" not in builder.nodes
        graph = compile_llm_only_graph()
        assert graph is not None


class TestAlwaysOnHITLNodes:
    """Verify node logic for Always-On HITL baseline."""

    def test_always_on_semantic_gate_turn_1_forces_failure(self) -> None:
        state = {
            "refinement_count": 0,
            "pddl_valid": True,
            "hitl_reconstruction": "Route from Hamburg to Berlin",
            "enriched_intent": "Route from Hamburg to Berlin",
        }
        res = always_on_semantic_gate_node(state)  # type: ignore
        assert res["usem_passed"] is False
        assert res["usem_score"] == 1.0
        assert "Always-On HITL" in res["error_context"]

    def test_always_on_semantic_gate_turn_2_delegates_to_standard(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Mock standard semantic_gate_node to verify delegation
        monkeypatch.setattr(
            "tests.evaluation.baselines.always_on_hitl.graph.semantic_gate_node",
            lambda s: {"usem_passed": True, "usem_score": 0.1, "error_context": None, "messages": []},
        )
        state = {
            "refinement_count": 1,
            "pddl_valid": True,
            "hitl_reconstruction": "Route from Berlin to Frankfurt",
            "active_intent": "Route from Berlin to Frankfurt with at least 12 dB GSNR.",
        }
        res = always_on_semantic_gate_node(state)  # type: ignore
        assert res["usem_passed"] is True
        assert res["usem_score"] == 0.1


class TestLLMOnlyNodes:
    """Verify node logic for LLM-Only baseline."""

    def test_bypassed_semantic_gate_unconditionally_passes(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "tests.evaluation.baselines.llm_only.graph.semantic_gate_node",
            lambda s: {"usem_score": 0.9, "usem_passed": False, "error_context": "Divergence", "messages": []},
        )
        state = {
            "pddl_valid": False,
            "hitl_reconstruction": "Vague route",
        }
        res = bypassed_semantic_gate_node(state)  # type: ignore
        assert res["usem_passed"] is True
        assert res["error_context"] is None
        assert "LLM-Only" in res["messages"][0].content

    def test_controller_surrogate_turn_1_nominal_feasible_approves(self) -> None:
        state = {
            "refinement_count": 0,
            "intent_class": "I_Nominal",
            "qot_results": [
                {"path": ["Berlin", "Frankfurt"], "feasible": True, "snr_dB": 16.5, "power_dBm": -12.0}
            ],
        }
        res = controller_surrogate_radg_node(state)  # type: ignore
        assert res["radg_decision"] == "approve"
        assert res.get("controller_reached") is True

    def test_controller_surrogate_turn_1_non_nominal_injects_restconf_error(self) -> None:
        state = {
            "refinement_count": 0,
            "intent_class": "III_Infeasible",
            "qot_results": [
                {"path": ["Berlin", "Frankfurt"], "feasible": False, "snr_dB": 8.0, "power_dBm": -12.0}
            ],
            "refinement_history": [],
        }
        res = controller_surrogate_radg_node(state)  # type: ignore
        assert res["radg_decision"] == "replan"
        assert res["refinement_count"] == 1
        assert res["controller_error"] is True
        assert "RFC 8040 RESTCONF" in res["refinement_history"][0]
        assert "ietf-restconf:errors" in res["error_context"]

    def test_controller_surrogate_turn_2_blind_retry_failure_triggers_interrupt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        interrupt_called = {}

        def mock_interrupt(payload):
            interrupt_called["payload"] = payload
            return {"action": "replan", "feedback": "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."}

        monkeypatch.setattr("tests.evaluation.baselines.llm_only.graph.interrupt", mock_interrupt)

        state = {
            "refinement_count": 1,
            "intent_class": "III_Infeasible",
            "qot_results": [
                {"path": ["Berlin", "Frankfurt"], "feasible": False, "snr_dB": 8.0, "power_dBm": -12.0}
            ],
            "refinement_history": [],
        }
        res = controller_surrogate_radg_node(state)  # type: ignore
        assert res["radg_decision"] == "replan"
        assert res["refinement_count"] == 2
        assert "Route traffic from Berlin to Frankfurt" in res["refinement_history"][0]
        assert interrupt_called["payload"]["decision"] == "replan"

    def test_controller_surrogate_turn_3_recovery_approves(self) -> None:
        state = {
            "refinement_count": 2,
            "intent_class": "III_Infeasible",
            "qot_results": [
                {"path": ["Berlin", "Frankfurt"], "feasible": True, "snr_dB": 16.5, "power_dBm": -12.0}
            ],
        }
        res = controller_surrogate_radg_node(state)  # type: ignore
        assert res["radg_decision"] == "approve"
        assert res["controller_error"] is False


class TestLLMOnlyEvaluator:
    """Verify LLM-Only evaluator policy: blind initial approve and controller error handling."""

    def test_llm_only_nominal_approves_and_succeeds(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from tests.evaluation.baselines.llm_only.evaluator import LLMOnlyEvaluator

        evaluator = LLMOnlyEvaluator()
        monkeypatch.setattr(
            "tests.evaluation.baselines.llm_only.evaluator.evaluate_intent_with_graph",
            lambda **kwargs: {
                "initial_action": "approve",
                "final_action": "approve",
                "hitl_count": 0,
                "total_elapsed_seconds": 3.0,
                "total_tokens": 1200,
            },
        )
        res = evaluator.evaluate_single({"id": "nom_01", "class": "I_Nominal", "intent_text": "Route A to B"})
        assert res["initial_action"] == "approve"
        assert res["controller_verdict"] == "approve"
        assert res["controller_error"] is False
        assert res["success"] is True
        assert res["is_unfeasible_approval"] is False

    def test_llm_only_non_nominal_marks_error_and_fails_pre_deployment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from tests.evaluation.baselines.llm_only.evaluator import LLMOnlyEvaluator

        evaluator = LLMOnlyEvaluator()
        monkeypatch.setattr(
            "tests.evaluation.baselines.llm_only.evaluator.evaluate_intent_with_graph",
            lambda **kwargs: {
                "initial_action": "replan",
                "final_action": "approve",
                "hitl_count": 1,
                "total_elapsed_seconds": 12.0,
                "total_tokens": 4500,
            },
        )
        res = evaluator.evaluate_single({"id": "inf_01", "class": "III_Infeasible", "intent_text": "Direct span 35 dB"})
        assert res["initial_action"] == "approve"
        assert res["controller_verdict"] == "replan"
        assert res["controller_error"] is True
        assert res["success"] is False
        assert res["is_unfeasible_approval"] is True

    def test_llm_only_visuals_generation(self, tmp_path: pytest.TempPathFactory) -> None:
        import json
        from pathlib import Path
        from tests.evaluation.generate_visuals import generate_run_visuals

        test_dir = Path(str(tmp_path))
        data = {
            "metadata": {
                "run_id": "test_llm",
                "baseline_id": "llm_only",
                "model": "qwen2.5:3b",
                "provider": "ollama",
                "total_demands": 4,
            },
            "pillar_metrics": {
                "pillar_1": {"operable_crr_rate": 100.0, "cfg_pass_rate": 100.0, "mean_well_formed_agreement": 0.9},
                "pillar_2": {"uar_rate": 25.0, "unfeasible_approved_count": 1, "total_approved_count": 4, "piir_rate": 0.0},
                "pillar_3": {"mean_e2e_latency_seconds": 10.0, "total_tokens_consumed": 20000, "mean_tokens_per_intent": 5000, "mean_hitl_turns": 0.75, "total_hitl_interrupts": 3},
                "pillar_4": {"fpr_rate": 100.0, "false_positives_count": 3, "gda_rate": 25.0},
            },
            "demands": [
                {"class": "I_Nominal", "initial_action": "approve", "final_action": "approve", "controller_error": False, "total_elapsed_seconds": 3.0, "total_tokens": 1500, "turn_telemetry": [{"turn": 1, "elapsed_s": 3.0, "total_tokens": 1500}]},
                {"class": "II_Ambiguous", "initial_action": "approve", "final_action": "approve", "controller_error": True, "total_elapsed_seconds": 11.0, "total_tokens": 6000, "turn_telemetry": [{"turn": 1, "elapsed_s": 5.0, "total_tokens": 2800}, {"turn": 2, "elapsed_s": 6.0, "total_tokens": 3200}]},
                {"class": "III_Infeasible", "initial_action": "approve", "final_action": "approve", "controller_error": True, "total_elapsed_seconds": 13.0, "total_tokens": 6500, "turn_telemetry": [{"turn": 1, "elapsed_s": 6.0, "total_tokens": 3000}, {"turn": 2, "elapsed_s": 7.0, "total_tokens": 3500}]},
                {"class": "IV_Adversarial", "initial_action": "approve", "final_action": "approve", "controller_error": True, "total_elapsed_seconds": 12.0, "total_tokens": 6000, "turn_telemetry": [{"turn": 1, "elapsed_s": 5.5, "total_tokens": 2900}, {"turn": 2, "elapsed_s": 6.5, "total_tokens": 3100}]},
            ],
        }
        json_path = test_dir / "evaluation_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        out_dir = generate_run_visuals(json_path, target_dir=test_dir)
        assert (out_dir / "deployment_flow_sankey.png").exists()
        assert (out_dir / "wasted_compute_overhead.png").exists()
        assert (out_dir / "llm_only_ablation_dashboard.png").exists()

    def test_always_on_hitl_visuals_generation(self, tmp_path: pytest.TempPathFactory) -> None:
        import json
        from pathlib import Path
        from tests.evaluation.generate_visuals import generate_run_visuals

        test_dir = Path(str(tmp_path))
        data = {
            "metadata": {
                "run_id": "test_always_on",
                "baseline_id": "always_on_hitl",
                "model": "qwen2.5:3b",
                "provider": "ollama",
                "total_demands": 2,
            },
            "pillar_metrics": {
                "pillar_1": {"operable_crr_rate": 100.0, "cfg_pass_rate": 100.0, "mean_well_formed_agreement": 0.0},
                "pillar_2": {"uar_rate": 0.0, "unfeasible_approved_count": 0, "total_approved_count": 0, "piir_rate": 100.0},
                "pillar_3": {"mean_e2e_latency_seconds": 12.0, "total_tokens_consumed": 16000, "mean_tokens_per_intent": 8000, "mean_hitl_turns": 1.0, "total_hitl_interrupts": 2},
                "pillar_4": {"gda_rate": 100.0, "fpr_rate": 0.0, "selective_hitl_precision": 0.0},
            },
            "demands": [
                {"id": "intent_nom_01", "class": "I_Nominal", "initial_action": "clarify", "final_action": "approve", "total_elapsed_seconds": 12.5, "total_tokens": 8100, "hitl_count": 1, "turn_telemetry": [{"turn": 1, "elapsed_s": 5.5, "total_tokens": 3700}, {"turn": 2, "elapsed_s": 7.0, "total_tokens": 4400}]},
                {"id": "intent_nom_02", "class": "I_Nominal", "initial_action": "clarify", "final_action": "approve", "total_elapsed_seconds": 11.5, "total_tokens": 7900, "hitl_count": 1, "turn_telemetry": [{"turn": 1, "elapsed_s": 5.0, "total_tokens": 3600}, {"turn": 2, "elapsed_s": 6.5, "total_tokens": 4300}]},
            ],
        }
        json_path = test_dir / "evaluation_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

        # Place a dummy old matrix to verify cleanup
        old_file = test_dir / "gate_accuracy_matrix.png"
        old_file.write_text("dummy")

        out_dir = generate_run_visuals(json_path, target_dir=test_dir)
        assert (out_dir / "wasted_compute_overhead.png").exists()
        assert (out_dir / "wasted_compute_overhead.pdf").exists()
        assert (out_dir / "scalability_projection.png").exists()
        assert (out_dir / "scalability_projection.pdf").exists()
        assert (out_dir / "always_on_ablation_dashboard.png").exists()
        assert (out_dir / "always_on_ablation_dashboard.pdf").exists()
        assert not (out_dir / "gate_accuracy_matrix.png").exists()


class TestEvaluationMetrics:
    """Verify constraint retention rate (CRR) and Four Pillars metric aggregation."""

    def test_compute_constraint_retention_all_matched(self) -> None:
        explicit = {
            "min_gsnr": 15.0,
            "bandwidth": 100,
            "max_hops": 3,
            "avoid_nodes": ["Frankfurt"],
        }
        pddl = "(problem test (:goal (and (min-gsnr 15.0) (bandwidth 100) (max-hops 3) (avoid-node Frankfurt))))"
        crr_info = compute_constraint_retention(explicit, pddl)
        assert crr_info["explicit_count"] == 4
        assert crr_info["preserved_count"] == 4
        assert crr_info["crr"] == 1.0

    def test_compute_constraint_retention_missing(self) -> None:
        explicit = {
            "min_gsnr": 15.0,
            "bandwidth": 100,
        }
        pddl = "(problem test (:goal (and (min-gsnr 15.0))))"
        crr_info = compute_constraint_retention(explicit, pddl)
        assert crr_info["explicit_count"] == 2
        assert crr_info["preserved_count"] == 1
        assert crr_info["crr"] == 0.5

    def test_compute_pillar_metrics(self) -> None:
        results = [
            {
                "class": "I_Nominal",
                "initial_action": "approve",
                "final_action": "approve",
                "success": True,
                "is_unfeasible_approval": False,
                "pddl_valid": True,
                "semantic_agreement": 0.9,
                "hitl_count": 0,
                "total_elapsed_seconds": 5.0,
                "total_tokens": 1000,
                "crr_info": {"explicit_count": 2, "preserved_count": 2, "crr": 1.0},
            },
            {
                "class": "III_Infeasible",
                "initial_action": "replan",
                "final_action": "approve",
                "success": True,
                "is_unfeasible_approval": False,
                "pddl_valid": True,
                "semantic_agreement": 0.85,
                "hitl_count": 1,
                "total_elapsed_seconds": 12.0,
                "total_tokens": 2500,
                "crr_info": {"explicit_count": 1, "preserved_count": 1, "crr": 1.0},
            },
        ]
        metrics = compute_pillar_metrics(results)
        assert metrics["pillar_1"]["crr_rate"] == 100.0
        assert metrics["pillar_2"]["uar_rate"] == 0.0
        assert metrics["pillar_2"]["piir_rate"] == 100.0
        assert metrics["pillar_3"]["mean_hitl_turns"] == 0.5
        assert metrics["pillar_4"]["gda_rate"] == 100.0
        assert metrics["pillar_4"]["fpr_rate"] == 0.0


class TestActionSuccessLogic:
    """Verify check_action_success across classes."""

    def test_nominal_requires_approve(self) -> None:
        assert check_action_success("I_Nominal", "approve", "approve") is True
        assert check_action_success("I_Nominal", "approve", "clarify") is False

    def test_ambiguous_requires_clarify(self) -> None:
        assert check_action_success("II_Ambiguous", "clarify", "clarify") is True
        assert check_action_success("II_Ambiguous", "clarify", "approve") is False

    def test_infeasible_accepts_clarify_or_replan(self) -> None:
        assert check_action_success("III_Infeasible", ["clarify", "replan"], "replan") is True
        assert check_action_success("III_Infeasible", ["clarify", "replan"], "clarify") is True
        assert check_action_success("III_Infeasible", ["clarify", "replan"], "approve") is False
        assert check_action_success("III_Infeasible", "replan", "clarify") is True

    def test_adversarial_accepts_clarify_or_replan(self) -> None:
        assert check_action_success("IV_Adversarial", ["clarify", "replan"], "clarify") is True
        assert check_action_success("IV_Adversarial", ["clarify", "replan"], "replan") is True
        assert check_action_success("IV_Adversarial", ["clarify", "replan"], "approve") is False


class TestRunnerTimeoutAndStatus:
    """Verify intent timeout and execution outcome taxonomy in evaluate_intent_with_graph."""

    def test_intent_timeout_triggers_timeout_status(self) -> None:
        """When total elapsed time exceeds intent_timeout, execution terminates with timeout status."""
        from unittest.mock import MagicMock
        from tests.evaluation.baselines.common.runner import evaluate_intent_with_graph

        mock_graph = MagicMock()
        mock_graph.stream.return_value = [{"intent_ingest": {"active_intent": "foo"}}]
        mock_state = MagicMock()
        mock_state.next = ["hitl_clarify"]
        mock_state.tasks = []
        mock_graph.get_state.return_value = mock_state

        # intent_timeout of 0.0 forces immediate timeout
        res = evaluate_intent_with_graph(
            graph_factory=lambda **kwargs: mock_graph,
            item={"id": "test_01", "class": "I_Nominal", "intent_text": "Route A to B"},
            max_turns=3,
            intent_timeout=0.0,
            verbose=False,
        )
        assert res["execution_status"] == "timeout"
        assert res["final_action"] == "timeout"
        assert res["success"] is False

    def test_compute_pillar_metrics_includes_task_completion_rate(self) -> None:
        """compute_pillar_metrics computes task completion rate and counts timeouts."""
        results = [
            {
                "class": "I_Nominal",
                "initial_action": "approve",
                "final_action": "approve",
                "execution_status": "completed",
                "success": True,
                "is_unfeasible_approval": False,
                "pddl_valid": True,
                "hitl_count": 0,
                "total_elapsed_seconds": 5.0,
                "total_tokens": 1000,
            },
            {
                "class": "I_Nominal",
                "initial_action": "timeout",
                "final_action": "timeout",
                "execution_status": "timeout",
                "success": False,
                "is_unfeasible_approval": False,
                "pddl_valid": False,
                "hitl_count": 1,
                "total_elapsed_seconds": 300.0,
                "total_tokens": 500,
            },
        ]
        metrics = compute_pillar_metrics(results)
        assert metrics["pillar_3"]["task_completion_rate"] == 50.0
        assert metrics["pillar_3"]["completed_demands_count"] == 1
        assert metrics["pillar_3"]["timeout_demands_count"] == 1


class TestComparativeRadarMetrics:
    """Verify 4 orthogonal normalized radar metrics calculations."""

    def test_radar_metrics_penalties(self) -> None:
        from tests.evaluation.baselines.common.metrics import compute_comparative_radar_metrics

        baselines_info = {
            "proposed_radg": {
                "pillar_metrics": {
                    "pillar_2": {"uar_rate": 0.0},
                    "pillar_3": {
                        "median_e2e_latency_seconds": 5.0,
                        "median_tokens_per_intent": 2000,
                    },
                    "pillar_4": {
                        "fpr_rate": 0.0,
                        "total_count": 20,
                        "total_interrupted_count": 0,
                    },
                }
            },
            "always_on_hitl": {
                "pillar_metrics": {
                    "pillar_2": {"uar_rate": 0.0},
                    "pillar_3": {
                        "median_e2e_latency_seconds": 12.5,
                        "median_tokens_per_intent": 5000,
                    },
                    "pillar_4": {
                        "fpr_rate": 0.0,
                        "total_count": 20,
                        "total_interrupted_count": 20,
                    },
                }
            },
            "llm_only": {
                "pillar_metrics": {
                    "pillar_2": {"uar_rate": 75.0},
                    "pillar_3": {
                        "median_e2e_latency_seconds": 15.0,
                        "median_tokens_per_intent": 8000,
                    },
                    "pillar_4": {
                        "fpr_rate": 75.0,
                        "total_count": 20,
                        "total_interrupted_count": 0,
                    },
                }
            },
        }

        radar = compute_comparative_radar_metrics(baselines_info)

        # Proposed RADG is optimal across all 4 axes
        assert radar["proposed_radg"]["speed"] == 100.0
        assert radar["proposed_radg"]["token_usage"] == 100.0
        assert radar["proposed_radg"]["pre_deployment_integrity"] == 100.0
        assert radar["proposed_radg"]["zero_touch_autonomy"] == 100.0

        # Always-On HITL is severely penalized in autonomy (0%), speed (40%), and token usage (40%)
        assert radar["always_on_hitl"]["speed"] == 40.0
        assert radar["always_on_hitl"]["token_usage"] == 40.0
        assert radar["always_on_hitl"]["pre_deployment_integrity"] == 100.0
        assert radar["always_on_hitl"]["zero_touch_autonomy"] == 0.0

        # LLM-Only is severely penalized in integrity (25%), speed (33.33%), token usage (25%), and zero-touch autonomy (0.0%)
        assert radar["llm_only"]["speed"] == 33.33
        assert radar["llm_only"]["token_usage"] == 25.0
        assert radar["llm_only"]["pre_deployment_integrity"] == 25.0
        assert radar["llm_only"]["zero_touch_autonomy"] == 0.0


class TestAlwaysOnCorpusConvergence:
    """Verify that AlwaysOnHITLEvaluator populates non-nominal demands from Proposed RADG."""

    def test_evaluate_corpus_merges_non_nominals(self, monkeypatch: pytest.MonkeyPatch, tmp_path: pytest.TempPathFactory) -> None:
        from pathlib import Path
        from tests.evaluation.baselines.always_on_hitl import AlwaysOnHITLEvaluator

        evaluator = AlwaysOnHITLEvaluator()
        test_dir = Path(str(tmp_path))

        corpus = [
            {"id": "nom_01", "class": "I_Nominal", "intent_text": "Route A to B"},
            {"id": "amb_01", "class": "II_Ambiguous", "intent_text": "Vague route"},
            {"id": "inf_01", "class": "III_Infeasible", "intent_text": "Direct span 30 dB"},
        ]

        monkeypatch.setattr(
            evaluator,
            "evaluate_single",
            lambda item, **kw: {
                "id": item["id"],
                "class": item["class"],
                "baseline": "always_on_hitl",
                "initial_action": "clarify",
                "final_action": "approve",
                "success": True,
                "hitl_count": 1,
                "total_elapsed_seconds": 12.0,
                "total_tokens": 8000,
                "pddl_valid": True,
                "crr_info": {"explicit_count": 1, "preserved_count": 1, "crr": 1.0},
            },
        )

        mock_proposed = {
            "amb_01": {
                "id": "amb_01",
                "class": "II_Ambiguous",
                "baseline": "proposed_radg",
                "initial_action": "clarify",
                "final_action": "approve",
                "success": True,
                "hitl_count": 1,
                "total_elapsed_seconds": 11.0,
                "total_tokens": 5000,
                "pddl_valid": True,
                "crr_info": {"explicit_count": 1, "preserved_count": 1, "crr": 1.0},
            },
            "inf_01": {
                "id": "inf_01",
                "class": "III_Infeasible",
                "baseline": "proposed_radg",
                "initial_action": "replan",
                "final_action": "approve",
                "success": True,
                "hitl_count": 1,
                "total_elapsed_seconds": 13.0,
                "total_tokens": 5500,
                "pddl_valid": True,
                "crr_info": {"explicit_count": 1, "preserved_count": 1, "crr": 1.0},
            },
        }

        monkeypatch.setattr(
            "tests.evaluation.baselines.always_on_hitl.evaluator._load_proposed_radg_demands",
            lambda run_id=None: mock_proposed,
        )

        results = evaluator.evaluate_corpus(
            corpus=corpus,
            output_dir=test_dir,
            metadata={"run_id": "test_conv"},
            generate_visuals=False,
        )

        assert len(results) == 3
        # Check that nominal item has always_on_hitl baseline
        assert results[0]["id"] == "nom_01"
        assert results[0]["baseline"] == "always_on_hitl"
        # Check that non-nominal items were populated and re-tagged
        assert results[1]["id"] == "amb_01"
        assert results[1]["baseline"] == "always_on_hitl"
        assert results[2]["id"] == "inf_01"
        assert results[2]["baseline"] == "always_on_hitl"
        assert results[2]["initial_action"] == "replan"


