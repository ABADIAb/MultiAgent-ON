---
title: "Weekly Report 2026-05-19"
date: 2026-05-19
tags: [report, weekly]
status: active
---
# Master's Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
Architecture Refinement & Tool Integration Proposal

## Date Range:
May 12, 2026 - May 19, 2026

---

## 1. Planned Goals for This Week

*Carried forward from [[Weekly_Report_20260511_Felipe_Abadia|previous report]]:*
1. **Resolve Workspace Access:** Connect to the remote environment using VS Code Remote SSH and verify the setup.
2. **Implement QoT Tool Integration:** Build the adapter/integration for the QoT tool based on the strategy.
3. **LangGraph Prototyping:** Implement the minimal Orchestrator `StateGraph` ([[Architecture_Workflow_20260427_Felipe_Abadia]]).

---

## 2. Actual Progress This Week

1. **Architectural Pivot (Goal 2 — Completed):** Conducted an extensive analysis of the `Code_for_Felipe` C++ codebase. Identified that the initial "Subprocess Wrapper" strategy (Option 1) introduced significant latency and file I/O overhead. Pivoted to **Option 2: Pure Python Physics Port**, extracting the core Gaussian Noise (GN) model logic into a native Python tool.
2. **Formal Proposal (Completed):** Drafted a formal proposal for the professor ([[experiments/Proposal_QoT_Integration]]) justifying the Python port. This approach ensures low latency, in-memory execution, and rich numeric feedback (SNR/Power/Cost) for LLM reasoning.
3. **Wiki Documentation Update (Completed):** Updated the [[tools_wiki/QoT_Tool]] and [[Tool_Registry]] to reflect the new architecture and highlighted critical questions for the professor regarding testbed topology extraction and hardware constants.
4. **Workspace Access (Goal 1 — Pending):** Continued investigation into SSH connection issues.
5. **LangGraph Prototyping (Goal 3 — Pending):** Deferred pending the finalization of the QoT tool integration path.

---

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access (Persistent).
- **Status:** Still unable to connect directly via SSH.
- **Next Step:** Seek guidance from lab assistants on the specific jump-host or VPN configuration required.

### Issue 2
- **Issue:** C++ Monolith Complexity. The original simulator is a global optimizer (Genetic Algorithm), making it unsuitable for single-path queries.
- **Solution:** Pivoted to porting only the physics equations (`calculateDemandSNR`, `spanSNR`) to Python.

---

## 4. Plan for Next Week

1. **Professor Consultation:** Present the `Proposal_QoT_Integration.md` slide deck to the professor and obtain a "green light" for the Python port.
2. **Topology Extraction:** Clarify whether testbed data (fiber lengths, OA locations) will be accessed via REST API or static configuration files.
3. **Initial Python Port:** Begin the translation of the GN model math from `Network.cpp` into a standalone `qot_tool.py`.
4. **StateGraph Implementation:** Resume LangGraph prototyping once the tool interface is finalized.

---

## 5. Do You Need Support?

Write here: Guidance on the verification baseline (known-good scenario) from the professor is needed to validate the Python port accuracy.

---

## 6. One-Sentence Summary

Write here: Pivoted to a high-performance Pure Python Physics Port for QoT integration and drafted a formal proposal and presentation for the professor to secure architectural approval.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
