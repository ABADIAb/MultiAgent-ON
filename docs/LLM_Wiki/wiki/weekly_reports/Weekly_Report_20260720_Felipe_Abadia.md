---
title: "Weekly Report 2026-07-20"
date: 2026-07-14
tags: [weekly, report, architecture-v5, radg, pddl, hitl]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date: 
2026-07-20 (Ongoing)

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the July 13 report)*
1. **Finalize Sprint 1 (Exp 1.3):** Execute RESTConf Testbed API integration.
2. **Execute Sprint 2 (Exp 2.1, 2.2, 2.3):** Implement the PDDL Parser (with CFG validator), the Reverse Prompting HITL reconstruction, and the Symbolic Solver.

## 2. What did I actually accomplish?

*This week is currently ongoing. Progress so far:*

1. **Exp 2.1 & 2.2 Completed (PDDL & HITL):** 
   - Implemented the deterministic CFG Regex validator to catch PDDL structural hallucinations.
   - Prompt-engineered Kimi to generate a simplified optical network PDDL subset (aligned with [[Architecture_v5]]).
   - Built the Reverse Prompting mechanism (`interrupt()`), translating PDDL to natural language to guarantee operator intent convergence and avoid semantic drift (see [[ProblemStatement_v5]]).
   - Resolved a feedback-loop bug where the LLM was ignoring operator refinement inputs.
   - Maintained Strict TDD compliance (126 passing tests).

2. **Architecture V4 → V5 Pivot (Risk-Adaptive Decision Gate):**
   - Based on advisor feedback, reframed the thesis contribution from multi-turn clarification (already covered by PoliMi/CNSM 2025) to a **Risk-Adaptive Decision Gate (RADG)** that jointly assesses semantic uncertainty ($U_{sem}$) and QoT feasibility before deployment.
   - Created [[ProblemStatement_v5]], [[Architecture_v5]], updated [[Scope_Pivot_20260706]], [[experiments/MVP_Roadmap|MVP_Roadmap]], and [[literature/sota_gap_analysis|SOTA Gap Analysis]].
   - Defined formal baselines (No-HITL, Always-HITL, Fixed-Retry) and evaluation metrics (UAR, HIC, QFR, E2EL, TC).
   - Added PoliMi/CNSM 2025 to the SOTA comparison.

3. **Architecture V5 Optimization (Fail-Fast & Binary QoT):**
   - Re-positioned the Semantic Uncertainty assessment to trigger *before* the Symbolic Solver (between Phases 2 and 3). This creates a **Fail-Fast Semantic Gate** that prevents expensive physical routing when the initial intent is ambiguous.
   - Simplified the Physical Risk Gate from a complex mathematical margin ($R_{qot}$) to a **Binary Feasibility Gate** (Valid/Invalid). Replaced the rigid "Reject" state with a "Suggest Replan" HITL loop that directly feeds back into Phase 2, vastly improving operator UX and system simplicity.

## 3. Issue List This Week

### Issue 1
- **Issue:** RESTConf Hook to Virtual Testbed.
- **What has already been tried:** Implemented a structural `RESTConfTestbedClient` stub in Python, but lack the exact endpoint details.
- **Result:** PENDING (Blocks Exp 1.3).
- **Estimated possible solution:** Await the professor's response with the virtual testbed API details (URL, Auth, Endpoints) to complete the integration.

## 4. Plan for Next Week

1. Finalize Exp 1.3 as soon as the RESTConf API is provided.
2. Execute Exp 2.3: Symbolic Solver and Mock GraphRAG.
3. Begin Exp 3.1: Risk-Adaptive Decision Gate (RADG) implementation (Refactoring `src/core/graph.py` and `src/core/radg.py` to wire the Fail-Fast Semantic Gate and Binary Physical Gate).

---

## 5. Do I Need Support?

Yes, I need support on two items:

1. **RESTConf API** (ongoing): I am still waiting for the API documentation (Base URL, Authentication, and Topology Endpoints) for the virtual RESTConf testbed to complete Exp 1.3.

2. **Semantic Uncertainty Proxy for RADG** (new): For the Risk-Adaptive Decision Gate, I plan to quantify semantic uncertainty ($U_{sem}$) using a two-layer approach:
   - *Layer 1*: Binary pass/fail from the CFG PDDL structural validator (already implemented).
   - *Layer 2*: Embedding-based similarity score between the original operator intent and the Reverse Prompting NL reconstruction — measuring how much the system's interpretation diverges from the operator's original request.

   **Question for the professor:** Is this two-layer approach (structural + semantic embedding similarity) a reasonable proxy for semantic uncertainty in the MVP? Would the professor recommend an alternative metric, such as LLM token-level log-probabilities or a different semantic similarity method? Any guidance on calibrating the threshold $\tau_{sem}$ for the Layer 2 disagreement score would also be valuable.

---

## 6. One-Sentence Summary

This week, we completed the PDDL parser and Reverse Prompting HITL, evolved the architecture from V4 to V5 around a Risk-Adaptive Decision Gate, and further optimized the pipeline with a Fail-Fast Semantic Gate and Binary Physical Gate to maximize UX and compute efficiency.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support

