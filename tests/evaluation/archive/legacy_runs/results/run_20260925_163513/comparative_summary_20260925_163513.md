# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260925_163513`
- **Date:** 2026-09-25 16:35:13
- **Provider / Model:** `None` / `None`
- **Corpus:** `compact`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **94.1%** | 94.1% | 88.2% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **95.0%** | 95.0% | 95.0% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.860** | 0.410 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | **$0.0\%$** | **0.0%** | 0.0% | **75.0%** | **Strict Safety Invariant**: zero unfeasible approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **80.0%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | Contextual | **25.32s** | 31.68s | 45.42s | Turnaround duration across pipeline |
| | Mean Token Footprint ($T_{tokens}$) | Monitored | **7898 tok** | 8998 tok | 11360 tok | Multi-turn prompt accumulation friction |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.80** | **1.05** | 0.70 | **Zero-fatigue autonomous nominal pass** |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $> 98\%$ | **95.0%** | 95.0% | 25.0% | Multi-class routing fidelity |
| | False Positive Rate (FPR) | **$0.0\%$** | **0.0%** | 0.0% | **100.0%** | Risky traffic deployed without validation |
