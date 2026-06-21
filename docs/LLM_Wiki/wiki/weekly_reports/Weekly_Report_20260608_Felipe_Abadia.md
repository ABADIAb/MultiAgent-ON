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

4. **SOTA & Literature Comparison (Goal 1 — Completed):**
   - I conducted a deep web search and created a systematic SOTA comparison ([[literature/lit_comparison|lit_comparison.md]]) mapping 5 architectural families (Confucius, AutoLight, HearthNet, etc.).
   - I developed [[literature/recommendations|recommendations.md]] with prioritized research directions based on the SOTA gap analysis.

5. **Intent Examples (Goal 2 — Deferred):**
   - I deferred this goal to next week to prioritize the concrete validation of the LangGraph MVP and the extensive SOTA analysis.

---

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access (Persistent).
- **Status:** Still unable to connect directly via SSH.
- **Next Step:** Seek guidance from lab assistants on the specific VPN/jump-host credentials.


---

## 4. Plan for Next Week

1. **Intent Examples:** Document 3-5 concrete user intent examples to fulfill Zheng's request.
2. **Ideate Experiment 002 (Routing + QoT):** Begin the design and ideation of the next experiment, defining what to test and how to integrate the Routing Agent and QoT tool into the LangGraph pipeline.
3. **Compute Scheduling Research:** Begin investigating the compute scheduling dimension of the thesis (as recommended in our new analysis).

---

## 5. Do You Need Support?

Write here: I still need technical assistance to configure my SSH credentials for remote workspace connection.

---

## 6. One-Sentence Summary

I designed and executed the Topology Query MVP (Experiment 001), integrated the Kimi API, successfully validated the full orchestrator pipeline via CLI, and completed a deep SOTA literature comparison identifying our unique architectural positioning.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
