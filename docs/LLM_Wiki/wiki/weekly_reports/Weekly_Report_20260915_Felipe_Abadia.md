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
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

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

---

## 3. What do I plan to accomplish next week?

1. **Review Thesis Defense Deck with Academic Advisor:** Present the 16-slide draft, timing targets, and narrative structure to Prof. Massimo Tornatore for formal academic review and feedback.
2. **Execute Sprint 4 Benchmark Evaluation:** Run the full 100-demand evaluation suite on the 17-node German backbone network across Baseline A (LLM-only), Baseline B (Rule-based), and Proposed (Neurosymbolic RADG).
3. **Populate Empirical Figures into Slide Deck:** Ingest the empirical benchmark plots (blocking probability, latency distributions, and HITL reduction curves) directly into Slide 14 and backup slides.
4. **Thesis Chapter 4 & 5 Drafting:** Begin drafting Chapter 4 (*Experimental Evaluation & Numerical Results*) using `thesis-coauthor` and Overleaf integration.

---

## 4. Do You Need Support?

- **Current Status:** No external blockers. The PowerPoint co-authoring workflow and export automation are fully operational under WSL and Windows.
- **Advisor Review:** I will schedule a checkpoint to present the 15-minute defense deck draft and collect feedback on slide emphasis and result presentation.

---

## 5. One-Sentence Summary

I created the `presentation-coauthor` skill and headless PowerPoint COM export pipeline, and authored a 16-slide, 15-minute Master's thesis defense deck adhering strictly to Prof. Tornatore's 15 Golden Rules and Politecnico di Milano template aesthetics.
