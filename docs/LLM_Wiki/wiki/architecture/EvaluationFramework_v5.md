---
title: "Evaluation Framework V5"
date: 2026-09-18
tags: [architecture, evaluation, metrics, v5]
status: active
---

# Validation and Evaluation Framework

This document outlines the theoretical evaluation metrics and baselines used to validate the LLM-Assisted Risk-Adaptive Decision Gates architecture. For execution instructions and test corpus details, refer to the [Evaluation Benchmark Guide](../../../../../tests/evaluation/README.md).

### 8.1 Comparative Baselines

| Baseline | Architecture | Operational Mode | Evaluation Role |
|----------|--------------|------------------|-----------------|
| **Baseline A (Monolithic LLM)** | Direct Prompting (NL $\to$ JSON/CLI) | Unconstrained autonomous execution with zero deterministic tools | Evaluates neural failure modes: hallucinated physics, topological invalidity, and high $UAR$ |
| **Baseline B (Always-On HITL)** | Full Neurosymbolic Pipeline | Mandatory human review at Phase 3b and Phase 6 for every intent | Evaluates operational friction: operator fatigue ($N_{hitl} = 100\%$), inflated token cost, and execution latency |
| **Baseline C (Always-Off HITL)** | Full Neurosymbolic Pipeline | Autonomous execution with decision gates bypassed (no HITL) | Evaluates safety failure modes: unhandled ambiguity, high service blocking, and deployment of unfeasible paths |
| **Baseline D (Traditional SDON)** | Non-LLM imperative YANG / RESTCONF RPC + PCE | Manual payload authoring by expert operator + deterministic Yen's $K$-SP / GN-model | Evaluates industrial standard: zero NL translation error, absolute safety ($UAR=0\%$), but $100\%$ human setup effort |
| **Proposed (Neurosymbolic RADG)** | Decoupled LangGraph pipeline (LLM translator + Yen's $K$-SP + GN-model) | Pre-deployment sequential risk gates ($U_{sem} \to \text{QoT}_{valid}$) with selective HITL | Evaluates proposed thesis hypothesis: pre-deployment safety ($UAR = 0\%$) with minimal operational friction ($N_{hitl} \le 1$) and high NL expressiveness |

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
  - **Unfeasible Approval Rate (UAR):** Fraction of intents producing physically infeasible lightpaths ($\text{GSNR} < \text{GSNR}_{th}$ or $P_{rx} < P_{rx,min}$) that receive an `approve` verdict. Hard Target: **$0\%$ (Absolute Safety Invariant)**.
  - **QoT Feasibility Rate (QFR):** Fraction of deployed lightpaths that satisfy required transmission margins under analytical GN-model validation. Target: **$100\%$**.
  - **Physical Infeasibility Interception Rate (PIIR):** Fraction of demands requesting physically impossible optical reaches that are successfully flagged for replanning rather than deployed. Target: **$100\%$**.

#### Pillar 3: Orchestration & Resource Efficiency (Computational & Operational Friction)
- **Objective:** Quantify computational savings in prompt tokens and runtime, alongside operator fatigue reduction through selective human engagement.
- **Metrics:**
  - **Prompt Token Reduction ($\Delta T_{tokens}$):** Percentage of input tokens eliminated by Neurosymbolic Context Bounding ($G_{sub} \subseteq G$) compared to monolithic full-topology JSON injection. Target: $> 75\%$.
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
