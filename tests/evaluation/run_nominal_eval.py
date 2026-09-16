"""Automated & Reproducible Evaluation Harness for Nominal Intents (V5 RADG Pipeline).

Evaluates the 5 Nominal Intents from tests/evaluation/test_corpus_compact.json.
Enforces a 120.0s request timeout, automated HITL follow-up handling, and exports
complete telemetry to tests/evaluation/results/ (JSON, CSV, Markdown).

Usage:
    uv run python tests/evaluation/run_nominal_eval.py
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
    intent_text = item["intent_text"]
    expected_radg = item.get("expected_radg_action", "approve")

    print(f"\n{'='*70}")
    print(f"[{item_id}] Intent: \"{intent_text}\"")
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

    return {
        "id": item_id,
        "intent_text": intent_text,
        "class": item.get("class", "I_Nominal"),
        "expected_radg_action": expected_radg,
        "initial_action": initial_action,
        "final_action": final_action,
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
        description="MultiAgentON - Nominal Intents Evaluation Harness"
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
    print("MultiAgentON: Sprint 4 Nominal Intents Evaluation Runner")
    print(f"Provider: {args.provider} | Model: {args.model}")
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

    nominal_items = [it for it in corpus if it.get("class") == "I_Nominal"]
    print(f"Loaded {len(nominal_items)} nominal intents from test_corpus_compact.json.\n")

    results = []
    for item in nominal_items:
        res = evaluate_single_intent(item, timeout=resolved_timeout)
        results.append(res)

    # Save JSON
    json_path = RESULTS_DIR / "nominal_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[✓] Raw telemetry exported: {json_path}")

    # Save CSV
    csv_path = RESULTS_DIR / "nominal_results.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id",
            "intent_text",
            "expected_action",
            "initial_action",
            "final_action",
            "passed_first_try",
            "hitl_count",
            "elapsed_seconds",
            "usem_score",
            "pddl_valid",
            "radg_decision",
        ])
        for r in results:
            writer.writerow([
                r["id"],
                r["intent_text"],
                r["expected_radg_action"],
                r["initial_action"],
                r["final_action"],
                r["passed_first_try"],
                r["hitl_count"],
                r["total_elapsed_seconds"],
                r["usem_score"],
                r["pddl_valid"],
                r["radg_decision"],
            ])
    print(f"[✓] Tabular CSV exported: {csv_path}")

    # Save Markdown Summary
    md_path = RESULTS_DIR / "nominal_summary.md"
    passed_count = sum(1 for r in results if r["passed_first_try"])
    total_count = len(results)
    avg_latency = sum(r["total_elapsed_seconds"] for r in results) / max(1, total_count)

    md_content = [
        "# Nominal Intents Evaluation Summary (V5 Neurosymbolic Pipeline)",
        "",
        f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **LLM Provider:** `{args.provider}`",
        f"- **Model Evaluated:** `{args.model}`",
        f"- **Total Nominal Demands:** {total_count}",
        f"- **Autonomous Pass Rate (First Try):** {passed_count}/{total_count} ({passed_count/total_count*100:.1f}%)",
        f"- **Intents Requiring HITL Follow-Up:** {total_count - passed_count}/{total_count}",
        f"- **Mean End-to-End Latency:** {avg_latency:.2f}s",
        f"- **Per-Request Timeout Guard:** {resolved_timeout}s",
        "",
        "## Detailed Results Matrix",
        "",
        "| ID | Intent | Expected | Initial Action | Final Action | 1st Try? | HITL Turns | Latency | $U_{sem}$ | CFG Valid | RADG Decision |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | :---: |",
    ]

    for r in results:
        status_badge = "✓ PASS" if r["passed_first_try"] else "⚠️ HITL"
        cfg_badge = "✓" if r["pddl_valid"] else "✗"
        usem_val = f"{r['usem_score']:.3f}" if r["usem_score"] is not None else "N/A"
        radg_val = r["radg_decision"] or "None"
        md_content.append(
            f"| `{r['id']}` | \"{r['intent_text'][:45]}...\" | `{r['expected_radg_action']}` | "
            f"`{r['initial_action']}` | `{r['final_action']}` | {status_badge} | "
            f"{r['hitl_count']} | {r['total_elapsed_seconds']:.2f}s | {usem_val} | {cfg_badge} | `{radg_val}` |"
        )

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_content) + "\n")
    print(f"[✓] Summary Markdown exported: {md_path}")


if __name__ == "__main__":
    main()
