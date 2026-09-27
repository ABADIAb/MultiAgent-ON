# Evaluation Summary: Baseline `proposed_radg`

- **Date:** 2026-09-27 17:06:25
- **Run ID:** `20260927_170625`
- **Baseline:** `proposed_radg`
- **LLM Provider:** `openai`
- **Model Evaluated:** `gpt-5-nano-2025-08-07`
- **Total Demands Evaluated:** 20
- **Gate Decision Accuracy (GDA):** 18/20 (90.0%)
- **False Positive Rate (FPR):** 13.3%
- **Median End-to-End Latency:** 11.50s (Mean: 9.60s)
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **88.2%** (15/17) | ✗ REVIEW |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **90.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **1.000** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **50.0%** | ✗ REVIEW |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **13.3%** (2/15) | ✗ CRITICAL |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **100.0%** (5/5) | ✓ PASS |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | $\text{Median} \ [\text{Mean}]$ | Contextual | **11.50s** [9.60s] | ✓ MONITORED |
| | Token Footprint per Demand | $\text{Median} \ [\text{Mean}]$ | Monitored | **8,725 tok** [7175.7] | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **143,514 tok** | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.65** (13 total) | ✓ PASS |
| | Task Completion Rate (TCR) | $\frac{\vert \text{Completed} \vert}{N}$ | $100\%$ | **100.0%** (20/20) | ✓ PASS |
| | Timeout / Aborted Demands | Count | $0$ | **0** (Timeouts: 0, Max Turns: 0) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **90.0%** (18/20) | ✗ FAIL |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **13.3%** (2) | ✗ CRITICAL |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Timeouts / Aborted | Median Lat | Mean Lat | Median Tok | Mean Tok | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 0 | 5.41s | 5.19s | 3773 | 3812 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 3/5 | 60.0% | 0 | 11.78s | 9.40s | 8815 | 6982 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 11.88s | 12.21s | 9080 | 9114 | 75.0% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 11.26s | 11.58s | 8635 | 8794 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.80s | 3661 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.41s | 3773 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.84s | 4258 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 4.55s | 3574 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 4.36s | 3796 | 100% | 0.000 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.14s | 8815 | N/A | 1.000 | ✗ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 11.78s | 8869 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `approve` | `approve` | ✗ FAIL | 0 | 5.45s | 4144 | N/A | 0.000 | ✓ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `approve` | `approve` | ✗ FAIL | 0 | 5.70s | 4090 | N/A | 0.200 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 11.94s | 8994 | N/A | 0.900 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 12.95s | 9080 | 67% | 0.000 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 11.74s | 8893 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 11.80s | 9438 | 50% | 0.000 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 11.88s | 9094 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 12.66s | 9067 | 100% | 0.000 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 12.55s | 9170 | 0% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 11.14s | 8635 | 100% | 0.000 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 12.06s | 8590 | N/A | 1.000 | ✗ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 10.91s | 8377 | 100% | 0.000 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 11.26s | 9196 | 100% | 0.000 | ✓ | `approve` |
