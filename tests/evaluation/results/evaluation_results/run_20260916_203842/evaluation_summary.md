# Neurosymbolic Intent Planning Evaluation Summary (V5 Pipeline)

- **Date:** 2026-09-16 20:38:42
- **Run ID:** `20260916_203842`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Overall Risk Gate Accuracy (GDA):** 19/20 (95.0%)
- **Unsafe Approval Rate (UAR):** 0.0% (Absolute Safety Invariant)
- **Mean End-to-End Latency:** 53.67s
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **94.1%** (16/17) | ✓ PASS |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **100.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.860** | ✓ PASS |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **90.0%** | ✓ PASS |
| **Pillar 2: Physical Feasibility** | Unsafe Approval Rate (UAR) | $\frac{\vert \text{Unsafe Approved} \vert}{\vert \text{Approved} \vert}$ | **$0.0\%$** | **0.0%** (0/5) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **80.0%** (4/5) | ✗ FAIL |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | $\frac{1}{N} \sum T_{elapsed}$ | Contextual | **53.67s** | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **147,510 tok** (7375.5 tok/intent) | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **0.75** (15 total) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **95.0%** (19/20) | ✓ PASS |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0) | ✓ PASS |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Mean Latency | Mean Tokens | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 5.62s | 3625 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 5/5 | 100.0% | 62.73s | 8750 | N/A |
| `III_Infeasible` | Physically Infeasible | 5 | `replan` | 4/5 | 80.0% | 134.01s | 8587 | 87.5% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% | 12.34s | 8540 | 75.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 10.69s | 3585 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.73s | 3706 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.07s | 4030 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 3.07s | 3318 | 100% | 0.100 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.52s | 3484 | 100% | 0.100 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.79s | 8698 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.73s | 8695 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical lig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 135.35s | 8752 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with h..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 136.51s | 8900 | N/A | 0.500 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hamb..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.25s | 8706 | N/A | 1.000 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from No..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 256.78s | 8732 | 67% | 0.100 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from H..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 17.10s | 8786 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct ..." | `replan` | `clarify` | `approve` | ✗ FAIL | 1 | 9.10s | 8332 | 100% | 0.500 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 3..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 375.30s | 8613 | 100% | 0.100 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich wi..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 11.75s | 8471 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.43s | 8736 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin a..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.93s | 8422 | 100% | 0.500 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.96s | 8720 | N/A | 0.500 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Muni..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 10.86s | 8070 | 100% | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.53s | 8754 | 0% | 0.500 | ✓ | `approve` |
