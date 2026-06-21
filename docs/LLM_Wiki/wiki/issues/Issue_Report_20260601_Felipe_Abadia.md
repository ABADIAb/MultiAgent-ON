---
title: "Issue Report 2026-06-01"
date: 2026-06-01
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
LangGraph MVP Implementation & Wiki Consolidation

## Date:
2026-06-01

---

### Solved Issues

#### Solved Issue 1 (Carry forward from May 11 Pending Issue 1)
- **Original issue:** No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- **What was tried:** I designed and implemented the first complete, functional end-to-end MVP pipeline: [[experiments/Experiment_001_Topology_Query_MVP|Experiment 001]].
- **Resolution / outcome:** The codebase is now fully active. I created 12 modular source files, configured the environment variables, and wrote 5 test suites under Strict TDD Mode. All **62 tests are passing** with **76% test coverage**.

#### Solved Issue 2 (Carry forward from May 11 Pending Issue 3)
- **Original issue:** Orchestrator Script Review.
- **What was tried:** I read and analyzed the baseline ECOC 2024 JSON schemas in `docs/LLM_Wiki/raw/ecoc2024-llm-orchestrator/data/json_schemas/` to align our models with Prof. Zhang's previous system.
- **Resolution / outcome:** The data structures for lightpaths, services, and measurements are now fully documented and integrated into the unified [[Architecture_v2]] design and the MVP state representation.

#### Solved Issue 3 (Carry forward from May 11 Pending Issue 4)
- **Original issue:** SOTA & Literature Comparison.
- **What was tried:** Conducted a comprehensive web search (covering Confucius, AutoLight, HearthNet, IETF drafts) to analyze the current SOTA.
- **Resolution / outcome:** Successfully created [[literature/lit_comparison|lit_comparison.md]] establishing the 5 architectural families and our unique positioning, and drafted [[literature/recommendations|recommendations.md]] for next steps. The issue is fully resolved.
---

### Pending Issues

#### Pending Issue 1 (Carry forward from May 11 Pending Issue 2)
- **Issue:** Remote Workspace Access (SSH).
- **What has already been tried:** I connected to the lab VPN and received SSH credentials, but connection attempts to the machine (`10.79.26.43`) fail or time out.
- **Result:** I cannot establish a persistent, direct remote workspace connection in VS Code.
- **Estimated possible solution:** Seek technical assistance from lab assistants to verify the specific jump-host configuration or jump-host IP required to reach the VM.

---

### Additional Notes
This week marks a major milestone: transitioning from purely conceptual architecture into a solid, tested codebase. The strict test coverage gives a robust foundation for the physical layer integration in Experiment 002.
