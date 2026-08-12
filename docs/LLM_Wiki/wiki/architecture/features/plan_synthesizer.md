---
title: "Feature: Plan Synthesizer"
date: 2026-08-06
tags: [feature, plan-synthesizer, reporting, phase7, nodes]
status: active
---

# Feature: Plan Synthesizer

## 1. Architecture Placement
**Phase 7: Plan Synthesizer** | [[Architecture_v5]]

The Plan Synthesizer is the final node in the Architecture V5 pipeline. It is only reached if the [[radg]] (Risk-Adaptive Decision Gate) approves the physical feasibility of at least one candidate path. Its purpose is to compile a full, auditable execution report detailing the decisions made across the entire pipeline.

## 2. Overview
The synthesizer reads the `AgentState` accumulated throughout the graph execution and produces a detailed markdown summary. This summary is intended to be both human-readable (for the operator) and machine-auditable.

## 3. How it Works
The node extracts the following traces from the state:
- **Semantic Trace**: Evaluates the Semantic Gate trace ($U_{sem}$ score, pass/fail).
- **Physical Trace**: Iterates through all candidate paths, outputting their QoT feasibility (`SNR` and `P_rx` against thresholds).
- **RADG Decision**: Explicitly records the upstream physical risk decision.
- **Recommendation**: Automatically selects the best feasible path (highest GSNR) and formats it as the final recommendation.

## 4. Associated Files
- **LangGraph Node**: [src/nodes/plan_synthesizer.py](file:///home/felipeab/MultiAgentON/src/nodes/plan_synthesizer.py) — `plan_synthesizer_node()`

## 5. Inputs / Outputs
- **Input (State)**: `enriched_intent`, `usem_score`, `usem_passed`, `radg_decision`, `qot_results`.
- **Output (State)**: `planning_report` (str), `messages` (AIMessage containing the report).

## 6. Pipeline Node Status
In Sprint 3, this node was upgraded from a simple placeholder to a full reporting engine that natively supports the Architecture V5 trace (Semantic + Physical Risk).

## 7. Cross-References
- [[Architecture_v5]] — Phase 7 description
- [[architecture/features/radg]] — Gate that conditionally routes to this node
- [[architecture/features/qot_tool]] — Generates the QoT results synthesized here
