---
title: "Chapter 4: Figure Catalog & Diagram Guide"
date: 2026-09-23
tags: [thesis, chapter-4, figures, diagrams, drawio, implementation, overleaf]
status: active
---

# Chapter 4: Figure Catalog & Diagram Guide

This directory contains the visual artifacts for **Chapter 4: Neurosymbolic Pipeline Implementation**, strictly structured according to the guidelines defined in [`thesis-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/thesis-coauthor/SKILL.md) and [`figure-guidelines.md`](file:///home/felipeab/MultiAgentON/.agents/skills/thesis-coauthor/references/figure-guidelines.md).

---

## 1. Directory Organization & Semantic Naming

To ensure clean separation between editable source models and compiled publication deliverables, files are organized into distinct subdirectories:

```text
figs_NPImp/
├── src/
│   ├── diagrams/       # Pathway A: Native Draw.io XML (.drawio) source models + generator scripts
│   └── plots/          # Pathway B: Python generator scripts (.py)
├── pdf/                # Vector graphics for Overleaf / LaTeX (\includegraphics)
├── png/                # 300 DPI high-resolution raster previews for visual QA
├── archive/            # Retired or deferred diagram sources and exports
└── README.md           # Catalog & LaTeX snippets
```

**Semantic Naming Policy:** All filenames use descriptive names without hardcoded figure numbers (e.g., `langgraph_execution_flow.drawio` and `semantic_engine.drawio`). Sequence numbering is dynamically resolved by LaTeX via `\label{fig:...}` and `Figure~\ref{fig:...}`.

---

## 2. Active Figure Catalog (Core 2)

Chapter 4 concentrates on **2 core architectural diagrams** illustrating the software state machine and the two-layer semantic validation engine:

| Semantic Label | Source File | Deliverable Files | Pathway | Section | Key Visual Concept |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fig:langgraph_execution_flow` | `src/diagrams/langgraph_execution_flow.drawio` | `pdf/langgraph_execution_flow.pdf`<br>`png/langgraph_execution_flow.png` | **Pathway A** (Draw.io) | **4.1.1** | LangGraph State Machine topology across 7 phases, showing thread state persistence, two asynchronous `interrupt()` boundaries (Phase 3b clarify and Phase 6 replan), fast-track manual override bypass, and feedback loops. |
| `fig:semantic_engine` | `src/diagrams/semantic_engine.drawio` | `pdf/semantic_engine.pdf`<br>`png/semantic_engine.png` | **Pathway A** (Draw.io) | **4.3** | Two-Layer Semantic Engine architecture: Intent Ingestion & Multi-Turn Reconciliation, Layer 1 AST CFG structural validation ($v_{\text{struct}}$), Layer 2 closed-loop Reverse Prompting ($I_{\text{recon}}$) with LLM Judge ($d_{\text{sem}}$), converging at the Semantic RADG decision multiplexer ($U_{\text{sem}}$). |

---

## 3. Ready-to-Copy LaTeX Snippets for Overleaf

Copy the vector files from `figs_NPImp/pdf/` directly to your Overleaf project under `Figures/figs_NPImp/`:

```latex
% 1. LangGraph State Machine Execution Flow (Section 4.1)
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.88\textwidth]{Figures/figs_NPImp/langgraph_execution_flow.pdf}
    \caption{\small\itshape LangGraph state machine execution graph and conditional routing flow across the seven neurosymbolic pipeline phases, showing thread checkpointer state persistence, asynchronous interruption boundaries (\texttt{interrupt()}), fast-track manual override, and iterative feedback trajectories.}
    \label{fig:langgraph_execution_flow}
\end{figure}
\FloatBarrier

% 2. Two-Layer Semantic Engine Architecture (Section 4.3)
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.88\textwidth]{Figures/figs_NPImp/semantic_engine.pdf}
    \caption{\small\itshape Two-layer Semantic Engine architecture illustrating intent ingestion, multi-turn reconciliation, Layer 1 Abstract Syntax Tree (AST) structural syntax verification ($v_{\text{struct}}$), Layer 2 automated closed-loop Reverse Prompting ($I_{\text{recon}}$) with LLM-as-a-judge semantic divergence scoring ($d_{\text{sem}}$), and Semantic RADG decision multiplexing ($U_{\text{sem}}$).}
    \label{fig:semantic_engine}
\end{figure}
\FloatBarrier
```

---

## 4. Re-generation Commands

- **To re-export all Draw.io diagrams to PDF and PNG:**
  ```bash
  python3 docs/LLM_Wiki/wiki/thesis_drafts/4_NPImp/figs_NPImp/src/diagrams/export_diagrams.py
  ```
  *(Or execute directly from `src/diagrams/`: `python3 export_diagrams.py`)*
- **To rebuild the diagram XML sources from Python generators:**
  ```bash
  uv run python docs/LLM_Wiki/wiki/thesis_drafts/4_NPImp/figs_NPImp/src/diagrams/build_langgraph_flow.py
  uv run python docs/LLM_Wiki/wiki/thesis_drafts/4_NPImp/figs_NPImp/src/diagrams/build_semantic_engine.py
  ```
