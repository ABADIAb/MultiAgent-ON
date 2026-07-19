---
title: "Issue Report 2026-07-20"
date: 2026-07-19
tags: [issues, report, blocker, langgraph, radg]
status: active
---

# Issue Report: 2026-07-20

## 1. RESTConf Hook to Virtual Testbed
- **Issue:** Unable to complete Exp 1.3 (SSH Testbed Connectivity Hook) because the specific virtual testbed API details are missing.
- **What has already been tried:** Implemented a structural `RESTConfTestbedClient` stub in Python, but lack the exact endpoint details, base URL, and authentication methodology.
- **Result:** PENDING. Blocks the full integration to the testbed.
- **Estimated possible solution:** Await the professor's response with the virtual testbed API details (URL, Auth, Endpoints) to complete the integration.

## 2. LangGraph Implementation Refactor (Architecture V5)
- **Issue:** The current codebase in `src/` requires refactoring to align with the simplified Architecture V5 optimizations (Fail-Fast Semantic Gate and Binary Physical Gate).
- **What has already been tried:** The architectural blueprint (`Architecture_v5.md`) has been fully updated. No code has been written yet.
- **Result:** PENDING execution.
- **Estimated possible solution:** 
  1. Modify `src/core/radg.py` to implement the Semantic Gate logic separated from the Physical Gate.
  2. Implement the Binary QoT feasibility check instead of the $R_{qot}$ calculation.
  3. Wire the new conditional looping paths in `src/core/graph.py` so that both "Clarify" and "Suggest Replan" trigger HITL and loop back to Phase 2.
