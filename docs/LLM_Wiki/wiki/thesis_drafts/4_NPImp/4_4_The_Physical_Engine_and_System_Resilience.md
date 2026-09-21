---
title: "Chapter 4 - Section 4.3: The Physical Engine and System Resilience"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, qot, physics-engine, radg, hitl, synthesis, e2e-flows]
status: draft
---

# 4.4 The Physical Engine and System Resilience

## 4.4.1 The Deterministic Symbolic Solver (Phase 4)

Once the intent passes the Semantic RADG, the validated PDDL constraints enter the non-neural Symbolic Solver. This module bridges the linguistic intent and the physical engine by computing feasible paths over the subtopology. 

The solver executes Yen's $K$-Shortest Paths algorithm over the pruned context graph, ensuring topological constraints (e.g., node exclusions, link avoidances, and maximum hop limits) are strictly enforced before any physical transmission calculations begin. By removing unfeasible topologies early, the solver guarantees that downstream calculations only process topologically sound paths.

## 4.4.2 Deterministic GN-Model Physical-Layer Physics Engine (Phase 5)

When candidate lightpaths are extracted by the Symbolic Solver in Phase 4, their transmission feasibility must be verified against the physical optical layer. Delegating this verification to an LLM introduces hallucinated physics. In our architecture, physical validation is strictly isolated within the **QoT Calculator** (`src/core/qot_calculator.py`), an analytical software engine implementing the incoherent Gaussian Noise (GN) model.

The software execution flow traces the continuous optical path across cascading spans and intermediate nodes:
1. **Per-Span Evaluation:** The engine computes the non-linear interference constant $\eta_0$ based on physical fiber parameters (attenuation, Kerr coefficient, dispersion). For each span, it calculates Amplified Spontaneous Emission (ASE) noise from EDFAs and non-linear distortion.
2. **End-to-End Accumulation:** The pipeline tracks signal degradation from the transponder noise floor, subtracting optical signal power attenuated by ROADM ingress/egress connectors, internal port switching losses, and wavelength multiplexer filters. Crucially, the engine maintains Trans-Node NLI Continuity, preserving unamplified fiber lengths across node boundaries to accurately model non-linear phase accumulation.
3. **Power Calibration:** To prevent non-linear performance issues caused by artificially high launch powers, the physics engine enforces strict operating limits matching industrial dense WDM transmission, clamping launch powers into the optimal linear regime.

The top-level evaluation function compares the computed Generalized Signal-to-Noise Ratio (GSNR) against modulation-specific thresholds (e.g., $8.6\text{ dB}$ for 100 Gbps DP-QPSK). This calculation executes deterministically, providing physical validation before any configuration reaches the control plane.

## 4.4.3 Physical RADG Execution Mechanics (Phase 6)

The core validation module governing physical safety is the **Physical RADG**, implemented in `src/nodes/radg_node.py`. Adhering strictly to our architectural methodology, the decision logic is completely devoid of framework dependencies and language model calls.

The gate applies a deterministic decision mapping based on the feasibility array produced by the QoT Calculator:
- **Branch A (Approve):** If at least one candidate lightpath meets or exceeds the required GSNR threshold and optical power budget, the physical risk is certified as zero. Execution transitions directly to Phase 7 (Plan Synthesis) with **zero human intervention**.
- **Branch B (Replan):** If all candidate paths violate physical feasibility (e.g., severe non-linear distortion or excessive attenuation), the system halts. The node invokes the orchestrator's `interrupt()` primitive, suspending execution and presenting the operator with the calculated telemetry. When the operator responds with relaxed parameters (such as lowering the target GSNR), execution resumes and loops back to the parsing phase.

## 4.4.4 Proportional HITL Engagement and Re-Entry Protocols

Previous approaches either risk unverified deployments or interrupt operators for every transaction. Our architecture resolves this dichotomy through **Proportional HITL Engagement**: human operators are engaged if and only if evaluated risk signals exceed acceptable tolerances.

The architecture establishes two strictly decoupled HITL interruption checkpoints:
1. **Semantic Clarification (Phase 3b):** Triggered when semantic uncertainty exceeds the tolerance threshold. Operators can clarify intent or use a fast-track manual override (bypassing re-parsing if the constraints are structurally valid).
2. **Physical Replan (Phase 6):** Triggered when physics calculations fail. Operators must relax constraints or physical margins.

To prevent infinite negotiation loops, the orchestrator bounds the maximum number of clarification turns. If iterations exceed the safety bound, execution terminates with an explicit escalation exception, preventing control-plane deadlocks.
