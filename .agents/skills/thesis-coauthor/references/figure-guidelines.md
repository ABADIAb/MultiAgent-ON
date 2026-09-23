# Academic Figure & Diagram Design Guidelines

## 1. Dual Visual Artifact Pathways & Directory Organization
 
To balance manual drag-and-drop editability for architecture diagrams with reproducibility for scientific physics simulations, we strictly separate production into two non-overlapping pathways within a clean directory hierarchy:
 
 ```text
 docs/LLM_Wiki/wiki/thesis_drafts/<Chapter>/figs_<Chapter>/
 ├── src/
 │   ├── diagrams/       # Pathway A: Native Draw.io XML (.drawio)
 │   └── plots/          # Pathway B: Python generator scripts (.py)
 ├── pdf/                # Production vector outputs for Overleaf / LaTeX (\includegraphics)
 ├── png/                # 300 DPI high-resolution previews for wiki & visual QA
 └── README.md           # Catalog & LaTeX snippets
 ```
 
- **Semantic Naming Standard:** Figure files MUST use semantic, descriptive names without hardcoded figure or chapter numbers (e.g., `conceptual_framework.drawio`, `radg_decision_space.py`). This insulates filenames from document restructuring.
- **Overleaf File Path Standard:** In Overleaf, figure assets are stored under `Figures/figs_<Chapter>/<semantic_name>.pdf` (e.g., `Figures/figs_SystemModel/conceptual_framework.pdf`). LaTeX `\includegraphics` commands MUST use `Figures/figs_<Chapter>/<semantic_name>.pdf`.
- **Pathway A (Architecture, Workflows & Pipeline Diagrams):** Direct Draw.io XML in `figs_<Chapter>/src/diagrams/<semantic_name>.drawio`. The operator refines them manually in Draw.io, and the assistant or author exports them to `pdf/` and `png/`.
- **Pathway B (Numerical Physics & Simulation Curves):** Python Matplotlib scripts in `figs_<Chapter>/src/plots/<semantic_name>.py` generating vector outputs in `pdf/` and raster in `png/`.

---

## 2. Core Figure Design Principles

### 2.1 The 5 Diagram Laws (Strict Visual Budget)
1. **Reuse Over Redundancy:** Before drafting or drawing a new diagram, check if the system workflow is already depicted in an earlier chapter (e.g. Chapter 3's `Figure~\ref{fig:conceptual_framework}`). If an existing diagram illustrates the pipeline, reference it in text. NEVER draw redundant or nearly identical diagrams across chapters.
2. **Block Count Budget:** Maximum 6 to 8 primary functional blocks per diagram. If a subsystem requires more, abstract it.
3. **Word Count Budget:** 3 to 6 words maximum per block (Component Name + Math Symbol/IO). ZERO full sentences, ZERO bullet points (`•`, `-`), ZERO algorithmic step listings inside shapes.
4. **Zero Explanatory Note Cards:** Strictly forbid side note cards, warning banners, contract blocks, or multi-line descriptions inside diagram files. Explanations belong in the chapter prose or code listings.
5. **Strict Single-Direction Flow:** Flow MUST follow a single primary direction (Top-to-Bottom or Left-to-Right). Connectors must be orthogonal with minimal crossings.

### 2.2 Visual Purpose & Anti-Redundancy (Complementary Role, No Poster Syndrome)
- **Do Not Repeat Prose:** Figures and diagrams must NEVER duplicate or verbatim restate text that is already articulated in the chapter sections.
- **Visual Amplification:** Their sole objective is to visually clarify, enhance, and complement understanding—illustrating complex multi-phase workflows, closed-loop feedback trajectories, state transitions, and multidimensional decision spaces that are cognitively harder to absorb from text alone.
- **Minimal Text Inside Figures:** Keep labels concise, functional, and minimal. Strictly avoid paragraph-style cards, explanatory summaries, or "poster-style" text boxes inside the diagram area (e.g., do not attach side panels restating architectural guarantees already detailed in the prose).
- **Anti-AI Pattern Filter in Figures:** Text within diagrams (node labels, gate questions, annotations) must strictly adhere to the academic writing standards in `writing-standards.md`. Strictly forbid empty AI buzzwords or cliché constructs (e.g., "paradigm", "mandates", "govern", "seamlessly", "vital role", "beacon", "testament").

### 2.3 Typography & Legibility Standard (Large, Crisp Sizing)
Because figures are scaled down to fit thesis page widths (`\includegraphics[width=0.75\textwidth]`), small fonts become completely illegible. All text elements MUST be sized generously so they remain sharp, legible, and prominent in the compiled PDF and print:
- **Draw.io Diagrams (Pathway A):**
  - **Process / Phase Titles:** `fontSize=15;` to `16;` (bold).
  - **Compact Math Subtitles:** `fontSize=12.5;` to `13.5;` (math symbols only, e.g. `<i>S</i><sub>PDDL</sub>`).
  - **Decision Gates (Diamonds):** `fontSize=14;` to `15;` (bold), math subtext `fontSize=12.5;` to `13;`.
  - **Edge / Transition Labels:** `fontSize=12.5;` to `13;`.
  - **Hard Minimum:** Strictly NEVER use 9–11 pt fonts in architecture diagrams.
- **Python Matplotlib Plots (Pathway B):**
  - **Axis Titles / Labels:** `13`–`15 pt` (bold/serif).
  - **Tick Labels:** `11`–`12 pt`.
  - **Legend Entries:** `11`–`12.5 pt`.
  - **In-Plot Zone Annotations:** `12`–`13.5 pt`.
 
 ---

## 3. Pathway A: Native Draw.io XML Specifications (`.drawio`)

When creating architecture overviews, sequence diagrams, decision flowcharts, or workflow pipelines:

### 3.1 Direct Generation (Native Draw.io XML)
- Directly generate `figs_<Chapter>/src/diagrams/<semantic_name>.drawio`.
- Validate the generated XML using Python's `xml.etree.ElementTree` to guarantee well-formed syntax.
- Export to vector `.pdf` and raster `.png` using the skill script:
  `uv run python .agents/skills/thesis-coauthor/scripts/export_diagram.py <semantic_name>`
  (which auto-detects Draw.io locally or via WSL/Windows integration).

### 3.2 XML Skeleton Structure
```xml
<mxfile host="app.diagrams.net" modified="2026-09-06T12:00:00.000Z" agent="5.0" version="22.0.0" type="device">
  <diagram id="fig_X_Y" name="Figure X.Y">
    <mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="1" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- Nodes and Edges -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 3.3 Mathematical Typography & Subscript Rules
Draw.io handles labels as HTML when `html=1` is set in the style. To guarantee clean mathematical notation without relying on external MathJax loading:
- **Always format variables and indices with HTML italics and subscripts:**
  - `<i>S</i><sub>PDDL</sub>`
  - `<i>I</i><sub>NL</sub>`
  - `<i>G</i><sub>sub</sub>`
  - `<i>U</i><sub>sem</sub>`
  - `<i>τ</i><sub>sem</sub>`
  - `<i>v</i><sub>struct</sub>`
  - `<i>P</i><sub>rx</sub>`
  - `QoT<sub>valid</sub>(<i>π</i>)`
  - `GSNR<sub>th</sub>`
- If full LaTeX MathJax is desired by the operator, Draw.io supports `$$ ... $$` when `Extras -> Mathematical Typesetting` is activated.

### 3.4 Strict XML Attribute Escaping (Crucial)
In XML attributes (`value="..."`), all HTML tags and quotes MUST be XML-escaped:
- `<` $\to$ `&lt;`
- `>` $\to$ `&gt;`
- `"` $\to$ `&quot;`
- `&` $\to$ `&amp;`
- `'` $\to$ `&#39;`

Example of properly escaped node label:
```xml
<mxCell id="p2" value="&lt;b&gt;Phase 2: CFG-Validated PDDL Parsing&lt;/b&gt;&lt;br&gt;&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;LLM Semantic Compiler → &lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt;&lt;/font&gt;" style="rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EBF8FF;strokeColor=#3182CE;strokeWidth=1.5;fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;" vertex="1" parent="1">
  <mxGeometry x="400" y="134" width="380" height="68" as="geometry" />
</mxCell>
```

### 3.5 Standard Draw.io Styles
- **Process / Phase Box:** `rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#...;strokeColor=#...;strokeWidth=1.5;fontFamily=Georgia, Times New Roman, serif;fontSize=15;`
- **Decision Gate (Diamond):** `rhombus;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#B7791F;strokeWidth=1.5;fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#744210;align=center;verticalAlign=middle;`
- **Orthogonal Connector:** `edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#...;strokeWidth=1.5;fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;endArrow=block;endFill=1;`
- **Curved Feedback Loop:** `edgeStyle=none;curved=1;dashed=1;html=1;strokeColor=#...;strokeWidth=1.5;fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;endArrow=block;endFill=1;`

---

## 4. Pathway B: Python Matplotlib Numerical Plots & Non-Diagram Figures (`.py`)

For mathematical simulation curves, parametric sweeps, and analytical decision-space plots (e.g., GSNR accumulation, NLI non-linear curves, RADG 2D operational space):
- **Output:** Generate Python generator script (`<semantic_name>.py`), along with both `.pdf` (vectorial for Overleaf under `Figures/figs_<Chapter>/`) and `.png` (300 DPI preview) in `figs_<Chapter>/`.
- **TrueType Selectable Text:**
  ```python
  import matplotlib.pyplot as plt
  plt.rcParams["pdf.fonttype"] = 42
  plt.rcParams["ps.fonttype"] = 42
  plt.rcParams["font.family"] = "serif"
  ```
- **Execution & Validation:** Execute via `uv run python fig_*.py` and inspect via `view_file`.

---

## 5. Cohesive Academic Color Palette

Use a sober, professional palette suitable for high-tier academic publications:

| Semantic Role | Background Fill | Border Stroke | Usage in Architecture |
| :--- | :--- | :--- | :--- |
| **Neural / Input / NL** | `#EBF8FF` | `#3182CE` | Intent Ingestion, PDDL Parser, Reverse Prompting |
| **Symbolic / Solver / Math** | `#EDFDFD` | `#319795` | Symbolic Solver, GraphRAG, GN-Model QoT Calculator |
| **Auto-Approve / Feasible** | `#F0FFF4` | `#38A169` | RADG Auto-Pass, Valid Feasibility ($QoT_{valid}=1$) |
| **Warning / Clarify HITL** | `#FEEBC8` | `#DD6B20` | Semantic Uncertainty Gate, Phase 3b Clarification |
| **Replan / Violation** | `#FED7D7` | `#E53E3E` | Physical Risk Replan Loop, Rejection |
| **Neutral Substrate** | `#F7FAFC` | `#CBD5E0` | Context boxes, background clusters, boundary limits |

---

## 6. Diagram Archival Protocol & Local Exporter Scripts

### 6.1 Diagram Archival Protocol
When an architectural figure is deprecated, superseded, or deferred to a later chapter (e.g., deferring `reverse_prompting_loop` from Chapter 3 to Chapter 4):
1. **Never Silently Delete:** Move the native `.drawio` source, compiled `.pdf`, and preview `.png` into `figs_<Chapter>/archive/`:
   ```text
   figs_<Chapter>/archive/
   ├── src/diagrams/<semantic_name>.drawio
   ├── pdf/<semantic_name>.pdf
   └── png/<semantic_name>.png
   ```
2. **Catalog Audit:** Update `figs_<Chapter>/README.md` to document the archival reason and target destination.
3. **Draft Cleanup:** Remove figure references, placeholders, and numbered walkthroughs from markdown drafts and LaTeX chapter files.

### 6.2 Standalone Chapter Exporters
In addition to the global skill script (`.agents/skills/thesis-coauthor/scripts/export_diagram.py`), each chapter visual suite may maintain a lightweight standalone `export_diagrams.py` directly inside `figs_<Chapter>/src/diagrams/`:
- **Purpose:** Allows the operator to run `python export_diagrams.py` directly from within the diagrams folder on Linux or WSL without remembering CLI arguments or paths.
- **Features:** Auto-detects local Draw.io or Windows `draw.io.exe` via WSL paths, automatically passes `--crop`, and exports both `.pdf` and `.png` to the parent `pdf/` and `png/` directories.
