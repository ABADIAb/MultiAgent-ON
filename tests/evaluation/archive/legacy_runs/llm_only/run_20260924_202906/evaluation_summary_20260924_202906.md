# Evaluation Summary: Baseline `llm_only` (No Pre-Deployment Decision Gates)

- **Date:** 2026-09-24 20:29:06
- **Run ID:** `20260924_202906`
- **Baseline:** `llm_only` (Ablation: Un-gated LLM Translation -> Direct SDON Controller Deployment)
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Pre-Deployment Admission Policy:** Blind Forwarding ($\mathcal{A}_{pre} = \{\text{approve}\})
- **Pre-Deployment False Positive Rate (FPR):** 100.0% (15/15 risky intents pushed to production)
- **SDON Controller Incident Rate:** 75.0% (15/20 intents caused controller deployment errors)
- **Unfeasible Approval Rate (UAR):** 75.0%
- **Mean End-to-End Latency:** 13.21s (Includes Turn 1 controller crash + Turn 2 reactive recovery)
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars (Ablation Analysis)

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **88.2%** (15/17) | ✗ REVIEW |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **95.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.770** | ✗ REVIEW |
| | Pre-Deployment Ambiguity Filter | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **0.0%** (Bypassed) | ✗ ZERO PRE-DEPLOYMENT GATING |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | $\frac{\vert \text{Unfeasible Approved} \vert}{\vert \text{Approved} \vert}$ | **$0.0\%$** | **75.0%** (15/20) | ✗ CRITICAL SAFETY INFRINGEMENT |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Pre-Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **0.0%** (0/5) | ✗ 0% INTERCEPTED PRE-DEPLOYMENT |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | $\frac{1}{N} \sum T_{elapsed}$ | Contextual | **13.21s** | ⚠️ INFLATED BY CONTROLLER CRASHES |
| | Total Token Footprint | Cumulative Tokens | Monitored | **153,856 tok** (7692.8 tok/intent) | ⚠️ ~50% WASTED IN TURN 1 |
| | Reactive HITL Interventions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.75** (15 total) | ⚠️ REACTIVE POST-MORTEM HITL |
| **Pillar 4: Gate Reliability & Admission** | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **100.0%** (15) | ✗ CRITICAL SAFETY COLLAPSE |
| | Controller Deployment Incident Rate | $\frac{\vert \text{Controller Errors} \vert}{\vert \text{Total Demands} \vert}$ | **$0.0\%$** | **75.0%** (15/20) | ✗ RUNTIME FAILURE IN PRODUCTION |
| | Pre-Deployment Gate Accuracy | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | N/A | **N/A (No Pre-Deployment Gates)** | — UN-GATED ARCHITECTURE |

## Class-by-Class Risk & Controller Outcome Breakdown

| Class | Category | Demands | Pre-Deployment Policy | SDON Controller Outcome | Recovery Status | Mean Latency | Mean Tokens | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | **Provisioned (Turn 1)** | Completed (Turn 1) | 7.25s | 3782 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `approve` | **Deployment Error (Turn 1)** | Recovered (Turn 2) | 13.86s | 8988 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `approve` | **Deployment Error (Turn 1)** | Recovered (Turn 2) | 17.06s | 9064 | 75.0% |
| `IV_Adversarial` | Adversarial | 5 | `approve` | **Deployment Error (Turn 1)** | Recovered (Turn 2) | 14.68s | 8937 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Pre-Deployment | Controller Verdict | Final Action | Outcome | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection fro..." | `approve` | `approve` | `approve` | ✓ PROVISIONED | 0 | 17.18s | 3670 | 100% | 0.100 | ✓ |
| `intent_nom_02` | `I` | "Establish an optical connection fro..." | `approve` | `approve` | `approve` | ✓ PROVISIONED | 0 | 5.10s | 3813 | 100% | 0.100 | ✓ |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Col..." | `approve` | `approve` | `approve` | ✓ PROVISIONED | 0 | 6.69s | 4160 | 100% | 0.100 | ✓ |
| `intent_nom_04` | `I` | "Provision an optical channel from M..." | `approve` | `approve` | `approve` | ✓ PROVISIONED | 0 | 4.78s | 3630 | 100% | 0.100 | ✓ |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with min..." | `approve` | `approve` | `approve` | ✓ PROVISIONED | 0 | 2.48s | 3638 | 100% | 0.100 | ✓ |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankf..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 9.48s | 8758 | N/A | 0.500 | ✓ |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the so..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 16.91s | 9067 | N/A | 0.500 | ✓ |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical ..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 14.80s | 9036 | N/A | 1.000 | ✓ |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city wit..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 13.75s | 9067 | N/A | 0.500 | ✓ |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in H..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 14.35s | 9013 | N/A | 1.000 | ✓ |
| `intent_inf_01` | `III` | "Establish a single direct span from..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 13.05s | 8957 | 67% | 0.500 | ✓ |
| `intent_inf_02` | `III` | "Establish an optical connection fro..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 16.59s | 9144 | 100% | 0.100 | ✓ |
| `intent_inf_03` | `III` | "Provision a single unamplified dire..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 8.22s | 8618 | 100% | 0.100 | ✓ |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requirin..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 33.97s | 9738 | 0% | 1.000 | ✗ |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 13.48s | 8862 | 100% | 0.100 | ✓ |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Colog..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 14.83s | 9139 | 100% | 0.500 | ✓ |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berli..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 13.42s | 8701 | 100% | 0.100 | ✓ |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with hi..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 16.64s | 9194 | N/A | 0.500 | ✓ |
| `intent_adv_04` | `IV` | "Provision an optical channel from M..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 12.23s | 8390 | 100% | 0.100 | ✓ |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankf..." | `approve` | `replan` | `approve` | ⚠️ RECOVERED | 1 | 16.27s | 9261 | 0% | 0.500 | ✓ |
