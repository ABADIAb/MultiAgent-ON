---
title: "Weekly Report 2026-08-03"
date: 2026-08-03
tags: [weekly, report, restconf, testbed, architecture-v5, radg, refactor, nodes, documentation]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date: 
2026-08-03

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the July 20 report & Sprint 2/3 transition)*
1. **Finalize Exp 1.3:** RESTConf API integration.
2. **Execute Exp 2.3:** Symbolic Solver and Mock GraphRAG.
3. **Codebase Reorganization:** Align `src/` folder structure and methodology with [[Architecture_v5]].
4. **Begin Exp 3.1:** Risk-Adaptive Decision Gate (RADG) integration.

## 2. What did I actually accomplish?

1. **Exp 1.3 (RESTConf Testbed API):** 
   - Successfully established a live connection to the SM Optics ONC virtual testbed via VPN (IP: 10.79.26.48). 
   - Reverse-engineered and resolved the complex CAS SSO authentication flow across multiple ports (443 for frontend, 8443 for REST NBI, 8843 for CAS server redirect).
   - Implemented dynamic NE filtering to successfully isolate the "Qiaolun" topology from co-existing lab data (Team E).
   - Accommodated vendor-specific REST API quirks in the `RESTConfTestbedClient` (e.g., mapping HTTP 400 Bad Request to empty lists when `infrastructure-eth` connections are absent instead of crashing).
   - All 7 integration tests are passing against the live testbed.

2. **Exp 2.3 (Symbolic Solver & Mock GraphRAG):** 
   - Implemented a deterministic Symbolic Solver using Yen's K-Shortest Paths algorithm via `networkx`. 
   - Successfully connected the solver to the `TopologySnapshot` data structure populated by the testbed client, replacing LLM hallucinations with deterministic pathfinding based on real (or mocked) physical parameters.

3. **Source Code Placement Methodology & Codebase Reorganization:**
   - Formalized `.agents/rules/src-methodology.md` defining strict placement criteria for `core/` (pure Python domain logic), `nodes/` (LangGraph pipeline stages), `tools/` (LangChain adapters), and `services/` (external I/O).
   - Renamed `src/agents/` to `src/nodes/` to accurately reflect LangGraph node function semantics.
   - Relocated `symbolic_solver.py` to `src/core/` because it is a deterministic algorithm with zero LLM calls.
   - Updated all import references across `src/` and `tests/`. All 172 unit tests are passing cleanly.

4. **Feature Documentation Hub:**
   - Consolidated feature documentation under `docs/LLM_Wiki/wiki/architecture/features/`.
   - Written 7 comprehensive feature docs mapping code to [[Architecture_v5]]: [[features/intent_ingest]], [[features/pddl_parser]], [[features/reverse_prompt]], [[features/symbolic_solver]], [[features/qot_tool]], [[features/testbed_client]], [[features/pipeline_graph]].
   - Updated [[Architecture_v5]] and `index.md` with the new Feature Documentation Map.

5. **Wiki Maintenance:**
   - Deleted legacy literature document `recommendations.md` to prevent ambiguity.

6. **Thesis Outline Refinement:**
   - Ingested the original PDF outline and produced V3 of the thesis outline (`Thesis_Outline_v3.md`).
   - Formally integrated the V5 Problem Statement (Given, Decide, Objective) into the Architecture section.
   - Mapped SOTA citations to specific chapters, and merged the Evaluation chapters for better narrative flow.

## 3. Issue List This Week

### Issue 1
- **Issue:** Testbed lacks provisioned physical connections (`infrastructure-eth`), resulting in a 0-link topology snapshot.
- **What has already been tried:** Built the testbed client to gracefully handle the 400 response and queried other connection types (`infrastructure-eth-nni`, `service-evc`), confirming all return no data.
- **Result:** PENDING provisioning.
- **Estimated possible solution:** Await the professor's intervention to provision the optical links on the ONC, or use a mocked topology payload in the meantime to unblock routing algorithm tests.

### Issue 2
- **Issue:** LangGraph V5 Implementation Wiring ([[Architecture_v5]]).
- **What has already been tried:** Codebase reorganization completed. Component nodes are clean, but the conditional edges for RADG ($U_{sem}$ and QoT Feasibility) in `src/core/graph.py` remain to be wired.
- **Result:** IN PROGRESS.
- **Estimated possible solution:** Implement `src/core/semantic_gate.py` and `src/core/radg.py` during Sprint 3.

### Issue 3
- **Issue:** Missing Physical Parameter Exposure in NBI. The ONC RESTConf NBI API (`onc-nbi.yaml`) only exposes service-layer entities and lacks GET endpoints for L0 physical topology parameters (e.g., fiber span lengths, attenuation, EDFA noise figures) required for QoT calculation.
- **What has already been tried:** Exhaustive regex search on the OpenAPI specification to confirm the absence of these endpoints.
- **Result:** BLOCKER / PENDING physical data strategy.
- **Estimated possible solution:** Await the professor's provision of a static configuration file containing the physical testbed parameters, or fallback to mocking standard telecommunications values (e.g., SMF-28, standard EDFAs) to unblock the QoT Validation phase.

## 4. Plan for Next Week

1. **Implement Semantic Gate ($U_{sem}$):** Create `src/core/semantic_gate.py` and `src/nodes/semantic_gate_node.py` to evaluate intent clarity before solver execution.
2. **Implement RADG Gate:** Create `src/core/radg.py` and `src/nodes/radg_node.py` for physical risk decision-making.
3. **Wire V5 StateGraph:** Update `src/core/graph.py` with conditional routing (`hitl_route`, `radg_route`) for early clarification and replanning loopbacks.

---

## 5. Do I Need Support?

Yes, I need support on the following testbed/domain items:

1. **Unprovisioned Infrastructure Connections:** Currently, the SM Optics ONC controller has 3 "Qiaolun" NEs configured, but 0 connections of type `infrastructure-eth` are provisioned, leading to a topology with 0 physical links. Could you please provision the physical connections between the NEs in the testbed, or clarify if there's a different connection type we should be querying?
2. **Optical Network Physics Parameters:** Since there are no GET requests available in the current REST API payload to extract real-time physical parameters (e.g., SNR, exact fiber lengths, num_amplifiers) to feed into our QoT check, how should we proceed? Should we continue using hardcoded ECOC-realistic defaults as placeholders, or is there an alternative API endpoint for extracting these physical parameters?

---

## 6. One-Sentence Summary

I successfully integrated the RESTConf API with the live SM Optics virtual testbed, completed the deterministic Symbolic Solver, and fully reorganized the codebase and feature documentation to align with Architecture V5.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
