---
title: "Weekly Report 2026-08-24"
date: 2026-08-24
tags: [weekly, report, mock-topology, nobel-germany, edfa, qot, symbolic-solver, architecture-v5]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date: 
2026-08-24

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the August 11 report & Sprint 3 completion)*
1. **Sprint 4 (Exp 4.0):** Design the structured Test Corpus spanning Safe, Ambiguous, and Infeasible physical and semantic risk categories.
2. **Sprint 4 (Exp 4.1):** Run the baseline comparison evaluation against the synthetic intents.
3. **Metrics Collection:** Measure and document Unsafe Approval Rate (UAR), Human Interaction Count (HIC), QoT Feasibility Rate (QFR), and Token Cost (TC) comparing our Risk-Adaptive HITL against No-HITL and Always-HITL baselines.

---

## 2. What did I actually accomplish?

1. **Topology Strategy Alignment & Mock Migration:**
   - Following direct feedback from the team ([[transcriptions/Transcript_20260811_ThesisOutline_MockTopology]]), I addressed the core limitation of evaluating on a downscaled 3-node lab testbed with sub-1km fibers.
   - Successfully migrated the orchestrator mock environment to the standard **Nobel-Germany 17-node, 26-link optical backbone network** (SNDlib benchmark), providing a realistic meshed topology suitable for long-distance multi-hop transmission and baseline evaluation.
2. **Optical Physical Layer & EDFA Calibration:**
   - Enriched `MockTestbedClient` with 17 core German nodes and 26 bidirectional links with realistic physical spans (37.5 km to 381.9 km).
   - Designed and integrated `_build_link_amplifiers()` implementing realistic physical optical amplification:
     - Boosters (3.0 dB gain) to offset node traversal loss without causing multi-hop power run-away.
     - Inline Amplifiers (ILAs) every $\approx 70\text{ km}$ on spans $>55\text{ km}$ compensating fiber attenuation ($\alpha = 0.25\text{ dB/km}$) and connector losses.
     - Preamplifiers at destination ingress.
   - Calibrated channel power levels ($-15\text{ dBm}$ to $-11\text{ dBm}$), guaranteeing physically sound GSNR ($11\text{ dB}$ to $23\text{ dB}$) for the GN-model and avoiding non-linear interference saturation.
3. **Symbolic Solver Constraint Parsing & Node Resolution Fix (BUG-006):**
   - Diagnosed and resolved an architectural parsing mismatch between the PDDL generator and the symbolic solver:
     - Enhanced `_parse_pddl_constraints()` to support standard PDDL `:goal` routing predicates (`(route <src> <dst>)`, `(routed <src> <dst>)`, `(path <src> <dst>)`) and individual endpoint predicates (`(target <dst>)`, `(destination <dst>)`).
     - Added case-insensitive matching and direct `node_id` lookup to `_resolve_node_id()`.
     - Implemented safe fallback to `state["enriched_intent"]`, completely eliminating silent fallbacks to arbitrary default nodes.
4. **Pipeline Node Synchronization & Test Suite Expansion (Strict TDD):**
   - Synchronized `intent_ingest_node`, `pddl_parser_node`, `symbolic_solver_node`, and CLI entrypoints to handle the 17-node German topology seamlessly.
   - Added unit test suites verifying $K$-shortest paths on the meshed German network, multi-hop trans-Germany ($>1000\text{ km}$) lightpath verification, and PDDL route constraint parsing variations.
   - Expanded the test suite to **242 unit tests**, passing with 100% success.
5. **Git & Feature Documentation:**
   - Published feature branch `feat/17-node-german-mock-topology`.
   - Updated feature documentation in [[architecture/features/testbed_client]] and [[architecture/features/symbolic_solver]].

---

## 3. Issue List This Week

### Issue 1 (SOLVED)
- **Issue:** The 3-node linear testbed lacked multi-hop routing diversity and realistic fiber span lengths for numerical evaluation of ILAs and baselines.
- **What has already been tried:** Implemented the 17-node Nobel-Germany benchmark topology with 26 bidirectional links in `MockTestbedClient`.
- **Result:** SOLVED.

### Issue 2 (SOLVED)
- **Issue:** Multi-hop routes across the German topology caused optical power accumulation at intermediate nodes, triggering GN-model non-linear saturation.
- **What has already been tried:** Calibrated booster gains to 3.0 dB and ILAs to span attenuation, stabilizing optical power between $-15\text{ dBm}$ and $-11\text{ dBm}$.
- **Result:** SOLVED.

### Issue 3 (SOLVED)
- **Issue:** The symbolic solver failed to extract source and destination from PDDL goal expressions `(route <src> <dst>)`, falling back to arbitrary default endpoints (`Hannover`/`Leipzig`).
- **What has already been tried:** Expanded regex constraint parsing, added case-insensitive node resolution, and safe fallback to enriched intent.
- **Result:** SOLVED.

### Issue 4 (PENDING)
- **Issue:** The physical testbed returns 0 connections for `infrastructure-eth` (unprovisioned links).
- **What has already been tried:** Handled gracefully via the mocked topology layer.
- **Result:** PENDING provisioning for the live run (Exp 4.3).

*(See full details in the [[issues/Issue_Report_20260824_Felipe_Abadia]]).*

---

## 4. Plan for Next Week

1. **Sprint 4 (Exp 4.0):** Design and formalize the structured synthetic Test Corpus (20–30 intents) spanning Safe, Ambiguous, and Infeasible physical and semantic risk categories mapped to the 17-node German topology.
2. **Sprint 4 (Exp 4.1):** Run the baseline comparison evaluation against the synthetic intents comparing Risk-Adaptive HITL against No-HITL and Always-HITL baselines.
3. **Metrics Collection:** Measure and document Unsafe Approval Rate (UAR), Human Interaction Count (HIC), QoT Feasibility Rate (QFR), and Token Cost (TC).

---

## 5. Do I Need Support?

No blocker at this moment. The 17-node German mock environment and solver pipeline are fully operational and unblock Sprint 4 (Exp 4.0 and Exp 4.1) for offline evaluation.

---

## 6. One-Sentence Summary

I successfully migrated the mock environment to the 17-node Nobel-Germany optical backbone network with calibrated EDFA physics, resolved the symbolic solver PDDL routing goal parsing, and verified full pipeline stability across 242 unit tests, preparing the system for Sprint 4 baseline evaluations.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
