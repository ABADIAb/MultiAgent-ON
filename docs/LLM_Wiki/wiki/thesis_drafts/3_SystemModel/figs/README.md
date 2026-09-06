---
title: "Chapter 3: Figure Guide & LaTeX Integration Placement"
date: 2026-09-05
tags: [thesis, chapter-3, figures, diagrams, system-model, overleaf]
status: active
---

# Chapter 3: Figure Catalog & Placement Guide

This directory contains the Python generator scripts, vector PDF files, and raster PNG previews for all figures of **Chapter 3: System Model and Neurosymbolic Architecture**.

Every figure is programmatically rendered using `matplotlib` with vector font embedding (`pdf.fonttype = 42`). When compiled into Overleaf, all text elements, mathematical notation, and labels remain crisp and fully selectable with the cursor.

---

## 1. Quick Execution
To re-generate all figures at once, run:

```bash
uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs/fig_3_1_problem_formulation.py
uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs/fig_3_2_conceptual_framework.py
uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs/fig_3_3_neurosymbolic_separation.py
uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs/fig_3_4_radg_decision_space.py
uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs/fig_3_5_hitl_sequence.py
```

---

## 2. Figure Catalog & Section Placement

| Figure | Script | Output PDF / PNG | Target Section in `chapter_3_system_model.txt` | Key Concept Visualized |
| :--- | :--- | :--- | :--- | :--- |
| **Figure 3.1** | `fig_3_1_problem_formulation.py` | `figure_3_1_problem_formulation.pdf` | End of Section **3.1.2** (after Global Objective) | Transformation from $(\mathcal{I}_{NL}, G, \mathbf{P}) \to \mathcal{S}_{PDDL} \to a \in \{\text{approve}, \text{clarify}, \text{replan}\}$. |
| **Figure 3.2** | `fig_3_2_conceptual_framework.py` / `export_fig_3_2_to_drawio.py` | `figure_3_2_conceptual_framework.pdf` / `.drawio` | End of Section **3.2.1** (Fail-Fast Paradigm) | Complete 7-Phase Swimlane showing Gate 1 ($U_{sem}$) and Gate 2 ($\text{QoT}_{valid}$) loops (editable Draw.io XML). |
| **Figure 3.3** | `fig_3_3_neurosymbolic_separation.py` | `figure_3_3_neurosymbolic_separation.pdf` | End of Section **3.3.1** ("LLMs Reason, Tools Calculate") | Side-by-side comparison: Baseline End-to-End LLM vs. Neurosymbolic Pipeline. |
| **Figure 3.4** | `fig_3_4_radg_decision_space.py` | `figure_3_4_radg_decision_space.pdf` | Directly after Section **3.4.1** (Decision Function) | 2D Operational Space ($U_{sem}$ vs $\Delta\text{GSNR}$ [dB]) showing the 3 Action Zones. |
| **Figure 3.5** | `fig_3_5_hitl_sequence.py` | `figure_3_5_hitl_sequence.pdf` | Section **3.5.2** (Reverse Prompting Invariant) | Sequence diagram: Operator $\leftrightarrow$ Orchestrator $\leftrightarrow$ LLM $\leftrightarrow$ Checkpointer. |

---

## 3. Ready-to-Copy LaTeX Snippets for Overleaf

### Figure 3.1
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{figure_3_1_problem_formulation.pdf}
    \caption{High-level architectural problem formulation: transforming unstructured operator intent and optical network state into a verified lightpath and risk-bounded pre-deployment control action.}
    \label{fig:problem_formulation}
\end{figure}
```

### Figure 3.2
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.98\textwidth]{figure_3_2_conceptual_framework.pdf}
    \caption{The 7-Phase Fail-Fast Risk-Adaptive Neurosymbolic Orchestration Pipeline, illustrating sequential evaluation across Gate 1 (Semantic Uncertainty $U_{\text{sem}}$) and Gate 2 (Physical Transmission Viability $\text{QoT}_{\text{valid}}$).}
    \label{fig:conceptual_framework}
\end{figure}
```

### Figure 3.3
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{figure_3_3_neurosymbolic_separation.pdf}
    \caption{Architectural comparison between a conventional black-box LLM baseline (prone to physical hallucination and high-latency deployment failure) and the proposed strict neurosymbolic separation framework.}
    \label{fig:neurosymbolic_separation}
\end{figure}
```

### Figure 3.4
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.82\textwidth]{figure_3_4_radg_decision_space.pdf}
    \caption{Two-dimensional operational state space of the Risk-Adaptive Decision Gate (RADG) mapped across Semantic Uncertainty ($U_{\text{sem}}$) and Physical Feasibility Margin ($\Delta\text{GSNR}$), demarcating Zone I (Auto-Approve), Zone II (Suggest Replan), and Zone III (Early HITL Clarify).}
    \label{fig:radg_decision_space}
\end{figure}
```

### Figure 3.5
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{figure_3_5_hitl_sequence.pdf}
    \caption{UML Sequence diagram illustrating the formal Human-in-the-Loop (HITL) Reverse Prompting lifecycle, showcasing atomic checkpoint state serialization via native LangGraph \texttt{interrupt()} and monotonic constraint recovery.}
    \label{fig:hitl_sequence}
\end{figure}
```
