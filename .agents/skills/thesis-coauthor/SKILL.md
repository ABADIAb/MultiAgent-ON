---
name: thesis-coauthor
description: "Trigger: thesis draft, write chapter, write section, refine chapter, thesis section, thesis figure, academic writing, thesis consistency. Plan, draft, audit, and generate figures for thesis chapters."
license: Apache-2.0
metadata:
  author: felipe-abadia
  version: "1.0"
---

## Activation Contract

Activate this skill when:
- Writing new Master's thesis chapters or sections from scratch.
- Auditing, reviewing, and mathematically validating written sections against the active codebase (`src/`), `Architecture_v5.md`, and feature documentation.
- Propagating updates across interconnected sections and figures to maintain global notation and conceptual consistency (ripple-effect audits).
- Designing, generating, or debugging publication-ready academic figures, architecture diagrams, or mathematical plots in Python (`matplotlib`).
- Consolidating individual markdown sections into the merged chapter LaTeX file (`chapter_<#>_<slug>.txt`).

Do not activate for routine weekly reports or non-thesis software engineering tasks.

---

## Hard Rules

### 1. Academic Rigor & Style
- **Venues Standard:** High-tier telecommunications venues (IEEE Transactions, ACM SIGCOMM, IEEE JOCN).
- **Top-Down Storytelling:** Chapters and sections must follow a strict top-down structure. Introduce the high-level conceptual framework or pipeline end-to-end *before* detailing specific mathematical components, decision gates, or sub-mechanisms.
- **Readability Target:** Flesch Reading Ease score between **35.0 and 55.0** (Grade Level 12–15). Dense, clear, precise sentences (18–25 words average).
- **Anti-AI Cliché Blacklist:** Strictly forbid "delve into", "tapestry", "in conclusion", "crucial/vital role", "seamlessly", "testament to", "beacon", "furthermore/moreover" spam, "composite", "orthogonal" (unless mathematically precise), "catastrophic" (use "total" instead), "monotonic" (unless mathematically precise), and "computationally intensive" (unless factually true for the specific algorithm). See [writing-standards.md](references/writing-standards.md).
- **Domain Vocabulary:** Always use "operational integrity" or "transmission integrity" instead of generic words like "safety" or "risks" when referring to network stability and resilience.
- **Exhaustive LaTeX Math:** Format all variables, sets, matrices, and numbered equations in formal LaTeX.

### 2. Codebase Grounding (Source of Truth)
- Ground every theoretical claim and mathematical formulation against `src/core/`, `src/nodes/`, and `docs/LLM_Wiki/wiki/architecture/Architecture_v5.md`.
- **Inconsistency in Draft:** Explain the discrepancy technically with file references and correct the draft.
- **Inconsistency in Code / Architecture:** **STOP.** Explain the issue with technical reasoning and obtain user approval before modifying any source code or architecture specifications.
- **Engineering Simplifications:** Document operational assumptions (e.g., SMF-28 homogeneous fiber, zero equalization loss) as explicit `Assumption` or `Remark` blocks.

### 3. Ripple-Effect Consistency & Backlog
- Whenever a parameter, mathematical symbol, threshold, or state option is altered in one section, audit all related sections and figures in the chapter.
- Log forward-looking dependencies and future implementation assumptions directly into `docs/LLM_Wiki/wiki/thesis_drafts/Drafting_Backlog.md`.
- **Merged LaTeX Milestone Rule:** Consolidate individual section drafts into `chapter_<#>_<slug>.txt` as an **explicit milestone step** once all chapter sections are approved.

### 4. Publication-Ready Figure & Diagram Generation
- **Visual Purpose & Anti-Redundancy (No Poster Syndrome):** Figures and diagrams must NOT verbatim repeat or cram text that is already explained in the main chapter sections. Their purpose is strictly to amplify information, visualize complex processes, closed-loop architectures, or abstract concepts that are difficult to grasp through text alone.
- **Directory Hierarchy (`figs_<Chapter>/`):**
  ```text
  figs_<Chapter>/         # e.g., figs_SystemModel/
  ├── src/
  │   ├── diagrams/       # Pathway A: Native Draw.io XML (.drawio)
  │   └── plots/          # Pathway B: Python generator scripts (.py)
  ├── pdf/                # Production vector outputs for LaTeX
  ├── png/                # 300 DPI high-resolution previews
  └── README.md           # Catalog & LaTeX snippets
  ```
- **Semantic Naming Standard:** Filenames must NEVER include hardcoded figure or chapter numbers (e.g., use `conceptual_framework.drawio` or `radg_decision_space.py`, NOT `figure_3_2_conceptual_framework.drawio` or `fig_3_4_radg.py`). This decouples filenames from document revisions. Sequence numbering is handled dynamically by LaTeX (`\label{fig:<name>}` and `Figure~\ref{fig:<name>}`).
- **Architecture, Pipeline & Workflow Diagrams (Pathway A):** Directly generate native **Draw.io XML (`<semantic_name>.drawio`)** in `figs_<Chapter>/src/diagrams/`.
  - **XML Source:** Generate `.drawio` XML directly. The operator refines the diagram manually in Draw.io.
  - **Math Formatting in Draw.io:** Always format mathematical symbols with HTML italics and subscripts for native rendering: `<i>S</i><sub>PDDL</sub>`, `<i>U</i><sub>sem</sub>`, `<i>τ</i><sub>sem</sub>`, `<i>I</i><sub>NL</sub>`, `<i>P</i><sub>rx</sub>`.
  - **Strict XML Escaping:** Ensure all HTML tags inside XML attributes (`value="..."`) are properly escaped (`&lt;b&gt;`, `&quot;`, `&amp;`), and validate syntax with `xml.etree.ElementTree`.
  - **Export Deliverables:** Compile to vector `.pdf` and 300 DPI `.png` in `figs_<Chapter>/pdf/` and `figs_<Chapter>/png/` using the skill exporter script:
    `uv run python .agents/skills/thesis-coauthor/scripts/export_diagram.py <semantic_name>`
    (Supports `--chapter <Chapter>` and `--all` flags, bridging Linux/WSL to Draw.io desktop binary).
- **Numerical Physics, Simulation Curves & Non-Diagram Figures (Pathway B):** Use Python matplotlib scripts (`<semantic_name>.py`) placed in `figs_<Chapter>/src/plots/` to generate `.pdf` (vectorial, `pdf.fonttype = 42`) in `figs_<Chapter>/pdf/` and `.png` (300 DPI) in `figs_<Chapter>/png/`.
- Follow [figure-guidelines.md](references/figure-guidelines.md).

---

## Decision Gates

| Action Required | Primary Focus | Key Reference |
| :--- | :--- | :--- |
| **Drafting from Scratch** | Redacting academic prose, LaTeX math, and structure | [writing-standards.md](references/writing-standards.md) |
| **Auditing & Fact-Checking** | Cross-verifying math and logic against `src/` | [consistency-protocol.md](references/consistency-protocol.md) |
| **Ripple-Effect Audit** | Synchronizing cross-section notation & figures | [consistency-protocol.md](references/consistency-protocol.md) |
| **Diagram Design (Flowcharts/Pipelines)** | Direct Draw.io XML (`.drawio`) in `figs_<Chapter>/src/diagrams/` | [figure-guidelines.md](references/figure-guidelines.md) |
| **Plot Design (Physics/Simulation)** | Python matplotlib scripts in `figs_<Chapter>/src/plots/` | [figure-guidelines.md](references/figure-guidelines.md) |
| **Milestone Chapter Merge** | Consolidating approved `.md` into LaTeX `.txt` with `\ref{fig:...}` | [consistency-protocol.md](references/consistency-protocol.md) |

---

## Execution Steps

### Step 1: Boot & Context Ingestion
1. Read mandatory boot files: `Architecture_v5.md`, `ProblemStatement_v5.md`, `index.md`, and recent session summaries.
2. Read the target chapter roadmap in `docs/LLM_Wiki/wiki/thesis_drafts/Writing_Roadmap_v1.md` and outline in `Thesis_Outline_v4.md`.
3. Locate and inspect the relevant `src/` modules (e.g., `src/core/`, `src/nodes/`).

### Step 2: Codebase Fact-Checking & Math Validation
1. Verify that mathematical symbols and physical formulas match domain models:
   - $G(V, E)$, physical parameters in `src/core/models.py`.
   - Decision function $D(U_{sem}, \text{QoT}_{valid})$ in `src/core/radg.py`.
   - Divergence $d_{sem}$ and uncertainty $U_{sem}$ in `src/core/semantic_gate.py`.
   - Physical feasibility $\text{QoT}_{valid}$ and GSNR in `src/core/qot_calculator.py`.
2. Flag any discrepancy between proposed equations and executable code.

### Step 3: Drafting & Refinement
1. Write or refine the section markdown under `docs/LLM_Wiki/wiki/thesis_drafts/<Chapter>/<#_#_name.md>`.
2. Apply IEEE/ACM academic prose and LaTeX formatting.
3. Append a `## Drafting Recommendations & Figure Placement` block at the end of each section.
4. **Zero Plain Text Diagrams:** Never retain ASCII-art or plain text diagrams in final section markdown. Replace them with formal figure placeholders.

### Step 4: Ripple-Effect Cross-Consistency Check
1. Check if modified equations or symbols affect other drafted sections or existing figures.
2. If cross-section discrepancies exist, propose or execute adjustments.
3. Log any unresolved forward dependencies in `Drafting_Backlog.md`.

### Step 5: Figure Design & Generation (When Needed)
- **Pathway A (Architecture, Workflows & Pipeline Diagrams):**
  1. Generate the native Draw.io XML directly into `figs_<Chapter>/src/diagrams/<semantic_name>.drawio` using semantic naming.
  2. Validate XML syntax using Python `xml.etree.ElementTree`.
  3. Ensure mathematical notation uses HTML tags (`<i>U</i><sub>sem</sub>`, `<i>S</i><sub>PDDL</sub>`).
  4. Export to vector `figs_<Chapter>/pdf/<semantic_name>.pdf` and raster `figs_<Chapter>/png/<semantic_name>.png` via:
     `uv run python .agents/skills/thesis-coauthor/scripts/export_diagram.py <semantic_name> [--chapter <Chapter>]`
     (or pass `--all` to export all diagrams in the chapter).
- **Pathway B (Numerical Physics, Simulation Curves & Non-Diagram Figures):**
  1. Write the Python generation script in `figs_<Chapter>/src/plots/<semantic_name>.py` using semantic naming.
  2. Execute via `uv run python <script_path>` to produce vector `.pdf` in `figs_<Chapter>/pdf/` and preview `.png` in `figs_<Chapter>/png/`.
  3. Audit the generated `.png` using `view_file` to verify zero text collision, proper alignment, and clean typography.
- **Documentation:** Update `figs_<Chapter>/README.md` and provide the LaTeX figure snippet for Overleaf integration.

### Step 6: Milestone LaTeX Consolidation (When Chapter is Complete)
1. When all sections of a chapter are drafted and approved, merge them into `chapter_<#>_<slug>.txt`.
2. **Chapter File Purity:** Chapter files must start directly at line 1 with `\chapter{...}` and contain zero package imports or macro definitions. All styling is centralized in `config.tex`.
3. **Strict LaTeX Cross-Referencing:** All in-text references to figures, listings, and specifications MUST strictly use LaTeX format (`Figure~\ref{fig:<semantic_name>}`, `Listing~\ref{lst:<name>}`). Hardcoded numbers (e.g., "Figure 3.1") or placeholder text (e.g., "Figure #") are STRICTLY FORBIDDEN.
4. **Formal Figure Environments & Float Barriers:** Insert complete LaTeX figure environments using `[!htbp]` priority, bounded widths (`0.85\textwidth` to `0.92\textwidth`), and insert `\FloatBarrier` before key section headings following figures to prevent float intrusions:
   ```latex
   \begin{figure}[!htbp]
     \centering
     \includegraphics[width=0.88\textwidth]{Figures/figs_<Chapter>/<semantic_name>.pdf}
     \caption{<Explanatory academic caption describing the figure>.}
     \label{fig:<semantic_name>}
   \end{figure}
   \FloatBarrier
   ```
5. **Zero Raw Verbatim:** Never use raw `\begin{verbatim}` blocks. Use `academicbox` for code/PDDL listings and `formalbox` for mathematical grammars and formal specifications (see [overleaf-standards.md](references/overleaf-standards.md)).
6. Verify that all figure labels, equation references, and citations are syntactically valid and balanced in LaTeX.

---

## Output Contract

Return:
1. Path to newly created or modified section markdown files in `thesis_drafts/`.
2. Code audit report detailing math-to-code alignment and any identified discrepancies.
3. Path to generated Python figure scripts and vector/preview artifacts in `figs_<Chapter>/`.
4. Summary of ripple-effect checks across dependent sections, figures, and `Drafting_Backlog.md`.
5. LaTeX integration snippets for document compilation.

---

## References

- [writing-standards.md](references/writing-standards.md) — Tone, Flesch score, anti-AI cliché blacklist, and LaTeX notation.
- [overleaf-standards.md](references/overleaf-standards.md) — Overleaf packages, centralized config.tex, academicbox/formalbox, and FloatBarrier rules.
- [consistency-protocol.md](references/consistency-protocol.md) — Grounding hierarchy, inconsistency resolution, ripple-effect audit, and backlog.
- [figure-guidelines.md](references/figure-guidelines.md) — Python matplotlib figure standards, TrueType fonts, palette, and anti-collision.
- [Writing_Roadmap_v1.md](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/thesis_drafts/Writing_Roadmap_v1.md) — Phased thesis writing roadmap.
- [Architecture_v5.md](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/wiki/architecture/Architecture_v5.md) — Authoritative system architecture.
