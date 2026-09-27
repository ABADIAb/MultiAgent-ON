# Evaluation Summary: Baseline `proposed_radg`

- **Date:** 2026-09-27 09:41:48
- **Run ID:** `20260927_094148`
- **Baseline:** `proposed_radg`
- **LLM Provider:** `openai`
- **Model Evaluated:** `gpt-6-luna`
- **Total Demands Evaluated:** 20
- **Gate Decision Accuracy (GDA):** 20/20 (100.0%)
- **False Positive Rate (FPR):** 0.0%
- **Median End-to-End Latency:** 12.77s (Mean: 11.56s)
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **100.0%** (17/17) | ✓ PASS |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **95.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.990** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **90.0%** | ✓ PASS |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0/15) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **100.0%** (5/5) | ✓ PASS |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | $\text{Median} \ [\text{Mean}]$ | Contextual | **12.77s** [11.56s] | ✓ MONITORED |
| | Token Footprint per Demand | $\text{Median} \ [\text{Mean}]$ | Monitored | **9,202 tok** [7950.1] | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **159,002 tok** | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.75** (15 total) | ✓ PASS |
| | Task Completion Rate (TCR) | $\frac{\vert \text{Completed} \vert}{N}$ | $100\%$ | **100.0%** (20/20) | ✓ PASS |
| | Timeout / Aborted Demands | Count | $0$ | **0** (Timeouts: 0, Max Turns: 0) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **100.0%** (20/20) | ✓ PASS |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0) | ✓ PASS |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Timeouts / Aborted | Median Lat | Mean Lat | Median Tok | Mean Tok | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 0 | 6.97s | 6.68s | 3849 | 3978 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 5/5 | 100.0% | 0 | 13.27s | 13.17s | 9163 | 9226 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 13.86s | 13.83s | 9420 | 9465 | 100.0% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 12.59s | 12.57s | 9242 | 9131 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 7.41s | 3827 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.97s | 3973 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 8.37s | 4562 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.42s | 3681 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.24s | 3849 | 100% | 0.000 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.23s | 9659 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 11.99s | 9025 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 13.68s | 8976 | N/A | 1.000 | ✗ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.69s | 9163 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 13.27s | 9306 | N/A | 0.500 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 14.57s | 9535 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 13.47s | 9400 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 14.39s | 9621 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 12.86s | 9351 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 13.86s | 9420 | 100% | 0.000 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 12.59s | 9370 | 0% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 11.29s | 8808 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 13.17s | 9242 | N/A | 0.500 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 10.74s | 8461 | 100% | 0.000 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 15.04s | 9773 | 100% | 1.000 | ✓ | `approve` |
