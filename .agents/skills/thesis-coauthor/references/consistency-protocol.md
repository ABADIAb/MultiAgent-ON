# Cross-Consistency and Codebase Grounding Protocol

## 1. Grounding Hierarchy (Source of Truth)

To ensure that the thesis manuscript reflects physical and software reality without hallucinating theoretical properties, maintain the following hierarchy:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Active Codebase (src/core/, src/nodes/, tests/)       │  <- Concrete Ground Truth
├─────────────────────────────────────────────────────────┤
│ 2. System Architecture (Architecture_v5, ProblemStmt)   │  <- Formal Design Invariants
├─────────────────────────────────────────────────────────┤
│ 3. Feature Specs (docs/.../features/*.md)              │  <- Component Contracts
├─────────────────────────────────────────────────────────┤
│ 4. Thesis Chapter Drafts (docs/.../thesis_drafts/)      │  <- Academic Formalization
└─────────────────────────────────────────────────────────┘
```

---

## 2. Inconsistency Resolution Rules

When cross-checking written drafts against the codebase and architecture:

1. **Inconsistency in Draft:**
   - *Action:* Explain the discrepancy technically with source references (file + line numbers) and fix the draft to match codebase reality.
2. **Inconsistency or Improvement Opportunity in Code / Architecture:**
   - *Action:* **STOP.** Explain the technical reason, architectural trade-offs, and proposed solution. **Ask the user before modifying any source code or architecture specifications.**
3. **Intentional Academic Abstraction (Assumptions):**
   - If the code implements a simplification of the general theory (e.g., homogeneous fiber SMF-28 parameters across links, zero equalization loss at ROADM nodes), formally state it as an explicit **Assumption** or **Remark** in the thesis draft.

---

## 3. The Ripple-Effect Audit Protocol

A modification to one section rarely exists in isolation. Whenever a notation, predicate, decision boundary, or parameter is modified:

### Checklist:
1. **Upstream / Downstream Section Check:**
   - Did changing Section $X.Y$ alter definitions used in Section $X.Z$?
   - *Example:* Standardizing Layer 2 semantic divergence $d_{sem} = \text{Score}_{divergence}$ in Section 3.5 requires checking Section 3.4 (RADG) and Section 3.2 (Conceptual Framework).
2. **Visual & Figure Alignment:**
   - Do the labels, state options, or mathematical thresholds in `figs/fig_*.py` match the updated text?
   - *Example:* Changing interrupt options in Phase 3b to `["clarify", "refine", "cancel"]` requires checking `fig_3_5_hitl_sequence.py` and `fig_3_2_conceptual_framework.py`.
3. **Drafting Backlog Logging:**
   - If a decision impacts a chapter not yet written (e.g., Chapter 4 implementation of RESTConf or Chapter 5 baseline benchmarks), immediately log a structured entry in:
     `docs/LLM_Wiki/wiki/thesis_drafts/Drafting_Backlog.md`.
4. **Merged LaTeX Consolidation (`chapter_<#>_<slug>.txt`):**
   - The merged `.txt` / `.tex` file consolidates all approved markdown sections into a single Overleaf-ready LaTeX chapter.
   - **Milestone Rule:** Re-generate and verify the merged LaTeX file as an **explicit milestone step** once all sections of the chapter are drafted, cross-audited, and approved by the user.
   - **1:1 Markdown-to-LaTeX Synchronization (Zero Drift):** Whenever an edit, tone refactor, or figure connection is made to an individual `.md` section draft, it MUST immediately be synchronized into the consolidated `chapter_<#>_<slug>.txt` file (and vice-versa).
   - **Automated Pre-Commit Invariants:**
     1. Line 1 MUST start directly with `\chapter{...}\label{chap:...}` without blank lines or preamble.
     2. Zero `\usepackage` imports or macro definitions (centralized in `config.tex`).
     3. All LaTeX environments (`\begin{...}` / `\end{...}`) must be strictly balanced.
     4. Use `academicbox` for code/PDDL/JSON listings, `formalbox` for CFG grammars; zero raw verbatim blocks.
     5. Pending figures must use compilation-safe `\fbox{\parbox{...}}` placeholders with commented `\includegraphics` commands.
     6. Every figure environment must be accompanied by a `\FloatBarrier` to prevent float intrusions.
