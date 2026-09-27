"""Interactive CLI & Benchmark Orchestrator for MultiAgentON Comparative Baselines.

Supports:
  - Proposed RADG (V5 Fail-Fast Decision Gates)
  - Always-On HITL (Paranoid Turn 1 Clarification on Nominals)
  - LLM-Only (No Semantic Gate Filter / Controller Deployment Error Simulation)
  - Comparative Multi-Baseline Benchmarks

Usage:
    uv run python tests/evaluation/main.py                  # Interactive mode with Rich UI
    uv run python tests/evaluation/main.py --baseline proposed_radg --mode interactive
    uv run python tests/evaluation/main.py --baseline always_on_hitl --mode eval
    uv run python tests/evaluation/main.py --baseline all --mode eval --corpus compact
"""

from __future__ import annotations

import argparse
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
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings  # noqa: E402
import questionary  # noqa: E402
from rich import box  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402
from rich.text import Text  # noqa: E402

from src.core.llm import (  # noqa: E402
    DEFAULT_KIMI_MODEL,
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_OPENROUTER_MODEL,
    SUPPORTED_OLLAMA_MODELS,
    create_configured_llm,
    get_supported_openai_models,
    get_supported_openrouter_models,
    resolve_llm_timeout,
    set_llm,
)
from src.core.state import ALLOWED_MSGPACK_MODULES  # noqa: E402
from src.services.testbed_client import MockTestbedClient  # noqa: E402
from tests.evaluation.baselines.always_on_hitl import (  # noqa: E402
    AlwaysOnHITLEvaluator,
    compile_always_on_graph,
)
from tests.evaluation.baselines.common.metrics import compute_pillar_metrics  # noqa: E402
from tests.evaluation.baselines.common.reporter import (  # noqa: E402
    generate_comparative_report,
    sanitize_model_name,
)
from tests.evaluation.baselines.common.runner import STANDARD_FOLLOW_UP_INTENT  # noqa: E402
from tests.evaluation.baselines.llm_only import (  # noqa: E402
    LLMOnlyEvaluator,
    compile_llm_only_graph,
)
from tests.evaluation.baselines.proposed_radg import (  # noqa: E402
    ProposedRADGEvaluator,
    compile_proposed_graph,
)

# Silence verbose loggers to avoid breaking Rich CLI layouts
logging.basicConfig(level=logging.ERROR)
for _log in ("src.nodes.radg_node", "src.nodes.semantic_gate_node", "src.nodes.qot_validation"):
    logging.getLogger(_log).setLevel(logging.ERROR)

console = Console()

COMPACT_CORPUS_PATH = PROJECT_ROOT / "tests" / "evaluation" / "test_corpus_compact.json"
FULL_CORPUS_PATH = PROJECT_ROOT / "tests" / "evaluation" / "test_corpus.json"
BASELINES_DIR = PROJECT_ROOT / "tests" / "evaluation" / "baselines"
RESULTS_DIR = PROJECT_ROOT / "tests" / "evaluation" / "results"

BACK_SENTINEL = "__GO_BACK__"

QUESTIONARY_STYLE = questionary.Style(
    [
        ("qmark", "fg:#00ffff bold"),
        ("question", "bold white"),
        ("answer", "fg:#00ff88 bold"),
        ("pointer", "fg:#00ffff bold"),
        ("highlighted", "fg:#00ffff bold"),
        ("selected", "fg:#00ff88"),
        ("placeholder", "fg:#666666 italic"),
    ]
)


def prompt_select(
    message: str,
    choices: list[Any],
    default: Any = None,
    allow_back: bool = False,
) -> Any:
    """Prompt user with questionary select and exit cleanly on cancel / Ctrl+C, supporting Backspace."""
    q = questionary.select(message, choices=choices, default=default, style=QUESTIONARY_STYLE)
    if allow_back:
        kb = KeyBindings()

        @kb.add("backspace")
        @kb.add("c-h")
        @kb.add("escape")
        def _back(event: Any) -> None:
            event.app.exit(result=BACK_SENTINEL)

        q.application.key_bindings = merge_key_bindings([q.application.key_bindings, kb])

    val = q.ask()
    if val is None:
        console.print("\n[yellow]Execution cancelled by operator.[/yellow]")
        sys.exit(0)
    return val


def prompt_text(
    message: str,
    default: str = "",
    validate: Any = None,
    allow_back: bool = False,
    placeholder: str = "",
) -> str:
    """Prompt user with questionary text and exit cleanly on cancel / Ctrl+C, supporting Backspace on empty."""
    kwargs: dict[str, Any] = {"style": QUESTIONARY_STYLE, "default": default}
    if validate:
        kwargs["validate"] = validate
    if placeholder:
        kwargs["placeholder"] = placeholder

    q = questionary.text(message, **kwargs)
    if allow_back:
        kb = KeyBindings()

        @kb.add("escape")
        def _esc_back(event: Any) -> None:
            event.app.exit(result=BACK_SENTINEL)

        @kb.add("backspace")
        @kb.add("c-h")
        def _back(event: Any) -> None:
            buf = event.app.current_buffer
            if not buf.text:
                event.app.exit(result=BACK_SENTINEL)
            else:
                buf.delete_before_cursor()

        q.application.key_bindings = merge_key_bindings([q.application.key_bindings, kb])

    val = q.ask()
    if val is None:
        console.print("\n[yellow]Execution cancelled by operator.[/yellow]")
        sys.exit(0)
    return val


BASELINE_DESCRIPTIONS: dict[str, str] = {
    "proposed_radg": "Proposed RADG: Author's solution with fail-fast Semantic & Physical RADGs",
    "always_on_hitl": "Always-On HITL: Mandatory Turn-1 human review on Nominal intents (Friction Ablation)",
    "llm_only": "LLM-Only: No Semantic Gate HITL filter (Controller Error Simulation Ablation)",
}

PHASE_META: dict[str, tuple[str, str]] = {
    "intent_ingest": ("Phase 1: Intent Ingestion", "Ingesting NL intent & scoping optical topology"),
    "pddl_parser": ("Phase 2: PDDL Translation", "Translating enriched intent to PDDL & AST validation"),
    "reverse_prompt": ("Phase 3a: Reverse Prompting", "Reconstructing natural language intent from PDDL"),
    "semantic_gate": ("Phase 3: Semantic Gate", "Evaluating Semantic Uncertainty U_sem"),
    "always_on_semantic_gate": ("Phase 3: Always-On Semantic Gate", "Enforcing mandatory operator review"),
    "bypassed_semantic_gate": ("Phase 3: Bypassed Semantic Gate", "Forwarding directly to controller (No HITL)"),
    "hitl_clarify": ("Phase 3b: HITL Clarification", "Awaiting operator clarification for ambiguous intent"),
    "symbolic_solver": ("Phase 4: Symbolic Solver", "Computing candidate lightpaths via Yen's K-SP"),
    "qot_validation": ("Phase 5: QoT Physics Engine", "Evaluating physical-layer feasibility with GN-model"),
    "radg": ("Phase 6: Physical RADG", "Applying Physical RADG"),
    "controller_surrogate_radg": ("Phase 6: Controller Surrogate", "Network controller validating deployment"),
    "plan_synthesizer": ("Phase 7: Plan Synthesis", "Compiling auditable planning report"),
}


def print_banner() -> None:
    """Render application header banner."""
    banner = Text()
    banner.append("⚡ MULTIAGENT-ON: EVALUATION ENVIRONMENT ", style="bold cyan")
    banner.append("│ Comparative Baselines & Benchmark Suite\n", style="bold white")
    banner.append("Optical Backbone: ", style="dim")
    banner.append("Nobel-Germany 17-Node Network ", style="bold green")
    banner.append("│ Physical Model: ", style="dim")
    banner.append("Coherent GN-Model (C-Band 96-ch)\n", style="bold green")
    banner.append("Baselines: ", style="dim")
    banner.append("Proposed RADG ", style="bold cyan")
    banner.append("│ Always-On HITL ", style="bold yellow")
    banner.append("│ LLM-Only", style="bold magenta")

    console.print()
    console.print(
        Panel(
            banner,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )
    console.print()


def render_interactive_execution(
    graph_factory: Any,
    intent_text: str,
    baseline_id: str,
    max_turns: int = 3,
) -> None:
    """Run an interactive session with live Rich phase updates and user HITL input."""
    console.print(
        Panel(
            f"[bold cyan]Baseline:[/bold cyan] {baseline_id.upper()}\n"
            f"[bold white]Operator Intent:[/bold white] \"{intent_text}\"",
            title="🎯 Active Execution Target",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    checkpointer = InMemorySaver(
        serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
    )
    graph = graph_factory(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": f"cli-interactive-{int(time.time())}"}}

    initial_state = {
        "messages": [HumanMessage(content=intent_text)],
        "topology_snapshot": MockTestbedClient().get_topology(),
    }

    stream_input: Any = initial_state
    turn = 1
    t_start = time.perf_counter()

    while turn <= max_turns:
        console.print(f"\n[bold yellow]─── Executing Turn {turn} ───[/bold yellow]")
        try:
            for event in graph.stream(stream_input, config=config, stream_mode="updates"):
                if "__interrupt__" in event:
                    continue
                for node_name, val in event.items():
                    title, desc = PHASE_META.get(node_name, (node_name, ""))
                    console.print(f"  [bold green]✓[/bold green] [bold cyan]{title}[/bold cyan] [dim]({desc})[/dim]")

                    if node_name == "reverse_prompt" and val.get("hitl_reconstruction"):
                        recon = val.get("hitl_reconstruction")
                        console.print(f"    [dim italic]Reconstruction:[/dim italic] {recon[:120]}...")
                    elif node_name in ("semantic_gate", "always_on_semantic_gate") and "usem_score" in val:
                        usem = val.get("usem_score", 0.0)
                        passed = val.get("usem_passed", False)
                        color = "green" if passed else "red"
                        console.print(f"    [dim]U_sem:[/dim] [{color}]{usem:.3f}[/{color}] [dim](Passed: {passed})[/dim]")
                    elif node_name == "qot_validation" and "qot_results" in val:
                        qots = val.get("qot_results", [])
                        feas = sum(1 for q in qots if q.get("feasible"))
                        console.print(f"    [dim]QoT Feasibility:[/dim] {feas}/{len(qots)} candidate paths valid")
                    elif node_name in ("radg", "controller_surrogate_radg") and "radg_decision" in val:
                        dec = val.get("radg_decision")
                        color = "green" if dec == "approve" else "yellow"
                        console.print(f"    [dim]Gate Verdict:[/dim] [{color}]{dec.upper()}[/{color}]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Interactive execution interrupted by operator.[/yellow]")
            return
        except Exception as exc:
            console.print(f"\n[bold red][!] Error during execution stream:[/bold red] {exc}")
            break

        state = graph.get_state(config)
        if state.next:
            gate_name = state.next[0]
            action = "clarify" if gate_name == "hitl_clarify" else "replan"

            interrupt_info: dict[str, Any] = {}
            if state.tasks and state.tasks[0].interrupts:
                interrupt_info = state.tasks[0].interrupts[0].value

            console.print()
            console.print(
                Panel(
                    f"[bold yellow]Trigger Gate:[/bold yellow] {gate_name} (Action: {action.upper()})\n"
                    f"[bold white]Reason:[/bold white] {interrupt_info.get('reason') or interrupt_info.get('error_context') or 'Risk threshold exceeded'}\n"
                    f"[bold dim]Suggestion:[/bold dim] {interrupt_info.get('suggestion') or 'Please provide refined instructions.'}",
                    title="⚠️  Human-in-the-Loop Operator Interrupt",
                    border_style="yellow",
                    box=box.ROUNDED,
                )
            )

            # Interactive choices for operator
            choices = []
            if action == "clarify" and interrupt_info.get("pddl_valid"):
                choices.append(
                    questionary.Choice(
                        title="✅ Proceed with current understanding (Approve and continue to solver)",
                        value="approve",
                    )
                )
            choices.append(
                questionary.Choice(
                    title="✏️  Provide Refined Intent (Recommended)",
                    value="refine",
                )
            )
            choices.append(
                questionary.Choice(
                    title="⚡ Use Standard Benchmark Recovery Intent",
                    value="standard",
                )
            )
            choices.append(
                questionary.Choice(
                    title="❌ Abort Execution",
                    value="abort",
                )
            )

            action_choice = questionary.select(
                "How would you like to respond to this gate interrupt?",
                choices=choices,
                style=QUESTIONARY_STYLE,
            ).ask()

            if action_choice is None or action_choice == "abort":
                console.print("\n[red]Execution aborted by operator.[/red]")
                return

            if action_choice == "approve":
                resume_payload = {"action": "approve"}
                console.print("[dim]Operator approved current understanding — proceeding to solver.[/dim]")
            elif action_choice == "standard":
                feedback = STANDARD_FOLLOW_UP_INTENT
                console.print(f"[dim]Injecting standard recovery intent:[/dim] \"{feedback}\"")
                resume_payload = {
                    "action": "refine" if action == "clarify" else "replan",
                    "feedback": feedback,
                }
            else:
                feedback = questionary.text(
                    "Enter refined intent or constraint feedback:",
                    default=STANDARD_FOLLOW_UP_INTENT,
                    style=QUESTIONARY_STYLE,
                ).ask()
                if feedback is None:
                    console.print("\n[red]Execution aborted by operator.[/red]")
                    return
                resume_payload = {
                    "action": "refine" if action == "clarify" else "replan",
                    "feedback": feedback,
                }

            stream_input = Command(resume=resume_payload)
            turn += 1
        else:
            elapsed = time.perf_counter() - t_start
            final_report = None
            if state.values and state.values.get("planning_report"):
                final_report = state.values.get("planning_report")

            console.print()
            console.print(
                Panel(
                    f"[bold green]✓ Pipeline completed in {elapsed:.2f}s ({turn} turn(s))![/bold green]\n"
                    + (f"[dim]Planning Report available ({len(str(final_report))} chars)[/dim]" if final_report else ""),
                    title="🏁 Execution Succeeded",
                    border_style="green",
                    box=box.ROUNDED,
                )
            )
            if final_report:
                console.print("\n[bold cyan]Planning Report Summary:[/bold cyan]")
                console.print(Markdown(str(final_report)))
            break

    if turn > max_turns:
        elapsed = time.perf_counter() - t_start
        console.print()
        console.print(
            Panel(
                f"[bold red]Execution stopped: Maximum turns ({max_turns}) exceeded without resolution.[/bold red]\n"
                f"[dim]Total time: {elapsed:.2f}s[/dim]",
                title="❌ Turn Limit Exceeded",
                border_style="red",
                box=box.ROUNDED,
            )
        )


def run_evaluation_mode(
    baseline_id: str,
    corpus: list[dict[str, Any]],
    output_dir: Path,
    metadata: dict[str, Any],
    max_turns: int = 3,
    intent_timeout: float = 300.0,
    warmup: bool = True,
) -> list[dict[str, Any]]:
    """Execute evaluation benchmark and render Four Pillars summary table."""
    evaluator: Any
    if baseline_id == "proposed_radg":
        evaluator = ProposedRADGEvaluator()
    elif baseline_id == "always_on_hitl":
        evaluator = AlwaysOnHITLEvaluator()
    elif baseline_id == "llm_only":
        evaluator = LLMOnlyEvaluator()
    else:
        raise ValueError(f"Unknown baseline: {baseline_id}")

    console.print(
        Panel(
            f"[bold cyan]Baseline:[/bold cyan] {baseline_id.upper()}\n"
            f"[bold white]Demands to evaluate:[/bold white] {len(corpus)}\n"
            f"[bold white]Output Directory:[/bold white] {output_dir}\n"
            f"[bold white]Intent Timeout:[/bold white] {intent_timeout}s (5 min)\n"
            f"[bold white]Warmup Pass:[/bold white] {'Enabled (Un-metered prime)' if warmup else 'Disabled'}",
            title="📊 Benchmark Execution Starting",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    t0 = time.perf_counter()
    results = evaluator.evaluate_corpus(
        corpus=corpus,
        output_dir=output_dir,
        metadata=metadata,
        max_turns=max_turns,
        intent_timeout=intent_timeout,
        verbose=True,
        generate_visuals=True,
        warmup=warmup,
    )
    elapsed = time.perf_counter() - t0

    # Display Pillar summary table
    pillar_metrics = compute_pillar_metrics(results)
    p1 = pillar_metrics.get("pillar_1", {})
    p2 = pillar_metrics.get("pillar_2", {})
    p3 = pillar_metrics.get("pillar_3", {})
    p4 = pillar_metrics.get("pillar_4", {})

    table = Table(
        title=f"Four Core Validation Pillars: {baseline_id.upper()}",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Pillar", style="bold white", width=30)
    table.add_column("Key Metric", style="dim", width=25)
    table.add_column("Measured Actual", justify="right", style="bold green", width=20)
    table.add_column("Target", justify="right", style="dim", width=15)

    table.add_row(
        "Pillar 1: Semantic Translation",
        "Constraint Retention (CRR)",
        f"{p1.get('operable_crr_rate', 0.0):.1f}%",
        "100.0%",
    )
    table.add_row(
        "",
        "CFG Pass Rate",
        f"{p1.get('cfg_pass_rate', 0.0):.1f}%",
        "≥ 95.0%",
    )
    table.add_row(
        "",
        "Semantic Agreement",
        f"{p1.get('mean_well_formed_agreement', 0.0):.3f}",
        "> 0.850",
    )
    table.add_row(
        "Pillar 2: Physical Feasibility & Integrity",
        "False Positive Rate (FPR)",
        f"{p4.get('fpr_rate', 0.0):.1f}%",
        "0.0%",
    )
    table.add_row(
        "",
        "Infeasibility Catch (PIIR)",
        f"{p2.get('piir_rate', 0.0):.1f}%",
        "100.0%",
    )
    table.add_row(
        "Pillar 3: Efficiency & Friction",
        "Median End-to-End Latency",
        f"{p3.get('median_e2e_latency_seconds', p3.get('mean_e2e_latency_seconds', 0.0)):.2f}s",
        "Contextual",
    )
    table.add_row(
        "",
        "Median Tokens / Demand",
        f"{p3.get('median_tokens_per_intent', p3.get('mean_tokens_per_intent', 0.0)):,.0f} tok",
        "Monitored",
    )
    table.add_row(
        "",
        "Total Token Consumption",
        f"{p3.get('total_tokens_consumed', 0):,} tok",
        "Monitored",
    )
    table.add_row(
        "",
        "Mean HITL Turns",
        f"{p3.get('mean_hitl_turns', 0.0):.2f}",
        "Selective",
    )
    table.add_row(
        "Pillar 4: Gate Reliability",
        "Gate Accuracy (GDA)",
        f"{p4.get('gda_rate', 0.0):.1f}%",
        "> 95.0%",
    )
    table.add_row(
        "",
        "False Positive Rate (FPR)",
        f"{p4.get('fpr_rate', 0.0):.1f}%",
        "0.0%",
    )

    console.print()
    console.print(table)
    console.print(f"\n[bold green]✓ Benchmark completed in {elapsed:.2f}s! Telemetry exported to {output_dir}[/bold green]\n")
    return results


def list_available_runs(baseline_id: str) -> list[str]:
    """Find all timestamped run directories for a specific baseline."""
    b_dir = BASELINES_DIR / baseline_id / "results"
    if not b_dir.exists():
        return []

    run_dirs: list[Path] = []
    for jf in b_dir.glob("**/evaluation_results*.json"):
        d = jf.parent
        if d not in run_dirs:
            run_dirs.append(d)

    # Sort newest first by timestamp (stripping run_ prefix)
    run_dirs.sort(key=lambda p: p.name.replace("run_", ""), reverse=True)
    return [str(p.relative_to(b_dir)) for p in run_dirs]


def resolve_baseline_run(
    baseline_id: str,
    explicit_run: str | None = None,
    interactive: bool = False,
) -> tuple[str, Path] | None:
    """Resolve which run folder to use for a baseline, defaulting to latest."""
    b_dir = BASELINES_DIR / baseline_id / "results"
    available = list_available_runs(baseline_id)
    if not available:
        console.print(f"[yellow]⚠️ No historical evaluation runs found for baseline '{baseline_id}'.[/yellow]")
        return None

    if explicit_run:
        clean_exp = explicit_run.replace("run_", "")
        target_path = b_dir / explicit_run
        if target_path.exists() and any(target_path.glob("evaluation_results*.json")):
            return explicit_run, target_path
        target_path2 = b_dir / clean_exp
        if target_path2.exists() and any(target_path2.glob("evaluation_results*.json")):
            return clean_exp, target_path2
        for cand in available:
            if explicit_run in cand or clean_exp in cand:
                return cand, b_dir / cand
        console.print(f"[red]Specified run '{explicit_run}' not found for baseline '{baseline_id}'.[/red]")
        return None

    if interactive and len(available) > 1:
        choices = [
            questionary.Choice(f"{r} (Latest)" if idx == 0 else r, r)
            for idx, r in enumerate(available)
        ]
        chosen = prompt_select(
            f"Select evaluation run version for {baseline_id.upper()}:",
            choices=choices,
            default=available[0],
        )
        return chosen, b_dir / chosen

    # Default to newest
    latest = available[0]
    return latest, b_dir / latest


def run_comparative_mode(
    proposed_run: str | None = None,
    hitl_run: str | None = None,
    llm_run: str | None = None,
    is_interactive: bool = False,
) -> None:
    """Execute comparative analysis across existing runs of baselines."""
    console.print(
        Panel(
            "[bold cyan]Mode: Cross-Baseline Comparative Evaluation[/bold cyan]\n"
            "[dim]Resolving runs across Proposed RADG, Always-On HITL, and LLM-Only...[/dim]",
            title="📊 Multi-Baseline Comparison Orchestrator",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    baseline_runs_map = {
        "proposed_radg": proposed_run,
        "always_on_hitl": hitl_run,
        "llm_only": llm_run,
    }

    resolved_runs: dict[str, Path] = {}
    all_results: dict[str, list[dict[str, Any]]] = {}

    for b_id, explicit in baseline_runs_map.items():
        res = resolve_baseline_run(b_id, explicit_run=explicit, interactive=is_interactive)
        if res is not None:
            r_id, r_path = res
            resolved_runs[b_id] = r_path
            json_file = next(r_path.glob("evaluation_results*.json"), r_path / "evaluation_results.json")
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
            all_results[b_id] = data.get("demands", [])
            console.print(f"  [green]✓[/green] [bold white]{b_id.upper()}:[/bold white] Using [cyan]{r_id}[/cyan] ({len(all_results[b_id])} demands)")

    if len(all_results) < 2:
        console.print("[red]Need at least 2 baselines with completed runs to generate comparative metrics.[/red]")
        return

    # Regenerate markdown reports and visual assets in each resolved baseline run folder
    from tests.evaluation.baselines.common.reporter import regenerate_baseline_summary
    from tests.evaluation.generate_visuals import generate_run_visuals

    for b_id, r_path in resolved_runs.items():
        json_file = next(r_path.glob("evaluation_results*.json"), r_path / "evaluation_results.json")
        try:
            console.print(f"  [dim]Regenerating summary report and visual assets for {b_id} in {r_path.name}...[/dim]")
            regenerate_baseline_summary(json_file, output_dir=r_path)
            generate_run_visuals(json_file, target_dir=r_path)
            console.print(f"  [green]✓[/green] [bold white]{b_id.upper()}:[/bold white] Updated summary & visuals in [cyan]{r_path.name}[/cyan]")
        except Exception as e:
            console.print(f"  [yellow]Warning: Could not regenerate artifacts for {b_id}: {e}[/yellow]")

    run_id = time.strftime("%Y%m%d_%H%M%S")

    # Resolve model and provider metadata from resolved baseline data
    model_name = "unknown_model"
    provider_name = "ollama"
    for r_path in resolved_runs.values():
        jf = next(r_path.glob("evaluation_results*.json"), None)
        if jf and jf.exists():
            try:
                with open(jf, encoding="utf-8") as fp:
                    m = json.load(fp).get("metadata", {})
                    model_name = m.get("model", model_name)
                    provider_name = m.get("provider", provider_name)
                    break
            except Exception:
                pass

    clean_model = sanitize_model_name(model_name)
    common_output_dir = RESULTS_DIR / clean_model / run_id

    metadata = {
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": run_id,
        "model": model_name,
        "provider": provider_name,
        "mode": "comparative_analysis",
        "included_runs": {b: p.name for b, p in resolved_runs.items()},
    }

    generate_comparative_report(
        all_results=all_results,
        output_dir=common_output_dir,
        metadata=metadata,
    )

    console.print()
    console.print(
        Panel(
            f"[bold green]✓ Comparative Multi-Baseline Evaluation Complete![/bold green]\n\n"
            f"[bold white]Output Directory:[/bold white] [cyan]{common_output_dir}[/cyan]\n"
            f"  ├── comparative_results_{run_id}.json\n"
            f"  ├── comparative_summary_{run_id}.md\n"
            f"  ├── comparative_pillars_breakdown.png / .pdf\n"
            f"  ├── comparative_deployment_flow_sankey.png / .pdf\n"
            f"  ├── comparative_scalability_projection.png / .pdf\n"
            f"  └── gate_accuracy_matrix.png / .pdf",
            title="🏆 Comparison Synthesized Successfully",
            border_style="green",
            box=box.ROUNDED,
        )
    )



def find_complete_model_runs() -> dict[str, list[str]]:
    """Return {sanitized_model: [timestamp, ...]} where every timestamp has
    evaluation_results for ALL three baselines (proposed_radg, always_on_hitl, llm_only)."""
    REQUIRED = ["proposed_radg", "always_on_hitl", "llm_only"]
    # map: model -> {timestamp -> set(baselines present)}
    model_ts_baselines: dict[str, dict[str, set[str]]] = {}

    for b_id in REQUIRED:
        b_root = BASELINES_DIR / b_id / "results"
        if not b_root.exists():
            continue
        for json_path in b_root.glob("**/evaluation_results*.json"):
            # Structure: results/<model>/<timestamp>/evaluation_results_<ts>.json
            parts = json_path.parts
            # Find the index of 'results' segment
            try:
                res_idx = parts.index("results", parts.index(b_id))
            except ValueError:
                continue
            if len(parts) < res_idx + 3:
                continue
            model_seg = parts[res_idx + 1]
            ts_seg = parts[res_idx + 2]
            model_ts_baselines.setdefault(model_seg, {}).setdefault(ts_seg, set()).add(b_id)

    complete: dict[str, list[str]] = {}
    for model, ts_map in model_ts_baselines.items():
        valid_ts = sorted(
            [ts for ts, baselines in ts_map.items() if len(baselines) == len(REQUIRED)],
            reverse=True,
        )
        if valid_ts:
            complete[model] = valid_ts

    return complete


def run_cross_model_comparison(selected: list[dict[str, str]]) -> None:
    """Load comparative JSONs for each selected model/timestamp and generate cross-model figures.

    Args:
        selected: List of {"model": sanitized_model, "timestamp": ts} dicts.
    """
    from tests.evaluation.generate_visuals import (
        plot_cross_model_efficiency,
        plot_cross_model_gate_accuracy_heatmap,
    )

    BASELINES = ["proposed_radg", "always_on_hitl", "llm_only"]
    CROSS_MODEL_DIR = RESULTS_DIR / "cross_model"

    console.print(
        Panel(
            "[bold cyan]Mode: Cross-Model LLM Comparison[/bold cyan]\n"
            "[dim]Loading comparative results and generating cross-model figures...[/dim]",
            title="🔬 Cross-Model Analysis",
            border_style="cyan",
            box=box.ROUNDED,
        )
    )

    models_data: list[dict[str, Any]] = []
    meta_entries: list[dict[str, str]] = []

    for entry in selected:
        model_seg = entry["model"]
        ts = entry["timestamp"]

        # Load the comparative_results JSON if it exists in results/<model>/<ts>/
        comp_dir = RESULTS_DIR / model_seg / ts
        comp_json = next(comp_dir.glob("comparative_results*.json"), None) if comp_dir.exists() else None

        if comp_json and comp_json.exists():
            with open(comp_json, encoding="utf-8") as f:
                comp_data = json.load(f)
            console.print(f"  [green]✓[/green] [bold white]{model_seg}[/bold white] @ [cyan]{ts}[/cyan] — loaded comparative JSON")
        else:
            # Build comparative_data on-the-fly from individual baseline JSONs
            comp_data: dict[str, Any] = {"metadata": {"model": model_seg, "run_id": ts}, "baselines": {}}
            for b_id in BASELINES:
                b_json = next(
                    (BASELINES_DIR / b_id / "results" / model_seg / ts).glob("evaluation_results*.json"),
                    None,
                )
                if b_json and b_json.exists():
                    with open(b_json, encoding="utf-8") as f:
                        b_raw = json.load(f)
                    comp_data["baselines"][b_id] = b_raw
            console.print(f"  [green]✓[/green] [bold white]{model_seg}[/bold white] @ [cyan]{ts}[/cyan] — assembled from baseline JSONs")

        # Resolve human-readable model label from metadata
        raw_model = comp_data.get("metadata", {}).get("model", model_seg)
        for b_id in BASELINES:
            b_dir = BASELINES_DIR / b_id / "results" / model_seg / ts
            bj = next(b_dir.glob("evaluation_results*.json"), None)
            if bj:
                try:
                    with open(bj, encoding="utf-8") as f:
                        raw_model = json.load(f).get("metadata", {}).get("model", raw_model)
                    break
                except Exception:
                    pass

        models_data.append({"label": raw_model, "comparative_data": comp_data})
        meta_entries.append({"model_label": raw_model, "model_dir": model_seg, "timestamp": ts})

    if len(models_data) < 2:
        console.print("[red]Need at least 2 models with complete data to generate cross-model figures.[/red]")
        return

    run_id = time.strftime("%Y%m%d_%H%M%S")
    out_dir = CROSS_MODEL_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[dim]Generating cross-model figures in {out_dir}...[/dim]")

    plot_cross_model_efficiency(models_data, out_dir / "cross_model_efficiency")
    console.print("  [green]✓[/green] cross_model_efficiency.png / .pdf")

    plot_cross_model_gate_accuracy_heatmap(models_data, out_dir / "cross_model_gate_accuracy")
    console.print("  [green]✓[/green] cross_model_gate_accuracy.png / .pdf")

    # Write metadata markdown
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    md_lines = [
        "---",
        f"title: \"Cross-Model LLM Comparison — {run_id}\"",
        f"date: {now_str}",
        "tags: [cross-model, evaluation, radg, comparative]",
        "status: active",
        "---",
        "",
        f"# Cross-Model Comparison Report — `{run_id}`",
        "",
        f"**Generated:** {now_str}  ",
        f"**Models compared:** {len(models_data)}  ",
        "",
        "## Models & Runs",
        "",
        "| # | Model Label | Directory | Timestamp |",
        "|---|-------------|-----------|-----------|" ,
    ]
    for i, me in enumerate(meta_entries, 1):
        md_lines.append(f"| {i} | `{me['model_label']}` | `{me['model_dir']}` | `{me['timestamp']}` |")

    md_lines += [
        "",
        "## Generated Figures",
        "",
        "| File | Description |",
        "|------|-------------|" ,
        "| `cross_model_efficiency.png/.pdf` | 2-panel grouped bar: Median Latency & Token Footprint per model per baseline. Captures LLM-dependent efficiency variability while holding baseline architecture constant. |",
        "| `cross_model_gate_accuracy.png/.pdf` | GDA% heatmap (model × risk class) + overall GDA & FPR summary bar for Proposed RADG. Validates model-agnostic integrity guarantees. |",
        "",
        "## Methodology Notes",
        "",
        "- **Structural figures** (Sankey, Scalability Projection, Integrity Pillars) are NOT regenerated here because they are architectural properties of the RADG pipeline, not LLM-dependent. They are documented once per-model in `results/<model>/<timestamp>/`.",
        "- **FPR** is expected to remain at `0.0%` across all models — this is the RADG system invariant. Any deviation should be investigated.",
        "- **Latency and Token Footprint** are the primary variables that differ across LLM backends (local SLMs vs. cloud APIs).",
        "- **GDA%** may show minor per-class variance driven by each model's conservatism on ambiguous intents.",
    ]

    md_path = out_dir / f"cross_model_comparison_{run_id}.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    console.print(f"  [green]✓[/green] {md_path.name}")

    console.print()
    console.print(
        Panel(
            f"[bold green]✓ Cross-Model Comparison Complete![/bold green]\n\n"
            f"[bold white]Output Directory:[/bold white] [cyan]{out_dir}[/cyan]\n"
            f"  ├── cross_model_efficiency.png / .pdf\n"
            f"  ├── cross_model_gate_accuracy.png / .pdf\n"
            f"  └── cross_model_comparison_{run_id}.md",
            title="🏆 Cross-Model Analysis Complete",
            border_style="green",
            box=box.ROUNDED,
        )
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI flags."""
    parser = argparse.ArgumentParser(
        description="MultiAgentON - Comparative Baselines & Benchmark Orchestrator"
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=None,
        choices=["proposed_radg", "always_on_hitl", "llm_only", "all"],
        help="Baseline to run",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        choices=["interactive", "eval", "compare"],
        help="Execution mode (interactive single intent, evaluation benchmark, or cross-baseline comparison)",
    )
    parser.add_argument(
        "--proposed-run",
        type=str,
        default=None,
        help="Run ID or timestamp for proposed_radg baseline in comparison mode (default: latest)",
    )
    parser.add_argument(
        "--hitl-run",
        type=str,
        default=None,
        help="Run ID or timestamp for always_on_hitl baseline in comparison mode (default: latest)",
    )
    parser.add_argument(
        "--llm-run",
        type=str,
        default=None,
        help="Run ID or timestamp for llm_only baseline in comparison mode (default: latest)",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="compact",
        choices=["compact", "full"],
        help="Evaluation corpus ('compact': 20 demands, 'full': 120 demands, default: 'compact')",
    )
    parser.add_argument(
        "--class",
        "--risk-class",
        dest="risk_class",
        type=str,
        default="all",
        choices=["all", "I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"],
        help="Risk class to filter (default: 'all')",
    )
    parser.add_argument(
        "--id",
        dest="demand_id",
        type=str,
        default=None,
        help="Filter specific demand ID (e.g. 'intent_nom_01')",
    )
    parser.add_argument(
        "--provider",
        type=str,
        default=os.getenv("LLM_PROVIDER", "ollama"),
        choices=["ollama", "openrouter", "openai", "kimi"],
        help="LLM provider",
    )
    parser.add_argument(
        "--reasoning-effort",
        type=str,
        default=os.getenv("OPENAI_REASONING_EFFORT", None),
        choices=["none", "low", "medium", "high"],
        help="Reasoning effort for OpenAI reasoning models ('none', 'low', 'medium', 'high')",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name (defaults to provider-specific default if omitted)",
    )
    parser.add_argument(
        "--intent",
        type=str,
        default=None,
        help="Natural language intent for direct execution",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_LLM_TIMEOUT,
        help=f"Per-request timeout (default: {DEFAULT_LLM_TIMEOUT}s)",
    )
    parser.add_argument(
        "--intent-timeout",
        type=float,
        default=300.0,
        help="Global wall-clock timeout per intent in seconds (default: 300.0s / 5 min)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)",
    )
    parser.add_argument(
        "--no-warmup",
        action="store_true",
        help="Skip un-metered LLM warmup pass before evaluation benchmark",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the evaluation CLI."""
    load_dotenv()
    args = parse_args()
    print_banner()

    # Check if comparative mode was requested via CLI flags
    if args.mode == "compare":
        run_comparative_mode(
            proposed_run=args.proposed_run,
            hitl_run=args.hitl_run,
            llm_run=args.llm_run,
            is_interactive=False,
        )
        return

    # Interactive configuration if neither baseline nor mode is specified
    is_fully_interactive = (args.baseline is None and args.mode is None and args.intent is None)
    provider = args.provider
    model = args.model
    timeout = resolve_llm_timeout(args.timeout)
    temperature = args.temperature
    baseline = args.baseline
    mode = args.mode
    intent_text = args.intent
    corpus_choice = args.corpus

    if is_fully_interactive:
        step_stack: list[str] = ["mode"]
        wizard: dict[str, Any] = {}

        while step_stack:
            step = step_stack[-1]

            if step == "mode":
                chosen_mode = prompt_select(
                    "Select Execution Mode:",
                    choices=[
                        questionary.Choice("Interactive Mode (Single intent, live node tracking, no metrics export)", "interactive"),
                        questionary.Choice("Evaluation Benchmark Mode (Automated test corpus, Four Pillars metrics, export results)", "eval"),
                        questionary.Choice("Comparative Analysis Mode (Compare existing baseline runs with custom/latest run selection)", "compare"),
                        questionary.Choice("Comparative LLMs Mode (Cross-model efficiency & gate accuracy figures)", "comparative_llms"),
                    ],
                    allow_back=False,
                )
                if chosen_mode == "compare":
                    run_comparative_mode(
                        proposed_run=args.proposed_run,
                        hitl_run=args.hitl_run,
                        llm_run=args.llm_run,
                        is_interactive=True,
                    )
                    return
                if chosen_mode == "comparative_llms":
                    step_stack.append("comparative_llms")
                    continue
                wizard["mode"] = chosen_mode
                step_stack.append("provider")

            elif step == "comparative_llms":
                complete_runs = find_complete_model_runs()
                if not complete_runs:
                    console.print(
                        "[yellow]⚠️  No models found with complete results in all 3 baselines.\n"
                        "Run evaluations for at least 2 models first.[/yellow]"
                    )
                    step_stack.pop()
                    continue

                # Build flat choice list: model/timestamp pairs
                all_pairs = [
                    (model_seg, ts)
                    for model_seg, ts_list in sorted(complete_runs.items())
                    for ts in ts_list
                ]

                if len(all_pairs) < 2:
                    console.print(
                        "[yellow]⚠️  Need at least 2 complete model/timestamp combinations.\n"
                        f"Found only {len(all_pairs)}. Run more model evaluations first.[/yellow]"
                    )
                    step_stack.pop()
                    continue

                selected_models: list[dict[str, str]] = wizard.get("cross_model_selected", [])

                while True:
                    n_selected = len(selected_models)
                    can_continue = n_selected >= 2
                    can_add = n_selected < 4

                    # Build choice list for this iteration
                    pair_choices = []
                    for model_seg, ts in all_pairs:
                        already = any(s["model"] == model_seg and s["timestamp"] == ts for s in selected_models)
                        indicator = " ✓" if already else ""
                        pair_choices.append(
                            questionary.Choice(
                                f"{model_seg}  [{ts}]{indicator}",
                                value=f"{model_seg}||{ts}",
                            )
                        )

                    if can_continue:
                        pair_choices.append(questionary.Choice("─── Continue with selected models ───", "__CONTINUE__"))
                    pair_choices.append(questionary.Choice("─── Clear selection ───", "__CLEAR__"))

                    status_msg = f"Selected: {n_selected}/4 model(s) ({'select 1 more to continue' if n_selected < 2 else 'ready — or add more (max 4)'})\n"
                    action = prompt_select(
                        f"{status_msg}Select a model/timestamp to toggle (Backspace to go back):",
                        choices=pair_choices,
                        allow_back=True,
                    )

                    if action == BACK_SENTINEL:
                        selected_models = []
                        wizard.pop("cross_model_selected", None)
                        step_stack.pop()
                        break

                    if action == "__CLEAR__":
                        selected_models = []
                        wizard["cross_model_selected"] = []
                        continue

                    if action == "__CONTINUE__":
                        wizard["cross_model_selected"] = selected_models
                        run_cross_model_comparison(selected_models)
                        return

                    # Toggle selection
                    model_seg, ts = action.split("||", 1)
                    existing = next(
                        (i for i, s in enumerate(selected_models) if s["model"] == model_seg and s["timestamp"] == ts),
                        None,
                    )
                    if existing is not None:
                        selected_models.pop(existing)
                    elif can_add:
                        selected_models.append({"model": model_seg, "timestamp": ts})
                    else:
                        console.print("[yellow]Maximum 4 models already selected. Deselect one first.[/yellow]")

                    wizard["cross_model_selected"] = selected_models

            elif step == "provider":
                env_p = args.provider or os.getenv("LLM_PROVIDER")
                chosen_p = prompt_select(
                    "Select LLM Provider (Backspace/Esc to go back):",
                    choices=[
                        questionary.Choice("Ollama (Local Open-Weights)", "ollama"),
                        questionary.Choice("OpenRouter (Cloud API)", "openrouter"),
                        questionary.Choice("OpenAI (Cloud API)", "openai"),
                        questionary.Choice("Kimi / Moonshot (Cloud API)", "kimi"),
                    ],
                    default=wizard.get("provider", env_p if env_p in ("ollama", "openrouter", "openai", "kimi") else "ollama"),
                    allow_back=True,
                )
                if chosen_p == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["provider"] = chosen_p
                if chosen_p == "openrouter":
                    step_stack.append("openrouter_model")
                elif chosen_p == "openai":
                    step_stack.append("openai_model")
                elif chosen_p == "ollama":
                    step_stack.append("ollama_model")
                else:
                    step_stack.append("kimi_model")

            elif step == "openrouter_model":
                configured_models = get_supported_openrouter_models()
                default_m = os.getenv("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL
                choices = [
                    questionary.Choice(f"{m} (Default)" if m == default_m else m, m)
                    for m in configured_models
                ]
                choices.append(questionary.Choice("Enter custom model slug...", "custom"))
                selected_m = prompt_select(
                    "Select OpenRouter Model:",
                    choices=choices,
                    default=default_m if default_m in configured_models else (choices[0].value if choices else None),
                    allow_back=True,
                )
                if selected_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                if selected_m == "custom":
                    step_stack.append("openrouter_custom_model")
                else:
                    wizard["model"] = selected_m
                    step_stack.append("baseline")

            elif step == "openrouter_custom_model":
                default_m = os.getenv("OPENROUTER_MODEL") or DEFAULT_OPENROUTER_MODEL
                custom_m = prompt_text(
                    "Enter OpenRouter Model Slug (e.g. 'openai/gpt-4o-mini', 'anthropic/claude-3.5-sonnet'):",
                    default=default_m,
                    allow_back=True,
                )
                if custom_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["model"] = custom_m
                step_stack.append("baseline")

            elif step == "openai_model":
                configured_models = get_supported_openai_models()
                default_m = os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
                choices = [
                    questionary.Choice(f"{m} (Default)" if m == default_m else m, m)
                    for m in configured_models
                ]
                choices.append(questionary.Choice("Enter custom model name...", "custom"))
                selected_m = prompt_select(
                    "Select OpenAI Model:",
                    choices=choices,
                    default=default_m if default_m in configured_models else (choices[0].value if choices else None),
                    allow_back=True,
                )
                if selected_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                if selected_m == "custom":
                    step_stack.append("openai_custom_model")
                else:
                    wizard["model"] = selected_m
                    step_stack.append("baseline")

            elif step == "openai_custom_model":
                default_m = os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL
                custom_m = prompt_text(
                    "Enter OpenAI Model Name (e.g. 'gpt-6-luna', 'gpt-oss-120b'):",
                    default=default_m,
                    allow_back=True,
                )
                if custom_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["model"] = custom_m
                step_stack.append("baseline")

            elif step == "ollama_model":
                choices = [questionary.Choice(m, m) for m in SUPPORTED_OLLAMA_MODELS]
                choices.append(questionary.Choice("Enter custom model name...", "custom"))
                default_m = os.getenv("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL
                selected_m = prompt_select(
                    "Select Ollama Model:",
                    choices=choices,
                    default=default_m if default_m in SUPPORTED_OLLAMA_MODELS else (choices[0].value if choices else None),
                    allow_back=True,
                )
                if selected_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                if selected_m == "custom":
                    step_stack.append("ollama_custom_model")
                else:
                    wizard["model"] = selected_m
                    step_stack.append("baseline")

            elif step == "ollama_custom_model":
                default_m = os.getenv("OLLAMA_MODEL") or DEFAULT_OLLAMA_MODEL
                custom_m = prompt_text(
                    "Enter Ollama Model Name:",
                    default=default_m,
                    allow_back=True,
                )
                if custom_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["model"] = custom_m
                step_stack.append("baseline")

            elif step == "kimi_model":
                custom_m = prompt_text(
                    "Enter Model Name for Kimi:",
                    default=os.getenv("KIMI_MODEL", DEFAULT_KIMI_MODEL),
                    allow_back=True,
                )
                if custom_m == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["model"] = custom_m
                step_stack.append("baseline")

            elif step == "baseline":
                chosen_b = prompt_select(
                    "Select Baseline Architecture to Run:",
                    choices=[
                        questionary.Choice("Proposed RADG (Dual Fail-Fast Risk Gates)", "proposed_radg"),
                        questionary.Choice("Always-On HITL (Paranoid Mandatory Clarification on Nominals)", "always_on_hitl"),
                        questionary.Choice("LLM-Only (No Semantic Gate / Controller Error Simulation)", "llm_only"),
                        questionary.Choice("Run All Baselines (Comparative Suite)", "all"),
                    ],
                    allow_back=True,
                    default=wizard.get("baseline"),
                )
                if chosen_b == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["baseline"] = chosen_b
                if wizard["mode"] == "interactive":
                    step_stack.append("intent_source")
                else:
                    step_stack.append("eval_corpus")

            elif step == "intent_source":
                chosen_src = prompt_select(
                    "How would you like to provide the intent?",
                    choices=[
                        questionary.Choice("Select from Benchmark Presets (Nominal, Ambiguous, Infeasible, Adversarial)", "preset"),
                        questionary.Choice("Enter Custom Natural Language Intent", "custom"),
                    ],
                    allow_back=True,
                )
                if chosen_src == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["intent_source"] = chosen_src
                if chosen_src == "preset":
                    step_stack.append("intent_preset")
                else:
                    step_stack.append("intent_custom")

            elif step == "intent_preset":
                with open(COMPACT_CORPUS_PATH, encoding="utf-8") as f:
                    presets = json.load(f)
                preset_choices = [
                    questionary.Choice(f"[{p['id']}] ({p['class']}) {p['intent_text'][:60]}...", p['intent_text'])
                    for p in presets
                ]
                chosen_preset = prompt_select(
                    "Choose a preset demand:",
                    choices=preset_choices,
                    allow_back=True,
                )
                if chosen_preset == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["intent_text"] = chosen_preset
                break

            elif step == "intent_custom":
                custom_intent = prompt_text(
                    "Enter your optical network intent:",
                    default="Route 100G from Berlin to Frankfurt with at least 15 dB GSNR.",
                    allow_back=True,
                )
                if custom_intent == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["intent_text"] = custom_intent
                break

            elif step == "eval_corpus":
                chosen_corpus = prompt_select(
                    "Select Benchmark Corpus:",
                    choices=[
                        questionary.Choice("Compact Corpus (20 Demands - 4 Balanced Classes)", "compact"),
                        questionary.Choice("Full Corpus (120 Demands - 4 Balanced Classes)", "full"),
                    ],
                    allow_back=True,
                )
                if chosen_corpus == BACK_SENTINEL:
                    step_stack.pop()
                    continue
                wizard["corpus"] = chosen_corpus
                break

        mode = wizard["mode"]
        provider = wizard["provider"]
        model = wizard["model"]
        baseline = wizard["baseline"]
        intent_text = wizard.get("intent_text")
        corpus_choice = wizard.get("corpus", "compact")
    else:
        # Non-fully interactive execution: resolve mode first if not set
        if mode is None:
            if args.intent:
                mode = "interactive"
            else:
                mode = prompt_select(
                    "Select Execution Mode:",
                    choices=[
                        questionary.Choice("Interactive Mode (Single intent, live node tracking, no metrics export)", "interactive"),
                        questionary.Choice("Evaluation Benchmark Mode (Automated test corpus, Four Pillars metrics, export results)", "eval"),
                        questionary.Choice("Comparative Analysis Mode (Compare existing baseline runs with custom/latest run selection)", "compare"),
                    ],
                )

        if mode == "compare":
            run_comparative_mode(
                proposed_run=args.proposed_run,
                hitl_run=args.hitl_run,
                llm_run=args.llm_run,
                is_interactive=False,
            )
            return

        if not model:
            if provider == "ollama":
                model = os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
            elif provider == "openrouter":
                model = os.getenv("OPENROUTER_MODEL", DEFAULT_OPENROUTER_MODEL)
            elif provider == "openai":
                model = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
            else:
                model = os.getenv("KIMI_MODEL", DEFAULT_KIMI_MODEL)

        if baseline is None:
            baseline = prompt_select(
                "Select Baseline Architecture to Run:",
                choices=[
                    questionary.Choice("Proposed RADG (Dual Fail-Fast Risk Gates)", "proposed_radg"),
                    questionary.Choice("Always-On HITL (Paranoid Mandatory Clarification on Nominals)", "always_on_hitl"),
                    questionary.Choice("LLM-Only (No Semantic Gate / Controller Error Simulation)", "llm_only"),
                    questionary.Choice("Run All Baselines (Comparative Suite)", "all"),
                ],
            )

    # Initialize shared LLM instance
    console.print(f"[dim]Configuring LLM provider: {provider} | Model: {model} | Timeout: {timeout}s...[/dim]")
    llm = create_configured_llm(
        provider=provider,
        model=model,
        temperature=temperature,
        timeout=timeout,
        reasoning_effort=getattr(args, "reasoning_effort", None),
    )
    set_llm(llm)

    # -------------------------------------------------------------------------
    # Mode A: Interactive Execution
    # -------------------------------------------------------------------------
    if mode == "interactive":
        if not intent_text:
            intent_text = args.intent
        if not intent_text:
            intent_source = prompt_select(
                "How would you like to provide the intent?",
                choices=[
                    questionary.Choice("Select from Benchmark Presets (Nominal, Ambiguous, Infeasible, Adversarial)", "preset"),
                    questionary.Choice("Enter Custom Natural Language Intent", "custom"),
                ],
            )

            if intent_source == "preset":
                with open(COMPACT_CORPUS_PATH, encoding="utf-8") as f:
                    presets = json.load(f)
                preset_choices = [
                    questionary.Choice(f"[{p['id']}] ({p['class']}) {p['intent_text'][:60]}...", p['intent_text'])
                    for p in presets
                ]
                intent_text = prompt_select(
                    "Choose a preset demand:",
                    choices=preset_choices,
                )
            else:
                intent_text = prompt_text(
                    "Enter your optical network intent:",
                    default="Route 100G from Berlin to Frankfurt with at least 15 dB GSNR.",
                )

        target_baselines = ["proposed_radg", "always_on_hitl", "llm_only"] if baseline == "all" else [baseline]

        for b_id in target_baselines:
            if b_id == "proposed_radg":
                g_factory = compile_proposed_graph
            elif b_id == "always_on_hitl":
                g_factory = compile_always_on_graph
            elif b_id == "llm_only":
                g_factory = compile_llm_only_graph
            else:
                continue

            console.print(f"\n[bold magenta]══════ Running Baseline: {b_id.upper()} ══════[/bold magenta]")
            render_interactive_execution(
                graph_factory=g_factory,
                intent_text=intent_text,
                baseline_id=b_id,
            )

    # -------------------------------------------------------------------------
    # Mode B: Evaluation Benchmark Execution
    # -------------------------------------------------------------------------
    else:
        if not corpus_choice:
            corpus_choice = args.corpus or "compact"
            if not args.corpus:
                corpus_choice = prompt_select(
                    "Select Benchmark Corpus:",
                    choices=[
                        questionary.Choice("Compact Corpus (20 Demands - 4 Balanced Classes)", "compact"),
                        questionary.Choice("Full Corpus (120 Demands - 4 Balanced Classes)", "full"),
                    ],
                )

        target_corpus_file = COMPACT_CORPUS_PATH if corpus_choice == "compact" else FULL_CORPUS_PATH
        with open(target_corpus_file, encoding="utf-8") as f:
            corpus = json.load(f)

        if args.demand_id:
            corpus = [it for it in corpus if it.get("id") == args.demand_id]
        elif args.risk_class != "all":
            corpus = [it for it in corpus if it.get("class") == args.risk_class]

        run_id = time.strftime("%Y%m%d_%H%M%S")
        metadata = {
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "run_id": run_id,
            "provider": provider,
            "model": model,
            "timeout_seconds": timeout,
            "corpus": corpus_choice,
        }

        target_baselines = ["proposed_radg", "always_on_hitl", "llm_only"] if baseline == "all" else [baseline]
        all_eval_results: dict[str, list[dict[str, Any]]] = {}

        clean_model = sanitize_model_name(model)
        for b_id in target_baselines:
            b_output_dir = BASELINES_DIR / b_id / "results" / clean_model / run_id
            eval_res = run_evaluation_mode(
                baseline_id=b_id,
                corpus=corpus,
                output_dir=b_output_dir,
                metadata=metadata,
                intent_timeout=args.intent_timeout,
                warmup=not args.no_warmup,
            )
            all_eval_results[b_id] = eval_res

        if baseline == "all" and len(all_eval_results) > 1:
            common_output_dir = RESULTS_DIR / clean_model / run_id
            generate_comparative_report(
                all_results=all_eval_results,
                output_dir=common_output_dir,
                metadata=metadata,
            )
            console.print(
                Panel(
                    f"[bold green]✓ Comparative Multi-Baseline Summary Compiled![/bold green]\n"
                    f"Saved in: [bold cyan]{common_output_dir}[/bold cyan]\n"
                    f"├── comparative_results_{run_id}.json\n"
                    f"└── comparative_summary_{run_id}.md",
                    title="🏆 Multi-Baseline Benchmark Complete",
                    border_style="green",
                    box=box.ROUNDED,
                )
            )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Execution interrupted by operator. Exiting...[/yellow]")
        sys.exit(0)
