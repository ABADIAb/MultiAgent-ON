# Sprint 4 Evaluation Environment & Benchmark Guide

This directory contains the automated, reproducible benchmark suite for evaluating the **LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning** pipeline (V5) across the standardized **17-Node Nobel-Germany Core Optical Backbone**.

---

## 1. Directory Structure

```text
tests/evaluation/
├── test_corpus_compact.json    # Standard 20-demand benchmark corpus (4 balanced risk classes)
├── run_nominal_eval.py         # Automated evaluation runner for Nominal Intents (Class I)
├── results/                    # Generated evaluation artifacts
│   ├── nominal_results.json    # Granular per-turn telemetry & PDDL AST records
│   ├── nominal_results.csv     # Exported tabular metrics
│   └── nominal_summary.md      # Consolidated markdown summary table
└── README.md                   # Environment, methodology, and execution instructions
```

---

## 2. Test Corpus: 4 Risk Classes

The dataset (`test_corpus_compact.json`) comprises 20 demands balanced equiprobably across 4 risk classes:

| Class | Name | Size | Expected RADG Action | Key Objective |
| :---: | :--- | :--: | :------------------: | :------------ |
| **I** | **Nominal** | 5 | `approve` (0 interrupts) | Feasible requests with valid optical paths and realistic GSNR ($\le 18\text{ dB}$). |
| **II** | **Ambiguous** | 5 | `clarify` (Phase 3b HITL) | Underspecified endpoints or colloquial SLA, caught fail-fast by Semantic Gate. |
| **III** | **Physically Infeasible** | 5 | `replan` (Phase 6 RADG) | Demands violating GN-model physical reach ($> 28\text{ dB}$ GSNR on multi-hop). |
| **IV** | **Adversarial** | 5 | `clarify` (Phase 3b / CFG) | Contradictory constraints or hallucinated node names intercepted by CFG / Gate. |

---

## 3. How to Run the Nominal Intents Evaluation

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

### Execution Command
Run the evaluation directly via `uv`:
```bash
uv run python tests/evaluation/run_nominal_eval.py
```

Optional CLI flags:
```bash
# Override model or timeout
uv run python tests/evaluation/run_nominal_eval.py --model qwen2.5:3b --timeout 120.0

# Run with alternative providers
uv run python tests/evaluation/run_nominal_eval.py --provider openrouter --model inclusionai/ling-3.0-flash-vl:free
```

---

## 4. Automated Recovery Protocol (Multi-Turn HITL)

When an intent fails a decision gate:
- **Phase 3b (`hitl_clarify`)**: The evaluation harness intercepts the pause, logs the semantic divergence ($d_{sem}, U_{sem}$), and automatically injects the standardized follow-up recovery intent:
  `"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`
- **Phase 6 (`radg`)**: If physical constraints fail, the harness provides the relaxed follow-up intent to allow completion through to Phase 7 (Synthesis).
- **Dual-Action Logging**:
  - `initial_action`: Preserves the first-try gate verdict (`approve`, `clarify`, or `replan`) to evaluate gate accuracy.
  - `final_action`: Records whether recovery succeeded in synthesizing a valid planning report (`approve`).

---

## 5. Output Artifacts

All evaluation outputs are saved to `tests/evaluation/results/`:
- `nominal_results.json`: Full diagnostic trace including PDDL strings, AST CFG pass status, reconstructed natural language, $U_{sem}$ scores, candidate routes, and QoT SNR margins.
- `nominal_results.csv`: Tabular spreadsheet format for rapid plotting and aggregation.
- `nominal_summary.md`: Publication-ready summary table for reports and thesis documentation.
