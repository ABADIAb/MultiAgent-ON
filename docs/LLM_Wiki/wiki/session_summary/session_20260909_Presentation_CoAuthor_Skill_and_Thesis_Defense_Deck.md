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
Under [`docs/LLM_Wiki/wiki/presentations/thesis_defense/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/) (with compatibility symlink `docs/LLM_Wiki/wiki/presentations/thesis_defence`):
- Relocated presentation package from root `presentations/` directly into the wiki hierarchy.
- Archived all 9 legacy presentation markdown notes into [`docs/LLM_Wiki/wiki/presentations/archive/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/archive/).
- Authored and updated [`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md): complete slide-by-slide text, visual layout hints (`> [!LAYOUT]`, `> [!VISUAL]`), concise bullet points without terminal periods, and timed speaker notes.
- Engineered and modernized [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) using `python-pptx` (v1.0.2) to assemble the presentation from the PoliMi template.
- Generated [`thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx) and compiled vector [`thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf) and 16 slide images in [`slides_png/`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/slides_png/).

| # | Slide Title | Visual Layout | Core Topic |
|---|-------------|---------------|------------|
| 1 | Title Slide | Layout 0 (PoliMi Cover) | Title, Candidate, Advisor, September 2026 |
| 2 | Outline | 5 Problem Banners | Thesis-specific challenge progression |
| 3 | Motivation: Intent-Based Optical Networks | 2 Columns | Operational shift & high-level abstraction |
| 4 | Illustrative Failure | 2 Cards (Alert) | Token saturation & hallucinated physics |
| 5 | Problem Statement | 3 Structured Cards + Native OMML | Inputs ($G(V,E)$), Constraints ($U_{sem} \le \tau_{sem}, GSNR, P_{rx}$), Objectives |
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

---

## 3. Verification & Test Outcomes

- **Unit Test Suite:** Executed `uv run pytest`; all 278 unit tests passed cleanly with zero regressions.
- **Visual Auditing:** Inspected rendered slide PNGs (`slide_01.png` through `slide_16.png`) via `view_file` to confirm alignment, contrast, dark Cambria Math font rendering, and layout balance across all 16 slides.
- **CLI Verification:** Successfully verified export and inspection scripts under WSL and Windows COM automation.

---

## 4. Handover & Next Steps

1. **Advisor Feedback:** Share `thesis_defense.pdf` with Prof. Massimo Tornatore to review pacing, visual balance, and content focus.
2. **Sprint 4 Benchmarking:** Execute the 100-demand evaluation suite across the 17-node German backbone to generate empirical figures.
3. **Figure Ingestion:** Inject empirical benchmark plots into Slides 8, 12, 14, and backup slides.
