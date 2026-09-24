---
title: "Session Summary: 2026-09-24 - LLM-Only Baseline Calibration, Wasted Compute Profiling & Telemetry Artifact Refactoring"
date: 2026-09-24
tags: [session-summary, debrief, evaluation, baselines, llm-only, ablation, controller-incident, wasted-compute, telemetry, artifacts, sprint-4]
status: active
---

# Session Summary: 2026-09-24 - LLM-Only Baseline Calibration, Wasted Compute Profiling & Telemetry Artifact Refactoring

## 1. Executive Summary

In this session, I completed the calibration and formalization of the **`LLM-Only`** ablation baseline within the Sprint 4 evaluation framework ([`tests/evaluation/baselines/llm_only/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only/)), eliminated redundant telemetry artifact generation across all baselines, and established repository-level hygiene rules for generated evaluation visuals.

First, I resolved a critical design question regarding how to rigorously benchmark an un-gated LLM-only pipeline. In an architecture without pre-deployment decision gates ($N_{gates} = 0$), measuring **Gate Decision Accuracy (GDA)** is conceptually invalid. Instead, I enforced an admission policy of blind forwarding ($\mathcal{A}_{pre} = \{\text{approve}\}$), reflecting a $100\%$ False Positive Rate ($FPR$) on risky demands. I modeled the failure mode as a reactive SDON controller runtime rejection: Class I (Nominal) traffic succeeds on Turn 1, whereas Classes II (Ambiguous), III (Infeasible), and IV (Adversarial) trigger controller deployment errors ($75\%$ incident rate on the balanced corpus), forcing a reactive replan and human recovery turn. To expose the operational penalty of omitting pre-deployment gating, I instrumented cumulative latency and token accounting to measure the compute wasted in the aborted Turn 1.

Second, I authored custom visual analytics tailored to `LLM-Only`: a **Pre-Deployment Blind Forwarding vs Controller Runtime Rejection Matrix** (`deployment_failure_matrix`), a **Wasted Compute Overhead Breakdown** (`wasted_compute_overhead`), and a 16:9 widescreen presentation slide graphic (`llm_only_ablation_dashboard`).

Third, I refactored the telemetry exporter ([`reporter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/reporter.py)) to eliminate unversioned duplicate file outputs (`evaluation_results.json`, `.csv`, `.md`), standardizing on a single, self-describing timestamped artifact set per run directory (`evaluation_results_<timestamp>.json`, etc.). I upgraded [`main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) and [`generate_visuals.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/generate_visuals.py) with dynamic globbing to resolve runs robustly, deleted all duplicate unversioned files from existing results directories, and updated [`.gitignore`](file:///home/felipeab/MultiAgentON/.gitignore) to exclude all generated binary figures (PNG/PDF) while whitelisting thesis documentation assets.

All changes were validated against the full unit test suite (344/344 passing tests in 6.69s) and verified with 100% clean Ruff static analysis.

---

## 2. Key Accomplishments

### 2.1 Un-Gated LLM-Only Baseline Calibration
- **State Channel Preservation (`src/core/state.py`):** Added `intent_class: str | None` to `AgentState` to prevent LangGraph from dropping the intent classification metadata channel during execution.
- **Blind Pre-Deployment Forwarding Policy:** Enforced `initial_action = "approve"` for all intents in `llm_only` within [`runner.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/runner.py) and [`evaluator.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only/evaluator.py), capturing total pre-deployment safety collapse ($FPR = 100.0\%$, $UAR = 75.0\%$).
- **SDON Controller Surrogate Runtime Modeling:**
  - Class I (Nominal) traffic provisions smoothly on Turn 1 with zero controller errors.
  - Classes II, III, and IV simulate controller runtime rejections (`controller_verdict = "replan"`, `controller_error = True`, `success = False`), triggering a reactive recovery turn ($N_{hitl} = 1$).
  - Turn 1 physical QoT results are preserved in `turn_1_qot_results` to prevent Turn 2 recovery from masking pre-deployment optical reach violations in `is_unfeasible_approval`.
- **Gate Metric Omission & Executive Reporting:** Gate Decision Accuracy (GDA) is formally marked as **N/A** in specialized `evaluation_summary.md` reports for `llm_only`, shifting the focus to pre-deployment risk interception ($0.0\%$), controller incident rate ($75.0\%$), and wasted compute penalties.

### 2.2 Tailored Visual Analytics Suite
- **Deployment Failure Matrix (`deployment_failure_matrix.png` / `.pdf`):** Juxtaposes the 100% blind pre-deployment approval against controller runtime incident distributions across all 4 risk classes.
- **Wasted Compute Overhead (`wasted_compute_overhead.png` / `.pdf`):** Dual-panel visualization quantifying the latency and token waste incurred during aborted Turn 1 deployment attempts prior to reactive recovery.
- **Ablation Dashboard (`llm_only_ablation_dashboard.png` / `.pdf`):** 16:9 composite slide summarizing the architectural fragility and compute overhead of eliminating pre-deployment neurosymbolic gates.

### 2.3 Telemetry Artifact Refactoring & Git Hygiene
- **Elimination of Duplicate Files:** Refactored [`reporter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/reporter.py) to write only a single set of timestamped files per run (`evaluation_results_<timestamp>.json`, `.csv`, `.md`, and comparative equivalents), removing redundant unversioned copies.
- **Robust Dynamic Run Discovery:** Updated `list_available_runs()` and `resolve_baseline_run()` in [`main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) and target resolution in [`generate_visuals.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/generate_visuals.py) to detect timestamped evaluation JSON files via pattern matching.
- **Workspace Cleanup:** Deleted all 14 un-timestamped duplicate copies across all baseline run directories and common results.
- **Git Ignore Rules ([`.gitignore`](file:///home/felipeab/MultiAgentON/.gitignore)):** Configured git rules to prevent committing generated PNG and PDF artifacts while whitelisting thesis documentation diagrams in `docs/LLM_Wiki/`.

---

## 3. Verification & Test Suite

1. **Unit Test Suite:**
   ```bash
   uv run pytest tests/unit/
   # 344 passed, 3 warnings in 6.69s
   ```
2. **Static Analysis & Formatting:**
   ```bash
   uv run ruff check src/ tests/
   # All checks passed!
   ```
3. **Git Status Audit:** Verified that no PNGs or PDFs in `tests/evaluation/` appear in git status, and only clean timestamped results files are tracked.

---

## 4. Next Steps
- Run the full 107-demand benchmark corpus across all three baselines using the local `qwen2.5:3b` model to collect final publication data.
- Integrate the comparative radar and bar charts into the Overleaf manuscript for Thesis Chapter 5.
