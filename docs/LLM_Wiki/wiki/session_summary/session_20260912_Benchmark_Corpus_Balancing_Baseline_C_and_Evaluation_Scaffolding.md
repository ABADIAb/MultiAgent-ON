---
title: "Session Summary: Benchmark Corpus Balancing, Baseline C Formalization & Evaluation Environment Scaffolding"
date: 2026-09-12
tags: [session-summary, evaluation-framework, test-corpus, baselines, sdon, pce, nobel-germany, graphrag]
status: active
---

# Session Summary: Benchmark Corpus Balancing, Baseline C Formalization & Evaluation Environment Scaffolding

## 1. Executive Summary

This session successfully transitioned the Master's thesis workflow into **Sprint 4 (Evaluation & Polish)** by formalizing the comparative baselines, resolving key topological and token-economy constraints, balancing the experimental corpus without class bias, and scaffolding the automated evaluation environment in `tests/evaluation/`. First, in response to advisor feedback regarding traditional non-LLM optical control planes, we conducted a literature survey on Software-Defined Optical Networks (SDON) and formalized **Baseline C (Traditional SDON / PCE without LLM)** based on RFC 8231, YANG models, and static policy engines. Second, we clarified the JSON representation of optical network topologies using SNDlib's 17-node Nobel-Germany network (17 nodes, 26 bidirectional links / 52 directional arcs) and analytically quantified the token economy of Mock GraphRAG ($k=2$ subtopology extraction yields $>90\%$ prompt token reduction). Third, we rebalanced the 100-demand benchmark corpus to a statistically sound $25 \times 4$ distribution (25 Class I Nominal, 25 Class II Ambiguous, 25 Class III Infeasible, 25 Class IV Adversarial/Malformed). Fourth, we created the evaluation scaffolding: `tests/evaluation/test_corpus.json` and `tests/evaluation/README.md`. Fifth, we synchronized `ProblemStatement_v5.md`, `MVP_Roadmap.md`, `Architecture_v5.md`, and presentation Slide 13 (`build_defense_deck.py`, `deck_spec.md`, `thesis_defense.pptx`). Finally, we developed a prompt for the next agent session to implement the automated evaluation harness under Strict TDD.

## 2. Key Accomplishments & Conceptual Formalizations

### 2.1 Baseline C Formalization (Traditional SDON / PCE)
- **Literature Review & Grounding:** Investigated state-of-the-art optical control plane standards (RFC 5440, RFC 8231, ONF Open Transport Switch, OpenConfig, IETF ACTN).
- **Architectural Definition:** Formalized **Baseline C: Traditional SDON / PCE (Intent-to-PCE without LLM)**:
  - Input: Constrained declarative GUI/CLI forms or rigid parameter templates mapping directly to YANG service models (`ietf-te-service-mapping`, `openconfig-optical-intent`).
  - Path Computation: Centralized Path Computation Element (PCE) executing Dijkstra / Yen's algorithm.
  - Physical Validation: Conservative static Design Rules / Margin tables ($M_{QoT} \ge 3\text{ dB}$ for worst-case end-of-life) without dynamic physics-informed closed-loop refinement.
  - Failure Modes: Complete inability to process natural language intents or operator ambiguity; high service over-provisioning and capacity wastage ($30\text{--}40\%$ spectrum stranded) due to worst-case static margins.

### 2.2 Nobel-Germany JSON Topology & GraphRAG Token Economy
- **Topology Clarification:** Formalized the SNDlib Nobel-Germany optical backbone structure: 17 Reconfigurable Optical Add-Drop Multiplexer (ROADM) nodes, 26 bidirectional spans (52 directed fiber links), standard SMF-28 parameters ($\alpha=0.2\text{ dB/km}$, $D=17\text{ ps/(nm}\cdot\text{km)}$, $\gamma=1.27\text{ W}^{-1}\text{km}^{-1}$), and EDFA amplifier chains ($G=20\text{ dB}$, $NF=5.5\text{ dB}$).
- **GraphRAG Validation:** Demonstrated that serializing the full German topology into an LLM prompt requires $\sim 8{,}000\text{--}10{,}000$ tokens, saturating context windows and causing attention degradation. By contrast, our Scoped Optical GraphRAG ($k=2$ hop neighborhood extraction) scopes the prompt to $\sim 800\text{--}1{,}000$ tokens, validating a $>90\%$ prompt token reduction while providing the LLM with exact localized link names and amplifier configurations.

### 2.3 Benchmark Corpus Balancing ($25 \times 4$)
- Aligned the 100-demand synthetic evaluation corpus into an equiprobable 4-class distribution to prevent class-imbalance bias in statistical evaluation:
  - **Class I: Nominal / Solvable [25 demands]:** Feasible intents with clear endpoints, SNR margins $\ge 3\text{ dB}$, and valid topology targets. Expected outcome: Automated Approval.
  - **Class II: Ambiguous / Underspecified [25 demands]:** Missing critical parameters (unspecified destination, vague latency constraint). Expected outcome: Phase 3 HITL Clarification interrupt (`reverse_prompt`).
  - **Class III: Physically Infeasible [25 demands]:** Physically violating constraints (demanding 400 Gbps 64-QAM over a 2000 km trans-regional path, unfeasible SNR, disjoint nodes). Expected outcome: Phase 6 RADG Replan interrupt (`radg_node`).
  - **Class IV: Adversarial / Malformed [25 demands]:** Prompt injection, non-existent node IDs, syntax attacks, or contradictory directives. Expected outcome: Early Gate Rejection ($U_{sem} = 1.0$ or CFG syntax failure).

### 2.4 Evaluation Environment Scaffolding (`tests/evaluation/`)
- Created [`tests/evaluation/test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json) containing the complete 100 validated intents, structured with schema: `intent_id`, `class_name`, `intent_text`, `ground_truth_pddl`, `expected_action`, `expected_qot_feasibility`, and `expected_subtopology_nodes`.
- Created [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) detailing:
  - The Four Validation Pillars: Semantic Translation Accuracy, Physical Feasibility ($UAR = 0\%$), Orchestration & Resource Efficiency, and RADG Decision Robustness.
  - Formal metrics, mathematical definitions, and evaluation targets.
  - Architectural matrix comparing Baseline A (LLM-Only), Baseline B (Static Rule-Based), Baseline C (Traditional SDON/PCE), and Proposed (Neurosymbolic RADG).
  - Directory structure, test runner interfaces, and execution guidelines.

### 2.5 Presentation & Documentation Synchronization
- Synchronized Slide 13 in [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) and [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md) to reflect the balanced $25 \times 4$ distribution (`Class I [25]`, `Class II [25]`, `Class III [25]`, `Class IV [25]`) and referenced Baseline C.
- Recompiled [`thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx).
- Synchronized [[architecture/ProblemStatement_v5]], [[experiments/MVP_Roadmap]], and [[architecture/Architecture_v5]].

## 3. Verification & Quality
- **Unit Tests:** Ran full test suite (`uv run pytest`), confirming 278 passed tests with zero regressions.
- **Corpus Integrity:** Validated JSON schema and class distribution across all 100 intents.

## 4. Handover State & Next Steps
1. **Automated Evaluation Harness Implementation:** In the next session, use the provided prompt to execute Strict TDD implementation of `tests/evaluation/scripts/run_benchmark.py`, `metrics.py`, and `plotter.py`.
2. **Benchmark Execution:** Run the 100-demand evaluation suite across the baselines to collect empirical data for Slide 14 and Chapter 4.
