"""Evaluation metrics across the Four Core Validation Pillars."""

from __future__ import annotations

from typing import Any

from src.core.symbolic_solver import _parse_pddl_constraints


def compute_constraint_retention(
    explicit_constraints: dict[str, Any],
    pddl_text: str | None,
) -> dict[str, Any]:
    """Calculate Constraint Retention Rate (CRR) for a single demand.

    Compares ground-truth explicit constraints against constraints extracted from PDDL.
    """
    if not explicit_constraints:
        return {
            "explicit_count": 0,
            "preserved_count": 0,
            "crr": None,
            "details": {},
        }

    extracted = _parse_pddl_constraints(pddl_text or "")
    explicit_count = 0
    preserved_count = 0
    details: dict[str, bool] = {}

    # 1. min_gsnr
    if "min_gsnr" in explicit_constraints:
        explicit_count += 1
        target_gsnr = float(explicit_constraints["min_gsnr"])
        matched = (
            extracted.get("min_gsnr") is not None
            and abs(float(extracted["min_gsnr"]) - target_gsnr) < 0.1
        )
        if matched:
            preserved_count += 1
        details["min_gsnr"] = matched

    # 2. bandwidth
    if "bandwidth" in explicit_constraints:
        explicit_count += 1
        target_bw = int(explicit_constraints["bandwidth"])
        matched = extracted.get("bandwidth") == target_bw
        if matched:
            preserved_count += 1
        details["bandwidth"] = matched

    # 3. max_hops
    if "max_hops" in explicit_constraints:
        explicit_count += 1
        target_hops = int(explicit_constraints["max_hops"])
        matched = extracted.get("max_hops") == target_hops
        if matched:
            preserved_count += 1
        details["max_hops"] = matched

    # 4. avoid_nodes
    if "avoid_nodes" in explicit_constraints:
        target_nodes = explicit_constraints["avoid_nodes"]
        extracted_avoid = [n.lower() for n in extracted.get("avoid_nodes", [])]
        for node in target_nodes:
            explicit_count += 1
            if node == "ALL":
                matched = "all" in extracted_avoid or bool(extracted_avoid)
            else:
                matched = node.lower() in extracted_avoid
            if matched:
                preserved_count += 1
            details[f"avoid_{node}"] = matched

    crr = (preserved_count / explicit_count) if explicit_count > 0 else None
    return {
        "explicit_count": explicit_count,
        "preserved_count": preserved_count,
        "crr": crr,
        "details": details,
    }


def compute_pillar_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate evaluation metrics across the Four Core Validation Pillars."""
    n_total = len(results)
    if n_total == 0:
        return {}

    # --- Pillar 1: Semantic Translation Accuracy ---
    total_explicit = sum(r.get("crr_info", {}).get("explicit_count", 0) for r in results)
    total_preserved = sum(r.get("crr_info", {}).get("preserved_count", 0) for r in results)
    crr_rate = (total_preserved / total_explicit * 100.0) if total_explicit > 0 else 100.0

    operable_demands = [r for r in results if r.get("class") in ("I_Nominal", "III_Infeasible")]
    operable_explicit = sum(r.get("crr_info", {}).get("explicit_count", 0) for r in operable_demands)
    operable_preserved = sum(r.get("crr_info", {}).get("preserved_count", 0) for r in operable_demands)
    operable_crr_rate = (operable_preserved / operable_explicit * 100.0) if operable_explicit > 0 else 100.0

    valid_cfg_count = sum(1 for r in results if r.get("pddl_valid") is True)
    cfg_pr = (valid_cfg_count / n_total) * 100.0

    agreements = [r.get("semantic_agreement") for r in results if r.get("semantic_agreement") is not None]
    mean_agreement = (sum(agreements) / len(agreements)) if agreements else 0.0

    well_formed_agreements = [
        r.get("semantic_agreement") for r in operable_demands if r.get("semantic_agreement") is not None
    ]
    mean_well_formed_agreement = (
        (sum(well_formed_agreements) / len(well_formed_agreements)) if well_formed_agreements else 0.0
    )

    ambiguous_demands = [r for r in results if r.get("class") in ("II_Ambiguous", "IV_Adversarial")]
    ambiguous_divergence_caught = sum(1 for r in ambiguous_demands if r.get("initial_action") == "clarify")
    ambiguity_catch_rate = (
        (ambiguous_divergence_caught / len(ambiguous_demands) * 100.0) if ambiguous_demands else 100.0
    )

    # --- Pillar 2: Physical Feasibility ---
    approved_demands = [r for r in results if r.get("initial_action") == "approve"]
    unfeasible_approved_count = sum(1 for r in approved_demands if r.get("is_unfeasible_approval"))
    uar = (unfeasible_approved_count / len(approved_demands) * 100.0) if approved_demands else 0.0

    class_3_demands = [r for r in results if r.get("class") == "III_Infeasible"]
    class_3_replan_count = sum(1 for r in class_3_demands if r.get("initial_action") == "replan")
    piir = (class_3_replan_count / len(class_3_demands) * 100.0) if class_3_demands else 100.0

    # --- Pillar 3: Orchestration & Resource Efficiency ---
    completed_count = sum(1 for r in results if r.get("execution_status", "completed") == "completed")
    tcr = (completed_count / n_total) * 100.0
    timeout_count = sum(1 for r in results if r.get("execution_status") == "timeout")
    max_turns_count = sum(1 for r in results if r.get("execution_status") == "max_turns_exceeded")

    mean_latency = sum(r.get("total_elapsed_seconds", 0.0) for r in results) / n_total
    total_tokens = sum(r.get("total_tokens", 0) for r in results)
    mean_tokens = total_tokens / n_total
    total_hitl_interrupts = sum(r.get("hitl_count", 0) for r in results)
    mean_hitl = total_hitl_interrupts / n_total

    # --- Pillar 4: RADG Robustness & Decision Boundary Integrity ---
    correct_gate_count = sum(1 for r in results if r.get("success"))
    gda = (correct_gate_count / n_total) * 100.0

    risky_demands = [r for r in results if r.get("class") in ("II_Ambiguous", "III_Infeasible", "IV_Adversarial")]
    false_positives = sum(1 for r in risky_demands if r.get("initial_action") == "approve")
    fpr = (false_positives / len(risky_demands) * 100.0) if risky_demands else 0.0

    interrupted_demands = [r for r in results if r.get("hitl_count", 0) > 0]
    true_interrupts = sum(
        1 for r in interrupted_demands if r.get("class") in ("II_Ambiguous", "III_Infeasible", "IV_Adversarial")
    )
    precision_hitl = (true_interrupts / len(interrupted_demands) * 100.0) if interrupted_demands else 100.0

    return {
        "pillar_1": {
            "crr_rate": round(crr_rate, 2),
            "operable_crr_rate": round(operable_crr_rate, 2),
            "total_explicit_constraints": total_explicit,
            "total_preserved_constraints": total_preserved,
            "operable_explicit": operable_explicit,
            "operable_preserved": operable_preserved,
            "cfg_pass_rate": round(cfg_pr, 2),
            "mean_semantic_agreement": round(mean_agreement, 3),
            "mean_well_formed_agreement": round(mean_well_formed_agreement, 3),
            "ambiguity_catch_rate": round(ambiguity_catch_rate, 2),
        },
        "pillar_2": {
            "uar_rate": round(uar, 2),
            "unfeasible_approved_count": unfeasible_approved_count,
            "total_approved_count": len(approved_demands),
            "piir_rate": round(piir, 2),
            "class_3_replan_count": class_3_replan_count,
            "class_3_total": len(class_3_demands),
        },
        "pillar_3": {
            "task_completion_rate": round(tcr, 2),
            "completed_demands_count": completed_count,
            "timeout_demands_count": timeout_count,
            "max_turns_exceeded_count": max_turns_count,
            "mean_e2e_latency_seconds": round(mean_latency, 2),
            "total_tokens_consumed": total_tokens,
            "mean_tokens_per_intent": round(mean_tokens, 1),
            "total_hitl_interrupts": total_hitl_interrupts,
            "mean_hitl_turns": round(mean_hitl, 2),
        },
        "pillar_4": {
            "gda_rate": round(gda, 2),
            "correct_gate_count": correct_gate_count,
            "total_count": n_total,
            "fpr_rate": round(fpr, 2),
            "false_positives_count": false_positives,
            "selective_hitl_precision": round(precision_hitl, 2),
            "total_interrupted_count": len(interrupted_demands),
        },
    }
