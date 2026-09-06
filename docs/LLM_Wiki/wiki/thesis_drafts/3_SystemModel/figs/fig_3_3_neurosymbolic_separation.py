#!/usr/bin/env python3
"""
Generate Figure 3.3: Strict Neurosymbolic Separation Comparison Diagram.
Fixes escape sequence on ampersand for clean academic render.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def generate_figure_3_3():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 8.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(11.5, 6.2), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    def draw_box(x, y, w, h, title, subtitle="", fc="#FFFFFF", ec="#000000", lw=1.2, rad=0.06):
        box = FancyBboxPatch(
            (x, y), w, h,
            boxstyle=f"round,pad=0.02,rounding_size={rad}",
            facecolor=fc, edgecolor=ec, linewidth=lw
        )
        ax.add_patch(box)
        if subtitle:
            ax.text(x + w/2, y + h*0.62, title, ha="center", va="center", fontweight="bold", fontsize=8.5, color="#1A202C")
            ax.text(x + w/2, y + h*0.28, subtitle, ha="center", va="center", fontsize=7.2, color="#4A5568")
        else:
            ax.text(x + w/2, y + h/2, title, ha="center", va="center", fontweight="bold", fontsize=8.5, color="#1A202C")

    # Baseline Container (Left)
    panel_left = FancyBboxPatch((0.4, 0.3), 4.6, 5.5, boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor="#FFF5F5", edgecolor="#FEB2B2", linewidth=1.5)
    ax.add_patch(panel_left)
    ax.text(2.7, 5.5, "Conventional Baseline: End-to-End LLM", ha="center", va="center",
            fontweight="bold", fontsize=10, color="#9B2C2C")

    # Proposed Container (Right)
    panel_right = FancyBboxPatch((5.5, 0.3), 5.6, 5.5, boxstyle="round,pad=0.02,rounding_size=0.1",
                                 facecolor="#F0FFF4", edgecolor="#9AE6B4", linewidth=1.5)
    ax.add_patch(panel_right)
    ax.text(8.3, 5.5, "Proposed Architecture: Strict Neurosymbolic", ha="center", va="center",
            fontweight="bold", fontsize=10, color="#22543D")

    # LEFT: BASELINE
    arr_l = dict(arrowstyle="-|>", mutation_scale=12, lw=1.3, color="#C53030")
    draw_box(0.8, 4.4, 3.8, 0.7, "Operator Natural Language Intent", r"$\mathcal{I}_{NL}$: 'Hamburg to Leipzig, avoid Hannover'",
             fc="#FFFFFF", ec="#E53E3E")
    
    draw_box(0.8, 3.1, 3.8, 0.85, "Black-Box LLM / ReAct Agent", "Direct Prompting over Full JSON Topology\n(Prone to Context Saturation)",
             fc="#FED7D7", ec="#E53E3E", lw=1.5)
    
    draw_box(0.8, 1.8, 3.8, 0.8, "Hallucinated Candidate Route", "Syntactically plausible, but violates physical\nGSNR margins or links non-existent nodes",
             fc="#FFF5F5", ec="#E53E3E")
    
    draw_box(0.8, 0.6, 3.8, 0.7, "Reactive Post-Deployment Failure", "Controller rejection / Optical SNR degradation\nHigh recovery latency & disruption risk",
             fc="#FEB2B2", ec="#9B2C2C", lw=1.6)

    ax.annotate("", xy=(2.7, 3.95), xytext=(2.7, 4.4), arrowprops=arr_l)
    ax.annotate("", xy=(2.7, 2.6), xytext=(2.7, 3.1), arrowprops=arr_l)
    ax.annotate("", xy=(2.7, 1.3), xytext=(2.7, 1.8), arrowprops=arr_l)

    # RIGHT: PROPOSED
    arr_r = dict(arrowstyle="-|>", mutation_scale=11, lw=1.3, color="#276749")
    
    draw_box(5.8, 4.55, 5.0, 0.65, "Operator Natural Language Intent", r"$\mathcal{I}_{NL}$ + Optical RAG Subtopology $G_{sub}$",
             fc="#FFFFFF", ec="#2B6CB0")

    draw_box(5.8, 3.65, 5.0, 0.65, "Neural Subsystem (LLM Semantic Compiler)", r"Translates intent to standard PDDL predicates $\mathcal{S}_{PDDL}$",
             fc="#EBF8FF", ec="#3182CE", lw=1.4)

    draw_box(5.8, 2.75, 5.0, 0.65, "Context-Free Grammar (CFG) Audit", r"Deterministic AST Validation: $v_{struct} \in \{0, 1\}$",
             fc="#FAF5FF", ec="#805AD5", lw=1.4)

    draw_box(5.8, 1.85, 5.0, 0.65, "Symbolic Subsystem (Yen's K-Shortest Paths)", r"Pruned graph $\widetilde{G}_{sub}$ + Hard constraint filtering",
             fc="#EDFDFD", ec="#319795", lw=1.4)

    draw_box(5.8, 0.95, 5.0, 0.65, "Analytical Physics Engine (Gaussian Noise Model)", r"Deterministic GSNR & Received Power $P_{rx}$ calculation",
             fc="#E6FFFA", ec="#234E52", lw=1.4)

    draw_box(5.8, 0.45, 5.0, 0.40, "Verified Pre-Deployment Configuration", "Zero physical risk provisioning to ROADM nodes",
             fc="#C6F6D5", ec="#22543D", lw=1.4)

    ax.annotate("", xy=(8.3, 4.3), xytext=(8.3, 4.55), arrowprops=arr_r)
    ax.annotate("", xy=(8.3, 3.4), xytext=(8.3, 3.65), arrowprops=arr_r)
    ax.annotate("", xy=(8.3, 2.5), xytext=(8.3, 2.75), arrowprops=arr_r)
    ax.annotate("", xy=(8.3, 1.6), xytext=(8.3, 1.85), arrowprops=arr_r)
    ax.annotate("", xy=(8.3, 0.85), xytext=(8.3, 0.95), arrowprops=arr_r)

    out_dir = Path(__file__).resolve().parent
    out_pdf = out_dir / "figure_3_3_neurosymbolic_separation.pdf"
    out_png = out_dir / "figure_3_3_neurosymbolic_separation.png"
    plt.savefig(out_pdf, bbox_inches="tight", format="pdf")
    plt.savefig(out_png, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated {out_pdf} and {out_png}")

if __name__ == "__main__":
    generate_figure_3_3()
