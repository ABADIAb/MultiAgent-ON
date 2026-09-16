---
title: "Weekly Report 2026-09-22"
date: 2026-09-22
tags: [weekly, report, thesis, evaluation, benchmark, radg, ollama, qwen2.5, sprint-4]
status: active
---

# Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date:
2026-09-22

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the previous report [[weekly_reports/Weekly_Report_20260915_Felipe_Abadia]])*
1. **Redesign Evaluation Test Suite:** Re-architect and implement the benchmarking harness from scratch around [`test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json) to reliably evaluate the full 7-phase neurosymbolic pipeline against the defined baselines.
2. **Review Thesis Defense Deck with Academic Advisor:** Present the 16-slide draft, timing targets, and narrative structure to Prof. Massimo Tornatore for formal academic review and feedback.
3. **Slide 14 Presentation Integration & Chapter 4 Preparation:** Integrate empirical figures from the newly redesigned benchmark runs into Slide 14 of the defense presentation deck, and prepare the experimental data foundations for Thesis Chapter 4.

---

## 2. What did I actually accomplish?

1. **Automated Nominal Evaluation Benchmark Harness & Non-Destructive Snapshotting:**
   - Engineered [`tests/evaluation/run_nominal_eval.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/run_nominal_eval.py) for reproducible evaluation of the Class I Nominal Intent cohort on the 17-node Nobel-Germany optical core backbone topology.
   - Built automated multi-format telemetry exporters (JSON, CSV, Markdown) generating timestamped run snapshots (`nominal_results_<timestamp>.*`) alongside canonical latest files to eliminate data loss across iterative benchmark runs.
   - Embedded automated [[concepts/Human_in_the_Loop|HITL]] recovery handling: when a decision gate triggers (`clarify` at Phase 3b or `replan` at Phase 6), the harness intercepts the pause, logs diagnostic telemetry, and automatically resumes execution using the standardized recovery intent (`"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`).

2. **Root-Cause Analysis & Progressive Prompt Hardening for Local Open-Weights Inference (`qwen2.5:3b`):**
   - Conducted a 4-run iterative optimization cycle identifying and eliminating three subtle failure modes inherent to small quantized models (3.1B parameters, 2.15 GB VRAM on RTX 3050):
     * **PDDL Constraint Placement & Dummy Bandwidth:** Solved dummy `(bandwidth 1)` injection and `:init` placement in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) by enforcing strict `:goal (and ...)` isolation and few-shot examples, paired with defensive bitrate validation in [`src/nodes/qot_validation.py`](file:///home/felipeab/MultiAgentON/src/nodes/qot_validation.py).
     * **Prompt-Example Leaking in Reverse Prompting:** Solved `intent_nom_04` hallucinating `"avoiding node Leipzig"` by replacing the single biased prompt example in [`src/nodes/reverse_prompt.py`](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) with diverse few-shot examples and filtering verbose topology predicates (`connected`, `link-active`) via `_clean_pddl_for_reverse_prompt()`.
     * **Lossy Intent Ingestion Summarization:** Solved `intent_nom_02` false-divergence by preserving the operator's verbatim message in `active_intent` within [`src/nodes/intent_ingest.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_ingest.py).

3. **Empirical Benchmark Verification (100.0% Pass Rate):**
   - In Run 4, achieved a **100.0% Autonomous Pass Rate (5/5)** on the first turn with **zero human interruptions** ($N_{hitl} = 0$).
   - Confirmed the strict physical safety invariant: **Unsafe Approval Rate $UAR = 0.0\%$**, with all lightpaths verified feasible under analytical GN-model physics ($\text{GSNR} \ge \text{GSNR}_{th}$).
   - Demonstrated high computational efficiency: mean end-to-end turnaround of **5.75s** using local WSL2 open-weights inference.
   - Proved that `qwen2.5:3b` is fully sufficient for the neurosymbolic pipeline without requiring heavier commercial cloud APIs.

4. **Testing & Code Quality Gates:**
   - All 321 unit tests passing under Strict TDD (`uv run pytest tests/unit/`) in 2.45s with zero regressions.
   - Repository-wide linting verified clean (`uv run ruff check src/ tests/`).

5. **Benchmark Expansion across All 4 Risk Classes & 100.0% Gate Decision Accuracy (20/20):**
   - Extended the evaluation framework to cover all 20 demands in [`tests/evaluation/test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json): Class I Nominal (5), Class II Ambiguous (5), Class III Physically Infeasible (5), and Class IV Adversarial (5).
   - Diagnosed and resolved multi-turn ghost constraint leakage in SLM recovery: fortified [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py) with deterministic full-replacement classification for standalone routing feedback, and isolated [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) from previous PDDL contamination on replacements.
   - Achieved **100.0% Gate Decision Accuracy (20/20)** across the 17-node Nobel-Germany topology using local `qwen2.5:3b`: 5/5 auto-approved on first try ($N_{hitl}=0$), 5/5 ambiguous demands caught fail-fast at Phase 3b (`clarify`), 5/5 infeasible demands caught at Phase 6 (`replan`), and 5/5 adversarial demands caught (`clarify`/`replan`), with **$UAR = 0.0\%$** and 100% successful multi-turn recovery to Phase 7 Synthesis.

---

## 3. What do I plan to accomplish next week?

1. **Comparative Baseline Benchmarking:** Execute automated evaluation across the 4 formal baselines (Proposed RADG, Baseline A Monolithic LLM, Baseline B Always-On HITL, Baseline C Traditional SDON) using the validated 20-demand compact corpus and export publication-ready telemetry.
2. **Review Thesis Defense Deck with Academic Advisor:** Present the 16-slide draft, timing targets, and empirical benchmark figures on Slide 14 to Prof. Massimo Tornatore for formal academic review and feedback.
3. **Thesis Chapter 4 Experimental Drafting:** Ingest validated empirical metrics into Chapter 4 of the thesis manuscript and prepare defense slide rehearsals.

---

## 4. Do You Need Support?

- **Current Status:** Full 20-demand benchmark evaluation across all 4 risk classes successfully verified at 100% gate decision accuracy ($UAR=0.0\%$, 20/20). Ready to execute comparative baselines and schedule presentation rehearsal with Prof. Massimo Tornatore.
- **Advisor Review:** Ready to schedule presentation rehearsal with Prof. Massimo Tornatore.

---

## 5. One-Sentence Summary

I validated a 100% Gate Decision Accuracy (20/20 demands, $UAR=0.0\%$, 17.46s latency) across all four risk classes on the 17-node Nobel-Germany benchmark using local `qwen2.5:3b`, eliminated multi-turn ghost constraint leakage in intent reconciliation and PDDL parsing, and preserved all 321 passing unit tests under Strict TDD.
