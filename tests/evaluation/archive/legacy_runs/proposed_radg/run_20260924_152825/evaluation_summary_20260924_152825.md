# Evaluation Summary: Baseline `proposed_radg`

- **Date:** 2026-09-24 15:28:25
- **Run ID:** `20260924_152825`
- **Baseline:** `proposed_radg`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Gate Decision Accuracy (GDA):** 20/20 (100.0%)
- **Unfeasible Approval Rate (UAR):** 0.0%
- **Mean End-to-End Latency:** 23.76s
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **94.1%** (16/17) | ✓ PASS |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **100.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.900** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **80.0%** | ✗ REVIEW |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | $\frac{\vert \text{Unfeasible Approved} \vert}{\vert \text{Approved} \vert}$ | **$0.0\%$** | **0.0%** (0/5) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **100.0%** (5/5) | ✓ PASS |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | $\frac{1}{N} \sum T_{elapsed}$ | Contextual | **23.76s** | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **153,196 tok** (7659.8 tok/intent) | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.75** (15 total) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **100.0%** (20/20) | ✓ PASS |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0) | ✓ PASS |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Mean Latency | Mean Tokens | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 5.21s | 3762 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 5/5 | 100.0% | 13.98s | 9024 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `replan` | 5/5 | 100.0% | 61.56s | 8912 | 87.5% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 14.28s | 8941 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 9.18s | 3670 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.63s | 3860 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.91s | 4184 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.85s | 3456 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.47s | 3638 | 100% | 0.100 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.83s | 8991 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.13s | 9037 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.66s | 9052 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.23s | 9146 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.05s | 8894 | N/A | 1.000 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 259.51s | 9239 | 67% | 0.100 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 14.16s | 8959 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 8.28s | 8614 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 13.11s | 8937 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 12.74s | 8813 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.46s | 9126 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 15.05s | 8828 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 13.38s | 9020 | N/A | 0.500 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 13.81s | 8554 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.72s | 9178 | 0% | 0.500 | ✓ | `approve` |
