---
title: "Problem Statement V5: Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks"
date: 2026-07-17
tags: [thesis, definition, objective, planning-loop, hitl, neurosymbolic, pddl, risk-adaptive, qot, evaluation]
status: active
supersedes: "[[archive/ProblemStatement_v4]]"
---

# Problem Statement V5: Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks

## 1. Context

- **Thesis Title:** Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment.
- **Keywords:** Generative AI, Intent-Based Networking, Quality of Transmission (QoT), Human-in-the-Loop (HITL), Neurosymbolic AI, PDDL, Risk-Adaptive Decision, Semantic Uncertainty, Pre-Deployment Validation.
- **Academic Setting:** Master's thesis in Telecommunications Engineering, conducted in collaboration with the Software-Defined Optical Networking (SDON) research laboratory.

## 2. The Problem

The translation of high-level operator intent into physical optical network configurations is severely bottlenecked by five interconnected challenges:

1. **Token Budget Saturation.** Injecting massive optical topologies (RESTConf JSON payloads) into LLM context windows causes attention degradation — the "lost-in-the-middle" phenomenon — leading to missed constraints and inflated inference costs.

2. **Hallucinated Physics.** LLMs are probabilistic text generators; they do not natively respect nonlinear optical constraints such as Generalized Signal-to-Noise Ratio (GSNR) margins or Stimulated Raman Scattering. Allowing an LLM to heuristically propose lightpaths produces structurally invalid and physically infeasible routes.

3. **Semantic Drift in HITL Refinement.** Unstructured conversational loops for intent refinement lack convergence guarantees. A correction in one turn may cause the LLM to inadvertently drop constraints from prior turns, creating an infinite loop of unverified plan states.

4. **Post-Deployment Failure Discovery.** Existing LLM-based networking systems (e.g., El Hachimi et al., CNSM 2025) rely on **fixed retry loops after deployment failure**: the system generates a configuration, deploys it, observes a controller error, and retries. This reactive pattern allows physically infeasible or unsafe configurations to reach the network controller before any corrective action is taken.

5. **Suboptimal HITL Engagement.** Current systems offer only two extremes: **always-on HITL** (every intent requires human review, creating bottlenecks and operator fatigue) or **no HITL** (fully autonomous, risking unsafe approvals). There is no mechanism to engage the human operator **proportionally to the assessed risk** of a given intent.

## 3. Prior Art and Its Limitations

| System | HITL Strategy | When Applied | Key Limitation |
|--------|--------------|--------------|----------------|
| **PoliMi/CNSM 2025** (El Hachimi et al.) | Fixed retry after controller deployment failure | Post-deployment | Reactive; deploys unsafe configs first, then retries up to N times |
| **Confucius** (Meta, SIGCOMM 2025) | Collector primitive for structured Q&A | Pre-execution | No optical physical-layer awareness; no QoT |
| **AutoLight** (SJTU, ECOC 2025) | None — pre-defined task sequences | Pre-execution | No operator validation; no risk assessment |
| **IntentLLM** | None — single-pass chatbot | N/A | No multi-agent coordination; no QoT |

**The fundamental gap:** No existing system combines **semantic uncertainty assessment** (did the LLM correctly understand the intent?) with **physical-layer QoT risk evaluation** (is the proposed lightpath physically feasible?) into a **fail-fast, sequential pre-deployment decision** that adaptively determines the appropriate corrective action without wasting computation.

## 4. The Proposed Solution

A **Neurosymbolic Intent Planning Pipeline** with a **Risk-Adaptive Decision Pipeline** that sequentially evaluates two orthogonal risk signals **before deployment** to determine the appropriate action for each intent.

### 4.1 Neurosymbolic Pipeline

The pipeline enforces a strict "LLMs reason, tools calculate" separation:

1. **Intent Ingestion + Optical RAG.** The natural language request is semantically enriched with domain standards (e.g., ITU-T specifications, transponder data) before LLM processing.
2. **PDDL Intent Parsing.** The LLM translates the enriched intent into formal PDDL constraints.
3. **Semantic Uncertainty Gate ($U_{sem}$).** Before complex computation, the system checks structural (CFG) and semantic (Reverse Prompting) validity. If uncertainty is high, it immediately requests the operator to clarify missing data.
4. **Symbolic Solver + GraphRAG.** A Python-based symbolic solver fetches only the necessary $k$-hop sub-graph from the topology (Mock GraphRAG) and extracts 3–5 structurally valid candidate paths.
5. **QoT Validation.** Candidate paths are evaluated by a deterministic Python QoT Tool (GN-model port) to compute precise GSNR and receiver power feasibility.
6. **Physical Risk Gate.** Evaluates the binary QoT feasibility to decide if the plan should be auto-approved or if the operator must be engaged to relax constraints via HITL.

### 4.2 Risk-Adaptive Decision Pipeline

The system acts upon two orthogonal risk signals in a sequential, fail-fast manner:

- **$U_{sem}$: Semantic Uncertainty (Evaluated Early).**
  - *Layer 1 (Structural)*: Binary pass/fail from the CFG PDDL validator — catches gross hallucinations.
  - *Layer 2 (Semantic)*: Disagreement score between the original operator intent and the Reverse Prompting natural language reconstruction. High $U_{sem}$ triggers early **Clarify** (HITL).

- **QoT Feasibility (Evaluated Later).** 
Binary check: $\text{GSNR}_{computed} \ge \text{GSNR}_{threshold}$

Assuming $U_{sem}$ is low (resolved in the earlier gate), the physical gate maps to two outcomes:

| Decision | Condition | Action |
|----------|-----------|--------|
| **Auto-Approve** | Valid (Feasible) | Deploy without human review |
| **Suggest Replan** | Invalid (Unfeasible) | Physics failed. Notify operator and suggest relaxing constraints via HITL (loops back to Phase 2) |

### 4.3 Decision Function

The risk-adaptive pipeline acts as a composed decision function:

$$D(U_{sem}, \text{QoT}_{valid}) \to \{\text{approve}, \text{clarify}, \text{replan}\}$$

This sequential approach is the **core novelty**: it is **pre-deployment** (no unsafe configuration reaches the network), **fail-fast** (avoids expensive compute on ambiguous intents), and **risk-proportional** (the human is engaged only when needed to resolve missing data or unfeasible physics).

## 5. Given

The planning system receives:
1. **The Natural Language Intent.** A high-level, unstructured semantic request from a human operator (e.g., "Route traffic from Milan to Rome with at least 20 dB GSNR, avoiding link L3").
2. **The Physical Network Graph $G(V,E)$.** Extracted from the SDON testbed via RESTConf/SSH.
3. **QoT Physical Parameters.** Fiber attenuation coefficients, optical amplifier gains, and channel configurations for deterministic GN-model computation.

## 6. Output

The output of the pipeline is a validated **Planning Report** containing:
- **Structurally Valid Paths** with verified QoT feasibility scores ($\text{GSNR}_{dB}$, $P_{rx,dBm}$, $R_{qot}$).
- **PDDL Constraint Map** guaranteeing the logic applied to the path search.
- **RADG Decision Trace** — the risk assessment that led to the final decision (approve/clarify/replan), including $U_{sem}$ and $R_{qot}$ values.
- **Reverse Prompting Trace** (when applicable) — the formal conversation history documenting the operator's agreement to the plan.
- **Approved Routing Decision** — ready to be pushed to the SDON testbed.

## 7. Objective

The objective of the Risk-Adaptive Neurosymbolic Intent Planning system is to maximize planning safety and efficiency while minimizing unnecessary human intervention:

$$\max_{\text{plan}} \Big( F_{intent}(\text{plan}) \cdot Q_{qot}(\text{plan}) \cdot S_{risk}(\text{plan}) \Big)$$

$$\text{subject to} \quad \text{UAR} = 0, \quad N_{hitl} \le N_{adaptive}, \quad T_{tokens} \le T_{max}$$

Where:
- $F_{intent}(\text{plan})$ is the intent fidelity, bounded by Reverse Prompting and semantic similarity.
- $Q_{qot}(\text{plan})$ is the QoT physical quality verified by the GN-model tool.
- $S_{risk}(\text{plan})$ is the safety score from the RADG — penalizing plans that bypass risk assessment.
- $\text{UAR}$ is the Unsafe Approval Rate (target: 0%).
- $N_{adaptive}$ is the risk-proportional HITL interaction count (strictly less than always-on HITL).
- $T_{max}$ is the bounded context window protected by Optical GraphRAG.

## 8. Evaluation Framework

### 8.1 Baselines

| Baseline | Description |
|----------|-------------|
| **No-HITL** | System runs end-to-end without any human check. Measures the risk of fully autonomous operation. |
| **Always-HITL** | Every intent triggers mandatory human review via Reverse Prompting. Measures the cost of maximum safety. |
| **Fixed-Retry** (à la PoliMi/CNSM 2025) | System generates config, deploys, observes failure, retries up to N times. Measures post-deployment correction. |
| **Risk-Adaptive HITL (Ours)** | RADG decides when and how to involve the human based on joint $U_{sem}$ and $R_{qot}$. |

### 8.2 Evaluation Metrics

| Metric | Symbol | Definition | Target |
|--------|--------|------------|--------|
| **Unsafe Approval Rate** | UAR | Fraction of intents that produce physically infeasible lightpaths approved for deployment | 0% |
| **Human Interaction Count** | HIC | Number of operator interruptions per intent | Lower than Always-HITL |
| **QoT Feasibility Rate** | QFR | Fraction of final plans that pass QoT validation | 100% |
| **End-to-End Latency** | E2EL | Wall-clock time from intent submission to final plan approval | Competitive |
| **Token Cost** | TC | Total LLM tokens consumed per intent | Lower than No-HITL retries |

### 8.3 Test Corpus

A structured set of 20–30 synthetic operator intents spanning three risk categories:
- **Safe + Clear**: Unambiguous intents with valid QoT → expected: auto-approve.
- **Ambiguous**: Intents with missing or contradictory constraints → expected: clarify early.
- **Infeasible QoT**: Well-specified intents that violate physical constraints → expected: suggest replan (relax constraints).

## 9. Cross-References

- [[Scope_Pivot_20260706]] — Architectural evolution from V2 through V5.
- [[Architecture_v5]] — System architecture mapping for the risk-adaptive neurosymbolic pipeline.
- [[experiments/MVP_Roadmap]] — Sprint plan and experimental roadmap.
- [[literature/sota_gap_analysis]] — Gap analysis positioning against SOTA.
