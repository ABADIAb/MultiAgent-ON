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
  1. Updated `create_row_list_slide` in [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/presentations/thesis_defense/build_defense_deck.py) to dynamically calculate row height, vertical gap, font sizes, and text frame margins based on the number of rows:
     $$\text{row\_height} = \frac{\text{avail\_height} - (N - 1) \times \text{gap}}{N}$$
  2. For $N > 5$, adjusted banner height to $0.73''$, gap to $0.10''$, margins to $0.06''$, title font to 14 pt, and description font to 12 pt.
  3. Recompiled and visually verified that all 7 pipeline phases render cleanly with uniform padding above the footer.

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

### Pending Issues

> None. The presentation authoring pipeline, automated headless export, visual inspection tooling, and initial 16-slide thesis defense deck are complete, verified, and passing all unit tests.

---

### Additional Notes

The complete presentation artifacts are tracked under:
- Master PowerPoint Deck: [`presentations/thesis_defense/thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/presentations/thesis_defense/thesis_defense.pptx)
- Vector PDF Preview: [`presentations/thesis_defense/thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/presentations/thesis_defense/thesis_defense.pdf)
- High-Resolution Slide Previews: [`presentations/thesis_defense/slides_png/`](file:///home/felipeab/MultiAgentON/presentations/thesis_defense/slides_png/)
- Slide Markdown Specification & Speaker Notes: [`presentations/thesis_defense/deck_spec.md`](file:///home/felipeab/MultiAgentON/presentations/thesis_defense/deck_spec.md)
- Programmatic Python Builder: [`presentations/thesis_defense/build_defense_deck.py`](file:///home/felipeab/MultiAgentON/presentations/thesis_defense/build_defense_deck.py)
