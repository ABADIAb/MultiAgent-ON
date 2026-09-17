# Neurosymbolic Intent Planning Evaluation Summary (V5 Pipeline)

- **Date:** 2026-09-16 21:34:46
- **Run ID:** `20260916_213446`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Overall Risk Gate Accuracy (GDA):** 17/20 (85.0%)
- **Unsafe Approval Rate (UAR):** 0.0% (Absolute Safety Invariant)
- **Mean End-to-End Latency:** 40.55s
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **82.3%** (14/17) | ✗ REVIEW |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **95.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.900** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **60.0%** | ✗ REVIEW |
| **Pillar 2: Physical Feasibility** | Unsafe Approval Rate (UAR) | $\frac{\vert \text{Unsafe Approved} \vert}{\vert \text{Approved} \vert}$ | **$0.0\%$** | **0.0%** (0/6) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **80.0%** (4/5) | ✗ FAIL |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | $\frac{1}{N} \sum T_{elapsed}$ | Contextual | **40.55s** | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **140,534 tok** (7026.7 tok/intent) | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.65** (13 total) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **85.0%** (17/20) | ✗ FAIL |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **6.7%** (1) | ✗ CRITICAL |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Mean Latency | Mean Tokens | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 5.71s | 3810 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 3/5 | 60.0% | 12.20s | 8085 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `replan` | 4/5 | 80.0% | 131.05s | 7262 | 62.5% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 13.23s | 8949 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 9.28s | 3699 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.37s | 3927 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 4.88s | 4055 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.53s | 3703 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.49s | 3667 | 100% | 0.100 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `replan` | `approve` | ✗ FAIL | 1 | 10.14s | 8874 | N/A | 0.200 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.45s | 8922 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.82s | 9242 | N/A | 1.000 | ✓ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `approve` | `approve` | ✗ FAIL | 0 | 8.40s | 4296 | N/A | 0.200 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.18s | 9091 | N/A | 1.000 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `replan` | `failed` | `failed` | ✗ FAIL | 0 | 362.23s | 494 | 0% | N/A | ✗ | `None` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 16.65s | 9186 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 7.93s | 8669 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 253.76s | 8932 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 14.66s | 9030 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 13.72s | 9174 | 100% | 1.000 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 12.85s | 8769 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 10.52s | 8849 | N/A | 1.000 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 13.00s | 8595 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 16.06s | 9360 | 0% | 1.000 | ✓ | `approve` |
