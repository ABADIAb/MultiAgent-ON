---
title: "Chapter 4 - Section 4.3: The Physical Engine and System Resilience"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, qot, physics-engine, radg, hitl, synthesis, e2e-flows]
status: draft
---

# 4.3 The Physical Engine and System Resilience

## 4.3.1 Deterministic GN-Model Physical-Layer Physics Engine

When candidate lightpaths are extracted by the symbolic solver in Phase 4 (utilizing Yen's $K$-Shortest Paths with topological constraint pruning), their transmission feasibility must be verified against the physical optical layer. Delegating this verification to an LLM introduces hallucinated physics. In our architecture, physical validation is strictly isolated within the **QoT Calculator** (`src/core/qot_calculator.py`), an analytical software engine implementing the incoherent Gaussian Noise (GN) model.

The software execution flow traces the continuous optical path across cascading spans and intermediate nodes:
1. **Per-Span Evaluation:** The engine computes the non-linear interference constant $\eta_0$ based on physical fiber parameters (attenuation, Kerr coefficient, dispersion). For each span, it calculates Amplified Spontaneous Emission (ASE) noise from EDFAs and non-linear distortion.
2. **End-to-End Accumulation:** The pipeline tracks signal degradation from the transponder noise floor, subtracting optical signal power attenuated by ROADM ingress/egress connectors, internal port switching losses, and wavelength multiplexer filters. Crucially, the engine maintains Trans-Node NLI Continuity, preserving unamplified fiber lengths across node boundaries to accurately model non-linear phase accumulation.
3. **Power Calibration:** To prevent non-linear performance explosions caused by artificially high launch powers, the physics engine enforces strict operating limits matching industrial dense WDM transmission, clamping launch powers into the optimal linear regime.

The top-level evaluation function compares the computed Generalized Signal-to-Noise Ratio (GSNR) against modulation-specific thresholds (e.g., $8.6\text{ dB}$ for 100 Gbps DP-QPSK, $15.2\text{ dB}$ for 200 Gbps DP-16QAM). This calculation executes in under $1.5\text{ ms}$ per candidate path, providing deterministic physical validation before any configuration reaches the control plane.

---

## 4.3.2 Physical RADG Execution Mechanics

The core pre-deployment validation module governing physical safety is the **Physical RADG**, implemented in `src/nodes/radg_node.py`. Adhering strictly to our architectural methodology, the decision logic is completely devoid of framework dependencies and language model calls.

The gate applies a deterministic decision mapping based on the feasibility array produced by the QoT Calculator:
- **Branch A (Approve):** If at least one candidate lightpath meets or exceeds the required GSNR threshold and optical power budget, the physical risk is certified as zero. Execution transitions directly to Phase 7 (Plan Synthesis) with **zero human intervention**.
- **Branch B (Replan):** If all candidate paths violate physical feasibility (e.g., severe non-linear distortion over long-haul multi-span distances, or excessive attenuation across degraded fiber links), the system halts. The node invokes the orchestrator's interrupt primitive, suspending execution and presenting the operator with the calculated telemetry. When the operator responds with relaxed parameters (such as lowering the target GSNR or changing the bitrate), execution resumes and loops back to the parsing phase.

---

## 4.3.3 Human-in-the-Loop Interaction and Re-Entry Protocols

Existing literature exhibits a polarization between fully autonomous systems that risk unfeasible deployments and rigid frameworks that interrupt operators for every transaction. Our architecture resolves this dichotomy through **Proportional HITL Engagement**: human operators are engaged if and only if evaluated risk signals exceed acceptable tolerances.

The architecture establishes two strictly decoupled HITL interruption checkpoints:
1. **Semantic Clarification (Phase 3b):** Triggered when semantic uncertainty exceeds the tolerance threshold. Operators can clarify intent or use a fast-track manual override (bypassing re-parsing if the constraints are structurally valid).
2. **Physical Replan (Phase 6):** Triggered when physics calculations fail. Operators must relax constraints or physical margins.

To prevent infinite negotiation loops commonly found in conversational AI, the orchestrator bounds the maximum number of clarification turns. If iterations exceed the safety bound, execution terminates with an explicit escalation exception, preventing control-plane deadlocks.

---


