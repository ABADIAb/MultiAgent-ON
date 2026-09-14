"""Baseline C: Traditional SDON / PCE (Static Industrial Reference Baseline).

Architecture: Deterministic Manual YANG/RESTConf RPC + PCE without LLM.
Grounded in RFC 8231, standard YANG models, and centralized Path Computation
Elements (PCE) configured manually by human operators.

Characteristics:
  1. Purpose: Serves strictly as an industrial reference baseline to highlight
     the declarative paradigm shift and operational velocity of IBON vs SDON.
  2. Execution: No dynamic NL intent parsing or live benchmark execution is performed.
     Traditional SDON does not accept natural language intents.
  3. Latency: Service provisioning in traditional SDON takes hours to days or weeks
     due to manual ticket workflows, review cycles, and maintenance windows.
  4. Metrics:
     - Prompt & completion tokens: Strictly N/A (0 tokens, non-LLM).
     - Unsafe Approval Rate (UAR): Strictly 0.0% (hardcoded industrial safety invariant).
     - Human effort: 100% manual authoring (N_hitl = 100% manual setup).
     - Neural / PDDL metrics (CRR, CFG-PR, GDA, FPR): Strictly N/A.
"""

from __future__ import annotations

from typing import Any

from tests.evaluation.baselines.base import (
    BaseBaseline,
    BaselineResult,
    register_baseline,
)


@register_baseline
class TraditionalSDONBaseline(BaseBaseline):
    """Baseline C: Traditional SDON / PCE (Static Industrial Reference)."""

    name = "Baseline C (Traditional SDON / PCE)"
    baseline_id = "traditional_sdon"

    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        intent_id = intent_data.get("id", "unknown")

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": "approve",
            "initial_action": "approve",
            "final_action": "approve",
            "selected_path": None,
            "computed_gsnr_dB": None,
            "qot_feasible": True,
            "pddl_valid": None,
            "parsed_constraints": None,
            "hitl_interrupts": 1,  # 100% manual operator authoring
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "execution_time_s": 0.0,
            "planning_report": (
                "Traditional SDON: Static industrial reference baseline. "
                "Manual provisioning workflow (hours/days/weeks); absolute safety invariant UAR = 0.0%."
            ),
            "error": None,
            "metadata": {
                "is_static_reference": True,
                "mode": "static_reference",
                "workflow_latency": "Hours to Days",
                "provisioning_latency": "Hours to Days",
                "human_effort": "100% manual authoring",
                "uar": 0.0,
                "uar_percent": 0.0,
            },
        }
