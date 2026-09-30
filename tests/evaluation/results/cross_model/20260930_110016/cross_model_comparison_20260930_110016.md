---
title: "Cross-Model LLM Comparison — 20260930_110016"
date: 2026-09-30 11:00:18
tags: [cross-model, evaluation, radg, comparative]
status: active
---

# Cross-Model Comparison Report — `20260930_110016`

**Generated:** 2026-09-30 11:00:18  
**Models compared:** 3  

## Models & Runs

| # | Model Label | Directory | Timestamp |
|---|-------------|-----------|-----------|
| 1 | `gpt-6-luna` | `gpt-6-luna` | `20260928_111332` |
| 2 | `qwen2.5:3b` | `qwen2.5_3b` | `20260930_070116` |
| 3 | `gpt-5-nano` | `gpt-5-nano-2025-08-07` | `20260928_124751` |

## Generated Figures

| File | Description |
|------|-------------|
| `cross_model_gate_accuracy.png/.pdf` | Action Distribution Matrix per model + Overall GDA & FPR summary (Cleveland Lollipop scale, 85%–100%). Validates model-agnostic integrity guarantees. |

## Methodology Notes

- **Structural figures** (Sankey, Scalability Projection, Integrity Pillars) are NOT regenerated here because they are architectural properties of the RADG pipeline, not LLM-dependent. They are documented once per-model in `results/<model>/<timestamp>/`.
- **FPR** is expected to remain at `0.0%` across all models — this is the RADG system invariant. Any deviation should be investigated.
- **Latency and Token Footprint** are the primary variables that differ across LLM backends (local SLMs vs. cloud APIs).
- **GDA%** may show minor per-class variance driven by each model's conservatism on ambiguous intents.