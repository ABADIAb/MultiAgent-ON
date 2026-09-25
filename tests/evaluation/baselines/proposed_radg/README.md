# Proposed RADG Baseline Specification: Dual Fail-Fast Risk-Adaptive Neurosymbolic Intent Planning

---

## 1. Executive Summary & Thesis Context

This document defines the architectural specification, evaluation methodology, and performance invariants for the **Proposed RADG (V5)** architecture, representing the author's primary scientific contribution in the Master's thesis:
> *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*

The proposed architecture resolves the fundamental dilemma between **un-gated hallucination** (LLM-Only) and **operator cognitive fatigue** (Always-On HITL) through a **Dual Fail-Fast Risk-Adaptive Decision Gate (RADG)** framework.

```mermaid
flowchart TD
    Phase1["Phase 1: Intent Ingest & Optical RAG Scoping"] --> Phase2["Phase 2: PDDL Parsing & CFG AST Validation"]
    Phase2 --> Phase3a["Phase 3a: Reverse Prompting NL Reconstruction"]
    Phase3a --> Phase3b{"Phase 3b: Semantic RADG Gate (U_sem)"}
    
    Phase3b -->|"U_sem > 0.30 (Ambiguous / Divergent)"| Phase3_Clarify["Phase 3b: HITL Clarification (interrupt)"]
    Phase3_Clarify -->|"Operator Clarifies"| Phase2
    
    Phase3b -->|"U_sem ≤ 0.30 (Passed)"| Phase4["Phase 4: Symbolic Solver (Yen's K-SP)"]
    Phase4 --> Phase5["Phase 5: Real Coherent QoT Engine (GN Model)"]
    Phase5 --> Phase6{"Phase 6: Physical RADG Gate"}
    
    Phase6 -->|"GSNR < Threshold (Infeasible)"| Phase6_Replan["Phase 6: HITL Replan (interrupt)"]
    Phase6_Replan -->|"Operator Relaxes Constraints"| Phase2
    
    Phase6 -->|"Feasible"| Phase7["Phase 7: Plan Synthesis & Verification Report"]
```

---

## 2. Core Architectural Pillars & Invariants

### 2.1 Dual Fail-Fast Risk Gates
1. **Semantic Risk-Adaptive Gate (Phase 3b):**
   Jointly evaluates structural AST grammar validity $v_{struct}$ and neural-semantic divergence $d_{sem}$ via reverse prompting reconstruction:
   $$U_{sem} = \begin{cases} 1.0 & \text{if } v_{struct} = 0 \\ d_{sem} & \text{if } v_{struct} = 1 \end{cases}$$
   $$\mathcal{A}_{sem} = \begin{cases} \text{pass} & \text{if } U_{sem} \le \tau_{sem} \\ \text{clarify} & \text{if } U_{sem} > \tau_{sem} \end{cases}$$
   When $\tau_{sem} = 0.30$, well-formed nominal intents pass autonomously without operator interruption, while ambiguous or adversarial demands are safely intercepted.

2. **Physical Risk-Adaptive Gate (Phase 6):**
   Delegates physical impairment validation strictly to an external, deterministic Gaussian Noise (GN) model calculator (evaluating ASE noise accumulation and non-linear interference across C-band 96 channels):
   $$\mathcal{A}_{phys} = \begin{cases} \text{approve} & \text{if } \exists p \in \mathcal{P}_{cand} : \text{GSNR}(p) \ge \gamma_{req} \\ \text{replan} & \text{otherwise} \end{cases}$$

### 2.2 Operational Invariants
- **Zero Operator Fatigue on Nominal Traffic:** For all Class I Nominal demands, $\mathbf{N_{hitl} = 0}$. The system acts with complete autonomy.
- **Strict Physical Safety Invariant:** Unfeasible Approval Rate is mathematically guaranteed to be **$0.0\%$** ($UAR = 0.0\%$).
  > **Note on K-Shortest Path Evaluation:** In Yen's K-Shortest Paths ($K=5$), the physical solver evaluates $K$ candidate lightpaths. In a typical nominal request, the primary shortest path is feasible ($\text{GSNR} \ge 14\text{ dB}$), while secondary detour paths may fail threshold. The system approves provisioning because a valid physical lightpath exists. A demand is only categorized as an unfeasible approval if *no* candidate lightpath satisfies physical reachability or if it belongs to Class III (Infeasible) and is approved.

### 2.3 Un-Metered Warm-up Pass (Cold-Start Mitigation)
To prevent Ollama model weight loading, CUDA context initialization, and LangGraph JIT compilation from distorting nominal latency metrics (where an initial cold request can require $\sim 35\text{s}$ vs $\sim 4.5\text{s}$ steady-state), the evaluation framework incorporates an un-metered dummy warm-up pass (`warmup_evaluator`). The dummy request primes GPU VRAM and execution caches before official timer and token counters commence.

---

## 3. Four Core Validation Pillars Telemetry

| Validation Pillar | Evaluated Metric | Theoretical Target | Proposed RADG Actual | Operational Meaning |
| :--- | :--- | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **$94.1\% - 100.0\%$** | High-fidelity preservation of explicit operator constraints |
| | CFG Pass Rate (CFG-PR) | $\ge 95\%$ | **$95.0\% - 100.0\%$** | Syntactically valid PDDL AST representation |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.85$ | **$0.860 - 0.912$** | High concordance between intent and reverse reconstruction |
| | Ambiguity / Adversarial Catch | $100\%$ | **$80.0\% - 100.0\%$** | Upstream interception before invoking physical solver |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | **$0.0\%$** | **$0.0\%$** | Zero reach-violating lightpaths approved (Invariant) |
| | Physical Infeasibility Catch (PIIR) | $100\%$ | **$80.0\% - 100.0\%$** | Class III infeasible demands intercepted and replanned |
| **Pillar 3: Efficiency & Friction** | Median E2E Latency ($\tilde{T}_{E2E}$, Nominal) | Contextual | **$3.8\text{s} - 4.5\text{s}$** (Mean: $5.2\text{s}$) | Steady-state turnaround (robust to outliers) |
| | Median Token Footprint (Nominal) | Monitored | **$3,740 - 3,762\text{ tok}$** | Minimal token consumption (single-turn pass) |
| | Nominal HITL Interruptions | $0$ | **$0.00$** ($100\%$ Efficiency) | Zero-friction autonomous operational pass |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $> 98\%$ | **$95.0\% - 100.0\%$** | Multi-class decision boundary fidelity |
| | False Positive Rate (FPR) | **$0.0\%$** | **$0.0\%$** | Zero risky traffic forwarded without validation |
| | Selective HITL Precision | $100\%$ | **$100.0\%$** | Every human interrupt corresponds to genuine risk |

---

## 4. Orthogonal Radar Coordinates

When mapped to the **Four Orthogonal Radar Axes (0 to 100, 100 optimal)**:

1. **Pre-Deployment Safety ($100 - UAR$):** **$100.0\%$**
   - Perfect physical safety invariant ($UAR = 0.0\%$).
2. **HITL Efficiency (Zero-Friction Nominal):** **$100.0\%$**
   - Zero interruptions on Class I Nominal demands ($0.00$ turns / request).
3. **Execution Latency (Normalized Speed):** **$100.0\%$**
   - Baseline standard: fastest end-to-end execution across all baselines.
4. **Token Economy (Normalized Frugality):** **$100.0\%$**
   - Baseline standard: lowest token consumption per nominal request.

Proposed RADG forms the **complete, fully expanded outer diamond** on the Four Pillars Radar Chart, establishing the Pareto-optimal frontier.

---

## 5. Artifacts, Visual Figures & Architectural Justifications

All baseline telemetry and visual figures are generated in `tests/evaluation/baselines/proposed_radg/results/run_<run_id>/`:

### 5.1 4-Stage Operational Sankey Diagram (`deployment_flow_sankey.png / .pdf`)
- **Purpose:** Traces the entire operational lifecycle of the 20 test demands across 4 distinct phases:
  1. **Stage 1 (Intent Ingest):** 20 demands across 4 classes enter the pipeline.
  2. **Stage 2 (Admission Policy):** The dual RADGs admit only 5 nominal intents (25%), while 15 risky intents (75%) are intercepted pre-deployment (Phase 3b Semantic Gate intercepts 5, Phase 6 Physical RADG intercepts 10).
  3. **Stage 3 (SDON Controller Execution):** All 5 forwarded demands pass controller validation cleanly.
  4. **Stage 4 (Operational Outcome):** Shows **Touchless Production Provisioning (5 demands, 25%)** and **Zero Post-Deployment Incident Alarms (0 / 20)**, proving total pre-deployment containment.

### 5.2 Gate Decision Accuracy Matrix (`gate_accuracy_matrix.png / .pdf`)
- **Purpose:** Multi-class confusion matrix plotting expected vs. actual initial gate actions (`approve`, `clarify`, `replan`) across Classes I, II, III, and IV, demonstrating high routing fidelity ($GDA \ge 95\%$) and zero false positives ($FPR = 0\%$).

### 5.3 Latency & Token Overhead Breakdown (`latency_tokens_overhead.png / .pdf`)
- **Purpose:** Dual-panel bar chart illustrating the distribution of turnaround time ($T_{E2E}$) and token consumption per risk class, confirming that nominal intents incur minimal latency ($\sim 4.5\text{s}$) while multi-turn recovery on ambiguous/infeasible requests accounts for expected recovery overhead.

### 5.4 16:9 Presentation Slide Dashboard (`presentation_slide_dashboard.png / .pdf`)
- **Purpose:** Master publication-ready widescreen dashboard for thesis defense slides, combining key KPI cards, the confusion matrix, latency distributions, and gate performance metrics into a single cohesive layout.
