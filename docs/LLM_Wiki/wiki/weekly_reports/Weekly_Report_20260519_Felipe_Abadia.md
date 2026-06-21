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
1. **Generate QoT Implementation Plan:** Define the technical strategy to integrate the physics port (GN model) into the multi-agent system.
2. **LangGraph Prototyping:** Initiate prototyping with the analysis of the Orchestrator Script and implement the minimal `StateGraph` ([[Architecture_Workflow_20260427_Felipe_Abadia]]).
3. **Orchestrator Script Review:** Review the initial Orchestrator script provided by the professor, analyze it, and decide if it aligns with the architectural design.

---

## 2. Actual Progress This Week

1. **Architectural Pivot (Goal 1 — Completed):** Conducted an extensive analysis of the `Code_for_Felipe` C++ codebase. Identified that the initial "Subprocess Wrapper" strategy (Option 1) introduced significant latency and file I/O overhead. Pivoted to **Option 2: Pure Python Physics Port**, extracting the core Gaussian Noise (GN) model logic into a native Python tool.
2. **Formal Proposal (Goal 1 — Completed):** Drafted a formal proposal for the professor ([[experiments/Proposal_QoT_Integration]]) and the integration strategy ([[experiments/QoT_Integration_Strategy.md]]), justifying the Python port. This approach ensures low latency, in-memory execution, and rich numeric feedback (SNR/Power/Cost) for LLM reasoning.
3. **Wiki Documentation Update (Completed):** Updated the [[tools_wiki/QoT_Tool]] and [[Tool_Registry]] to reflect the new architecture and highlighted critical questions for the professor regarding testbed topology extraction and hardware constants.
4. **Workspace Access (Issue — Pending):** Continued investigation into SSH connection issues.
5. **Orchestrator Script Review (Goal 3 — Completed):** Cloned and analyzed the professor's `ecoc2024-llm-orchestrator` repository. Generated a technical report ([[literature/OrchestratorScriptReport]]) and a formal integration proposal ([[experiments/Proposal_Orchestrator_Integration]]). Determined the baseline script cannot be used as-is (procedural, stateless, hardcoded to `llama_cpp`), but identified reusable assets: the pipeline logic, JSON schemas, and RESTConf interaction model.
6. **LangGraph Architecture Design (Goal 2 — In Progress):** Designed the V2 LangGraph Orchestrator architecture integrating the professor's pipeline logic with our [[Hybrid_Memory_Architecture]] and a Human-in-the-Loop validation phase. Defined three specialized sub-agents: Lightpath Agent, QoT Physics Agent, and Topology Agent.
7. **Topology Extraction Resolved:** Confirmed via the ECOC 2024 paper that testbed topology data (fiber lengths, OA locations) is accessible dynamically via the **RESTConf NBI**. No static configuration files needed.

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

1. **Professor Consultation:** Present both proposals to the professor: [[experiments/Proposal_QoT_Integration]] (Python port) and [[experiments/Proposal_Orchestrator_Integration]] (LangGraph architecture). Obtain approval to proceed with implementation.
2. **QoT Implementation Execution:** Begin the translation of the GN model math from `Network.cpp` into a standalone `qot_tool.py` as per the approved strategy.
3. **StateGraph Implementation:** Begin coding the LangGraph `StateGraph` based on the V2 architecture: Supervisor Node, HITL validation, and the first sub-agent (Topology Agent with RESTConf).

---

## 5. Do You Need Support?

Write here: Guidance on the verification baseline (known-good scenario) from the professor is needed to validate the Python port accuracy.

---

## 6. One-Sentence Summary

Pivoted to a native Python physics port for QoT integration, completed the Orchestrator Script review, resolved the Topology question (RESTConf), and drafted two architectural proposals detailing a LangGraph V2 integration with our Hybrid Memory.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
