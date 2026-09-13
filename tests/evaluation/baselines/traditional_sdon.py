"""Baseline D: Traditional SDON / PCE (Non-LLM Industrial Baseline).

Architecture: Deterministic YANG/RESTConf RPC + PCE (Yen's K-SP).
Grounded in RFC 8231, standard YANG models, and centralized Path Computation
Elements (PCE) without any LLM components.

Characteristics:
  1. Input: Direct parameter extraction from ground_truth_constraints (simulating
     the expert operator authoring the structured YANG RPC).
  2. Ambiguity Handling: Cannot process natural language or underspecified requests.
     Ambiguous (Class II) or Adversarial (Class IV) intents fail parameter extraction
     and require full manual operator intervention.
  3. Routing & Physics: Computes deterministic Yen's K-SP paths and validates
     against optical thresholds using conservative static design margins (3 dB margin).
  4. Metrics:
     - Prompt & completion tokens: Strictly 0.
     - Unsafe Approval Rate (UAR): Strictly 0% (absolute industrial safety invariant).
     - Human effort: 100% manual authoring (N_hitl = 1 for all requests).
"""

from __future__ import annotations

import time
from typing import Any

from src.core.symbolic_solver import symbolic_solver_node
from tests.evaluation.baselines.base import (
    BaseBaseline,
    BaselineResult,
    register_baseline,
)


@register_baseline
class TraditionalSDONBaseline(BaseBaseline):
    """Baseline D: Traditional SDON / PCE without LLM."""

    name = "Baseline D (Traditional SDON / PCE)"
    baseline_id = "traditional_sdon"

    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        start_time = time.perf_counter()
        intent_id = intent_data.get("id", "unknown")
        intent_class = intent_data.get("class", "")
        source_node = intent_data.get("source_node")
        target_node = intent_data.get("target_node")
        gt_constraints = intent_data.get("ground_truth_constraints", {})

        # In traditional SDON, manual RPC authoring represents 1 human interaction event (100% manual setup)
        hitl_interrupts = 1

        # Check if endpoints are valid nodes in Nobel-Germany topology
        valid_nodes = {n.name for n in self.topology_snapshot.nodes}

        # Class II (Ambiguous) or Class IV (Adversarial) cannot be compiled into standard YANG RPC
        if (
            not source_node
            or not target_node
            or source_node not in valid_nodes
            or target_node not in valid_nodes
            or "Ambiguous" in intent_class
            or "Adversarial" in intent_class
        ):
            return {
                "intent_id": intent_id,
                "baseline_id": self.baseline_id,
                "action": "reject",
                "selected_path": None,
                "computed_gsnr_dB": None,
                "qot_feasible": False,
                "pddl_valid": None,
                "parsed_constraints": None,
                "hitl_interrupts": hitl_interrupts,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
                "execution_time_s": time.perf_counter() - start_time,
                "planning_report": "Traditional PCE: RPC compilation failed due to underspecified or invalid endpoints.",
                "error": "Missing or invalid optical endpoint parameters in YANG request.",
                "metadata": {"traditional_pce": True},
            }

        # Extract structured constraints
        avoid_nodes = gt_constraints.get("avoid_nodes", [])
        avoid_links = gt_constraints.get("avoid_links", [])
        max_hops = gt_constraints.get("max_hops")
        min_gsnr = float(gt_constraints.get("min_gsnr", 15.0))

        # Build deterministic PDDL representation representing the structured YANG RPC
        pddl_goals = [f"(route {source_node} {target_node})"]
        if min_gsnr:
            pddl_goals.append(f"(min-gsnr {min_gsnr})")
        for an in avoid_nodes:
            pddl_goals.append(f"(avoid-node {an})")
        for al in avoid_links:
            pddl_goals.append(f"(avoid-link {al})")
        if max_hops is not None:
            pddl_goals.append(f"(max-hops {max_hops})")

        pddl_str = (
            f"(define (problem sdon-route-{source_node}-{target_node})\n"
            f"  (:domain optical-network)\n"
            f"  (:goal (and {' '.join(pddl_goals)}))\n"
            f")"
        )
        solver_state = {
            "pddl_constraints": pddl_str,
            "topology_snapshot": self.topology_snapshot,
            "enriched_intent": f"Source: {source_node} | Target: {target_node}",
        }
        solver_res = symbolic_solver_node(solver_state)  # type: ignore
        candidate_paths = solver_res.get("candidate_paths") or []

        selected_path: list[str] | None = None
        computed_gsnr: float | None = None
        qot_feasible = False
        action: str = "reject"

        # Evaluate against GN-model with conservative industrial design margin (+3 dB)
        for path_info in candidate_paths:
            path = path_info.get("nodes", [])
            snr, feasible = self.verify_optical_path(path, min_gsnr_dB=min_gsnr)
            if feasible and snr is not None and (snr - min_gsnr) >= 3.0:
                selected_path = path
                computed_gsnr = snr
                qot_feasible = True
                action = "approve"
                break

        # If no path met the strict 3 dB design margin, check standard feasibility
        if not qot_feasible and candidate_paths:
            best_path = candidate_paths[0].get("nodes", [])
            computed_gsnr, qot_feasible = self.verify_optical_path(
                best_path, min_gsnr_dB=min_gsnr
            )
            selected_path = best_path
            # In traditional systems, failing design margin triggers an alert/replan
            action = "approve" if qot_feasible else "replan"

        exec_time = time.perf_counter() - start_time

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": action,  # type: ignore
            "selected_path": selected_path,
            "computed_gsnr_dB": computed_gsnr,
            "qot_feasible": qot_feasible,
            "pddl_valid": None,
            "parsed_constraints": gt_constraints,
            "hitl_interrupts": hitl_interrupts,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "execution_time_s": exec_time,
            "planning_report": f"Traditional SDON PCE: Route {selected_path} | Feasible: {qot_feasible}",
            "error": None,
            "metadata": {"traditional_pce": True, "static_margin_dB": 3.0},
        }
