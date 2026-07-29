---
title: "Issue Report 2026-07-27"
date: 2026-07-29
tags: [issues, report, blocker, langgraph, radg, testbed]
status: active
---

# Issue Report: 2026-07-27

## 1. RESTConf Hook to Virtual Testbed (SOLVED)
- **Issue:** Unable to complete Exp 1.3 (SSH Testbed Connectivity Hook) because the specific virtual testbed API details were missing.
- **What has already been tried:** We received the VPN credentials (`10.79.26.48`). Mapped the CAS SSO authentication flow across ports 8843 and 8443. Rewrote the `RESTConfTestbedClient` to handle the redirect chain and establish the session cookie.
- **Result:** SOLVED. We can now fetch NEs, connections, and topologies. 172/172 unit tests and 7/7 integration tests pass.

## 2. Unprovisioned Infrastructure Connections (NEW)
- **Issue:** The testbed returns 0 connections for `infrastructure-eth`, leading to a topology snapshot with 3 nodes but 0 links.
- **What has already been tried:** We updated the `RESTConfTestbedClient` to gracefully handle the ONC's 400 Bad Request error (which it throws when an array is empty). We also probed alternative endpoints (`infrastructure-eth-nni`, `service-evc`), all returning no physical links.
- **Result:** PENDING provisioning.
- **Estimated possible solution:** The professor must provision the physical DWDM links in the SM Optics ONC. Alternatively, we can use a mocked topology payload so the Symbolic Solver can route over a realistic graph structure in the meantime.

## 3. LangGraph Implementation Refactor (Architecture V5) (PENDING)
- **Issue:** The current codebase in `src/` requires refactoring to align with the simplified Architecture V5 optimizations (Fail-Fast Semantic Gate and Binary Physical Gate).
- **What has already been tried:** The components (client, symbolic solver, validators) are completed. The orchestrator pipeline itself has not been rewritten yet.
- **Result:** PENDING execution.
- **Estimated possible solution:** 
  1. Modify `src/core/radg.py` to implement the Fail-Fast Semantic Gate logic.
  2. Implement the Binary QoT feasibility check in the pipeline.
  3. Wire the conditional edges in `src/core/graph.py` so both "Clarify" and "Suggest Replan" trigger HITL and loop back safely.
