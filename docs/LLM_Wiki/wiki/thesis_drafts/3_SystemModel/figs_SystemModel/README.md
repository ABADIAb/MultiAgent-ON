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

## 2. Active Figure Catalog (Core 2)

To maintain a dense, purely mathematical focus on the system model and avoid textual redundancy, Chapter 3 concentrates on **2 core figures**:

| Semantic Label | Source File | Deliverable Files | Pathway | Section | Key Visual Concept |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fig:conceptual_framework` | `src/diagrams/conceptual_framework.drawio` | `pdf/conceptual_framework.pdf`<br>`png/conceptual_framework.png` | **Pathway A** (Draw.io) | **3.2.1** | 7-Phase Fail-Fast Pipeline with Gate 1 (Semantic Uncertainty $U_{sem}$) and Gate 2 (Physical Risk Gate $\text{QoT}_{valid}$), including HITL clarify & replan loops. |
| `fig:radg_decision_space` | `src/plots/radg_decision_space.py` | `pdf/radg_decision_space.pdf`<br>`png/radg_decision_space.png` | **Pathway B** (Python Plot) | **3.4.1** | 2D Operational State Space: $U_{sem} \in [0, 1]$ vs. $\Delta\text{GSNR}$ (dB) demarcating Zone I (Auto-Approve), Zone II (Suggest Replan), and Zone III (Early HITL Clarify). |

### Archived & Deferred Figures (`figs_SystemModel/archive/`)
The following diagrams were moved to archive or deferred to avoid redundancy:
- `neural_symbolic_subsystems.drawio` (Archived; subsystem separation is mathematically detailed in Section 3.3).
- `reverse_prompting_loop.drawio` (Deferred to Chapter 4, Section 4.3; implementation details of the two-layer semantic engine).
- `problem_formulation.drawio` (Black-box inputs/outputs, fully superseded by `conceptual_framework`).
- `neurosymbolic_comparison.drawio` (Comparative baseline analysis; prioritized for Chapter 1 or Chapter 2).
- `hitl_sequence.drawio` (Software-engineering UML sequence; software lifecycle is captured in Chapter 4).

---

## 3. Ready-to-Copy LaTeX Snippets for Overleaf

Copy the vector files from `figs_SystemModel/pdf/` directly to your Overleaf project under `Figures/figs_SystemModel/`:

```latex
% 1. Conceptual Framework
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.75\textwidth]{Figures/figs_SystemModel/conceptual_framework.pdf}
    \caption{\small\itshape The 7-Phase Fail-Fast Risk-Adaptive Neurosymbolic Orchestration Pipeline, illustrating sequential evaluation across Gate 1 (Semantic Uncertainty $U_{\text{sem}}$) and Gate 2 (Physical Transmission Viability $\text{QoT}_{\text{valid}}$).}
    \label{fig:conceptual_framework}
\end{figure}

% 2. RADG Decision Space
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.82\textwidth]{Figures/figs_SystemModel/radg_decision_space.pdf}
    \caption{\small\itshape Two-dimensional operational state space of the Risk-Adaptive Decision Gate (RADG) mapped across Semantic Uncertainty ($U_{\text{sem}}$) and Physical Feasibility Margin ($\Delta\text{GSNR}$), demarcating Zone I (Auto-Approve), Zone II (Suggest Replan), and Zone III (Early HITL Clarify).}
    \label{fig:radg_decision_space}
\end{figure}
```

---

## 4. Re-generation Commands

- **To re-export all Draw.io diagrams to PDF and PNG:**
  ```bash
  python3 docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/src/diagrams/export_diagrams.py
  ```
  *(Or execute directly from `src/diagrams/`: `python3 export_diagrams.py`)*
- **To re-generate the RADG scientific plot:**
  ```bash
  uv run python docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/src/plots/radg_decision_space.py
  ```
