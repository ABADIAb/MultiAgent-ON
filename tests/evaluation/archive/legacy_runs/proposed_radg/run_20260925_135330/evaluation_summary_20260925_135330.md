# Evaluation Summary: Baseline `proposed_radg`

- **Date:** 2026-09-25 13:53:30
- **Run ID:** `20260925_135330`
- **Baseline:** `proposed_radg`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Gate Decision Accuracy (GDA):** 19/20 (95.0%)
- **False Positive Rate (FPR):** 0.0%
- **Median End-to-End Latency:** 13.87s (Mean: 25.32s)
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **94.1%** (16/17) | ✓ PASS |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **95.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.860** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **80.0%** | ✗ REVIEW |
| **Pillar 2: Physical Feasibility & Integrity** | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0/15) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **80.0%** (4/5) | ✗ FAIL |
| **Pillar 3: Efficiency & Friction** | End-to-End Latency ($T_{E2E}$) | $\text{Median} \ [\text{Mean}]$ | Contextual | **13.87s** [25.32s] | ✓ MONITORED |
| | Token Footprint per Demand | $\text{Median} \ [\text{Mean}]$ | Monitored | **8,888 tok** [7897.6] | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **157,951 tok** | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.80** (16 total) | ✓ PASS |
| | Task Completion Rate (TCR) | $\frac{\vert \text{Completed} \vert}{N}$ | $100\%$ | **100.0%** (20/20) | ✓ PASS |
| | Timeout / Aborted Demands | Count | $0$ | **0** (Timeouts: 0, Max Turns: 0) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **95.0%** (19/20) | ✓ PASS |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0) | ✓ PASS |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Timeouts / Aborted | Median Lat | Mean Lat | Median Tok | Mean Tok | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 0 | 4.43s | 10.27s | 3670 | 3741 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 5/5 | 100.0% | 0 | 15.83s | 38.82s | 8947 | 8982 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `clarify / replan` | 4/5 | 80.0% | 0 | 12.43s | 36.83s | 8964 | 9809 | 87.5% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 0 | 15.66s | 15.35s | 9230 | 9058 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 35.40s | 3670 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 4.43s | 3768 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.98s | 4172 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.98s | 3456 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.58s | 3638 | 100% | 0.100 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 7.13s | 8513 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.83s | 9065 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 16.89s | 8670 | N/A | 1.000 | ✗ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 140.86s | 9717 | N/A | 1.000 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 13.37s | 8947 | N/A | 1.000 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `replan` | `clarify` | `approve` | ✗ FAIL | 1 | 134.11s | 8984 | 67% | 0.500 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 13.72s | 8964 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `replan` | `replan` | `approve` | ✓ PASS | 2 | 11.78s | 13369 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 12.43s | 8926 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 12.11s | 8801 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 16.65s | 9368 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 14.69s | 8851 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.71s | 9230 | N/A | 0.500 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 14.02s | 8610 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.66s | 9232 | 0% | 0.500 | ✓ | `approve` |
