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

## 4. Hardcoded Topology in PDDL Parser (SOLVED)
- **Issue:** The PDDL parser (Phase 2) relied on a hardcoded testbed topology string in its system prompt, preventing the pipeline from scaling to dynamic live topologies.
- **What has already been tried:** Integrated Mock GraphRAG into the Intent Ingest node (Phase 1) to dynamically extract a $k=2$ hop neighborhood around the requested nodes. This subgraph is serialized into text and passed as `topology_context` to the PDDL parser.
- **Result:** SOLVED. The parser now dynamically generates constraints based strictly on the provided context without relying on hardcoded strings.

## 5. GN-Model Non-Linear Interference Saturation in Short Spans (SOLVED)
- **Issue:** The QoT Validation calculation using the GN-model yielded impossible values (-47 dB SNR) for feasible routes.
- **What has already been tried:** Traced the root cause to the `MockTestbedClient`. It inherited default EDFA gains (+43 dB per link) meant for 80km spans. In our 20km and 40km MVP spans, this over-amplified the signal to 2 Watts (+33 dBm), triggering a cubic explosion in the non-linear interference ($NLI \propto P^3$). Calibrated the EDFA gains to exactly offset span attenuation.
- **Result:** SOLVED. The GN-model now yields accurate physical ranges ($P_{rx} = -6.0\text{ dBm}$, $SNR = 21.76\text{ dB}$).

## 6. PDDL Parser Node Naming Leakage (SOLVED)
- **Issue:** The Reverse Prompting module (Phase 3) hallucinated internal technical node IDs (`node_1`) in its natural language reconstruction instead of human-readable names (`Milano-A`).
- **What has already been tried:** Identified that `mock_graphrag.py` included `(node_1)` in the injected context, leading the `pddl_parser` to select it as the object name in the PDDL string. Restricted the context serialization and `PDDL_SYSTEM_PROMPT` to enforce human-readable names exclusively.
- **Result:** SOLVED. PDDL properly generates with `Milano-A` and the HITL reconstruction correctly names the nodes.

## 7. Test Corpus Generation for Baseline Evaluation (NEW)
- **Issue:** To execute Exp 4.1, we require a mathematically sound synthetic test corpus that spans multiple risk categories (Safe, Ambiguous, Infeasible).
- **What has already been tried:** N/A (Just starting Sprint 4).
- **Result:** IN PROGRESS.
- **Estimated possible solution:** Design ~20-30 natural language intents in a JSON structure mapped to the expected physical outcome on our 3-node topology.
