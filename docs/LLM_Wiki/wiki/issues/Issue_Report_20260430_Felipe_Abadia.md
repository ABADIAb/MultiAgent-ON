---
title: "Issue Report 2026-04-30"
date: 2026-04-30
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
Exploration

## Date:
2026-04-30

---

### Solved Issues

#### Solved Issue 1

- Original issue: The repository had no clear separation between AI assistant configuration, application code, documentation, and tests. Everything was in the root directory.
- What was tried: Discussed architectural patterns (Screaming Architecture, src/ layout) and the role of `.agents/` vs `src/`.
- Resolution / outcome: Restructured the entire repo into `src/`, `docs/`, `.agents/`, and `tests/`. Moved `LLM_Wiki` into `docs/`, split `AGENTS.md` into persona + modular skills.

#### Solved Issue 2

- Original issue: Risk of confusing the AI assistant's own skills/tools with the LangGraph tools being built for the optical network system.
- What was tried: Discussed the semantic difference and physical separation of both toolsets.
- Resolution / outcome: AI assistant skills live in `.agents/skills/`. Application tools for the multi-agent system will live in `src/tools/`. The old `Skills.md` was renamed to `Tool_Registry.md` and moved into the wiki under `architecture/`.

---

### Pending Issues

#### Pending Issue 1

- Issue: No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- What has already been tried: Defined the folder structure (`src/agents/`, `src/tools/`, `src/core/`, `src/services/`, `src/graph.py`).
- Result: The skeleton is ready, but no Python code has been written.
- Estimated possible solution: Begin with a minimal LangGraph `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the pipeline end-to-end.

#### Pending Issue 2

- Issue: The QoT (Quality of Transmission) estimator tool has been mentioned but no code or specification has been received yet.
- What has already been tried: Registered it as "Planning / In Development" in the Tool Registry.
- Result: Waiting for the professor to provide the QoT function/code.
- Estimated possible solution: Follow up with the professor in the next meeting to obtain the QoT tool code and its input/output specification.

---

### Additional Notes

This session was entirely focused on infrastructure and developer experience (DX). No research or implementation code was produced. The next session should pivot to either literature review (ingesting papers into the wiki) or hands-on LangGraph prototyping.
