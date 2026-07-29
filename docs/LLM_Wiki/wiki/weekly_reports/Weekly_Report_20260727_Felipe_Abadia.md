---
title: "Weekly Report 2026-07-27"
date: 2026-07-29
tags: [weekly, report, restconf, testbed, architecture-v5, radg, pddl, hitl]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date: 
2026-07-29

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the July 20 report)*
1. **Finalize Exp 1.3:** RESTConf API integration.
2. **Execute Exp 2.3:** Symbolic Solver and Mock GraphRAG.
3. **Begin Exp 3.1:** Risk-Adaptive Decision Gate (RADG) integration.

## 2. What did I actually accomplish?

1. **Exp 1.3 (RESTConf Testbed API):** 
   - Successfully established a live connection to the SM Optics ONC virtual testbed via VPN (IP: 10.79.26.48). 
   - Reverse-engineered and resolved the complex CAS SSO authentication flow across multiple ports (443 for frontend, 8443 for REST NBI, 8843 for CAS server redirect).
   - Implemented dynamic NE filtering to successfully isolate the "Qiaolun" topology from co-existing lab data (Team E).
   - Accommodated vendor-specific REST API quirks in the `RESTConfTestbedClient` (e.g., mapping HTTP 400 Bad Request to empty lists when `infrastructure-eth` connections are absent instead of crashing).
   - All 7 integration tests are now passing against the live testbed.

2. **Exp 2.3 (Symbolic Solver & Mock GraphRAG):** 
   - Implemented a deterministic Symbolic Solver using Yen's K-Shortest Paths algorithm via `networkx`. 
   - Successfully connected the solver to the `TopologySnapshot` data structure populated by the testbed client, replacing LLM hallucinations with deterministic pathfinding based on real (or mocked) physical parameters.

## 3. Issue List This Week

### Issue 1
- **Issue:** Testbed lacks provisioned physical connections (`infrastructure-eth`), resulting in a 0-link topology snapshot.
- **What has already been tried:** Built the testbed client to gracefully handle the 400 response and queried other connection types (`infrastructure-eth-nni`, `service-evc`), confirming all return no data.
- **Result:** PENDING provisioning.
- **Estimated possible solution:** Await the professor's intervention to provision the optical links on the ONC, or use a mocked topology payload in the meantime to unblock routing algorithm tests.

### Issue 2
- **Issue:** LangGraph Implementation Refactor ([[Architecture_v5]]).
- **What has already been tried:** The components (client, solver, validators) are ready, but the orchestrator pipeline needs to be re-wired to align with the Fail-Fast Semantic Gate and Binary Physical Gate logic.
- **Result:** PENDING execution.
- **Estimated possible solution:** Refactor `src/core/radg.py` and `src/core/graph.py` during Sprint 3.

## 4. Plan for Next Week

1. **Execute Exp 3.1:** Implement the Risk-Adaptive Decision Gate (RADG) wiring the Fail-Fast Semantic Gate and Binary Physical Gate in LangGraph.
2. **Finalize Sprint 3:** Run end-to-end pipeline tests connecting natural language intent all the way to testbed physical paths.
3. **Draft Thesis Chapters:** Begin structuring the methodology chapter based on the finalized [[Architecture_v5]].

---

## 5. Do I Need Support?

Yes, I need support on the following testbed/domain items:

1. **Unprovisioned Infrastructure Connections:** Currently, the SM Optics ONC controller has 3 "Qiaolun" NEs configured, but 0 connections of type `infrastructure-eth` are provisioned, leading to a topology with 0 physical links. Could you please provision the physical connections between the NEs in the testbed, or clarify if there's a different connection type we should be querying?
2. **Optical Network Physics Parameters:** Since there are no GET requests available in the current REST API payload to extract real-time physical parameters (e.g., SNR, exact fiber lengths, num_amplifiers) to feed into our QoT check, how should we proceed? Should we continue using hardcoded ECOC-realistic defaults as placeholders, or is there an alternative API endpoint for extracting these physical parameters?

---

## 6. One-Sentence Summary

I successfully integrated the RESTConf API with the live SM Optics virtual testbed, handling complex CAS auth and API quirks, and finalized the deterministic Symbolic Solver for intent routing.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
