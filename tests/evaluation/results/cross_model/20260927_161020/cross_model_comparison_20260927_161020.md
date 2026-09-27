---
title: "Cross-Model LLM Comparison — 20260927_161020"
date: 2026-09-27 16:10:22
tags: [cross-model, evaluation, radg, comparative]
status: active
---

# Cross-Model Comparison Report — `20260927_161020`

**Generated:** 2026-09-27 16:10:22  
**Models compared:** 2  

## Models & Runs

| # | Model Label | Directory | Timestamp |
|---|-------------|-----------|-----------|
| 1 | `gpt-6-luna` | `gpt-6-luna` | `20260927_144208` |
| 2 | `qwen2.5:3b` | `qwen2.5_3b` | `20260926_175018` |

## Generated Figures

| File | Description |
|------|-------------|
| `cross_model_efficiency.png/.pdf` | 2-panel grouped bar: Median Latency & Token Footprint per model per baseline. Captures LLM-dependent efficiency variability while holding baseline architecture constant. |
| `cross_model_gate_accuracy.png/.pdf` | GDA% heatmap (model × risk class) + overall GDA & FPR summary bar for Proposed RADG. Validates model-agnostic integrity guarantees. |

## Methodology Notes

- **Structural figures** (Sankey, Scalability Projection, Integrity Pillars) are NOT regenerated here because they are architectural properties of the RADG pipeline, not LLM-dependent. They are documented once per-model in `results/<model>/<timestamp>/`.
- **FPR** is expected to remain at `0.0%` across all models — this is the RADG system invariant. Any deviation should be investigated.
- **Latency and Token Footprint** are the primary variables that differ across LLM backends (local SLMs vs. cloud APIs).
- **GDA%** may show minor per-class variance driven by each model's conservatism on ambiguous intents.