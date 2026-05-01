---
title: "Weekly Report 2026-04-27"
date: 2026-04-27
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
April 25, 2026 - April 27, 2026

---

## 1. Planned Goals for This Week

1. **LangGraph Exploration:** Start hands-on exploration and prototyping with the LangGraph framework to build the new orchestrator foundation.
2. **QoT Tool Study:** Deep dive into the Quality of Transmission (QoT) tool/function to understand its inputs, outputs, and constraints for agentic calling.
3. **New Architecture Design:** Formalize the integration of the "LLM wiki" memory structure and the "Skills.md" dynamic loading system into the LangGraph nodes.

---

## 2. Actual Progress This Week

1. **Problem Statement Mathematical Refinement:** Refined the [[ProblemStatement_20260427_Felipe_Abadia|Problem Statement]]'s objective function to couple optical variables (e.g., spectrum fragmentation, EDFA power) and compute variables (GPU utilization, VRAM). Shifted Semantic Distortion and Inference Latency into explicit, strict constraints.
2. **Architecture V2 Formalization:** Upgraded the [[Architecture_Workflow_20260427_Felipe_Abadia|Architecture Workflow]] to a LangGraph-driven topology featuring Hybrid Memory (LLM Wiki + RAG), Tool-RAG registries, and Ephemeral Sub-Agents to strictly manage the context window.
3. **Deep Research Plan Generation:** Created a structured [[Research_Plan_MultiAgentON|research plan]] with specific database queries and deep research prompts to validate our mathematical constraints and explore state-of-the-art memory management.

---

## 3. Issue List This Week

### Issue 1

- **Issue:** Uncertainty regarding the exact implementation mechanism of the LLM Wiki memory method within the LangGraph framework. Furthermore, practical integration is blocked pending access to the actual QoT script and test-bed control scripts.
- **What has already been tried:** Formalized the theoretical Architecture V2 document and mapped out the LangGraph Supervisor-Worker topology.
- **Result:** Theoretical design is complete, but we need the physical scripts to design the actual Python LangGraph `StateGraph` schema and tool bindings.
- **Estimated possible solution:** Request the necessary scripts from the team and create a graphical flowchart to map out tool inputs/outputs before starting to write the Python code.

---

## 4. Plan for Next Week

1. **LangGraph Flowcharts & Tool Interaction:** Continue studying LangGraph and design a graphical flowchart mapping the interaction between the Orchestrator, Sub-Agents, and the QoT tool.
2. **QoT Tool Experiments:** Begin running small, isolated experiments with the QoT tool to understand its behavior and JSON serialization requirements for the LangGraph `ToolNode`.
3. **Skills.md Implementation:** Start building the actual `Skill.md` architecture, drafting the first template and testing how to dynamically inject it into a LangGraph prompt.
4. **Deep Research Execution:** Run the generated Deep Research plan to find literature supporting our mathematical objective and exploring memory management in intent-based networking.

---

## 5. Do You Need Support?

Write here: Yes. I need the following support to proceed efficiently:
1. Comments and guidance on the refined mathematical objective in the Problem Statement.
2. Feedback on the proposed Architecture V2 (LangGraph + Hybrid Memory).
3. Access to the actual QoT tool script.
4. Access to the scripts used to interact with the physical optical testbed so I can begin designing the LangGraph tool bindings.

---

## 6. One-Sentence Summary

Write here: We formalized the problem statement math and upgraded the architecture to a LangGraph-driven topology, but now require the physical testbed and QoT scripts to begin flowcharting and implementing the proof-of-concept.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
