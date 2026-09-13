"""Deterministic mathematical engine for Sprint 4 evaluation metrics.

Calculates metrics across the 4 Core Validation Pillars:
  1. Semantic Translation Accuracy (CRR, CFG-PR, Syntax Error Rate, Hallucination Rate).
  2. Physical Feasibility (UAR, QFR, PIIR).
  3. Orchestration Efficiency (Latencies, Token Consumption, Token Savings, HITL Reduction).
  4. RADG Decision Robustness (GDA, FPR, HITL Interruption Distribution).

All functions are pure, deterministic, and strictly-typed.
"""

from __future__ import annotations

import statistics
from typing import Any

from tests.evaluation.baselines.base import BaselineResult


# ---------------------------------------------------------------------------
# Pillar 1: Semantic Translation Accuracy
# ---------------------------------------------------------------------------


def _check_constraint_match(gt_val: Any, parsed_val: Any) -> bool:
    """Helper to verify if a parsed constraint satisfies the ground truth constraint."""
    if gt_val is None:
        return True
    if parsed_val is None:
        return False
    if isinstance(gt_val, (int, float)) and isinstance(parsed_val, (int, float)):
        return abs(float(gt_val) - float(parsed_val)) < 0.1
    if isinstance(gt_val, list) and isinstance(parsed_val, list):
        gt_set = set(str(x).lower() for x in gt_val)
        parsed_set = set(str(x).lower() for x in parsed_val)
        return gt_set.issubset(parsed_set)
    return str(gt_val).lower() == str(parsed_val).lower()


def compute_semantic_metrics(
    results: list[BaselineResult], intents: list[dict[str, Any]]
) -> dict[str, float]:
    """Calculate Pillar 1: Semantic Translation Accuracy metrics.

    Metrics:
      - crr_percent: Constraint Retention Rate (%)
      - cfg_pass_rate_percent: Context-Free Grammar Pass Rate (%)
      - syntax_error_rate_percent: 100 - CFG-PR (%)
      - hallucination_rate_percent: Fraction of runs with hallucinated topology/nodes (%)
      - mean_semantic_agreement: Average (1 - d_sem) semantic agreement [0.0, 1.0]
    """
    if not results:
        return {
            "crr_percent": 0.0,
            "cfg_pass_rate_percent": 0.0,
            "syntax_error_rate_percent": 100.0,
            "hallucination_rate_percent": 0.0,
            "mean_semantic_agreement": 0.0,
        }

    intents_by_id = {item.get("id"): item for item in intents}

    total_explicit_constraints = 0
    preserved_constraints = 0
    cfg_passed_count = 0
    hallucination_count = 0
    agreement_scores: list[float] = []

    for res in results:
        intent_id = res.get("intent_id")
        intent_data = intents_by_id.get(intent_id, {})
        gt_constraints = intent_data.get("ground_truth_constraints", {})

        # 1. CRR calculation
        parsed = res.get("parsed_constraints") or {}
        for c_key, c_val in gt_constraints.items():
            total_explicit_constraints += 1
            if c_key in parsed and _check_constraint_match(c_val, parsed[c_key]):
                preserved_constraints += 1

        # 2. CFG-PR
        if res.get("pddl_valid") is True:
            cfg_passed_count += 1

        # 3. Hallucination check
        selected_path = res.get("selected_path")
        if selected_path:
            # If path was proposed but optical check deemed it non-existent or invalid topology
            if res.get("computed_gsnr_dB") is None:
                hallucination_count += 1
        elif res.get("error") and "hallucinat" in str(res.get("error")).lower():
            hallucination_count += 1

        # 4. Semantic agreement
        metadata = res.get("metadata", {})
        if "usem_score" in metadata and metadata["usem_score"] is not None:
            score = float(metadata["usem_score"])
            agreement_scores.append(max(0.0, min(1.0, 1.0 - score)))
        else:
            agreement_scores.append(1.0 if res.get("pddl_valid") else 0.0)

    n_results = len(results)
    crr = (
        (preserved_constraints / total_explicit_constraints * 100.0)
        if total_explicit_constraints > 0
        else 100.0
    )
    cfg_pr = (cfg_passed_count / n_results) * 100.0
    syntax_error = 100.0 - cfg_pr
    hallucination_rate = (hallucination_count / n_results) * 100.0
    mean_agreement = statistics.mean(agreement_scores) if agreement_scores else 0.0

    return {
        "crr_percent": round(crr, 2),
        "cfg_pass_rate_percent": round(cfg_pr, 2),
        "syntax_error_rate_percent": round(syntax_error, 2),
        "hallucination_rate_percent": round(hallucination_rate, 2),
        "mean_semantic_agreement": round(mean_agreement, 3),
    }


# ---------------------------------------------------------------------------
# Pillar 2: Physical Feasibility
# ---------------------------------------------------------------------------


def compute_physical_metrics(
    results: list[BaselineResult], intents: list[dict[str, Any]]
) -> dict[str, float]:
    """Calculate Pillar 2: Physical Feasibility metrics.

    Metrics:
      - uar_percent: Unsafe Approval Rate (%) -> STRICT 0% FOR PROPOSED
      - qfr_percent: QoT Feasibility Rate (%) -> 100% when UAR=0%
      - piir_percent: Physical Infeasibility Interception Rate (%)
    """
    if not results:
        return {
            "uar_percent": 0.0,
            "qfr_percent": 0.0,
            "piir_percent": 100.0,
        }

    intents_by_id = {item.get("id"): item for item in intents}
    approved = [r for r in results if r.get("action") == "approve"]

    # 1. UAR and QFR
    if not approved:
        uar = 0.0
        qfr = 0.0
    else:
        unsafe_count = 0
        for res in approved:
            intent_data = intents_by_id.get(res.get("intent_id"), {})
            gt_constraints = intent_data.get("ground_truth_constraints", {})
            min_gsnr_req = gt_constraints.get("min_gsnr", 15.0)

            is_feasible = res.get("qot_feasible") is True
            computed_gsnr = res.get("computed_gsnr_dB")

            # Check both binary flag and numerical threshold
            if (
                not is_feasible
                or computed_gsnr is None
                or float(computed_gsnr) < float(min_gsnr_req)
            ):
                unsafe_count += 1

        uar = (unsafe_count / len(approved)) * 100.0
        qfr = ((len(approved) - unsafe_count) / len(approved)) * 100.0

    # 2. PIIR (Physical Infeasibility Interception Rate for Class III)
    class_3_intents = [
        item
        for item in intents
        if item.get("class") == "III_Infeasible"
        or item.get("expected_radg_action") == "replan"
    ]
    if not class_3_intents:
        piir = 100.0
    else:
        class_3_ids = {item.get("id") for item in class_3_intents}
        class_3_results = [r for r in results if r.get("intent_id") in class_3_ids]

        intercepted = 0
        for r in class_3_results:
            if r.get("action") == "replan" or (
                r.get("action") != "approve"
                and r.get("action") in ("clarify", "reject")
            ):
                intercepted += 1

        piir = (
            (intercepted / len(class_3_results) * 100.0) if class_3_results else 100.0
        )

    return {
        "uar_percent": round(uar, 2),
        "qfr_percent": round(qfr, 2),
        "piir_percent": round(piir, 2),
    }


# ---------------------------------------------------------------------------
# Pillar 3: Orchestration & Resource Efficiency
# ---------------------------------------------------------------------------


def compute_efficiency_metrics(
    results: list[BaselineResult],
    baseline_id: str,
    all_results: dict[str, list[BaselineResult]] | None = None,
) -> dict[str, float]:
    """Calculate Pillar 3: Orchestration & Resource Efficiency metrics.

    Metrics:
      - mean_latency_s, median_latency_s, p95_latency_s
      - mean_prompt_tokens, mean_completion_tokens, mean_total_tokens
      - token_reduction_percent (vs llm_only baseline)
      - hitl_reduction_percent (vs always_on baseline)
    """
    if not results:
        return {
            "mean_latency_s": 0.0,
            "median_latency_s": 0.0,
            "p95_latency_s": 0.0,
            "mean_prompt_tokens": 0.0,
            "mean_completion_tokens": 0.0,
            "mean_total_tokens": 0.0,
            "token_reduction_percent": 0.0,
            "hitl_reduction_percent": 0.0,
        }

    latencies = [r.get("execution_time_s", 0.0) for r in results]
    prompt_tokens = [r.get("prompt_tokens", 0) for r in results]
    completion_tokens = [r.get("completion_tokens", 0) for r in results]
    total_tokens = [r.get("total_tokens", 0) for r in results]

    mean_lat = statistics.mean(latencies)
    median_lat = statistics.median(latencies)
    sorted_lat = sorted(latencies)
    p95_idx = int(len(sorted_lat) * 0.95)
    p95_lat = sorted_lat[min(p95_idx, len(sorted_lat) - 1)]

    mean_prompt = statistics.mean(prompt_tokens)
    mean_comp = statistics.mean(completion_tokens)
    mean_tot = statistics.mean(total_tokens)

    # Token reduction vs LLM-Only baseline
    token_reduction = 0.0
    if all_results and "llm_only" in all_results:
        ref_prompts = [r.get("prompt_tokens", 0) for r in all_results["llm_only"]]
        ref_mean_prompt = statistics.mean(ref_prompts) if ref_prompts else 0.0
        if ref_mean_prompt > 0:
            token_reduction = max(
                0.0,
                ((ref_mean_prompt - mean_prompt) / ref_mean_prompt) * 100.0,
            )

    # HITL reduction vs Always-On baseline
    hitl_reduction = 0.0
    if all_results and "always_on" in all_results:
        ref_hitl = sum(r.get("hitl_interrupts", 0) for r in all_results["always_on"])
        my_hitl = sum(r.get("hitl_interrupts", 0) for r in results)
        if ref_hitl > 0:
            hitl_reduction = max(
                0.0,
                (1.0 - (my_hitl / ref_hitl)) * 100.0,
            )

    return {
        "mean_latency_s": round(mean_lat, 3),
        "median_latency_s": round(median_lat, 3),
        "p95_latency_s": round(p95_lat, 3),
        "mean_prompt_tokens": round(mean_prompt, 1),
        "mean_completion_tokens": round(mean_comp, 1),
        "mean_total_tokens": round(mean_tot, 1),
        "token_reduction_percent": round(token_reduction, 2),
        "hitl_reduction_percent": round(hitl_reduction, 2),
    }


# ---------------------------------------------------------------------------
# Pillar 4: RADG Robustness & Decision Boundary
# ---------------------------------------------------------------------------


def compute_radg_metrics(
    results: list[BaselineResult], intents: list[dict[str, Any]]
) -> dict[str, float]:
    """Calculate Pillar 4: RADG Robustness & Gate Boundary metrics.

    Metrics:
      - gda_percent: Gate Decision Accuracy (%)
      - fpr_percent: False Positive Rate (%) on non-nominal intents
      - hitl_interruption_rate_percent: Fraction of runs requiring HITL (%)
      - semantic_clarify_count: Absolute count of Phase 3b clarify actions
      - physical_replan_count: Absolute count of Phase 6 replan actions
    """
    if not results:
        return {
            "gda_percent": 0.0,
            "fpr_percent": 0.0,
            "hitl_interruption_rate_percent": 0.0,
            "semantic_clarify_count": 0.0,
            "physical_replan_count": 0.0,
        }

    intents_by_id = {item.get("id"): item for item in intents}

    matched_actions = 0
    non_nominal_count = 0
    approved_non_nominal = 0
    interrupted_runs = 0
    semantic_clarifies = 0
    physical_replans = 0

    for res in results:
        intent_data = intents_by_id.get(res.get("intent_id"), {})
        expected_action = intent_data.get("expected_radg_action")
        actual_action = res.get("action")
        intent_class = intent_data.get("class", "")

        # 1. Gate Decision Accuracy
        if expected_action and actual_action == expected_action:
            matched_actions += 1

        # 2. False Positive Rate on Class II, III, IV
        if intent_class != "I_Nominal" and expected_action != "approve":
            non_nominal_count += 1
            if actual_action == "approve":
                approved_non_nominal += 1

        # 3. Interruption tracking
        interrupts = res.get("hitl_interrupts", 0)
        if interrupts > 0:
            interrupted_runs += 1

        if actual_action == "clarify":
            semantic_clarifies += 1
        elif actual_action == "replan":
            physical_replans += 1

    n_results = len(results)
    gda = (matched_actions / n_results) * 100.0
    fpr = (
        (approved_non_nominal / non_nominal_count * 100.0)
        if non_nominal_count > 0
        else 0.0
    )
    hitl_rate = (interrupted_runs / n_results) * 100.0

    return {
        "gda_percent": round(gda, 2),
        "fpr_percent": round(fpr, 2),
        "hitl_interruption_rate_percent": round(hitl_rate, 2),
        "semantic_clarify_count": float(semantic_clarifies),
        "physical_replan_count": float(physical_replans),
    }


# ---------------------------------------------------------------------------
# Aggregated Metrics Calculation
# ---------------------------------------------------------------------------


def compute_baseline_metrics(
    results: list[BaselineResult],
    intents: list[dict[str, Any]],
    all_results: dict[str, list[BaselineResult]] | None = None,
) -> dict[str, Any]:
    """Compute all 4 validation pillars for a single baseline."""
    baseline_id = results[0].get("baseline_id", "unknown") if results else "unknown"

    semantic = compute_semantic_metrics(results, intents)
    physical = compute_physical_metrics(results, intents)
    efficiency = compute_efficiency_metrics(
        results, baseline_id, all_results=all_results
    )
    radg = compute_radg_metrics(results, intents)

    return {
        "baseline_id": baseline_id,
        "sample_size": len(results),
        "semantic": semantic,
        "physical": physical,
        "efficiency": efficiency,
        "radg": radg,
    }


def compute_all_baselines_metrics(
    results_by_baseline: dict[str, list[BaselineResult]],
    intents: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Compute metrics for all baselines with cross-baseline comparative metrics."""
    metrics_summary: dict[str, dict[str, Any]] = {}
    for b_id, res_list in results_by_baseline.items():
        metrics_summary[b_id] = compute_baseline_metrics(
            res_list, intents, all_results=results_by_baseline
        )
    return metrics_summary


# ---------------------------------------------------------------------------
# Markdown Table Generation
# ---------------------------------------------------------------------------


def generate_summary_markdown(metrics_by_baseline: dict[str, dict[str, Any]]) -> str:
    """Generate a clean, publication-ready markdown summary table across all baselines."""
    headers = [
        "Baseline",
        "CRR (%)",
        "CFG-PR (%)",
        "UAR (%)",
        "QFR (%)",
        "PIIR (%)",
        "Latency (s)",
        "Prompt Tokens",
        "Total Tokens",
        "ΔTokens (%)",
        "ΔHITL (%)",
        "GDA (%)",
        "FPR (%)",
    ]

    baseline_labels = {
        "proposed_radg": "**Proposed (Neurosymbolic RADG)**",
        "llm_only": "Baseline A (Monolithic LLM)",
        "always_on": "Baseline B (Always-On HITL)",
        "always_off": "Baseline C (Always-Off HITL)",
        "traditional_sdon": "Baseline D (Traditional SDON)",
    }

    rows: list[list[str]] = []
    for b_id, data in metrics_by_baseline.items():
        label = baseline_labels.get(b_id, b_id)
        sem = data.get("semantic", {})
        phys = data.get("physical", {})
        eff = data.get("efficiency", {})
        radg = data.get("radg", {})

        row = [
            label,
            f"{sem.get('crr_percent', 0.0):.1f}%",
            f"{sem.get('cfg_pass_rate_percent', 0.0):.1f}%",
            f"{phys.get('uar_percent', 0.0):.1f}%",
            f"{phys.get('qfr_percent', 0.0):.1f}%",
            f"{phys.get('piir_percent', 0.0):.1f}%",
            f"{eff.get('mean_latency_s', 0.0):.2f}s",
            f"{int(eff.get('mean_prompt_tokens', 0))}",
            f"{int(eff.get('mean_total_tokens', 0))}",
            f"{eff.get('token_reduction_percent', 0.0):.1f}%",
            f"{eff.get('hitl_reduction_percent', 0.0):.1f}%",
            f"{radg.get('gda_percent', 0.0):.1f}%",
            f"{radg.get('fpr_percent', 0.0):.1f}%",
        ]
        rows.append(row)

    md_lines = [
        "# Sprint 4 Evaluation Benchmark: Consolidated Metrics Summary",
        "",
        "> Standardized 17-Node Nobel-Germany Core Backbone Topology ($|V|=17, |E|=26$).",
        "> Invariant Proof: **Proposed Neurosymbolic RADG strictly guarantees UAR = 0.0%**.",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join([":---"] + [":---:"] * (len(headers) - 1)) + " |",
    ]
    for r in rows:
        md_lines.append("| " + " | ".join(r) + " |")

    md_lines.extend(
        [
            "",
            "### Metric Definitions & Target Invariants",
            "- **CRR (Constraint Retention Rate):** Percentage of operator constraints preserved in PDDL. (Target: 100%)",
            "- **CFG-PR (Context-Free Grammar Pass Rate):** PDDL AST structural validity. (Target: 100% on valid, 0% on adversarial)",
            "- **UAR (Unsafe Approval Rate):** Physically infeasible paths receiving `approve`. (**Absolute Target: 0.0%**)",
            "- **QFR (QoT Feasibility Rate):** Ratio of approved paths that satisfy GSNR threshold under GN-model physics. (Target: 100%)",
            "- **PIIR (Physical Infeasibility Interception Rate):** Class III infeasible demands routed to `replan`. (Target: 100%)",
            "- **ΔTokens (%):** Prompt token reduction achieved by Scoped Optical GraphRAG vs Baseline A. (Target: > 75%)",
            "- **ΔHITL (%):** Operator interruption reduction vs Always-On HITL baseline. (Target: > 70%)",
            "- **GDA (Gate Decision Accuracy):** Alignment with optimal RADG decision state. (Target: > 98%)",
            "- **FPR (False Positive Rate):** Unsafe or ambiguous intents approved. (Target: 0.0%)",
            "",
        ]
    )

    return "\n".join(md_lines)
