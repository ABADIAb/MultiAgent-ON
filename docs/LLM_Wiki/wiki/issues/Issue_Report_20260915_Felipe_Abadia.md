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

#### Solved Issue 10: Residual 'Reject' Action in Baseline Implementations and Publication Plotting

- **Issue:** Despite normalizing the test corpus to the strictly ternary RADG action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$, residual `"reject"` references remained embedded in baseline implementations (`llm_only.py`, `always_off_hitl.py`, `traditional_sdon.py`), schema definitions (`base.py`), node logic (`radg_node.py`), and publication plotting scripts (`plotter.py`). As a consequence, the generated `gate_decision_distribution` figure incorrectly displayed a Burgundy bar for an obsolete "reject" action category.
- **What has already been tried:** The test corpus was normalized in Issue 9, but downstream baseline fallbacks (e.g. JSON parse errors in LLM-Only, solver path starvation in Traditional SDON) still returned `"reject"`.
- **Result:** Visual inconsistency in generated thesis figures and schema type pollution across baseline modules.
- **Estimated possible solution / Resolution:**
  1. Updated [`tests/evaluation/baselines/base.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/base.py) to define `action: Literal["approve", "clarify", "replan"]`.
  2. Replaced all fallback and error actions in [`llm_only.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/llm_only.py), [`always_off_hitl.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/always_off_hitl.py), and [`traditional_sdon.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/baselines/traditional_sdon.py) with `"replan"`.
  3. Cleaned legacy `"reject"` branch handling from [`src/nodes/radg_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/radg_node.py).
  4. Purged `"reject"` from [`tests/evaluation/scripts/plotter.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/plotter.py), removing the Burgundy color mapping and plot entry.
  5. Updated unit test assertions in [`tests/unit/test_baselines.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_baselines.py) to assert `'replan'`.

---

#### Solved Issue 11: Phase 6 HITL Interruption Origin Misattribution for Autonomous Baselines (A & C)

- **Issue:** In the publication figure `hitl_interruption_origin.pdf` and `.png`, both Baseline A (LLM-Only) and Baseline C (Always-Off HITL) erroneously displayed Phase 6 HITL interruptions for Class III infeasible intents. Because both baselines are architecturally defined as fully autonomous ($N_{hitl} = 0$), displaying human interruptions distorted comparative evaluation.
- **What has already been tried:** Verified baseline runtime telemetry. Both baselines returned `hitl_interrupts = 0` correctly in their `BaselineResult` payloads.
- **Result:** The plotting metrics aggregation in `metrics.py` misattributed baseline replans as human interventions.
- **Estimated possible solution / Resolution:**
  1. Traced the issue to `compute_radg_metrics()` in [`tests/evaluation/scripts/metrics.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/metrics.py), which unconditionally incremented `physical_replans += 1` whenever `actual_action == "replan"`, regardless of whether a human interruption was triggered.
  2. Wrapped `semantic_clarifies` and `physical_replans` tallies inside an explicit `if interrupts > 0:` guard.
  3. Recomputed benchmark metrics and recompiled `hitl_interruption_origin.pdf`, confirming that Baselines A and C strictly report $0$ HITL interruptions.

---

#### Solved Issue 12: High Token Consumption and Quota Exhaustion During Live LLM API Benchmarking

- **Issue:** Executing the full 107-intent synthetic benchmark corpus across multiple LLM-driven baselines rapidly exhausts live LLM API token and request rate quotas (such as Moonshot/Kimi API limits), blocking complete live evaluation passes.
- **What has already been tried:** Executing full passes with `--live` led to rate-limit interruption mid-benchmark.
- **Result:** Benchmark runs were interrupted before collecting full multi-baseline telemetry.
- **Estimated possible solution / Resolution:**
  1. Engineered [`tests/evaluation/test_corpus_compact.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus_compact.json), selecting 20 highly representative demands (5 per risk class: Nominal, Ambiguous, Infeasible, Adversarial).
  2. Configured [`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py) to default to `test_corpus_compact.json`, reducing live API token consumption by $>80\%$ while maintaining full mathematical validity and coverage across all 4 validation pillars.
  3. Retained the full 107-demand corpus (`test_corpus.json`) for final offline mock benchmarks and full-scale runs once production quotas reset.

---

#### Solved Issue 13: Local Reasoning Model Thinking Tokens Disrupting Pydantic Parsing and PDDL CFG Validation

- **Issue:** Newly integrated local Ollama models with native reasoning capabilities (`qwen3.5:4b` and `gemma4:e4b`) output internal monologues wrapped in `<think>...</think>` tags prior to generating final responses. This corrupted structured JSON output in `OllamaChatOpenAI.with_structured_output` (causing `IntentSummary` validation crashes) and contaminated PDDL translations, causing deterministic CFG AST validation to fail ($v_{struct}=0$) and falsely triggering Semantic Gate rejections.
- **What has already been tried:** Tested standard Ollama completions with tight token budgets (e.g. 50-100 tokens), which resulted in empty responses because reasoning tokens consumed the entire completion budget.
- **Result:** Reasoning models could not reliably produce valid PDDL or parse structured operator intent without errors or truncations.
- **Estimated possible solution / Resolution:**
  1. Updated `OllamaChatOpenAI._parse_pydantic` in [`src/core/llm.py`](file:///home/felipeab/MultiAgentON/src/core/llm.py) to strip `<think>.*?</think>` tags using `re.sub(..., flags=re.DOTALL)` before extracting the outermost JSON payload.
  2. Enhanced `_strip_code_fences` in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) to remove `<think>` tags before extracting PDDL code fences, ensuring clean AST parsing.
  3. Tuned `create_ollama_llm` to automatically allocate a 3000-token ceiling for thinking models to prevent token starvation.
  4. Conducted empirical hardware profiling proving that `qwen2.5:3b` remains the optimal default (100% in 4GB VRAM, ~1.5s latency, zero RAM swapping) on the deployment laptop, while supporting `qwen3.5:4b` and `gemma4:e4b` as fully functional, selectable engines.
  5. Expanded [`tests/integration/test_ollama_configurations.py`](file:///home/felipeab/MultiAgentON/tests/integration/test_ollama_configurations.py) with automated post-test memory unloading (`_unload_model`), maintaining 347 passing unit tests under Strict TDD.

---

#### Solved Issue 14: Local Multi-Model Expansion and Latency Offload Characterization (`phi4-mini:latest` & `qwen3:4b`)

- **Issue:** Expanding the local Ollama LLM provider to support newly downloaded models (`phi4-mini:latest` 3.8B and `qwen3:4b` 4.0B) required verifying parameter budgeting, JSON schema compliance, and memory allocation constraints on local laptop hardware (RTX 3050 Laptop GPU with 4 GB VRAM).
- **What has already been tried:** Tested `qwen3:4b` under tight request timeouts (120s) with 3000-token completion limits and concurrent process execution.
- **Result:** Reasoning models exceeding VRAM capacity trigger memory bandwidth bottlenecks and timeouts due to hybrid CPU/system RAM offloading (~3-4 tok/s vs 70 tok/s in VRAM). Conversely, `phi4-mini:latest` executes with direct output (~12.8s) but has higher VRAM footprint (~2.8 GB) than `qwen2.5:3b`.
- **Estimated possible solution / Resolution:**
  1. Updated `SUPPORTED_OLLAMA_MODELS` and `create_ollama_llm()` in [`src/core/llm.py`](file:///home/felipeab/MultiAgentON/src/core/llm.py) with dynamic token ceilings (3000 tokens for reasoning models, 2000 for standard models).
  2. Integrated both models into [`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py) and [`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py).
  3. Empirically confirmed `qwen2.5:3b` as the optimal default (100% in VRAM, ~1.5s latency), with `phi4-mini:latest` serving as the best direct non-reasoning alternative.
  4. Successfully verified `phi4-mini:latest` live end-to-end through all 7 neurosymbolic pipeline phases, including interactive HITL clarify, RADG replanning, and GN-model physics feasibility verification.
  5. Expanded [`tests/integration/test_ollama_configurations.py`](file:///home/felipeab/MultiAgentON/tests/integration/test_ollama_configurations.py) with automated post-test unloading (`keep_alive=0`) to ensure system RAM is immediately reclaimed.

---

### Pending Issues

> None. The presentation authoring pipeline, benchmark corpus, intent reconciliation engine, multi-provider local LLM infrastructure, and full 7-phase neurosymbolic pipeline are complete, verified, and passing all unit tests.

---

### Additional Notes

The complete presentation artifacts are tracked under:
- Master PowerPoint Deck: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx)
- Vector PDF Preview: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf)
- High-Resolution Slide Previews: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/)
- Slide Markdown Specification & Speaker Notes: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md)
- Programmatic Python Builder: [`docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py)

