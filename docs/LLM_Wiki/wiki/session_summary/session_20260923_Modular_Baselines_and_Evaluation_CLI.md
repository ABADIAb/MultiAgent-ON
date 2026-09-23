---
title: "Session Summary: 2026-09-23 - Modular Comparative Baselines & Interactive Evaluation CLI"
date: 2026-09-23
tags: [session-summary, debrief, evaluation, baselines, proposed-radg, always-on-hitl, llm-only, cli, rich, questionary, sprint-4]
status: active
---

# Session Summary: 2026-09-23 - Modular Comparative Baselines & Interactive Evaluation CLI

## 1. Executive Summary

In this session, I expanded the Sprint 4 evaluation environment by formalizing, engineering, and verifying the comparative evaluation baselines (**Proposed RADG**, **Always-On HITL**, and **LLM-Only**) alongside a unified, interactive CLI in [`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py). 

Rather than adopting a code-duplication anti-pattern (copying `src/` modules across baselines), I implemented a clean, decoupled architecture in [`tests/evaluation/baselines/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/) that directly imports and wraps production nodes and physical-layer engines from `src/`. This preserves strict scientific rigor in ablation testing by isolating the decision gate policies while keeping `src/` as the single source of truth.

The implementation was verified using Strict TDD (16 new unit tests, 337 total passing tests), 100% clean static analysis with Ruff, and live empirical execution across all three baselines using local open-weights inference (`qwen2.5:3b` via Ollama).

---

## 2. Key Accomplishments

### 2.1 Modular Baseline Architecture (`tests/evaluation/baselines/`)

1. **Common Framework ([`tests/evaluation/baselines/common/`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/common/)):**
   - **Runner & Callback Telemetry (`runner.py`):** Encapsulated the multi-turn graph execution loop, `TokenTracker` (LangChain callback tracking prompt, completion, and total tokens), and automated [[concepts/Human_in_the_Loop|HITL]] recovery injection (`STANDARD_FOLLOW_UP_INTENT`).
   - **Metrics Engine (`metrics.py`):** Formally implemented the Four Core Validation Pillars metrics: Constraint Retention Rate (CRR), Context-Free Grammar Pass Rate (CFG-PR), Semantic Agreement ($1 - d_{sem}$), Unfeasible Approval Rate (UAR), Physical Infeasibility Interception Rate (PIIR), Latency ($T_{E2E}$), Token Footprint ($T_{tokens}$), Mean HITL Turns ($N_{hitl}$), Gate Decision Accuracy (GDA), and False Positive Rate (FPR).
   - **Multi-Format Telemetry Reporter (`reporter.py`):** Built snapshot and canonical exporters generating structured JSON, CSV tables, and publication-ready Markdown summaries alongside automated visual figure generation.

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

### 2.2 Unified Interactive CLI ([`tests/evaluation/main.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/main.py))

- Engineered an interactive terminal interface using `rich` (banners, phase progress, styled panels, Markdown report rendering) and `questionary` (arrow-key selection).
- Provides two distinct operating modes:
  - **Interactive Mode:** Allows selecting preset benchmark demands or typing custom intents, displaying live progress across all 7 pipeline phases, and providing an interactive prompt on HITL interrupts (Refine, Standard Recovery, Abort).
  - **Evaluation Benchmark Mode:** Automated batch evaluation over compact (20 demands) or full (107 demands) corpora, filtering by risk class or demand ID, generating a Four Pillars summary table, and exporting artifacts to `tests/evaluation/results/<baseline>/`.

### 2.3 Documentation Synchronization ([`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md))

- Updated the directory tree and instructions to document the modular baseline taxonomy and provide ready-to-run CLI commands for interactive and evaluation modes.

---

## 3. Verification & Quality Gates

1. **Unit Testing (Strict TDD):**
   - Created [`tests/unit/test_evaluation_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_evaluation_baselines.py) with 16 comprehensive unit tests covering graph compilation, node policies across turns, and Four Pillars metrics aggregation.
   - Full test suite verified: **337 passing unit tests** in 2.94s (`uv run pytest tests/unit/`) with zero regressions.
2. **Code Quality & Linting:**
   - 100% clean check with zero errors across all modules (`uv run ruff check src/ tests/`).
3. **Live Empirical Verification with Local Open-Weights Model (`qwen2.5:3b`):**
   - **Proposed RADG:** Verified 1-turn autonomous pass on `intent_nom_01` (13.08s, $N_{hitl}=0$, $U_{sem}=0.100$, 1/5 QoT feasible, Synthesis complete).
   - **Always-On HITL:** Verified Turn 1 forced clarification interrupt at `hitl_clarify`, followed by Turn 2 recovery and synthesis to completion ($N_{hitl}=1$, 11.09s, 7,937 tokens).
   - **LLM-Only:** Verified Turn 1 semantic gate bypass, followed by Phase 6 controller rejection interrupt on ambiguous intent `intent_amb_01`, and Turn 2 recovery to completion (8,867 tokens).

---

## 4. Next Steps & Handover State

1. **Full Comparative Benchmark Runs:** Execute all 4 risk classes across Proposed RADG, Always-On HITL, and LLM-Only to produce final comparative figures for Thesis Chapter 5 and defense Slide 14.
2. **Advisor Consultation:** Present the modular baseline architecture and interactive CLI to Prof. Massimo Tornatore.
