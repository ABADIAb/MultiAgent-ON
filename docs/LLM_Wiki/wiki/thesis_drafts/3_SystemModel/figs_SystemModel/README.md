---
title: "Chapter 3: Figure Catalog & Diagram Guide"
date: 2026-09-06
tags: [thesis, chapter-3, figures, diagrams, drawio, system-model, overleaf]
status: active
---

# Chapter 3: Figure Catalog & Diagram Guide

This directory contains the visual artifacts for **Chapter 3: System Model and Neurosymbolic Architecture**, strictly structured according to the guidelines defined in [`thesis-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/thesis-coauthor/SKILL.md) and [`figure-guidelines.md`](file:///home/felipeab/MultiAgentON/.agents/skills/thesis-coauthor/references/figure-guidelines.md).

---

## 1. Directory Organization & Semantic Naming

To ensure clean separation between editable source models and compiled publication deliverables, files are organized into distinct subdirectories:

```text
figs_SystemModel/
├── src/
│   ├── diagrams/       # Pathway A: Native Draw.io XML (.drawio) source models
│   └── plots/          # Pathway B: Python Matplotlib generator scripts (.py)
├── pdf/                # Vector graphics for Overleaf / LaTeX (\includegraphics)
├── png/                # 300 DPI high-resolution raster previews for visual QA
└── README.md           # Catalog & LaTeX snippets
```

**Semantic Naming Policy:** All filenames use descriptive names without hardcoded figure numbers (e.g., `conceptual_framework.drawio` or `radg_decision_space.py`). Sequence numbering is dynamically resolved by LaTeX via `\label{fig:...}` and `Figure~\ref{fig:...}`.

---

## 2. Active Figure Catalog (Core 4)

To prevent cognitive overload and maintain a dense, purely mathematical focus on the system model, Chapter 3 concentrates on **4 core figures**:

| Semantic Label | Source File | Deliverable Files | Pathway | Section | Key Visual Concept |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fig:conceptual_framework` | `src/diagrams/conceptual_framework.drawio` | `pdf/conceptual_framework.pdf`<br>`png/conceptual_framework.png` | **Pathway A** (Draw.io) | **3.2.1** | 7-Phase Fail-Fast Pipeline with Gate 1 (Semantic Uncertainty $U_{sem}$) and Gate 2 (Physical Risk Gate $\text{QoT}_{valid}$), including HITL clarify & replan loops. |
| `fig:neural_symbolic_subsystems` | `src/diagrams/neural_symbolic_subsystems.drawio` | `pdf/neural_symbolic_subsystems.pdf`<br>`png/neural_symbolic_subsystems.png` | **Pathway A** (Draw.io) | **3.3.1** | Functional division: Neural Subsystem (linguistic reasoning) and Symbolic Subsystem (deterministic physics) bound by the typed PDDL predicates and CFG structural contract. |
| `fig:radg_decision_space` | `src/plots/radg_decision_space.py` | `pdf/radg_decision_space.pdf`<br>`png/radg_decision_space.png` | **Pathway B** (Python Plot) | **3.4.1** | 2D Operational State Space: $U_{sem} \in [0, 1]$ vs. $\Delta\text{GSNR}$ (dB) demarcating Zone I (Auto-Approve), Zone II (Suggest Replan), and Zone III (Early HITL Clarify). |
| `fig:reverse_prompting_loop` | `src/diagrams/reverse_prompting_loop.drawio` | `pdf/reverse_prompting_loop.pdf`<br>`png/reverse_prompting_loop.png` | **Pathway A** (Draw.io) | **3.5.2** | Closed-loop validation cycle: Forward translation $\mathcal{M}_{forward} \to \mathcal{S}_{PDDL} \to$ Reverse reconstruction $\mathcal{M}_{reverse} \to \mathcal{I}_{recon} \to$ Semantic divergence $d_{sem} \to$ LangGraph `interrupt()`. |

### Archived Figures (`figs_SystemModel/archive/`)
The following diagrams were archived to avoid redundancy and keep the chapter compact:
- `problem_formulation.drawio` (Black-box inputs/outputs, fully superseded by `conceptual_framework`).
- `neurosymbolic_comparison.drawio` (Comparative baseline analysis; prioritized for Chapter 1 or Chapter 2).
- `hitl_sequence.drawio` (Software-engineering UML sequence; logic is formally captured in `reverse_prompting_loop`).

---

## 3. Ready-to-Copy LaTeX Snippets for Overleaf

Copy the vector files from `figs_SystemModel/pdf/` directly to your Overleaf project under `Figures/figs_SystemModel/`:

```latex
% 1. Conceptual Framework
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.98\textwidth]{Figures/figs_SystemModel/conceptual_framework.pdf}
    \caption{The 7-Phase Fail-Fast Risk-Adaptive Neurosymbolic Orchestration Pipeline, illustrating sequential evaluation across Gate 1 (Semantic Uncertainty $U_{\text{sem}}$) and Gate 2 (Physical Transmission Viability $\text{QoT}_{\text{valid}}$).}
    \label{fig:conceptual_framework}
\end{figure}

% 2. Subsystem Architecture
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{Figures/figs_SystemModel/neural_symbolic_subsystems.pdf}
    \caption{Neurosymbolic subsystem division of responsibilities: decoupling linguistic formalization within the Neural Subsystem from deterministic constraint satisfaction and physical simulation in the Symbolic Subsystem via typed PDDL predicates.}
    \label{fig:neural_symbolic_subsystems}
\end{figure}

% 3. RADG Decision Space
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.82\textwidth]{Figures/figs_SystemModel/radg_decision_space.pdf}
    \caption{Two-dimensional operational state space of the Risk-Adaptive Decision Gate (RADG) mapped across Semantic Uncertainty ($U_{\text{sem}}$) and Physical Feasibility Margin ($\Delta\text{GSNR}$), demarcating Zone I (Auto-Approve), Zone II (Suggest Replan), and Zone III (Early HITL Clarify).}
    \label{fig:radg_decision_space}
\end{figure}

% 4. Reverse Prompting Loop
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.95\textwidth]{Figures/figs_SystemModel/reverse_prompting_loop.pdf}
    \caption{Closed-loop Reverse Prompting validation cycle enforcing semantic convergence through forward formal translation, reverse natural language reconstruction, and automated semantic divergence scoring prior to human intervention.}
    \label{fig:reverse_prompting_loop}
\end{figure}

```

---

## 4. Re-generation Commands

- **To re-export all Draw.io diagrams to PDF and PNG:**
  ```bash
  python3 scratch/export_drawio_batch.py
  ```
- **To re-generate the RADG scientific plot:**
  ```bash
  uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/src/plots/radg_decision_space.py
  ```
