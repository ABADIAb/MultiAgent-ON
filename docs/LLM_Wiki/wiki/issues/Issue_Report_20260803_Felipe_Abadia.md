---
title: "Issue Report 2026-08-03"
date: 2026-08-03
tags: [issues, report, blocker, langgraph, radg, testbed, refactor]
status: active
---

# Issue Report: 2026-08-03

## 1. RESTConf Hook to Virtual Testbed (SOLVED)
- **Issue:** Unable to complete Exp 1.3 (SSH Testbed Connectivity Hook) because the specific virtual testbed API details were missing.
- **What has already been tried:** We received the VPN credentials (`10.79.26.48`). Mapped the CAS SSO authentication flow across ports 8843 and 8443. Rewrote the `RESTConfTestbedClient` to handle the redirect chain and establish the session cookie.
- **Result:** SOLVED. We can now fetch NEs, connections, and topologies. 172/172 unit tests and 7/7 integration tests pass.

## 2. Unprovisioned Infrastructure Connections (PENDING)
- **Issue:** The testbed returns 0 connections for `infrastructure-eth`, leading to a topology snapshot with 3 nodes but 0 links.
- **What has already been tried:** We updated the `RESTConfTestbedClient` to gracefully handle the ONC's 400 Bad Request error (which it throws when an array is empty). We also probed alternative endpoints (`infrastructure-eth-nni`, `service-evc`), all returning no physical links.
- **Result:** PENDING provisioning.
- **Estimated possible solution:** The professor must provision the physical DWDM links in the SM Optics ONC. Alternatively, we can use a mocked topology payload so the Symbolic Solver can route over a realistic graph structure in the meantime.

## 3. Codebase Reorganization & Architecture V5 Alignment (SOLVED)
- **Issue:** The current codebase in `src/` required refactoring to align with the simplified Architecture V5 structure and methodology (`nodes/`, `core/` separation, feature documentation).
- **What has already been tried:** Formulated `.agents/rules/src-methodology.md`, renamed `agents/` to `nodes/`, moved `symbolic_solver.py` to `core/`, updated imports across `src/` and `tests/`, and authored 7 feature docs under `docs/LLM_Wiki/wiki/architecture/features/`.
- **Result:** SOLVED. Codebase is clean, fully documented, and mapped to [[Architecture_v5]].

## 4. LangGraph Implementation Refactor & RADG Wiring (IN PROGRESS)
- **Issue:** The orchestrator pipeline in `src/core/graph.py` requires wiring the Fail-Fast Semantic Gate ($U_{sem}$) and Binary Physical Risk Gate (RADG) conditional loopbacks.
- **What has already been tried:** Built component nodes and state models.
- **Result:** IN PROGRESS (Sprint 3 target).
- **Estimated possible solution:** 
  1. Create `src/core/semantic_gate.py` for $U_{sem}$ calculation.
  2. Create `src/core/radg.py` for the binary QoT decision function.
  3. Wire the conditional edges in `src/core/graph.py` so both "Clarify" and "Suggest Replan" trigger HITL and loop back safely.

## 5. Missing Physical Parameter Exposure in NBI (BLOCKER)
- **Issue:** The ONC RESTConf NBI API (`onc-nbi.yaml`) only exposes service-layer entities (L2, EVPL, PM counters, Alarms) and lacks GET endpoints for L0 physical topology parameters (e.g., fiber span lengths, attenuation, EDFA noise figures). 
- **What has already been tried:** Exhaustive regex search on the OpenAPI specification.
- **Result:** PENDING physical data strategy.
- **Estimated possible solution:** The professor must provide a static configuration file (e.g., JSON/YAML) detailing the physical testbed parameters to inject into the `qot_calculator.py`. Otherwise, we will be forced to mock standard telecommunications values (e.g., SMF-28, standard EDFAs) to run the QoT Validation phase.
