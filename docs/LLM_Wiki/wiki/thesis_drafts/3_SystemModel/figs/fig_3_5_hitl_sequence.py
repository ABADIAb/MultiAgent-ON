#!/usr/bin/env python3
"""
Generate Figure 3.5: Sequence Diagram of Formal HITL Reverse Prompting Lifecycle.
Refined spacing for operator review box and feedback annotations.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def generate_figure_3_5():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 8.5,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(11.5, 7.5), dpi=300)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    actors = [
        ("Operator", 1.5, "#EBF8FF", "#3182CE"),
        ("Orchestrator Graph", 4.3, "#EDFDFD", "#319795"),
        ("LLM Engine", 7.1, "#FAF5FF", "#805AD5"),
        ("State Checkpointer", 9.9, "#FEFCBF", "#D69E2E"),
    ]

    y_top = 6.8
    y_bottom = 0.4

    for name, x, fc, ec in actors:
        box = FancyBboxPatch((x - 1.1, y_top), 2.2, 0.5, boxstyle="round,pad=0.02,rounding_size=0.05",
                             facecolor=fc, edgecolor=ec, linewidth=1.3)
        ax.add_patch(box)
        ax.text(x, y_top + 0.25, name, ha="center", va="center", fontweight="bold", fontsize=9.2, color="#1A202C")
        ax.plot([x, x], [y_top, y_bottom], linestyle="--", color="#CBD5E0", linewidth=1.1, zorder=1)

    def draw_msg(x1, x2, y, text, is_dotted=False, color="#2D3748"):
        ls = ":" if is_dotted else "-"
        arr = dict(arrowstyle="-|>", mutation_scale=10, lw=1.2, color=color, linestyle=ls)
        ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=arr)
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y + 0.09, text, ha="center", va="bottom", fontsize=7.8, color=color, fontweight="bold")

    def draw_note(x, y, w, h, text, fc="#FFF5F5", ec="#E53E3E"):
        box = FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
                             facecolor=fc, edgecolor=ec, linewidth=1.0)
        ax.add_patch(box)
        ax.text(x, y, text, ha="center", va="center", fontsize=7.2, color="#742A2A")

    # 1. Operator sends intent
    draw_msg(1.5, 4.3, 6.3, r"1. Submit Intent $\mathcal{I}_{NL}$ ('Hamburg to Leipzig...')", color="#2B6CB0")

    # 2. Graph queries LLM for PDDL
    draw_msg(4.3, 7.1, 5.75, r"2. Forward Translation Prompt $(\mathcal{I}_{NL}, G_{sub})$")

    # 3. LLM returns PDDL
    draw_msg(7.1, 4.3, 5.25, r"3. Returns $\mathcal{S}_{PDDL}$ (AST Validated $v_{struct}=1$)", is_dotted=True)

    # 4. Graph asks LLM for Reverse Reconstruction
    draw_msg(4.3, 7.1, 4.75, r"4. Reverse Reconstruction $(\mathcal{S}_{PDDL})$")

    # 5. LLM returns reconstructed intent
    draw_msg(7.1, 4.3, 4.25, r"5. Returns $\mathcal{I}_{recon}$ + Evaluates Divergence $d_{sem}$", is_dotted=True)

    # Note: Semantic gate detects ambiguity
    draw_note(4.3, 3.75, 3.6, 0.45, r"Semantic Gate: $d_{sem} = 0.42 > \tau_{sem} (0.30)$" + "\nTrigger LangGraph interrupt()",
              fc="#FEEBC8", ec="#DD6B20")

    # 6. Graph serializes state to Checkpointer
    draw_msg(4.3, 9.9, 3.2, r"6. Atomic Checkpoint: Serialize $\mathcal{S}_{state}$ (Thread ID)", color="#B7791F")

    # 7. Orchestrator prompts operator for clarify
    draw_msg(4.3, 1.5, 2.65, r"7. Present $\mathcal{I}_{recon}$ & Request Clarification", color="#C05621")

    # Note: Execution suspended placed in operator territory without collision
    draw_note(1.5, 2.05, 2.7, 0.45, "Execution Paused (0 tokens)\nOperator reviews reconstruction",
              fc="#EDF2F7", ec="#718096")

    # 8. Operator submits refined feedback
    draw_msg(1.5, 4.3, 1.45, r"8. Inject Feedback $\mathcal{F}$ ('Relax hops to 4...')", color="#276749")

    # 9. Graph resumes from Checkpointer
    draw_msg(4.3, 9.9, 1.0, r"9. Resume Graph & Reload State $(\mathcal{S}_{state}, \mathcal{F})$", color="#276749")

    # 10. Graph loops back to LLM for regeneration
    draw_msg(4.3, 7.1, 0.55, r"10. Monotonic Update $\mathcal{C}_{k+1}$ & Reparse PDDL", color="#276749")

    out_dir = Path(__file__).resolve().parent
    out_pdf = out_dir / "figure_3_5_hitl_sequence.pdf"
    out_png = out_dir / "figure_3_5_hitl_sequence.png"
    plt.savefig(out_pdf, bbox_inches="tight", format="pdf")
    plt.savefig(out_png, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated {out_pdf} and {out_png}")

if __name__ == "__main__":
    generate_figure_3_5()
