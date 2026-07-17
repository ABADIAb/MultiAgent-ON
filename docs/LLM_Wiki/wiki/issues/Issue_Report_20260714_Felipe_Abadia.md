---
title: "Issue Report 2026-07-14"
date: 2026-07-14
tags: [issue, report, pddl, hitl, restconf]
status: active
---

# Issue Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Neurosymbolic Orchestration of Intents for Optical Networks: A Graph-Aware Human-in-the-Loop Approach

## Date: 
2026-07-14

---

## 1. Solved Issues

### Issue 1: PDDL Feedback Loop Ignoring Refinement
- **Issue:** During the HITL interruption in `src/main.py`, if the user chose `refine` and provided feedback (e.g., "I made a mistake, route from B to D"), the system looped back to `pddl_parser` but ignored the feedback, generating the exact same PDDL again based on the original intent.
- **What has already been tried:** We traced the state keys during the LangGraph loop and noticed that `error_context` correctly stored the operator's feedback, but `pddl_parser_node` was only reading `enriched_intent` and ignoring both the previous constraints and the feedback.
- **Result:** **SOLVED**. We updated `src/agents/pddl_parser.py` (part of [[Architecture_v4]]) to check for `previous_pddl` and `error_context`. If present, the LLM is prompted with the original intent, the rejected PDDL, and the specific operator feedback to generate the corrected output. Added a unit test to guarantee this behavior.

---

## 2. Pending Issues

### Issue 2: RESTConf Hook to Virtual Testbed (Carried from July 10)
- **Issue:** We need to verify the provisioning hook to the virtual testbed before full LangGraph integration (Blocks Experiment 1.3).
- **What has already been tried:** We identified that the testbed uses RESTConf (not SSH). I implemented a structural `RESTConfTestbedClient` stub in Python, but the exact endpoints are missing.
- **Result:** PENDING (Blocks Exp 1.3).
- **Estimated possible solution:** Await the professor's response with the specific virtual testbed API documentation (URL, Authentication, and Topology Endpoints). Once received, I will complete the `get_topology` and `health_check` methods.

---

## 3. Do I Need Support?

Write here: Yes, I need the professor to provide the API documentation (Base URL, Authentication, and Topology Endpoints) for the virtual RESTConf testbed to complete Exp 1.3.

---

## 4. One-Sentence Summary

I successfully resolved the HITL refinement loop bug, allowing the orchestrator to correctly process operator feedback, leaving only the virtual testbed API documentation as the final blocker for Sprint 1.

---

## 5. Self-Check Before Submission

- [x] I have detailed the issue clearly
- [x] I have written what has already been tried
- [x] I have written the result of what has been tried
- [x] I have written the estimated possible solution
- [x] I have indicated whether I need support
