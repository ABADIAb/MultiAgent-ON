---
title: "Weekly Report 2026-09-29"
date: 2026-09-29
tags: [weekly, report, thesis, evaluation, baselines, radg, hitl, llm-only, cli, radar-chart, pillars-bar, sprint-4]
status: active
---

# Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date:
2026-09-29

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the previous report [[weekly_reports/Weekly_Report_20260922_Felipe_Abadia]])*
1. **Expand and Strengthen the Evaluation Environment:** Fortalecer y modernizar el harness y entorno de pruebas automatizadas con baselines comparativos modulares (Proposed RADG, Always-On HITL, LLM-Only) para benchmarking riguroso.
2. **Four Pillars Telemetry & Interactive Tooling:** Integrar la captura automatizada de métricas de los Cuatro Pilares y construir una interfaz unificada de ejecución interactiva y por lotes.
3. **Drafting Preparation for Thesis Chapter 5:** Preparar el entorno experimental, herramientas de visualización comparativa y datos preliminares para iniciar la redacción formal del Capítulo 5 de la tesis (Evaluación Experimental, Resultados y Benchmarks Comparativos).

---

## 2. What did I actually accomplish?

1. **Modular Comparative Baselines Architecture ([`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/)):**
   - Engineered a modular comparative baselines package in [`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/) adhering to strict DRY principles, reusing production pipeline modules from `src/` without duplicating core logic:
     * **Proposed RADG (`proposed_radg/`):** Full V5 neurosymbolic pipeline with two-stage fail-fast Risk-Adaptive Decision Gates (Semantic RADG at Phase 3 and Physical RADG at Phase 6).
     * **Always-On HITL (`always_on_hitl/`):** Enforces mandatory Turn 1 operator clarification on Nominal traffic ($N_{hitl}=1$), followed by automated recovery with standard follow-up intent (`"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`) to quantify latency, token friction, and operator fatigue overhead.
     * **LLM-Only (`llm_only/`):** Completely bypasses the Phase 3 Semantic Gate, feeding unvalidated PDDL configurations directly to the physical layer; Phase 6 acts as a controller deployment surrogate triggering replan interrupts on invalid traffic, exposing False Positive Rate ($FPR$), Unfeasible Approval Rate ($UAR$), and controller-level replanning latencies.
     * **Common Execution Engine & Metrics (`common/`):** Implemented `runner.py` with multi-turn loop and automated recovery, `TokenTracker` callback, `metrics.py` implementing all Four Pillars mathematical formulas, and `reporter.py` providing snapshot-preserving multi-format telemetry exports (JSON, CSV, Markdown) and automated visual asset triggers.

2. **Segregated Baseline Results Storage & Version Resolution:**
   - Standardized per-baseline evaluation storage into isolated timestamped directories:
     * `tests/evaluation/baselines/proposed_radg/results/run_YYYYMMDD_HHMMSS/`
     * `tests/evaluation/baselines/always_on_hitl/results/run_YYYYMMDD_HHMMSS/`
     * `tests/evaluation/baselines/llm_only/results/run_YYYYMMDD_HHMMSS/`
   - Each run directory encapsulates full evaluation artifacts: `evaluation_results.json`, `evaluation_results.csv`, `evaluation_summary.md`, and per-baseline visual charts (`gate_accuracy_matrix`, `latency_tokens_overhead`, `presentation_slide_dashboard` in 300 DPI PNG and vector PDF).
   - Implemented run version resolution logic (`resolve_baseline_run()`): users can specify exact historical run timestamps via CLI flags (`--proposed-run`, `--hitl-run`, `--llm-run`) or interactive selection prompts, defaulting automatically to the most recent timestamped run when unspecified.

3. **Comparative Analysis Mode & Automated Visualization Suite:**
   - Extended [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) with `--mode compare`, enabling instantaneous offline cross-baseline synthesis without requiring active LLM connectivity:
     * **Four Pillars Grouped Bar Chart (`comparative_pillars_bar.png` / `.pdf`):** A 4-panel grouped comparative figure illustrating Unfeasible Approval Rate ($UAR$), Human-in-the-Loop Interventions ($N_{hitl}$), End-to-End Latency ($T_{E2E}$), and Token Footprint ($T_{tokens}$) side-by-side across all three baselines.
     * **5-Axis Polar Radar Chart (`comparative_radar_chart.png` / `.pdf`):** A publication-grade radar chart mapping the Four Pillars trade-offs: Safety ($1 - UAR$), Autonomy ($1 - \text{normalized } N_{hitl}$), Speed ($1 - \text{normalized } T_{E2E}$), Token Efficiency ($1 - \text{normalized } T_{tokens}$), and PDDL Structural Quality ($CFG\text{-}PR$).
     * **Consolidated Comparative Markdown Report:** Automatically generated in `tests/evaluation/baselines/common/results/run_YYYYMMDD_HHMMSS/comparative_summary.md`, tabulating exact metric deltas and thesis evaluation highlights.

4. **CLI Ergonomics & Terminal Robustness Fixes:**
   - **Graceful Interrupt Handling:** Resolved a critical terminal freeze issue caused by `questionary` catching `SIGINT` internally and returning `None`. Implemented `prompt_select()` and `prompt_text()` wrappers, alongside outer `KeyboardInterrupt` handlers in both [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) and [`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py), ensuring immediate, clean exits on `Ctrl+C`.
   - **Full Planning Report Display:** Eliminated an arbitrary hardcoded character slice (`[:1000]`) in the CLI report viewer, ensuring the complete, auditable Phase 7 Planning Report (including full path hops, SNR margins, and decision traces) renders without truncation.

5. **Legacy Runner & Results Archiving:**
   - Archived the legacy monolithic runner [`run_evaluation.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/archive/run_evaluation.py) and historical test results into [`tests/evaluation/archive/`](file:///home/felipeab/MultiAgentON/tests/evaluation/archive/), establishing a clean separation between legacy artifacts and the active modular baseline architecture.
   - Updated [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) with comprehensive instructions for running individual baselines, configuring run selections, and executing comparative analyses.

6. **Evaluation Harness Multi-Turn Resilience & Watchdog Hardening:**
   - Engineered robust multi-stage extraction of semantic divergence $U_{sem}$ in [`src/nodes/semantic_gate_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py), prioritizing decimal scores and keyword indicators over bare integers to prevent false ambiguities from model reasoning text.
   - Introduced an interactive direct operator approval bypass in [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) when $v_{struct}=1$, alongside explicit turn-limit overrun alerts.
   - Enforced a 5-minute (300.0s) global wall-clock watchdog per demand (`DEFAULT_INTENT_TIMEOUT`) and explicit outcome taxonomy (`completed`, `timeout`, `max_turns_exceeded`) in [`tests/evaluation/baselines/common/runner.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/runner.py) and baseline evaluators.
   - Integrated Task Completion Rate (TCR) and timeout tracking in Four Pillars telemetry formulas ([`tests/evaluation/baselines/common/metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/metrics.py)).

7. **Strict TDD Unit Testing Suite (344/344 Tests Passing):**
   - Maintained full test suite integrity with dedicated baseline and gate parser tests in [`tests/unit/test_evaluation_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_evaluation_baselines.py) and [`tests/unit/test_semantic_gate.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_semantic_gate.py).
   - All 344 unit tests passing cleanly in ~6.7s under pytest (`pytest tests/unit/`).
   - Static analysis verified 100% clean with zero warnings or errors across the entire codebase (`ruff check src/ tests/`).

8. **LLM-Only Baseline Calibration & Controller Incident Model:**
   - Enforced blind pre-deployment admission policy ($\mathcal{A}_{pre} = \{\text{approve}\}$), formally exposing a 100% False Positive Rate ($FPR$) on risky demands.
   - Modeled reactive SDON controller runtime rejections: Class I (Nominal) provisions cleanly in Turn 1, whereas Classes II (Ambiguous), III (Infeasible), and IV (Adversarial) trigger controller deployment errors ($75\%$ incident rate on the balanced corpus), forcing a reactive replan and human recovery turn.
   - Omitted inapplicable gate metrics (Gate Decision Accuracy marked N/A) and instrumented cumulative latency and token accounting to capture compute wasted during aborted Turn 1 deployments.
   - Designed custom visual outputs: `deployment_failure_matrix`, `wasted_compute_overhead`, and a 16:9 `llm_only_ablation_dashboard`.

9. **Telemetry Artifact Refactoring & Repository Hygiene:**
   - Refactored [`reporter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/reporter.py) to output only a single set of self-describing timestamped files per run (`evaluation_results_<timestamp>.json`, `.csv`, `.md`, and comparative equivalents), completely eliminating redundant unversioned duplicates.
   - Upgraded [`main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) and [`generate_visuals.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/generate_visuals.py) with dynamic globbing to resolve runs robustly.
   - Deleted all 14 redundant unversioned copies from existing baseline directories and updated [`.gitignore`](file:///home/felipeab/MultiAgentON/.gitignore) to exclude generated evaluation PNG/PDF figures while preserving thesis documentation assets.

10. **LLM-Only Analytics Polish & Root Cause Fusion:**
   - Upgraded the LLM-only ablation dashboard by integrating a cascading Sankey Diagram that visually breaks down controller incidents by Root Cause (Missing Params, GN-Model Violations, Syntax Conflicts).
   - Hardened executive KPIs to explicitly track Unsafe Approval Rate (UAR) and Reactive HITL Interventions, linking the absence of defensive gating directly to operator fatigue and system compromise.
   - Pruned redundant figures from the `llm_only` baseline output, ensuring a concise and focused evaluation asset footprint.

---

## 3. What do I plan to accomplish next week?

1. **Execute Comprehensive Comparative Benchmarking:** Run full batch evaluation across all 20 demands in `test_corpus_compact.json` comparing Proposed RADG against Always-On HITL and LLM-Only baselines, analyzing latency, token consumption, and safety tradeoffs.
2. **Draft Thesis Chapter 5 (Experimental Results & Evaluation):** Begin formal drafting of Chapter 5 integrating empirical tables, Four Pillars radar charts, and comparative ablation figures.
3. **Academic Presentation Rehearsal:** Review the comparative baseline outcomes and updated slide deck with academic advisor Prof. Massimo Tornatore.

---

## 4. Do You Need Support?

- **Current Status:** The comparative baselines, segregated telemetry architecture, cross-baseline visual generators, and interactive CLI are fully functional and tested.
- **Advisor Review:** Ready to schedule presentation rehearsal and benchmark review with Prof. Massimo Tornatore once the full batch comparison run is generated.

---

## 5. One-Sentence Summary

I calibrated the un-gated LLM-Only ablation baseline with controller runtime error modeling, wasted compute profiling, and custom visual analytics, eliminated duplicate telemetry artifacts across all baselines, and established repository-level hygiene rules for generated figures, validated with 344 passing unit tests.
