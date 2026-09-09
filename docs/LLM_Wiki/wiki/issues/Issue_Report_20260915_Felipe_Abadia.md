---
title: "Issue Report 2026-09-15"
date: 2026-09-15
tags: [issues, presentation, pptx, powerpoint, file-locking, com-automation, overflow, layout]
status: active
---

# Issue Report

---

## Student Name:
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Current Stage:
> Thesis Defense Preparation & Presentation Tooling Infrastructure

## Date:
2026-09-15

---

### Solved Issues

#### Solved Issue 1: Windows PowerPoint File-Locking During Programmatic Iteration

- **Issue:** When developing and refining PowerPoint presentations (`.pptx`) using programmatic scripts (`python-pptx`), keeping the presentation open in Microsoft PowerPoint on Windows locks the file exclusively. Any script attempting to overwrite or update the file crashes with `PermissionError: [Errno 13] Permission denied`, preventing a smooth iterative editing cycle.
- **What has already been tried:** Investigated Linux-native headless converters (LibreOffice, unoconv), but LibreOffice was not installed in the WSL environment and third-party python converters degrade complex OpenXML shapes and theme layouts.
- **Result:** Programmatic slide generation required repeatedly opening, saving, closing, and reopening PowerPoint by hand.
- **Estimated possible solution / Resolution:**
  1. Leveraged the WSL-Windows bridge to access Windows PowerShell COM automation directly from Python:
     ```powershell
     $ppt = New-Object -ComObject PowerPoint.Application
     $pres = $ppt.Presentations.Open(...)
     $pres.SaveAs($outPdf, 32) # Export to vector PDF
     $pres.Slides.Item($i).Export($slidePng, "PNG", 1920, 1080) # Export 1080p slide PNGs
     ```
  2. Encapsulated this logic in [`export_presentation.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/export_presentation.py), compiling `<deck>.pdf` and `slides_png/slide_*.png` headlessly in under 6 seconds.
  3. The PDF and PNG files can remain permanently open in PDF viewers (Edge, SumatraPDF, VS Code) without locking the `.pptx` binary.
  4. Added a `--watch` mode to monitor `.pptx` file modification timestamps and auto-trigger export upon save.

---

#### Solved Issue 2: Slide Canvas Overflow on Multi-Stage Pipeline Banners

- **Issue:** When generating Slide 7 (*End-to-End System Architecture & Pipeline Flow*) with 7 horizontal banner rows, fixed banner heights (`0.95''`) and margins caused the bottom rows (Phase 6 RADG and Phase 7 Plan Synthesizer) to overflow past the bottom slide margin, clipping into the PoliMi footer chrome and slide number.
- **What has already been tried:** Inspected the rendered `slides_png/slide_07.png` using visual audit tooling. Confirmed visual truncation of text runs and footer collision.
- **Result:** Slide 7 was illegible and failed academic presentation standards.
- **Estimated possible solution / Resolution:**
  1. Updated `create_row_list_slide` in [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) to dynamically calculate row height, vertical gap, font sizes, and text frame margins based on the number of rows:
     $$\text{row\_height} = \frac{\text{avail\_height} - (N - 1) \times \text{gap}}{N}$$
  2. For $N > 5$, adjusted banner height to $0.73''$, gap to $0.10''$, margins to $0.06''$, title font to 14 pt, and description font to 12 pt.
  3. Subsequently evolved Slide 7 into a horizontal 7-phase chevron pipeline (`create_pipeline_flow_slide`), providing ample horizontal space for directional chevrons and bottom HITL loop callout banners.

---

#### Solved Issue 3: Obsolete Presentation Skill Lacking PowerPoint & Template Support

- **Issue:** The existing `presentation-designer` skill in `.agents/skills/` was a primitive text-only formatting template intended for generic markdown slide decks, with zero support for PowerPoint binaries, institutional templates, or presentation rules.
- **What has already been tried:** Evaluated replacing or extending `presentation-designer`.
- **Result:** The old skill lacked academic rigor, slide budgeting rules, and script automation.
- **Estimated possible solution / Resolution:**
  1. Deprecated and deleted `.agents/skills/presentation-designer/`.
  2. Authored the comprehensive [`presentation-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/SKILL.md) skill with dedicated reference documentation (`presentation-standards.md`, `template-guide.md`, `workflow-guide.md`).
  3. Codified Prof. Massimo Tornatore's 15 Golden Rules for Master's thesis presentations into hard constraints.
  4. Updated `.atl/skill-registry.md` to register `presentation-coauthor`.

---

#### Solved Issue 4: DrawingML Shape Text Inversion on Light Fill Containers

- **Issue:** In the official PoliMi template, shapes created with `s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE)` default to white text (`#FFFFFF`) from master layout styles. When paragraphs or native OMML math equations were added directly to `card.text_frame` on light card containers (`#F4F6F9`), the equations and bullets rendered as invisible white-on-white text (affecting Slides 9, 10, and 11).
- **What has already been tried:** Checked run font properties inside DrawingML equations; DrawingML equation runs inherit shape text properties rather than slide theme defaults.
- **Result:** Piecewise $U_{sem}$, RADG decision function $D$, and analytical GN-model formulas ($P_{ASE}, P_{NLI}, GSNR, P_{rx}$) were washed out and invisible against light backgrounds.
- **Estimated possible solution / Resolution:**
  1. Decoupled visual background containers from text frames: left the rounded rectangle purely as a styled background card.
  2. Layered a transparent `slide.shapes.add_textbox(...)` on top of each card container.
  3. Because textboxes default to dark font colors, both regular text runs and native OMML math formulas automatically render in bold institutional navy and dark slate.
  4. Verified across high-resolution PNG previews (`slide_09.png`, `slide_10.png`, `slide_11.png`).

---

#### Solved Issue 5: Text-Heavy Slide Walls Lacking Visual Support and Mathematical Rigor

- **Issue:** The initial slide deck relied heavily on standard bullet points without diagrams, process chevrons, decision trees, or formal mathematical formulations, failing Prof. Massimo Tornatore's strict presentation standard requiring $\ge 50\%$ visual surface per slide.
- **What has already been tried:** External diagram tools require manual re-export and rasterization, degrading math typography into low-resolution bitmap images.
- **Result:** Slides lacked visual dynamism and failed to showcase the mathematical rigor of the thesis.
- **Estimated possible solution / Resolution:**
  1. Implemented `add_omml_equation()` using native DrawingML `<a14:m><m:oMathPara><m:oMath>...</m:oMath></m:oMathPara></a14:m>` XML injection, producing native, scalable, editable Cambria Math equations for Slides 5, 9, 10, and 11.
  2. Built modular visual layouts in `build_defense_deck.py`:
     - Horizontal 7-phase connected chevron flow with directional chevrons and HITL loop banners (Slide 7).
     - Split comparative cards with standardized dashed figure placeholders (Slides 8, 12).
     - Decision tree slide with piecewise formulation and 3 outcome cards (Slide 10).
     - 3 giant-number KPI stat banners paired with empirical plot placeholders (Slide 14).
  3. Replaced Windows fallback emoji `🇩🇪` on Slide 12 with universal icon `🌐`.
  4. Recompiled and verified that all slides have $\ge 50\%$ visual surface and zero terminal periods.

---

#### Solved Issue 6: Iterative Presentation Layout Optimization & Subsystem Architecture Alignment

- **Issue:** Aligning the presentation's conceptual structure and visual layout with Chapter 3 system model formalisms while adhering to the 15 Golden Rules (such as eliminating text walls, enforcing formal problem formulation sequences, and representing multi-level subsystem architectures without visual clutter). Additionally, redundant filesystem symlinks caused duplicate folder entries in IDEs across WSL.
- **What has already been tried:** Initial presentation iterations relied on standard text-heavy bullet cards and generic column structures that lacked visual hierarchy, failed to emphasize mathematical formulation sequences, and obscured the core architectural separation.
- **Result:** Visual density was suboptimal, mathematical variables were unformatted, and architectural contributions were overshadowed by implementation frameworks.
- **Estimated possible solution / Resolution:**
  1. Developed modular layout primitives in [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) (horizontal failure mode banners, 2-tier problem formulation matrices, decoupled subsystem cards, and highlighted core contribution blocks).
  2. Integrated native DrawingML subscript and superscript formatting for rigorous formula presentation.
  3. Cleaned up redundant Linux symlinks, standardizing the presentation repository structure under `docs/LLM_Wiki/wiki/presentations/thesis_defense/`.
  4. Recompiled the presentation headlessly, inspected high-resolution PNGs, and verified that all 278 unit tests pass without regressions.

---

### Pending Issues

> None. The presentation authoring pipeline, automated headless export, visual inspection tooling, and refined 16-slide thesis defense deck are complete, verified, and passing all unit tests.

---

### Additional Notes

The complete presentation artifacts are tracked under:
- Master PowerPoint Deck: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx)
- Vector PDF Preview: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf)
- High-Resolution Slide Previews: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/)
- Slide Markdown Specification & Speaker Notes: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md)
- Programmatic Python Builder: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py)

