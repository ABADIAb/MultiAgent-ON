---
title: "Session Summary: Sprint 4 Evaluation Modernization, Automated Follow-Up Protocol & 4-Baseline Matrix"
date: 2026-09-14
tags: [session-summary, evaluation, benchmark, radg, follow-up, sdon, hitl, strict-tdd, sprint-4]
status: active
---

# Session Summary: Sprint 4 Evaluation Modernization, Automated Follow-Up Protocol & 4-Baseline Matrix

## 1. Executive Summary

In this session, I executed a major architectural modernization of the Sprint 4 evaluation and benchmarking framework (`tests/evaluation/`) for the Master's thesis:
> *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*

Key technical breakthroughs:
1. **Automated Follow-Up Protocol for Real E2E Latency & Cumulative Token Accounting:** Designed and implemented an automated recovery mechanism in `tests/evaluation/baselines/proposed_radg.py` and `always_on_hitl.py`. When intents are intercepted at decision gates (Phase 3b `clarify` or Phase 6 `replan`), the harness automatically resumes execution via LangGraph `Command(resume=...)` using a standardized recovery intent (`STANDARD_FOLLOW_UP_INTENT = "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`). This enables measuring true End-to-End latency and cumulative token consumption through to final plan synthesis, broken down across all four intent risk categories (`I_Nominal`, `II_Ambiguous`, `III_Infeasible`, `IV_Adversarial`).
2. **Dual-Action Tracking Architecture:** Decoupled `initial_action` from `final_action` in `BaselineResult`. The initial gate verdict (`clarify` / `replan`) is preserved in `action` and `initial_action` to evaluate gate accuracy metrics (GDA, FPR, UAR, PIIR), while `final_action` (`approve`) and cumulative elapsed time/tokens reflect completed multi-turn recovery.
3. **Consolidation to a 4-Baseline Comparative Matrix:** Deprecated and completely removed redundant Baseline C (`Always-Off HITL`) across source code, runner scripts, plotting utilities, and unit tests, consolidating the experimental comparison into 4 core systems:
   - **Proposed (Neurosymbolic RADG):** Selective HITL via calibrated risk gates.
   - **Baseline A (Monolithic LLM):** Zero HITL, direct prompting with full topology context.
   - **Baseline B (Always-On HITL):** Mandatory human intervention at Phase 3b and Phase 6.
   - **Baseline C (Traditional SDON / PCE):** Static industrial reference.
4. **Pillar 2 & Pillar 3 Metric Refinements:**
   - *Pillar 2 (Physical Feasibility):* Eliminated redundant QFR ($QFR = 100\% - UAR$), focusing strictly on $UAR = 0.0\%$ (safety invariant) and $PIIR = 100.0\%$ (physical infeasibility interception).
   - *Pillar 3 (Efficiency):* Demoted GraphRAG token reduction percentage from high-level pillars to an implementation detail, standardizing on E2E Latency ($T_{E2E}$), Token Footprint (Prompt, Completion, Total), and HITL reduction ($\Delta N_{hitl}$).
5. **Traditional SDON Formalized as a Static Industrial Reference:** Formalized Traditional SDON as a static reference baseline representing manual provisioning workflows taking hours to days/weeks. It does not parse natural language or execute live benchmark iterations; metrics reflect the industrial status quo ($UAR = 0.0\%$, Tokens = `N/A`, Latency = `Hours / Days`).

All 350 unit tests pass under Strict TDD (`pytest-expert`), the codebase is 100% clean under `ruff check`, and the offline benchmark dry-run verified generation of consolidated markdown tables and 4 IEEE/PoliMi publication figure sets.

---

## 2. Technical Deliverables & Source Code Map

### Baseline Implementations (`tests/evaluation/baselines/`)
- [`base.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/base.py): Added `STANDARD_FOLLOW_UP_INTENT` and updated `BaselineResult` schema with `initial_action` and `final_action`.
- [`proposed_radg.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/proposed_radg.py): Multi-turn recovery loop resuming on interrupts via `Command(resume=...)`, accumulating cumulative tokens across all turns/messages, and preserving `initial_action` for gate metrics while completing to `final_action = "approve"`.
- [`always_on_hitl.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_on_hitl.py): Updated multi-turn execution to process both Phase 3b and Phase 6 checkpoints with the standard follow-up intent, accumulating latency and tokens across multiple turns ($N_{hitl} \ge 2$).
- [`traditional_sdon.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/traditional_sdon.py): Converted to static industrial reference returning constant metrics ($UAR = 0.0\%$, tokens = 0, $N_{hitl} = 1$, latency = 0.0, static metadata).
- `always_off_hitl.py`: Deleted file; removed from [`__init__.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/__init__.py).

### Metrics, Plotting & Benchmark Runner (`tests/evaluation/scripts/`)
- [`metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/metrics.py):
  - Removed `qfr_percent` from Pillar 2 and `token_reduction_percent` from Pillar 3.
  - Implemented `compute_per_class_metrics()` to calculate mean E2E latency and total tokens per risk category.
  - Updated `generate_summary_markdown()` with 4-baseline headers, `N/A` handling for Traditional SDON, and the secondary per-class latency/token table.
- [`plotter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/plotter.py):
  - Purged `always_off` from labels and colors.
  - Updated `plot_latency_vs_tokens` (automated baselines only, total tokens).
  - Updated `plot_success_vs_uar` (PIIR vs UAR).
- [`run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py):
  - Default baselines set to `proposed_radg,llm_only,always_on,traditional_sdon`.
  - Added mock dispatcher support for `RefinedIntentAnalysis` and recovery feedback.
  - Formatted live terminal output with Rich tables for both 4-Pillar summary and per-class latency/tokens.

### Test Suite & Documentation
- [`tests/unit/test_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_baselines.py): Tested static reference behavior for Traditional SDON, deleted `TestAlwaysOffHITLBaseline`, added `test_proposed_radg_ambiguous_intent_recovery_via_follow_up`, and removed `always_off` from polymorphic contract.
- [`tests/unit/test_metrics.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_metrics.py): Removed `qfr_percent` and `token_reduction_percent` assertions, and added `TestPerClassMetrics`.
- [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md): Documented the 4-baseline matrix, updated Pillars 2 & 3 definitions, and detailed the follow-up recovery protocol.

---

## 3. Verification & Benchmark Dry-Run Results

- **Unit Tests:** `uv run pytest` $\to$ **350 passed, 34 deselected, 3 warnings in 5.23s** (100% pass rate).
- **Linter:** `uv run ruff check src/ tests/` $\to$ **All checks passed!**
- **Benchmark Dry-Run:** Executed in 1.36s with zero errors, generating:
  - `summary_table.md` with 4-baseline consolidated metrics and per-class latency/token table.
  - Raw telemetry files (`raw_results.json`, `raw_results.csv`).
  - 4 IEEE / PoliMi thesis figure sets in vector PDF and 300+ DPI PNG:
    - `latency_vs_tokens` (.pdf, .png)
    - `success_vs_uar` (.pdf, .png)
    - `hitl_interruption_origin` (.pdf, .png)
    - `gate_decision_distribution` (.pdf, .png)
