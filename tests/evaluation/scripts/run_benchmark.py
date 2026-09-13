"""Automated Benchmark Execution Harness for Sprint 4.

Iterates over the 100-demand test corpus (test_corpus.json) across the 5 comparative
evaluation baselines over the 17-node Nobel-Germany optical backbone topology.

Key features:
  - Polymorphic execution via tests.evaluation.baselines.run_baseline().
  - Zero modifications to src/ (purely consuming core/ and nodes/).
  - Supports --mock flag for offline, reproducible, token-free validation runs.
  - Exports raw telemetry (JSON and CSV) to results/raw/.
  - Computes all 4 Validation Pillars via metrics.py.
  - Automatically exports summary_table.md and IEEE/PoliMi publication figures via plotter.py.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.llm import create_kimi_llm, set_llm  # noqa: E402
from src.nodes.intent_ingest import IntentSummary  # noqa: E402
from tests.evaluation.baselines import (  # noqa: E402
    BaselineResult,
    list_baselines,
    run_baseline,
)
from tests.evaluation.baselines.llm_only import LLMOnlyOutput  # noqa: E402
from tests.evaluation.scripts.metrics import (  # noqa: E402
    compute_all_baselines_metrics,
    generate_summary_markdown,
)
from tests.evaluation.scripts.plotter import generate_all_figures  # noqa: E402

console = Console()


# ---------------------------------------------------------------------------
# Offline Mock LLM Factory for Dry-Run Benchmarking
# ---------------------------------------------------------------------------


def setup_mock_llm(active_intent: dict[str, Any]) -> None:
    """Configure a dynamic mock LLM tailored to the active intent for deterministic dry-runs."""
    intent_class = active_intent.get("class", "")
    src = active_intent.get("source_node", "Berlin")
    dst = active_intent.get("target_node", "Frankfurt")
    gt_constraints = active_intent.get("ground_truth_constraints", {})
    min_gsnr = gt_constraints.get("min_gsnr", 15.0)

    # 1. Structured intent summary
    summary_obj = IntentSummary(
        summary=f"Route from {src} to {dst}",
        source_node=src if "Ambiguous" not in intent_class else None,
        target_node=dst if "Ambiguous" not in intent_class else None,
    )

    # 2. PDDL representation
    if "Adversarial" in intent_class or "Ambiguous" in intent_class:
        pddl_str = "(define (problem invalid-syntax))"
        usem_score_str = "0.95"
    elif "Infeasible" in intent_class:
        pddl_str = (
            f"(define (problem route-infeasible)\n"
            f"  (:domain optical-network)\n"
            f"  (:objects {src} {dst} - node)\n"
            f"  (:init (connected {src} {dst}))\n"
            f"  (:goal (and (route {src} {dst}) (min-gsnr {min_gsnr})))\n"
            f")"
        )
        usem_score_str = "0.05"
    else:  # Nominal
        pddl_str = (
            f"(define (problem route-nominal)\n"
            f"  (:domain optical-network)\n"
            f"  (:objects {src} {dst} Hannover - node)\n"
            f"  (:init (connected {src} Hannover) (connected Hannover {dst}))\n"
            f"  (:goal (and (route {src} {dst}) (min-gsnr {min_gsnr})))\n"
            f")"
        )
        usem_score_str = "0.05"

    # 3. LLM-only output
    if "Nominal" in intent_class:
        llm_only_route = [src, "Hannover", dst]
        llm_only_action = "approve"
        est_gsnr = 16.0
    elif "Infeasible" in intent_class:
        # LLM-only hallucinates feasible GSNR on impossible reach (exposing UAR)
        llm_only_route = [src, dst]
        llm_only_action = "approve"
        est_gsnr = 35.0
    else:
        llm_only_route = [src, dst]
        llm_only_action = "approve"
        est_gsnr = 14.0

    mock_llm = MagicMock()

    def _structured_side_effect(schema: Any, *args: Any, **kwargs: Any):
        sub_mock = MagicMock()
        if schema == LLMOnlyOutput:
            sub_mock.invoke.return_value = LLMOnlyOutput(
                source_node=src or "",
                destination_node=dst or "",
                route=llm_only_route,
                estimated_gsnr_dB=est_gsnr,
                action=llm_only_action,
                reasoning="Direct prompt routing estimation",
            )
        else:
            sub_mock.invoke.return_value = summary_obj
        return sub_mock

    mock_llm.with_structured_output.side_effect = _structured_side_effect

    def _dispatcher(messages: Any, *args: Any, **kwargs: Any) -> AIMessage:
        first_msg = messages[0] if messages else None
        prompt_text = getattr(first_msg, "content", "")
        if "PDDL Parser module" in prompt_text:
            return AIMessage(content=pddl_str)
        elif "Reverse Prompting module" in prompt_text:
            return AIMessage(content=f"Route traffic from {src} to {dst}")
        elif "semantic similarity evaluator" in prompt_text:
            return AIMessage(content=usem_score_str)
        return AIMessage(content="OK")

    mock_llm.invoke.side_effect = _dispatcher
    set_llm(mock_llm)


# ---------------------------------------------------------------------------
# Corpus & Setup Helpers
# ---------------------------------------------------------------------------


def load_test_corpus(corpus_path: Path) -> list[dict[str, Any]]:
    """Load and validate the test intent demands corpus."""
    if not corpus_path.exists():
        raise FileNotFoundError(f"Test corpus not found at: {corpus_path}")
    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
    if not isinstance(corpus, list):
        raise ValueError("Corpus JSON must be an array of intent objects.")
    return corpus


def filter_corpus(
    corpus: list[dict[str, Any]],
    classes: list[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Filter intents by risk class and apply sample limits."""
    filtered = corpus
    if classes:
        classes_set = set(classes)
        filtered = [item for item in filtered if item.get("class") in classes_set]
    if limit is not None and limit > 0:
        filtered = filtered[:limit]
    return filtered


# ---------------------------------------------------------------------------
# Results Export Helpers
# ---------------------------------------------------------------------------


def export_raw_results(
    results_by_baseline: dict[str, list[BaselineResult]],
    raw_dir: Path,
    timestamp: str,
) -> tuple[Path, Path]:
    """Save raw evaluation data as JSON and flat tabular CSV."""
    raw_dir.mkdir(parents=True, exist_ok=True)

    # 1. Consolidated JSON
    json_path = raw_dir / f"raw_results_{timestamp}.json"
    latest_json_path = raw_dir / "raw_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_by_baseline, f, indent=2)
    with open(latest_json_path, "w", encoding="utf-8") as f:
        json.dump(results_by_baseline, f, indent=2)

    # 2. Consolidated CSV
    csv_path = raw_dir / f"raw_results_{timestamp}.csv"
    latest_csv_path = raw_dir / "raw_results.csv"

    fieldnames = [
        "timestamp",
        "intent_id",
        "baseline_id",
        "action",
        "qot_feasible",
        "computed_gsnr_dB",
        "pddl_valid",
        "hitl_interrupts",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "execution_time_s",
        "selected_path",
        "error",
    ]

    all_rows = []
    for b_id, results in results_by_baseline.items():
        for r in results:
            path_str = " -> ".join(r.get("selected_path") or [])
            row = {
                "timestamp": timestamp,
                "intent_id": r.get("intent_id"),
                "baseline_id": r.get("baseline_id"),
                "action": r.get("action"),
                "qot_feasible": r.get("qot_feasible"),
                "computed_gsnr_dB": r.get("computed_gsnr_dB"),
                "pddl_valid": r.get("pddl_valid"),
                "hitl_interrupts": r.get("hitl_interrupts"),
                "prompt_tokens": r.get("prompt_tokens"),
                "completion_tokens": r.get("completion_tokens"),
                "total_tokens": r.get("total_tokens"),
                "execution_time_s": r.get("execution_time_s"),
                "selected_path": path_str,
                "error": r.get("error"),
            }
            all_rows.append(row)

    for p in (csv_path, latest_csv_path):
        with open(p, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)

    return latest_json_path, latest_csv_path


# ---------------------------------------------------------------------------
# Main Benchmark Runner
# ---------------------------------------------------------------------------


def run_benchmark(
    corpus_path: Path,
    selected_baselines: list[str],
    classes: list[str] | None = None,
    limit: int | None = None,
    use_mock: bool = False,
    output_dir: Path = Path("tests/evaluation/results"),
    skip_plots: bool = False,
) -> dict[str, Any]:
    """Execute automated benchmark suite across all designated baselines."""
    start_total_time = time.perf_counter()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    console.print()
    banner_text = (
        f"[bold cyan]⚡ MultiAgentON Sprint 4: Automated Evaluation Harness[/bold cyan]\n"
        f"[dim]Optical Backbone:[/dim] Nobel-Germany 17-Node Network (|V|=17, |E|=26)\n"
        f"[dim]Evaluation Mode:[/dim] [bold {'yellow' if use_mock else 'green'}]{'OFFLINE MOCK (Zero API Cost)' if use_mock else 'LIVE LLM API'}[/bold {'yellow' if use_mock else 'green'}]"
    )
    console.print(Panel(banner_text, border_style="cyan", box=box.ROUNDED))

    # 1. Load corpus
    corpus = load_test_corpus(corpus_path)
    filtered_intents = filter_corpus(corpus, classes=classes, limit=limit)
    console.print(
        f"[bold green]✓[/bold green] Loaded [bold white]{len(filtered_intents)}[/bold white] test demands "
        f"across risk categories from [dim]{corpus_path}[/dim]"
    )

    # 2. Verify registered baselines
    registered = list_baselines()
    valid_baselines = [b for b in selected_baselines if b in registered]
    if not valid_baselines:
        raise ValueError(
            f"No valid baselines found in {selected_baselines}. Registered: {registered}"
        )
    console.print(
        f"[bold green]✓[/bold green] Evaluated systems ({len(valid_baselines)}): [cyan]{', '.join(valid_baselines)}[/cyan]"
    )

    # 3. Setup LLM if live mode
    if not use_mock:
        load_dotenv()
        api_key = os.getenv("KIMI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            console.print(
                "[yellow]Warning: No API key found in environment. Defaulting to --mock mode.[/yellow]"
            )
            use_mock = True
        else:
            base_url = os.getenv("KIMI_BASE_URL")
            model = os.getenv("KIMI_MODEL", "kimi-for-coding-highspeed")
            llm = create_kimi_llm(
                api_key=api_key,
                base_url=base_url or None,
                model=model,
                temperature=1.0,
                max_tokens=8000,
            )
            set_llm(llm)
            console.print(
                f"[bold green]✓[/bold green] Live LLM configured: [cyan]{model}[/cyan]"
            )

    # 4. Execute Benchmark Loop
    results_by_baseline: dict[str, list[BaselineResult]] = {
        b_id: [] for b_id in valid_baselines
    }

    total_tasks = len(valid_baselines) * len(filtered_intents)

    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="cyan", complete_style="bold green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        benchmark_task = progress.add_task(
            "[bold cyan]Running Benchmark Suite...[/bold cyan]",
            total=total_tasks,
        )

        for b_id in valid_baselines:
            for intent in filtered_intents:
                intent_id = intent.get("id", "unknown")
                progress.update(
                    benchmark_task,
                    description=f"[dim]System:[/dim] [cyan]{b_id}[/cyan] │ [dim]Intent:[/dim] [white]{intent_id}[/white]",
                )

                if use_mock:
                    setup_mock_llm(intent)

                try:
                    result = run_baseline(b_id, intent)
                except Exception as e:
                    result = {
                        "intent_id": intent_id,
                        "baseline_id": b_id,
                        "action": "clarify",
                        "qot_feasible": False,
                        "hitl_interrupts": 0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "execution_time_s": 0.0,
                        "error": str(e),
                        "metadata": {},
                    }

                results_by_baseline[b_id].append(result)
                progress.advance(benchmark_task)

    total_duration = time.perf_counter() - start_total_time
    console.print(
        f"\n[bold green]✓[/bold green] Benchmark execution complete in [bold white]{total_duration:.2f}s[/bold white]."
    )

    # 5. Export Raw Results
    raw_dir = output_dir / "raw"
    json_path, csv_path = export_raw_results(results_by_baseline, raw_dir, timestamp)
    console.print(
        f"[bold green]✓[/bold green] Raw telemetry exported to:\n"
        f"    • JSON: [dim]{json_path}[/dim]\n"
        f"    • CSV:  [dim]{csv_path}[/dim]"
    )

    # 6. Calculate Metrics for All 4 Pillars
    metrics_summary = compute_all_baselines_metrics(
        results_by_baseline, filtered_intents
    )
    metrics_json_path = output_dir / "metrics.json"
    with open(metrics_json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_summary, f, indent=2)

    # 7. Generate & Save Markdown Summary
    summary_md = generate_summary_markdown(metrics_summary)
    summary_path = output_dir / "summary_table.md"
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_md)
    console.print(
        f"[bold green]✓[/bold green] Consolidated metrics table saved to [dim]{summary_path}[/dim]"
    )

    # 8. Render Visual Figures
    if not skip_plots:
        fig_dir = output_dir / "figures"
        raw_dicts = {
            b_id: [dict(r) for r in res_list]
            for b_id, res_list in results_by_baseline.items()
        }
        figures = generate_all_figures(
            metrics_summary, raw_dicts, filtered_intents, fig_dir
        )
        console.print(
            f"[bold green]✓[/bold green] IEEE / PoliMi thesis figures exported ({len(figures)} sets):"
        )
        for fig_name, paths in figures.items():
            exts = ", ".join(p.suffix for p in paths)
            console.print(f"    • [bold white]{fig_name}[/bold white] ({exts})")

    # 9. Print Rich Table to Terminal
    display_terminal_summary(metrics_summary)

    return {
        "timestamp": timestamp,
        "total_intents": len(filtered_intents),
        "baselines_evaluated": valid_baselines,
        "execution_time_s": total_duration,
        "metrics_summary": metrics_summary,
        "raw_json": str(json_path),
        "raw_csv": str(csv_path),
        "summary_table_md": str(summary_path),
    }


def display_terminal_summary(metrics_summary: dict[str, dict[str, Any]]) -> None:
    """Print consolidated evaluation table to terminal with Rich styling."""
    table = Table(
        title="Sprint 4 Evaluation Benchmark: 4 Core Validation Pillars",
        box=box.ROUNDED,
        header_style="bold cyan",
    )

    table.add_column("Baseline System", style="bold white")
    table.add_column("CRR", justify="right")
    table.add_column("CFG-PR", justify="right")
    table.add_column("UAR (Target: 0%)", justify="right")
    table.add_column("QFR", justify="right")
    table.add_column("Latency", justify="right")
    table.add_column("Tokens", justify="right")
    table.add_column("ΔTokens", justify="right")
    table.add_column("ΔHITL", justify="right")
    table.add_column("GDA", justify="right")

    for b_id, data in metrics_summary.items():
        sem = data.get("semantic", {})
        phys = data.get("physical", {})
        eff = data.get("efficiency", {})
        radg = data.get("radg", {})

        uar_val = phys.get("uar_percent", 0.0)
        uar_style = "bold green" if uar_val == 0.0 else "bold red"

        table.add_row(
            b_id,
            f"{sem.get('crr_percent', 0.0):.1f}%",
            f"{sem.get('cfg_pass_rate_percent', 0.0):.1f}%",
            f"[{uar_style}]{uar_val:.1f}%[/{uar_style}]",
            f"{phys.get('qfr_percent', 0.0):.1f}%",
            f"{eff.get('mean_latency_s', 0.0):.2f}s",
            f"{int(eff.get('mean_prompt_tokens', 0))}",
            f"{eff.get('token_reduction_percent', 0.0):.1f}%",
            f"{eff.get('hitl_reduction_percent', 0.0):.1f}%",
            f"{radg.get('gda_percent', 0.0):.1f}%",
        )

    console.print()
    console.print(table)
    console.print()


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Automated Evaluation Harness for MultiAgentON (Sprint 4)."
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="tests/evaluation/test_corpus.json",
        help="Path to benchmark intent corpus JSON",
    )
    parser.add_argument(
        "--baselines",
        type=str,
        default="proposed_radg,llm_only,always_on,always_off,traditional_sdon",
        help="Comma-separated list of baselines to evaluate",
    )
    parser.add_argument(
        "--classes",
        type=str,
        default=None,
        help="Comma-separated intent classes to evaluate (e.g., I_Nominal,III_Infeasible)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of intents to evaluate (useful for rapid testing)",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run benchmark using deterministic offline mock responses",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="tests/evaluation/results",
        help="Directory to save raw telemetry, summaries, and figures",
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        help="Skip generation of publication figures",
    )

    args = parser.parse_args()

    corpus_path = Path(args.corpus)
    selected_baselines = [b.strip() for b in args.baselines.split(",") if b.strip()]
    selected_classes = (
        [c.strip() for c in args.classes.split(",") if c.strip()]
        if args.classes
        else None
    )
    output_dir = Path(args.output_dir)

    run_benchmark(
        corpus_path=corpus_path,
        selected_baselines=selected_baselines,
        classes=selected_classes,
        limit=args.limit,
        use_mock=args.mock,
        output_dir=output_dir,
        skip_plots=args.skip_plots,
    )


if __name__ == "__main__":
    main()
