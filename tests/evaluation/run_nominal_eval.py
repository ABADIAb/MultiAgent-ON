"""Automated & Reproducible Evaluation Harness for Neurosymbolic Intent Planning (V5 RADG Pipeline).

Evaluates the benchmark intents from tests/evaluation/test_corpus_compact.json
across all four risk classes:
  - Class I: Nominal (expected initial action: approve)
  - Class II: Ambiguous (expected initial action: clarify)
  - Class III: Infeasible (expected initial action: replan)
  - Class IV: Adversarial (expected initial action: clarify or replan)

Enforces per-request timeout guards, automated HITL follow-up handling, and exports
complete telemetry to tests/evaluation/results/ (JSON, CSV, Markdown).

Usage:
    uv run python tests/evaluation/run_nominal_eval.py
    uv run python tests/evaluation/run_nominal_eval.py --class all
    uv run python tests/evaluation/run_nominal_eval.py --class I_Nominal
    uv run python tests/evaluation/run_nominal_eval.py --id intent_amb_01
    uv run python tests/evaluation/run_nominal_eval.py --model qwen2.5:3b --provider ollama
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
from src.services.testbed_client import MockTestbedClient  # noqa: E402

# Standardized follow-up response for automated recovery upon HITL interrupts
STANDARD_FOLLOW_UP_INTENT = "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."
RESULTS_DIR = PROJECT_ROOT / "tests" / "evaluation" / "results"
CORPUS_PATH = PROJECT_ROOT / "tests" / "evaluation" / "test_corpus_compact.json"

logging.basicConfig(level=logging.WARNING)


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

    print(f"\n{'='*70}")
    print(f"[{item_id}] ({item_class}) Intent: \"{intent_text}\"")
    print(f"Target RADG Action: {expected_radg}")
    print(f"{'-'*70}")

    checkpointer = InMemorySaver(
        serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
    )
    graph = compile_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": f"eval-{item_id}"}}

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
        "usem_score": diagnostics.get("usem_score"),
        "usem_passed": diagnostics.get("usem_passed"),
        "pddl_valid": diagnostics.get("pddl_valid"),
        "radg_decision": diagnostics.get("radg_decision"),
        "turn_telemetry": turn_telemetry,
        "diagnostics": diagnostics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="MultiAgentON - Neurosymbolic Intent Planning Evaluation Harness"
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
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    resolved_timeout = resolve_llm_timeout(args.timeout)

    print("=" * 70)
    print("MultiAgentON: Sprint 4 Neurosymbolic Evaluation Runner")
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
        res = evaluate_single_intent(item, timeout=resolved_timeout)
        results.append(res)

    run_timestamp = time.strftime("%Y%m%d_%H%M%S")

    # 1. JSON Export
    json_path = RESULTS_DIR / "evaluation_results.json"
    ts_json_path = RESULTS_DIR / f"evaluation_results_{run_timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    with open(ts_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # If nominals are included, also maintain nominal_results.json
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
        "usem_score",
        "pddl_valid",
        "radg_decision",
    ]
    for target_csv in (csv_path, ts_csv_path):
        with open(target_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            for r in results:
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
                    r["usem_score"],
                    r["pddl_valid"],
                    r["radg_decision"],
                ])

    if nominal_subset:
        with open(RESULTS_DIR / "nominal_results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(csv_headers)
            for r in nominal_subset:
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
                    r["usem_score"],
                    r["pddl_valid"],
                    r["radg_decision"],
                ])

    print(f"[✓] Tabular CSV exported: {csv_path}")
    print(f"[✓] Run CSV snapshot: {ts_csv_path}")

    # 3. Markdown Summary Export
    md_path = RESULTS_DIR / "evaluation_summary.md"
    ts_md_path = RESULTS_DIR / f"evaluation_summary_{run_timestamp}.md"

    passed_count = sum(1 for r in results if r["success"])
    total_count = len(results)
    pass_pct = (passed_count / total_count * 100) if total_count > 0 else 0.0
    avg_latency = sum(r["total_elapsed_seconds"] for r in results) / max(1, total_count)

    # Class breakdown
    classes = ["I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"]
    class_stats: dict[str, dict[str, Any]] = {}
    for c in classes:
        c_items = [r for r in results if r["class"] == c]
        if c_items:
            c_pass = sum(1 for r in c_items if r["success"])
            class_stats[c] = {
                "total": len(c_items),
                "passed": c_pass,
                "pct": (c_pass / len(c_items)) * 100,
            }

    md_content = [
        "# Neurosymbolic Intent Planning Evaluation Summary (V5 Pipeline)",
        "",
        f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Run ID:** `{run_timestamp}`",
        f"- **LLM Provider:** `{args.provider}`",
        f"- **Model Evaluated:** `{args.model}`",
        f"- **Total Demands Evaluated:** {total_count}",
        f"- **Overall Risk Gate Accuracy:** {passed_count}/{total_count} ({pass_pct:.1f}%)",
        f"- **Mean End-to-End Latency:** {avg_latency:.2f}s",
        f"- **Per-Request Timeout Guard:** {resolved_timeout}s",
        "",
        "## Class-by-Class Risk Gate Breakdown",
        "",
        "| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate |",
        "| :---: | :--- | :---: | :---: | :---: | :---: |",
    ]

    class_meta = {
        "I_Nominal": ("Nominal", "approve"),
        "II_Ambiguous": ("Ambiguous", "clarify"),
        "III_Infeasible": ("Physically Infeasible", "replan"),
        "IV_Adversarial": ("Adversarial", "clarify / replan"),
    }

    for c in classes:
        if c in class_stats:
            cat_name, exp_act = class_meta[c]
            st = class_stats[c]
            md_content.append(
                f"| `{c}` | {cat_name} | {st['total']} | `{exp_act}` | {st['passed']}/{st['total']} | {st['pct']:.1f}% |"
            )

    md_content.extend([
        "",
        "## Detailed Results Matrix",
        "",
        "| ID | Class | Intent | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | $U_{sem}$ | CFG Valid | RADG Decision |",
        "| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | :---: |",
    ])

    for r in results:
        status_badge = "✓ PASS" if r["success"] else "✗ FAIL"
        cfg_badge = "✓" if r["pddl_valid"] else "✗"
        usem_val = f"{r['usem_score']:.3f}" if r["usem_score"] is not None else "N/A"
        radg_val = r["radg_decision"] or "None"
        md_content.append(
            f"| `{r['id']}` | `{r['class'].split('_')[0]}` | \"{r['intent_text'][:40]}...\" | "
            f"`{r['expected_radg_action']}` | `{r['initial_action']}` | `{r['final_action']}` | "
            f"{status_badge} | {r['hitl_count']} | {r['total_elapsed_seconds']:.2f}s | {usem_val} | "
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


if __name__ == "__main__":
    main()
