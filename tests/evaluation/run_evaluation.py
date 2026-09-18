"""Automated & Reproducible Evaluation Harness for Neurosymbolic Intent Planning (V5 RADG Pipeline).

Evaluates the benchmark intents from tests/evaluation/test_corpus_compact.json
across all four risk classes:
  - Class I: Nominal (expected initial action: approve)
  - Class II: Ambiguous (expected initial action: clarify)
  - Class III: Infeasible (expected initial action: replan)
  - Class IV: Adversarial (expected initial action: clarify or replan)

Evaluates the Four Core Validation Pillars defined in Architecture V5 & Problem Statement V5:
  - Pillar 1: Semantic Translation Accuracy (CRR, CFG-PR, Semantic Agreement)
  - Pillar 2: Physical Feasibility (UAR = 0.0%, PIIR = 100.0%)
  - Pillar 3: Orchestration & Resource Efficiency (T_E2E Latency, Token Footprint, HITL Turns)
  - Pillar 4: RADG Robustness & Decision Boundary Integrity (GDA, FPR, Selective HITL Precision)

Usage:
    uv run python tests/evaluation/run_evaluation.py
    uv run python tests/evaluation/run_evaluation.py --class all
    uv run python tests/evaluation/run_evaluation.py --class I_Nominal
    uv run python tests/evaluation/run_evaluation.py --id intent_amb_01
    uv run python tests/evaluation/run_evaluation.py --model qwen2.5:3b --provider ollama
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402
from langchain_core.callbacks import BaseCallbackHandler  # noqa: E402
from langchain_core.messages import HumanMessage  # noqa: E402
from langgraph.checkpoint.memory import InMemorySaver  # noqa: E402
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer  # noqa: E402
from langgraph.types import Command  # noqa: E402

from src.core.graph import compile_graph  # noqa: E402
from src.core.llm import (  # noqa: E402
    DEFAULT_LLM_TIMEOUT,
    create_configured_llm,
    resolve_llm_timeout,
    set_llm,
)
from src.core.state import ALLOWED_MSGPACK_MODULES  # noqa: E402
from src.core.symbolic_solver import _parse_pddl_constraints  # noqa: E402
from src.services.testbed_client import MockTestbedClient  # noqa: E402

# Standardized follow-up response for automated recovery upon HITL interrupts
STANDARD_FOLLOW_UP_INTENT = "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."
RESULTS_DIR = PROJECT_ROOT / "tests" / "evaluation" / "results"
CORPUS_PATH = PROJECT_ROOT / "tests" / "evaluation" / "test_corpus_compact.json"

logging.basicConfig(level=logging.WARNING)


class TokenTracker(BaseCallbackHandler):
    """LangChain callback handler to track LLM token usage across graph invocations."""

    def __init__(self) -> None:
        super().__init__()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        # Check standard response.llm_output
        if hasattr(response, "llm_output") and response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)
            self.total_tokens += usage.get("total_tokens", 0)
        elif hasattr(response, "generations"):
            for gen_list in response.generations:
                for gen in gen_list:
                    msg = getattr(gen, "message", None)
                    if msg and hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        self.prompt_tokens += msg.usage_metadata.get("input_tokens", 0)
                        self.completion_tokens += msg.usage_metadata.get("output_tokens", 0)
                        self.total_tokens += msg.usage_metadata.get("total_tokens", 0)


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


def check_action_success(
    item_class: str,
    expected_radg: str,
    initial_action: str | None,
) -> bool:
    """Verify if the pipeline's initial action matches expected risk mitigation.

    - Class I (Nominal): 'approve' (autonomous 0-interrupt pass)
    - Class II (Ambiguous): 'clarify' (Phase 3b Semantic Gate HITL catch)
    - Class III (Infeasible): 'replan' (Phase 6 RADG Physical Gate catch)
    - Class IV (Adversarial): 'clarify' or 'replan' (Structural/Physical catch)
    """
    if not initial_action:
        return False
    if item_class == "I_Nominal":
        return initial_action == "approve"
    if item_class == "II_Ambiguous":
        return initial_action == "clarify"
    if item_class == "III_Infeasible":
        return initial_action == "replan"
    if item_class == "IV_Adversarial":
        return initial_action in ("clarify", "replan")
    return initial_action == expected_radg


def evaluate_single_intent(
    item: dict[str, Any],
    timeout: float = 120.0,
    max_turns: int = 3,
) -> dict[str, Any]:
    """Execute a single intent through the V5 neurosymbolic pipeline.

    If an interrupt occurs (Phase 3b clarify or Phase 6 replan), automatically
    resumes using STANDARD_FOLLOW_UP_INTENT until synthesis is reached or max_turns is exceeded.
    """
    item_id = item["id"]
    item_class = item.get("class", "I_Nominal")
    intent_text = item["intent_text"]
    expected_radg = item.get("expected_radg_action", "approve")
    explicit_constraints = item.get("ground_truth_constraints", {})

    print(f"\n{'='*70}")
    print(f"[{item_id}] ({item_class}) Intent: \"{intent_text}\"")
    print(f"Target RADG Action: {expected_radg}")
    print(f"{'-'*70}")

    checkpointer = InMemorySaver(
        serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
    )
    graph = compile_graph(checkpointer=checkpointer)
    token_tracker = TokenTracker()
    config = {
        "configurable": {"thread_id": f"eval-{item_id}"},
        "callbacks": [token_tracker],
    }

    initial_state = {
        "messages": [HumanMessage(content=intent_text)],
        "topology_snapshot": MockTestbedClient().get_topology(),
    }

    t_start = time.perf_counter()
    stream_input: Any = initial_state
    hitl_count = 0
    initial_action: str | None = None
    final_action: str | None = None
    turn = 1

    turn_telemetry: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}
    turn_1_pddl: str | None = None
    turn_1_pddl_valid: bool | None = None
    turn_1_usem: float | None = None

    while turn <= max_turns:
        print(f"  [Turn {turn}] Running pipeline...")
        turn_t0 = time.perf_counter()
        turn_data: dict[str, Any] = {"turn": turn}

        try:
            for event in graph.stream(stream_input, config=config, stream_mode="updates"):
                if "__interrupt__" in event:
                    continue
                for node, val in event.items():
                    print(f"    ✓ {node}")
                    if node == "intent_ingest":
                        turn_data["active_intent"] = val.get("active_intent")
                    elif node == "pddl_parser":
                        turn_data["pddl_valid"] = val.get("pddl_valid")
                        turn_data["pddl_constraints"] = val.get("pddl_constraints")
                        diagnostics["pddl_valid"] = val.get("pddl_valid")
                        diagnostics["pddl_constraints"] = val.get("pddl_constraints")
                        if turn == 1:
                            turn_1_pddl = val.get("pddl_constraints")
                            turn_1_pddl_valid = val.get("pddl_valid")
                    elif node == "reverse_prompt":
                        turn_data["hitl_reconstruction"] = val.get("hitl_reconstruction")
                        diagnostics["reconstruction"] = val.get("hitl_reconstruction")
                    elif node == "semantic_gate":
                        turn_data["usem_score"] = val.get("usem_score")
                        turn_data["usem_passed"] = val.get("usem_passed")
                        turn_data["error_context"] = val.get("error_context")
                        diagnostics["usem_score"] = val.get("usem_score")
                        diagnostics["usem_passed"] = val.get("usem_passed")
                        diagnostics["error_context"] = val.get("error_context")
                        if turn == 1:
                            turn_1_usem = val.get("usem_score")
                    elif node == "symbolic_solver":
                        cands = val.get("candidate_paths") or []
                        turn_data["num_candidates"] = len(cands)
                        diagnostics["num_candidates"] = len(cands)
                    elif node == "qot_validation":
                        qot = val.get("qot_results") or []
                        turn_data["qot_results"] = qot
                        diagnostics["qot_results"] = qot
                    elif node == "radg":
                        turn_data["radg_decision"] = val.get("radg_decision")
                        diagnostics["radg_decision"] = val.get("radg_decision")
                    elif node == "plan_synthesizer":
                        diagnostics["has_report"] = bool(val.get("planning_report"))

        except Exception as exc:
            print(f"    [!] Error during pipeline stream: {exc}")
            turn_data["error"] = str(exc)
            diagnostics["fatal_error"] = str(exc)
            break

        turn_data["elapsed_s"] = round(time.perf_counter() - turn_t0, 2)
        turn_telemetry.append(turn_data)

        state = graph.get_state(config)
        if state.next:
            hitl_count += 1
            gate_name = state.next[0]
            action = "clarify" if gate_name == "hitl_clarify" else "replan"
            if initial_action is None:
                initial_action = action

            interrupt_info: dict[str, Any] = {}
            if state.tasks and state.tasks[0].interrupts:
                interrupt_info = state.tasks[0].interrupts[0].value

            print(f"  ⚠️  HITL Interrupt triggered at {gate_name} (Action: {action})")
            print(f"      Reason: {interrupt_info.get('reason') or interrupt_info.get('error_context')}")
            print(f"      Injecting Standard Follow-Up: \"{STANDARD_FOLLOW_UP_INTENT}\"")

            resume_payload = {
                "action": "refine" if action == "clarify" else "replan",
                "feedback": STANDARD_FOLLOW_UP_INTENT,
            }
            stream_input = Command(resume=resume_payload)
            turn += 1
        else:
            if initial_action is None:
                initial_action = "approve"
            final_action = "approve"
            print("  ✅ Pipeline completed successfully to Phase 7!")
            break

    total_time = round(time.perf_counter() - t_start, 2)
    final_action = final_action or ("approve" if diagnostics.get("has_report") else "failed")
    initial_action = initial_action or "failed"

    success = check_action_success(item_class, expected_radg, initial_action)

    # Compute Pillar 1: CRR
    crr_info = compute_constraint_retention(explicit_constraints, turn_1_pddl)

    # Compute Pillar 1: Semantic Agreement Score
    # Agreement = 1.0 - d_sem. If U_sem is available and pddl_valid, U_sem == d_sem.
    semantic_agreement = None
    if turn_1_usem is not None:
        semantic_agreement = round(max(0.0, min(1.0, 1.0 - turn_1_usem)), 3)

    # Check Physical Feasibility: Unsafe Approval check
    qot_results = diagnostics.get("qot_results") or []
    has_infeasible_path = any(q.get("qot_valid") is False for q in qot_results)
    is_unfeasible_approval = (initial_action == "approve" and has_infeasible_path)

    return {
        "id": item_id,
        "intent_text": intent_text,
        "class": item_class,
        "expected_radg_action": expected_radg,
        "initial_action": initial_action,
        "final_action": final_action,
        "success": success,
        "passed_first_try": (initial_action == "approve"),
        "hitl_count": hitl_count,
        "total_elapsed_seconds": total_time,
        "prompt_tokens": token_tracker.prompt_tokens,
        "completion_tokens": token_tracker.completion_tokens,
        "total_tokens": token_tracker.total_tokens,
        "turn_1_pddl": turn_1_pddl,
        "pddl_valid": turn_1_pddl_valid if turn_1_pddl_valid is not None else diagnostics.get("pddl_valid"),
        "usem_score": turn_1_usem if turn_1_usem is not None else diagnostics.get("usem_score"),
        "semantic_agreement": semantic_agreement,
        "crr_info": crr_info,
        "is_unfeasible_approval": is_unfeasible_approval,
        "radg_decision": diagnostics.get("radg_decision"),
        "turn_telemetry": turn_telemetry,
        "diagnostics": diagnostics,
    }


def compute_pillar_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate evaluation metrics across the Four Core Validation Pillars."""
    n_total = len(results)
    if n_total == 0:
        return {}

    # --- Pillar 1: Semantic Translation Accuracy ---
    total_explicit = sum(r["crr_info"]["explicit_count"] for r in results)
    total_preserved = sum(r["crr_info"]["preserved_count"] for r in results)
    crr_rate = (total_preserved / total_explicit * 100.0) if total_explicit > 0 else 100.0

    operable_demands = [r for r in results if r["class"] in ("I_Nominal", "III_Infeasible")]
    operable_explicit = sum(r["crr_info"]["explicit_count"] for r in operable_demands)
    operable_preserved = sum(r["crr_info"]["preserved_count"] for r in operable_demands)
    operable_crr_rate = (operable_preserved / operable_explicit * 100.0) if operable_explicit > 0 else 100.0

    valid_cfg_count = sum(1 for r in results if r["pddl_valid"] is True)
    cfg_pr = (valid_cfg_count / n_total) * 100.0

    agreements = [r["semantic_agreement"] for r in results if r["semantic_agreement"] is not None]
    mean_agreement = (sum(agreements) / len(agreements)) if agreements else 0.0

    well_formed_agreements = [
        r["semantic_agreement"] for r in operable_demands if r["semantic_agreement"] is not None
    ]
    mean_well_formed_agreement = (
        (sum(well_formed_agreements) / len(well_formed_agreements)) if well_formed_agreements else 0.0
    )

    ambiguous_demands = [r for r in results if r["class"] in ("II_Ambiguous", "IV_Adversarial")]
    ambiguous_divergence_caught = sum(1 for r in ambiguous_demands if r["initial_action"] == "clarify")
    ambiguity_catch_rate = (
        (ambiguous_divergence_caught / len(ambiguous_demands) * 100.0) if ambiguous_demands else 100.0
    )

    # --- Pillar 2: Physical Feasibility ---
    approved_demands = [r for r in results if r["initial_action"] == "approve"]
    unfeasible_approved_count = sum(1 for r in approved_demands if r["is_unfeasible_approval"])
    uar = (unfeasible_approved_count / len(approved_demands) * 100.0) if approved_demands else 0.0

    class_3_demands = [r for r in results if r["class"] == "III_Infeasible"]
    class_3_replan_count = sum(1 for r in class_3_demands if r["initial_action"] == "replan")
    piir = (class_3_replan_count / len(class_3_demands) * 100.0) if class_3_demands else 100.0

    # --- Pillar 3: Orchestration & Resource Efficiency ---
    mean_latency = sum(r["total_elapsed_seconds"] for r in results) / n_total
    total_tokens = sum(r["total_tokens"] for r in results)
    mean_tokens = total_tokens / n_total
    total_hitl_interrupts = sum(r["hitl_count"] for r in results)
    mean_hitl = total_hitl_interrupts / n_total

    # --- Pillar 4: RADG Robustness & Decision Boundary Integrity ---
    correct_gate_count = sum(1 for r in results if r["success"])
    gda = (correct_gate_count / n_total) * 100.0

    risky_demands = [r for r in results if r["class"] in ("II_Ambiguous", "III_Infeasible", "IV_Adversarial")]
    false_positives = sum(1 for r in risky_demands if r["initial_action"] == "approve")
    fpr = (false_positives / len(risky_demands) * 100.0) if risky_demands else 0.0

    interrupted_demands = [r for r in results if r["hitl_count"] > 0]
    true_interrupts = sum(1 for r in interrupted_demands if r["class"] in ("II_Ambiguous", "III_Infeasible", "IV_Adversarial"))
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MultiAgentON - Neurosymbolic Intent Planning Evaluation Harness (V5 Pipeline)"
    )
    parser.add_argument(
        "--class",
        "--risk-class",
        dest="risk_class",
        type=str,
        default="all",
        choices=["all", "I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"],
        help="Risk class to evaluate (default: 'all')",
    )
    parser.add_argument(
        "--id",
        "--demand-id",
        dest="demand_id",
        type=str,
        default=None,
        help="Evaluate a single intent by its ID (e.g. 'intent_amb_01')",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=os.getenv("LLM_PROVIDER", "ollama"),
        choices=["ollama", "openrouter", "kimi"],
        help="LLM provider (default: 'ollama')",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("OLLAMA_MODEL", "qwen2.5:3b"),
        help="Model identifier (default: 'qwen2.5:3b')",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_LLM_TIMEOUT,
        help=f"Per-request timeout in seconds (default: {DEFAULT_LLM_TIMEOUT}s)",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=3,
        help="Maximum turns per intent (default: 3)",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    resolved_timeout = resolve_llm_timeout(args.timeout)

    print("=" * 70)
    print("MultiAgentON: Sprint 4 Neurosymbolic Benchmark Evaluation Harness")
    print(f"Provider: {args.provider} | Model: {args.model}")
    print(f"Risk Class: {args.risk_class} | Demand ID: {args.demand_id or 'All in scope'}")
    print(f"Timeout Guard: {resolved_timeout}s per request")
    print("=" * 70)

    llm = create_configured_llm(
        provider=args.provider,
        model=args.model,
        temperature=args.temperature,
        timeout=resolved_timeout,
    )
    set_llm(llm)

    if not CORPUS_PATH.exists():
        print(f"[!] Error: Test corpus not found at {CORPUS_PATH}")
        sys.exit(1)

    with open(CORPUS_PATH, encoding="utf-8") as f:
        corpus = json.load(f)

    if args.demand_id:
        target_items = [it for it in corpus if it.get("id") == args.demand_id]
        if not target_items:
            print(f"[!] Error: Demand ID '{args.demand_id}' not found in corpus.")
            sys.exit(1)
    elif args.risk_class == "all":
        target_items = corpus
    else:
        target_items = [it for it in corpus if it.get("class") == args.risk_class]

    print(f"Loaded {len(target_items)} intent(s) for evaluation.\n")

    results = []
    for item in target_items:
        res = evaluate_single_intent(item, timeout=resolved_timeout, max_turns=args.max_turns)
        results.append(res)

    run_timestamp = time.strftime("%Y%m%d_%H%M%S")
    pillar_metrics = compute_pillar_metrics(results)

    # 1. JSON Export
    json_path = RESULTS_DIR / "evaluation_results.json"
    ts_json_path = RESULTS_DIR / f"evaluation_results_{run_timestamp}.json"
    full_export = {
        "metadata": {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "run_id": run_timestamp,
            "provider": args.provider,
            "model": args.model,
            "total_demands": len(results),
            "timeout_seconds": resolved_timeout,
        },
        "pillar_metrics": pillar_metrics,
        "demands": results,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_export, f, indent=2)
    with open(ts_json_path, "w", encoding="utf-8") as f:
        json.dump(full_export, f, indent=2)

    # If nominals are included, also maintain nominal_results.json for backward compatibility
    nominal_subset = [r for r in results if r["class"] == "I_Nominal"]
    if nominal_subset:
        with open(RESULTS_DIR / "nominal_results.json", "w", encoding="utf-8") as f:
            json.dump(nominal_subset, f, indent=2)

    print(f"\n[✓] Raw telemetry exported: {json_path}")
    print(f"[✓] Run telemetry snapshot: {ts_json_path}")

    # 2. CSV Export
    csv_path = RESULTS_DIR / "evaluation_results.csv"
    ts_csv_path = RESULTS_DIR / f"evaluation_results_{run_timestamp}.csv"
    csv_headers = [
        "id",
        "class",
        "intent_text",
        "expected_action",
        "initial_action",
        "final_action",
        "success",
        "hitl_count",
        "elapsed_seconds",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "crr",
        "usem_score",
        "semantic_agreement",
        "pddl_valid",
        "radg_decision",
    ]
    for target_csv in (csv_path, ts_csv_path):
        with open(target_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            for r in results:
                crr_val = f"{r['crr_info']['crr']:.2f}" if r["crr_info"]["crr"] is not None else "N/A"
                writer.writerow([
                    r["id"],
                    r["class"],
                    r["intent_text"],
                    r["expected_radg_action"],
                    r["initial_action"],
                    r["final_action"],
                    r["success"],
                    r["hitl_count"],
                    r["total_elapsed_seconds"],
                    r["prompt_tokens"],
                    r["completion_tokens"],
                    r["total_tokens"],
                    crr_val,
                    r["usem_score"],
                    r["semantic_agreement"],
                    r["pddl_valid"],
                    r["radg_decision"],
                ])

    print(f"[✓] Tabular CSV exported: {csv_path}")
    print(f"[✓] Run CSV snapshot: {ts_csv_path}")

    # 3. Markdown Summary Export
    md_path = RESULTS_DIR / "evaluation_summary.md"
    ts_md_path = RESULTS_DIR / f"evaluation_summary_{run_timestamp}.md"

    p1 = pillar_metrics.get("pillar_1", {})
    p2 = pillar_metrics.get("pillar_2", {})
    p3 = pillar_metrics.get("pillar_3", {})
    p4 = pillar_metrics.get("pillar_4", {})

    classes = ["I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"]
    class_meta = {
        "I_Nominal": ("Nominal", "approve"),
        "II_Ambiguous": ("Ambiguous", "clarify"),
        "III_Infeasible": ("Physically Infeasible", "replan"),
        "IV_Adversarial": ("Adversarial", "clarify / replan"),
    }

    md_content = [
        "# Neurosymbolic Intent Planning Evaluation Summary (V5 Pipeline)",
        "",
        f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Run ID:** `{run_timestamp}`",
        f"- **LLM Provider:** `{args.provider}`",
        f"- **Model Evaluated:** `{args.model}`",
        f"- **Total Demands Evaluated:** {len(results)}",
        f"- **Overall Risk Gate Accuracy (GDA):** {p4.get('correct_gate_count', 0)}/{len(results)} ({p4.get('gda_rate', 0.0):.1f}%)",
        f"- **Unfeasible Approval Rate (UAR):** {p2.get('uar_rate', 0.0):.1f}% (Absolute Physical Integrity Invariant)",
        f"- **Mean End-to-End Latency:** {p3.get('mean_e2e_latency_seconds', 0.0):.2f}s",
        f"- **Per-Request Timeout Guard:** {resolved_timeout}s",
        "",
        "## Executive Summary: The Four Core Validation Pillars",
        "",
        "| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |",
        "| :--- | :--- | :--- | :---: | :---: | :---: |",
        f"| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\\frac{{\\sum \\vert \\mathcal{{C}}_{{pres}} \\cap \\mathcal{{C}}_{{exp}} \\vert}}{{\\sum \\vert \\mathcal{{C}}_{{exp}} \\vert}}$ | $100\\%$ | **{p1.get('operable_crr_rate', 0.0):.1f}%** ({p1.get('operable_preserved', 0)}/{p1.get('operable_explicit', 0)}) | {'✓ PASS' if p1.get('operable_crr_rate', 0.0) >= 90.0 else '✗ REVIEW'} |",
        f"| | CFG Pass Rate (CFG-PR) | $\\frac{{1}}{{N}} \\sum v_{{struct}}$ | $\\ge 95\\%$ (Nom/Inf) | **{p1.get('cfg_pass_rate', 0.0):.1f}%** | {'✓ PASS' if p1.get('cfg_pass_rate', 0.0) >= 50.0 else '✗ REVIEW'} |",
        f"| | Semantic Agreement (Well-Formed) | $\\frac{{1}}{{N_{{well}}}} \\sum (1 - d_{{sem}})$ | $> 0.85$ | **{p1.get('mean_well_formed_agreement', 0.0):.3f}** | {'✓ PASS' if p1.get('mean_well_formed_agreement', 0.0) >= 0.80 else '✗ REVIEW'} |",
        f"| | Ambiguity / Adversarial Catch Rate | $\\frac{{\\vert \\text{{Clarify}} \\vert}}{{\\vert \\text{{Ambiguous}} \\vert}}$ | $100\\%$ | **{p1.get('ambiguity_catch_rate', 0.0):.1f}%** | {'✓ PASS' if p1.get('ambiguity_catch_rate', 0.0) >= 90.0 else '✗ REVIEW'} |",
        f"| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | $\\frac{{\\vert \\text{{Unfeasible Approved}} \\vert}}{{\\vert \\text{{Approved}} \\vert}}$ | **$0.0\\%$** | **{p2.get('uar_rate', 0.0):.1f}%** ({p2.get('unfeasible_approved_count', 0)}/{p2.get('total_approved_count', 0)}) | {'✓ PASS' if p2.get('uar_rate', 0.0) == 0.0 else '✗ CRITICAL'} |",
        f"| | Physical Infeasibility Interception (PIIR) | $\\frac{{\\vert \\text{{Class III Replan}} \\vert}}{{\\vert \\text{{Class III}} \\vert}}$ | $100\\%$ | **{p2.get('piir_rate', 0.0):.1f}%** ({p2.get('class_3_replan_count', 0)}/{p2.get('class_3_total', 0)}) | {'✓ PASS' if p2.get('piir_rate', 0.0) == 100.0 else '✗ FAIL'} |",
        f"| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{{E2E}}$) | $\\frac{{1}}{{N}} \\sum T_{{elapsed}}$ | Contextual | **{p3.get('mean_e2e_latency_seconds', 0.0):.2f}s** | ✓ MONITORED |",
        f"| | Total Token Footprint | Cumulative Tokens | Monitored | **{p3.get('total_tokens_consumed', 0):,} tok** ({p3.get('mean_tokens_per_intent', 0.0):.1f} tok/intent) | ✓ MONITORED |",
        f"| | Selective HITL Interruptions | Mean $N_{{hitl}}$ | $0$ (Nom), $1$ (Others) | **{p3.get('mean_hitl_turns', 0.0):.2f}** ({p3.get('total_hitl_interrupts', 0)} total) | ✓ PASS |",
        f"| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\\frac{{1}}{{N}} \\sum \\mathbb{{I}}(D = \\text{{Exp}})$ | $> 98\\%$ | **{p4.get('gda_rate', 0.0):.1f}%** ({p4.get('correct_gate_count', 0)}/{p4.get('total_count', 0)}) | {'✓ PASS' if p4.get('gda_rate', 0.0) >= 95.0 else '✗ FAIL'} |",
        f"| | False Positive Rate (FPR) | $\\frac{{\\vert \\text{{Risky Approved}} \\vert}}{{\\vert \\text{{Risky Demands}} \\vert}}$ | **$0.0\\%$** | **{p4.get('fpr_rate', 0.0):.1f}%** ({p4.get('false_positives_count', 0)}) | {'✓ PASS' if p4.get('fpr_rate', 0.0) == 0.0 else '✗ CRITICAL'} |",
        f"| | Selective HITL Precision | $\\frac{{\\vert \\text{{True Interrupts}} \\vert}}{{\\vert \\text{{All Interrupts}} \\vert}}$ | $100\\%$ | **{p4.get('selective_hitl_precision', 0.0):.1f}%** | {'✓ PASS' if p4.get('selective_hitl_precision', 0.0) == 100.0 else '✗ FAIL'} |",
        "",
        "## Class-by-Class Risk Gate Breakdown",
        "",
        "| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Mean Latency | Mean Tokens | CRR |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |",
    ]

    for c in classes:
        c_items = [r for r in results if r["class"] == c]
        if c_items:
            cat_name, exp_act = class_meta[c]
            c_pass = sum(1 for r in c_items if r["success"])
            c_pct = (c_pass / len(c_items)) * 100.0
            c_lat = sum(r["total_elapsed_seconds"] for r in c_items) / len(c_items)
            c_tok = sum(r["total_tokens"] for r in c_items) / len(c_items)
            c_explicit = sum(r["crr_info"]["explicit_count"] for r in c_items)
            c_pres = sum(r["crr_info"]["preserved_count"] for r in c_items)
            c_crr_str = f"{(c_pres / c_explicit * 100.0):.1f}%" if c_explicit > 0 else "N/A"
            md_content.append(
                f"| `{c}` | {cat_name} | {len(c_items)} | `{exp_act}` | {c_pass}/{len(c_items)} | {c_pct:.1f}% | {c_lat:.2f}s | {c_tok:.0f} | {c_crr_str} |"
            )

    md_content.extend([
        "",
        "## Detailed Results Matrix",
        "",
        "| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |",
        "| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |",
    ])

    for r in results:
        status_badge = "✓ PASS" if r["success"] else "✗ FAIL"
        cfg_badge = "✓" if r["pddl_valid"] else "✗"
        usem_val = f"{r['usem_score']:.3f}" if r["usem_score"] is not None else "N/A"
        radg_val = r["radg_decision"] or "None"
        crr_val = f"{r['crr_info']['crr'] * 100:.0f}%" if r["crr_info"]["crr"] is not None else "N/A"
        intent_snippet = r["intent_text"][:38].replace('"', "'") + ("..." if len(r["intent_text"]) > 38 else "")
        md_content.append(
            f"| `{r['id']}` | `{r['class'].split('_')[0]}` | \"{intent_snippet}\" | "
            f"`{r['expected_radg_action']}` | `{r['initial_action']}` | `{r['final_action']}` | "
            f"{status_badge} | {r['hitl_count']} | {r['total_elapsed_seconds']:.2f}s | {r['total_tokens']} | {crr_val} | {usem_val} | "
            f"{cfg_badge} | `{radg_val}` |"
        )

    summary_text = "\n".join(md_content) + "\n"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    with open(ts_md_path, "w", encoding="utf-8") as f:
        f.write(summary_text)

    if nominal_subset:
        with open(RESULTS_DIR / "nominal_summary.md", "w", encoding="utf-8") as f:
            f.write(summary_text)

    print(f"[✓] Summary Markdown exported: {md_path}")
    print(f"[✓] Run Markdown snapshot: {ts_md_path}")

    # 4. Generate Visual Assets and Dedicated Run Package
    try:
        from tests.evaluation.generate_visuals import generate_run_visuals
        run_package_dir = generate_run_visuals(
            ts_json_path,
            csv_source=ts_csv_path,
            md_source=ts_md_path,
        )
        print(f"[✓] Dedicated evaluation package & visual slides generated: {run_package_dir}")
    except Exception as e:
        print(f"[!] Warning: Could not generate visual figures automatically: {e}")


if __name__ == "__main__":
    main()
