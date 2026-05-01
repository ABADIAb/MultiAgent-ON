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
2. **Skills.md → Tool Registry (Goal 3 — Completed with change of scope):** Instead of building `Skills.md` injection into LangGraph prompts, we resolved a deeper issue: the semantic confusion between AI assistant skills and application tools. The old `Skills.md` was renamed to [[Tool_Registry]] and moved into the wiki under `architecture/`. AI assistant skills now live in `.agent/skills/`, and application tools will live in `src/tools/`.
3. **Screaming Architecture (Unplanned — Critical):** Identified that the flat repo structure would not scale. Restructured the entire repository into four top-level directories:
   - `src/` — Application code (`agents/`, `tools/`, `core/`, `services/`).
   - `docs/` — Research knowledge base, including the [[index|LLM Wiki]] with its 2-layer architecture.
   - `.agent/` — AI assistant persona (`AGENTS.md`) and modular skills (`wiki-protocol`, `langgraph-expert`).
   - `tests/` — Reserved for Strict TDD test suite.
4. **QoT Tool Experiments (Goal 2 — Blocked):** Still waiting for the QoT script from the professor. Cannot proceed without it.
5. **Deep Research Execution (Goal 4 — Deferred):** Deferred due to time spent on repository restructuring. Will resume this week.

---

## 3. Issue List This Week

### Issue 1

- **Issue:** No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- **What has already been tried:** Defined the complete folder structure (`src/agents/`, `src/tools/`, `src/core/`, `src/services/`, `src/graph.py`).
- **Result:** The skeleton is ready, but no Python code has been written.
- **Estimated possible solution:** Begin with a minimal LangGraph `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the pipeline end-to-end.

### Issue 2

- **Issue:** The QoT (Quality of Transmission) estimator tool has been mentioned but no code or specification has been received yet.
- **What has already been tried:** Registered it as "Planning / In Development" in the [[Tool_Registry]].
- **Result:** Waiting for the professor to provide the QoT function/code.
- **Estimated possible solution:** Follow up with the professor in the next meeting to obtain the QoT tool code and its input/output specification.

---

## 4. Plan for Next Week

*Carried forward from this week + new:*
1. **LangGraph Prototyping (Continued):** Implement a minimal `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the end-to-end pipeline. Design the flowchart deferred from this week.
2. **Deep Research Execution (Deferred from this week):** Run the generated [[Research_Plan_MultiAgentON|Deep Research plan]] to find literature supporting the mathematical objective.
3. **Literature Ingestion:** Ingest at least one foundational paper into the wiki using the `Ingest` workflow.
4. **QoT Tool Follow-up:** Request the QoT tool script and testbed control scripts from the professor.

---

## 5. Do You Need Support?

Write here: Yes. I need the following support to proceed efficiently:
1. Access to the QoT tool script.
2. Access to the scripts used to interact with the physical optical testbed so I can begin designing the LangGraph tool bindings.
3. Feedback on the Screaming Architecture restructuring and whether the proposed `src/` layout aligns with team expectations.

---

## 6. One-Sentence Summary

Write here: We restructured the entire repository following a Screaming Architecture pattern, separating application code, documentation, and AI configuration into modular directories, and are now ready to begin LangGraph prototyping.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
