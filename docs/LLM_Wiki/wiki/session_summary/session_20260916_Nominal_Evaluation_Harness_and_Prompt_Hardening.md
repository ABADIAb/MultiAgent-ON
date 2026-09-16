---
title: "Session Summary: Nominal Intent Benchmark Harness, Prompt Hardening & Gate Calibration"
date: 2026-09-16
tags: [session-summary, evaluation, benchmark, pddl-parser, semantic-gate, reverse-prompt, hitl, sprint-4]
status: active
---

# Session Summary: Nominal Intent Benchmark Harness, Prompt Hardening & Gate Calibration

## 1. Executive Summary

In this session, we established a reproducible, automated evaluation harness for the nominal evaluation slice of Sprint 4, benchmarked the pipeline on the standardized 17-node Nobel-Germany topology using local open-weights inference (`qwen2.5:3b`), and executed targeted prompt and logic hardening across four core pipeline nodes to eliminate spurious decision gate interceptions on nominal requests.

Key breakthroughs and engineering accomplishments:
1. **Automated Nominal Evaluation Harness (`run_nominal_eval.py`):**
   - Implemented an automated runner evaluating the 5 nominal intents from [`test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json).
   - Embedded automated [[concepts/Human_in_the_Loop|HITL]] recovery handling: when a decision gate triggers (`clarify` at Phase 3b or `replan` at Phase 6), the harness intercepts the pause, logs diagnostic telemetry, and automatically resumes execution using the standardized recovery intent (`"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."`).
   - Integrated configurable per-turn timeouts (default 120s) and comprehensive multi-format export to `tests/evaluation/results/` (`nominal_results.json`, `nominal_results.csv`, `nominal_summary.md`).

2. **Root-Cause Analysis of Local LLM Divergences (`qwen2.5:3b`):**
   - Small quantized models exhibit a strong predisposition to fill empty PDDL template slots with dummy zero values (e.g., `(min-gsnr 0)` or `(min-bandwidth 0)`).
   - On waypoint intents (e.g., `"via Leipzig"`), the model hallucinated `(avoid-node ...)` exclusions for unrelated intermediate nodes.
   - In the [[architecture/features/semantic_gate_node|Semantic Gate]] evaluator, raw input intents contained orchestration metadata/tags, inducing semantic divergence ($U_{sem}$) false positives.

3. **Multi-Node Prompt & Logic Hardening:**
   - **[[architecture/features/pddl_parser|PDDL Parser]] (`src/nodes/pddl_parser.py`):** Fortified system and user prompts with explicit negative constraint rules. Strictly forbade generating default zero-values (`0 dB`, `0 Gbps`) and prohibited inferring `avoid-node` or `avoid-link` unless the operator explicitly used exclusion keywords ("avoid", "bypass", "exclude").
   - **[[architecture/features/semantic_gate_node|Semantic Gate]] (`src/nodes/semantic_gate_node.py`):** Implemented `_clean_intent_for_evaluation()` to strip technical metadata, prompt prefixes, and system markers, presenting the LLM agreement judge with pure natural language. Recalibrated agreement scale instructions.
   - **[[architecture/features/reverse_prompt|Reverse Prompt]] (`src/nodes/reverse_prompt.py`):** Added explicit instruction to disregard zero-value dummy constraints so that reconstructed natural language accurately mirrors real operator requirements without hallucinated zero thresholds.
   - **[[architecture/features/intent_reconciler|Intent Reconciler]] (`src/nodes/intent_reconciler.py`):** Added a deterministic heuristic override: if both source and target endpoints change during interactive clarification, classify the mutation as `FULL_REPLACEMENT` rather than `PARTIAL_UPDATE` to prevent invalid composite PDDL specifications.

4. **Verification & Testing:**
   - Full test suite passing: **321 passed, 3 warnings in 2.40s** (`uv run pytest tests/unit/`).
   - Zero lint errors across repository (`uv run ruff check src/ tests/`).

---

## 2. Technical Deliverables & Source Code Map

### Source Code Hardening (`src/nodes/`)
- [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py):
  - Hardened `PDDL_TRANSLATION_SYSTEM_PROMPT` to prohibit default/dummy zero-value generation and forbid negative constraint hallucinations for waypoint requests.
  - Added strict constraint mapping instructions ensuring that nominal intents produce minimal, clean PDDL definitions.
- [`src/nodes/semantic_gate_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py):
  - Added `_clean_intent_for_evaluation()` to sanitize input intents prior to LLM evaluation.
  - Refined evaluation prompt to prevent false-positive semantic divergence scores on clean nominal intents.
- [`src/nodes/reverse_prompt.py`](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py):
  - Instructed reverse translation prompt to ignore dummy 0 values (e.g. `(min-gsnr 0)`).
- [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py):
  - Added structural check to enforce `FULL_REPLACEMENT` taxonomy when endpoints are redefined.

### Evaluation Suite (`tests/evaluation/`)
- [`tests/evaluation/run_nominal_eval.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/run_nominal_eval.py): Automated benchmark runner for Class I Nominal Intents with multi-turn HITL resumption, timeout safety, and telemetry export.
- [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md): Comprehensive guide detailing corpus structure, runner CLI flags, environment setup, and metric definitions.
- [`tests/evaluation/results/nominal_results.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/results/nominal_results.json): Full per-demand telemetry trace.
- [`tests/evaluation/results/nominal_results.csv`](file:///home/felipeab/MultiAgentON/tests/evaluation/results/nominal_results.csv): Tabular metric export.
- [`tests/evaluation/results/nominal_summary.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/results/nominal_summary.md): Summary markdown report.

---

## 3. Verification & Benchmark Baseline Comparison

- **Unit Test Execution:**
  ```bash
  uv run pytest tests/unit/
  # Output: 321 passed, 3 warnings in 2.40s
  ```
- **Linter Quality Gate:**
  ```bash
  uv run ruff check src/ tests/
  # Output: All checks passed!
  ```
- **Evaluation Baseline:** The benchmark harness generated initial baseline metrics documenting where `qwen2.5:3b` encountered decision gate trips prior to prompt hardening. The prompt for follow-up validation in a fresh session was provided to verify the complete resolution of gate trips.

---

## 4. Next Steps & Handover State

1. **Re-run Nominal Evaluation:** Execute `uv run python tests/evaluation/run_nominal_eval.py` in a clean session to verify that all 5 Class I intents achieve `initial_action = "approve"` without triggering false-positive `clarify` or `replan` interrupts.
2. **Expand to Ambiguous & Infeasible Classes:** Once nominal intent stability is confirmed, extend the automated harness to evaluate Class II (`Ambiguous`), Class III (`Physically Infeasible`), and Class IV (`Adversarial`) demands.
3. **Thesis & Weekly Report Updates:** Ingest empirical metrics into thesis Chapter 4 experimental section and weekly tracking reports.
