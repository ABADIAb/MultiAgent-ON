#!/usr/bin/env python3
"""
Generate Figure 3.2: Conceptual Framework & 7-Phase Fail-Fast Orchestration Pipeline.
Refactored applying the 'thesis-coauthor' visual anti-collision protocol:
1. Opaque text badges (bbox) on all decision branches so no line crosses any letter.
2. Clean curved corridors for feedback loops without touching text or boxes.
3. Fully isolated, readable side panel with distinct properties.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

def generate_figure_3_2():
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 9,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })

    fig, ax = plt.subplots(figsize=(13.2, 9.8), dpi=300)
    ax.set_xlim(0, 13.2)
    ax.set_ylim(0, 9.8)
    ax.axis("off")

    def draw_phase(x, y, w, h, p_num, title, detail="", fc="#F7FAFC", ec="#4A5568", lw=1.3):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                             facecolor=fc, edgecolor=ec, linewidth=lw)
        ax.add_patch(box)
        ax.text(x + w/2, y + h*0.65, f"{p_num}: {title}", ha="center", va="center",
                fontweight="bold", fontsize=9.2, color="#1A202C")
        if detail:
            ax.text(x + w/2, y + h*0.28, detail, ha="center", va="center",
                    fontsize=7.8, color="#4A5568")

    def draw_gate(cx, cy, r_w, r_h, title, detail="", fc="#FEFCBF", ec="#B7791F"):
        diamond = Polygon([
            [cx, cy + r_h],
            [cx + r_w, cy],
            [cx, cy - r_h],
            [cx - r_w, cy]
        ], closed=True, facecolor=fc, edgecolor=ec, linewidth=1.5)
        ax.add_patch(diamond)
        ax.text(cx, cy + 0.12, title, ha="center", va="center", fontweight="bold", fontsize=8.8, color="#744210")
        ax.text(cx, cy - 0.18, detail, ha="center", va="center", fontsize=7.5, color="#744210")

    # Layout coordinates
    cw = 4.4
    cx = 3.8
    center_x = cx + cw / 2  # 6.0

    # Phase 1: Intent Ingest & Optical RAG
    draw_phase(cx, 8.6, cw, 0.75, "Phase 1", "Intent Ingestion & Optical RAG",
               r"Raw intent $\mathcal{I}_{NL}$ + k-hop subtopology $G_{sub}$ extraction",
               fc="#EBF8FF", ec="#3182CE")

    # Phase 2: CFG-Validated PDDL Parsing
    draw_phase(cx, 7.45, cw, 0.75, "Phase 2", "CFG-Validated PDDL Parsing",
               r"LLM Semantic Compiler $\to \mathcal{S}_{PDDL}$ + AST Audit ($v_{struct}$)",
               fc="#EBF8FF", ec="#3182CE")

    # Phase 3a: Reverse Prompting
    draw_phase(cx, 6.3, cw, 0.75, "Phase 3a", "Automated Reverse Prompting",
               r"Autonomous PDDL $\to \mathcal{I}_{recon}$ (0 interrupts, LLM reconstruction)",
               fc="#FAF5FF", ec="#805AD5")

    # Gate 1: Semantic Gate
    draw_gate(center_x, 5.25, 2.1, 0.5, "GATE 1: Semantic Gate", r"$U_{sem} = f(v_{struct}, d_{sem}) \leq \tau_{sem}$ ?")

    # Phase 3b: HITL Clarify (Left branch)
    draw_phase(0.6, 4.8, 2.4, 0.9, "Phase 3b", "HITL Clarify",
               "LangGraph interrupt()\nOperator resolves ambiguity",
               fc="#FEEBC8", ec="#DD6B20", lw=1.5)

    # Phase 4: Deterministic Symbolic Solver
    draw_phase(cx, 3.85, cw, 0.75, "Phase 4", "Deterministic Symbolic Solver",
               r"Pruned topology $\widetilde{G}_{sub}$ + Yen's K-Shortest Paths ($K=5$)",
               fc="#EDFDFD", ec="#319795")

    # Phase 5: Deterministic QoT Validation
    draw_phase(cx, 2.7, cw, 0.75, "Phase 5", "Deterministic QoT Validation",
               r"Analytical Coherent GN Model: GSNR & $P_{rx}$ calculation",
               fc="#EDFDFD", ec="#319795")

    # Gate 2: Physical Risk Gate (RADG)
    draw_gate(center_x, 1.6, 2.1, 0.5, "GATE 2: Physical Risk Gate", r"$\text{QoT}_{valid}(\pi) = 1$ ? ($\mathrm{GSNR} \geq \mathrm{GSNR}_{th}$)")

    # Phase 6: Suggest Replan (Left branch)
    draw_phase(0.6, 1.15, 2.4, 0.9, "Phase 6", "Suggest Replan (RADG)",
               "LangGraph interrupt()\nRelax constraints / modulation",
               fc="#FED7D7", ec="#E53E3E", lw=1.5)

    # Phase 7: Synthesis & Provisioning
    draw_phase(cx, 0.25, cw, 0.75, "Phase 7", "Plan Synthesis & Provisioning",
               "Auditable Planning Report + RESTCONF / NETCONF Dispatch",
               fc="#F0FFF4", ec="#38A169")

    # Spine Arrows
    arr = dict(arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#2D3748")
    ax.annotate("", xy=(center_x, 8.2), xytext=(center_x, 8.6), arrowprops=arr)
    ax.annotate("", xy=(center_x, 7.05), xytext=(center_x, 7.45), arrowprops=arr)
    ax.annotate("", xy=(center_x, 5.75), xytext=(center_x, 6.3), arrowprops=arr)

    # Gate 1 Pass: Down to Phase 4
    ax.annotate("", xy=(center_x, 4.6), xytext=(center_x, 4.75), arrowprops=arr)
    ax.text(center_x, 4.72, " Yes (Auto-Pass) ", ha="center", va="center",
            fontsize=7.8, color="#276749", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#276749", lw=0.8, alpha=0.95))

    # Gate 1 Fail: Left to Phase 3b
    ax.annotate("", xy=(3.0, 5.25), xytext=(3.9, 5.25),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#C05621"))
    ax.text(3.45, 5.25, r" No ($U_{sem} > \tau_{sem}$) ", ha="center", va="center",
            fontsize=7.5, color="#C05621", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#C05621", lw=0.8, alpha=0.95))

    # Phase 3b loop back to Phase 2
    ax.annotate("", xy=(3.8, 7.82), xytext=(1.8, 5.7),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#C05621",
                               connectionstyle="arc3,rad=0.32"))
    ax.text(1.3, 7.0, " Operator Clarification Loop ", ha="center", va="center",
            fontsize=7.8, color="#C05621", rotation=50,
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#C05621", lw=0.8, alpha=0.95))

    # Phase 4 to Phase 5
    ax.annotate("", xy=(center_x, 3.45), xytext=(center_x, 3.85), arrowprops=arr)
    # Phase 5 to Gate 2
    ax.annotate("", xy=(center_x, 2.1), xytext=(center_x, 2.7), arrowprops=arr)

    # Gate 2 Pass: Down to Phase 7
    ax.annotate("", xy=(center_x, 1.0), xytext=(center_x, 1.1), arrowprops=arr)
    ax.text(center_x, 1.08, " Yes (Auto-Approve) ", ha="center", va="center",
            fontsize=7.8, color="#276749", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#276749", lw=0.8, alpha=0.95))

    # Gate 2 Fail: Left to Phase 6
    ax.annotate("", xy=(3.0, 1.6), xytext=(3.9, 1.6),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#C53030"))
    ax.text(3.45, 1.6, " No (QoT Invalid) ", ha="center", va="center",
            fontsize=7.5, color="#C53030", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#C53030", lw=0.8, alpha=0.95))

    # Phase 6 loop back to Phase 2
    ax.annotate("", xy=(3.8, 7.6), xytext=(0.8, 2.05),
                arrowprops=dict(arrowstyle="-|>", mutation_scale=12, lw=1.4, color="#C53030",
                               connectionstyle="arc3,rad=0.48"))
    ax.text(0.2, 5.1, " Replan & Constraint Relaxation Loop ", ha="center", va="center",
            fontsize=7.8, color="#C53030", rotation=77,
            bbox=dict(boxstyle="round,pad=0.2", fc="#FFFFFF", ec="#C53030", lw=0.8, alpha=0.95))

    # Right-side panel: Fail-Fast Properties
    panel = FancyBboxPatch((8.8, 1.5), 3.9, 7.0, boxstyle="round,pad=0.03,rounding_size=0.08",
                           facecolor="#F7FAFC", edgecolor="#CBD5E0", linewidth=1.2)
    ax.add_patch(panel)
    ax.text(10.75, 8.1, "Fail-Fast Properties", ha="center", va="center",
            fontweight="bold", fontsize=10.5, color="#2D3748")

    props = [
        ("Orthogonal Gating:", "Decouples linguistic ambiguity (Gate 1)\nfrom physical propagation feasibility (Gate 2)."),
        ("Zero-Overhead Autonomy:", "When U_sem <= 0.30 and QoT passes,\nexecution completes with 0 human pauses."),
        ("Deterministic Physics:", "GN model physics calculations never\nrun on hallucinatory paths."),
        ("Protected Control Plane:", "No unverified commands ever reach\nthe SDON controller or ROADM hardware."),
        ("LangGraph Checkpointing:", "Human-in-the-Loop interrupts use\natomic state serialization.")
    ]
    y_p = 7.4
    for title, desc in props:
        ax.text(9.05, y_p, title, fontweight="bold", fontsize=8.2, color="#2B6CB0")
        y_p -= 0.30
        ax.text(9.05, y_p, desc, fontsize=7.5, color="#4A5568")
        y_p -= 0.74

    out_dir = Path(__file__).resolve().parent
    out_pdf = out_dir / "figure_3_2_conceptual_framework.pdf"
    out_png = out_dir / "figure_3_2_conceptual_framework.png"
    plt.savefig(out_pdf, bbox_inches="tight", format="pdf")
    plt.savefig(out_png, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"Generated {out_pdf} and {out_png}")

if __name__ == "__main__":
    generate_figure_3_2()
