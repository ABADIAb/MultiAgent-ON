---
title: "Weekly Report 2026-06-22"
date: 2026-06-22
tags: [weekly, report]
status: active
---
# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
QoT-Informed Intent Planning for Optical Networks: A Neurosymbolic Human-in-the-Loop Approach

## Date: 
2026-06-22

---

## 1. What did you plan to accomplish this week?

(Carried forward from the June 8 report):
1. **Intent Examples:** Document 3-5 concrete user intent examples.
2. **Ideate Experiment 002 (Routing + QoT):** Begin design and integration of the Routing Agent and QoT tool.
3. **Compute Scheduling Research:** Investigate the compute dimension.

## 2. What did you actually accomplish?

I did not work on the previously planned goals because the SOTA presentation was delayed at the professor's request to integrate new material. Instead, I focused heavily on refining the core [[Architecture_v3|architecture]] and completing the presentation for this week:

1. **Strategic Thesis Pivot:**
   - I formally excised "compute scheduling" from the immediate scope, deferring it to future work due to time constraints. 
   - I updated my [[ProblemStatement_20260427_Felipe_Abadia|Problem Statement]] to structurally reinforce the thesis around three core differentiators: Natural Language Intent Parsing, Deterministic QoT Validation, and Formal Human-In-The-Loop (HITL) Safety.

2. **Literature Ingestion & Gap Analysis:**
   - I ingested and analyzed key competitor literature: Meta's [[literature/Confucius_SIGCOMM2025|Confucius]] and the [[literature/SJTU_Invited_Tutorial_JOCN2026|SJTU AutoLight Tutorial]].
   - I comprehensively updated my [[literature/sota_gap_analysis|SOTA Gap Analysis]] and [[literature/lit_comparison|Literature Comparison]] to position MultiAgentON against these frameworks.

3. **SOTA Presentation Completed:**
   - I finalized the [[Presentation_20260604_SOTA_Analysis|SOTA Comparison Presentation]] requested by the professor, heavily emphasizing our unique "Slow Loop" safety features (Neurosymbolic Separation and `interrupt()` HITL). It is now ready for review.

4. **AutoLight Field Trial Ingestion & Framework Validation:**
   - I ingested and analyzed the latest ECOC 2025 field-trial paper for AutoLight (SJTU). 
   - I discovered that AutoLight is built entirely on LangGraph, independently validating our core architectural choice with the most advanced optical multi-agent framework to date.
   - I refined our SOTA Gap Analysis to explicitly define our Unique Selling Proposition (USP): combining Natural Language Intent Parsing, QoT-aware routing, and formal `interrupt()` HITL protocols—a combination absent in the SJTU approach.

5. **Formal Scope Pivot (Session June 22):**
   - After analyzing the SOTA evidence, I formally pivoted the thesis scope from a full multi-agent lifecycle system to the **Intent Planning Loop** — the iterative phase where operator intent is parsed, validated against QoT constraints, and refined through multi-turn HITL.
   - Created [[Architecture_v3]] (superseding V2), [[ProblemStatement_v3]] (superseding V1), and a formal [[Scope_Pivot_20260621|Scope Pivot]] rationale document.
   - Rewrote the [[literature/sota_gap_analysis|SOTA Gap Analysis]], updated [[literature/lit_comparison|Literature Comparison]] and [[literature/recommendations|Research Recommendations]] to reflect the planning-loop focus.
   - Prepared a [[Presentation_20260621_Scope_Pivot|9-slide presentation]] for the professor explaining the SOTA-driven pivot.

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access.
- **Status:** The SSH connection is now supposed to be working, but I still need to verify it.
- **Next Step:** Test the SSH connection to confirm the issue is fully resolved.

---

## 4. Plan for Next Week

1. **Experiment 002**: Intent Parsing + HITL reverse prompting (NL → `sla_matrix` with multi-turn `interrupt()`).
2. **Design PlanningReport Schema**: Define the Pydantic models (`PlanningReport`, `CandidatePath`, `SLAMatrix`).
3. **Intent Examples**: Document 3-5 concrete operator intent examples to fulfill the previous request.
4. **Present Scope Pivot**: Present the new scope to the professor using the prepared presentation.

---

## 5. Do You Need Support?

Write here: I need to verify my SSH connection this week to see if the jump-host is properly configured.

---

## 6. One-Sentence Summary

I formally pivoted the thesis scope to the "Intent Planning Loop" based on rigorous SOTA evidence, updated all core architecture and literature artifacts accordingly, and prepared the final scope presentation for the professor.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
