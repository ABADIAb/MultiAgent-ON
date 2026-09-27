# Sprint 4 Evaluation Environment & Benchmark Guide

This directory contains the automated, reproducible benchmark suite for evaluating the **LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning** pipeline (V5) across the standardized **17-Node Nobel-Germany Core Optical Backbone**.

---

## 1. Directory Structure

```text
tests/evaluation/
├── main.py                     # Unified interactive CLI & benchmark runner (Rich + Questionary)
├── results/                    # Global comparative results ([LLM]/[timestamp]/ and cross_model/[timestamp]/)
│   └── cross_model/            # Cross-model LLM comparison outputs ([timestamp]/)
├── baselines/                  # Modular baseline implementations reusing src/
│   ├── common/                 # Shared runner, token tracker, metrics, and reporter
│   │   ├── metrics.py          # Four Pillars telemetry formulas (CRR, CFG-PR, FPR, GDA)
│   │   ├── runner.py           # Multi-turn execution loop with HITL recovery interception
│   │   └── reporter.py         # Multi-format telemetry exporter (JSON, CSV, MD)
│   ├── proposed_radg/          # Proposed System: Fail-fast Semantic & Physical RADGs
│   ├── always_on_hitl/         # Baseline: Always-On HITL (Paranoid Turn-1 Review on Nominals)
│   └── llm_only/               # Baseline: LLM-Only (No Semantic Gate / Controller Error Surrogate)
├── test_corpus_compact.json    # Standard 20-demand benchmark corpus (4 balanced risk classes)
├── test_corpus.json            # 120-demand full benchmark corpus (4 balanced risk classes)
├── generate_visuals.py         # Visualizer generating publication/slide figures (PNG/PDF)
├── archive/                    # Archived legacy scripts and previous evaluation snapshots
└── README.md                   # Environment, methodology, and execution instructions
```

> [!NOTE]
> **Baseline Deep Dives**: Detailed mathematical derivations, ablation justifications, and visual figure catalogs for each baseline are documented in their respective guides:
> - [Proposed RADG Guide](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/proposed_radg/README.md)
> - [Always-On HITL Baseline Guide](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_on_hitl/README.md)
> - [LLM-Only Baseline Guide](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only/README.md)

---

## 2. The Four Core Validation Pillars

The evaluation framework assesses intent translation, optical reachability, efficiency, and gate robustness across four orthogonal pillars:

| Pillar | Metric | Formula / Scope | Target | Focus |
| :--- | :--- | :--- | :---: | :--- |
| **Pillar 1: Semantic Translation Accuracy** | **Constraint Retention Rate (CRR)** | $\frac{\sum \|\mathcal{C}_{pres} \cap \mathcal{C}_{exp}\|}{\sum \|\mathcal{C}_{exp}\|} \times 100\%$ | $100.0\%$ | Explicit operator constraint preservation in PDDL AST |
| | **Context-Free Grammar Pass Rate (CFG-PR)** | $\frac{1}{N} \sum v_{struct} \times 100\%$ | $\ge 95\%$ | PDDL syntactic & AST validity |
| | **Semantic Agreement Score** | $1 - d_{sem} \in [0, 1]$ | $> 0.85$ | Neural agreement via reverse-prompting reconstruction |
| **Pillar 2: Physical Feasibility & Integrity** | **False Positive Rate (FPR)** | $\frac{\|\text{Risky Approved}\|}{\|\text{Risky Demands}\|} \times 100\%$ | **$0.0\%$** | **Strict Pre-Deployment Integrity Invariant** (Zero un-gated or reach-violating lightpaths) |
| | **Physical Infeasibility Interception Rate (PIIR)** | $\frac{\|\text{Class III Intercepted}\|}{\|\text{Class III}\|} \times 100\%$ | $100.0\%$ | Pre-deployment interception of reach-violating intents |
| **Pillar 3: Orchestration & Efficiency** | **Median End-to-End Latency ($\tilde{T}_{E2E}$)** | $\text{Median}(T_{E2E})$ [seconds] | Hardware | Robust turnaround latency (median avoids skew from GPU throttling) |
| | **Median Token Footprint ($\tilde{T}_{tokens}$)** | $\text{Median}(\text{Prompt} + \text{Completion})$ | Frugal | LLM inference token consumption across all execution turns |
| | **Selective HITL Turns ($N_{hitl}$)** | $\text{Mean}(N_{turns} - 1)$ | $0.00$ Nom | Minimizing human cognitive fatigue on nominal intents |
| | **Task Completion Rate (TCR)** | $\frac{\|\text{Completed Plans}\|}{\|\text{Total Demands}\|} \times 100\%$ | $100.0\%$ | Execution robustness across transient timeouts or aborts |
| **Pillar 4: Gate Reliability & Autonomy** | **Gate Decision Accuracy (GDA)** | $\frac{\sum \mathbb{I}(D(U_{sem}, QoT) = \text{Action}_{GT})}{N} \times 100\%$ | $> 98\%$ | Routing fidelity on initial gate pass (approve / clarify / replan) |
| | **False Positive Rate (FPR)** | $\frac{\|\text{Risky Approved}\|}{\|\text{Risky Demands}\|} \times 100\%$ | **$0.0\%$** | Pre-deployment leak prevention on Classes II, III, and IV |
| | **Zero-Touch Autonomy** | $\frac{\text{Total} - \text{Interrupted}}{\text{Total}} \times 100\%$ | High | Autonomous touchless provisioning rate across all demands |

---

## 3. Test Corpus & Diurnal Operational Shift Framework

The benchmark models a 24-hour diurnal operational shift in a carrier-grade core optical network rather than an artificial homogeneous batch. In production network operations, intent arrivals form a non-homogeneous stochastic stream where routine, well-formed provisioning requests arrive alongside underspecified, physically infeasible, or corrupted requests.

The evaluation evaluates two datasets:
- **Compact Corpus (`test_corpus_compact.json`):** 20 demands (5 per class) for rapid pre-deployment iteration.
- **Full Benchmark Corpus (`test_corpus.json`):** 120 demands (30 per class) for statistical rigor and thesis validation.

| Class | Name | Compact | Full | Expected RADG Action | Operational Scenario / Dilemma |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **I** | **Nominal** | 5 | 30 | `approve` (0 interrupts) | Feasible requests with valid paths and realistic GSNR ($\le 18\text{ dB}$). **Always-On Dilemma**: Causes severe alert fatigue if verified manually. |
| **II** | **Ambiguous** | 5 | 30 | `clarify` (Phase 3b HITL) | Underspecified endpoints or colloquial SLA. Caught fail-fast by Semantic Gate before controller. |
| **III** | **Physically Infeasible** | 5 | 30 | `clarify` / `replan` | Demands violating GN-model reach ($> 28\text{ dB}$ GSNR). **LLM-Only Dilemma**: Causes runtime controller crashes if un-gated. |
| **IV** | **Adversarial** | 5 | 30 | `clarify` / `replan` | Contradictory constraints or hallucinated node names intercepted fail-fast. |

### Operational Dilemmas Grounding Multi-Baseline Comparison
1. **The Alert Fatigue Dilemma (Why Always-On HITL Fails):** Enforcing a static "always verify" policy forces human intervention on 100% of demands ($\Delta N_{hitl} \ge 1.0$), degrading operator cognitive alertness, turning human oversight into mechanical rubber-stamping, and introducing severe latency friction.
2. **The Cascading Controller Collapse Dilemma (Why LLM-Only Fails):** Removing human validation and defensive gating achieves rapid execution on nominal traffic but blindly forwards invalid lightpaths to the SDON/PCE controller ($FPR = 100\%$, 75% incident rate on balanced corpora), triggering runtime controller crashes and costly reactive recovery.
3. **The RADG Synthesis:** Risk-Adaptive Decision Gates provide the optimal Pareto boundary: touchless zero-fatigue execution on nominal demands ($N_{hitl}=0.0$), paired with deterministic fail-fast pre-deployment interception (clarify or replan) for ambiguous, physically unfeasible, and adversarial requests.

---

## 4. Execution Guide (`tests/evaluation/main.py`)

### 4.1 Prerequisites & Environment Setup
Ensure your local SLM or cloud API is configured in `.env`:
```bash
LLM_PROVIDER="ollama"
OLLAMA_MODEL="qwen2.5:3b"
OLLAMA_BASE_URL="http://localhost:11434/v1"
LLM_TIMEOUT=120.0
```

### 4.2 Interactive CLI
Launch the interactive terminal UI with arrow-key menus:
```bash
uv run python tests/evaluation/main.py
```

### 4.3 Direct CLI Execution
```bash
# Run Proposed RADG on compact corpus:
uv run python tests/evaluation/main.py --baseline proposed_radg --mode eval --corpus compact

# Run Always-On HITL baseline (evaluates nominal overhead):
uv run python tests/evaluation/main.py --baseline always_on_hitl --mode eval --corpus compact

# Run LLM-Only baseline (evaluates un-gated controller error):
uv run python tests/evaluation/main.py --baseline llm_only --mode eval --corpus compact

# Run all baselines sequentially:
uv run python tests/evaluation/main.py --baseline all --mode eval --corpus compact

# Interactive test of a single custom intent:
uv run python tests/evaluation/main.py --baseline proposed_radg --mode interactive --intent "Route 100G from Hamburg to Berlin with at least 15 dB GSNR"
```

### 4.4 Cross-Baseline Comparative Mode
To synthesize cross-baseline comparison matrices and executive visual figures:
```bash
# Compare the latest runs of each baseline and regenerate all figures:
uv run python tests/evaluation/main.py --mode compare

# Compare specific timestamped runs:
uv run python tests/evaluation/main.py --mode compare \
  --proposed-run 20260925_135330 \
  --hitl-run 20260925_135330 \
  --llm-run 20260925_135330

# Regenerate figures manually from a comparative results directory:
uv run python tests/evaluation/generate_visuals.py tests/evaluation/results/qwen2.5_3b/20260926_154258
```

### 4.5 Cross-Model Comparative LLMs Mode
To compare efficiency and gate accuracy across multiple LLM backends using the **interactive wizard**:
```bash
uv run python tests/evaluation/main.py
# Select: "Comparative LLMs Mode (Cross-model efficiency & gate accuracy figures)"
```

The wizard will:
1. **Scan eligible model/timestamp pairs** — only timestamps where all 3 baselines (`proposed_radg`, `always_on_hitl`, `llm_only`) have completed evaluation results are shown.
2. **Allow multi-selection** (minimum 2, maximum 4 models) with toggle-style checkboxes. The "Continue" option appears once at least 2 models are selected.
3. **Generate two cross-model figures** in `tests/evaluation/results/cross_model/[timestamp]/` alongside a companion `.md` metadata report.
4. **Backspace** at any point returns to the main mode selection.

---

## 5. Automated Recovery Protocol (Multi-Turn HITL)

When an intent triggers a decision gate during evaluation:
- **Phase 3b (`hitl_clarify`)**: The harness intercepts the pause, logs semantic divergence ($d_{sem}, U_{sem}$), and injects a standardized recovery intent:
  `"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`
- **Phase 6 (`radg`)**: If physical constraints fail, the harness provides a relaxed follow-up intent to verify Phase 7 synthesis recovery.
- **Dual-Action Logging**:
  - `initial_action`: Preserves the first-try gate verdict (`approve`, `clarify`, or `replan`) to evaluate Gate Decision Accuracy.
  - `final_action`: Records whether the multi-turn recovery successfully synthesized a valid planning report (`approve`).

---

## 6. Output Artifacts & Comparative Visuals

Results are persisted in timestamped folders organized hierarchically by sanitized model identifier:

### Baseline Execution Artifacts (`tests/evaluation/baselines/<baseline>/results/<LLM>/<timestamp>/`)
- `evaluation_results.json`: Comprehensive telemetry traces (PDDL ASTs, $U_{sem}$, routes, QoT SNR margins, token counts).
- `evaluation_results.csv`: Flat tabular export for rapid spreadsheet inspection.
- `evaluation_summary.md`: Publication-ready Four Pillars markdown report with risk class breakdown and timeout tracking.
- **Baseline Executive Visual Dashboard (16:9 widescreen):**
  * **Proposed RADG (`proposed_radg/`):** `presentation_slide_dashboard.png / .pdf` (16:9 executive infographic dashboard).
  * **Always-On HITL (`always_on_hitl/`):** `always_on_ablation_dashboard.png / .pdf` (16:9 operational tax infographic dashboard).
  * **LLM-Only (`llm_only/`):** `llm_only_ablation_dashboard.png / .pdf` (16:9 controller incident & root cause infographic dashboard).

*(Note: Per-baseline standalone figures such as `gate_accuracy_matrix` and `scalability_projection` are no longer generated in individual baseline directories to avoid clutter; they are consolidated directly in the global comparative suite below).*

### Global Comparative Visuals (`tests/evaluation/results/<LLM>/<timestamp>/`)
When running comparative mode or full multi-baseline evaluations, cross-baseline analytics and gate diagnostics are generated in `tests/evaluation/results/<LLM>/<timestamp>/`:
- `comparative_results_<timestamp>.json`: Combined cross-baseline raw traces and pillar metrics.
- `comparative_summary_<timestamp>.md`: Side-by-side executive comparison matrix across all baselines.
- `comparative_integrity_pillars.png / .pdf`: 2-panel standalone comparison for Pre-Deployment Integrity & Operator Burden (Pillars 2 & 3: FPR rate and Operator Interventions count).
- `comparative_efficiency_pillars.png / .pdf`: 2-panel standalone comparison for Computational Efficiency (Pillar 3: Latency Boxplot distributions on left, Token Footprint Stacked Bars highlighting useful vs. wasted compute on right).
- `comparative_pillars_breakdown.png / .pdf`: 4-panel comprehensive breakdown covering Integrity, Friction, Latency, and Tokens in a single grid.
- `comparative_deployment_flow_sankey.png / .pdf`: Publication-grade dual-panel Sankey flow contrasting autonomous gating against un-gated Controller Integrity Collapse.
- `comparative_scalability_projection.png / .pdf`: Scalability projection modeling cumulative operator interventions ($N_{hitl}$ cognitive fatigue) across the 120-demand diurnal operational stream, comparing Proposed RADG against Always-On HITL.
- `gate_accuracy_matrix.png / .pdf`: Multi-class confusion matrix and gate decision accuracy breakdown for Proposed RADG across all 4 risk classes, tracking first-try gating accuracy and timeout mitigation.

### Cross-Model Comparison Figures (`tests/evaluation/results/cross_model/<timestamp>/`)
When running **Comparative LLMs Mode**, cross-model figures are saved in a shared `cross_model/` directory (model-agnostic by design):
- `cross_model_efficiency.png / .pdf`: 2-panel grouped bar chart showing Median End-to-End Latency (left) and Median Token Footprint (right) grouped by model, with the 3 baselines as colored sub-bars inside each group. Captures LLM-dependent efficiency variability while holding baseline architecture constant.
- `cross_model_gate_accuracy.png / .pdf`: GDA% heatmap (model × risk class) using a Red–Yellow–Green colormap, paired with a horizontal bar summary showing overall GDA and annotated FPR per model. Validates the FPR ≈ 0% model-agnostic integrity invariant of the Proposed RADG.
- `cross_model_comparison_<timestamp>.md`: Metadata report listing compared models, their run timestamps, figure descriptions, and methodology notes explaining which figures are structural (invariant across models) vs. model-sensitive.
