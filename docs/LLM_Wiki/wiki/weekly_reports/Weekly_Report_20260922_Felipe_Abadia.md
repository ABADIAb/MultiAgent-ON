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

5. **Benchmark Expansion across All 4 Risk Classes & Multi-Turn Refinement:**
   - Extended the evaluation framework to cover all 20 demands in [`tests/evaluation/test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json): Class I Nominal (5), Class II Ambiguous (5), Class III Physically Infeasible (5), and Class IV Adversarial (5).
   - Diagnosed and resolved multi-turn ghost constraint leakage in SLM recovery: fortified [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py) with deterministic full-replacement classification for standalone routing feedback, and isolated [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) from previous PDDL contamination on replacements.
   - Verified that 100% of intercepted intents successfully recover upon receiving standard feedback to Phase 7 Synthesis with $UAR = 0.0\%$.

6. **Four Core Validation Pillars Formalization & Runner Modernization (`run_evaluation.py`):**
   - Transformed `run_nominal_eval.py` into [`tests/evaluation/run_evaluation.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/run_evaluation.py), integrating comprehensive telemetry across the Four Core Validation Pillars:
     * **Pillar 1 (Semantic):** Built `compute_constraint_retention()` to measure CRR (94.1% on operable demands), CFG Pass Rate (100.0%), and Semantic Agreement ($1 - d_{sem} = 0.860$).
     * **Pillar 2 (Physical Feasibility):** Verified $UAR = 0.0\%$ (Strict Invariant) and 100% Turn 1 interception of physical/semantic risk.
     * **Pillar 3 (Efficiency):** Integrated `TokenTracker` callback telemetry capturing prompt, completion, and total tokens across all turns (7,375 tok/intent; 5.62s nominal latency).
     * **Pillar 4 (Gate Reliability):** Verified Gate Decision Accuracy (95.0%, 19/20), False Positive Rate (0.0%), and Selective HITL Precision (100.0%).

7. **Thesis Architecture Pivot and Tone Refactor:**
   - Realigned the core narrative across [[ProblemStatement_v5]], [[Architecture_v5]], and LaTeX drafts to explicitly emphasize the optimization of Human-in-the-Loop (HITL) operator interventions.
   - Systematically replaced fatalistic terminology ("Unsafe Approval Rate", "safety guarantee") with academically precise operational terminology ("Unfeasible Approval Rate", "operational integrity") across the Wiki, LaTeX drafts, and the `tests/evaluation` Python harness.
   - Consolidated the theoretical metrics into a dedicated [[EvaluationFramework_v5]] to prevent redundancies and inconsistencies with the benchmark README.

8. **Thesis Chapter 4 Drafting & Plural RADGs Architecture Refactor:**
   - Drafted all three sections of Chapter 4 (`4_1_Network_State_and_GraphRAG.md`, `4_2_Semantic_and_QoT_Validation_Modules.md`, `4_3_Decision_Outcomes_and_Orchestration_Flow.md`), mathematically grounding network state abstraction, AST CFG validation, two-layer semantic uncertainty ($U_{sem}$), and analytical GN-model physics against `src/`.
   - Standardized terminology across the thesis drafts, outlines, architecture feature docs, and codebase to "Risk-Adaptive Decision Gates (RADGs)" (plural), formally distinguishing the Semantic RADG (Phase 3) and Physical RADG (Phase 6).
   - Renamed Section 3.4 to `3_4_Risk_Adaptive_Decision_Gates.md`, resolved merged Section 3.5 references, authored missing concept notes (`Human_in_the_Loop.md`, `Constraint_Isolation.md`, `PDDL.md`), and completed a repository-wide Wiki Deep Lint.

9. **Chapter 3 and Chapter 4 Restructuring for Narrative Fluidity:**
   - Consolidated all mathematical formulations (GN-model physics, $U_{sem}$) and formal grammars (PDDL CFG) into Chapter 3, establishing it purely as the theoretical system model.
   - Completely redesigned Chapter 4 to trace the end-to-end software lifecycle across four newly defined sections: Orchestration and Network Context (4.1), The Semantic Engine (4.2), The Physical Engine and System Resilience (4.3), and Plan Synthesis and Verification (4.4).
   - Removed raw PDDL code blocks and math proofs from Chapter 4 to focus on software implementation mechanics and storytelling.

10. **Chapter 3 Top-Down Storytelling & Anti-AI Refactor:**
    - Reordered and renamed the theoretical framework sections in Chapter 3 to enforce a top-down storytelling structure, introducing the End-to-End Conceptual Framework (3.2) before the deep mathematical dives into Strict Neurosymbolic Separation (3.3) and RADGs (3.4).
    - Executed a comprehensive tone refactor across Chapter 3 to eliminate latent AI-like clichés (e.g., orthogonal, composite, monotonic) and consolidated the use of "operational integrity" over generic phrasing.
    - Simplified the Context-Free Grammar (CFG) formalization to focus strictly on Abstract Syntax Tree parsing logic and corrected inaccuracies regarding GN-model complexity.
    - Updated the `thesis-coauthor` skill to mandate top-down storytelling and expand the blacklist of prohibited AI vocabulary for future drafting sessions.

11. **Overleaf LaTeX Chapter Consolidation & Woven Figure Narrative Integration:**
    - Consolidated and mathematically validated standalone Overleaf-ready LaTeX chapter text files: [`chapter_3_system_model.txt`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/chapter_3_system_model.txt) and [`chapter_4_implementation.txt`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/4_NPImp/chapter_4_implementation.txt), verifying line 1 `\chapter`, zero `\usepackage`, balanced environments, and strict float barrier placements.
    - Integrated in-text explanatory narratives for all active figures and placeholders (`Figure~\ref{fig:conceptual_framework}`, `Figure~\ref{fig:radg_decision_space}`, `Figure~\ref{fig:reverse_prompting_loop}`, `Figure~\ref{fig:langgraph_execution_flow}`, `Figure~\ref{fig:semantic_engine}`), detailing axes, operational zones, structural stages, and feedback loops.
    - Upgraded the `thesis-coauthor` skill (`SKILL.md`, `writing-standards.md`, `consistency-protocol.md`) with explicit rules on storytelling transitions, in-text figure walk-throughs, expanded anti-AI cliché blacklist (banning "swimlane", "paradigm", "mandates", "govern", "certified", "canonical", "empirical"), and 1:1 Markdown-to-LaTeX synchronization.
    - Resolved Item 2 in [`Drafting_Backlog.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/Drafting_Backlog.md) (`\label{chap:implementation}`).

12. **Thesis Chapter 3 Figure Refactoring, Archival & Caption Standardization (2026-09-23):**
    - Refactored `conceptual_framework` (`figs_SystemModel/src/diagrams/conceptual_framework.drawio`): stripped redundant right-hand panel cards, significantly enlarged typography (titles to 15–16 pt bold, subtext to 13 pt, gates to 14 pt bold), and aligned symmetric HITL clarify and replan boxes without text collisions.
    - Moved `neural_symbolic_subsystems` and `reverse_prompting_loop` to `figs_SystemModel/archive/`, deferring the reverse prompting diagram to Chapter 4 (Semantic Engine).
    - Synchronized Chapter 3 text ([`3_4_Risk_Adaptive_Decision_Gates.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates.md) and [`chapter_3_system_model.txt`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/chapter_3_system_model.txt)) by removing the obsolete 5-step figure explanation and explicitly introducing the formal LLM-as-a-judge role in evaluating Layer 2 semantic divergence ($d_{sem}$).
    - Eliminated hardcoded figure numbering across Drafting Recommendations in all markdown drafts to use semantic references exclusively.
    - Authored a dedicated standalone compilation script ([`export_diagrams.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/src/diagrams/export_diagrams.py)) in the diagrams directory with automated `--crop` for manual and headless batch generation.
    - Standardized figure captions across Chapters 3 and 4 to academic thesis standard (`\small\itshape`).
    - Upgraded the `thesis-coauthor` skill and `figure-guidelines.md` reference with strict rules on large typography, visual anti-redundancy, and anti-AI phrasing.

---

## 3. What do I plan to accomplish next week?

1. **Comparative Baseline Benchmarking:** Execute automated evaluation across the 4 formal baselines (Proposed RADG, Baseline A Monolithic LLM, Baseline B Always-On HITL, Baseline C Traditional SDON) using the validated 20-demand compact corpus and export publication-ready telemetry.
2. **Review Thesis Defense Deck with Academic Advisor:** Present the 16-slide draft, timing targets, and empirical benchmark figures on Slide 14 to Prof. Massimo Tornatore for formal academic review and feedback.
3. **Thesis Chapter 4 Experimental Drafting:** Ingest validated empirical metrics into Chapter 4 of the thesis manuscript and prepare defense slide rehearsals.

---

## 4. Do You Need Support?

- **Current Status:** Full 20-demand benchmark evaluation across all 4 risk classes successfully verified at 95.0% gate decision accuracy ($UAR=0.0\%$, 19/20 demands, 0.0% FPR, 100% selective HITL precision). Ready to execute comparative baselines and schedule presentation rehearsal with Prof. Massimo Tornatore.
- **Advisor Review:** Ready to schedule presentation rehearsal with Prof. Massimo Tornatore.

---

## 5. One-Sentence Summary

I modernized the evaluation harness with full Four Pillars telemetry, validated the compact corpus on the 17-node Nobel-Germany topology, and executed a complete architectural tone refactor to emphasize HITL optimization and deterministic physical feasibility across all thesis drafts and codebase, followed by a major restructuring of Chapters 3 and 4 to optimize narrative fluidity.
