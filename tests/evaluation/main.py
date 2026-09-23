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
import questionary  # noqa: E402
from rich import box  # noqa: E402
from rich.console import Console  # noqa: E402
from rich.markdown import Markdown  # noqa: E402
from rich.panel import Panel  # noqa: E402
from rich.table import Table  # noqa: E402
from rich.text import Text  # noqa: E402

from src.core.llm import (  # noqa: E402
    DEFAULT_LLM_TIMEOUT,
    DEFAULT_OLLAMA_MODEL,
    create_configured_llm,
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
RESULTS_ROOT = PROJECT_ROOT / "tests" / "evaluation" / "results"

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

            # Interactive prompt for operator
            action_choice = questionary.select(
                "How would you like to respond to this gate interrupt?",
                choices=[
                    questionary.Choice("Provide Refined Intent (Recommended)", "refine"),
                    questionary.Choice("Use Standard Benchmark Recovery Intent", "standard"),
                    questionary.Choice("Abort Execution", "abort"),
                ],
                style=QUESTIONARY_STYLE,
            ).ask()

            if action_choice == "abort":
                console.print("[red]Execution aborted by operator.[/red]")
                return

            if action_choice == "standard":
                feedback = STANDARD_FOLLOW_UP_INTENT
                console.print(f"[dim]Injecting standard recovery intent:[/dim] \"{feedback}\"")
            else:
                feedback = questionary.text(
                    "Enter refined intent or constraint feedback:",
                    default=STANDARD_FOLLOW_UP_INTENT,
                    style=QUESTIONARY_STYLE,
                ).ask()

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
                console.print(Markdown(str(final_report)[:1000] + ("..." if len(str(final_report)) > 1000 else "")))
            break


def run_evaluation_mode(
    baseline_id: str,
    corpus: list[dict[str, Any]],
    output_dir: Path,
    metadata: dict[str, Any],
    max_turns: int = 3,
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
            f"[bold white]Output Directory:[/bold white] {output_dir}",
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
        verbose=True,
        generate_visuals=True,
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
        "Pillar 2: Physical Feasibility",
        "Unfeasible Approval Rate",
        f"{p2.get('uar_rate', 0.0):.1f}%",
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
        "Mean End-to-End Latency",
        f"{p3.get('mean_e2e_latency_seconds', 0.0):.2f}s",
        "Contextual",
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
        choices=["interactive", "eval"],
        help="Execution mode (interactive single intent vs evaluation benchmark)",
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default="compact",
        choices=["compact", "full"],
        help="Evaluation corpus (default: 'compact')",
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
        choices=["ollama", "openrouter", "kimi"],
        help="LLM provider",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
        help="Model name",
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
        "--temperature",
        type=float,
        default=0.2,
        help="Sampling temperature (default: 0.2)",
    )
    return parser.parse_args()


def main() -> None:
    """Entry point for the evaluation CLI."""
    load_dotenv()
    args = parse_args()
    print_banner()

    # 1. Resolve Provider and Model
    provider = args.provider
    model = args.model
    timeout = resolve_llm_timeout(args.timeout)
    temperature = args.temperature

    # Interactive configuration if neither baseline nor mode is specified
    is_fully_interactive = (args.baseline is None and args.mode is None and args.intent is None)

    if is_fully_interactive:
        provider = questionary.select(
            "Select LLM Provider:",
            choices=[
                questionary.Choice("Ollama (Local Open-Weights)", "ollama"),
                questionary.Choice("OpenRouter (Cloud API)", "openrouter"),
                questionary.Choice("Kimi / Moonshot (Cloud API)", "kimi"),
            ],
            default=provider,
            style=QUESTIONARY_STYLE,
        ).ask()

        default_model = "qwen2.5:3b" if provider == "ollama" else ("inclusionai/ling-3.0-flash-vl:free" if provider == "openrouter" else "moonshot-v1-8k")
        model = questionary.text(
            f"Enter Model Name for {provider}:",
            default=default_model,
            style=QUESTIONARY_STYLE,
        ).ask()

    # Initialize shared LLM instance
    console.print(f"[dim]Configuring LLM provider: {provider} | Model: {model} | Timeout: {timeout}s...[/dim]")
    llm = create_configured_llm(
        provider=provider,
        model=model,
        temperature=temperature,
        timeout=timeout,
    )
    set_llm(llm)

    # 2. Select Baseline
    baseline = args.baseline
    if baseline is None:
        baseline = questionary.select(
            "Select Baseline Architecture to Run:",
            choices=[
                questionary.Choice("Proposed RADG (Dual Fail-Fast Risk Gates)", "proposed_radg"),
                questionary.Choice("Always-On HITL (Paranoid Mandatory Clarification on Nominals)", "always_on_hitl"),
                questionary.Choice("LLM-Only (No Semantic Gate / Controller Error Simulation)", "llm_only"),
                questionary.Choice("Run All Baselines (Comparative Suite)", "all"),
            ],
            style=QUESTIONARY_STYLE,
        ).ask()

    # 3. Select Mode
    mode = args.mode
    if mode is None and args.intent is None:
        mode = questionary.select(
            "Select Execution Mode:",
            choices=[
                questionary.Choice("Interactive Mode (Single intent, live node tracking, no metrics export)", "interactive"),
                questionary.Choice("Evaluation Benchmark Mode (Automated test corpus, Four Pillars metrics, export results)", "eval"),
            ],
            style=QUESTIONARY_STYLE,
        ).ask()
    elif args.intent:
        mode = "interactive"

    # -------------------------------------------------------------------------
    # Mode A: Interactive Execution
    # -------------------------------------------------------------------------
    if mode == "interactive":
        intent_text = args.intent
        if not intent_text:
            intent_source = questionary.select(
                "How would you like to provide the intent?",
                choices=[
                    questionary.Choice("Select from Benchmark Presets (Nominal, Ambiguous, Infeasible, Adversarial)", "preset"),
                    questionary.Choice("Enter Custom Natural Language Intent", "custom"),
                ],
                style=QUESTIONARY_STYLE,
            ).ask()

            if intent_source == "preset":
                with open(COMPACT_CORPUS_PATH, encoding="utf-8") as f:
                    presets = json.load(f)
                preset_choices = [
                    questionary.Choice(f"[{p['id']}] ({p['class']}) {p['intent_text'][:60]}...", p['intent_text'])
                    for p in presets
                ]
                intent_text = questionary.select(
                    "Choose a preset demand:",
                    choices=preset_choices,
                    style=QUESTIONARY_STYLE,
                ).ask()
            else:
                intent_text = questionary.text(
                    "Enter your optical network intent:",
                    default="Route 100G from Berlin to Frankfurt with at least 15 dB GSNR.",
                    style=QUESTIONARY_STYLE,
                ).ask()

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
        corpus_choice = args.corpus
        if is_fully_interactive and args.corpus == "compact":
            corpus_choice = questionary.select(
                "Select Benchmark Corpus:",
                choices=[
                    questionary.Choice("Compact Corpus (20 Demands - 4 Balanced Classes)", "compact"),
                    questionary.Choice("Full Corpus (107 Demands)", "full"),
                ],
                style=QUESTIONARY_STYLE,
            ).ask()

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

        for b_id in target_baselines:
            b_output_dir = RESULTS_ROOT / b_id / f"run_{run_id}"
            run_evaluation_mode(
                baseline_id=b_id,
                corpus=corpus,
                output_dir=b_output_dir,
                metadata=metadata,
            )


if __name__ == "__main__":
    main()
