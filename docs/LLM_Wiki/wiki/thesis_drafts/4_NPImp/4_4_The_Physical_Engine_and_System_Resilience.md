---
title: "Chapter 4 - Section 4.3: The Physical Engine and System Resilience"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, qot, physics-engine, radg, hitl, synthesis, e2e-flows]
status: draft
---

# 4.4 The Physical Engine and System Resilience

## 4.4.1 The Deterministic Symbolic Solver (Phase 4)

Once the intent passes the Semantic RADG, the validated PDDL constraints enter the non-neural Symbolic Solver. This module bridges the linguistic intent and the physical engine by computing feasible paths over the subtopology. 

The solver executes Yen's $K$-Shortest Paths algorithm over the pruned context graph $\widetilde{G}_{sub}$, directly realizing the topological vertex and edge pruning operations formalized in Section~\ref{subsec:symbolic_solver_traversal}. It ensures topological constraints (e.g., node exclusions, link avoidances, and maximum hop limits) are applied before any physical transmission calculations begin. By removing unfeasible topologies early, the solver guarantees that downstream calculations only process valid routing paths.

## 4.4.2 Deterministic GN-Model Physical-Layer Physics Engine (Phase 5)

When candidate lightpaths are extracted by the Symbolic Solver in Phase 4, their transmission feasibility must be verified against the physical optical layer. In our architecture, physical validation is isolated within an analytical software engine implementing the incoherent Gaussian Noise (GN) model derived in Section~\ref{subsec:qot_evaluation}.

The software execution flow traces the continuous optical path across cascading spans and intermediate nodes:
1. **Per-Span Evaluation:** The engine computes Amplified Spontaneous Emission (ASE) noise from EDFAs via Equation~\eqref{eq:ase_noise} and Non-Linear Interference (NLI) distortion via Equation~\eqref{eq:nli_noise}, parameterizing fiber attenuation $\alpha$, chromatic dispersion $D$, and the non-linear Kerr coefficient $\gamma$.
2. **End-to-End Accumulation:** The pipeline tracks signal degradation by accumulating inverse linear SNR contributions across all cascaded links via Equation~\eqref{eq:gsnr_accumulation}. The engine preserves unamplified fiber lengths across node boundaries to accurately model non-linear phase accumulation.
3. **Power Calibration:** To prevent non-linear performance issues, the physics engine enforces operating limits matching industrial dense WDM transmission, keeping launch powers within the optimal linear regime.

The top-level evaluation function compares the computed Generalized Signal-to-Noise Ratio (GSNR) against modulation-specific thresholds ($\text{GSNR}_{th}$). This calculation executes deterministically, providing physical validation before any configuration reaches the control plane.

## 4.4.3 Physical RADG Execution Mechanics (Phase 6)

The Physical RADG evaluates the binary physical feasibility ($\text{QoT}_{valid}$) of the proposed paths, implementing the physical validation component of the decision function established in Section~\ref{subsec:radg_formulation} (Equation~\eqref{eq:radg_decision}):
- **Branch A (Approve):** If at least one candidate lightpath meets or exceeds the required GSNR threshold and optical power budget ($\text{QoT}_{valid} = 1$), the intent resides in Zone I (Auto-Approve / Safe) of the RADG state space (Figure~\ref{fig:radg_decision_space}). In the orchestrator state machine (Figure~\ref{fig:langgraph_execution_flow}), execution transitions along the forward edge directly to Phase 7 (Plan Synthesis) with **zero human intervention**.
- **Branch B (Replan):** If all candidate paths violate physical feasibility ($\text{QoT}_{valid} = 0$), the state maps to Zone II (Suggest Replan). As shown at the Phase 6 checkpoint in Figure~\ref{fig:langgraph_execution_flow}, the node invokes an interrupt, suspending execution and presenting the operator with the calculated telemetry. When the operator responds with relaxed parameters (such as lowering the target GSNR), execution resumes and loops back to Phase 2 along the feedback edge.

## 4.4.4 Proportional HITL Engagement and Re-Entry Protocols

Our architecture establishes a **Proportional HITL Engagement** model: human operators are engaged if and only if evaluated risk signals exceed acceptable tolerances. This mitigates cognitive overload while guaranteeing that physically infeasible configurations are blocked before deployment.

The architecture establishes two strictly decoupled HITL interruption checkpoints, visible as the two suspension barriers in the execution flow of Figure~\ref{fig:langgraph_execution_flow}:
1. **Semantic Clarification (Phase 3b):** Triggered when semantic uncertainty exceeds the tolerance threshold ($U_{sem} > \tau_{sem}$). Operators can clarify intent or use a fast-track manual override (bypassing re-parsing if the constraints are structurally valid).
2. **Physical Replan (Phase 6):** Triggered when physics calculations fail ($\text{QoT}_{valid} = 0$). Operators must relax constraints or physical margins.

To prevent infinite negotiation loops, the orchestrator bounds the maximum number of clarification turns to $N_{max} = 3$ and enforces the formal Constraint Preservation condition formalized in Equation~\eqref{eq:constraint_preservation}. If iterations exceed the safety bound, execution terminates with an explicit escalation exception, preventing control-plane deadlocks.

Once candidate paths are verified, Section~\ref{sec:plan_synthesis_verification} presents Phase 7 (Plan Synthesis) and the validation of the orchestrator across seven operational test scenarios.
