---
title: "Weekly Report 2026-08-11"
date: 2026-08-11
tags: [weekly, report, sprint3, radg, qot, architecture-v5, langgraph]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date: 
2026-08-11

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the August 03 report & Sprint 2/3 transition)*
1. **Implement Semantic Gate ($U_{sem}$):** Create evaluation logic for intent clarity before solver execution.
2. **Implement RADG Gate:** Create physical risk decision-making node mapping QoT to `{approve, replan}`.
3. **Wire V5 StateGraph:** Update the core graph with conditional routing for early clarification and replanning loopbacks.

## 2. What did I actually accomplish?

1. **Sprint 3 Completion:** I successfully fully implemented all planned goals for Sprint 3. The orchestrator is now feature-complete for the MVP.
2. **LangGraph Pipeline Refactor:** 
   - Wired the fail-fast conditional routing of Architecture V5 (`src/core/graph.py`).
   - Removed the manual 3-way routing from the `reverse_prompt` node, cleanly separating the reconstruction checkpoint from the semantic routing decision.
3. **Semantic Gate Implementation:**
   - Authored `src/core/semantic_gate.py` implementing the two-layer $U_{sem}$ validation.
   - For the semantic divergence ($d_{sem}$), I designed an LLM-scored agreement method to evaluate the divergence between the natural language intent and the PDDL reconstruction, avoiding heavy external dependencies.
4. **Physical Risk Gate (RADG) Implementation:**
   - Formalized the RADG logic in `src/core/radg.py` and its corresponding LangGraph node (`radg_node.py`), replacing the previous placeholders.
   - Upgraded the QoT Validation phase to execute the real GN-model `assess_qot()` over the candidate paths produced by the symbolic solver.
5. **Topology & Mocking Strategy:**
   - Downscaled the topology to a mathematically strict 3-node linear topology (`Milano-A ↔ Milano-B ↔ Milano-C`) to align with realistic physical lab capabilities.
   - Overcame the NBI parameter limitations (unexposed L0 values) by artificially enriching the `MockTestbedClient` with standard ECOC physical parameters (EDFAs, port losses), guaranteeing determinism for the baseline evaluation phase.
6. **Codebase Stability:** Test suite grew from 172 to 231 tests, all passing with 100% success.
7. **Documentation Hub Expansion:** Created and updated feature documentation across the wiki for all new components (Semantic Gate, RADG, Plan Synthesizer, etc.).

## 3. Issue List This Week

### Issue 1
- **Issue:** The orchestrator pipeline required wiring the Fail-Fast Semantic Gate ($U_{sem}$) and Binary Physical Risk Gate (RADG) conditional loopbacks.
- **What has already been tried:** Implemented nodes and state models. Wired conditionals directly into `StateGraph`.
- **Result:** SOLVED.

### Issue 2
- **Issue:** The ONC RESTConf NBI API lacks GET endpoints for L0 physical topology parameters.
- **What has already been tried:** Enriched the `MockTestbedClient` with hardcoded realistic ECOC physical parameters to bypass the API limitation.
- **Result:** SOLVED / MITIGATED. 

### Issue 3
- **Issue:** The testbed returns 0 connections for `infrastructure-eth` (unprovisioned links). 
- **What has already been tried:** Handled gracefully via the mocked topology.
- **Result:** PENDING provisioning for the final live execution.

*(See full details in the [[issues/Issue_Report_20260811_Felipe_Abadia]]).*

## 4. Plan for Next Week

1. **Sprint 4 (Exp 4.0):** Design the structured Test Corpus spanning Safe, Ambiguous, and Infeasible physical and semantic risk categories.
2. **Sprint 4 (Exp 4.1):** Run the baseline comparison evaluation against the synthetic intents.
3. **Metrics Collection:** Measure and document Unsafe Approval Rate (UAR), Human Interaction Count (HIC), QoT Feasibility Rate (QFR), and Token Cost (TC) comparing our Risk-Adaptive HITL against No-HITL and Always-HITL baselines.

---

## 5. Do I Need Support?

Yes, regarding the final MVP deadline execution:

1. **Test Corpus Generation:** To execute the baseline evaluations (Exp 4.1), I urgently need the mathematically sound synthetic test corpus that spans multiple risk categories (Safe, Ambiguous, Infeasible) mapped to the 3-node topology.
2. **Live Server and VPN Access:** Currently, the live server and VPN are offline. While this does not block Exp 4.0 and 4.1 (which rely on our deterministic mock testbed for baseline comparisons), I will need the server restored and the `infrastructure-eth` connections physically provisioned if we intend to execute Exp 4.3 (Live E2E Lab Testbed Execution). 

---

## 6. One-Sentence Summary

I successfully completed Sprint 3 by formalizing the Risk-Adaptive Decision Gate, wiring the Architecture V5 conditional loopbacks, and integrating real GN-model QoT validation against a downscaled 3-node mock topology.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
