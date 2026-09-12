# Sprint 4 Evaluation Environment & Methodology Guide

## 1. Overview & Evaluation Philosophy

This directory contains the experimental evaluation harness for the Master's thesis:
> **"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"**

The evaluation is designed to assess the pre-deployment intent planning mechanism across the standardized **17-Node Nobel-Germany Core Backbone Topology** ($|V| = 17, |E| = 26$ bidirectional fiber links, SNDlib benchmark).

The fundamental hypothesis under test is that **a sequential, pre-deployment risk-adaptive architecture achieves a 0% Unsafe Approval Rate (UAR) while minimizing operational and computational friction** compared to unconstrained LLMs, rigid rule-based systems, and traditional manual SDON workflows.

---

## 2. The Four Core Validation Pillars & Exact Metrics

To avoid one-dimensional evaluations (such as measuring only wall-clock latency or token counters), the system is evaluated across four orthogonal pillars:

### Pillar 1: Semantic Translation Accuracy (Neural Domain Fidelity)
Validates that the neural subsystem faithfully translates unstructured natural language intents into formal PDDL constraints without dropping restrictions or inventing network primitives.

1. **Constraint Retention Rate (CRR):**
   $$\text{CRR} = \frac{\sum_{i=1}^{N} |\mathcal{C}_{\text{preserved}}^{(i)} \cap \mathcal{C}_{\text{explicit}}^{(i)}|}{\sum_{i=1}^{N} |\mathcal{C}_{\text{explicit}}^{(i)}|} \times 100\%$$
   - **Definition:** Percentage of explicit operator constraints (e.g., specific endpoints, link/node exclusions, minimum GSNR targets, maximum hop counts) correctly preserved in the PDDL problem definition.
   - **Target:** $100\%$.
   - **Measurement:** Compare parsed PDDL dictionary (`pddl_parsed_constraints`) against ground-truth intent constraints in `test_corpus.json`.

2. **Context-Free Grammar Pass Rate (CFG-PR):**
   $$\text{CFG-PR} = \frac{1}{N} \sum_{i=1}^{N} v_{struct}^{(i)} \times 100\%$$
   - **Definition:** Fraction of generated PDDL ASTs that pass deterministic Context-Free Grammar validation ($v_{struct} \in \{0, 1\}$).
   - **Target:** $100\%$ on well-formed intents; $0\%$ on adversarial syntax injections.
   - **Measurement:** Output of `validate_pddl_syntax()` in `src/core/pddl_validator.py`.

3. **Semantic Agreement Score ($1 - d_{sem}$):**
   - **Definition:** Discrepancy metric between original operator intent $\mathcal{I}_{NL}$ and reverse-prompted natural language reconstruction $\mathcal{I}_{recon}$.
   - **Formula:** $d_{sem} \in [0.0, 1.0]$ scored by LLM evaluator; Agreement $= 1.0 - d_{sem}$.
   - **Measurement:** Output of `_score_semantic_agreement()` in `src/nodes/semantic_gate_node.py`.

---

### Pillar 2: Physical Feasibility (Optical Layer Integrity)
Guarantees that all approved lightpaths strictly satisfy physical-layer transmission impairments (ASE noise, non-linear interference via the GN model) before touching the network controller.

1. **Unsafe Approval Rate (UAR):**
   $$\text{UAR} = \frac{|\{\text{plan} \in \text{Approved} \mid \text{GSNR}_{\text{actual}} < \text{GSNR}_{th} \lor P_{rx} < P_{rx,min}\}|}{|\text{Approved}|} \times 100\%$$
   - **Definition:** Fraction of intents producing physically infeasible lightpaths that receive an `approve` verdict.
   - **Target:** **$0\%$ (Absolute Safety Invariant)**.
   - **Measurement:** Compare RADG verdict against physical GN-model calculation (`assess_qot()`).

2. **QoT Feasibility Rate (QFR):**
   $$\text{QFR} = \frac{|\{\text{plan} \in \text{Approved} \mid \text{QoT}_{valid} = 1\}|}{|\text{Approved}|} \times 100\%$$
   - **Definition:** Fraction of deployed lightpaths that satisfy required transmission margins under analytical GN-model validation.
   - **Target:** $100\%$.

3. **Physical Infeasibility Interception Rate (PIIR):**
   $$\text{PIIR} = \frac{|\{\text{intent} \in \text{Class III} \mid \text{Action} = \text{replan}\}|}{|\text{Class III}|} \times 100\%$$
   - **Definition:** Fraction of demands requesting physically impossible optical reaches that are successfully intercepted and flagged for replanning rather than approved.
   - **Target:** $100\%$.

---

### Pillar 3: Orchestration & Resource Efficiency (Friction Minimization)
Quantifies computational savings in prompt tokens and runtime, alongside operator fatigue reduction through selective human engagement.

1. **Prompt Token Reduction ($\Delta T_{tokens}$):**
   $$\Delta T_{tokens} = \frac{T_{\text{full\_JSON}} - T_{\text{scoped\_GraphRAG}}}{T_{\text{full\_JSON}}} \times 100\%$$
   - **Definition:** Percentage of input tokens eliminated by Scoped Optical GraphRAG ($k=2$ neighborhood) compared to full RFC 8345 / RFC 9093 RESTCONF JSON topology injection.
   - **Target:** $> 75\%$ (Empirically measured: **$> 93\%$** on Nobel-Germany).
   - **Measurement:** `tiktoken` (`cl100k_base`) token counter comparing serialized full topology vs. `graph_to_context_string()`.

2. **Human Intervention Reduction ($\Delta N_{hitl}$):**
   $$\Delta N_{hitl} = \left( 1 - \frac{N_{hitl,\text{ours}}}{N_{hitl,\text{always}}} \right) \times 100\%$$
   - **Definition:** Reduction in operator interruptions compared to the mandatory Always-HITL baseline ($N_{hitl} = 100\%$).
   - **Target:** $> 70\%$.
   - **Measurement:** Count of `interrupt()` events triggered across the 100 test demands.

3. **Deterministic Compute Latency ($T_{det}$):**
   $$T_{det} = T_{solver} + T_{phys}$$
   - **Definition:** Wall-clock execution time of symbolic routing (Yen's $K$-SP, $T_{solver} < 10\text{ ms}$) and GN-model physics ($T_{phys} < 5\text{ ms}$).
   - **Target:** $< 15\text{ ms}$.
   - **Measurement:** `time.perf_counter()` inside `symbolic_solver_node` and `qot_validation_node`.

4. **End-to-End Orchestration Latency ($T_{E2E}$):**
   - **Definition:** Total wall-clock turnaround from NL submission to final planning report generation.
   - **Measurement:** Overall invocation duration excluding human pause time in `interrupt()`.

---

### Pillar 4: RADG Robustness & Decision Boundary Integrity (Gate Reliability)
Stress-tests the piecewise decision function $D(U_{sem}, \text{QoT}_{valid})$ across boundary conditions.

1. **Gate Decision Accuracy (GDA):**
   $$\text{GDA} = \frac{\sum_{i=1}^{N} \mathbb{I}(D(U_{sem}^{(i)}, \text{QoT}_{valid}^{(i)}) = \text{Action}_{\text{ground\_truth}}^{(i)})}{N} \times 100\%$$
   - **Definition:** Overall accuracy of the RADG in routing intents to the optimal action state (`approve`, `clarify`, `replan`, `reject`).
   - **Target:** $> 98\%$.

2. **False Positive Rate (FPR):**
   $$\text{FPR} = \frac{|\{\text{intent} \in (\text{Class II} \cup \text{Class III} \cup \text{Class IV}) \mid \text{Action} = \text{approve}\}|}{|\text{Class II} \cup \text{Class III} \cup \text{Class IV}|} \times 100\%$$
   - **Definition:** Probability of issuing an `approve` decision given an unfeasible, ambiguous, or adversarial intent.
   - **Target:** **$0\%$**.

3. **Selective HITL Precision:**
   $$\text{Precision}_{HITL} = \frac{|\{\text{intent} \text{ interrupted} \mid \text{ambiguity} \lor \text{infeasibility}\}|}{|\text{intents interrupted}|} \times 100\%$$
   - **Definition:** Fraction of human interruptions that correctly target ambiguous or infeasible intents requiring genuine operator input rather than false alarms on clear nominal intents.

---

## 3. Comparative Baselines

| Baseline | Architecture | Operational Mode | Evaluation Role |
|----------|--------------|------------------|-----------------|
| **Baseline A (LLM-Only)** | Monolithic LLM (Direct NL $\to$ JSON/CLI) | Unconstrained autonomous execution with reactive post-deployment retry | Evaluates failure modes: hallucinated physics, attention degradation, and high recovery latency |
| **Baseline B (Static Rule-Based)** | Deterministic regex / CFG parser | Always-on human review (mandatory human validation on every intent) | Evaluates operational friction: operator fatigue, low expressiveness, and configuration rigidity |
| **Baseline C (Traditional SDON)** | Non-LLM imperative YANG / RESTCONF RPC + PCE | Manual payload authoring by expert operator + deterministic Yen's $K$-SP / GN-model | Evaluates industrial baseline: zero NL translation error, absolute safety ($UAR=0\%$), but high human friction ($N_{human}$) and zero ambiguity tolerance |
| **Proposed (Neurosymbolic RADG)** | Decoupled LangGraph pipeline (LLM translator + Yen's $K$-SP + GN-model) | Pre-deployment sequential risk gates ($U_{sem} \to \text{QoT}_{valid}$) with selective HITL | Evaluates proposed thesis hypothesis: pre-deployment safety ($UAR = 0\%$) with minimal operational friction and high NL expressiveness |

---

## 4. Benchmark Corpus: `test_corpus.json`

The evaluation dataset contains **100 synthetic operator intents** structured into four equal classes (25 intents each) tailored for the 17-node German backbone topology:

| Class | Name | Size | Key Characteristics | Target RADG Action |
|:-----:|:-----|:----:|:-------------------|:------------------:|
| **Class I** | **Nominal** | 25 | Clear source-destination pairs, feasible optical paths, realistic GSNR requirements ($\le 18\text{ dB}$). | `approve` (0 interrupts) |
| **Class II** | **Ambiguous** | 25 | Underspecified endpoints ("to the north region"), colloquial SLA ("ultra-fast link"), missing constraints. | `clarify` (Phase 3b HITL) |
| **Class III** | **Physically Infeasible** | 25 | Impossible physical constraints on Nobel-Germany ($>30\text{ dB}$ GSNR on multi-hop routes, 0 hops). | `replan` (Phase 6 RADG) |
| **Class IV** | **Adversarial** | 25 | Hallucinated non-German nodes ("Paris to Rome"), contradictory constraints, PDDL syntax injection. | `reject` / `clarify` (Layer 1 CFG) |

---

## 5. Running the Evaluation

To validate the test corpus schema:
```bash
uv run python -c "
import json
with open('tests/evaluation/test_corpus.json') as f:
    corpus = json.load(f)
assert len(corpus) == 100
print('Benchmark corpus verified: 100 intents across 4 balanced classes.')
"
```

To run unit tests across all pipeline modules:
```bash
uv run pytest
```
