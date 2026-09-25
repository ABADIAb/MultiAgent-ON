---
title: "Technical Handover: Multi-Class Visuals, Median Metrics & Clean Repository"
date: 2026-09-25
tags: [session-summary, handover, visuals, median-metrics, git-hygiene, baselines]
status: active
---

# Technical Handover Card: 2026-09-25 (Multi-Class Visuals & Median)

## 1. Scope & Objective
Resolve the latency inversion on benchmark run 173441 via median metrics, upgrade Always-On and LLM-Only Wasted Compute across all 4 intent classes, disaggregate Pillars 3 & 4 in comparative breakdowns, introduce dual-panel Sankey, and purge `.agents/` tracking.

## 2. Key Architectural Decisions
- **Median vs. Mean Telemetry:** Diagnosed nominal latency skew from 3 Ollama runtime stalls (+500s across 30 demands). Integrated median metrics in `metrics.py`, `reporter.py`, and `generate_visuals.py`, revealing true steady-state nominal latency ($3.80\text{s}$ Proposed vs. $11.85\text{s}$ Always-On, $3.12\times$ speedup).
- **Multi-Class Wasted Compute:** Upgraded `plot_always_on_wasted_compute` and `plot_llm_only_wasted_compute` to plot all 4 intent classes + Overall, contrasting directly against the Proposed RADG floor with stacked deltas.
- **Grouped Risk-Class Breakdown:** Converted Panels 3 & 4 of `comparative_pillars_breakdown` to grouped bars per baseline across Nominal, Ambiguous, Infeasible, and Adversarial classes using robust medians.
- **Dual-Panel Comparative Sankey:** Created `comparative_deployment_flow_sankey` contrasting safe pre-deployment gating with blind admission controller collapse (75% incident rate).
- **Repository Git Hygiene:** Untracked `.agents/` directory from git index (`git rm -r --cached .agents`), enforcing strict remote hygiene via `.gitignore`.

## 3. Test & Code Health
- **Unit Suite:** 349 passed in 6.44s (`uv run pytest tests/unit/`).
- **Visual Asset Verification:** Regenerated all PNG/PDF assets for historical runs (`run_20260925_173441` and `run_20260925_135330`) with exit code 0.
- **Documentation:** Synchronized all 4 READMEs (`tests/evaluation/README.md`, `always_on_hitl/README.md`, `llm_only/README.md`, `proposed_radg/README.md`).

## 4. Exact Cursor & Next Prompt
- **Cursor:** `tests/evaluation/baselines/proposed_radg/results/run_20260925_173441/` and `tests/evaluation/generate_visuals.py`.
- **Next Prompt:** "Continuemos con la revisión y corrección de detalles técnicos y visuales de las gráficas de proposed_radg (gate accuracy matrix, distribuciones de latencia/tokens y dashboard)."
