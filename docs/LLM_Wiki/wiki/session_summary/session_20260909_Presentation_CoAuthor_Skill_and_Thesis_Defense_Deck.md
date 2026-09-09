---
title: "Session 2026-09-09: Presentation Co-Author Skill, Automated Export Pipeline, and Thesis Defense Deck"
date: 2026-09-09
tags: [session-summary, presentation, powerpoint, pptx, presentation-coauthor, defense, polimi]
status: active
---

# Session Summary: Presentation Co-Author Skill & Master's Thesis Defense Deck

---

## 1. Context & Motivation

To prepare for the upcoming Master's thesis defense, an authoritative presentation workflow was established using the official presentation template provided by academic advisor Prof. Massimo Tornatore (`docs/LLM_Wiki/raw/ACP_MinPowCons_v5.pptx`).

The previous setup relied on a primitive markdown skill (`presentation-designer`) that lacked PowerPoint integration, template fidelity, and academic defense rules. Furthermore, manual editing of PowerPoint files presents a severe friction point: Microsoft PowerPoint on Windows places an exclusive lock on open `.pptx` files, preventing external scripts from writing updates and forcing tedious manual file closing/reopening cycles.

In this session, we established a reproducible co-authoring architecture mirroring our [[thesis_drafts/Writing_Roadmap_v1|Draw.io diagram workflow]]: programmatic OpenXML generation via Python, headless compilation via Windows PowerPoint COM to vector PDF and PNG previews, and authored the complete 16-slide thesis defense deck adhering strictly to the professor's 15 Golden Rules.

---

## 2. What was Accomplished?

### 2.1 Creation of the `presentation-coauthor` Skill
- Replaced the deprecated `presentation-designer` skill with the comprehensive **`presentation-coauthor`** skill in [`.agents/skills/presentation-coauthor/`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/SKILL.md).
- Codified **Prof. Tornatore's 15 Golden Rules for Thesis Presentations**:
  1. Strict 15-minute budget (15–18 slides, 1 min/slide).
  2. Bespoke problem-driven Table of Contents (no generic ToC).
  3. Motivation via illustrative failure example.
  4. Structured Problem Statement (Inputs, Constraints, Objectives).
  5. Explicit statement of contributions in methodologies.
  6. Clear evaluation settings, metrics, and benchmark scenarios.
  7. Legible figures with large fonts; key results only.
  8. Clear conclusion slide with main takeaways.
  9. Zero walls of text (4–6 bullets max, 6–10 words per bullet).
  10. Strict English language throughout.
  11. Storytelling animation guidance.
  12. Logical narrative bridges between slides.
  13. Self-explanatory vector plots with explicit units.
  14. Disciplined slide count.
  15. **No terminal periods** (`.`) at the end of bullet points and titles.
- Documented references:
  - [`presentation-standards.md`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/references/presentation-standards.md)
  - [`template-guide.md`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/references/template-guide.md)
  - [`workflow-guide.md`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/references/workflow-guide.md)
- Updated [`.atl/skill-registry.md`](file:///home/felipeab/MultiAgentON/.atl/skill-registry.md).

### 2.2 Headless Windows PowerPoint COM Export Pipeline
- Built [`export_presentation.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/export_presentation.py), which bridges Linux/WSL to Windows PowerShell COM automation (`New-Object -ComObject PowerPoint.Application`).
- Compiles `.pptx` into a vector `.pdf` and per-slide 1080p `.png` files (`slides_png/`) headlessly in $\approx 5.8$ seconds.
- Solves the file-locking issue: the operator can keep the PDF or PNGs open in any reader without locking the master `.pptx`.
- Supports a `--watch` mode that monitors `.pptx` modification times and automatically re-exports previews upon saving manual edits.

### 2.3 Master's Thesis Defense Presentation Deck (16 Slides)
Under [`docs/LLM_Wiki/wiki/presentations/thesis_defense/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/):
- Relocated presentation package from root `presentations/` directly into the wiki hierarchy.
- Archived all 9 legacy presentation markdown notes into [`docs/LLM_Wiki/wiki/presentations/archive/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/archive/).
- Authored and updated [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md): complete slide-by-slide text, visual layout hints (`> [!LAYOUT]`, `> [!VISUAL]`), concise bullet points without terminal periods, and timed speaker notes.
- Engineered and modernized [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) using `python-pptx` (v1.0.2) to assemble the presentation from the PoliMi template.
- Generated [`thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx) and compiled vector [`thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf) and 16 slide images in [`slides_png/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/).

| # | Slide Title | Visual Layout | Core Topic |
|---|-------------|---------------|------------|
| 1 | Title Slide | Layout 0 (PoliMi Cover) | Title, Candidate, Advisor, September 2026 |
| 2 | Outline | 5 Problem Banners | Thesis-specific challenge progression |
| 3 | Motivation: Intent-Based Optical Networks | 2 Columns + Callouts | Operational shift & high-level abstraction |
| 4 | Illustrative Failure Modes | 5 Horizontal Cards + Alert Banner | 5 formal failure modes from [[thesis_drafts/3_SystemModel/3_1_Formal_Problem_Definition\|Section 3.1.1]] |
| 5 | Problem Statement: Inputs, Constraints & Objectives | 2x2 Quadrant Matrix | Given, Decide, Objective, Constraints (Resource vs Physical/Semantic Boundary) |
| 6 | Proposed Solution | 2 Columns + Contribution Banner | "LLMs reason, tools calculate" & 4 contributions |
| 7 | End-to-End System Architecture | 7 Horizontal Chevrons + Loop Banners | Complete 7-phase pipeline flow with risk gates |
| 8 | Overcoming Token Saturation | Split Diagram + Figure Placeholder | Scoped GraphRAG ($k$-hop subtopology extraction, $>75\%$ cut) |
| 9 | Overcoming Semantic Drift | 2 Cards + Native OMML | Layer 1 CFG + Layer 2 Reverse Prompting piecewise $U_{sem}$ formula |
| 10 | Pre-Deployment Risk Gate | Decision Tree + Native OMML | Piecewise RADG formula $D(U_{sem}, \text{QoT}_{valid})$ + 3 outcome cards |
| 11 | Deterministic Physical Layer | 2 Cards + Native OMML | Analytical GN-model formulas ($P_{ASE}, P_{NLI}, GSNR, P_{rx}$) in Cambria Math |
| 12 | Experimental Setup & Testbed | Split Benchmark + Figure Placeholder | 17-node German network, SMF-28 parameters, and SDON RESTConf testbed |
| 13 | Evaluation Framework & Scenarios | 3 Cards | 100 test demands across 4 intent categories |
| 14 | Key Findings & Guarantees | 3 KPI Stat Banners + Plot Placeholder | 100% pre-deployment safety, $>70\%$ HITL cut, $<15$ ms latency |
| 15 | Conclusions & Main Takeaways | 4 Synthesis Cards | Core architectural and operational takeaways |
| 16 | Future Outlook & Acknowledgments | 2 Columns (Outlook & PoliMi Thanks) | Joint compute scheduling, C+L multi-band, and committee Q&A |

### 2.4 Visual Quality Auditing, OMML Math & Bugfixes
- **Native Office Math (OMML) in DrawingML:** Developed `add_omml_equation()` using `parse_xml()` to inject `<a14:m><m:oMathPara><m:oMath>...</m:oMath></m:oMathPara></a14:m>`, rendering native editable Cambria Math for subscripts, superscripts, fractions, and piecewise equations with curly braces.
- **DrawingML Shape Text Color Bug:** Fixed a template inheritance issue where rounded rectangles defaulted to white text, making math formulas invisible on `#F4F6F9` fill. Layered transparent textboxes over container shapes so DrawingML math and text render in bold institutional navy and dark slate.
- **Emoji Glyphs Fallback:** Replaced national flag emoji `🇩🇪` with `🌐` to avoid raw text `DE` fallback on Windows systems.
- Authored [`inspect_deck.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/inspect_deck.py) for terminal-based slide inspection.
- Fixed Cover Slide conference logo collision and updated date banner.

### 2.5 Slide 3–4 Refinements & Failure Modes Mapping
- **Symlink Cleanup:** Removed legacy Linux symlink `docs/LLM_Wiki/wiki/presentations/thesis_defence` that caused confusing duplicate folder entries in IDEs and a 1KB stub in Windows/WSL Explorer, standardizing entirely on `thesis_defense/`.
- **Slide 3 (Motivation) Callouts:** Extracted `🎯 Goal` and `⚠️ Critical Challenge` from standard bullet lists into dedicated, high-contrast callout blocks at the base of each column. Clarified the physical rationale for why optical backbones cannot tolerate probabilistic errors: hard forward error correction (FEC) cliff-edge behavior (BER explodes if GSNR drops 0.3–0.5 dB below threshold, causing transponder DSP carrier loss and total link blackout), multi-terabit blast radius, and Kerr nonlinearities (XPM/FWM) in shared EDFAs. Refined the natural language intent example to a realistic carrier operation: `"Establish a 400G lightpath between Milan and Rome avoiding link L2"`.
- **Slide 4 (Illustrative Failure Modes):** Overhauled layout from 2 cards into 5 distinct horizontal cards via `create_five_challenges_slide()`, mapping 1-to-1 to the 5 formal failure modes in [[thesis_drafts/3_SystemModel/3_1_Formal_Problem_Definition#311-failure-modes-of-pure-llm-orchestration|Section 3.1.1]]:
  1. Token Budget Saturation (LLM context exhausted by raw JSON/YANG topology snapshots).
  2. Hallucinated Physical Constraints (LLM invents non-existent fiber paths or miscalculates nonlinear interference).
  3. Semantic Drift (Operator intent distorted during natural-to-formal translation).
  4. Reactive Post-Deployment Latency (Discovering infeasibility at provisioning triggers multi-minute replanning).
  5. Suboptimal HITL Friction (Frequent operator interrupts cause operational fatigue).
  Moved detailed explanatory lists to speaker notes to maintain clean, punchy slide density, and updated the bottom empirical risk banner.

### 2.6 Slide 5 & 6 Structural Overhaul: 2-Tier Problem Formulation & Neurosymbolic Synergies
- **Slide 5 Restructuring (2-Tier Split):**
  - Evolved the problem formulation layout from a 2x2 quadrant into a clean 2-tier horizontal split via `create_problem_statement_slide()`.
  - **Upper half (3 columns):** Given ($G(V, E, W)$, $d = (s, t, b)$, $\Omega$), Decide ($P_{sd} \subseteq \Pi$, $\Lambda_p \subseteq W$), and Objective ($\min \sum \text{cost}$ / load friction).
  - **Lower half (2 columns):** Constraints spanning the full bottom half, separated into Resource Constraints ($T_{prompt} \le 8192$, $t_{exec} \le 5\text{ s}$, $K\text{-SP}$) on the left and Physical & Semantic Boundary Constraints ($U_{sem} \le \tau_{sem}$, $\text{SNIR}(p) \ge \gamma_{th}$, EDFA saturation) on the right.
  - **Mathematical Formula Typography:** Developed `render_math_to_runs()` and `render_math_expression()` with native DrawingML subscript (`baseline: -25000`) and superscript formatting in Cambria Math, eliminating plain-text variable artifacts.
- **Slide 6 Restructuring (Neurosymbolic Decoupling & Contribution Protagonism):**
  - Synthesized the conceptual foundation between Section 3.2.1 of [[thesis_drafts/3_SystemModel/3_2_Conceptual_Framework|Chapter 3 Section 3.2]] (Fail-Fast Pre-Deployment Hierarchy, early semantic vs. late optical physical gate) and Section 3.3.1 of [[thesis_drafts/3_SystemModel/3_3_Strict_Neurosymbolic_Separation|Chapter 3 Section 3.3]] ("LLMs Reason, Tools Calculate", linguistic compilation vs. deterministic symbolic/physics solvers).
  - **Upper half (Decoupled Subsystems):**
    - **Neural Subsystem (Semantic Domain):** Intent compilation to PDDL AST, Scoped GraphRAG $k$-hop subtopology, and early semantic gate ($U_{sem} \le \tau_{sem}$).
    - **Symbolic Subsystem (Optical Domain):** Deterministic Yen's KSP path search, GN-model physical layer feasibility ($P_{ase} + P_{nli}$), and late optical physical gate ($U_{opt} \le \tau_{opt}$).
  - **Lower half (Core Contributions Protagonism):** Restructured into 3 highlighted, prominent visual cards:
    1. *Strict Neurosymbolic Compilation* (linguistic compilation decoupled from physical computation).
    2. *Scoped Optical GraphRAG* (subtopology pruning preventing context exhaustion).
    3. *Fail-Fast Risk Gates (RADG)* (hierarchical gating eliminating hallucination risk prior to deployment).
  - **LangGraph Demotion:** Removed LangGraph Orchestrator from core thesis contributions, documenting it as an implementation framework / runtime vehicle in speaker notes.
  - **Visual Density & Speaker Notes:** Minimized slide text (Golden Rules 9 & 15, zero terminal periods) and expanded complete defense narrative into 60-second structured speaker notes in [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md).

### 2.7 Consistency Audit & Ellipsoid Scope Pivot
- Conducted a deep consistency verification between the presentation deck, the `src/` codebase, and the Chapter 3 System Model thesis drafts.
- **k-hop vs. Ellipsoid Subtopology:** Explored the theoretical risk of connectivity loss in static $k$-hop neighborhoods on highly elongated optical topologies. Proposed a dynamic "ellipsoid" path extraction strategy as a solution.
- **Fidelity Enforcement:** Since the `src/core/mock_graphrag.py` implementation currently relies strictly on $k$-hop subgraphs, reversed an overzealous update that prematurely documented the "ellipsoid" approach as active.
- Documented the ellipsoid approach as a robust future direction in [`Drafting_Backlog.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/Drafting_Backlog.md) and added explanatory footnotes in the thesis drafts acknowledging the current $k$-hop limitation.

---

## 3. Verification & Test Outcomes

- **Unit Test Suite:** Executed `uv run pytest`; all 278 unit tests passed cleanly with zero regressions.
- **Visual Auditing:** Inspected rendered slide PNGs (`slide_01.png` through `slide_16.png`, with specific re-inspection of `slide_03.png`, `slide_04.png`, `slide_05.png`, and `slide_06.png`) via `view_file` to confirm alignment, contrast, dark Cambria Math font rendering, and layout balance across all 16 slides.
- **CLI Verification:** Successfully verified export and inspection scripts under WSL and Windows COM automation.

---

## 4. Handover & Next Steps

1. **Advisor Feedback:** Share `thesis_defense.pdf` with Prof. Massimo Tornatore to review pacing, visual balance, and content focus.
2. **Sprint 4 Benchmarking:** Execute the 100-demand evaluation suite across the 17-node German backbone to generate empirical figures.
3. **Figure Ingestion:** Inject empirical benchmark plots into Slides 8, 12, 14, and backup slides.
