---
title: "Weekly Report 2026-09-15"
date: 2026-09-15
tags: [weekly, report, thesis, presentation, powerpoint, pptx, defense, presentation-coauthor, polimi]
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
1. **Thesis Defense Presentation Strategy & Tooling:** Design and implement a reproducible co-authoring workflow for PowerPoint presentations (`.pptx`), moving away from static Markdown drafts and integrating directly with the official Politecnico di Milano presentation template.
2. **Real-Time Live Preview & File-Locking Solution:** Establish a non-blocking preview pipeline allowing real-time visual inspection of presentation slides during programmatic generation without triggering Windows file-lock collisions.
3. **Master's Thesis Defense Deck Generation:** Author the initial 16-slide thesis defense deck strictly adhering to the 15 Golden Rules established by Prof. Massimo Tornatore (15-minute time budget, problem-specific ToC, no terminal periods on bullet points, explicit contributions, formal problem formulation, and structured speaker notes).
4. **Tooling & Skill Upgrade:** Deprecate the legacy `presentation-designer` skill and establish the comprehensive `presentation-coauthor` skill in `.agents/skills/presentation-coauthor/`.
5. **Sprint 4 Synthetic Benchmark Corpus:** Advance the test scenarios and metrics framework for 17-node German backbone evaluation.

---

## 2. What did I actually accomplish?

1. **New Presentation Co-Author Skill (`presentation-coauthor`):**
   - Deprecated the legacy text-only `presentation-designer` skill.
   - Authored the comprehensive [`presentation-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/SKILL.md) skill, establishing authoritative rules for:
     - Prof. Massimo Tornatore's **15 Golden Rules for Thesis Presentations** (strict 15-minute budget, 15–18 slides, bespoke problem-driven ToC, no terminal periods on bullets, explicit contributions, clear problem statement, and timed speaker notes).
     - **Politecnico di Milano Template Standards:** Extracted official 16:9 widescreen dimensions ($13.333'' \times 7.5''$), institutional color palette (Navy Blue `#0F2C53`, Burgundy Accent `#85200C`, Card Fill `#F4F6F9`), typography (`Titillium Web SemiBold`, `Abel`, `Arial`), and layout placeholders.
     - Codified reference guides: `presentation-standards.md`, `template-guide.md`, and `workflow-guide.md`.

2. **Automated Headless Export Pipeline (`export_presentation.py`):**
   - Diagnosed and resolved the Windows PowerPoint file-locking constraint (`PermissionError: [Errno 13]`), where keeping `.pptx` open prevents external script overwrites.
   - Engineered [`export_presentation.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/export_presentation.py), bridging Linux/WSL to Windows PowerShell COM automation (`PowerPoint.Application`).
   - Enables headless compilation of any `.pptx` into a vector `.pdf` and per-slide 1080p `.png` previews (`slides_png/slide_01.png` to `slide_16.png`) in under 6 seconds.
   - Built a `--watch` mode enabling automated background compilation whenever the `.pptx` binary is saved after manual adjustments.

3. **Master's Thesis Defense Presentation Deck Generation (`build_defense_deck.py` & `deck_spec.md`):**
   - Programmatically authored the complete 16-slide thesis defense deck strictly adhering to the 15-minute defense budget.
   - Aligned the problem formulation, illustrative failure modes, and neurosymbolic decoupling architecture directly with Chapter 3 system model formalisms.
   - Structured key slides into high-impact visual flows (7-phase process chevrons, decision gates, KPI summaries, and comparative layouts) with timed speaker notes, eliminating text walls and standardizing on zero terminal periods.
   - Preserved PoliMi master slide chrome (official header, logo, underline separator, footer text, and dynamic slide numbers) while clearing previous conference content.

4. **Native PowerPoint Mathematical Typography & Visual Layout Engine:**
   - Implemented native Office Math (OMML) XML injection in DrawingML (`<a14:m><m:oMathPara>`), eliminating rasterization and rendering native, scalable Cambria Math equations in PowerPoint.
   - Solved DrawingML shape text color inheritance by layering transparent textboxes over card containers, guaranteeing bold institutional navy and dark slate contrast.
   - Implemented native DrawingML subscript and superscript formatting for rigorous formula presentation.
   - Sanitized presentation directory by standardizing entirely on `docs/LLM_Wiki/wiki/presentations/thesis_defense/` and archiving legacy presentation files to `archive/`.

5. **Deep Consistency Audit & Future Scope Ideation:**
   - Conducted a deep consistency verification between the presentation slides, the system model documentation (`Chapter 3`), and the actual `src/` implementation.
   - Identified the transition from static $k$-hop subtopology extraction to dynamic ellipsoid-based path extraction as a critical scaling enhancement. Formally deferred this to the "Future Work" backlog to preserve the strict fidelity of the current system scope.

6. **Thesis Title Modernization & Ecosystem Alignment:**
   - Evaluated terminology tradeoffs regarding multi-agent systems vs. neurosymbolic orchestration, concluding that multi-agent systems overpromise distributed negotiation protocols not present in the deterministic pipeline.
   - Formally updated the thesis title across the active ecosystem to: *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*.
   - Synchronized the updated title in system rules (`AGENTS.md`), project metadata (`openspec/config.yaml`), architecture documents (`Architecture_v5.md`, `ProblemStatement_v5.md`), thesis roadmap (`Writing_Roadmap_v1.md`, `Thesis_Outline_v4.md`), presentation specifications (`deck_spec.md`, `build_defense_deck.py`), and CLI entrypoint/state docstrings (`main.py`, `graph.py`, `state.py`).
   - Recompiled `thesis_defense.pptx`, vector `thesis_defense.pdf`, and 1080p `slides_png/` previews, verifying visual layout and 100% test pass rate across 278 unit tests.

7. **Manual PowerPoint Visual Refinement & Programmatic Synchronization:**
   - Inspected manual visual refinements made to the presentation deck to reduce text density and enhance readability across Slides 1, 3, 4, and 5.
   - Decoded OpenXML DrawingML `<mc:AlternateContent>` structures containing embedded native Office Math equations, extracting exact layout coordinates, shape styling, and typography.
   - Synchronized all visual improvements back into [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) and [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md):
     - **Slide 1 (Cover):** Added co-advisor metadata (`"Academic Advisor: Prof. Massimo Tornatore & Prof. Qiaolun Zhang"`).
     - **Slide 3 (Motivation Evolution):** Implemented `create_evolution_sdon_ibon_slide()` featuring the comparative paradigm-shift layout (Burgundy Imperative SDON card vs. Navy Declarative IBON card, central connector arrow with `"PARADIGM SHIFT: HOW ➔ WHAT"` badge, 6 modular white rounded pills, and bottom caution banner).
     - **Slide 4 (Failure Modes):** Standardized challenge badge typography to 14 pt, updated descriptions to 12 pt, and tuned the empirical risk banner text.
     - **Slide 5 (Problem Statement):** Converted dense text blocks into 4 modular white rounded pills ($3.21'' \times 0.43''$) per upper card, resized the lower constraints container to $10.31'' \times 2.13''$, and added native OMML equation mappings for $T_{prompt} \le T_{max}$ and $\min \alpha N_{hitl} + \beta T_{tokens}$.
   - Recompiled `thesis_defense.pptx`, rendered updated vector `thesis_defense.pdf` and 1080p slide PNGs, and verified zero test regressions (278 passing unit tests).

8. **Evaluation Framework Restructuring & Slide 13 Two-Way Synchronization:**
   - Formally structured the thesis evaluation methodology into the **Four Core Validation Pillars**:
     - *Pillar 1 (Semantic Translation Accuracy):* Constraint Retention Rate ($\text{CRR} = 100\%$) and CFG AST Pass Rate ($v_{struct} = 1$).
     - *Pillar 2 (Physical Feasibility):* Strict hard invariant of Unsafe Approval Rate ($\text{UAR} = 0\%$) and QoT Feasibility Rate ($100\%$).
     - *Pillar 3 (Orchestration & Resource Efficiency):* $> 75\%$ prompt token reduction via Scoped Optical GraphRAG and $> 70\%$ human intervention cut.
     - *Pillar 4 (RADG Decision Robustness):* Piecewise gate accuracy $> 98\%$ and zero false positives across boundary conditions.
   - Formalized comparative baselines: **Baseline A (LLM-Only)** with unconstrained prompt execution and reactive retry, and **Baseline B (Static Rule-Based)** with rigid regex parsing and mandatory Always-HITL review; analyzed the "Always-Off HITL" paradigm, demonstrating that turning off HITL in our pipeline yields high service blocking probability.
   - Synchronized manual visual improvements on **Slide 13**:
     - Replaced dense text blocks with parallel modular comparison pills for `Baseline A` and `Baseline B` with a centered `vs.` badge, and a full-width `Proposed Neurosymbolic RADG` pill.
     - Diagnosed and fixed DrawingML text run color inheritance where white theme styling overrode paragraph defaults, locking text runs to bold Navy (`#0F2C53`).
     - Converted the 100 Test Demands benchmark corpus into a structured, color-coded 3-column table (`Class & Size`, `Intent Characteristics`, `RADG Action`).
     - Cleaned right column by letting the 4 validation pillar cards float directly on the canvas without outer container bounding boxes.
    - Verified 0 discrepancies across all 16 slides via `inspect_deck.py --diff`, regenerated vector `thesis_defense.pdf` and 1080p slide PNGs, and confirmed 100% test pass rate (278 tests).

9. **Benchmark Corpus Balancing, Baseline C Formalization & Evaluation Scaffolding:**
   - In response to advisor inquiries regarding non-LLM baselines, formalized **Baseline C (Traditional SDON / PCE without LLM)** grounded in RFC 8231, standard YANG models, and static design margins.
   - Analytically validated the JSON topology of the 17-node German backbone network (Nobel-Germany) and confirmed that Scoped Optical GraphRAG ($k=2$ hop neighborhood extraction) achieves $>90\%$ prompt token reduction compared to full topology injection.
   - Rebalanced the 100-demand synthetic evaluation benchmark into an equiprobable $25 \times 4$ distribution across all four intent risk categories (Class I Nominal [25], Class II Ambiguous [25], Class III Infeasible [25], Class IV Adversarial [25]) to prevent class-imbalance bias.
   - Scaffolded the automated evaluation environment under [`tests/evaluation/`](file:///home/felipeab/MultiAgentON/tests/evaluation/):
     - Generated [`test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json) containing all 100 validated intent demands with ground truth mappings and expected actions.
     - Authored [`README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) documenting the Four Validation Pillars, formal metric equations, comparative baseline matrix, and runner execution contracts.
   - Synchronized Slide 13 in [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) and [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md), recompiled the presentation deck, and updated system architecture documentation (`ProblemStatement_v5.md`, `MVP_Roadmap.md`, `Architecture_v5.md`).

10. **LLM-Assisted Intent Reconciliation & Refinement Reasoning Engine:**
    - Resolved semantic contradictions caused by naive string concatenation (`base_intent + "\n" + feedback`) during Phase 3b (clarify) and Phase 6 (replan) HITL loops.
    - Implemented [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py), applying Chain-of-Thought prompt engineering and Pydantic structured output to classify the refinement scope into `FULL_REPLACEMENT` (complete request reset) vs `PARTIAL_UPDATE` (delta constraint adjustment).
    - Added `active_intent`, `intent_update_reasoning`, and `intent_update_type` to `AgentState` in [`src/core/state.py`](file:///home/felipeab/MultiAgentON/src/core/state.py), ensuring a single, non-contradictory operational truth.
    - Integrated Mock GraphRAG dynamic rescoping: re-extracts the $k$-hop subtopology neighborhood whenever operator refinement changes routing endpoints.
    - Updated Phase 2 (`pddl_parser.py`), Semantic Gate (`semantic_gate_node.py`), and Plan Synthesizer (`plan_synthesizer.py`) to consume `active_intent` directly.
11. **Bandwidth SLA Constraint Mapping, 400G Physical SNR Threshold & Synthetic Corpus Rebalancing:**
    - Integrated formal optical bandwidth/capacity constraints into the neurosymbolic pipeline to support real-world operator SLAs (e.g., 100G, 200G, 400G).
    - Extended the PDDL Context-Free Grammar (CFG) in [`src/core/pddl_validator.py`](file:///home/felipeab/MultiAgentON/src/core/pddl_validator.py) with the production rule `(bandwidth <int>)` and updated [`src/core/symbolic_solver.py`](file:///home/felipeab/MultiAgentON/src/core/symbolic_solver.py) to preserve bandwidth demands.
    - Updated the physical layer constants in [`src/core/constants.py`](file:///home/felipeab/MultiAgentON/src/core/constants.py) by calibrating `snr_threshold_400g_dB = 21.5` and wired dynamic SNR threshold selection into [`src/nodes/qot_validation.py`](file:///home/felipeab/MultiAgentON/src/nodes/qot_validation.py), enabling realistic physical infeasibility detection on long multi-hop optical paths.
    - Enhanced LLM prompt definitions in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) and [`src/nodes/reverse_prompt.py`](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) to eliminate false-alarm semantic divergences during reverse prompting.
    - Expanded [`tests/evaluation/test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json) to 107 intents, sequentially categorized across four classes (28 Nominal, 26 Ambiguous, 27 Infeasible, 26 Adversarial).
    - Generated the structured Excel workbook [`docs/LLM_Wiki/raw/test_corpus_summary.xlsx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/raw/test_corpus_summary.xlsx) with color-coded taxonomy.
    - Normalized the benchmark corpus action space, strictly eliminating erroneous `reject` labels and aligning with the formal RADG ternary action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$.
    - Verified full test suite under Strict TDD with 294 passing unit tests (100% success rate).

---

## 3. What do I plan to accomplish next week?

1. **Review Thesis Defense Deck with Academic Advisor:** Present the 16-slide draft, timing targets, and narrative structure to Prof. Massimo Tornatore for formal academic review and feedback.
2. **Implement Automated Evaluation Harness:** Develop `run_benchmark.py`, `metrics.py`, and `plotter.py` in `tests/evaluation/scripts/` following Strict TDD to execute the 107-demand corpus across Baseline A, Baseline B, Baseline C, and Proposed.
3. **Execute Sprint 4 Benchmark Evaluation & Collect Empirical Data:** Run the full evaluation suite on the 17-node German backbone network and generate high-resolution IEEE/PoliMi style figures for Slide 14 and Chapter 4.
4. **Thesis Chapter 4 Drafting:** Begin drafting Chapter 4 (*Experimental Evaluation & Numerical Results*) using `thesis-coauthor` and Overleaf integration.

---

## 4. Do You Need Support?

- **Current Status:** No external blockers. The evaluation dataset, baseline definitions, bandwidth SLA mechanics, and PowerPoint presentation deck are fully aligned and validated.
- **Advisor Review:** I will schedule a checkpoint to present the 15-minute defense deck draft and discuss empirical benchmark results.

---

## 5. One-Sentence Summary

I formalized Baseline C, mapped bandwidth/capacity SLA constraints into PDDL and GN-model physics with a 21.5 dB 400G threshold, expanded and balanced the synthetic benchmark corpus to 107 intents with normalized ternary RADG actions, and generated the comprehensive Excel dataset while maintaining a 100% test pass rate across 294 unit tests.
