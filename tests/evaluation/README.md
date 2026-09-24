# Sprint 4 Evaluation Environment & Benchmark Guide

This directory contains the automated, reproducible benchmark suite for evaluating the **LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning** pipeline (V5) across the standardized **17-Node Nobel-Germany Core Optical Backbone**.

---

## 1. Directory Structure

```text
tests/evaluation/
├── main.py                     # Unified interactive CLI & benchmark runner (Rich + Questionary)
├── baselines/                  # Modular baseline implementations reusing src/
│   ├── common/                 # Shared runner, callback TokenTracker, metrics, and reporter
│   │   ├── metrics.py          # Four Pillars telemetry formulas (CRR, CFG-PR, UAR, GDA)
│   │   ├── runner.py           # Multi-turn execution loop with HITL recovery interception
│   │   ├── reporter.py         # Multi-format telemetry exporter (JSON, CSV, MD)
│   │   └── results/            # Comparative multi-baseline aggregated summaries (run_<timestamp>/)
│   ├── proposed_radg/          # Proposed System: Fail-fast Semantic & Physical RADGs
│   │   ├── graph.py            # Wires standard src.core.graph
│   │   ├── evaluator.py        # Proposed RADG evaluator
│   │   └── results/            # Run artifacts per execution (run_<timestamp>/)
│   ├── always_on_hitl/         # Baseline: Always-On HITL (Paranoid Turn-1 Review on Nominals)
│   │   ├── graph.py            # StateGraph with Turn-1 mandatory clarification
│   │   ├── evaluator.py        # Always-On HITL evaluator
│   │   └── results/            # Run artifacts per execution (run_<timestamp>/)
│   └── llm_only/               # Baseline: LLM-Only (No Semantic Gate / Controller Error Surrogate)
│       ├── graph.py            # StateGraph with bypassed semantic gate + controller surrogate
│       ├── evaluator.py        # LLM-Only evaluator
│       └── results/            # Run artifacts per execution (run_<timestamp>/)
├── test_corpus_compact.json    # Standard 20-demand benchmark corpus (4 balanced risk classes)
├── test_corpus.json            # 107-demand full benchmark corpus
├── generate_visuals.py         # Visualizer generating publication/slide figures (PNG/PDF)
├── archive/                    # Archived legacy scripts and previous evaluation runs
│   ├── run_evaluation.py       # (Legacy) Replaced by tests/evaluation/main.py
│   └── results_legacy/         # (Legacy) Historical test snapshots
└── README.md                   # Environment, methodology, and execution instructions
```

---

## 2. The Four Core Validation Pillars & Exact Metrics

The evaluation framework assesses the system across four orthogonal validation pillars defined in [[ProblemStatement_v5]] and [[docs/LLM_Wiki/raw/README-evaluation]]:

### Pillar 1: Semantic Translation Accuracy (Neural Domain Fidelity)
Validates that the neural subsystem faithfully translates unstructured natural language intents into formal PDDL constraints without dropping restrictions or inventing network primitives.

1. **Constraint Retention Rate (CRR):**
   $$\text{CRR} = \frac{\sum_{i=1}^{N} |\mathcal{C}_{\text{preserved}}^{(i)} \cap \mathcal{C}_{\text{explicit}}^{(i)}|}{\sum_{i=1}^{N} |\mathcal{C}_{\text{explicit}}^{(i)}|} \times 100\%$$
   - **Definition:** Percentage of explicit operator constraints (GSNR, node exclusions, hop limits, bandwidth) correctly preserved in the synthesized PDDL.
   - **Target:** $100\%$.
2. **Context-Free Grammar Pass Rate (CFG-PR):**
   $$\text{CFG-PR} = \frac{1}{N} \sum_{i=1}^{N} v_{struct}^{(i)} \times 100\%$$
   - **Definition:** Fraction of generated PDDL ASTs passing deterministic grammar validation ($v_{struct} \in \{0, 1\}$).
   - **Target:** $\ge 95\%$ on well-formed intents; $0\%$ on adversarial syntax injections.
3. **Semantic Agreement Score ($1 - d_{sem}$):**
   - **Definition:** Semantic concordance between original operator intent $\mathcal{I}_{NL}$ and Reverse Prompting reconstruction $\mathcal{I}_{recon}$.
   - **Target:** $> 0.85$.

---

### Pillar 2: Physical Feasibility (Optical Layer Integrity)
Guarantees that all approved lightpaths strictly satisfy physical-layer transmission impairments (ASE noise, non-linear interference via the GN model) before touching the network controller.

1. **Unfeasible Approval Rate (UAR):**
   $$\text{UAR} = \frac{|\{\text{plan} \in \text{Approved} \mid \text{GSNR}_{\text{actual}} < \text{GSNR}_{th} \lor P_{rx} < P_{rx,min}\}|}{|\text{Approved}|} \times 100\%$$
   - **Definition:** Fraction of intents producing physically infeasible lightpaths that receive an `approve` verdict.
   - **Hard Target:** **$0.0\%$ (Absolute Physical Integrity Invariant)**.
2. **Physical Infeasibility Interception Rate (PIIR):**
   $$\text{PIIR} = \frac{|\{\text{intent} \in \text{Class III} \mid \text{Action} = \text{replan}\}|}{|\text{Class III}|} \times 100\%$$
   - **Definition:** Fraction of demands requesting physically impossible optical reaches that are intercepted and flagged for replanning.
   - **Target:** $100.0\%$.

---

### Pillar 3: Orchestration & Resource Efficiency (Friction Minimization)
Quantifies computational savings in runtime latency and total token consumption, alongside operator fatigue reduction through selective human engagement.

1. **End-to-End Orchestration Latency ($T_{E2E}$):**
   - **Definition:** Total turnaround duration from natural language submission to final planning report synthesis. Contextual target depending on hardware and SLM quantization.
2. **Token Footprint ($T_{tokens}$):**
   - **Definition:** Cumulative prompt, completion, and total tokens consumed per intent across all turns, tracked via LangChain callbacks.
3. **Selective HITL Turns ($N_{hitl}$):**
   - **Definition:** Number of HITL interrupts triggered. Target: $0$ for Nominal intents, $1$ for recovery on ambiguous/infeasible intents.

---

### Pillar 4: RADG Robustness & Decision Boundary Integrity (Gate Reliability)
Stress-tests the piecewise decision function $D(U_{sem}, \text{QoT}_{valid})$ across boundary conditions.

1. **Gate Decision Accuracy (GDA):**
   $$\text{GDA} = \frac{\sum_{i=1}^{N} \mathbb{I}(D(U_{sem}^{(i)}, \text{QoT}_{valid}^{(i)}) = \text{Action}_{\text{ground\_truth}}^{(i)})}{N} \times 100\%$$
   - **Definition:** Overall accuracy of the RADG in routing intents to the optimal action state (`approve`, `clarify`, `replan`) on initial gate interception.
   - **Target:** $> 98\%$.
2. **False Positive Rate (FPR):**
   $$\text{FPR} = \frac{|\{\text{intent} \in (\text{Class II} \cup \text{Class III} \cup \text{Class IV}) \mid \text{Action} = \text{approve}\}|}{|\text{Class II} \cup \text{Class III} \cup \text{Class IV}|} \times 100\%$$
   - **Target:** **$0.0\%$**.
3. **Selective HITL Precision:**
   $$\text{Precision}_{HITL} = \frac{|\{\text{intent interrupted} \mid \text{Class} \neq \text{Nominal}\}|}{|\text{intents interrupted}|} \times 100\%$$
   - **Target:** $100.0\%$.

---

## 3. Test Corpus: 4 Balanced Risk Classes

The dataset (`test_corpus_compact.json`) comprises 20 demands balanced equiprobably across 4 risk classes:

| Class | Name | Size | Expected RADG Action | Key Objective |
| :---: | :--- | :--: | :------------------: | :------------ |
| **I** | **Nominal** | 5 | `approve` (0 interrupts) | Feasible requests with valid optical paths and realistic GSNR ($\le 18\text{ dB}$). |
| **II** | **Ambiguous** | 5 | `clarify` (Phase 3b HITL) | Underspecified endpoints or colloquial SLA, caught fail-fast by Semantic Gate. |
| **III** | **Physically Infeasible** | 5 | `replan` (Phase 6 RADG) | Demands violating GN-model physical reach ($> 28\text{ dB}$ GSNR on multi-hop). |
| **IV** | **Adversarial** | 5 | `clarify` / `replan` (CFG / Gate) | Contradictory constraints or hallucinated node names intercepted by CFG / Gate. |

---

## 4. How to Run the Evaluation Benchmark

### Prerequisites
1. **Ollama running with `qwen2.5:3b`** (or configured cloud provider in `.env`):
   ```bash
   ollama run qwen2.5:3b
   ```
2. **Environment Variables** (`.env`):
   ```bash
   LLM_PROVIDER="ollama"
   OLLAMA_MODEL="qwen2.5:3b"
   # If using WSL2, point to host gateway or localhost:
   OLLAMA_BASE_URL="http://172.27.144.1:11434/v1"
   LLM_TIMEOUT=120.0
   ```

### 4.1 Unified Interactive CLI (`tests/evaluation/main.py`)
Launch the rich, interactive terminal UI with arrow-key menus:
```bash
uv run python tests/evaluation/main.py
```
This interactive CLI allows you to:
1. Choose between **Proposed RADG**, **Always-On HITL**, **LLM-Only**, or **All Baselines**.
2. Select **Interactive Mode** (single intent with live phase tracking) or **Evaluation Benchmark Mode**.
3. Select test corpus (**Compact 20-demands** or **Full 107-demands**) and risk class filters.
4. Configure LLM provider (`ollama`, `openrouter`, `kimi`) and target model.

### 4.2 Direct Baseline Benchmark Execution
Run specific baselines directly via CLI flags:
```bash
# Run Proposed RADG on the compact corpus:
uv run python tests/evaluation/main.py --baseline proposed_radg --mode eval --corpus compact

# Run Always-On HITL (evaluates Nominal intents):
uv run python tests/evaluation/main.py --baseline always_on_hitl --mode eval --corpus compact

# Run LLM-Only (evaluates all classes, simulating controller error):
uv run python tests/evaluation/main.py --baseline llm_only --mode eval --corpus compact

# Run all baselines sequentially:
uv run python tests/evaluation/main.py --baseline all --mode eval --corpus compact

# Interactive execution with custom intent:
uv run python tests/evaluation/main.py --baseline proposed_radg --mode interactive --intent "Route 100G from Hamburg to Berlin with at least 15 dB GSNR"
```

### 4.3 Cross-Baseline Comparative Mode & Version Selection
Generate comparative executive matrices and figures (Four Pillars breakdown + 5-axis Radar chart) comparing runs across baselines:
```bash
# Compare the latest run of each baseline automatically:
uv run python tests/evaluation/main.py --mode compare

# Compare specific timestamped runs per baseline:
uv run python tests/evaluation/main.py --mode compare \
  --proposed-run 20260924_135646 \
  --hitl-run 20260924_120000 \
  --llm-run 20260924_113000
```
In interactive mode, select **Comparative Analysis Mode** from the main menu; if a baseline has multiple historical runs, the CLI provides an arrow-key selector with `(Latest)` as the default. Output artifacts are persisted into `tests/evaluation/baselines/common/results/run_<timestamp>/`.

---

## 5. Automated Recovery Protocol (Multi-Turn HITL)

When an intent triggers a decision gate:
- **Phase 3b (`hitl_clarify`)**: The evaluation harness intercepts the pause, logs the semantic divergence ($d_{sem}, U_{sem}$), and automatically injects the standardized follow-up recovery intent:
  `"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`
- **Phase 6 (`radg`)**: If physical constraints fail, the harness provides the relaxed follow-up intent to allow completion through to Phase 7 (Synthesis).
- **Dual-Action Logging**:
  - `initial_action`: Preserves the first-try gate verdict (`approve`, `clarify`, or `replan`) to evaluate gate accuracy.
  - `final_action`: Records whether recovery succeeded in synthesizing a valid planning report (`approve`).

---

## 6. Output Artifacts & Results Organization

All evaluation outputs are strictly segregated by baseline and timestamped per execution:
- **Baseline Runs (`tests/evaluation/baselines/<baseline>/results/run_<timestamp>/`):**
  - `evaluation_results.json`: Full diagnostic trace including PDDL strings, AST CFG pass status, reconstructed natural language, $U_{sem}$ scores, candidate routes, token counts, and QoT SNR margins.
  - `evaluation_results.csv`: Tabular spreadsheet format for rapid plotting and aggregation.
  - `evaluation_summary.md`: Publication-ready summary table featuring the Executive Four Core Validation Pillars matrix, Class Breakdown, and Detailed Trace.
  - `gate_accuracy_matrix.png / .pdf`: Gate Interception breakdown chart.
  - `latency_tokens_overhead.png / .pdf`: Latency & Token Distribution across Risk Classes.
  - `presentation_slide_dashboard.png / .pdf`: 16:9 Widescreen Composite Visual for thesis defense slides.

- **Comparative Aggregations (`tests/evaluation/baselines/common/results/run_<timestamp>/`):**
  When running all baselines (`--baseline all`), the common framework synthesizes:
  - `comparative_results.json`: Cross-baseline metrics across all four pillars.
  - `comparative_summary.md`: Side-by-side executive comparison matrix contrasting Proposed RADG vs Always-On HITL vs LLM-Only.
