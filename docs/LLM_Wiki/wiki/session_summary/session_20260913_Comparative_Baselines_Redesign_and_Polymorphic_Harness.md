---
title: "Session Summary: Comparative Baselines Redesign & Polymorphic Harness Implementation"
date: 2026-09-13
tags: [session-summary, evaluation-baselines, sprint4, polymorphic-contract, llm-only, always-on-hitl, always-off-hitl, traditional-sdon, proposed-radg]
status: active
---

# Session Summary: Comparative Baselines Redesign & Polymorphic Harness Implementation

## 1. Executive Summary

In this session, we formalized and implemented the comparative evaluation baselines for the Master's thesis evaluation suite (Sprint 4). Prompted by the need to conduct a rigorous ablation study of both the **Neurosymbolic Separation** (LLM vs deterministic tools) and the **Risk-Adaptive Decision Gate (RADG)** (selective HITL vs static policies), we redesigned the baseline taxonomy into four comparative baselines plus the Proposed architecture:
1. **Baseline A: Monolithic LLM (LLM-Only)**
2. **Baseline B: Always-On HITL (Paranoid)**
3. **Baseline C: Always-Off HITL (Reckless Autonomous)**
4. **Baseline D: Traditional SDON / PCE (Non-LLM Industrial Standard)**
5. **Proposed System: Neurosymbolic RADG (Selective Fail-Fast Gates)**

We established a clean, modular package strictly located in [`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/) to prevent polluting `src/`. All five systems share a unified, polymorphic execution interface defined in [`base.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/base.py) returning a standardized `BaselineResult` schema. We synchronized the evaluation framework in [[architecture/ProblemStatement_v5]] and [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md), authored 20 dedicated unit tests in [`tests/unit/test_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_baselines.py) following Strict TDD, formatted all code with `ruff`, and verified 100% test pass rate across the full test suite (314 passed tests).

---

## 2. Key Accomplishments & Conceptual Formalizations

### 2.1 Baseline Taxonomy & Ablation Study Formalization
We aligned the baselines to directly challenge and prove the thesis's two core scientific hypotheses:
- **Hypothesis 1 (Neurosymbolic Separation):** Monolithic LLMs cannot accurately compute physical optical parameters (GSNR, non-linear interference) or topological routing. *Baseline A (LLM-Only)* exposes this failure mode through high Unsafe Approval Rates ($UAR > 0\%$) and topological disconnects.
- **Hypothesis 2 (Risk-Adaptive HITL Efficiency & Safety):** Engaging the human operator on every intent causes intolerable operational friction and latency, while removing the human causes catastrophic network misconfigurations. *Baseline B (Always-On HITL)* establishes the upper bound of operational friction ($N_{hitl} \ge 2$), while *Baseline C (Always-Off HITL)* demonstrates the danger of bypassing decision gates ($N_{hitl} = 0$, high $UAR$).
- **Industry Ground Truth:** *Baseline D (Traditional SDON / PCE)* anchors the comparison against today's non-LLM control planes, proving that the proposed system achieves the same $0\%$ $UAR$ safety standard while drastically reducing manual setup effort.

### 2.2 Polymorphic Interface & Package Implementation (`tests/evaluation/baselines/`)
We constructed the baseline execution layer with zero dependencies on `src/` modifications:
- [`base.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/base.py):
  - Defined the `BaselineResult` schema (`intent_id`, `baseline_id`, `action`, `selected_path`, `computed_gsnr_dB`, `qot_feasible`, `pddl_valid`, `hitl_interrupts`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `execution_time_s`, `planning_report`, `error`, `metadata`).
  - Created `BaseBaseline(ABC)` with `count_tokens()` (`cl100k_base` via `tiktoken`) and `verify_optical_path()` (evaluating candidate routes against the true GN-model physics via `assess_qot`).
  - Implemented dynamic registration and dispatch: `get_baseline()`, `list_baselines()`, and `run_baseline()`.
- [`llm_only.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only.py): Monolithic prompt injecting full 17-node Nobel-Germany topology and intent, calling `get_llm()` and verifying proposed routes with GN-model physics.
- [`always_on_hitl.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_on_hitl.py): Neurosymbolic execution with mandatory human confirmation interrupts at Phase 3b and Phase 6 ($N_{hitl} \ge 2$).
- [`always_off_hitl.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_off_hitl.py): Neurosymbolic execution with Semantic Gate and RADG bypassed ($N_{hitl} = 0$).
- [`traditional_sdon.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/traditional_sdon.py): Non-LLM deterministic pipeline using structured parameters, Yen's $K$-SP, and conservative $+3\text{ dB}$ static design margins ($0$ tokens, $N_{hitl} = 1$).
- [`proposed_radg.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/proposed_radg.py): Wrapper around `compile_graph()`, programmatically handling LangGraph `interrupt()` events for automated benchmarking.
- [`__init__.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/__init__.py): Clean package exports.

### 2.3 Documentation Synchronization
- Synchronized [[architecture/ProblemStatement_v5]] Section 8.1 table and text to reflect the 4 baselines vs. Proposed.
- Synchronized [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) Section 3 with detailed architectural matrix and code examples for the polymorphic contract.

---

## 3. Verification & Quality

- **Unit Testing (Strict TDD):** Authored 20 unit tests in [`tests/unit/test_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_baselines.py) covering registry dispatch, token counting, optical verification, individual baseline behaviors across all 4 intent classes, and polymorphic contract adherence.
- **Full Test Suite:** Executed `uv run pytest` — all 314 unit tests passed cleanly with 0 regressions.
- **Lint & Formatting:** Executed `uv run ruff check` and `uv run ruff format`, ensuring 100% code quality compliance.

---

## 4. Handover State & Next Steps

1. **Implement Automated Evaluation Harness:** Now that the polymorphic baselines package is complete, develop `tests/evaluation/scripts/run_benchmark.py` to iterate over `tests/evaluation/test_corpus.json` (107 demands) across all baselines.
2. **Implement Metrics & Visualization:** Develop `metrics.py` (calculating CRR, CFG-PR, UAR, QFR, PIIR, $\Delta T_{tokens}$, $\Delta N_{hitl}$, GDA) and `plotter.py` (generating high-resolution IEEE/PoliMi style figures for thesis Chapter 4 and defense Slide 14).
3. **Execute Benchmark & Collect Empirical Data:** Run the benchmark suite to populate empirical figures and tables.
