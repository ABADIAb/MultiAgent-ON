# 📊 Comparative Multi-Baseline Evaluation Report

- **Run ID:** `20260924_152825`
- **Date:** 2026-09-24 15:28:25
- **Provider / Model:** `ollama` / `qwen2.5:3b`
- **Corpus:** `compact`

## Four Core Validation Pillars: Comparative Executive Matrix

| Validation Pillar | Evaluated Metric | Target | Proposed RADG (V5) | Always-On HITL | LLM-Only | Comparative Insight |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Pillar 1: Semantic Translation** | Constraint Retention Rate (CRR) | $100\%$ | **94.1%** | 100.0% | 88.2% | Preserved across all neural translation phases |
| | Context-Free Grammar Pass (CFG-PR) | $\ge 95\%$ | **100.0%** | 100.0% | 90.0% | Deterministic AST syntactical verification |
| | Semantic Agreement ($1 - d_{sem}$) | $> 0.850$ | **0.900** | 0.000 | N/A (Bypassed) | Reverse prompting concordance |
| **Pillar 2: Physical Feasibility** | Unfeasible Approval Rate (UAR) | **$0.0\%$** | **0.0%** | 0.0% | **28.6%** | **Strict Safety Invariant**: zero unfeasible approvals |
| | Physical Infeasibility Interception (PIIR) | $100\%$ | **100.0%** | N/A (Nominals only) | 80.0% | Intercepts GN-model reach violations |
| **Pillar 3: Efficiency & Friction** | Mean End-to-End Latency ($T_{E2E}$) | Contextual | **23.76s** | 12.66s | 27.71s | Turnaround duration across pipeline |
| | Mean Token Footprint ($T_{tokens}$) | Monitored | **7660 tok** | 8219 tok | 6655 tok | Multi-turn prompt accumulation friction |
| | Mean HITL Interventions ($N_{hitl}$) | $0$ (Nominal) | **0.75** | **1.00** | 0.60 | **Zero-fatigue autonomous nominal pass** |
| **Pillar 4: Gate Reliability** | Gate Decision Accuracy (GDA) | $> 98\%$ | **100.0%** | 100.0% | 85.0% | Multi-class routing fidelity |
| | False Positive Rate (FPR) | **$0.0\%$** | **0.0%** | 0.0% | **13.3%** | Risky traffic deployed without validation |
