---
title: "Issue Report 2026-05-25"
date: 2026-05-25
tags: [issues, weekly]
status: active
---
# Issue Report

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
LangGraph Scaffolding & Post-Meeting Planning

## Date:
2026-05-25

---

### Solved Issues

#### Solved Issue 1 (Carry forward from May 11)
- **Original issue:** No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- **What was tried:** Scaffolded the full LangGraph `StateGraph` with `AgentState` TypedDict, 5 graph nodes, and 4 mock agent modules.
- **Resolution / outcome:** `src/core/state.py`, `src/core/graph.py`, and `src/agents/` (supervisor, topology, routing, lightpath) are created. Tests (`test_state.py`, `test_graph.py`) passing.

#### Solved Issue 2 (Carry forward from May 11)
- **Original issue:** Orchestrator Script Review was pending.
- **What was tried:** Cloned and analyzed the professor's `ecoc2024-llm-orchestrator` repository.
- **Resolution / outcome:** Technical report generated ([[literature/OrchestratorScriptReport]]). Pipeline logic, JSON schemas, and RESTConf interaction model extracted. V2 LangGraph architecture designed incorporating these assets ([[LangGraph_Orchestrator_V2]]).

---

### Pending Issues

#### Pending Issue 1
- **Issue:** Remote Workspace SSH Access (Persistent, carry forward from May 11).
- **What has already been tried:** Connected to the VPN and received SSH credentials (`ssh qiaolun@10.79.26.43`).
- **Result:** Connection still not established.
- **Estimated possible solution:** Seek guidance from lab assistants on jump-host or VPN configuration.

#### Pending Issue 2
- **Issue:** The [[Research_Plan_MultiAgentON|Research Plan]] literature review is still in progress (Phases 1 and 2). Now elevated by Prof. Qiaolun's explicit request for a SOTA comparison table/slides.
- **What has already been tried:** Some papers read and incorporated into architecture decisions.
- **Result:** No formal comparison artifact produced yet.
- **Estimated possible solution:** Dedicate focused time to compile a comparison table of existing agentic AI works in optical networking vs. our approach. Target: 1-2 slides for the next professor meeting.

---

### Additional Notes

This session marked the transition from pure architecture design to actual code scaffolding. The LangGraph graph compiles and all tests pass, validating the architectural design decisions. The next critical path items are the SOTA comparison (academic deliverable) and replacing mock agents with real LLM integration (technical deliverable).
