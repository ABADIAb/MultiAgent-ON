---
title: "Weekly Report 2026-06-01"
date: 2026-06-01
tags: [weekly-reports, status]
status: active
---
# Master's Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
LangGraph MVP Implementation & Wiki Consolidation

## Date Range:
May 26, 2026 - June 01, 2026

---

## 1. Planned Goals for This Week

*Carried forward from [[Weekly_Report_20260526_Felipe_Abadia|previous report]]:*
1. **SOTA & Literature Comparison:** Create the comparison table and some slides summarizing the differences of my MultiAgentON approach compared to existing agentic AI systems in the literature (Prof. Zhang's request).
2. **Intent Examples:** Document 3-5 concrete user intent examples showing how the LangGraph pipeline activates different agent sequences (Zheng's request).
3. **Supervisor LLM Integration:** Replace mock code in `supervisor.py` with actual LangChain/LangGraph LLM calls to parse intents into the `sla_matrix`.
4. **Pydantic Schemas:** Study the baseline JSON schemas for Python Pydantic classes implementation.

---

## 2. Actual Progress This Week

1. **Supervisor LLM Integration & Pydantic Schemas (Goals 3 & 4 — Completed):**
   - I successfully analyzed the ECOC 2024 JSON schemas in `docs/LLM_Wiki/raw/ecoc2024-llm-orchestrator/data/json_schemas/` and translated them into proper Pydantic data models for network state (`TopologySnapshot`, `NetworkNode`, `FiberLink`) and task planning (`TaskPlan`, `TaskItem`, `TaskType`).
   - I integrated the real **Kimi API** (using `langchain-anthropic` in Anthropic compatibility mode) into `src/agents/supervisor.py` to parse user queries into structured `TaskPlan` models.
2. **Experiment 001 Coded (Additional Goal — Completed):**
   - I coded and delivered the first complete end-to-end MVP pipeline: [[experiments/Experiment_001_Topology_Query_MVP|Experiment 001]].
   - Applied **Strict TDD Mode** throughout development. Built 12 modular source files and 5 test suites.
   - Achieved **62 passing tests** with **76% test coverage** across the core LangGraph modules.
3. **Architecture Fusion (Additional Goal — Completed):**
   - I unified the system design under [[Architecture_v2]], merging the two legacy architecture drafts and the three experiment proposals into a single, high-fidelity source of truth.
4. **Wiki Housekeeping (Additional Goal — Completed):**
   - I restructured all wiki directories, creating `archive/` folders for obsolete files, and updated both `index.md` and `log.md` to keep the knowledge base fully synchronized.
5. **SOTA & Intent Examples (Goals 1 & 2 — Deferred):**
   - I deferred these goals to next week to prioritize the concrete coding implementation of the LangGraph MVP.

---

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access (Persistent).
- **Status:** Still unable to connect directly via SSH.
- **Next Step:** Seek guidance from lab assistants on the specific VPN/jump-host credentials.

### Issue 2
- **Issue:** QoT Physics Port Constants & Verification Data.
- **Status:** I need the exact physical-layer constants and gold-standard verification data to translate the C++ GA solver equations in `Network.cpp` into Python.
- **Next Step:** Consult with Aryanaz to acquire the parameters.

---

## 4. Plan for Next Week

1. **Test MVP in CLI:** Test the completed [[experiments/Experiment_001_Topology_Query_MVP|Experiment 001]] using the live Kimi API via the `src/main.py` entrypoint.
2. **SOTA & Literature Comparison:** Create the literature comparison table requested by Prof. Zhang.
3. **Intent Examples:** Document 3-5 concrete user intent examples to fulfill Zheng's request.
4. **Experiment 002 (Routing + QoT):** Begin the design of the Routing Agent and the Python port of the C++ QoT equations, linking them back to the LangGraph pipeline.

---

## 5. Do You Need Support?

Write here: I still need technical assistance to configure my SSH credentials for remote workspace connection. I also need to coordinate with Aryanaz to get the C++ parameters.

---

## 6. One-Sentence Summary

I successfully consolidated the project design into Architecture V2, coded the complete LangGraph Topology Query MVP with 62 passing tests using strict TDD, and established the weekly progress towards the physics-layer implementation.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
