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

## 2. Active Figure Catalog

Chapter 4 intentionally avoids duplicating the 7-phase execution workflow and two-gate decision structure already illustrated in Chapter 3 (`Figure~\ref{fig:conceptual_framework}`). The implementation narrative in Chapter 4 references `Figure~\ref{fig:conceptual_framework}` directly, focusing the text and code listings on concrete software realization, deterministic parsing algorithms, and state persistence mechanics.

---

## 3. Archived Diagrams (`archive/`)

The following candidate diagrams were authored, evaluated, and subsequently archived to avoid visual redundancy and maintain maximal manuscript clarity:

| Semantic Label | Archived Source | Deliverable Files | Archival Rationale |
| :--- | :--- | :--- | :--- |
| `fig:langgraph_execution_flow` | `archive/src/diagrams/langgraph_execution_flow.drawio` | `archive/pdf/langgraph_execution_flow.pdf`<br>`archive/png/langgraph_execution_flow.png` | Redundant with `Figure~\ref{fig:conceptual_framework}` (Chapter 3). The LangGraph state machine is a 1:1 software realization of the 7-phase conceptual pipeline; re-illustrating it added cognitive noise without new conceptual insight. |
| `fig:semantic_engine` | `archive/src/diagrams/semantic_engine.drawio` | `archive/pdf/semantic_engine.pdf`<br>`archive/png/semantic_engine.png` | Redundant with Phases 2 & 3 and Gate 1 of `Figure~\ref{fig:conceptual_framework}`. The two-layer verification mechanics ($v_{\text{struct}}$ and $d_{\text{sem}}$) and RADG gate are already anchored in the conceptual framework and detailed textually in Section 4.3. |

---

## 4. Re-generation Commands

Active visual artifacts in Chapter 4 currently rely on Chapter 3's `Figure~\ref{fig:conceptual_framework}`. Candidate diagrams and standalone builders are preserved in `archive/src/diagrams/` for historical auditability.

