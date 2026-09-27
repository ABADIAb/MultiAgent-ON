# Evaluation Summary: Baseline `always_on_hitl`

- **Date:** 2026-09-24 15:28:25
- **Run ID:** `20260924_152825`
- **Baseline:** `always_on_hitl`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 5
- **Gate Decision Accuracy (GDA):** 5/5 (100.0%)
- **Unfeasible Approval Rate (UAR):** 0.0%
- **Mean End-to-End Latency:** 12.66s
- **Per-Request Timeout Guard:** 120.0s

## Executive Summary: The Four Core Validation Pillars

| Pillar | Metric | Formula / Source | Target | Measured Actual | Status |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **Pillar 1: Semantic Translation Accuracy** | Constraint Retention Rate (CRR, Operable) | $\frac{\sum \vert \mathcal{C}_{pres} \cap \mathcal{C}_{exp} \vert}{\sum \vert \mathcal{C}_{exp} \vert}$ | $100\%$ | **100.0%** (9/9) | ✓ PASS |
| | CFG Pass Rate (CFG-PR) | $\frac{1}{N} \sum v_{struct}$ | $\ge 95\%$ (Nom/Inf) | **100.0%** | ✓ PASS |
| | Semantic Agreement (Well-Formed) | $\frac{1}{N_{well}} \sum (1 - d_{sem})$ | $> 0.85$ | **0.000** | ✗ REVIEW |
| | Ambiguity / Adversarial Catch Rate | $\frac{\vert \text{Clarify} \vert}{\vert \text{Ambiguous} \vert}$ | $100\%$ | **100.0%** | ✓ PASS |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | $\frac{\vert \text{Unfeasible Approved} \vert}{\vert \text{Approved} \vert}$ | **$0.0\%$** | **0.0%** (0/0) | ✓ PASS |
| | Physical Infeasibility Interception (PIIR) | $\frac{\vert \text{Class III Replan} \vert}{\vert \text{Class III} \vert}$ | $100\%$ | **100.0%** (0/0) | ✓ PASS |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | $\frac{1}{N} \sum T_{elapsed}$ | Contextual | **12.66s** | ✓ MONITORED |
| | Total Token Footprint | Cumulative Tokens | Monitored | **41,095 tok** (8219.0 tok/intent) | ✓ MONITORED |
| | Selective HITL Interruptions | Mean $N_{hitl}$ | $0$ (Nom), $1$ (Others) | **1.00** (5 total) | ✓ PASS |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $\frac{1}{N} \sum \mathbb{I}(D = \text{Exp})$ | $> 98\%$ | **100.0%** (5/5) | ✓ PASS |
| | False Positive Rate (FPR) | $\frac{\vert \text{Risky Approved} \vert}{\vert \text{Risky Demands} \vert}$ | **$0.0\%$** | **0.0%** (0) | ✓ PASS |
| | Selective HITL Precision | $\frac{\vert \text{True Interrupts} \vert}{\vert \text{All Interrupts} \vert}$ | $100\%$ | **0.0%** | ✗ FAIL |

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate | Mean Latency | Mean Tokens | CRR |
| :---: | :--- | :---: | :---: | :---: | :---: | -: | -: | -: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% | 12.66s | 8219 | 100.0% |

## Detailed Results Matrix

| ID | Class | Intent Summary | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | Tokens | CRR | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from H..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.80s | 8113 | 100% | 1.000 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from H..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.52s | 8326 | 100% | 1.000 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologn..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.36s | 8654 | 100% | 1.000 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Muni..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 9.72s | 7817 | 100% | 1.000 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimu..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 11.88s | 8185 | 100% | 1.000 | ✓ | `approve` |
