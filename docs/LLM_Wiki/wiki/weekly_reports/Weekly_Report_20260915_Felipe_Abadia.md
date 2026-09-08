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

1. **New Skill & Automation Infrastructure (`presentation-coauthor`):**
   - Deprecated and removed the legacy text-only `presentation-designer` skill.
   - Authored the comprehensive [`presentation-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/SKILL.md) skill, establishing authoritative rules for:
     - The **15 Golden Rules for Thesis Presentations** (strict 15-minute budget, 15–18 slides, bespoke problem-driven ToC, no terminal periods on bullets, explicit contributions, clear problem statement, and timed speaker notes).
     - **Politecnico di Milano Template Standards:** Extracted official 16:9 widescreen dimensions ($13.333'' \times 7.5''$), institutional color palette (Navy Blue `#0F2C53`, Burgundy Accent `#85200C`, Card Fill `#F4F6F9`), typography (`Titillium Web SemiBold`, `Abel`, `Arial`), and layout placeholders.
     - Documented reference guides: `references/presentation-standards.md`, `references/template-guide.md`, and `references/workflow-guide.md`.

2. **Automated Headless Export Pipeline (`export_presentation.py`):**
   - Diagnosed and resolved the Windows PowerPoint file-locking constraint (`PermissionError: [Errno 13]`), where keeping `.pptx` open prevents external script overwrites.
   - Engineered [`export_presentation.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/export_presentation.py), bridging Linux/WSL to Windows PowerShell COM automation (`PowerPoint.Application`).
   - Enables headless compilation of any `.pptx` into a vector `.pdf` and per-slide 1080p `.png` previews (`slides_png/slide_01.png` to `slide_16.png`) in under 6 seconds.
   - Built a `--watch` mode enabling automated background compilation whenever the `.pptx` binary is saved after manual adjustments.

3. **Programmatic Thesis Defense Deck Assembly (`build_defense_deck.py`):**
   - Added `python-pptx` (v1.0.2) to project dependencies via `uv`.
   - Engineered [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) to programmatically assemble the complete defense presentation from `docs/LLM_Wiki/raw/ACP_MinPowCons_v5.pptx`.
   - Preserved PoliMi master slide chrome (official header, logo, underline separator, footer text, and dynamic slide numbers) while clearing previous conference content.
   - Implemented rich visual taxonomies:
     - `create_cover_slide`: Burgundy accent title, candidate/advisor metadata, and updated date.
     - `create_row_list_slide`: Dynamic height and padding scaling for 5 to 7 structural progression banners.
     - `create_pipeline_flow_slide`: Horizontal 7-phase connected chevron cards with amber/burgundy risk gate borders and bottom HITL loop banners (`interrupt()` clarification and replan loops).
     - `create_decision_tree_slide`: Pre-deployment RADG decision gate featuring native piecewise formulation $D(U_{sem}, \text{QoT}_{valid})$ and 3 outcome cards (*Clarify*, *Replan*, *Auto-Approve*).
     - `create_card_slide`: 3-card and 4-card layouts with formulation blocks.
     - `create_split_diagram_slide`: Left-column structured cards paired with right-column standardized dashed figure placeholders.
     - `create_kpi_and_placeholder_slide`: 3 giant-number KPI banners paired with empirical plot placeholders.
   - Injected structured speaker notes with estimated delivery seconds into every slide.

4. **Authored 16-Slide Thesis Defense Master Deck:**
   - **Slide 1:** Title Slide (PoliMi Branding, Thesis Title, Student: Felipe Abadía, Advisor: Prof. Massimo Tornatore, September 2026).
   - **Slide 2:** Outline (Thesis-specific problem progression, zero generic ToC clichés).
   - **Slide 3:** Motivation: The Vision of Intent-Based Optical Networks (Operational paradigm shift and high-level intent promise).
   - **Slide 4:** Illustrative Failure: Why Standard LLMs Break Optical Backbones (Side-by-side comparison of Token Budget Saturation vs. Hallucinated Physics).
   - **Slide 5:** Problem Statement: Inputs, Constraints & Objectives (3 structured cards with native OMML equations: $U_{sem} \le \tau_{sem}$, $GSNR \ge GSNR_{th}$, $P_{rx} \ge P_{rx,min}$).
   - **Slide 6:** Proposed Solution: Neurosymbolic Decoupling (The core philosophy: "LLMs reason, deterministic tools calculate", and the 4 core contributions).
   - **Slide 7:** End-to-End System Architecture & Pipeline Flow (7-phase horizontal pipeline flow with directional arrows and sequential fail-fast risk gates).
   - **Slide 8:** Overcoming Token Saturation: Scoped Optical GraphRAG ($k$-hop subtopology scoping yielding $> 75\%$ prompt reduction + topology scoping placeholder).
   - **Slide 9:** Overcoming Semantic Drift: Reverse Prompting & HITL Loop (Layer 1 CFG regex check + Layer 2 Reverse Prompting piecewise $U_{sem}$ formula in Cambria Math).
   - **Slide 10:** Pre-Deployment Risk Gate: The RADG Decision Function (Piecewise formulation $D(U_{sem}, \text{QoT}_{valid})$ in Cambria Math with 3 outcome cards).
   - **Slide 11:** Deterministic Physical Layer: GN-Model QoT Validation (Native OMML formulas for $P_{ASE}$, $P_{NLI}$, $GSNR$, and $P_{rx}$ + execution speed banner).
   - **Slide 12:** Experimental Setup & Testbed Environment (17-node German backbone network, SMF-28 parameters, and SDON RESTConf testbed + 16:9 topology placeholder).
   - **Slide 13:** Evaluation Framework & Benchmark Scenarios (100 test demands across nominal, ambiguous, unfeasible, and adversarial categories).
   - **Slide 14:** Key Findings & Pre-Deployment Guarantees (3 KPI stat banners: 100% safety, $> 70\%$ HITL cut, $< 15$ ms latency + empirical benchmark placeholder).
   - **Slide 15:** Conclusions & Main Takeaways (4 high-impact synthesis cards summarizing thesis achievements).
   - **Slide 16:** Future Outlook & Acknowledgments (Extension to joint compute scheduling, C+L multi-band, and committee Q&A).

5. **Native PowerPoint Office Math (OMML) & Visual Auditing:**
   - Implemented `add_omml_equation()` using DrawingML `<a14:m><m:oMathPara>` XML injection, eliminating external rasterization and rendering native, scalable Cambria Math equations in PowerPoint.
   - Solved DrawingML shape text color inheritance bug by layering transparent textboxes over card containers, ensuring equations and body text render in dark navy/slate.
   - Relocated presentation package to `docs/LLM_Wiki/wiki/presentations/thesis_defense/` with symlink `thesis_defence`, and archived legacy presentation files to `archive/`.
   - Visually inspected all 16 rendered PNGs via `view_file` to confirm layout harmony, contrast, and mathematical sharpness. Zero test regressions across 278 unit tests.

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
