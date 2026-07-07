---
title: "Weekly Report 2026-07-06"
date: 2026-07-06
tags: [weekly, report, pivot, neurosymbolic, mvp]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Neurosymbolic Orchestration of Intents for Optical Networks: A Graph-Aware Human-in-the-Loop Approach

## Date: 
2026-07-06

---

## 1. What did you plan to accomplish this week?

*(Carried forward from the June 22 report)*
1. **Experiment 002:** Intent Parsing + HITL reverse prompting (NL → `sla_matrix` with multi-turn `interrupt()`).
2. **Design PlanningReport Schema:** Define the Pydantic models.
3. **Intent Examples:** Document 3-5 concrete operator intent examples.
4. **Present Scope Pivot:** Present the new scope to the professor.

## 2. What did you actually accomplish?

I deferred Experiment 002 as originally designed because new research into IBON and AON revealed critical flaws in the purely generative loop approach (specifically token saturation and hallucinated physical calculations). Instead, I executed a rigorous strategic pivot:

1. **Pivoted to Architecture V4 (Neurosymbolic Intent Orchestration):**
   - Transitioned from a purely generative loop to a pipeline that separates LLM reasoning (PDDL generation) from deterministic physical calculation (Mock GraphRAG + Symbolic Solver + QoT Python Tool).
   - Documented the [[Scope_Pivot_20260706|Scope Pivot]] rationale.

2. **Wiki Restructuring:**
   - Archived all V3 documentation.
   - Authored [[Architecture_v4]] and [[ProblemStatement_v4]] to establish the new thesis foundation.
   - Updated the [[sota_gap_analysis|SOTA Gap Analysis]] to reflect the Neurosymbolic positioning.

3. **Defined MVP Roadmap:**
   - Established a 4-sprint roadmap targeting a functional prototype by August 25. 
   - This roadmap focuses on pragmatic integration: migrating the C++ QoT simulator to Python, implementing a Mock GraphRAG dictionary, and establishing SSH connectivity with the lab testbed.

4. **Codebase Handover Preparation:**
   - Analyzed the existing `experiment_001` baseline in `src/`.
   - Generated a formal handover document (`Context_For_Next_Chat.md`) to ensure seamless continuation of the LangGraph development without context loss in future sessions.

5. **Exp 1.1 & 1.2 Completed (QoT Tooling):**
   - Successfully ported the core GN model physics from C++ (`Network.cpp`) into a pure Python module (`qot_calculator.py`) using Strict TDD (95% coverage, 30 passing tests).
   - Created the `@tool` wrapper (`qot_tool.py`) for LangGraph, finalizing the deterministic physics component of the Neurosymbolic architecture.

## 3. Issue List This Week

### Issue 1
- **Issue:** C++ to Python QoT translation is pending.
- **What has already been tried:** The C++ simulator is documented, but we need a pure Python equivalent to run smoothly as a LangChain tool.
- **Result:** **SOLVED**. The translation was successfully achieved using a rigorous Strict TDD process.
- **Estimated possible solution:** (Solved) The GN-model calculations were translated to Python and wrapped in a `@tool` decorator (`qot_tool.py`), successfully closing Exp 1.1 and 1.2.

### Issue 2
- **Issue:** Need to verify the SSH hook to the physical testbed.
- **What has already been tried:** We have the `MockTestbedClient` working locally.
- **Result:** Real-world provisioning is untested.
- **Estimated possible solution:** Write a secure Python Paramiko adapter to connect via SSH to the simple testbed, proving we can fetch topology and push configurations.

---

## 4. Plan for Next Week

1. **Execute Sprint 1 (Exp 1.0, 1.1, 1.2, 1.3):** 
   - Verify Kimi LLM connection.
   - Translate QoT to Python and wrap it as a LangGraph tool.
   - Establish the SSH testbed connection.
2. **Begin Sprint 2 (Exp 2.1):** 
   - Prompt engineering for the PDDL Intent Parser.

---

## 5. Do You Need Support?

Write here: I need the professor to review the new [[Presentation_20260706_Neurosymbolic_MVP|Neurosymbolic MVP Presentation]] to validate the August 25 prototype deadline.

---

## 6. One-Sentence Summary

## 6. One-Sentence Summary

I successfully analyzed the flaws of the generative loop, pivoted the thesis architecture to a Neurosymbolic pipeline with a firm August 25 MVP roadmap, and fully implemented the QoT physics tool in Python as the first operational component of the MVP.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
