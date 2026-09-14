---
title: "Weekly Report 2026-09-15"
date: 2026-09-15
tags: [weekly, report, thesis, presentation, evaluation, benchmark, radg, ollama, polimi]
status: active
---

# Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date:
2026-09-15

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the previous report [[weekly_reports/Weekly_Report_20260908_Felipe_Abadia]] & Thesis Defense Milestones)*
1. **Thesis Defense Presentation Strategy & Tooling:** Design and implement a reproducible co-authoring workflow for PowerPoint presentations (`.pptx`), integrating directly with the official Politecnico di Milano presentation template.
2. **Real-Time Live Preview & File-Locking Solution:** Establish a non-blocking preview pipeline allowing real-time visual inspection of presentation slides during programmatic generation without triggering Windows file-lock collisions.
3. **Master's Thesis Defense Deck Generation:** Author the initial 16-slide thesis defense deck strictly adhering to the 15 Golden Rules established by Prof. Massimo Tornatore (15-minute time budget, problem-specific ToC, no terminal periods on bullet points, explicit contributions, formal problem formulation, and structured speaker notes).
4. **Tooling & Skill Upgrade:** Deprecate the legacy `presentation-designer` skill and establish the comprehensive `presentation-coauthor` skill in `.agents/skills/presentation-coauthor/`.
5. **Sprint 4 Synthetic Benchmark Corpus & Evaluation Harness:** Advance the test scenarios, baseline definitions, and metrics framework for 17-node German backbone evaluation.

---

## 2. What did I actually accomplish?

1. **Master's Thesis Defense Presentation Deck & Automated Headless Export Pipeline:**
   - Deprecated legacy presentation tooling and established the authoritative [`presentation-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/SKILL.md) skill, codifying Prof. Massimo Tornatore's 15 Golden Rules (strict 15-minute budget, bespoke problem-driven ToC, no terminal periods on bullets, timed speaker notes) and official Politecnico di Milano template standards (16:9 widescreen, institutional palette `#0F2C53` / `#85200C`, `Titillium Web SemiBold`).
   - Engineered [`export_presentation.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/export_presentation.py) via Windows PowerShell COM automation (`PowerPoint.Application`), bypassing Windows file-locking constraints to export vector `.pdf` and per-slide 1080p `.png` previews in under 6 seconds, with an automated `--watch` background compiler.
   - Programmatically authored the complete 16-slide defense deck ([`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py), [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md)), aligning problem formulation, failure modes, and neurosymbolic decoupling with Chapter 3 formalisms.
   - Implemented native Office Math (OMML) XML injection in DrawingML (`<a14:m><m:oMathPara>`), eliminating equation rasterization and rendering crisp, scalable Cambria Math formulas.
   - Synchronized all manual visual refinements back into the programmatic generator (modular comparison pills, paradigm-shift card layout, and floating validation pillars on Slide 13).

2. **Thesis Title Modernization & Core Ecosystem Synchronization:**
   - Evaluated terminology tradeoffs between multi-agent systems and neurosymbolic orchestration, concluding that multi-agent systems overpromise distributed negotiation protocols not present in our deterministic pipeline.
   - Formally updated the thesis title across the active ecosystem to: *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*.
   - Synchronized the updated title across system rules (`AGENTS.md`), project metadata (`openspec/config.yaml`), architecture documents (`Architecture_v5.md`, `ProblemStatement_v5.md`), thesis roadmap (`Writing_Roadmap_v1.md`, `Thesis_Outline_v4.md`), presentation specifications, and codebase entrypoints.

3. **LLM-Assisted Intent Reconciliation & SLA Constraint Mapping:**
   - Implemented [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py), applying Chain-of-Thought prompting and Pydantic structured output to classify operator feedback into `FULL_REPLACEMENT` (complete request reset) vs `PARTIAL_UPDATE` (delta constraint adjustment), eliminating semantic contradictions during Phase 3b and Phase 6 HITL refinement loops.
   - Integrated Mock GraphRAG dynamic rescoping: automatically re-extracts the $k$-hop subtopology neighborhood whenever operator refinement alters routing endpoints.
   - Extended the PDDL Context-Free Grammar (CFG) in [`src/core/pddl_validator.py`](file:///home/felipeab/MultiAgentON/src/core/pddl_validator.py) with production rule `(bandwidth <int>)`, updated [`src/core/symbolic_solver.py`](file:///home/felipeab/MultiAgentON/src/core/symbolic_solver.py) to preserve bandwidth demands, and calibrated 400G physical SNR threshold selection (`21.5 dB`) in [`src/nodes/qot_validation.py`](file:///home/felipeab/MultiAgentON/src/nodes/qot_validation.py) for realistic physical infeasibility detection on multi-hop paths.

4. **Local Multi-Provider LLM Engine & Hardware Architecture Profiling (Ollama):**
   - Engineered `OllamaChatOpenAI` in [`src/core/llm.py`](file:///home/felipeab/MultiAgentON/src/core/llm.py) with automatic WSL2 host IP resolution and robust Pydantic structured output extraction, enabling transparent local open-weights execution alongside cloud providers (Kimi, OpenRouter).
   - Conducted a hardware architecture audit on an RTX 3050 Laptop GPU (4 GB VRAM) with 8 GB RAM, profiling `qwen2.5:3b`, `phi4-mini:latest`, `qwen3:4b`, `qwen3.5:4b`, and `gemma4:e4b`.
   - Empirically proved that **`qwen2.5:3b` is the optimal default** because it fits 100% in VRAM (2.15 GB), delivering ~1.5s latency at ~70 tok/s with zero RAM swapping, while establishing `phi4-mini` as the structured direct alternative and supporting `qwen3:4b` with dynamic token budgeting (3000 tokens) and native `<think>` regex stripping.
   - Hardened Phase 3 Semantic Gate prompts, eliminating `:init` topology contamination in [[reverse_prompt]] to prevent false semantic divergences.

5. **Sprint 4 Evaluation Framework Modernization & Automated Follow-Up Protocol:**
   - Consolidated the comparative evaluation matrix to 4 core systems: **Proposed (Neurosymbolic RADG)**, **Baseline A (Monolithic LLM)**, **Baseline B (Always-On HITL)**, and **Baseline C (Traditional SDON / PCE)**. Completely deprecated and removed redundant `Always-Off HITL`.
   - Formalized Traditional SDON / PCE as a static industrial reference representing manual provisioning workflows taking hours to days/weeks ($UAR = 0.0\%$, tokens = `N/A`, latency = `Hours / Days`).
   - Refined the Four Core Validation Pillars: standardized Pillar 2 on $UAR = 0.0\%$ (safety invariant) and $PIIR = 100.0\%$ (infeasibility interception), and Pillar 3 on E2E Latency, Token Footprint, and HITL reduction ($\Delta N_{hitl}$), demoting GraphRAG token reduction percentage to an implementation detail.
   - Implemented an automated follow-up recovery protocol in [`proposed_radg.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/proposed_radg.py) and [`always_on_hitl.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_on_hitl.py) using LangGraph `Command(resume=...)`, injecting `STANDARD_FOLLOW_UP_INTENT` on gate interruptions (`clarify` / `replan`) to measure true E2E latency and cumulative token footprint through to synthesis per intent risk class (`I_Nominal`, `II_Ambiguous`, `III_Infeasible`, `IV_Adversarial`).
   - Standardized the 100-demand benchmark corpus ([`test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json)) and 20-demand compact subset ([`test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json)), purging legacy `"reject"` branches to strictly enforce the ternary RADG action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$.
   - Built the automated runner ([`run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py)) and IEEE/PoliMi publication plotting suite ([`plotter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/plotter.py)), exporting vector PDFs and 300+ DPI PNGs.
   - Verified 100% test pass rate across all 350 unit tests under Strict TDD with zero regressions.

---

## 3. What do I plan to accomplish next week?

1. **Review Thesis Defense Deck with Academic Advisor:** Present the 16-slide draft, timing targets, and narrative structure to Prof. Massimo Tornatore for formal academic review and feedback.
2. **Slide 14 Presentation Integration:** Integrate the newly generated empirical figures (`latency_vs_tokens.png`, `success_vs_uar.png`, `hitl_interruption_origin.png`) into Slide 14 of the thesis defense presentation deck.
3. **Thesis Chapter 4 Drafting:** Begin drafting Chapter 4 (*Experimental Evaluation & Numerical Results*) using `thesis-coauthor`, leveraging the vector PDFs and `summary_table.md`.

---

## 4. Do You Need Support?

- **Current Status:** No external blockers. The automated evaluation harness, baseline definitions, metrics calculation, publication figures, and local multi-model inference engine are fully completed, verified, and operational.
- **Advisor Review:** I will schedule a checkpoint to present the 15-minute defense deck draft and discuss empirical benchmark results.

---

## 5. One-Sentence Summary

I modernized the Sprint 4 evaluation framework with an automated follow-up recovery protocol for true E2E latency/token accounting, consolidated the 4-baseline comparative matrix, established `qwen2.5:3b` as the optimal 100% VRAM local engine, authored the 16-slide defense presentation deck with native OMML math, and maintained 350 passing unit tests under Strict TDD.
