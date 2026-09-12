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
LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

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

#### Solved Issue 7: Reverse-Engineering & Programmatic Synchronization of Manual PowerPoint Visual Refinements

- **Issue:** Manual visual modifications made in Microsoft PowerPoint to reduce text density, improve slide aesthetics, and add co-advisor metadata (Slides 1, 3, 4, and 5) risk being overwritten on subsequent programmatic executions of `build_defense_deck.py`. Furthermore, PowerPoint on Windows encapsulates native DrawingML math shapes inside `<mc:AlternateContent><mc:Choice>`, causing standard `python-pptx` shape iterators (`slide.shapes`) to silently ignore them.
- **What has already been tried:** Executed standard `python-pptx` inspection scripts to extract modified shapes and text. The scripts reported 0 shapes or missing pills on Slide 5 because the `<mc:AlternateContent>` wrapper was ignored by `python-pptx`.
- **Result:** Naive script inspection gave false negative results indicating shapes were deleted, risking divergence between the manual presentation and the authoritative code.
- **Estimated possible solution / Resolution:**
  1. Developed low-level OpenXML inspection scripts using `lxml.etree` with XPath queries targeting `.//p:sp` across all markup compatibility namespaces, successfully extracting exact coordinates, colors, fonts, margins, and equation payloads.
  2. Implemented `create_evolution_sdon_ibon_slide()` in [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) for Slide 3 (Burgundy/Navy comparative containers, 6 white rounded pills, right-arrow connector with `"PARADIGM SHIFT: HOW ➔ WHAT"` badge, and bottom warning banner).
  3. Standardized Slide 4 challenge badge typography to 14 pt, descriptions to 12 pt, and tuned the empirical risk banner.
  4. Refactored Slide 5 into 4 modular white rounded pills ($3.21'' \times 0.43''$) per upper card, resized the lower constraints container to $10.31'' \times 2.13''$, and added native OMML mappings for $T_{prompt} \le T_{max}$ and $\min \alpha N_{hitl} + \beta T_{tokens}$.
  5. Updated [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md) and recompiled `thesis_defense.pptx`, vector `thesis_defense.pdf`, and 1080p `slides_png/` previews, verifying 1:1 visual match with 278 passing tests.

---

#### Solved Issue 8: Naive String Concatenation and Semantic Contradictions in HITL Intent Refinement

- **Issue:** During multi-turn Human-in-the-Loop refinement loops (Phase 3b Semantic Gate clarification and Phase 6 RADG replan), operator feedback was processed via naive string concatenation (`base_intent + "\n" + feedback`). This created semantic contradictions in prompts (e.g. both old and new destinations present in the same prompt string), forcing the downstream PDDL parser to guess constraint precedence, biasing the Semantic Gate agreement judge with conflicting text blocks, and producing oxymoronic updates in the final planning report.
- **What has already been tried:** Monotonic refinement feedback capture (BUG-009) accumulated feedback in `refinement_history` to prevent gate drift, but the reference string remained an ad-hoc concatenation of conflicting turns.
- **Result:** Refinement prompts grew noisy and contradictory; full replacements could not prune superseded constraints; planning reports displayed cluttered trails.
- **Estimated possible solution / Resolution:**
  1. Implemented the LLM-assisted Intent Reconciler in [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py), applying Chain-of-Thought prompt engineering and Pydantic structured output (`RefinedIntentAnalysis`) to classify refinement scope into `FULL_REPLACEMENT` (complete request reset) vs `PARTIAL_UPDATE` (delta constraint adjustment).
  2. Extended `AgentState` with `active_intent`, `intent_update_reasoning`, and `intent_update_type` in [`src/core/state.py`](file:///home/felipeab/MultiAgentON/src/core/state.py), providing a single, non-contradictory operational truth across the pipeline.
  3. Integrated Mock GraphRAG dynamic rescoping: dynamically re-extracts the $k$-hop subtopology neighborhood whenever operator refinement alters routing endpoints.
  4. Updated Phase 2 (`pddl_parser.py`), Semantic Gate (`semantic_gate_node.py`), and Plan Synthesizer (`plan_synthesizer.py`) to consume `active_intent` directly.
  5. Authored dedicated unit tests in `tests/unit/test_intent_reconciler.py` and updated regression tests, achieving a 100% pass rate across 291 unit tests with zero lint errors.

---

#### Solved Issue 9: Erroneous 'Reject' Action in Synthetic Corpus and Mathematical Action Space Divergence

- **Issue:** 24 intents in Class IV (Adversarial) were labeled with `"expected_radg_action": "reject"`, and several edge cases had inconsistent mappings (`intent_adv_26` had `replan` while `intent_amb_26` had `approve`). This directly contradicted the thesis problem statement (ProblemStatement_v5, Section 4.3), which formalizes the RADG action space as strictly ternary: $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$.
- **What has already been tried:** Traced the source code in [`src/core/radg.py`](file:///home/felipeab/MultiAgentON/src/core/radg.py) and [`src/nodes/radg_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/radg_node.py). `evaluate_radg()` evaluates only physical feasibility outcomes and returns strictly `"approve"` or `"replan"`.
- **Result:** Adversarial intents (unknown nodes, topological contradictions, PDDL injection) fail structurally at Layer 1 ($v_{struct}=0$) or diverge semantically at Layer 2 ($U_{sem} > \tau_{sem}$), triggering early fail-fast `clarify` in Phase 3b. They never reach the RADG physical gate as a "reject".
- **Estimated possible solution / Resolution:**
  1. Normalized all 107 intents in [`tests/evaluation/test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json):
     - **Class I (Nominal)**: $U_{sem} \to$ `pass`, RADG $\to$ `approve`, $\text{QoT} \to$ `true`.
     - **Class II (Ambiguous)**: $U_{sem} \to$ `clarify`, RADG $\to$ `clarify`, $\text{QoT} \to$ `null`.
     - **Class III (Infeasible)**: $U_{sem} \to$ `pass`, RADG $\to$ `replan`, $\text{QoT} \to$ `false`.
     - **Class IV (Adversarial)**: $U_{sem} \to$ `clarify`, RADG $\to$ `clarify`, $\text{QoT} \to$ `null`.
  2. Updated the benchmark taxonomy table in [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md) to replace `reject / clarify` with `clarify (Phase 3b HITL / CFG)`.
  3. Regenerated [`docs/LLM_Wiki/raw/test_corpus_summary.xlsx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/raw/test_corpus_summary.xlsx) reflecting the corrected actions.
  4. Verified all 294 unit tests continue to pass with 100% success.

---

### Pending Issues

> None. The presentation authoring pipeline, benchmark corpus, intent reconciliation engine, and full 7-phase neurosymbolic pipeline are complete, verified, and passing all unit tests.

---

### Additional Notes

The complete presentation artifacts are tracked under:
- Master PowerPoint Deck: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx)
- Vector PDF Preview: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf)
- High-Resolution Slide Previews: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/)
- Slide Markdown Specification & Speaker Notes: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md)
- Programmatic Python Builder: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py)

