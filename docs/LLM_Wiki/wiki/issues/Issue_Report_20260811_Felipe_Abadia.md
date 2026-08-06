---
title: "Issue Report 2026-08-11"
date: 2026-08-11
tags: [issues, report, langgraph, radg, testbed]
status: active
---

# Issue Report: 2026-08-11

## 1. LangGraph Implementation Refactor & RADG Wiring (SOLVED)
- **Issue:** The orchestrator pipeline in `src/core/graph.py` required wiring the Fail-Fast Semantic Gate ($U_{sem}$) and Binary Physical Risk Gate (RADG) conditional loopbacks (Sprint 3).
- **What has already been tried:** Implemented `src/core/semantic_gate.py` and `src/core/radg.py`. Removed V4's 3-way routing from `reverse_prompt_node`. Wired the conditionals (`semantic_gate_route` and `radg_route`) directly into the `StateGraph` in `src/core/graph.py`.
- **Result:** SOLVED. The Architecture V5 pipeline is fully operational with 231 passing tests.

## 2. Missing Physical Parameter Exposure in NBI (SOLVED/MITIGATED)
- **Issue:** The ONC RESTConf NBI API lacks GET endpoints for L0 physical topology parameters (e.g., fiber span lengths, EDFA noise figures) required for QoT calculation.
- **What has already been tried:** Since the live server and VPN are currently offline anyway, I pivoted to enriching the `MockTestbedClient`. I hardcoded realistic ECOC physical parameters (EDFA boosters/preamps, port losses) directly into the mocked 3-node linear topology.
- **Result:** SOLVED for the MVP. This unblocks the QoT Validation phase deterministically.

## 3. Unprovisioned Infrastructure Connections (PENDING)
- **Issue:** The physical testbed returns 0 connections for `infrastructure-eth`, leading to a topology snapshot with nodes but 0 links.
- **What has already been tried:** Handled gracefully via the `MockTestbedClient` which provides the expected 3-node topology (`Milano-A ↔ Milano-B ↔ Milano-C`).
- **Result:** PENDING provisioning for the live run.
- **Estimated possible solution:** For Sprint 4's baseline evaluations (Exp 4.1), the mocked topology is sufficient. However, for the final Live E2E Lab Testbed Execution (Exp 4.3), the server must be brought online and physical DWDM links must be provisioned in the SM Optics ONC.

## 4. Test Corpus Generation for Baseline Evaluation (NEW)
- **Issue:** To execute Exp 4.1, we require a mathematically sound synthetic test corpus that spans multiple risk categories (Safe, Ambiguous, Infeasible).
- **What has already been tried:** N/A (Just starting Sprint 4).
- **Result:** IN PROGRESS.
- **Estimated possible solution:** Design ~20-30 natural language intents in a JSON structure mapped to the expected physical outcome on our 3-node topology.
