# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260925_173441`
- **Date:** 2026-09-25 17:34:41
- **Provider / Model:** `ollama` / `qwen2.5:3b`
- **Corpus:** `full`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **94.6%** | 94.6% | 96.0% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **98.3%** | 98.3% | 98.3% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.863** | 0.412 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | **$0.0\%$** | **0.0%** | 0.0% | **75.0%** | **Strict Safety Invariant**: zero unfeasible approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **86.7%** | N/A (Nominals only) | 0.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | Contextual | **25.95s** | 24.76s | 38.71s | Turnaround duration across pipeline |
| | Mean Token Footprint ($T_{tokens}$) | Monitored | **7565 tok** | 8598 tok | 11954 tok | Multi-turn prompt accumulation friction |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.74** | **0.97** | 0.73 | **Zero-fatigue autonomous nominal pass** |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $> 98\%$ | **92.5%** | 94.2% | 25.0% | Multi-class routing fidelity |
| | False Positive Rate (FPR) | **$0.0\%$** | **1.1%** | 1.1% | **100.0%** | Risky traffic deployed without validation |
