#!/usr/bin/env python3
"""
Generate Figure 3.1: High-Level Problem Formulation Block Diagram.
Refined layout to ensure zero label overlapping and generous whitespace.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def generate_figure_3_1():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 10,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(11.5, 4.8), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 4.8)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle="", fc="#FFFFFF", ec="#000000", lw=1.5, rad=0.08):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.02,rounding_size={rad}",
            facecolor=fc, edgecolor=ec, linewidth=lw
        )
        ax.add_patch(box)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, ha="center", va="center", fontweight="bold", fontsize=9.5, color="#1A202C")
            ax.text(x + w/2, y + h*0.30, subtitle, ha="center", va="center", fontsize=8, color="#4A5568")
        else:
            ax.text(x + w/2, y + h/2, title, ha="center", va="center", fontweight="bold", fontsize=9.5, color="#1A202C")

    # Inputs Block (Left)
    draw_box(0.5, 2.7, 2.5, 1.5, "Operator Intent", r"$\mathcal{I}_{NL} = (s, d, \mathcal{C}_{req})$", "#EBF3FB", "#2B6CB0")
    draw_box(0.5, 0.7, 2.5, 1.5, "Network State", r"$G(V,E), \; \mathbf{P}, \; \text{GSNR}_{th}$", "#EBF3FB", "#2B6CB0")

    # Outer Engine Box
    outer = FancyBboxPatch((3.7, 0.5), 3.9, 3.9, boxstyle="round,pad=0.02,rounding_size=0.12",
                           facecolor="#F0FFF4", edgecolor="#276749", linewidth=1.8)
    ax.add_patch(outer)
    ax.text(5.65, 4.15, "Pre-Deployment Planning Engine", ha="center", va="center",
            fontweight="bold", fontsize=11, color="#22543D")

    # Inner Steps
    draw_box(4.0, 2.9, 3.3, 0.85, r"Symbolic Spec: $\mathcal{S}_{PDDL}$", "PDDL Goal Predicates & AST Audit", "#FFFFFF", "#319795", lw=1.2)
    draw_box(4.0, 1.8, 3.3, 0.85, r"Path Generation: $\pi^* \in \mathcal{K}_{path}$", "Pruned Graph Yen's K-Shortest Paths", "#FFFFFF", "#319795", lw=1.2)
    draw_box(4.0, 0.7, 3.3, 0.85, r"Objective Optimization", r"$\min \mathcal{J} = \alpha N_{hitl} + \beta T_{tokens}$", "#FFFFFF", "#319795", lw=1.2)

    # Action Blocks (Right)
    draw_box(8.7, 3.4, 2.3, 0.9, "Approve Action", r"$a = \text{approve}$ (Provision)", "#C6F6D5", "#22543D")
    draw_box(8.7, 2.05, 2.3, 0.9, "Clarify Action", r"$a = \text{clarify}$ (Semantic HITL)", "#FEEBC8", "#7B341E")
    draw_box(8.7, 0.7, 2.3, 0.9, "Replan Action", r"$a = \text{replan}$ (Physics HITL)", "#FED7D7", "#742A2A")

    # Input Arrows
    arrow_in = dict(arrowstyle="-|>", mutation_scale=14, lw=1.5, color="#2D3748")
    ax.annotate("", xy=(3.7, 3.45), xytext=(3.0, 3.45), arrowprops=arrow_in)
    ax.annotate("", xy=(3.7, 1.45), xytext=(3.0, 1.45), arrowprops=arrow_in)

    # Output Arrows with explicit offsets and labels
    ax.annotate("", xy=(8.7, 3.85), xytext=(7.6, 3.0),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=13, lw=1.4, color="#22543D"))
    ax.text(8.15, 3.65, r"$D = \text{approve}$", ha="center", va="center", fontsize=8, color="#22543D", fontweight="bold")

    ax.annotate("", xy=(8.7, 2.5), xytext=(7.6, 2.5),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=13, lw=1.4, color="#7B341E"))
    ax.text(8.15, 2.7, r"$U_{sem} > \tau_{sem}$", ha="center", va="center", fontsize=8, color="#7B341E", fontweight="bold")

    ax.annotate("", xy=(8.7, 1.15), xytext=(7.6, 2.0),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=13, lw=1.4, color="#742A2A"))
    ax.text(8.15, 1.35, r"$\text{QoT} = 0$", ha="center", va="center", fontsize=8, color="#742A2A", fontweight="bold")

    out_dir = Path(__file__).resolve().parent
    out_pdf = out_dir / "figure_3_1_problem_formulation.pdf"
    out_png = out_dir / "figure_3_1_problem_formulation.png"
    plt.savefig(out_pdf, bbox_inches="tight", format="pdf")
    plt.savefig(out_png, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated {out_pdf} and {out_png}")

if __name__ == "__main__":
    generate_figure_3_1()
