---
title: "Problem Statement V5: LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks"
date: 2026-07-17
tags: [thesis, definition, objective, planning-loop, hitl, neurosymbolic, pddl, risk-adaptive, qot, evaluation]
status: active
supersedes: "[[architecture/archive/ProblemStatement_v4]]"
---

# Problem Statement V5: LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks

## 1. Context

- **Thesis Title:** LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment.
- **Keywords:** Generative AI, Intent-Based Networking, Quality of Transmission (QoT), Human-in-the-Loop (HITL), Neurosymbolic AI, PDDL, Risk-Adaptive Decision, Semantic Uncertainty, Pre-Deployment Validation.
- **Academic Setting:** Master's thesis in Telecommunications Engineering, conducted in collaboration with the Software-Defined Optical Networking (SDON) research laboratory.

## 2. The Problem

The translation of high-level operator intent into physical optical network configurations is severely bottlenecked by five interconnected challenges:

1. **Token Budget Saturation.** Injecting massive optical topologies (RESTConf JSON payloads) into LLM context windows causes attention degradation — the "lost-in-the-middle" phenomenon — leading to missed constraints and inflated inference costs.

2. **Hallucinated Physics.** LLMs are probabilistic text generators; they do not natively respect nonlinear optical constraints such as Generalized Signal-to-Noise Ratio (GSNR) margins or Stimulated Raman Scattering. Allowing an LLM to heuristically propose lightpaths produces structurally invalid and physically infeasible routes.

3. **Semantic Drift in HITL Refinement.** Unstructured conversational loops for intent refinement lack convergence guarantees. A correction in one turn may cause the LLM to inadvertently drop constraints from prior turns, creating an infinite loop of unverified plan states.

4. **Reactive Post-Deployment Verification.** Existing LLM-based networking systems rely on **heuristic trial-and-error loops after a deployment failure**: the system generates a configuration, deploys it, observes a controller error, and retries. This reactive pattern allows physically infeasible or unsafe configurations to reach the network controller before any corrective action is taken.

5. **Suboptimal HITL Engagement.** Current systems offer only two extremes: **always-on HITL** (every intent requires human review, creating bottlenecks and operator fatigue) or **no HITL** (fully autonomous, risking unsafe approvals). There is no mechanism to engage the human operator **proportionally to the assessed risk** of a given intent.

## 3. The Fundamental Gap

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
Binary check: $\text{GSNR}_{computed} \ge \text{GSNR}_{threshold} \land P_{rx} \ge P_{rx, min}$

Assuming $U_{sem}$ is low (resolved in the earlier gate), the physical gate maps to two outcomes:

| Decision | Condition | Action |
|----------|-----------|--------|
| **Auto-Approve** | Valid (Feasible) | Deploy without human review |
| **Suggest Replan** | Invalid (Unfeasible) | Physics failed. Notify operator and suggest relaxing constraints via HITL (loops back to Phase 2) |

### 4.3 Formalizing the Risk-Adaptive Decision Gate (RADG)

The RADG is formulated as a piecewise decision function $D$ that evaluates two constraints sequentially:

1. **Semantic Uncertainty ($U_{sem}$):** A function of structural validity ($v_{struct} \in \{0, 1\}$) and semantic divergence ($d_{sem} \in [0, 1]$).
   $$U_{sem} = \begin{cases} 1 & \text{if } v_{struct} = 0 \text{ (Structural Failure)} \\ d_{sem} & \text{if } v_{struct} = 1 \text{ (Semantic Divergence)} \end{cases}$$
   Given a tolerance threshold $\tau_{sem}$, if $U_{sem} > \tau_{sem}$, the intent is considered ambiguous.

2. **Physical Viability ($QoT_{valid}$):** A binary indicator based on deterministic physics:
   $$QoT_{valid} = \mathbb{I}(\text{GSNR}_{computed} \ge \text{GSNR}_{threshold} \land P_{rx} \ge P_{rx, min})$$

The decision function maps the state to an action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$:

$$D(U_{sem}, \text{QoT}_{valid}) = \begin{cases} \text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ \text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ \text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 \end{cases}$$

This formalization enforces the **pre-deployment fail-fast** mechanism.

## 5. Given

The planning system receives:
1. **The Natural Language Intent.** A high-level, unstructured semantic request from a human operator (e.g., "Route traffic from Hamburg to Munich with at least 15 dB GSNR, avoiding Frankfurt").
2. **The Physical Network Graph $G(V,E)$.** Extracted from the SDON testbed via RESTConf/SSH.
3. **QoT Physical Parameters.** Fiber attenuation coefficients, optical amplifier gains, and channel configurations for deterministic GN-model computation.

## 6. Output

The output of the pipeline is a validated **Planning Report** containing:
- **Structurally Valid Paths** with verified QoT feasibility scores ($\text{GSNR}_{dB}$, $P_{rx,dBm}$, $\text{QoT}_{valid}$).
- **PDDL Constraint Map** guaranteeing the logic applied to the path search.
- **RADG Decision Trace** — the risk assessment that led to the final decision (approve/clarify/replan), including $U_{sem}$ and $\text{QoT}_{valid}$ values.
- **Reverse Prompting Trace** (when applicable) — the formal conversation history documenting the operator's agreement to the plan.
- **Approved Routing Decision** — ready to be pushed to the SDON testbed.

## 7. The Optimization Objective

The objective of the LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning system is **not** to "maximize safety" (as physical safety is non-negotiable in optical networks), but rather to **minimize operational and computational friction** subject to strict safety constraints.

$$\min_{\text{plan}} \Big( \alpha \cdot N_{hitl}(\text{plan}) + \beta \cdot T_{tokens}(\text{plan}) \Big)$$

$$\text{subject to:} \quad D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$$

Where:
- $N_{hitl}(\text{plan})$ is the number of human-in-the-loop interruptions (operational friction).
- $T_{tokens}(\text{plan})$ is the LLM token consumption (computational friction).
- $\alpha, \beta$ are weighting coefficients for human time vs. API cost.
- $D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$ is the strict hard constraint guaranteeing that the plan satisfies both the semantic threshold ($\tau_{sem}$) and the physical physics threshold ($\text{GSNR}_{threshold}$) before deployment.

## 8. Evaluation Framework

### 8.1 Comparative Baselines

| Baseline | Architecture | Operational Mode | Evaluation Role |
|----------|--------------|------------------|-----------------|
| **Baseline A (LLM-Only)** | Monolithic LLM (Direct NL $\to$ JSON/CLI) | Unconstrained autonomous execution with reactive post-deployment retry | Evaluates failure modes: hallucinated physics, attention degradation, and high recovery latency |
| **Baseline B (Static Rule-Based)** | Deterministic regex / CFG parser | Always-on human review (mandatory human validation on every intent) | Evaluates operational friction: operator fatigue, low expressiveness, and configuration rigidity |
| **Baseline C (Traditional SDON)** | Non-LLM imperative YANG / RESTCONF RPC + PCE | Manual payload authoring by expert operator + deterministic Yen's $K$-SP / GN-model | Evaluates industrial baseline: zero NL translation error, absolute safety ($UAR=0\%$), but high human friction ($N_{human}$) and zero ambiguity tolerance |
| **Proposed (Neurosymbolic RADG)** | Decoupled LangGraph pipeline (LLM translator + Yen's $K$-SP + GN-model) | Pre-deployment sequential risk gates ($U_{sem} \to \text{QoT}_{valid}$) with selective HITL | Evaluates proposed thesis hypothesis: pre-deployment safety ($UAR = 0\%$) with minimal operational friction and high NL expressiveness |

### 8.2 The Four Core Validation Pillars & Performance Metrics

To ensure a rigorous, multidimensional assessment beyond mere latency and token counting, the system is evaluated across four orthogonal validation pillars:

#### Pillar 1: Semantic Translation Accuracy (Neural Domain Fidelity)
- **Objective:** Validate that the neural subsystem faithfully translates unstructured operator intent into formal PDDL constraints without dropping restrictions or inventing network primitives.
- **Metrics:**
  - **Constraint Retention Rate (CRR):** Percentage of explicit intent constraints (e.g., node/link exclusions, latency limits) correctly preserved in the synthesized PDDL specification. Target: $100\%$.
  - **Context-Free Grammar Pass Rate (CFG-PR):** Fraction of generated PDDL ASTs that pass deterministic grammar validation ($v_{struct} \in \{0, 1\}$).
  - **Semantic Agreement Score ($1 - d_{sem}$):** Discrepancy metric computed between original intent $\mathcal{I}_{NL}$ and reverse-prompted reconstruction $\mathcal{I}_{recon}$.

#### Pillar 2: Physical Feasibility (Optical Layer Integrity)
- **Objective:** Guarantee that all approved lightpaths strictly satisfy physical-layer transmission impairments (non-linearities, dispersion, ASE noise) before touching the network controller.
- **Metrics:**
  - **Unsafe Approval Rate (UAR):** Fraction of intents producing physically infeasible lightpaths ($\text{GSNR} < \text{GSNR}_{th}$ or $P_{rx} < P_{rx,min}$) that receive an `approve` verdict. Hard Target: **$0\%$ (Absolute Safety Invariant)**.
  - **QoT Feasibility Rate (QFR):** Fraction of deployed lightpaths that satisfy required transmission margins under analytical GN-model validation. Target: **$100\%$**.
  - **Physical Infeasibility Interception Rate (PIIR):** Fraction of demands requesting physically impossible optical reaches that are successfully flagged for replanning rather than deployed. Target: **$100\%$**.

#### Pillar 3: Orchestration & Resource Efficiency (Computational & Operational Friction)
- **Objective:** Quantify computational savings in prompt tokens and runtime, alongside operator fatigue reduction through selective human engagement.
- **Metrics:**
  - **Prompt Token Reduction ($\Delta T_{tokens}$):** Percentage of input tokens eliminated by Scoped GraphRAG ($G_{sub} \subseteq G$) compared to full-topology JSON injection. Target: $> 75\%$.
  - **Human Intervention Reduction ($\Delta N_{hitl}$):** Reduction in operator interruptions compared to the Always-HITL baseline ($1 - \frac{N_{hitl,\text{ours}}}{N_{hitl,\text{always}}}$). Target: $> 70\%$.
  - **Sub-Second Deterministic Compute Latency ($T_{det}$):** Wall-clock execution time of symbolic routing ($T_{solver} < 10\text{ ms}$) and GN-model physics ($T_{phys} < 5\text{ ms}$).
  - **End-to-End Orchestration Latency ($T_{E2E}$):** Total wall-clock turnaround from NL submission to final planning report.

#### Pillar 4: RADG Robustness & Decision Boundary Integrity (Gate Reliability)
- **Objective:** Stress-test the piecewise decision function $\mathcal{D}(U_{sem}, \text{QoT}_{valid})$ across boundary conditions, verifying accurate classification into `approve`, `clarify`, and `replan`.
- **Metrics:**
  - **Gate Decision Accuracy (GDA):** Overall accuracy of the RADG in routing intents to the optimal action state according to ground-truth risk profiles. Target: $> 98\%$.
  - **False Positive Rate ($\text{FPR}$):** Probability of issuing an `approve` decision given an unfeasible or ambiguous intent. Target: **$0\%$**.
  - **Selective HITL Precision:** Fraction of human interruptions that correctly target ambiguous intents requiring genuine operator clarification rather than false alarms.

### 8.3 Benchmark Corpus: 100 Test Demands (4 Risk Classes)

The evaluation suite executes on the standardized **17-Node Nobel-Germany Core Backbone Topology** ($|V| = 17, |E| = 26$ bidirectional SMF-28 links, dual-stage EDFAs, span lengths $L \in [45, 350]\text{ km}$), balanced across four equal cohorts (25 demands each):

| Class | Intent Category | Sample Size | Intent Characteristics | Expected RADG Action | Target Outcome |
|:-----:|-----------------|:-----------:|------------------------|:---------------------:|:--------------:|
| **I** | **Nominal Intents** | 25 | Unambiguous source-destination requests with feasible physical paths | Auto-Approve | Zero human intervention, $U_{sem} \le \tau_{sem}$, $\text{QoT}_{valid} = 1$ |
| **II** | **Ambiguous Intents** | 25 | Under-specified constraints, missing endpoints, or underspecified SLAs | Clarify Intent | Early fail-fast pause in Phase 3b via `interrupt()`, $U_{sem} > \tau_{sem}$ |
| **III** | **Physically Infeasible** | 25 | Demands requiring unachievable GSNR targets over ultra-long unregenerated reaches | Suggest Replan | Intercepted in Phase 6, $\text{QoT}_{valid} = 0$, human invited to relax constraints |
| **IV** | **Adversarial Prompts** | 25 | Hallucinated node names, syntax injection, or contradictory topological constraints | Reject / Clarify | Intercepted by Layer 1 CFG validator ($v_{struct} = 0 \to U_{sem} = 1.0$) |

## 9. Cross-References

- [[Scope_Pivot_20260706]] — Architectural evolution from V2 through V5.
- [[Architecture_v5]] — System architecture mapping for the risk-adaptive neurosymbolic pipeline.
- [[experiments/MVP_Roadmap]] — Sprint plan and experimental roadmap.
- [[literature/sota_gap_analysis]] — Gap analysis positioning against SOTA.
