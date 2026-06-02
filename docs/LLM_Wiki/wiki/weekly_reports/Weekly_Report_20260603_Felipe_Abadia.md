---
title: "Weekly Report 2026-06-03"
date: 2026-06-03
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
LangGraph MVP Validation & Kimi API Integration

## Date Range:
May 26, 2026 - June 03, 2026

---

## 1. Planned Goals for This Week

*Carried forward from [[Weekly_Report_20260526_Felipe_Abadia|previous report]]:*
1. **SOTA & Literature Comparison:** Create the comparison table and some slides summarizing the differences of my MultiAgentON approach compared to existing agentic AI systems in the literature (Prof. Zhang's request).
2. **Intent Examples:** Document 3-5 concrete user intent examples showing how the LangGraph pipeline activates different agent sequences (Zheng's request).
3. **Supervisor LLM Integration:** Replace mock code in `supervisor.py` with actual LangChain/LangGraph LLM calls to parse intents into the `sla_matrix`.
4. **Pydantic Schemas:** Study the baseline JSON schemas for Python Pydantic classes implementation.
5. **Test MVP in CLI:** Test the completed [[experiments/Experiment_001_Topology_Query_MVP|Experiment 001]] using the live Kimi API via the `src/main.py` entrypoint.

---

## 2. Actual Progress This Week

1. **Experiment 001 Ideation & Execution (New Goal — Completed):**
   - I designed [[experiments/Experiment_001_Topology_Query_MVP|Experiment 001]] from scratch: defined the hypothesis, scope, success criteria, and test flow. I documented it as a structured markdown specification.
   - I then executed the experiment, building the full LangGraph pipeline (Supervisor + Topology Agent + mock testbed) and validating the end-to-end flow with 62 passing tests and 76% test coverage under Strict TDD.

2. **Supervisor LLM Integration & Pydantic Schemas (Goals 3 & 4 — Completed):**
   - I analyzed the ECOC 2024 JSON schemas in `docs/LLM_Wiki/raw/ecoc2024-llm-orchestrator/data/json_schemas/` and translated them into Pydantic data models for network state (`TopologySnapshot`, `NetworkNode`, `FiberLink`) and task planning (`TaskPlan`, `TaskItem`, `TaskType`).
   - I integrated the real **Kimi API** into `src/agents/supervisor.py` using `langchain-openai` (replacing the initial `langchain-anthropic` approach due to endpoint restrictions). This required spoofing the `User-Agent` header to bypass API restrictions. See [[Architecture_v2]] §8 for the updated technology stack.

3. **CLI Validation with Live Kimi API (Goal 5 — Completed):**
   - I successfully tested the full orchestrator pipeline via the CLI (`src/main.py`), validating the complete flow: Intent Parsing → Topology Fetching → Synthesis.
   - I resolved several integration issues during validation:
     - Increased `max_tokens` from the default 1024 to 8192 to prevent silent response truncation during Kimi's reasoning.
     - Implemented `json_mode` and robust `AliasChoices` in `TaskItem` Pydantic schemas to handle Kimi's inconsistent field naming (e.g., `"task_type"` vs. `"type"`).
     - Separated the Supervisor's system prompt into two stages: a strict JSON extraction prompt for intent parsing and a conversational prompt for human-readable synthesis.

4. **SOTA & Intent Examples (Goals 1 & 2 — Deferred):**
   - I deferred these goals to next week to prioritize the concrete validation of the LangGraph MVP with real API calls.

---

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access (Persistent).
- **Status:** Still unable to connect directly via SSH.
- **Next Step:** Seek guidance from lab assistants on the specific VPN/jump-host credentials.

### Issue 2
- **Issue:** QoT Physics Port Constants & Verification Data.
- **Status:** I need the exact physical-layer constants and gold-standard verification data to translate the C++ GA solver equations in `Network.cpp` into Python. See [[tools_wiki/QoT_Tool]] for current parameter documentation.
- **Next Step:** Consult with Aryanaz to acquire the parameters.

---

## 4. Plan for Next Week

1. **SOTA & Literature Comparison:** Create the literature comparison table requested by Prof. Zhang.
2. **Intent Examples:** Document 3-5 concrete user intent examples to fulfill Zheng's request.
3. **Ideate Experiment 002 (Routing + QoT):** Begin the design and ideation of the next experiment, defining what to test and how to integrate the Routing Agent and QoT tool into the LangGraph pipeline.

---

## 5. Do You Need Support?

Write here: I still need technical assistance to configure my SSH credentials for remote workspace connection. I also need to coordinate with Aryanaz to get the C++ parameters.

---

## 6. One-Sentence Summary

I designed and executed the Topology Query MVP (Experiment 001), integrated the Kimi API with robust JSON parsing and two-stage prompting, and successfully validated the full orchestrator pipeline via CLI with real API calls.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
