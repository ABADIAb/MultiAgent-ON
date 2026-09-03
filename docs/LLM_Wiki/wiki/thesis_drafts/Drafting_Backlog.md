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
