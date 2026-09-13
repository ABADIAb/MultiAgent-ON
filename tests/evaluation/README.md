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

2. **Baseline Token Consumption ($T_{tokens}$):**
   - **Definition:** Raw number of prompt and completion tokens consumed per intent by each baseline architecture.
   - **Purpose:** Compares the absolute computational footprint and LLM API cost across different planning approaches.
   - **Measurement:** `tiktoken` (`cl100k_base`) token counter across all LLM calls per intent execution.

3. **Human Intervention Reduction ($\Delta N_{hitl}$):**
   $$\Delta N_{hitl} = \left( 1 - \frac{N_{hitl,\text{ours}}}{N_{hitl,\text{always}}} \right) \times 100\%$$
   - **Definition:** Reduction in operator interruptions compared to the mandatory Always-HITL baseline ($N_{hitl} = 100\%$).
   - **Target:** $> 70\%$.
   - **Measurement:** Count of `interrupt()` events triggered across the 107 test demands.

4. **Deterministic Compute Latency ($T_{det}$):**
   $$T_{det} = T_{solver} + T_{phys}$$
   - **Definition:** Wall-clock execution time of symbolic routing (Yen's $K$-SP, $T_{solver} < 10\\text{ ms}$) and GN-model physics ($T_{phys} < 5\\text{ ms}$).
   - **Target:** $< 15\\text{ ms}$.
   - **Measurement:** `time.perf_counter()` inside `symbolic_solver_node` and `qot_validation_node`.

5. **End-to-End Orchestration Latency ($T_{E2E}$):**
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

## 3. Comparative Baselines & Polymorphic Execution Contract

| Baseline | Architecture | Operational Mode | Evaluation Role |
|----------|--------------|------------------|-----------------|
| **Baseline A (Monolithic LLM)** | Direct Prompting (NL $\to$ JSON/CLI) | Unconstrained autonomous execution with zero deterministic tools | Evaluates neural failure modes: hallucinated physics, topological invalidity, and high $UAR$ |
| **Baseline B (Always-On HITL)** | Full Neurosymbolic Pipeline | Mandatory human review at Phase 3b and Phase 6 for every intent | Evaluates operational friction: operator fatigue ($N_{hitl} = 100\%$), inflated token cost, and execution latency |
| **Baseline C (Always-Off HITL)** | Full Neurosymbolic Pipeline | Autonomous execution with decision gates bypassed (no HITL) | Evaluates safety failure modes: unhandled ambiguity, high service blocking, and deployment of unfeasible paths |
| **Baseline D (Traditional SDON)** | Non-LLM imperative YANG / RESTCONF RPC + PCE | Manual payload authoring by expert operator + deterministic Yen's $K$-SP / GN-model | Evaluates industrial standard: zero NL translation error, absolute safety ($UAR=0\%$), but $100\%$ human setup effort |
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
- `action`: Ternary RADG action (`"approve"`, `"clarify"`, `"replan"`, or `"reject"`).
- `selected_path`: Route computed or hallucinated by the system.
- `computed_gsnr_dB`: Ground-truth physical GSNR computed via GN-model.
- `qot_feasible`: Ground-truth binary optical feasibility.
- `pddl_valid`: Context-free grammar validation flag.
- `hitl_interrupts`: Total count of human interruptions ($N_{hitl}$).
- `prompt_tokens`, `completion_tokens`, `total_tokens`: Token consumption metrics.
- `execution_time_s`: Wall-clock execution latency.
- `planning_report`: Output report string or JSON.

---

## 4. Benchmark Corpus: `test_corpus.json`

The evaluation dataset contains **107 synthetic operator intents** structured into four classes tailored for the 17-node German backbone topology:

| Class | Name | Size | Key Characteristics | Target RADG Action |
|:-----:|:-----|:----:|:-------------------|:------------------:|
| **Class I** | **Nominal** | 28 | Clear source-destination pairs, feasible optical paths, realistic GSNR requirements ($\le 18\text{ dB}$). | `approve` (0 interrupts) |
| **Class II** | **Ambiguous** | 26 | Underspecified endpoints ("to the north region"), colloquial SLA ("ultra-fast link"), missing constraints. | `clarify` (Phase 3b HITL) |
| **Class III** | **Physically Infeasible** | 27 | Impossible physical constraints on Nobel-Germany ($>30\text{ dB}$ GSNR on multi-hop routes, 0 hops). | `replan` (Phase 6 RADG) |
| **Class IV** | **Adversarial** | 26 | Hallucinated non-German nodes ("Paris to Rome"), contradictory constraints, PDDL syntax injection. | `clarify` (Phase 3b HITL / CFG) |

---

## 5. Running the Automated Evaluation Harness

The benchmark harness is executed using `uv run` and supports both **Live LLM API** runs and **Deterministic Offline Mock** runs for instant zero-cost reproducibility and CI testing.

### 5.1 Quick Validation & Dry-Run (Mock Mode)

To run the complete benchmark suite across all 107 test demands and all 5 comparative baselines offline without consuming API tokens:

```bash
uv run python tests/evaluation/scripts/run_benchmark.py --mock
```

To run a rapid subset (e.g., first 10 intents):
```bash
uv run python tests/evaluation/scripts/run_benchmark.py --mock --limit 10
```

To run only specific baselines:
```bash
uv run python tests/evaluation/scripts/run_benchmark.py --mock --baselines proposed_radg,llm_only
```

To filter by intent risk category:
```bash
uv run python tests/evaluation/scripts/run_benchmark.py --mock --classes I_Nominal,III_Infeasible
```

### 5.2 Full Live LLM API Benchmark

To execute the benchmark against the production Kimi LLM API endpoint:
```bash
uv run python tests/evaluation/scripts/run_benchmark.py
```

### 5.3 Regenerating Figures & Visual Artifacts

To re-render all IEEE / PoliMi thesis figures from an existing `metrics.json`:
```bash
uv run python tests/evaluation/scripts/plotter.py --metrics-file tests/evaluation/results/metrics.json
```

### 5.4 Running Evaluation Unit Tests (Strict TDD)

```bash
# Test the deterministic metrics engine and plotter
uv run pytest tests/unit/test_metrics.py -v

# Test baseline abstractions and polymorphic registry
uv run pytest tests/unit/test_baselines.py -v

# Run the complete test suite (320+ unit tests)
uv run pytest
```

---

## 6. Output Artifacts & Directory Structure

All benchmark outputs are strictly encapsulated within `tests/evaluation/results/`:

```
tests/evaluation/results/
├── summary_table.md             # Consolidated markdown summary table (ready for thesis/papers)
├── metrics.json                 # Structured metrics dictionary across all 4 pillars
├── raw/
│   ├── raw_results.json         # Complete per-intent execution dictionary for all baselines
│   ├── raw_results.csv          # Flat tabular CSV for pandas / R / statistical analysis
│   ├── raw_results_<timestamp>.json
│   └── raw_results_<timestamp>.csv
└── figures/
    ├── latency_vs_tokens.pdf    # Vector PDF: Orchestration latency vs. Prompt tokens
    ├── latency_vs_tokens.png    # 300 DPI preview for slide decks and quick inspection
    ├── success_vs_uar.pdf       # Vector PDF: QoT Feasibility vs. UAR (0% Invariant)
    ├── success_vs_uar.png
    ├── hitl_interruption_origin.pdf # Vector PDF: Phase 3b Semantic vs. Phase 6 Physical interrupts
    ├── hitl_interruption_origin.png
    ├── gate_decision_distribution.pdf # Vector PDF: Action breakdown across intent classes
    └── gate_decision_distribution.png
```

