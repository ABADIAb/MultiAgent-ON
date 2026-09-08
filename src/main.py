"""CLI entrypoint for the Risk-Adaptive Neurosymbolic Intent Orchestrator (V5).

Usage:
    uv run python src/main.py  # Interactive mode with rich UI and arrow-key selection
    uv run python src/main.py "Route 100G from Berlin to Frankfurt with at least 15 dB GSNR"
    uv run python src/main.py --help  # View CLI flags
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

# Add project root to sys.path to allow running main.py directly
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command
import questionary
from rich import box
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.core.graph import compile_graph
from src.core.llm import DEFAULT_KIMI_MODEL, create_kimi_llm, set_llm
from src.core.state import ALLOWED_MSGPACK_MODULES
from src.services.testbed_client import MockTestbedClient

# Configure logging to prevent raw logger dumps from duplicating Rich panels in the CLI
logging.basicConfig(level=logging.ERROR)
for _logger_name in ("src.nodes.radg_node", "src.nodes.semantic_gate_node", "src.nodes.qot_validation"):
    logging.getLogger(_logger_name).setLevel(logging.ERROR)

console = Console()

# Phase display names and descriptive icons for live progress tracking
PHASE_META: dict[str, tuple[str, str]] = {
    "intent_ingest": ("Phase 1: Intent Ingestion", "Ingesting NL intent & scoping optical topology (GraphRAG)"),
    "pddl_parser": ("Phase 2: PDDL Translation", "Translating enriched intent to PDDL & AST CFG validation"),
    "reverse_prompt": ("Phase 3a: Reverse Prompting", "Reconstructing natural language intent from PDDL"),
    "semantic_gate": ("Phase 3: Semantic Gate", "Evaluating Semantic Uncertainty U_sem vs threshold"),
    "hitl_clarify": ("Phase 3b: HITL Clarification", "Awaiting operator clarification for ambiguous intent"),
    "symbolic_solver": ("Phase 4: Symbolic Solver", "Computing candidate lightpaths via Yen's K-Shortest Paths"),
    "qot_validation": ("Phase 5: QoT Physics Engine", "Evaluating physical-layer feasibility with GN-model"),
    "radg": ("Phase 6: Physical Risk Gate", "Applying Risk-Adaptive Decision Gate (RADG)"),
    "plan_synthesizer": ("Phase 7: Plan Synthesis", "Compiling auditable planning and provisioning report"),
}

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


def print_banner() -> None:
    """Render a modern visual banner for the application."""
    banner = Text()
    banner.append("⚡ MULTIAGENT-ON ", style="bold cyan")
    banner.append("│ Risk-Adaptive Neurosymbolic Intent Orchestrator (V5)\n", style="bold white")
    banner.append("Optical Backbone: ", style="dim")
    banner.append("Nobel-Germany 17-Node Network ", style="bold green")
    banner.append("│ Physical Model: ", style="dim")
    banner.append("Coherent GN-Model (C-Band 96-ch)\n", style="bold green")
    banner.append("Safety Guarantee: ", style="dim")
    banner.append("Pre-Deployment Fail-Fast Gates (Semantic Gate + Physical RADG)", style="italic yellow")

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


def interactive_configuration() -> dict[str, Any]:
    """Interactively prompt operator for LLM model and execution settings."""
    profile_choice = questionary.select(
        "Select Execution Profile:",
        choices=[
            questionary.Choice(
                title="⚡ Recommended Default (kimi-for-coding-highspeed | 8000 max tokens | temp=1.0)",
                value="default",
            ),
            questionary.Choice(
                title="🛠️  Custom Settings (Select model, temperature, reasoning tokens)",
                value="custom",
            ),
        ],
        style=QUESTIONARY_STYLE,
    ).ask()

    if profile_choice is None:
        console.print("[yellow]Setup cancelled by operator.[/yellow]")
        sys.exit(0)

    if profile_choice == "default":
        return {
            "model": DEFAULT_KIMI_MODEL,
            "temperature": 1.0,
            "max_tokens": 8000,
            "think_effort": None,
            "thinking_disabled": False,
        }

    # Custom configuration flow
    model = questionary.select(
        "Select Kimi LLM Model:",
        choices=[
            questionary.Choice(title="kimi-for-coding-highspeed (Ultra-fast reasoning, 262k ctx)", value="kimi-for-coding-highspeed"),
            questionary.Choice(title="k3 (1M context reasoning model)", value="k3"),
            questionary.Choice(title="kimi-for-coding (Standard coding model)", value="kimi-for-coding"),
        ],
        style=QUESTIONARY_STYLE,
    ).ask()

    if model is None:
        sys.exit(0)

    thinking_disabled = False
    think_effort = None
    if model == "k3":
        reasoning_mode = questionary.select(
            "Configure Reasoning (Thinking) Mode:",
            choices=[
                questionary.Choice(title="Default high effort reasoning", value="default"),
                questionary.Choice(title="Low effort reasoning", value="low"),
                questionary.Choice(title="Disable thinking mode (fastest, lower precision)", value="disabled"),
            ],
            style=QUESTIONARY_STYLE,
        ).ask()
        if reasoning_mode == "disabled":
            thinking_disabled = True
        elif reasoning_mode == "low":
            think_effort = "low"

    default_temp = "0.6" if thinking_disabled else "1.0"
    temp_str = questionary.text(
        "Sampling Temperature (0.0 to 1.0):",
        default=default_temp,
        validate=lambda val: True if 0.0 <= float(val) <= 1.0 else "Must be between 0.0 and 1.0",
        style=QUESTIONARY_STYLE,
    ).ask()

    default_tokens = "8000" if model == "kimi-for-coding-highspeed" else "2500"
    tokens_str = questionary.text(
        "Max Completion Tokens:",
        default=default_tokens,
        validate=lambda val: True if val.isdigit() and int(val) > 0 else "Must be a positive integer",
        style=QUESTIONARY_STYLE,
    ).ask()

    return {
        "model": model,
        "temperature": float(temp_str or default_temp),
        "max_tokens": int(tokens_str or default_tokens),
        "think_effort": think_effort,
        "thinking_disabled": thinking_disabled,
    }


def handle_hitl_interrupt(interrupt_val: dict[str, Any]) -> dict[str, Any] | None:
    """Display modern Rich panels for HITL interrupts and prompt with questionary."""
    console.print()

    # Case 1: Semantic Gate Clarification (Phase 3b)
    if interrupt_val.get("status") == "clarification_required":
        reconstruction = interrupt_val.get("reconstruction", "N/A")
        usem_score = interrupt_val.get("usem_score")
        pddl_valid = interrupt_val.get("pddl_valid")
        error_context = interrupt_val.get("error_context")

        panel_content = Text()
        panel_content.append("⚠️ SEMANTIC UNCERTAINTY EXCEEDS THRESHOLD\n\n", style="bold yellow")
        panel_content.append("System Reconstruction:\n", style="bold white")
        panel_content.append(f'"{reconstruction}"\n\n', style="italic cyan")

        usem_text = f"{usem_score:.3f}" if isinstance(usem_score, (int, float)) else "N/A"
        panel_content.append("Semantic Uncertainty (U_sem): ", style="bold white")
        panel_content.append(f"{usem_text} ", style="bold red" if (usem_score or 0) > 0.3 else "bold green")
        panel_content.append("(Tolerance Threshold τ_sem = 0.300)\n", style="dim")

        panel_content.append("CFG Syntax Valid: ", style="bold white")
        panel_content.append("PASS\n" if pddl_valid else "FAIL\n", style="bold green" if pddl_valid else "bold red")

        if error_context:
            panel_content.append(f"\nReason / Error: {error_context}\n", style="yellow")

        console.print(
            Panel(
                panel_content,
                title="[bold yellow]HITL Clarification Required (Phase 3b)[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED,
            )
        )

        choices = []
        if pddl_valid:
            choices.append(
                questionary.Choice(
                    title="✅ Proceed with current understanding (Approve and continue to solver)",
                    value="approve",
                )
            )
        choices.append(
            questionary.Choice(
                title="✏️  Refine / Clarify intent (Provide updated instructions)",
                value="refine",
            )
        )
        choices.append(
            questionary.Choice(
                title="❌ Cancel execution",
                value="cancel",
            )
        )

    # Case 2: Physical Risk Gate Replan (Phase 6 RADG)
    elif interrupt_val.get("decision") == "replan":
        raw_reason = interrupt_val.get("reason", "Physical QoT threshold violated.")
        clean_reason = raw_reason.replace("RADG Decision: SUGGEST REPLAN | ", "").strip()
        suggestion = interrupt_val.get("suggestion", "")
        qot_results = interrupt_val.get("qot_results") or []

        panel_content = Text()
        panel_content.append("⚠️ PHYSICAL-LAYER FEASIBILITY VIOLATION\n\n", style="bold red")
        panel_content.append(f"{clean_reason}\n\n", style="white")
        if suggestion:
            panel_content.append(f"Suggestion: {suggestion}\n", style="italic cyan")

        console.print(
            Panel(
                panel_content,
                title="[bold red]RADG Decision: SUGGEST REPLAN (Phase 6)[/bold red]",
                border_style="red",
                box=box.ROUNDED,
            )
        )

        if qot_results:
            table = Table(title="Evaluated Candidate Lightpaths", box=box.SIMPLE_HEAVY)
            table.add_column("Path ID", justify="center", style="cyan")
            table.add_column("Route", style="white")
            table.add_column("Computed GSNR", justify="right")
            table.add_column("Threshold", justify="right")
            table.add_column("Status", justify="center")

            for idx, res in enumerate(qot_results, start=1):
                route = " ➔ ".join(res.get("path", []))
                snr = f"{res.get('snr_dB', 0.0):.2f} dB"
                thresh = f"{res.get('threshold_dB', 0.0):.2f} dB"
                status_str = "[green]FEASIBLE[/green]" if res.get("feasible") else "[red]INFEASIBLE[/red]"
                table.add_row(str(idx), route, snr, thresh, status_str)

            console.print(table)
            console.print()

        choices = [
            questionary.Choice(title="🔄 Replan (Relax GSNR threshold or modify route)", value="replan"),
            questionary.Choice(title="❌ Cancel Execution", value="cancel"),
        ]

    # Generic fallback
    else:
        console.print(Panel(str(interrupt_val), title="[bold yellow]HITL Interrupt[/bold yellow]", border_style="yellow"))
        choices = [
            questionary.Choice(title="✅ Approve", value="approve"),
            questionary.Choice(title="✏️  Refine", value="refine"),
            questionary.Choice(title="❌ Cancel", value="cancel"),
        ]

    action = questionary.select(
        "Select Action (Use ↑/↓ arrows, press Enter):",
        choices=choices,
        style=QUESTIONARY_STYLE,
    ).ask()

    if action is None or action == "cancel":
        console.print("[yellow]Pipeline execution cancelled by operator.[/yellow]")
        return None

    if action in ("refine", "replan", "clarify"):
        feedback = questionary.text(
            "Enter your feedback / updated constraints:",
            style=QUESTIONARY_STYLE,
        ).ask()
        if feedback is None:
            console.print("[yellow]Pipeline execution cancelled by operator.[/yellow]")
            return None
        return {"action": action, "feedback": feedback.strip()}

    return {"action": action}


def display_results(result: dict[str, Any]) -> None:
    """Format and display final planning results with Rich tables and markdown."""
    console.print()
    planning_report = result.get("planning_report")
    qot_results = result.get("qot_results") or []

    if qot_results:
        table = Table(
            title="Physical-Layer QoT Evaluation Summary (GN-Model)",
            box=box.ROUNDED,
            header_style="bold cyan",
        )
        table.add_column("#", justify="center", style="dim")
        table.add_column("Candidate Route", style="bold white")
        table.add_column("Computed GSNR", justify="right")
        table.add_column("Threshold", justify="right")
        table.add_column("Margin (ΔGSNR)", justify="right")
        table.add_column("Verdict", justify="center")

        for idx, res in enumerate(qot_results, start=1):
            route = " ➔ ".join(res.get("path", []))
            snr = res.get("snr_dB", 0.0)
            thresh = res.get("threshold_dB", 0.0)
            margin = snr - thresh
            feasible = res.get("feasible", False)

            status_style = "bold green" if feasible else "bold red"
            status_badge = "[bold green]✓ FEASIBLE[/bold green]" if feasible else "[bold red]✗ INFEASIBLE[/bold red]"
            margin_badge = f"[{status_style}]{margin:+.2f} dB[/{status_style}]"

            table.add_row(
                str(idx),
                route,
                f"{snr:.2f} dB",
                f"{thresh:.2f} dB",
                margin_badge,
                status_badge,
            )

        console.print(table)
        console.print()

    if planning_report:
        console.print(
            Panel(
                Markdown(planning_report),
                title="[bold green]📋 Final Auditable Planning Report[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
    else:
        console.print(Panel("Execution finished without a planning report.", border_style="yellow"))


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Risk-Adaptive Neurosymbolic Intent Orchestrator for Optical Networks (V5)"
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Optional natural language intent string. If omitted, starts in interactive mode.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Kimi LLM model identifier (default: {DEFAULT_KIMI_MODEL})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=None,
        help="Sampling temperature (default: 1.0 for reasoning, 0.6 if disabled)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=None,
        help="Maximum completion tokens (default: 8000 for highspeed, 2500 for k3)",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Disable interactive question prompts and run directly with defaults/flags",
    )
    return parser.parse_args()


def main() -> None:
    """Entrypoint function."""
    load_dotenv()
    args = parse_args()

    api_key = os.getenv("KIMI_API_KEY", "")
    base_url = os.getenv("KIMI_BASE_URL", "")

    if not api_key:
        console.print(
            Panel(
                "[bold red]ERROR: KIMI_API_KEY is not set in your environment or .env file.[/bold red]\n\n"
                "Please configure your .env file with:\n"
                '  KIMI_API_KEY="your-api-key-here"\n'
                '  KIMI_BASE_URL="https://api.kimi.com/coding/v1"\n'
                f'  KIMI_MODEL="{DEFAULT_KIMI_MODEL}"',
                title="[bold red]Missing API Credentials[/bold red]",
                border_style="red",
            )
        )
        sys.exit(1)

    print_banner()

    # Determine query and config
    query_from_args = " ".join(args.query).strip() if args.query else None

    if query_from_args or args.no_interactive:
        llm_config = {
            "model": args.model or os.getenv("KIMI_MODEL", DEFAULT_KIMI_MODEL),
            "temperature": args.temperature if args.temperature is not None else 1.0,
            "max_tokens": args.max_tokens or (8000 if (args.model or DEFAULT_KIMI_MODEL) == DEFAULT_KIMI_MODEL else 2500),
            "think_effort": None,
            "thinking_disabled": False,
        }
        user_input = query_from_args or "Route 100G optical circuit from Berlin to Frankfurt with at least 15 dB GSNR"
    else:
        llm_config = interactive_configuration()
        example_intent = "Route 100G optical circuit from Berlin to Frankfurt with at least 15 dB GSNR"
        raw_input = questionary.text(
            "Enter Operator Intent:",
            placeholder=example_intent,
            style=QUESTIONARY_STYLE,
        ).ask()
        if raw_input is None:
            console.print("[yellow]Setup cancelled by operator.[/yellow]")
            sys.exit(0)
        user_input = raw_input.strip() or example_intent

    # Initialize LLM
    llm = create_kimi_llm(
        api_key=api_key,
        base_url=base_url or None,
        model=str(llm_config["model"]) if llm_config.get("model") else None,
        temperature=float(llm_config["temperature"]) if llm_config.get("temperature") is not None else None,
        max_tokens=int(llm_config["max_tokens"]) if llm_config.get("max_tokens") is not None else None,
        think_effort=str(llm_config["think_effort"]) if llm_config.get("think_effort") else None,
        thinking_disabled=bool(llm_config.get("thinking_disabled", False)),
    )
    set_llm(llm)

    console.print()
    console.print(
        f"[dim]Engine configured:[/dim] [bold cyan]{llm_config['model']}[/bold cyan] "
        f"[dim](max_tokens={llm_config['max_tokens']}, temp={llm_config['temperature']})[/dim]"
    )
    console.print(f"[dim]Processing Intent:[/dim] [bold white]\"{user_input}\"[/bold white]")
    console.print()

    # Setup Graph with safe msgpack whitelist to avoid deserialization warnings
    checkpointer = InMemorySaver(
        serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
    )
    graph = compile_graph(checkpointer=checkpointer)

    topology_snapshot = MockTestbedClient().get_topology()

    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "enriched_intent": None,
        "pddl_constraints": None,
        "pddl_valid": None,
        "hitl_reconstruction": None,
        "hitl_approved": None,
        "topology_snapshot": topology_snapshot,
        "candidate_paths": None,
        "qot_results": None,
        "planning_report": None,
        "error_context": None,
    }

    config = {"configurable": {"thread_id": "cli-session"}}
    stream_input: Any = initial_state

    # Execution & HITL Loop
    while True:
        with console.status("[bold cyan]Initializing Neurosymbolic Pipeline...[/bold cyan]", spinner="dots") as status:
            for event in graph.stream(stream_input, config=config, stream_mode="updates"):
                if "__interrupt__" in event:
                    continue

                for node_name in event:
                    phase_title, phase_desc = PHASE_META.get(
                        node_name, (f"Node: {node_name}", "Executing pipeline node...")
                    )
                    console.print(f"  [bold green]✓[/bold green] [cyan]{phase_title}[/cyan] [dim]({phase_desc})[/dim]")
                    status.update("[bold cyan]Processing next pipeline stage...[/bold cyan]")

        # Check for interrupt
        state = graph.get_state(config)
        if state.next:
            interrupt_val: dict[str, Any] = {}
            if state.tasks:
                for task in state.tasks:
                    if hasattr(task, "interrupts") and task.interrupts:
                        interrupt_val = task.interrupts[0].value
                        break

            resume_cmd = handle_hitl_interrupt(interrupt_val)
            if resume_cmd is None:
                # Cancelled by user
                return

            console.print("[dim]Resuming pipeline execution with operator input...[/dim]\n")
            stream_input = Command(resume=resume_cmd)
            continue

        # Completed successfully
        display_results(state.values)
        break


if __name__ == "__main__":
    main()
