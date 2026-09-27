# Evaluation Summary: Baseline `proposed_radg`

- **Date:** 2026-09-27 08:55:47
- **Run ID:** `20260927_085547`
- **Baseline:** `proposed_radg`
- **LLM Provider:** `openai`
- **Model Evaluated:** `gpt-6-luna`
- **Total Demands Evaluated:** 20
- **Gate Decision Accuracy (GDA):** 20/20 (100.0%)
- **False Positive Rate (FPR):** 0.0%
- **Median End-to-End Latency:** 16.70s (Mean: 15.04s)
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **100.0%** (17/17) | ✓ PASS |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **100.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.940** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **80.0%** | ✗ REVIEW |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0/15) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **80.0%** (4/5) | ✗ FAIL |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | $\text{Median} \ [\text{Mean}]$ | Contextual | **16.70s** [15.04s] | ✓ MONITORED |
| | Token Footprint per Demand | $\text{Median} \ [\text{Mean}]$ | Monitored | **9,756 tok** [8434.9] | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **168,698 tok** | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.75** (15 total) | ✓ PASS |
| | Task Completion Rate (TCR) | $\frac{\vert \text{Completed} \vert}{N}$ | $100\%$ | **100.0%** (20/20) | ✓ PASS |
| | Timeout / Aborted Demands | Count | $0$ | **0** (Timeouts: 0, Max Turns: 0) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **100.0%** (20/20) | ✓ PASS |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0) | ✓ PASS |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Timeouts / Aborted | Median Lat | Mean Lat | Median Tok | Mean Tok | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 0 | 7.74s | 7.76s | 4076 | 4148 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 5/5 | 100.0% | 0 | 17.58s | 17.80s | 9942 | 9878 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 16.12s | 16.22s | 9855 | 9820 | 100.0% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 18.90s | 18.39s | 10134 | 9895 | 100.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 7.74s | 3988 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 7.54s | 4076 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 8.62s | 4666 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.87s | 3785 | 100% | 0.000 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 8.04s | 4223 | 100% | 0.000 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 17.58s | 9963 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 17.88s | 9709 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 17.06s | 9972 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 17.19s | 9802 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 19.28s | 9942 | N/A | 0.500 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 16.12s | 9855 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 16.34s | 9677 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 17.32s | 10086 | 100% | 0.500 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 16.02s | 9862 | 100% | 0.000 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 15.30s | 9619 | 100% | 0.000 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 18.90s | 10399 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 17.37s | 9495 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 19.00s | 10134 | N/A | 1.000 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify/replan` | `replan` | `approve` | ✓ PASS | 1 | 15.63s | 9084 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify/replan` | `clarify` | `approve` | ✓ PASS | 1 | 21.06s | 10361 | 100% | 1.000 | ✓ | `approve` |
