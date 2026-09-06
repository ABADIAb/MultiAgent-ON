#!/usr/bin/env python3
"""
Generate Figure 3.4: 2D Operational State Space of the Risk-Adaptive Decision Gate (RADG).
Axes:
- X-axis: Semantic Uncertainty U_sem in [0, 1] with delimiter tau_sem = 0.30
- Y-axis: GSNR Margin Delta GSNR = GSNR_computed - GSNR_th (dB) with delimiter at 0 dB
Quadrants:
- Auto-Approve Zone (Top-Left: U_sem <= 0.30, Delta GSNR >= 0)
- Replan Zone (Bottom-Left: U_sem <= 0.30, Delta GSNR < 0)
- Clarify Zone (Right: U_sem > 0.30, regardless of physical margin)
"""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def generate_figure_3_4():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(8.0, 5.8), dpi=300)

    # Thresholds
    tau_sem = 0.30

    # Background shading for the 3 operational zones
    # Zone 1: Auto-Approve (U_sem <= 0.30 and Delta GSNR >= 0)
    ax.axvspan(0.0, tau_sem, ymin=0.5, ymax=1.0, color="#C6F6D5", alpha=0.65, label="Auto-Approve Zone")
    # Zone 2: Replan (U_sem <= 0.30 and Delta GSNR < 0)
    ax.axvspan(0.0, tau_sem, ymin=0.0, ymax=0.5, color="#FED7D7", alpha=0.65, label="Replan Zone")
    # Zone 3: Clarify (U_sem > 0.30)
    ax.axvspan(tau_sem, 1.0, ymin=0.0, ymax=1.0, color="#FEEBC8", alpha=0.65, label="Clarify Zone")

    # Delimiter Lines
    ax.axvline(x=tau_sem, color="#C05621", linestyle="--", linewidth=2.0, label=r"Semantic Threshold $\tau_{sem} = 0.30$")
    ax.axhline(y=0.0, color="#C53030", linestyle="--", linewidth=2.0, label=r"Feasibility Boundary $\Delta\text{GSNR} = 0\text{ dB}$")

    # Axis Limits and Labels
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-6.0, 6.0)
    ax.set_xlabel(r"Semantic Uncertainty Metric $U_{sem} \in [0, 1]$", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel(r"Physical Margin $\Delta\text{GSNR} = \text{GSNR}_{path} - \text{GSNR}_{th}$ [dB]", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_title("Risk-Adaptive Decision Gate (RADG) 2D Operational Space", fontsize=12, fontweight="bold", pad=12)

    # Zone Descriptive Annotations
    # Auto-Approve
    ax.text(0.15, 3.0, "ZONE I:\nAUTO-APPROVE\n($a = \\text{approve}$)",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#1C4532",
            bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#22543D", alpha=0.85))
    ax.text(0.15, 1.2, "Semantic clarity established\nPhysical QoT satisfies target\nZero operator overhead",
            ha="center", va="center", fontsize=8, color="#22543D")

    # Replan
    ax.text(0.15, -3.0, "ZONE II:\nSUGGEST REPLAN\n($a = \\text{replan}$)",
            ha="center", va="center", fontsize=10, fontweight="bold", color="#742A2A",
            bbox=dict(boxstyle="round,pad=0.3", fc="#FFFFFF", ec="#742A2A", alpha=0.85))
    ax.text(0.15, -4.6, "Semantic intent understood\nTransmission infeasible\nHITL constraint relaxation",
            ha="center", va="center", fontsize=8, color="#742A2A")

    # Clarify
    ax.text(0.65, 0.0, "ZONE III:\nEARLY HITL CLARIFY\n($a = \\text{clarify}$)",
            ha="center", va="center", fontsize=11, fontweight="bold", color="#7B341E",
            bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec="#7B341E", alpha=0.9))
    ax.text(0.65, -1.8, "Grammar violation ($v_{struct} = 0$)\nor semantic divergence ($d_{sem} > \\tau_{sem}$)\nPhysical simulation strictly bypassed",
            ha="center", va="center", fontsize=8.5, color="#7B341E")

    # Grid & Spines
    ax.grid(True, linestyle=":", alpha=0.5, color="#718096")
    for spine in ax.spines.values():
        spine.set_color("#2D3748")
        spine.set_linewidth(1.1)

    # Legend
    ax.legend(loc="upper right", framealpha=0.95, fontsize=8.5, edgecolor="#A0AEC0")

    out_dir = Path(__file__).resolve().parent
    out_pdf = out_dir / "figure_3_4_radg_decision_space.pdf"
    out_png = out_dir / "figure_3_4_radg_decision_space.png"
    plt.savefig(out_pdf, bbox_inches="tight", format="pdf")
    plt.savefig(out_png, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated {out_pdf} and {out_png}")

if __name__ == "__main__":
    generate_figure_3_4()
