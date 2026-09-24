---
title: "Session Summary: 2026-09-23 - Modular Comparative Baselines, Interactive CLI & Comparative Visualization Suite"
date: 2026-09-23
tags: [session-summary, debrief, evaluation, baselines, proposed-radg, always-on-hitl, llm-only, cli, radar-chart, pillars-bar, rich, questionary, sprint-4]
status: active
---

# Session Summary: 2026-09-23 - Modular Comparative Baselines, Interactive CLI & Comparative Visualization Suite

## 1. Executive Summary

In this session, I formalized, engineered, and hardened the Sprint 4 comparative evaluation environment by implementing modular evaluation baselines (**Proposed RADG**, **Always-On HITL**, and **LLM-Only**), a unified interactive CLI in [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py), and an automated cross-baseline visualization suite.

Rather than adopting a code-duplication anti-pattern (copying `src/` modules across baselines), I implemented a clean, decoupled architecture in [`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/) that directly imports and wraps production nodes and physical-layer engines from `src/`. This preserves strict scientific rigor in ablation testing by isolating the decision gate policies while keeping `src/` as the single source of truth.

Additionally, I standardized per-baseline segregated telemetry storage (`tests/evaluation/baselines/<baseline>/results/run_<timestamp>/`), built a flexible historical run version picker, engineered publication-ready comparative visual generators (Four Pillars Grouped Bar Chart and 5-Axis Polar Radar Chart), resolved critical CLI ergonomics issues (Ctrl+C terminal hangs and report truncation), and archived legacy evaluation scripts.

The implementation was verified using Strict TDD (16 new unit tests, 337 total passing tests), 100% clean static analysis with Ruff, and live empirical execution across all three baselines using local open-weights inference (`qwen2.5:3b` via Ollama).

---

## 2. Key Accomplishments

### 2.1 Modular Baseline Architecture ([`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/))

1. **Common Framework ([`tests/evaluation/baselines/common/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/)):**
   - **Runner & Callback Telemetry (`runner.py`):** Encapsulated the multi-turn graph execution loop, `TokenTracker` (LangChain callback tracking prompt, completion, and total tokens), and automated [[concepts/Human_in_the_Loop|HITL]] recovery injection (`STANDARD_FOLLOW_UP_INTENT`).
   - **Metrics Engine (`metrics.py`):** Formally implemented the Four Core Validation Pillars metrics: Constraint Retention Rate (CRR), Context-Free Grammar Pass Rate (CFG-PR), Semantic Agreement ($1 - d_{sem}$), Unfeasible Approval Rate (UAR), Physical Infeasibility Interception Rate (PIIR), Latency ($T_{E2E}$), Token Footprint ($T_{tokens}$), Mean HITL Turns ($N_{hitl}$), Gate Decision Accuracy (GDA), and False Positive Rate (FPR).
   - **Multi-Format Telemetry Reporter (`reporter.py`):** Built snapshot and canonical exporters generating structured JSON, CSV tables, and publication-ready Markdown summaries alongside automated visual asset triggers.

2. **Baseline 1: Proposed RADG ([`tests/evaluation/baselines/proposed_radg/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/proposed_radg/)):**
   - Implemented the full V5 neurosymbolic pipeline with two-stage fail-fast Risk-Adaptive Decision Gates ([[architecture/Architecture_v5|Architecture V5]]).
   - Turn 1 nominal intents pass autonomously with zero human interruptions ($N_{hitl}=0$), while ambiguous and infeasible intents are intercepted early at Phase 3b and Phase 6.

3. **Baseline 2: Always-On HITL ([`tests/evaluation/baselines/always_on_hitl/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_on_hitl/)):**
   - Formulated as an ablation testing the operational cost of unadapted, paranoid human review on Nominal traffic (`Class I_Nominal`).
   - Built `always_on_semantic_gate_node`: unconditionally forces $U_{sem} = 1.0$ and `usem_passed = False` on Turn 1, triggering a mandatory operator clarification interrupt at Phase 3b.
   - Upon receiving the standard follow-up intent, Turn 2 delegates to the standard Semantic Gate, completing to Phase 7 Synthesis with $N_{hitl} = 1$ and capturing the resulting latency and token overhead.

4. **Baseline 3: LLM-Only ([`tests/evaluation/baselines/llm_only/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only/)):**
   - Formulated as an ablation testing the absence of pre-deployment semantic gating before configurations reach the optical network controller.
   - Built `bypassed_semantic_gate_node`: bypasses the Phase 3 HITL filter, allowing configurations to push directly through physics validation.
   - Built `controller_surrogate_radg_node`: Phase 6 acts as the surrogate for the network controller.
     - Nominal demands pass if physically feasible.
     - Ambiguous, Infeasible, or Adversarial demands reaching the controller simulate deployment rejections, triggering a `replan` interrupt on Turn 1.
     - Tracks False Positives ($FPR$) and Unfeasible Approvals ($UAR$), then re-runs with recovery feedback to complete synthesis.

### 2.2 Segregated Results Storage & Run Version Resolution

- Segregated all baseline evaluation outputs into self-contained, timestamped run folders:
  * `tests/evaluation/baselines/proposed_radg/results/run_YYYYMMDD_HHMMSS/`
  * `tests/evaluation/baselines/always_on_hitl/results/run_YYYYMMDD_HHMMSS/`
  * `tests/evaluation/baselines/llm_only/results/run_YYYYMMDD_HHMMSS/`
- Each run encapsulates `evaluation_results.json`, `evaluation_results.csv`, `evaluation_summary.md`, and visual figures (`gate_accuracy_matrix`, `latency_tokens_overhead`, `presentation_slide_dashboard` in 300 DPI PNG and vector PDF).
- Built run resolution logic (`resolve_baseline_run()`):
  - In batch comparison mode, users can target specific historical timestamps via `--proposed-run`, `--hitl-run`, and `--llm-run`, or select them interactively via questionary list prompts.
  - Defaults automatically to the latest timestamped run for each baseline if none is specified, preventing accidental overwriting or stale artifact reuse.

### 2.3 Comparative Analysis Mode & Publication Visualization Suite

- Introduced `--mode compare` in [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) for instantaneous offline cross-baseline evaluation:
  * **Four Pillars Grouped Bar Chart (`comparative_pillars_bar.png` / `.pdf`):** 4-panel comparative visualization in [`tests/evaluation/generate_visuals.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/generate_visuals.py) contrasting Unfeasible Approval Rate ($UAR$), Operator Fatigue ($N_{hitl}$), End-to-End Latency ($T_{E2E}$), and Token Footprint ($T_{tokens}$) across all three baselines.
  * **5-Axis Polar Radar Chart (`comparative_radar_chart.png` / `.pdf`):** Publication-grade polar radar chart illustrating the multi-objective trade-offs between Safety ($1 - UAR$), Autonomy ($1 - \text{norm}(N_{hitl})$), Speed ($1 - \text{norm}(T_{E2E})$), Token Efficiency ($1 - \text{norm}(T_{tokens})$), and Structural Quality ($CFG\text{-}PR$).
  * **Consolidated Comparative Markdown Report:** Generated in `tests/evaluation/baselines/common/results/run_YYYYMMDD_HHMMSS/comparative_summary.md`, aggregating metrics and comparative conclusions for thesis Chapter 5.

### 2.4 Terminal Ergonomics & CLI Bugfixes

- **Graceful Ctrl+C Handling:** Diagnosed and fixed a terminal hang where Questionary caught SIGINT internally and returned `None`. Implemented `prompt_select()` and `prompt_text()` helper functions that cleanly intercept `None` and exit immediately (`sys.exit(0)`). Added outer `KeyboardInterrupt` handlers in both [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py) and [`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py).
- **Full Planning Report Display:** Removed a hardcoded `[:1000]` character slice in the interactive CLI viewer, allowing complete display of Phase 7 Planning Reports (SNR margins, physical lightpaths, and auditable gate traces).

### 2.5 Legacy Archiving & Documentation Synchronization

- Archived the legacy monolithic runner [`run_evaluation.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/archive/run_evaluation.py) and legacy results into [`tests/evaluation/archive/`](file:///home/felipeab/MultiAgentON/tests/evaluation/archive/).
- Updated [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) with detailed commands for single baseline runs, comparative analysis mode, run selection flags, and metric definitions.

### 2.6 Evaluation Harness Multi-Turn Resilience & Watchdogs Hardening

- **Multi-Stage $U_{sem}$ Score Parsing ([`src/nodes/semantic_gate_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py)):** Refactored `_score_semantic_agreement` with prioritized decimal float regex extraction, key phrase matching (`d_sem`, `score`, `divergence`), and concluding number selection, eliminating false ambiguity fallbacks caused by model chain-of-thought or numbered constraint lists.
- **Direct Operator Approval Bypass ([`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py)):** Enhanced the interactive CLI to offer `✅ Proceed with current understanding (Approve and continue to solver)` when `pddl_valid == True`, routing directly to Phase 4 (Symbolic Solver) without redundant re-parsing. Added explicit alerts when maximum turns are reached without resolution.
- **5-Minute Global Wall-Clock Watchdog ([`tests/evaluation/baselines/common/runner.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/runner.py)):** Established `DEFAULT_INTENT_TIMEOUT = 300.0` (5 minutes) across the multi-turn execution loop and baseline evaluators to safeguard against hanging models during local SLM inference. Established an explicit execution status taxonomy (`completed`, `timeout`, `max_turns_exceeded`, `error`).
- **Telemetry Formulas Extension ([`tests/evaluation/baselines/common/metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/metrics.py)):** Added Task Completion Rate (TCR) and timeout tracking into Pillar 3 metrics.

---

## 3. Verification & Quality Gates

1. **Unit Testing (Strict TDD):**
   - Created dedicated baseline, timeout watchdog, and robust score extraction tests in [`tests/unit/test_evaluation_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_evaluation_baselines.py) and [`tests/unit/test_semantic_gate.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_semantic_gate.py).
   - Full test suite verified: **341 passing unit tests** in ~3.2s (`uv run pytest tests/unit/`) with zero regressions.
2. **Code Quality & Linting:**
   - 100% clean check with zero errors across all modules (`uv run ruff check src/ tests/`).
3. **Live Empirical Verification with Local Open-Weights Model (`qwen2.5:3b`):**
   - **Proposed RADG:** 
     * Verified 1-turn autonomous pass on nominal traffic (`"Route 100G from Hamburg to Berlin with at least 15 dB GSNR."`, 11.18s, $N_{hitl}=0$, $U_{sem}=0.100$, 1/5 QoT feasible, Synthesis complete).
     * Verified fail-fast pre-deployment catch on ambiguous intent (`"Route traffic to Berlin with high quality"`, $U_{sem}=0.500 > 0.300$), followed by 2-turn recovery to completion in 19.31s via standard recovery intent.
   - **Always-On HITL:** 
     * Verified Turn 1 forced clarification interrupt at `hitl_clarify` ($U_{sem}=1.000$), followed by verified direct operator approval bypass (`pddl_valid == True`) proceeding immediately to solver without re-parsing, completing in 18.71s ($N_{hitl}=1$).
   - **LLM-Only:** 
     * Verified Turn 1 semantic gate bypass ($U_{sem}=0.500$), demonstrating a False Positive where ambiguous traffic with hallucinated endpoints is deployed to the network (5.34s) solely due to physical feasibility.
4. **Offline Comparative Generation:**
   - Verified that running `python -m tests.evaluation.main --mode compare` executes instantaneously (< 2 seconds) and generates publication-grade PNG and vector PDF charts without requiring LLM API connectivity.

---

## 4. Next Steps & Handover State

1. **Full Comparative Benchmark Runs:** Execute all 4 risk classes across Proposed RADG, Always-On HITL, and LLM-Only to produce final comparative figures for Thesis Chapter 5 and defense Slide 14.
2. **Draft Thesis Chapter 5 (Experimental Evaluation):** Integrate empirical tables, Four Pillars radar charts, and comparative ablation figures into the thesis narrative.
3. **Advisor Consultation:** Present the comparative baseline outcomes, radar chart trade-offs, and updated slide deck to Prof. Massimo Tornatore.
