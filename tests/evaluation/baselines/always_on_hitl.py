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
    STANDARD_FOLLOW_UP_INTENT,
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
        initial_action = "approve"

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

        # Handle ambiguous, malformed, or adversarial intent via operator clarification follow-up
        if (
            not pddl_valid
            or "Ambiguous" in intent_class
            or "Adversarial" in intent_class
        ):
            initial_action = "clarify"
            # Operator clarifies by injecting clean, unambiguous intent
            state["active_intent"] = STANDARD_FOLLOW_UP_INTENT
            state["enriched_intent"] = STANDARD_FOLLOW_UP_INTENT
            state["error_context"] = f"Operator clarified: {STANDARD_FOLLOW_UP_INTENT}"

            prompt_tokens += self.count_tokens(STANDARD_FOLLOW_UP_INTENT)
            re_parser_res = pddl_parser_node(state)  # type: ignore
            state.update(re_parser_res)
            re_pddl = state.get("pddl_constraints") or ""
            pddl_valid = state.get("pddl_valid", False)
            completion_tokens += self.count_tokens(re_pddl)

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
        else:
            # Physical infeasibility (Class III) triggers replan
            if initial_action == "approve":
                initial_action = "replan"
            # Operator relaxes constraints via follow-up replan
            hitl_interrupts += 1
            state["active_intent"] = STANDARD_FOLLOW_UP_INTENT
            state["enriched_intent"] = STANDARD_FOLLOW_UP_INTENT
            prompt_tokens += self.count_tokens(STANDARD_FOLLOW_UP_INTENT)
            re_parser_res = pddl_parser_node(state)  # type: ignore
            state.update(re_parser_res)
            re_solver_res = symbolic_solver_node(state)  # type: ignore
            state.update(re_solver_res)
            re_qot_res = qot_validation_node(state)  # type: ignore
            state.update(re_qot_res)
            re_qot_results = state.get("qot_results") or []
            re_feasible = [p for p in re_qot_results if p.get("feasible")]
            if re_feasible:
                best = re_feasible[0]
                selected_path = best.get("path")
                computed_gsnr = best.get("snr_dB")
                qot_feasible = True
            elif qot_results:
                selected_path = qot_results[0].get("path")
                computed_gsnr = qot_results[0].get("snr_dB")

        exec_time = time.perf_counter() - start_time

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": initial_action,  # type: ignore
            "initial_action": initial_action,  # type: ignore
            "final_action": "approve" if qot_feasible else initial_action,  # type: ignore
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
                "checkpoints_triggered": ["phase_3_semantic", "phase_6_physical"],
                "initial_action": initial_action,
            },
        }
