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

2. **Physical Infeasibility Interception Rate (PIIR):**
   $$\text{PIIR} = \frac{|\{\text{intent} \in \text{Class III} \mid \text{Action} = \text{replan}\}|}{|\text{Class III}|} \times 100\%$$
   - **Definition:** Fraction of demands requesting physically impossible optical reaches that are successfully intercepted and flagged for replanning rather than approved.
   - **Target:** $100\%$.

---

### Pillar 3: Orchestration & Resource Efficiency (Friction Minimization)
Quantifies computational savings in runtime latency and total token consumption, alongside operator fatigue reduction through selective human engagement.

1. **End-to-End Orchestration Latency ($T_{E2E}$):**
   - **Definition:** Total turnaround duration from natural language submission to final planning report synthesis.
   - **Multi-Turn Follow-Up Contract:** For intents intercepted at Phase 3b (`clarify`) or Phase 6 (`replan`), the benchmark automatically supplies a standardized nominal follow-up intent (`"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`), allowing the pipeline to recover and complete through to Phase 7. This captures the true E2E completion latency across all risk classes.

2. **Token Footprint ($T_{tokens}$):**
   - **Definition:** Cumulative prompt, completion, and total tokens consumed per intent across all conversational and refinement turns.

3. **Human Intervention Reduction ($\Delta N_{hitl}$):**
   $$\Delta N_{hitl} = \left( 1 - \frac{N_{hitl,\text{ours}}}{N_{hitl,\text{always}}} \right) \times 100\%$$
   - **Definition:** Reduction in operator interruptions compared to the mandatory Always-HITL baseline ($N_{hitl} \ge 2$).
   - **Target:** $> 70\%$.

---

### Pillar 4: RADG Robustness & Decision Boundary Integrity (Gate Reliability)
Stress-tests the piecewise decision function $D(U_{sem}, \text{QoT}_{valid})$ across boundary conditions.

1. **Gate Decision Accuracy (GDA):**
   $$\text{GDA} = \frac{\sum_{i=1}^{N} \mathbb{I}(D(U_{sem}^{(i)}, \text{QoT}_{valid}^{(i)}) = \text{Action}_{\text{ground\_truth}}^{(i)})}{N} \times 100\%$$
   - **Definition:** Overall accuracy of the RADG in routing intents to the optimal action state (`approve`, `clarify`, `replan`). Evaluated on the *initial gate interception* before follow-up recovery.
   - **Target:** $> 98\%$.

2. **False Positive Rate (FPR):**
   $$\text{FPR} = \frac{|\{\text{intent} \in (\text{Class II} \cup \text{Class III} \cup \text{Class IV}) \mid \text{Action} = \text{approve}\}|}{|\text{Class II} \cup \text{Class III} \cup \text{Class IV}|} \times 100\%$$
   - **Definition:** Probability of issuing an `approve` decision given an unfeasible, ambiguous, or adversarial intent.
   - **Target:** **$0\%$**.

3. **Selective HITL Precision:**
   $$\text{Precision}_{HITL} = \frac{|\{\text{intent} \text{ interrupted} \mid \text{ambiguity} \lor \text{infeasibility}\}|}{|\text{intents interrupted}|} \times 100\%$$
   - **Definition:** Fraction of human interruptions that correctly target ambiguous or infeasible intents requiring genuine operator input rather than false alarms on clear nominal intents.

---

## 3. Comparative Baselines & Polymorphic Execution Contract

| Baseline | Architecture | Operational Mode | Evaluation Role |
|----------|--------------|------------------|-----------------|
| **Baseline A (Monolithic LLM)** | Direct Prompting (NL $\to$ JSON/CLI) | Unconstrained autonomous execution with zero deterministic tools | Evaluates neural failure modes: hallucinated physics, topological invalidity, and high $UAR$ |
| **Baseline B (Always-On HITL)** | Full Neurosymbolic Pipeline | Mandatory human review at Phase 3b and Phase 6 for every intent | Evaluates operational friction: operator fatigue ($N_{hitl} \ge 2$), inflated token cost, and execution latency |
| **Baseline C (Traditional SDON)** | Static Industrial Reference | Manual YANG RPC authoring by expert operator + PCE | Evaluates industrial standard: zero NL translation error, absolute safety ($UAR=0\%$), non-LLM, manual provisioning taking hours to days |
| **Proposed (Neurosymbolic RADG)** | Decoupled LangGraph pipeline (LLM translator + Yen's $K$-SP + GN-model) | Pre-deployment sequential risk gates ($U_{sem} \to \text{QoT}_{valid}$) with selective HITL | Evaluates proposed thesis hypothesis: pre-deployment safety ($UAR = 0\%$) with minimal operational friction ($N_{hitl} \le 1$) and high NL expressiveness |

### 3.1 Polymorphic Baseline Contract (`tests/evaluation/baselines/`)

All baselines (and the Proposed architecture wrapper) implement a unified contract defined in `tests/evaluation/baselines/base.py`:

```python
class BaseBaseline(ABC):
    name: str
    baseline_id: str

    @abstractmethod
    def run(self, intent_data: dict[str, Any], **kwargs) -> BaselineResult:
        """Execute the baseline against a single intent record."""
        ...
```

The output `BaselineResult` standardizes metrics for downstream comparative plotting (`run_benchmark.py`):
- `intent_id`: Identifier of the intent from `test_corpus.json`.
- `baseline_id`: Key of the evaluated system (`"llm_only"`, `"always_on"`, `"always_off"`, `"traditional_sdon"`, `"proposed_radg"`).
- `action`: Ternary RADG action (`"approve"`, `"clarify"`, or `"replan"`).
- `selected_path`: Route computed or hallucinated by the system.
- `computed_gsnr_dB`: Ground-truth physical GSNR computed via GN-model.
- `qot_feasible`: Ground-truth binary optical feasibility.
- `pddl_valid`: Context-free grammar validation flag.
- `hitl_interrupts`: Total count of human interruptions ($N_{hitl}$).
- `prompt_tokens`, `completion_tokens`, `total_tokens`: Token consumption metrics.
- `execution_time_s`: Wall-clock execution latency.
- `planning_report`: Output report string or JSON.

---

## 4. Benchmark Corpus: `test_corpus_compact.json`

The evaluation dataset utilizes a **20-intent compact corpus** structured into four equal classes (5 demands each) tailored for the 17-node German backbone topology.

**Corpus Design & Validation Methodology:**
1. **How were the intents generated?** Intents were synthetically generated to systematically stress-test specific parsing and reasoning capabilities over the 17-node Nobel-Germany topology (e.g., node combinations, hop limits, GSNR requirements).
2. **Why were these categories selected?** The four classes map directly to the edge cases of the RADG decision boundaries: nominal (auto-approve), semantic ambiguity (early HITL clarify), physical infeasibility (late HITL replan), and adversarial/hallucination (CFG rejection / early clarify).
3. **How were the reference labels validated?** The ground-truth constraints and expected outcomes (`expected_pddl_valid`, `expected_radg_action`) were manually verified against the deterministic Python GN-model and graph topology properties to ensure absolute baseline correctness.

| Class | Name | Size | Key Characteristics | Target RADG Action |
|:-----:|:-----|:----:|:-------------------|:------------------:|
| **Class I** | **Nominal** | 5 | Clear source-destination pairs, feasible optical paths, realistic GSNR requirements ($\le 18\text{ dB}$). | `approve` (0 interrupts) |
| **Class II** | **Ambiguous** | 5 | Underspecified endpoints ("to the north region"), colloquial SLA ("ultra-fast link"), missing constraints. | `clarify` (Phase 3b HITL) |
| **Class III** | **Physically Infeasible** | 5 | Impossible physical constraints on Nobel-Germany ($>30\text{ dB}$ GSNR on multi-hop routes, 0 hops). | `replan` (Phase 6 RADG) |
| **Class IV** | **Adversarial** | 5 | Hallucinated non-German nodes ("Paris to Rome"), contradictory constraints, PDDL syntax injection. | `clarify` (Phase 3b HITL / CFG) |

