# Evaluation Summary: Baseline `llm_only`

- **Date:** 2026-09-24 15:28:25
- **Run ID:** `20260924_152825`
- **Baseline:** `llm_only`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Gate Decision Accuracy (GDA):** 17/20 (85.0%)
- **Unfeasible Approval Rate (UAR):** 28.6%
- **Mean End-to-End Latency:** 27.71s
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **88.2%** (15/17) | ✗ REVIEW |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **90.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.900** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **0.0%** | ✗ REVIEW |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | $\frac{\vert \text{Unfeasible Approved} \vert}{\vert \text{Approved} \vert}$ | **$0.0\%$** | **28.6%** (2/7) | ✗ CRITICAL |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **80.0%** (4/5) | ✗ FAIL |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | $\frac{1}{N} \sum T_{elapsed}$ | Contextual | **27.71s** | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **133,109 tok** (6655.4 tok/intent) | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.60** (12 total) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **85.0%** (17/20) | ✗ FAIL |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **13.3%** (2) | ✗ CRITICAL |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Mean Latency | Mean Tokens | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 4.28s | 3737 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 3/5 | 60.0% | 9.96s | 6809 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `replan` | 4/5 | 80.0% | 82.95s | 7192 | 75.0% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 13.66s | 8884 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.41s | 3495 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.20s | 3867 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 7.06s | 4230 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 3.07s | 3456 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.66s | 3638 | 100% | 0.100 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 12.73s | 8966 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `approve` | `approve` | ✗ FAIL | 0 | 6.96s | 3963 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 11.94s | 8298 | N/A | 1.000 | ✗ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 12.93s | 8909 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `approve` | `approve` | ✗ FAIL | 0 | 5.25s | 3907 | N/A | 1.000 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 12.72s | 8819 | 67% | 0.100 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 16.20s | 9091 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 8.79s | 8640 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `replan` | `failed` | `failed` | ✗ FAIL | 0 | 361.95s | 473 | 0% | N/A | ✗ | `None` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 15.11s | 8935 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 13.18s | 9052 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 9.75s | 8397 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 15.33s | 9147 | N/A | 1.000 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 14.15s | 8574 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 15.89s | 9252 | 0% | 0.500 | ✓ | `approve` |
