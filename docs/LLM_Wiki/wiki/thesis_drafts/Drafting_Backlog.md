---
title: "Thesis Drafting Backlog"
date: 2026-09-01
tags: [thesis, drafts, backlog, reminders]
status: active
---

# Thesis Drafting Backlog

This document serves as a registry and reminder of all assumptions, clarifications, and engineering details that must be included in thesis chapters and sections that have not yet been written.

Review this list before finalizing each chapter.

## Chapter 4: Neurosymbolic Pipeline Implementation

### 1. Document Optical RAG Bypass (ITU-T Specs)
- **Context:** In the theoretical model (Chapter 3), Phase 1 (*Intent Ingestion & Optical RAG*) includes both dynamic topology extraction (GraphRAG) and querying standard optical specifications (ITU-T, amplifier parameters) via document retrieval.
- **Mandatory Clarification to Include:** For the scope of the MVP and experimental validation, the textual document retrieval branch of the Optical RAG was bypassed. The physical parameters of the ITU-T grid and EDFA characteristics were injected statically as constants in the code to deterministically isolate the performance of the *Risk-Adaptive Decision Gate (RADG)*.
- **Action:** Ensure it is mentioned that dynamic standard text retrieval remains as **Future Work**.

### 2. Verify LaTeX Cross-Reference Label
- **Context:** In Section 3.1.5 (Optimization Objective), we referenced Chapter 4 for the baseline experiments. We used `Chapter~\ref{chap:implementation}` to avoid hardcoding the number.
- **Action:** Ensure that when Chapter 4 is created, the label `\label{chap:implementation}` is explicitly declared right after the `\chapter{...}` command so the cross-reference resolves correctly. Also remove the `\textcolor{red}{[TODO...]}`.

---

## Chapter 1 / Chapter 2: Motivation & Literature Review

### 1. Evaluate Inclusion of Architectural Comparison Figure (`neurosymbolic_comparison`)
- **Context:** An architectural comparison figure (`neurosymbolic_comparison.drawio`) contrasting a conventional black-box End-to-End LLM baseline (prone to attention degradation, hallucinated physics, and reactive controller failure) against the proposed strict Neurosymbolic Framework was authored for Chapter 3.
- **Decision:** To prevent redundancy and maintain a dense, purely mathematical focus on our own system model within Chapter 3, this figure was moved to `figs_SystemModel/archive/`.
- **Action:** When drafting Chapter 1 (Motivation) or Chapter 2 (Literature Review & SOTA Gap Analysis), evaluate retrieving and placing this figure to visually substantiate the architectural gap against SOTA.

