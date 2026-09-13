"""Baseline C: Always-Off HITL (Reckless Autonomous Baseline).

Architecture: Neurosymbolic Pipeline with Decision Gates Bypassed.
In this baseline, the neurosymbolic modules are invoked, but both decision gates
are disabled:
  1. Semantic Gate Bypassed: Never halts to clarify ambiguous (Class II) or
     syntactically invalid (Class IV) intents; attempts best-effort solver execution.
  2. Physical Risk Gate Bypassed: Never halts or requests replanning when physical
     QoT feasibility fails (Class III); blindly issues an 'approve' action on the
     first candidate path regardless of computed GSNR.

Used to evaluate:
  - Catastrophic safety failures (Unsafe Approval Rate UAR >> 0%)
  - Service blocking probability when ambiguities cannot resolve automatically
  - Proves that pre-deployment decision gates are non-negotiable for network safety
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
class AlwaysOffHITLBaseline(BaseBaseline):
    """Baseline C: Always-Off HITL (Zero Human Intervention, Gates Bypassed)."""

    name = "Baseline C (Always-Off HITL)"
    baseline_id = "always_off"

    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        start_time = time.perf_counter()
        intent_id = intent_data.get("id", "unknown")
        intent_text = intent_data.get("intent_text", "")

        prompt_tokens = 0
        completion_tokens = 0

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

        # 1. Phase 1: Intent Ingest
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

        # GATE BYPASS 1: No Phase 3 Semantic Gate!
        # Even if pddl_valid is False or intent is ambiguous, do NOT clarify.
        # Push directly into Symbolic Solver.

        # 3. Phase 4: Symbolic Solver
        solver_res = symbolic_solver_node(state)  # type: ignore
        state.update(solver_res)
        candidate_paths = state.get("candidate_paths") or []

        # 4. Phase 5: QoT Validation
        qot_res = qot_validation_node(state)  # type: ignore
        state.update(qot_res)
        qot_results = state.get("qot_results") or []

        # GATE BYPASS 2: No Phase 6 Physical Risk Gate (RADG)!
        # In Always-Off mode, the system never halts or replans.
        # It blindly approves whatever candidate path was computed (or rejects only if solver returned 0 paths).
        selected_path: list[str] | None = None
        computed_gsnr: float | None = None
        qot_feasible = False
        action: str = "approve"

        if qot_results:
            first_path = qot_results[0]
            selected_path = first_path.get("path")
            computed_gsnr = first_path.get("snr_dB")
            qot_feasible = bool(first_path.get("feasible", False))
            # Blindly approve even if qot_feasible is False!
            action = "approve"
        elif candidate_paths:
            selected_path = candidate_paths[0].get("nodes")
            action = "approve"
        else:
            action = "reject"
            state["error_context"] = "Solver failed to find any path."

        exec_time = time.perf_counter() - start_time

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": action,  # type: ignore
            "selected_path": selected_path,
            "computed_gsnr_dB": computed_gsnr,
            "qot_feasible": qot_feasible,
            "pddl_valid": pddl_valid,
            "parsed_constraints": state.get("pddl_parsed_constraints"),
            "hitl_interrupts": 0,  # Strictly zero
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "execution_time_s": exec_time,
            "planning_report": f"Always-Off execution complete. Action: {action} (Gates bypassed)",
            "error": state.get("error_context"),
            "metadata": {"gates_bypassed": True},
        }
