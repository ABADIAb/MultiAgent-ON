---
title: "Technical Handover: LLM-Only Error Mock & Comparative Metrics"
date: 2026-09-25
tags: [session-summary, handover, llm-only, evaluation, radar-metrics]
status: active
---

# Technical Handover Card: 2026-09-25

## 1. Scope & Objective
Formalize the token penalty simulation for the `LLM-Only` baseline via a mock RESTConf error payload, validate the Always-On HITL data filling strategy, and define orthogonal axes for the Four Pillars Comparative Radar Chart.

## 2. Key Architectural Decisions
- **LLM-Only Incident Recovery Loop:** Instead of a clean replan string, the baseline will inject a realistic RFC 8040 RESTConf JSON error payload into the LLM context to empirically demonstrate token inflation and hallucination (Turn 2 self-recovery failure).
- **Comparative Radar Axes (Orthogonality):** 1. Pre-Deployment Safety (100 - UAR), 2. HITL Efficiency (0% friction on nominals), 3. Execution Latency, 4. Token Economy. This exposes each baseline's isolated weakness.
- **Always-On Data Strategy:** Confirmed that utilizing Proposed RADG data for non-nominal intents in Always-On HITL is architecturally valid, as both systems converge to identical Turn 1 recovery behaviors.

## 3. Test/Code Health
- No new code generated. Mock JSON saved to `docs/LLM_Wiki/raw/mock_restconf_error.json`. Backlog updated.

## 4. Exact Cursor & Next Prompt
- Open `tests/evaluation/baselines/llm_only/graph.py` to wire the mock RESTConf error into the surrogate controller node.
- **Next Prompt:** Use the generated prompt provided in the chat response to execute the implementation.
