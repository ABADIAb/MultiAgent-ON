---
title: "Session 2026-09-10: Thesis Title Modernization & Defense Deck Alignment"
date: 2026-09-10
tags: [session-summary, thesis-title, neurosymbolic, presentation, defense, llm-assisted]
status: active
---

# Session Summary: Thesis Title Modernization & Defense Deck Alignment

---

## 1. Context & Motivation

In this session, the user evaluated options for updating the thesis title to explicitly reflect the presence and role of Artificial Intelligence (considering terms like "Multiagent System" vs. "LLM").

As Senior Architect, I provided technical guidance on the terminology tradeoffs:
- **"Multiagent System" (MAS):** Strongly discouraged. In the V5 scope pivot ([[Scope_Pivot_20260706]]), the system deliberately moved away from an autonomous agent swarm to a deterministic, fail-fast **Neurosymbolic Pipeline** in LangGraph ("LLMs reason, tools calculate"). Promising a MAS would expose the candidate to critical defense questions regarding distributed game-theoretic negotiations or consensus protocols that are not implemented in the codebase.
- **"LLM-Assisted Neurosymbolic":** Selected as the optimal, rigorous choice. It explicitly highlights the large language model as a linguistic translator without overpromising an unneeded swarm architecture, while preserving the formal depth of the pre-deployment risk gates.

The user approved updating the official thesis title to:
> **LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment**

Furthermore, the user consulted the two-way synchronization workflow of the [`presentation-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/SKILL.md) skill when making manual modifications in Microsoft PowerPoint.

---

## 2. What was Accomplished?

### 2.1 E2E Thesis Title Modernization Across Ecosystem
The title was updated across all active project artifacts while strictly preserving the integrity of historical weekly reports:
1. **Agent Rules & Mission:** Updated [`.agents/rules/AGENTS.md`](file:///home/felipeab/MultiAgentON/.agents/rules/AGENTS.md) (replacing legacy working title).
2. **Project Context Metadata:** Updated [`openspec/config.yaml`](file:///home/felipeab/MultiAgentON/openspec/config.yaml).
3. **Core Architecture Documents:**
   - [`docs/LLM_Wiki/wiki/architecture/ProblemStatement_v5.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/architecture/ProblemStatement_v5.md): Updated title, formal thesis title line, and Section 7 optimization objective.
   - [`docs/LLM_Wiki/wiki/architecture/Architecture_v5.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/architecture/Architecture_v5.md): Updated title and executive summary.
   - [`docs/LLM_Wiki/index.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/index.md): Synchronized active architecture catalog entries.
4. **Thesis Drafting Roadmap:**
   - [`docs/LLM_Wiki/wiki/thesis_drafts/Writing_Roadmap_v1.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/Writing_Roadmap_v1.md): Master thesis writing roadmap title and formal target.
   - [`docs/LLM_Wiki/wiki/thesis_drafts/Thesis_Outline_v4.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/Thesis_Outline_v4.md): Section 3.2 conceptual framework description.
5. **Presentation Deck & Automation:**
   - [`docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md): Slide 1 title, subtitle, and spoken introduction script.
   - [`docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py): Title formatting on Slide 1 (scaled to 32pt to ensure balanced two-line layout without line breaks) and speaker notes.
6. **Active Reports:**
   - [`docs/LLM_Wiki/wiki/weekly_reports/Weekly_Report_20260915_Felipe_Abadia.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/weekly_reports/Weekly_Report_20260915_Felipe_Abadia.md): Updated Project Title and logged title modernization in Section 2. Older weekly reports were preserved untouched to maintain historical fidelity.
   - [`docs/LLM_Wiki/wiki/issues/Issue_Report_20260915_Felipe_Abadia.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/issues/Issue_Report_20260915_Felipe_Abadia.md): Synchronized Project Title.
7. **Application Codebase (`src/`):**
   - [`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py): Module docstring, CLI banner text, and argparse description.
   - [`src/core/graph.py`](file:///home/felipeab/MultiAgentON/src/core/graph.py): StateGraph module and builder docstrings.
   - [`src/core/state.py`](file:///home/felipeab/MultiAgentON/src/core/state.py): State schema module and `AgentState` docstrings.

### 2.2 PowerPoint Deck Re-Compilation & Vector Export
- Re-executed [`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py) to compile the master presentation binary:
  - Output: [`thesis_defense.pptx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx) (16 slides).
- Re-executed [`export_presentation.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/export_presentation.py) via Windows PowerShell COM automation:
  - Generated vector PDF preview: [`thesis_defense.pdf`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pdf).
  - Re-rendered all 1080p slide preview images in `slides_png/` (`slide_01.png` to `slide_16.png`).
  - Verified that Slide 1 displays the updated title with pristine typography and zero clipping.

### 2.3 Presentation Co-Authoring Protocol Clarification
Codified the explicit answer regarding manual `.pptx` edits:
- The AI can inspect manual edits using `inspect_deck.py` and visual PNG previews.
- Since `python-pptx` does not support automatic bidirectional decompilation, the protocol requires the AI to migrate verified manual adjustments back into `build_defense_deck.py` and `deck_spec.md`, preserving the code as the authoritative source of truth.

### 2.4 Manual PowerPoint Visual Enhancement & Two-Way Code Synchronization
Following the user's manual design refinements in PowerPoint to reduce text density and elevate visual hierarchy:
1. **Low-Level XML Reverse-Engineering:**
   - Identified that PowerPoint on Windows encapsulates native DrawingML math equations inside `<mc:AlternateContent><mc:Choice>`, causing high-level `slide.shapes` iterators to overlook them.
   - Built low-level `lxml.etree` extraction scripts querying `.//p:sp` across all DrawingML namespaces, extracting exact coordinates, colors, font sizes, margins, and equation payloads.
2. **Programmatic Generator Updates ([`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py)):**
   - **Slide 1:** Updated advisor metadata to include co-advisor Prof. Qiaolun Zhang (`"Academic Advisor: Prof. Massimo Tornatore & Prof. Qiaolun Zhang"`).
   - **Slide 3:** Added `create_evolution_sdon_ibon_slide()` implementing the paradigm-shift comparison (Burgundy Imperative SDON card vs. Navy Declarative IBON card, central right-arrow connector with `"PARADIGM SHIFT: HOW ➔ WHAT"` badge, 6 modular white rounded pills, and bottom warning banner).
   - **Slide 4:** Standardized challenge badge typography to 14 pt, descriptions to 12 pt, and tuned the empirical risk banner text.
   - **Slide 5:** Refactored the upper tier into 4 modular white rounded pills ($3.21'' \times 0.43''$) per card, resized the lower constraints container to $10.31'' \times 2.13''$, and added native OMML equation mappings for $T_{prompt} \le T_{max}$ and $\min \alpha N_{hitl} + \beta T_{tokens}$.
3. **Specification Alignment ([`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md)):**
   - Updated layout definitions, visual element inventories, bullet texts, and timed speaker notes for Slides 1, 3, 4, and 5.
4. **Full Recompilation & Vector Export:**
   - Compiled `thesis_defense.pptx` (16 slides) and exported vector `thesis_defense.pdf` and 1080p `slides_png/` previews via COM automation in under 6s.
   - Visually confirmed 100% 1:1 match against the user's manual layout.

### 2.5 Manual PowerPoint Visual Enhancement (Slides 6, 7, 8) & Complete Skill Codification
Following the user's manual design refinements in PowerPoint to reduce text density and elevate visual aesthetics on Slides 6, 7, and 8:
1. **Low-Level OpenXML Reverse-Engineering & Blind-Spot Resolution:**
   - Identified that PowerPoint on Windows encapsulates native DrawingML math equations inside `<mc:AlternateContent><mc:Choice>`, causing standard `python-pptx` `slide.shapes` iteration to skip them.
   - Upgraded [`.agents/skills/presentation-coauthor/scripts/inspect_deck.py`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/scripts/inspect_deck.py) to traverse the full OpenXML `spTree` (including Choice and Fallback elements), extracting bounding boxes, preset geometries, fills, lines, text paragraphs, font sizes, and OMML runs.
2. **Programmatic Generator Updates ([`build_defense_deck.py`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/build_defense_deck.py)):**
   - **Slide 6 (Proposed Solution: RADG with Neurosymbolic Planning):** Replaced dense textboxes with $2 \times 3$ modular white rounded pills (`Translation of the intent`, `Validation of the semantic similarity`, `Orchestration` on Neural card; `Topology extraction`, `Deterministic tools usage`, `Physical feasibility validation` on Symbolic card). Synthesized the 3 contribution highlight cards on the right with concise bullets and OMML math tags ($v_{struct} \in \{0, 1\}$, $d_{sem}$, $UAR = 0$).
   - **Slide 7 (Pipeline Flow):** Formatted Phase 3 (Semantic Gate) into 2 clean bulleted lines (`Evaluate CFG v_{struct}` and `Reverse Prompting d_{sem}`). Renamed Phase 6 to `"Feasibility Gate"`.
   - **Slide 8 (Scoped Optical GraphRAG):** Created `create_scoped_graphrag_slide()` implementing the large background container card (`#F4F6F9`), a 3-stage vertical pill flow connected by a burgundy down arrow (`#85200C`), mathematical scoping bounds ($G_{sub} \subseteq G$, $T_{prompt}(G_{sub}) \ll T_{prompt}(G)$), the 17-node German backbone network map with click animation, topology citation, and bottom callout banner.
3. **Specification Alignment ([`deck_spec.md`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/presentations/thesis_defense/deck_spec.md)):**
   - Synchronized visual architecture descriptions, component inventories, and copy for Slides 6, 7, and 8.
4. **Recompilation, Vector Export & Automated Diffing:**
   - Recompiled `thesis_defense.pptx` and exported vector `thesis_defense.pdf` and 1080p `slides_png/` previews via Windows PowerPoint COM automation in under 6 seconds.
   - Ran `inspect_deck.py --diff` comparing the user's manual backup against the newly generated deck: **0 discrepancies detected across all 16 slides (100% match)**.
5. **Permanent Skill Codification ([`presentation-coauthor`](file:///home/felipeab/MultiAgentON/.agents/skills/presentation-coauthor/)):**
   - Enshrined **Hard Rule 5 (Two-Way Synchronization & Reverse Engineering Contract)** in `SKILL.md`.
   - Formalized the 6-step protocol in `references/workflow-guide.md` (Backup $\rightarrow$ Deep OpenXML Inspection $\rightarrow$ Python Reverse-Engineering $\rightarrow$ Spec Synchronization $\rightarrow$ Diff Verification $\rightarrow$ Re-Export).
   - Added `--diff` and `--json` CLI capabilities to `scripts/inspect_deck.py` with unicode math normalization.
   - Synchronized to both local `.agents/skills/presentation-coauthor/` and global `~/.gemini/config/skills/presentation-coauthor/`.

---

## 3. Verification & Test Outcomes

- **Automated Diff Verification:** Executed `inspect_deck.py <user_backup.pptx> --diff <thesis_defense.pptx>`. Result: **0 discrepancies detected across all 16 slides (100% match)**.
- **Unit Test Suite:** Ran `uv run pytest`. All **278 unit tests passed cleanly** (100% success, 0 regressions, 4.42s runtime).
- **Presentation Compilation & Export:** `build_defense_deck.py` and `export_presentation.py` completed with exit code 0.
- **Visual Inspection:** Inspected all generated slide PNGs (`slide_06.png`, `slide_07.png`, `slide_08.png`), verifying sharp layout, native math typography, and zero text overflow.
- **Git Audit:** Confirmed clean git status touching only relevant active documents and preserving historical weekly reports.

---

## 4. Handover & Next Steps

1. **Commit and Push:** Commit all modernized artifacts, synchronized presentation files, and skill upgrades using conventional commits and push to open PR #65 (`feat/presentation-coauthor-and-defense-deck`).
2. **Advisor Checkpoint:** Present the updated defense deck and narrative structure to Prof. Massimo Tornatore and Prof. Qiaolun Zhang.
3. **Sprint 4 Benchmarking:** Proceed with the 100-demand evaluation on the 17-node German backbone network.
