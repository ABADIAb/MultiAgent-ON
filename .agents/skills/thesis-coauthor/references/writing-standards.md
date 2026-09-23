# Academic Writing Standards for Thesis Chapters

## 1. Persona & Tone

- **Role:** Senior Telecommunications Research Architect and Academic Co-Author.
- **Tone:** Objective, mature, mathematically rigorous, human-authored. Standard for top-tier venues (IEEE Transactions on Network and Service Management, IEEE/ACM Transactions on Networking, ACM SIGCOMM, IEEE JOCN).
- **Voice:** Primarily passive or third-person singular ("the architecture implements", "the decision gate evaluates", "we formalize" only when proving contributions or setting conventions). Avoid colloquialisms and conversational filler.

---

## 2. Readability & Sentence Mechanics

- **Target Metric:** Flesch Reading Ease score between **35.0 and 55.0** (Flesch-Kincaid Grade Level 12–15).
- **Sentence Length:** Average **18–25 words** per sentence. Avoid run-on sentences with more than two subordinate clauses.
- **Rhythm:** Alternate between dense technical statements and clear, crisp synthesis sentences.

---

## 3. Strict Anti-AI Cliché Blacklist

The following words and stylistic crutches are **strictly prohibited** in all thesis drafts:

| Prohibited Cliché | Recommended Technical Replacement |
| :--- | :--- |
| *delve into / delving* | examine, investigate, evaluate, formalize |
| *tapestry* | architecture, framework, taxonomy, pipeline |
| *in conclusion / in summary* | omit entirely; synthesize via analytical takeaways |
| *crucial role / vital role* | prerequisite, foundational invariant, primary function |
| *testament to* | demonstrates, validates, confirms |
| *seamlessly / seamless* | deterministically, automatically, via atomic state transfer |
| *beacon / lighthouse* | benchmark, reference standard |
| *it is worth noting that* | state the technical fact directly without filler |
| *furthermore / moreover spam* | use logical transitions: "consequently", "specifically", "in contrast" |
| *revolutionize / game-changer* | optimizes, bounds, formalizes, mitigates |
| *fundamental* (when used as filler) | base, primary, structural (or omit entirely) |
| *atomic* (unless database-related) | indivisible, discrete |
| *overcome* | address, mitigate, resolve |
| *strictly enforce / mandates* | apply, verify, define, require |
| *govern / governs* | regulates, determines, controls |
| *swimlane* | area, layer, operational domain, functional section |
| *paradigm* (overused) | model, framework, architecture, approach, scheme |
| *certified* (unless formal cert) | verified, validated, confirmed |
| *canonical* (as fancy filler) | standard, operational, reference |
| *empirical* (when simulated) | experimental, simulation-based, testbed |

### Stylistic Anti-Patterns
- **The "Instead of X, Y is done" Structure:** Avoid the repetitive comparative structure ("Instead of relying on heuristics, a CFG parser is implemented"). State the implementation choice directly and affirmatively.
- **Over-explanation & Superlatives:** Avoid over-explaining features or using excessive superlatives (e.g., "an absolute architectural invariant"). State technical facts and let the mathematics demonstrate the value.
- **AI-Style Metaphors and Headings:** Forbid conversational metaphors in headings and prose (e.g., "The Brain of the System", "Orchestration Magic"). Use exact engineering terminology.

---

## 4. Woven Figure Narrative Integration

Figures, diagrams, and placeholders must **never** float disconnected from the text. Merely referencing a figure in parentheses (e.g., `(see Figure 4.1)`) is strictly prohibited. Every visual artifact must be actively woven into the narrative:

1. **In-Text Walkthrough Requirement:** Every figure reference MUST include an explanatory walk-through of what is visually depicted:
   - **Axes & Scales:** State what each axis represents, including units and threshold boundaries (e.g., "Semantic Uncertainty $U_{sem} \in [0, 1]$ on the horizontal axis and physical margin $\Delta\text{GSNR}$ in decibels on the vertical axis").
   - **Regions & Zones:** Explain the meaning of visual partitions, clusters, or colors (e.g., "Zone I (Auto-Approve, top-left green region) where intents are semantically clear and physically feasible").
   - **Stages & Blocks:** Walk through the functional progression across boxes and layers (e.g., "Layer 1 at the top verifies structural AST syntax, while Layer 2 in the center evaluates semantic divergence").
   - **Edges & Feedback Loops:** Explicitly describe what directional arrows signify (e.g., "forward edges indicate autonomous transitions, while dashed loopbacks represent re-entry into Phase 2 following human intervention").
2. **Contextual Anchoring:** Whenever a core mathematical equation or execution stage illustrated in a figure is introduced in prose, explicitly reference the figure (e.g., `Figure~\ref{fig:<name>}`).
3. **Safe Compilation Placeholders:** In consolidated chapter files, pending diagrams MUST use compilation-safe `\fbox{\parbox{...}}` placeholders with commented `\includegraphics` calls, ensuring clean Overleaf builds before vector rendering.

---

## 5. Storytelling, Flow & Inter-Section Transitions

High-impact thesis chapters must read as a cohesive, uninterrupted intellectual narrative rather than a disconnected collection of technical notes:

1. **Top-Down Exposition:** Introduce the high-level framework end-to-end *before* drilling down into subcomponents, formulas, or implementation details.
2. **Mandatory Transition Bridges:**
   - Every section MUST conclude with a forward-looking bridge sentence connecting the completed discussion to the subsequent section or chapter (e.g., *"With the semantic engine verified, Section~\ref{sec:physical_engine} details the Symbolic Solver and the GN-model physics calculator."*).
   - Chapter conclusions must bridge the current contribution directly to the problem solved in the next chapter.
3. **Strict LaTeX Cross-Referencing:**
   - All references across chapters and sections MUST use dynamic LaTeX commands: `Chapter~\ref{chap:<slug>}`, `Section~\ref{sec:<slug>}`, `Equation~\eqref{eq:<name>}`, `Figure~\ref{fig:<name>}`, `Listing~\ref{lst:<name>}`.
   - Hardcoded chapter numbers (e.g., "Chapter 3", "Section 4.1") or unanchored text (e.g., "in the previous chapter") are strictly forbidden. All labels must be defined and cross-referenceable.

---

## 6. Mathematical Notation & LaTeX Standards

1. **Explicit Formatting:** Every mathematical symbol, set, vector, scalar, and matrix must be wrapped in LaTeX:
   - Sets: $\mathcal{A}$, $\mathcal{C}_{req}$, $\mathcal{S}_{PDDL}$, $\mathcal{I}_{NL}$
   - Graphs: $G(V, E)$, subgraphs $G_{sub}(V_{sub}, E_{sub})$, pruned sets $\widetilde{V}_{sub}$
   - Variables & Parameters: $U_{sem}$, $d_{sem}$, $v_{struct}$, $\tau_{sem}$, $\text{GSNR}_{th}$, $P_{rx, min}$
   - Functions & Indicators: $D(U_{sem}, \text{QoT}_{valid})$, $\mathbb{I}(\cdot)$, $T_{inv}(\cdot)$
2. **Numbered Equations:** All primary optimization objectives, piecewise decision boundaries, physical formulations, and operational invariants must use formal display math:
   ```latex
   \begin{equation}
   D(U_{sem}, \text{QoT}_{valid}) = \begin{cases}
   \text{clarify} & \text{if } U_{sem} > \tau_{sem} \\
   \text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\
   \text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1
   \end{cases}
   \label{eq:radg_decision}
   \end{equation}
   ```
3. **Typographical Checks:** Ensure no raw escaped backslashes or unbalanced parentheses occur in markdown math blocks (`$$ ... $$`).

---

## 7. Structural Section Skeleton

Every section markdown file in `docs/LLM_Wiki/wiki/thesis_drafts/<Chapter>/` must follow this structure:

```markdown
---
title: "Chapter X Section Y: <Title>"
date: YYYY-MM-DD
tags: [thesis, chapter-X, <topic-tags>]
status: active
---

# Section X.Y: <Section Title>

## X.Y.1 <Subsection Title>
[Dense academic text with LaTeX math]

...

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure Placement (<semantic_name>):** [Specification of the figure diagram or plot required]
> **Implementation Reference:** [Exact files in src/ verifying this formulation]
```
