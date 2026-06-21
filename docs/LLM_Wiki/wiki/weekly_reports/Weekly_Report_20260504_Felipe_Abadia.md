---
title: "Weekly Report 2026-05-04"
date: 2026-05-04
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
Architecture Design & Tool Exploration

## Date Range:
April 28, 2026 - May 4, 2026

---

## 1. Planned Goals for This Week

*Carried forward from [[Weekly_Report_20260427_Felipe_Abadia|previous report]]:*
1. **LangGraph Flowcharts & Tool Interaction:** Continue studying LangGraph and design a graphical flowchart mapping the interaction between the Orchestrator, Sub-Agents, and the QoT tool.
2. **QoT Tool Experiments:** Begin running small, isolated experiments with the QoT tool.
3. **Skills.md Implementation:** Start building the actual `Skill.md` architecture and testing dynamic injection into a LangGraph prompt.
4. **Deep Research Execution:** Run the generated Deep Research plan to find literature supporting the mathematical objective.

---

## 2. Actual Progress This Week

1. **LangGraph Exploration (Goal 1 — In Progress):** Started hands-on study of the LangGraph framework. Flowchart design still pending.
2. **Screaming Architecture (Goal 1 — Repo Structure):** Identified that the flat repo structure would not scale. Restructured the entire repository into four top-level directories following Python/LangGraph best practices.
   - `src/` — Application code (`agents/`, `tools/`, `core/`, `services/`).
   - `docs/` — Research knowledge base, including the [[index|LLM Wiki]] (an md file that keeps track of all the research and progress).
   - `tests/` — Reserved for Strict TDD test suite.
3. **QoT Tool Experiments (Goal 2 — Partially Done):** I mapped out the functional specification and architectural boundaries of the QoT tool (SNR threshold, -18 dBm receiver power, GN model). These parameters are now formally documented in the Wiki. However, the script is still pending.
4. **Skills.md → Tool Registry (Goal 3 — Completed with change of scope):** The old `Skills.md` was renamed to [[Tool_Registry]] and moved into the wiki under `architecture/`, this file will keep track of the tools that the agents can use (for now it has the descriptions of the QoT tool). The actual scripts of the application tools will live in `src/tools/`.
5. **Deep Research Execution (Goal 4 — In Progress):** Successfully ingested state-of-the-art literature to define the [[Hybrid_Memory_Architecture]] (Wiki + Graph + Vector). To be presented.


---

## 3. Issue List This Week

### Issue 1

- **Issue:** No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- **What has already been tried:** Defined the complete folder structure (`src/agents/`, `src/tools/`, `src/core/`, `src/services/`, `src/graph.py`).
- **Result:** The skeleton is ready, but no Python code has been written.
- **Estimated possible solution:** Begin with a minimal LangGraph `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the pipeline end-to-end.

### Issue 2

- **Issue:** The QoT (Quality of Transmission) estimator tool has been mentioned but the script has not been provided and the virtual environment for testing is not yet ready.
- **What has already been tried:** Registered the tool as "Planning / In Development" in the [[Tool_Registry]] and secured VPN access to the network.
- **Result:** VPN is active, but waiting to set up the virtual environment to replicate the testbed.
- **Estimated possible solution:** Follow up with the professor next week regarding the status of the virtual environment setup and the QoT tool script.




---

## 4. Plan for Next Week

*Carried forward from this week + new:*
1. **LangGraph Prototyping (Continued):** Implement a minimal `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the end-to-end pipeline.
2. **QoT Tool & Virtual Environment Follow-up:** Request the QoT tool script and track the status of the virtual environment setup.
3. **Orchestrator Script Review:** Review the initial Orchestrator script provided by the professor, analyze it, and decide if it aligns with the architectural design; refine it based on feedback.


---

## 5. Do You Need Support?

Write here: Yes. I need the following support to proceed efficiently:
1. Access to the QoT tool script.
2. Status update and access to the virtual environment that replicates the physical testbed so I can begin designing and testing the LangGraph tool bindings.


---

## 6. One-Sentence Summary

Write here: I restructured the entire repository following a Screaming Architecture pattern, designed the Hybrid Memory Architecture, and secured VPN access, leaving me ready to familiarize with QoT tool and the virtual environment. Continue to study LangGraph.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
