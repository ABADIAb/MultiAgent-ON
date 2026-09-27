---
title: "Weekly Report 2026-09-29"
date: 2026-09-29
tags: [weekly, report, thesis, evaluation, baselines, radg, hitl, llm-only, cli, pillars-bar, sprint-4, openai, cross-model, comparative-llms]
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

1. **Modular Comparative Baselines Engine ([`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/)):**
   - Engineered a DRY, production-aligned evaluation framework benchmarking three core architectures: **Proposed RADG** (two-stage fail-fast gates), **Always-On HITL** (mandatory Turn 1 clarification to quantify cognitive friction), and **LLM-Only** (bypassed semantic validation with reactive controller-incident replanning).
   - Standardized the multi-turn execution engine ([`runner.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/runner.py)) with automated recovery, a 5-minute watchdog per intent, median-based Four Pillars telemetry calculations ([`metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/metrics.py)), and snapshot-preserving JSON/CSV/Markdown exports.

2. **Hierarchical Telemetry Storage & Version Resolution:**
   - Restructured results into sanitized model directories (`<baseline>/results/<LLM>/<timestamp>/` and comparative results under `tests/evaluation/results/<LLM>/<timestamp>/`), eliminating unversioned file redundancy.
   - Built a dynamic run version resolver (`resolve_baseline_run()`) in [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py), allowing instant switching between specific historical benchmarks via CLI flags or interactive selection.

3. **Publication-Ready Comparative Visual Suite ([`tests/evaluation/generate_visuals.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/generate_visuals.py)):**
   - Implemented an automated offline visual generation suite producing 300 DPI PNG and vector PDF assets: partitioned pillars (`comparative_integrity_pillars`, `comparative_efficiency_pillars`), detailed breakdowns (`comparative_pillars_breakdown`), deployment flow Sankey, and dynamic-width gate accuracy matrix (`gate_accuracy_matrix`).
   - Harmonized baseline chromatic identities (Proposed RADG: Blue, Always-On: Purple, LLM-Only: Orange) and standardized terminology from "safety" to "integrity" across all figures, legends, and docs.
   - Refined the scalability projection (`comparative_scalability_projection`) to focus on operator cognitive relief by demonstrating 28 interventions averted against Always-On HITL fatigue.

4. **Multi-Model Provider Expansion & Interactive CLI Ergonomics:**
   - Integrated OpenAI multi-model support (`src/core/llm.py`) with support for `gpt-6-luna`, parameterizing reasoning effort (`none` vs. `low`) to benchmark cost/latency trade-offs ($\approx 10$ min clock savings and $-\$0.025$ USD with `none`).
   - Engineered bidirectional wizard navigation with `prompt_toolkit` keybindings (`Backspace`, `Ctrl+H`, `Escape`) across `src/main.py` and `tests/evaluation/main.py`, alongside graceful `Ctrl+C` interrupt handlers and un-truncated Phase 7 Planning Report rendering.

5. **Adversarial Invariant Realignment & Full Test Suite Integrity:**
   - Hardened Rule 4 in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) to preserve corrupted and non-numeric literals (`NaN dB`), guaranteeing deterministic CFG failure and immediate Phase 3b fail-fast ($U_{sem}=1.000$).
   - Realigned physical safety telemetry to enforce the theoretical $UAR=0.0\%$ invariant and un-gated baseline calibration ($FPR=100\%$).
   - Maintained full test suite integrity with 358 passing unit tests (`uv run pytest tests/unit/`) and 100% clean static analysis (`uv run ruff check src/ tests/`).

6. **Cross-Model Comparative LLMs Mode ([`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py), [`tests/evaluation/generate_visuals.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/generate_visuals.py)):**
   - Implemented `find_complete_model_runs()` to scan all 3 baselines and surface only timestamps where ALL baselines have completed results, enforcing strict cross-model comparability eligibility.
   - Added a new **"Comparative LLMs Mode"** wizard step to the interactive CLI: toggle-style multi-model selection (2 min, 4 max), "Continue" unlocked at 2nd model, full Backspace navigation.
   - Implemented two new cross-model publication figures: `plot_cross_model_efficiency()` (2-panel grouped bar: median latency + median token footprint by model per baseline) and `plot_cross_model_gate_accuracy_heatmap()` (RdYlGn GDA% heatmap by model × risk class, paired with FPR-annotated overall GDA bar).
   - Outputs persisted to `tests/evaluation/results/cross_model/<timestamp>/` with a companion `.md` metadata report. Structural/invariant figures (Sankey, Pillars) excluded by design — they capture pipeline architecture, not LLM backend effects.

---

## 3. What do I plan to accomplish next week?

1. **Draft Thesis Chapter 5 (Experimental Results & Evaluation):** Formally draft Chapter 5 incorporating empirical benchmark tables, Four Pillars radar charts, multi-class breakdowns, and comparative ablation figures.
2. **Multi-Model Cross-LLM Benchmarks:** Execute full-corpus runs on a second model (e.g., `phi4-mini:latest` or a cloud API) and trigger the new **Comparative LLMs Mode** to generate the first real cross-model efficiency and gate accuracy figures.
3. **Academic Presentation Rehearsal:** Review the full-corpus comparative baseline outcomes and updated slide deck with academic advisor Prof. Massimo Tornatore.

---

## 4. Do You Need Support?

- **Current Status:** Comparative baselines, segregated telemetry architecture, cross-baseline and cross-model visual generators, OpenAI multi-model provider, and interactive CLI navigation are fully functional with 358 passing unit tests.
- **Advisor Review:** Ready to schedule presentation rehearsal and benchmark review with Prof. Massimo Tornatore based on the empirical comparative data.

---

## 5. One-Sentence Summary

I engineered a modular comparative evaluation suite with hierarchical telemetry and publication-ready visuals, integrated OpenAI provider and bidirectional CLI navigation, enforced adversarial invariants with 358 passing unit tests, and implemented a Cross-Model Comparative LLMs Mode that automatically surfaces eligible runs and generates cross-model efficiency and gate accuracy figures.
