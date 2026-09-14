"""Baseline B: Always-On HITL (Paranoid Baseline).

Architecture: Full Neurosymbolic Pipeline with Mandatory Operator Review.
In this baseline, the full neurosymbolic architecture is active (Intent Ingest,
PDDL Parser, AST Validation, Symbolic Solver, and GN-model QoT engine).
However, the adaptive decision intelligence of the RADG is overridden:
  1. Mandatory Phase 3 Review: The system ALWAYS interrupts the operator to confirm
     semantic understanding and PDDL extraction, even when U_sem is 0.0.
  2. Mandatory Phase 6 Review: The system ALWAYS interrupts the operator to approve
     the physical lightpath before provisioning, even when QoT margins are high.

Used to evaluate:
  - Worst-case operational friction (N_hitl = 100% of intents, >= 2 interrupts each)
  - Latency penalty of continuous human validation
  - Token consumption inflated by repeated confirmation dialogues
"""

from __future__ import annotations

import time
from typing import Any

from src.core.symbolic_solver import symbolic_solver_node
from src.nodes.intent_ingest import intent_ingest_node
from src.nodes.pddl_parser import pddl_parser_node
from src.nodes.qot_validation import qot_validation_node
from tests.evaluation.baselines.base import (
    BaseBaseline,
    BaselineResult,
    register_baseline,
)


@register_baseline
class AlwaysOnHITLBaseline(BaseBaseline):
    """Baseline B: Always-On HITL (Mandatory Human Intervention at all checkpoints)."""

    name = "Baseline B (Always-On HITL)"
    baseline_id = "always_on"

    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        start_time = time.perf_counter()
        intent_id = intent_data.get("id", "unknown")
        intent_text = intent_data.get("intent_text", "")
        intent_class = intent_data.get("class", "")

        prompt_tokens = 0
        completion_tokens = 0
        hitl_interrupts = 0

        # State setup
        state: dict[str, Any] = {
            "messages": [{"role": "user", "content": intent_text}],
            "topology_snapshot": self.topology_snapshot,
            "active_intent": intent_text,
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "candidate_paths": None,
            "qot_results": None,
            "error_context": None,
        }

        # 1. Phase 1: Intent Ingest (Mock GraphRAG Scoping)
        ingest_res = intent_ingest_node(state)  # type: ignore
        state.update(ingest_res)
        prompt_tokens += self.count_tokens(
            state.get("topology_context", "") + intent_text
        )

        # 2. Phase 2: PDDL Translation
        parser_res = pddl_parser_node(state)  # type: ignore
        state.update(parser_res)
        pddl_str = state.get("pddl_constraints") or ""
        pddl_valid = state.get("pddl_valid", False)
        completion_tokens += self.count_tokens(pddl_str)

        # MANDATORY HITL INTERRUPT 1 (Semantic Verification):
        # In Always-On HITL, the operator is ALWAYS queried to verify the PDDL
        hitl_interrupts += 1

        # Simulate operator verification response
        if (
            not pddl_valid
            or "Ambiguous" in intent_class
            or "Adversarial" in intent_class
        ):
            # Ambiguous or malformed intent requires clarification
            action = "clarify"
            return {
                "intent_id": intent_id,
                "baseline_id": self.baseline_id,
                "action": action,
                "selected_path": None,
                "computed_gsnr_dB": None,
                "qot_feasible": False,
                "pddl_valid": pddl_valid,
                "parsed_constraints": state.get("pddl_parsed_constraints"),
                "hitl_interrupts": hitl_interrupts,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "execution_time_s": time.perf_counter() - start_time,
                "planning_report": f"Always-On HITL Interrupted at Phase 3 (Clarify required for {intent_class})",
                "error": state.get("error_context"),
                "metadata": {"checkpoints_triggered": ["phase_3_semantic"]},
            }

        # 3. Phase 4: Symbolic Solver
        solver_res = symbolic_solver_node(state)  # type: ignore
        state.update(solver_res)

        # 4. Phase 5: QoT Physics Engine
        qot_res = qot_validation_node(state)  # type: ignore
        state.update(qot_res)
        qot_results = state.get("qot_results") or []

        # MANDATORY HITL INTERRUPT 2 (Physical Pre-Deployment Verification):
        # In Always-On HITL, the operator is ALWAYS queried before deployment
        hitl_interrupts += 1

        # Inspect QoT results
        feasible_paths = [p for p in qot_results if p.get("feasible")]
        selected_path: list[str] | None = None
        computed_gsnr: float | None = None
        qot_feasible = False

        if feasible_paths:
            best = feasible_paths[0]
            selected_path = best.get("path")
            computed_gsnr = best.get("snr_dB")
            qot_feasible = True
            action = "approve"
        else:
            action = "replan"
            if qot_results:
                selected_path = qot_results[0].get("path")
                computed_gsnr = qot_results[0].get("snr_dB")

        exec_time = time.perf_counter() - start_time

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": action,
            "selected_path": selected_path,
            "computed_gsnr_dB": computed_gsnr,
            "qot_feasible": qot_feasible,
            "pddl_valid": pddl_valid,
            "parsed_constraints": state.get("pddl_parsed_constraints"),
            "hitl_interrupts": hitl_interrupts,  # Always >= 2 on completed runs
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "execution_time_s": exec_time,
            "planning_report": f"Always-On HITL completed with {hitl_interrupts} mandatory operator interventions.",
            "error": state.get("error_context"),
            "metadata": {
                "checkpoints_triggered": ["phase_3_semantic", "phase_6_physical"]
            },
        }
