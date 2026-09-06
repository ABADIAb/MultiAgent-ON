---
title: "Issue Report 2026-09-06"
date: 2026-09-06
tags: [issues, drawio, gitignore, tooling, system-model]
status: active
---

# Issue Report

---

## Student Name:
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Current Stage:
> Execution / Wrap-up of Chapter 3

## Date:
2026-09-06

---

### Solved Issues

#### Solved Issue 1: Draw.io Temporary Lock and Backup Files Cluttering Workspace

- **Original issue:** When editing `.drawio` diagram files in VS Code / Electron Draw.io, hidden lock and backup files prefixed with `.$` (e.g., `.$problem_formulation.drawio.bkp`) were automatically generated and persisted in the filesystem even after closing the application.
- **What was tried:** Investigated the Electron auto-save and crash-recovery locking mechanism. Verified that once the main `.drawio` file is saved, the `.$*.bkp` files contain redundant transient snapshots.
- **Resolution / outcome:** Added permanent ignore patterns (`.\$*.drawio*` and `*.drawio.bkp`) to `.gitignore`, safely purged orphaned backup files, and verified that `git status` remains clean.

---

### Pending Issues

> None. All Chapter 3 drafting ([[thesis_drafts/3_SystemModel/3_1_Formal_Problem_Definition|Section 3.1]]–[[thesis_drafts/3_SystemModel/3_5_Formal_HITL_Reverse_Prompting|3.5]]), figure generation ([[thesis_drafts/3_SystemModel/figs/README]]), and LaTeX compilation ([[thesis_drafts/3_SystemModel/chapter_3_system_model.txt]]) deliverables are fully resolved and verified.

---

### Additional Notes

The thesis workflow now features two clearly separated visual artifact pathways documented in [[thesis_drafts/3_SystemModel/figs/README]]:
- **Pathway A (Draw.io XML):** Stored in `figs/src/diagrams/`, allowing interactive manual editing without Python dependencies, and exported via CLI to vector `.pdf` and 300 DPI `.png`.
- **Pathway B (Matplotlib Python Scripts):** Stored in `figs/src/plots/`, generating analytical simulation curves directly to `pdf/` and `png/`.
