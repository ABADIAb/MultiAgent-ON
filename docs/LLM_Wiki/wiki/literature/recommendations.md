---
title: "Literature Recommendations and SOTA Takeaways"
date: 2026-09-19
tags: [literature, sota, recommendations, research]
status: active
---

# Literature Recommendations and SOTA Takeaways

This document synthesizes core recommendations and architectural guidance extracted from the State of the Art (SOTA) review across Agentic AI, Intent-Based Optical Networks (IBON), and Neurosymbolic planning.

### 1. Neurosymbolic Separation over Monolithic Generation
- **Key Insight:** Pure LLM generation fails in optical transmission due to hallucinated physical constraints and combinatorial path invalidity (ECOC 2024, Confucius SIGCOMM 2025).
- **Recommendation:** Isolate routing (Yen's K-SP) and physics (Gaussian Noise model) into deterministic Python engines, using the LLM solely as an intent translator. See [[concepts/Constraint_Isolation]].

### 2. Guarding against Semantic Drift via Formal HITL
- **Key Insight:** Standard conversational multi-turn prompts suffer from prompt drift and context saturation over long sessions (SJTU JOCN 2026).
- **Recommendation:** Implement Reverse Prompting with formal Context-Free Grammar AST validation ($v_{struct}$) and LangGraph state-preserving interrupts. See [[concepts/Human_in_the_Loop]].

### 3. Context Scoping via GraphRAG
- **Key Insight:** Serializing full optical topologies (nodes, EDFA spans, ROADMs) exceeds LLM context windows and degrades attention.
- **Recommendation:** Apply dual-ball $k$-hop topological subgraphs ($V_{sub} = N_k(s) \cup N_k(d)$) to reduce prompt tokens by $>97\%$.

### Cross-References
- [[literature/lit_comparison]] — Full SOTA comparative matrix.
- [[literature/sota_gap_analysis]] — Detailed research gap analysis.
- [[Architecture_v5]] — System architecture reflecting these recommendations.
