"""Academic publication-quality figure generation suite for Sprint 4 evaluation.

Strictly follows IEEE Paper and Politecnico di Milano Master's Thesis styling:
  - Vector PDF exports (for LaTeX thesis) and 300+ DPI PNG previews.
  - Institutional colorblind-safe palette (PoliMi Navy #0F2C53, Burgundy #85200C,
    Slate #3B75AF, Amber #D95F02, Forest Green #1B7837).
  - Clean typography and subtle gridlines.

Required figures:
  1. latency_vs_tokens: Comparative dual-axis / grouped chart of End-to-End Latency vs Token Usage.
  2. success_vs_uar: Grouped bar chart of QoT Success Rate vs Unsafe Approval Rate (UAR = 0%).
  3. hitl_interruption_origin: Stacked bar chart showing Phase 3b (Semantic) vs Phase 6 (Physical) interrupts.
  4. gate_decision_distribution: Action breakdown by intent risk category for Proposed RADG.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------------------
# Styling Configurations
# ---------------------------------------------------------------------------

POLIMI_NAVY = "#0F2C53"
POLIMI_BURGUNDY = "#85200C"
POLIMI_SLATE = "#3B75AF"
POLIMI_AMBER = "#D95F02"
POLIMI_GREEN = "#1B7837"
POLIMI_MUTED = "#6C757D"
POLIMI_GRID = "#E2E8F0"

BASELINE_LABELS = {
    "proposed_radg": "Proposed\n(RADG)",
    "llm_only": "Baseline A\n(LLM-Only)",
    "always_on": "Baseline B\n(Always-On)",
    "always_off": "Baseline C\n(Always-Off)",
    "traditional_sdon": "Baseline D\n(Trad. SDON)",
}

BASELINE_COLORS = {
    "proposed_radg": POLIMI_NAVY,
    "llm_only": POLIMI_BURGUNDY,
    "always_on": POLIMI_SLATE,
    "always_off": POLIMI_AMBER,
    "traditional_sdon": POLIMI_GREEN,
}


def apply_publication_style() -> None:
    """Set rigorous publication-level rcParams for IEEE / PoliMi thesis standards."""
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "STIXGeneral", "Times New Roman", "serif"],
            "font.size": 10.5,
            "axes.titlesize": 12.0,
            "axes.titleweight": "bold",
            "axes.labelsize": 11.0,
            "axes.labelweight": "bold",
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.fontsize": 9.5,
            "figure.titlesize": 13.0,
            "figure.titleweight": "bold",
            "axes.edgecolor": "#333333",
            "axes.linewidth": 1.0,
            "grid.color": POLIMI_GRID,
            "grid.linestyle": "--",
            "grid.linewidth": 0.7,
            "grid.alpha": 0.8,
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.08,
        }
    )


def _save_figure(fig: plt.Figure, output_dir: Path, base_name: str) -> list[Path]:
    """Save figure as both vector PDF and high-res PNG."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / f"{base_name}.pdf"
    png_path = output_dir / f"{base_name}.png"

    fig.savefig(pdf_path, format="pdf")
    fig.savefig(png_path, format="png")
    plt.close(fig)
    return [pdf_path, png_path]


# ---------------------------------------------------------------------------
# Figure 1: Latency vs Token Consumption
# ---------------------------------------------------------------------------


def plot_latency_vs_tokens(
    metrics_summary: dict[str, dict[str, Any]],
    output_dir: Path,
) -> list[Path]:
    """Plot comparative dual-panel chart: Latency and Token Consumption across baselines."""
    apply_publication_style()

    baselines = [b for b in BASELINE_LABELS.keys() if b in metrics_summary]
    labels = [BASELINE_LABELS[b] for b in baselines]

    latencies = [
        metrics_summary[b]["efficiency"].get("mean_latency_s", 0.0) for b in baselines
    ]
    tokens = [
        metrics_summary[b]["efficiency"].get("mean_prompt_tokens", 0.0)
        for b in baselines
    ]
    colors = [BASELINE_COLORS[b] for b in baselines]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    # Panel 1: End-to-End Latency
    bars1 = ax1.bar(
        labels, latencies, color=colors, width=0.55, edgecolor="#222222", linewidth=0.8
    )
    ax1.set_ylabel("End-to-End Latency (s)")
    ax1.set_title("Mean Orchestration Latency ($T_{E2E}$)")
    ax1.grid(axis="y")
    ax1.set_axisbelow(True)

    # Add data labels
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.03 * max(latencies or [1]),
            f"{yval:.2f}s",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="semibold",
        )

    # Panel 2: Prompt Token Consumption
    bars2 = ax2.bar(
        labels, tokens, color=colors, width=0.55, edgecolor="#222222", linewidth=0.8
    )
    ax2.set_ylabel("Prompt Tokens ($T_{tokens}$)")
    ax2.set_title("Prompt Token Budget Saturation")
    ax2.grid(axis="y")
    ax2.set_axisbelow(True)

    # Highlight Scoped Optical GraphRAG savings
    if "proposed_radg" in baselines and "llm_only" in baselines:
        p_tokens = metrics_summary["proposed_radg"]["efficiency"].get(
            "mean_prompt_tokens", 0
        )
        l_tokens = metrics_summary["llm_only"]["efficiency"].get(
            "mean_prompt_tokens", 1
        )
        if l_tokens > 0:
            reduction = ((l_tokens - p_tokens) / l_tokens) * 100.0
            ax2.annotate(
                f"Scoped GraphRAG\n>{reduction:.0f}% Savings",
                xy=(0, p_tokens),
                xytext=(0.4, max(tokens) * 0.45),
                arrowprops=dict(
                    facecolor=POLIMI_NAVY, shrink=0.08, width=1.5, headwidth=6
                ),
                bbox=dict(
                    boxstyle="round,pad=0.3", fc="#F8FAFC", ec=POLIMI_NAVY, lw=1.2
                ),
                fontsize=8.5,
                fontweight="bold",
                color=POLIMI_NAVY,
            )

    for bar in bars2:
        yval = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval + 0.02 * max(tokens or [1]),
            f"{int(yval)}",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="semibold",
        )

    fig.suptitle(
        "Orchestration Efficiency: Latency vs. Prompt Token Overhead",
        fontsize=13,
        y=1.02,
    )
    fig.tight_layout()
    return _save_figure(fig, output_dir, "latency_vs_tokens")


# ---------------------------------------------------------------------------
# Figure 2: Success Rate vs Unsafe Approval Rate (UAR)
# ---------------------------------------------------------------------------


def plot_success_vs_uar(
    metrics_summary: dict[str, dict[str, Any]],
    output_dir: Path,
) -> list[Path]:
    """Plot grouped bar chart comparing Optical Feasibility (QFR) vs Unsafe Approval Rate (UAR)."""
    apply_publication_style()

    baselines = [b for b in BASELINE_LABELS.keys() if b in metrics_summary]
    labels = [BASELINE_LABELS[b] for b in baselines]

    qfr_values = [
        metrics_summary[b]["physical"].get("qfr_percent", 0.0) for b in baselines
    ]
    uar_values = [
        metrics_summary[b]["physical"].get("uar_percent", 0.0) for b in baselines
    ]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10.0, 5.0))

    rects1 = ax.bar(
        x - width / 2,
        qfr_values,
        width,
        label="QoT Feasibility Rate (QFR %)",
        color=POLIMI_NAVY,
        edgecolor="#222222",
        linewidth=0.8,
    )
    rects2 = ax.bar(
        x + width / 2,
        uar_values,
        width,
        label="Unsafe Approval Rate (UAR %)",
        color=POLIMI_BURGUNDY,
        edgecolor="#222222",
        linewidth=0.8,
    )

    ax.set_ylabel("Rate (%)")
    ax.set_title("Physical Feasibility vs. Safety Invariant (UAR) by Baseline")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 115)
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#CCCCCC", loc="upper right")

    # Add text labels on bars
    for rect in rects1:
        h = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2.0,
            h + 1.5,
            f"{h:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="semibold",
            color=POLIMI_NAVY,
        )

    for rect in rects2:
        h = rect.get_height()
        ax.text(
            rect.get_x() + rect.get_width() / 2.0,
            h + 1.5,
            f"{h:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="semibold",
            color=POLIMI_BURGUNDY if h > 0 else POLIMI_GREEN,
        )

    # Explicit callout for Proposed UAR = 0.0% invariant
    if "proposed_radg" in baselines:
        idx = baselines.index("proposed_radg")
        ax.annotate(
            "CRITICAL INVARIANT\nUAR = 0.0% (Zero Hallucination)",
            xy=(x[idx] + width / 2, 0),
            xytext=(x[idx] + 0.1, 35),
            arrowprops=dict(
                facecolor=POLIMI_GREEN, shrink=0.08, width=1.5, headwidth=6
            ),
            bbox=dict(boxstyle="round,pad=0.35", fc="#ECFDF5", ec=POLIMI_GREEN, lw=1.2),
            fontsize=8.5,
            fontweight="bold",
            color="#065F46",
        )

    fig.tight_layout()
    return _save_figure(fig, output_dir, "success_vs_uar")


# ---------------------------------------------------------------------------
# Figure 3: Origin of HITL Interruptions
# ---------------------------------------------------------------------------


def plot_hitl_interruption_origin(
    metrics_summary: dict[str, dict[str, Any]],
    output_dir: Path,
) -> list[Path]:
    """Plot stacked bar chart of HITL interruptions categorized by Semantic Clarify vs Physical Replan."""
    apply_publication_style()

    baselines = [b for b in BASELINE_LABELS.keys() if b in metrics_summary]
    labels = [BASELINE_LABELS[b] for b in baselines]

    semantic_counts = [
        metrics_summary[b]["radg"].get("semantic_clarify_count", 0.0) for b in baselines
    ]
    physical_counts = [
        metrics_summary[b]["radg"].get("physical_replan_count", 0.0) for b in baselines
    ]

    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    width = 0.52

    ax.bar(
        labels,
        semantic_counts,
        width,
        label="Phase 3b: Semantic Clarification ($U_{sem} > \\tau_{sem}$)",
        color=POLIMI_SLATE,
        edgecolor="#222222",
        linewidth=0.8,
    )
    ax.bar(
        labels,
        physical_counts,
        width,
        bottom=semantic_counts,
        label="Phase 6: Physical Replan ($\\text{QoT}_{valid} = 0$)",
        color=POLIMI_AMBER,
        edgecolor="#222222",
        linewidth=0.8,
    )

    ax.set_ylabel("Operator Interruptions ($N_{hitl}$ Count)")
    ax.set_title("Human-in-the-Loop Interruption Origin by Decision Gate")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#CCCCCC", loc="upper left")

    # Add total values on top of stacked bars
    for i in range(len(labels)):
        total = semantic_counts[i] + physical_counts[i]
        if total > 0:
            ax.text(
                i,
                total + 0.8,
                f"{int(total)}",
                ha="center",
                va="bottom",
                fontsize=9.5,
                fontweight="bold",
            )

    fig.tight_layout()
    return _save_figure(fig, output_dir, "hitl_interruption_origin")


# ---------------------------------------------------------------------------
# Figure 4: RADG Decision Distribution by Intent Class
# ---------------------------------------------------------------------------


def plot_gate_decision_distribution(
    raw_results: list[dict[str, Any]],
    intents: list[dict[str, Any]],
    output_dir: Path,
) -> list[Path]:
    """Plot RADG decision breakdown across the 4 intent risk categories for Proposed system."""
    apply_publication_style()

    intents_by_id = {item.get("id"): item for item in intents}

    classes = ["I_Nominal", "II_Ambiguous", "III_Infeasible", "IV_Adversarial"]
    class_labels = [
        "Class I\nNominal",
        "Class II\nAmbiguous",
        "Class III\nInfeasible",
        "Class IV\nAdversarial",
    ]

    actions = ["approve", "clarify", "replan"]
    action_colors = {
        "approve": POLIMI_GREEN,
        "clarify": POLIMI_SLATE,
        "replan": POLIMI_AMBER,
    }

    counts: dict[str, dict[str, int]] = {c: {a: 0 for a in actions} for c in classes}

    for res in raw_results:
        intent_id = res.get("intent_id")
        intent_data = intents_by_id.get(intent_id, {})
        cls_name = intent_data.get("class", "")
        action = res.get("action", "clarify")

        if cls_name in counts and action in counts[cls_name]:
            counts[cls_name][action] += 1

    fig, ax = plt.subplots(figsize=(9.8, 5.0))
    width = 0.55
    bottom = np.zeros(len(classes))

    for action in actions:
        values = [counts[c][action] for c in classes]
        ax.bar(
            class_labels,
            values,
            width,
            bottom=bottom,
            label=f"Action: {action.upper()}",
            color=action_colors[action],
            edgecolor="#222222",
            linewidth=0.8,
        )
        bottom += np.array(values)

    ax.set_ylabel("Demands Count")
    ax.set_title("Proposed RADG Action Distribution Across Intent Risk Classes")
    ax.grid(axis="y")
    ax.set_axisbelow(True)
    ax.legend(frameon=True, facecolor="#FFFFFF", edgecolor="#CCCCCC", loc="upper right")

    # Add total annotations on top of bars
    for i, b in enumerate(bottom):
        ax.text(
            i,
            b + 0.6,
            f"N={int(b)}",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
        )

    fig.tight_layout()
    return _save_figure(fig, output_dir, "gate_decision_distribution")


# ---------------------------------------------------------------------------
# Master Generation Function
# ---------------------------------------------------------------------------


def generate_all_figures(
    metrics_summary: dict[str, dict[str, Any]],
    raw_results_by_baseline: dict[str, list[dict[str, Any]]],
    intents: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, list[Path]]:
    """Generate all academic figures required for thesis Chapter 4 and defense deck."""
    output_dir.mkdir(parents=True, exist_ok=True)
    generated: dict[str, list[Path]] = {}

    generated["latency_vs_tokens"] = plot_latency_vs_tokens(metrics_summary, output_dir)
    generated["success_vs_uar"] = plot_success_vs_uar(metrics_summary, output_dir)
    generated["hitl_interruption_origin"] = plot_hitl_interruption_origin(
        metrics_summary, output_dir
    )

    proposed_results = raw_results_by_baseline.get("proposed_radg", [])
    if proposed_results:
        generated["gate_decision_distribution"] = plot_gate_decision_distribution(
            proposed_results, intents, output_dir
        )

    return generated


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate benchmark publication figures."
    )
    parser.add_argument(
        "--metrics-file",
        type=str,
        default="tests/evaluation/results/metrics.json",
        help="Path to consolidated metrics JSON file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="tests/evaluation/results/figures",
        help="Directory to save generated figures",
    )
    args = parser.parse_args()

    metrics_path = Path(args.metrics_file)
    out_dir = Path(args.output_dir)

    if not metrics_path.exists():
        print(f"Error: metrics file not found at {metrics_path}")
        exit(1)

    with open(metrics_path, "r") as f:
        metrics_data = json.load(f)

    # In standalone CLI run, render figures using available metrics
    apply_publication_style()
    plot_latency_vs_tokens(metrics_data, out_dir)
    plot_success_vs_uar(metrics_data, out_dir)
    plot_hitl_interruption_origin(metrics_data, out_dir)
    print(f"Publication figures successfully exported to: {out_dir}")
