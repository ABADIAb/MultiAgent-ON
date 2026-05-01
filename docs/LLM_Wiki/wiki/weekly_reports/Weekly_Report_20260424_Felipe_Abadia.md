---
title: "Weekly Report 2026-04-24"
date: 2026-04-24
tags: [report, weekly]
status: active
---
# Master's Weekly Report Template (Formal Version v3)

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
Exploration

## Date Range:
April 18, 2026 - April 24, 2026

---

## 1. Planned Goals for This Week

1. Finalize the Problem Statement and conceptual presentation for the Orchestrator.
2. Define the framework to be used for the implementation.

---

## 2. Actual Progress This Week

1. **Presentation & Problem Statement:** Completed the presentation defining the formal [[ProblemStatement_20260427_Felipe_Abadia|Problem Statement]].
2. **Architectural Pivot Exploration:** Began researching and designing a new architectural paradigm based on an **"LLM wiki"** for structured memory/knowledge management and a **"Skills.md"** framework for modular agent capabilities. 
3. **Tool Integration Prep:** Received the first deterministic tool/function related to Quality of Transmission (QoT) aware requests to be called by the Agentic system.

---

## 3. Issue List This Week

### Issue 1

- Issue: Transitioning the architecture to the new "LLM wiki + Skills.md" paradigm requires redefining how the agent stores and retrieves state.
- What has already been tried: Initial exploration of the Skills.md structure and how it differs from monolithic prompt instructions.
- Result: Currently mapping out how LangGraph will handle these dynamic skill injections.
- Estimated possible solution: Dedicate next week to building a proof-of-concept in LangGraph that successfully loads a "Skill" and queries the "LLM wiki".

---

## 4. Plan for Next Week

1. **LangGraph Exploration:** Start hands-on exploration and prototyping with the LangGraph framework to build the new orchestrator foundation.
2. **QoT Tool Study:** Deep dive into the newly provided Quality of Transmission (QoT) tool/function to understand its inputs, outputs, and constraints for agentic calling.
3. **New Architecture Design:** Formalize the integration of the "LLM wiki" memory structure and the "Skills.md" dynamic loading system into the LangGraph nodes.

---

## 5. Do You Need Support?

Write here: I would appreciate the code of the new QoT tool to ensure the LangGraph agent parses the operator's intent correctly before calling it. Also, feedback on the "LLM wiki" + "Skills.md" pivot would be highly valuable.

---

## 6. One-Sentence Summary

Write here: We finalized the initial problem statement presentation, but are actively pivoting the architecture to incorporate an "LLM wiki" and a "Skills.md" framework, while preparing to integrate the first QoT-aware tool using LangGraph.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support