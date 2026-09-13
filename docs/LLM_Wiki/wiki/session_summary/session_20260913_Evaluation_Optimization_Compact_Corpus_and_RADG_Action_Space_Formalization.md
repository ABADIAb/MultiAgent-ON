---
title: "Session Summary: Evaluation Optimization, Compact Corpus & RADG Action Space Formalization"
date: 2026-09-13
tags: [session-summary, evaluation-optimization, compact-corpus, radg-action-space, hitl-metrics-fix, publication-figures, strict-tdd]
status: active
---

# Session Summary: Evaluation Optimization, Compact Corpus & RADG Action Space Formalization

## 1. Executive Summary

In this session, I executed a focused optimization and bugfix cycle on the **Automated Evaluation Harness (Sprint 4: Evaluation & Polish)** for the Master's thesis:
> *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*

Following an empirical live benchmarking run where external API quota constraints were encountered, I addressed three critical requirements:
1. **Token Economy Optimization:** Created an equiprobable, representative compact benchmark corpus ([`tests/evaluation/test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json)) containing 20 intent demands (5 per risk class) to enable fast, low-cost regression and live API benchmarking.
2. **Strict Ternary Action Space Formalization:** Completely purged the obsolete `"reject"` action across the entire codebase—including baseline implementations, schema definitions, plotting routines, and documentation—enforcing the mathematically formal RADG action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$.
3. **HITL Interruption Origin Metric Bugfix:** Diagnosed and fixed a metrics bug in [`tests/evaluation/scripts/metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/metrics.py) where autonomous baselines without human intervention (Baseline A: LLM-Only and Baseline C: Always-Off HITL) erroneously registered Phase 6 HITL interruptions due to unconditional replan counting.

All 324 unit tests pass with zero regressions under Strict TDD (`pytest-expert`), and all IEEE/PoliMi publication figures were recompiled cleanly.

---

## 2. Key Accomplishments & Technical Deliverables

### 2.1 Compact Benchmark Corpus ([`test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json))
- Extracted 20 highly representative intent demands from the full 107-demand corpus ([`tests/evaluation/test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json)), balanced equiprobably across the four thesis risk classes:
  - **Class I (Nominal):** 5 demands (`intent_nom_01` to `05`) testing direct and multi-hop paths, optical SNR margins, and bandwidth SLA constraints.
  - **Class II (Ambiguous):** 5 demands (`intent_amb_01` to `05`) testing missing endpoints, vague geographical regions, and underspecified constraints requiring Phase 3b reverse prompting.
  - **Class III (Infeasible):** 5 demands (`intent_inf_01` to `05`) testing long-haul multi-hop routes exceeding 400G physical SNR thresholds or low receiver power, requiring Phase 6 physical replanning.
  - **Class IV (Adversarial):** 5 demands (`intent_adv_01` to `05`) testing non-existent topological nodes, prompt injection attacks, and negative optical parameters failing Layer 1 CFG validation.
- Configured [`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py) to use `test_corpus_compact.json` as the default input corpus, significantly decreasing token consumption during live API evaluation while preserving mathematical rigor.

### 2.2 Complete Purge of "Reject" & Strict Ternary RADG Action Alignment
- **Mathematical Alignment:** The thesis system model (Chapter 3, Section 3.4; [[architecture/ProblemStatement_v5]]) formalizes the Risk-Adaptive Decision Gate (RADG) action space as strictly ternary:
  $$\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$$
  In this architecture, invalid, ambiguous, or adversarial requests are intercepted early by the Context-Free Grammar (CFG) AST validator or the Phase 3b Semantic Gate ($U_{sem} > \tau_{sem}$), triggering a `clarify` action. Physical infeasibilities trigger a `replan` action. The system never emits an uninformative "reject".
- **Codebase Sanitization:**
  - Standardized the output contract in [`tests/evaluation/baselines/base.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/base.py): `BaselineResult.action: Literal["approve", "clarify", "replan"]`.
  - Updated Baseline A ([`tests/evaluation/baselines/llm_only.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only.py)) to remove `"reject"` from the structured Pydantic schema, prompt instructions, and error fallbacks (mapping errors to `"replan"`).
  - Updated Baseline C ([`tests/evaluation/baselines/always_off_hitl.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_off_hitl.py)) to emit `"replan"` when the solver fails to find any candidate path.
  - Updated Baseline D ([`tests/evaluation/baselines/traditional_sdon.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/traditional_sdon.py)) to emit `"replan"` on missing paths or physical infeasibility.
  - Cleaned up [`src/nodes/radg_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/radg_node.py) to eliminate legacy `"reject"` branches in human response parsing.
  - Purged `"reject"` from [`tests/evaluation/scripts/plotter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/plotter.py), removing the Burgundy `#85200C` reject bar from `gate_decision_distribution.pdf` and `.png`.
  - Updated test assertions in [`tests/unit/test_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_baselines.py) to expect `"replan"`.
  - Updated [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) documentation.

### 2.3 HITL Interruption Origin Metric Bugfix ([`metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/metrics.py))
- **Bug Diagnosis:** In `plot_hitl_interruption_origin`, Baselines A (LLM-Only) and C (Always-Off HITL) showed non-zero Phase 6 HITL interruptions on Class III infeasible demands, despite both baselines being designed as fully autonomous ($N_{hitl} = 0$).
- **Root Cause:** In `compute_radg_metrics()`, the counters `semantic_clarifies` and `physical_replans` were incremented whenever `actual_action == "replan"`, regardless of whether a human interruption actually occurred.
- **Resolution:** Encapsulated the breakdown counters inside `if interrupts > 0:`. Now, autonomous baselines without human intervention correctly report $0$ HITL interruptions originating from both Phase 3b and Phase 6.

### 2.4 Empirical Benchmark Verification
- Executed full mock benchmark across all 5 baselines and 20 compact intents (100 runs in 0.8s):
  - **Proposed RADG:** $UAR = 0.0\%$, $QFR = 100.0\%$, $PIIR = 100.0\%$, with selective human intervention ($N_{hitl} \le 1$).
  - **Baseline A (LLM-Only):** Catastrophic $UAR = 80.0\%$, zero human intervention ($N_{hitl} = 0$).
  - **Baseline C (Always-Off HITL):** Severe safety violation with $UAR = 50.0\%$, zero human intervention ($N_{hitl} = 0$).
  - **Baseline B (Always-On HITL):** High operational friction ($N_{hitl} = 2$).
  - **Baseline D (Traditional SDON):** Zero token overhead, $100\%$ manual setup ($N_{hitl} = 1$).
- Recompiled all 4 publication-quality figures in [`tests/evaluation/results/figures/`](file:///home/felipeab/MultiAgentON/tests/evaluation/results/figures/):
  - `gate_decision_distribution.pdf` & `.png`: now strictly ternary (`approve`, `clarify`, `replan`).
  - `hitl_interruption_origin.pdf` & `.png`: accurately reflects zero interruptions for Baselines A and C.
  - `latency_vs_tokens.pdf` & `.png`: updated with compact run telemetry.
  - `success_vs_uar.pdf` & `.png`: corroborating the fundamental $UAR = 0.0\%$ thesis invariant.

---

## 3. Verification & Test Suite Status

- **Strict TDD Compliance:** Executed full unit test suite with `uv run pytest`.
- **Result:** `324 passed, 14 deselected, 3 warnings in 7.94s` (100% pass rate, 0 regressions).

---

## 4. Handover & Next Steps

1. **Live API Benchmarking Execution:** Once Kimi LLM API quota regenerates, execute `uv run python tests/evaluation/scripts/run_benchmark.py --live` with the new compact corpus to collect final real-world token and latency distributions.
2. **Slide 14 Integration:** Embed the recompiled vector/PNG figures into Slide 14 of the thesis defense presentation deck.
3. **Thesis Chapter 4 Drafting:** Incorporate the finalized empirical results into Chapter 4 using `thesis-coauthor`.
