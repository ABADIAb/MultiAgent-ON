---
title: "Thesis Drafting Backlog"
date: 2026-09-01
tags: [thesis, drafts, backlog, reminders]
status: active
---

# Thesis Drafting Backlog

This document serves as a registry and reminder of all assumptions, clarifications, and engineering details that must be included in thesis chapters and sections that have not yet been written.

Review this list before finalizing each chapter.

## Chapter 4: Neurosymbolic Pipeline Implementation (Drafted)

- **Status:** Sections 4.1, 4.2, and 4.3 drafted under `docs/LLM_Wiki/wiki/thesis_drafts/4_NPImp/`.

### 1. Document Optical RAG Bypass (ITU-T Specs) — [RESOLVED]
- **Resolution:** Explicitly documented in Section 4.1 under *Remark 1 (Optical RAG Standard Specification Bypass)*. Dynamic retrieval is deferred to Chapter 6 Future Work.

### 2. Verify LaTeX Cross-Reference Label — [RESOLVED]
- **Resolution:** Declared `\label{chap:implementation}` immediately following `\chapter{Neurosymbolic Pipeline Implementation}` on line 1 of `chapter_4_implementation.txt`, ensuring cross-chapter references from Chapter 3 resolve cleanly.

### 3. Dynamic Subtopology Scoping (Ellipsoid GraphRAG) — [RESOLVED]
- **Resolution:** Explicitly documented in Section 4.1 under *Remark 2 (Ellipsoid Subtopology Scoping for Large Diameters)* with the formal node set equation.

---

## Chapter 1 / Chapter 2: Motivation & Literature Review

### 1. Evaluate Inclusion of Architectural Comparison Figure (`neurosymbolic_comparison`)
- **Context:** An architectural comparison figure (`neurosymbolic_comparison.drawio`) contrasting a conventional black-box End-to-End LLM baseline (prone to attention degradation, hallucinated physics, and reactive controller failure) against the proposed strict Neurosymbolic Framework was authored for Chapter 3.
- **Decision:** To prevent redundancy and maintain a dense, purely mathematical focus on our own system model within Chapter 3, this figure was moved to `figs_SystemModel/archive/`.
- **Action:** When drafting Chapter 1 (Motivation) or Chapter 2 (Literature Review & SOTA Gap Analysis), evaluate retrieving and placing this figure to visually substantiate the architectural gap against SOTA.

### 3. Dynamic Subtopology Scoping (Ellipsoid GraphRAG)
- **Context:** In Phase 1 and 4, the initial theoretical design proposed a naive static $k$-hop neighborhood extraction to bound the context size. However, if the shortest path distance $d > 2k$, the extracted subgraph becomes disconnected, causing the LLM to falsely conclude infeasibility.
- **Action:** Ensure that the final architecture description (and future work section) explicitly clarifies the migration from naive $k$-hop to an **Ellipsoid Subtopology Scoping** (or dynamic $k$-hop), where nodes are extracted conditionally based on $d(S, v) + d(v, T) \le d(S, T) + \Delta$ to guarantee subgraph connectivity and optimal token efficiency regardless of network diameter.
