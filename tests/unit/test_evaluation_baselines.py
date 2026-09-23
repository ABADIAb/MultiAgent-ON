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

    def test_controller_surrogate_turn_1_non_nominal_triggers_interrupt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        interrupt_called = {}

        def mock_interrupt(payload):
            interrupt_called["payload"] = payload
            return {"action": "replan", "feedback": "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."}

        monkeypatch.setattr("tests.evaluation.baselines.llm_only.graph.interrupt", mock_interrupt)

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
        assert "Route traffic from Berlin to Frankfurt" in res["refinement_history"][0]
        assert interrupt_called["payload"]["decision"] == "replan"

    def test_controller_surrogate_turn_2_recovery_approves(self) -> None:
        state = {
            "refinement_count": 1,
            "intent_class": "III_Infeasible",
            "qot_results": [
                {"path": ["Berlin", "Frankfurt"], "feasible": True, "snr_dB": 16.5, "power_dBm": -12.0}
            ],
        }
        res = controller_surrogate_radg_node(state)  # type: ignore
        assert res["radg_decision"] == "approve"


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

    def test_infeasible_requires_replan(self) -> None:
        assert check_action_success("III_Infeasible", "replan", "replan") is True
        assert check_action_success("III_Infeasible", "replan", "approve") is False

    def test_adversarial_accepts_clarify_or_replan(self) -> None:
        assert check_action_success("IV_Adversarial", "clarify", "clarify") is True
        assert check_action_success("IV_Adversarial", "replan", "replan") is True
        assert check_action_success("IV_Adversarial", "clarify", "approve") is False
