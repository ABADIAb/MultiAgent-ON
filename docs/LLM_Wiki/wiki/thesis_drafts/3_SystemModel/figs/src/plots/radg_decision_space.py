#!/usr/bin/env python3
"""
Generate Figure 3.4: 2D Operational State Space of the Risk-Adaptive Decision Gate (RADG).

Axes:
- X-axis: Semantic Uncertainty U_sem in [0, 1] with delimiter tau_sem = 0.30
- Y-axis: GSNR Margin Delta GSNR = GSNR_computed - GSNR_th (dB) with delimiter at 0 dB

Quadrants / Zones:
- Zone I: Auto-Approve (Top-Left: U_sem <= 0.30, Delta GSNR >= 0) -> a = approve
- Zone II: Suggest Replan (Bottom-Left: U_sem <= 0.30, Delta GSNR < 0) -> a = replan
- Zone III: Early HITL Clarify (Right: U_sem > 0.30) -> a = clarify (physics bypassed)
"""
from pathlib import Path
import matplotlib.pyplot as plt

def generate_figure_3_4():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(8.5, 6.0), dpi=300)

    tau_sem = 0.30

    # Background shading for the 3 operational zones
    # Zone 1: Auto-Approve (U_sem <= 0.30 and Delta GSNR >= 0)
    ax.axvspan(0.0, tau_sem, ymin=0.5, ymax=1.0, color="#C6F6D5", alpha=0.65, label="Zone I: Auto-Approve")
    # Zone 2: Suggest Replan (U_sem <= 0.30 and Delta GSNR < 0)
    ax.axvspan(0.0, tau_sem, ymin=0.0, ymax=0.5, color="#FED7D7", alpha=0.65, label="Zone II: Suggest Replan")
    # Zone 3: Clarify (U_sem > 0.30)
    ax.axvspan(tau_sem, 1.0, ymin=0.0, ymax=1.0, color="#FEEBC8", alpha=0.65, label="Zone III: Early Clarify")

    # Delimiter Lines
    ax.axvline(x=tau_sem, color="#C05621", linestyle="--", linewidth=2.0, label=r"Semantic Threshold $\tau_{sem} = 0.30$")
    ax.axhline(y=0.0, color="#C53030", linestyle="--", linewidth=2.0, label=r"Physical Boundary $\Delta\text{GSNR} = 0\text{ dB}$")

    # Axis Limits and Labels
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-6.0, 6.0)
    ax.set_xlabel(r"Semantic Uncertainty Metric $U_{sem} \in [0, 1]$", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_ylabel(r"Physical Margin $\Delta\text{GSNR} = \text{GSNR}_{path} - \text{GSNR}_{th}$ [dB]", fontsize=11, fontweight="bold", labelpad=8)
    ax.set_title("Risk-Adaptive Decision Gate (RADG) 2D Operational Space", fontsize=12, fontweight="bold", pad=12)

    # Zone Descriptive Annotations with opaque badges
    # Zone I: Auto-Approve
    ax.text(0.15, 3.2, "ZONE I:\nAUTO-APPROVE\n($a = \\text{approve}$)",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#1C4532",
            bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec="#22543D", lw=1.2, alpha=0.9))
    ax.text(0.15, 1.3, "Semantic clarity established\nPhysical QoT satisfies target\nZero human interruptions",
            ha="center", va="center", fontsize=8, color="#22543D")

    # Zone II: Suggest Replan
    ax.text(0.15, -2.8, "ZONE II:\nSUGGEST REPLAN\n($a = \\text{replan}$)",
            ha="center", va="center", fontsize=9.5, fontweight="bold", color="#742A2A",
            bbox=dict(boxstyle="round,pad=0.4", fc="#FFFFFF", ec="#742A2A", lw=1.2, alpha=0.9))
    ax.text(0.15, -4.6, "Semantic intent understood\nTransmission infeasible\nHITL constraint relaxation",
            ha="center", va="center", fontsize=8, color="#742A2A")

    # Zone III: Early Clarify
    ax.text(0.65, 0.2, "ZONE III:\nEARLY HITL CLARIFY\n($a = \\text{clarify}$)",
            ha="center", va="center", fontsize=10.5, fontweight="bold", color="#7B341E",
            bbox=dict(boxstyle="round,pad=0.45", fc="#FFFFFF", ec="#7B341E", lw=1.3, alpha=0.95))
    ax.text(0.65, -1.8, "Grammar violation ($v_{struct} = 0$)\nor semantic divergence ($d_{sem} > \\tau_{sem}$)\nPhysical simulation strictly bypassed",
            ha="center", va="center", fontsize=8.5, color="#7B341E")

    # Grid & Spines
    ax.grid(True, linestyle=":", alpha=0.5, color="#718096")
    for spine in ax.spines.values():
        spine.set_color("#2D3748")
        spine.set_linewidth(1.1)

    # Legend
    ax.legend(loc="upper right", framealpha=0.95, fontsize=8.5, edgecolor="#CBD5E0")

    figs_dir = Path(__file__).resolve().parent.parent.parent
    out_pdf = figs_dir / "pdf" / "radg_decision_space.pdf"
    out_png = figs_dir / "png" / "radg_decision_space.png"
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_pdf, bbox_inches="tight", format="pdf")
    plt.savefig(out_png, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated {out_pdf} and {out_png}")

if __name__ == "__main__":
    generate_figure_3_4()
