---
title: "Weekly Report 2026-09-23"
date: 2026-09-23
tags: [weekly, report, thesis, evaluation, baselines, radg, hitl, llm-only, cli, sprint-4]
status: active
---

# Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date:
2026-09-23

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the previous report [[weekly_reports/Weekly_Report_20260922_Felipe_Abadia]])*
1. **Expand and Strengthen the Evaluation Environment:** Fortalecer y modernizar el harness y entorno de pruebas automatizadas con baselines comparativos modulares (Proposed RADG, Always-On HITL, LLM-Only) para benchmarking riguroso.
2. **Four Pillars Telemetry & Interactive Tooling:** Integrar la captura automatizada de métricas de los Cuatro Pilares y construir una interfaz unificada de ejecución interactiva y por lotes.
3. **Drafting Preparation for Thesis Chapter 5:** Preparar el entorno experimental y datos preliminares para iniciar la redacción formal del Capítulo 5 de la tesis (Evaluación Experimental, Resultados y Benchmarks Comparativos).

---

## 2. What did I actually accomplish?

1. **Modular Comparative Baselines Architecture (`tests/evaluation/baselines/`):**
   - Engineered a modular comparative baselines package in [`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/) adhering to strict DRY principles, reusing production pipeline modules from `src/` without duplicating core logic:
     * **Proposed RADG (`proposed_radg/`):** Full V5 neurosymbolic pipeline with two-stage fail-fast Risk-Adaptive Decision Gates (Semantic RADG at Phase 3 and Physical RADG at Phase 6).
     * **Always-On HITL (`always_on_hitl/`):** Enforces mandatory Turn 1 operator clarification on Nominal traffic ($N_{hitl}=1$), followed by automated recovery with standard follow-up intent (`"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`) to quantify latency, token friction, and operator fatigue overhead.
     * **LLM-Only (`llm_only/`):** Completely bypasses the Phase 3 Semantic Gate, feeding unvalidated PDDL configurations directly to the physical layer; Phase 6 acts as a controller deployment surrogate triggering replan interrupts on invalid traffic, exposing False Positive Rate ($FPR$), Unfeasible Approval Rate ($UAR$), and controller-level replanning latencies.
     * **Common Execution Engine & Metrics (`common/`):** Implemented `runner.py` with multi-turn loop and automated recovery, `TokenTracker` callback, `metrics.py` implementing all Four Pillars mathematical formulas, and `reporter.py` providing snapshot-preserving multi-format telemetry exports (JSON, CSV, Markdown) and automated visual asset triggers.

2. **Unified Interactive & Benchmark Terminal CLI (`tests/evaluation/main.py`):**
   - Developed an interactive CLI entrypoint in [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) powered by `rich` and `questionary`:
     * **Interactive Mode:** Real-time terminal dashboard with colored panels for each pipeline phase, displaying intermediate PDDL generation, semantic uncertainty scores ($U_{sem}$), physical GSNR values, and live operator pauses on HITL interrupts.
     * **Evaluation Benchmark Mode:** Automated batch execution of the compact test corpus with real-time progress bars, aggregated metric tables, and persistent exports into `tests/evaluation/results/`.

3. **Strict TDD Unit Testing Suite (337/337 Tests Passing):**
   - Authored 16 comprehensive unit tests in [`tests/unit/test_evaluation_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_evaluation_baselines.py) covering graph compilation, custom node behavior across turns, and Four Pillars metric calculations.
   - All 337 unit tests across the entire repository passing cleanly in 2.94s under pytest (`pytest tests/unit/`).
   - Repository-wide linting verified 100% clean (`ruff check src/ tests/`).

4. **Live Empirical Verification with Local Open-Weights Inference (`qwen2.5:3b`):**
   - Successfully verified live end-to-end execution of all three baselines against local Ollama inference (`qwen2.5:3b` on WSL2 RTX 3050):
     * `proposed_radg`: Nominal intent passed cleanly on Turn 1 in 13.08s with $N_{hitl}=0$.
     * `always_on_hitl`: Mandatory Turn 1 clarification triggered as designed, followed by automated recovery in 11.09s ($N_{hitl}=1$).
     * `llm_only`: Reached Phase 6 controller surrogate, triggered replan interrupt on Turn 1, and successfully recovered in 11.65s.

5. **Evaluation Documentation & Standards Alignment:**
   - Updated [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) with the new modular directory tree, execution commands for the CLI and baseline evaluation runners, and metric definitions.
   - Documented the session architecture in [`session_20260923_Modular_Baselines_and_Evaluation_CLI.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/session_summary/session_20260923_Modular_Baselines_and_Evaluation_CLI.md).

---

## 3. What do I plan to accomplish next week?

1. **Execute Comprehensive Comparative Benchmarking:** Run full batch evaluation across all 20 demands in `test_corpus_compact.json` comparing Proposed RADG against Always-On HITL and LLM-Only baselines, analyzing latency, token consumption, and safety tradeoffs.
2. **Draft Thesis Chapter 5 (Experimental Results & Evaluation):** Begin formal drafting of Chapter 5 integrating empirical tables, Four Pillars radar charts, and comparative ablation figures.
3. **Academic Presentation Rehearsal:** Review the comparative baseline outcomes and updated slide deck with academic advisor Prof. Massimo Tornatore.

---

## 4. Do You Need Support?

- **Current Status:** The comparative baselines and interactive CLI are fully functional, verified with 337 passing unit tests and live local LLM inference. Ready to generate batch benchmark results for Chapter 5.
- **Advisor Review:** Ready to schedule presentation rehearsal and benchmark review with Prof. Massimo Tornatore.

---

## 5. One-Sentence Summary

I designed and implemented the modular comparative baselines architecture and unified interactive CLI for the Four Pillars evaluation benchmark, verified all 337 unit tests under strict TDD, and validated live runs across all baselines using local open-weights inference.
