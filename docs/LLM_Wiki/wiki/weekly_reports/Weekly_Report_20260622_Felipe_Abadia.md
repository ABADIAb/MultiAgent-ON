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
Agentic AI for joint routing and compute scheduling in optical networks

## Date: 
2026-06-22

---

## 1. What did you plan to accomplish this week?

(Carried forward from the June 8 report):
1. **Intent Examples:** Document 3-5 concrete user intent examples.
2. **Ideate Experiment 002 (Routing + QoT):** Begin design and integration of the Routing Agent and QoT tool.
3. **Compute Scheduling Research:** Investigate the compute dimension.

## 2. What did you actually accomplish?

I did not work on the previously planned goals because the SOTA presentation was delayed at the professor's request to integrate new material. Instead, I focused heavily on refining the core [[Architecture_v2|architecture]] and completing the presentation for this week:

1. **Strategic Thesis Pivot:**
   - I formally excised "compute scheduling" from the immediate scope, deferring it to future work due to time constraints. 
   - I updated my [[ProblemStatement_20260427_Felipe_Abadia|Problem Statement]] to structurally reinforce the thesis around three core differentiators: Natural Language Intent Parsing, Deterministic QoT Validation, and Formal Human-In-The-Loop (HITL) Safety.

2. **Literature Ingestion & Gap Analysis:**
   - I ingested and analyzed key competitor literature: Meta's [[literature/Confucius_SIGCOMM2025|Confucius]] and the [[literature/SJTU_Invited_Tutorial_JOCN2026|SJTU AutoLight Tutorial]].
   - I comprehensively updated my [[literature/sota_gap_analysis|SOTA Gap Analysis]] and [[literature/lit_comparison|Literature Comparison]] to position MultiAgentON against these frameworks.

3. **SOTA Presentation Completed:**
   - I finalized the [[Presentation_20260604_SOTA_Analysis|SOTA Comparison Presentation]] requested by the professor, heavily emphasizing our unique "Slow Loop" safety features (Neurosymbolic Separation and `interrupt()` HITL). It is now ready for review.

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access.
- **Status:** The SSH connection is now supposed to be working, but I still need to verify it.
- **Next Step:** Test the SSH connection to confirm the issue is fully resolved.

---

## 4. Plan for Next Week

1. **Ideate Experiment 002:** Integrate the Routing Agent and the Python GN model [[tools_wiki/QoT_Tool|QoT tool]] into the LangGraph MVP.
2. **Formal HITL Implementation:** Design and code the `interrupt()` mechanism to allow operator validation of parsed intent before execution.
3. **Intent Examples:** Document 3-5 concrete user intent examples to fulfill the previous request.

---

## 5. Do You Need Support?

Write here: I need to verify my SSH connection this week to see if the jump-host is properly configured.
