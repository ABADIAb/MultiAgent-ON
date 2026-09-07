---
title: "Session Summary: Thesis Chapter 3 Drafting & Formal Problem Formulation"
date: 2026-08-26
tags: [session, summary, thesis, chapter-3, system-model, problem-definition, mathematical-formulation, optical-networks]
status: active
---

# Session Summary: Thesis Chapter 3 Drafting & Formal Problem Formulation

## Date: 2026-08-26

## Overview
This session marked the formal kick-off of the Master's thesis document redaction, beginning with **Chapter 3: System Model: The Risk-Adaptive Neurosymbolic Architecture**. During this session, I structured and refined the overall master thesis roadmap in [[thesis_drafts/Writing_Roadmap_v1]], generated initial drafts for Sections 3.1 through 3.5 under `docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/`, and performed a rigorous validation of Section 3.1 (*Formal Problem Definition*) against the operational implementation in `src/core/`.

---

## What was Accomplished?

### 1. Thesis Outline & Writing Roadmap Alignment:
- Validated and structured [[thesis_drafts/Thesis_Outline_v4]] and [[thesis_drafts/Writing_Roadmap_v1]].
- Established the 5-phase redaction methodology:
  - **Phase 1:** Chapter 3 (System Model & Risk-Adaptive Neurosymbolic Architecture).
  - **Phase 2:** Chapter 4 (Implementation & Engineering Verification).
  - **Phase 3:** Chapter 5 (Experimental Evaluation & Benchmark Results).
  - **Phase 4:** Chapter 2 (Background & Literature Gap Analysis).
  - **Phase 5:** Chapter 1 (Introduction/Contributions) & Chapter 6 (Conclusions/Future Work).
- Enforced academic style rules, anti-AI cliché guidelines, and Flesch readability standards.

### 2. Chapter 3 Drafting (Sections 3.1 to 3.5):
- Created structural drafts for all sections in `docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/`:
  - `3_1_Formal_Problem_Definition.md`: Architectural vulnerabilities in LLM optical planning, network graph definition $G(V, E)$, physical parameter tuples, decision variables, resource constraints ($T_{max}$, $t_{exec}$, $K$-shortest paths), physical/semantic boundary constraints, and the composite optimization objective $\min \mathcal{J} = \alpha N_{hitl} + \beta T_{tokens}$ subject to $D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$.
  - `3_2_Conceptual_Framework.md`: 7-phase fail-fast pipeline, architectural component separation, and computational complexity bounds.
  - `3_3_Strict_Neurosymbolic_Separation.md`: Strict boundaries, CFG structural validator, and token context scoping via $k$-hop Optical RAG.
  - `3_4_Risk_Adaptive_Decision_Gate.md`: Piecewise decision function $D(U_{sem}, \text{QoT}_{valid})$ and Gaussian Noise model integration.
  - `3_5_Formal_HITL_Reverse_Prompting.md`: State preservation, prompt reconstruction, and human-in-the-loop disambiguation protocol.

### 3. Codebase Alignment & Assumption Formalization:
- Conducted an in-depth code-to-math audit against `src/core/` (`models.py`, `qot_calculator.py`, `semantic_gate.py`, `radg.py`, `symbolic_solver.py`).
- Integrated two crucial engineering assumptions into Section 3.1:
  - **Assumption 1 (Homogeneous Fiber Profile):** Formally noted that while the general formulation supports heterogeneous parameters per link ($\alpha_{ij}, D_{ij}, \gamma_{ij}$), the practical evaluation testbed assumes standard single-mode fiber (SMF-28) with global constants ($\alpha, D, \gamma$).
  - **Assumption 2 (Zero Equalization Loss & Filtered Network):** Documented that the QoT calculation assumes a ROADM-filtered regime with zero equalization loss at intermediate nodes.
- Refined the physical feasibility constraint to verify receiver sensitivity floor ($P_{rx}(\pi) \ge P_{rx, min}$) rather than an artificial upper bound.
- Justified the bound $K \in [3, 5]$ based on the computational complexity scaling of Yen's algorithm ($O(K|V|(|E| + |V|\log|V|))$).
- Updated [[architecture/ProblemStatement_v5]] to align $\text{QoT}_{valid} = \mathbb{I}(\text{GSNR} \ge \text{GSNR}_{th} \land P_{rx} \ge P_{rx, min})$.

---

## Next Steps

1. **Chapter 3 Section 3.2 Deep Review:** Conduct the code-to-theory validation for Section 3.2 (*Conceptual Framework*) and Section 3.3 (*Strict Neurosymbolic Separation*).
2. **Sprint 4 Evaluation Scaffolding:** Finalize the synthetic test corpus (`tests/evaluation/test_corpus.json`) and run the baseline evaluation script (`tests/evaluation/baseline_evaluation.py`) across the 17-node Nobel-Germany topology.
