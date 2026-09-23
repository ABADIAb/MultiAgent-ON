# Overleaf & LaTeX Architectural Standards

This reference documents the global formatting, packages, environments, and architectural conventions for all thesis chapters compiled in Overleaf.

---

## 1. Centralized Configuration Architecture (`config.tex` / `main.tex`)

To preserve modularity, chapter files (`chapter_<#>_<slug>.txt`) must contain **zero preamble configuration or environment definitions**. All packages, custom environments, and global commands are centralized in `config.tex` (loaded via `\input{config.tex}` in `main.tex` prior to `\begin{document}`).

### Master Configuration Snippet (in `config.tex`)

```latex
% ======================================================================
% Master Thesis Styling & Academic Boxes
% Centralized in config.tex (loaded in preamble before \begin{document})
% ======================================================================
\usepackage[most]{tcolorbox}
\usepackage{placeins}

% ----------------------------------------------------------------------
% 1. Academic Box: Verbatim Code, PDDL Specs & Python Listings
% ----------------------------------------------------------------------
\newtcblisting{academicbox}[2][]{%
  enhanced,
  arc=1.2mm,
  boxrule=0.6pt,
  colback=gray!4,
  colframe=gray!60,
  coltitle=black!85,
  colbacktitle=gray!15,
  fonttitle=\sffamily\bfseries\footnotesize,
  title={#2},
  titlerule=0.4pt,
  top=5pt, bottom=5pt, left=8pt, right=8pt,
  before skip=1em, after skip=1em,
  nobreak,
  listing only,
  listing options={
    basicstyle=\ttfamily\footnotesize,
    breaklines=true,
    columns=flexible,
    keepspaces=true,
    showstringspaces=false,
    tabsize=2
  },
  #1
}

% ----------------------------------------------------------------------
% 2. Formal Box: Mathematical Specifications, CFG Grammars & Invariants
% ----------------------------------------------------------------------
\newtcolorbox{formalbox}[2][]{%
  enhanced,
  arc=1.2mm,
  boxrule=0.6pt,
  colback=gray!3,
  colframe=gray!50,
  coltitle=black!85,
  colbacktitle=gray!15,
  fonttitle=\sffamily\bfseries\footnotesize,
  title={#2},
  titlerule=0.4pt,
  top=6pt, bottom=6pt, left=10pt, right=10pt,
  before skip=1em, after skip=1em,
  nobreak,
  #1
}
```

---

## 2. Core Environments & Usage Patterns

### Pattern A: Code, PDDL & Software Listings (`academicbox`)
- **Engine:** `tcblisting` wrapping `listings` verbatim parsing.
- **Rule:** **Zero raw `\begin{verbatim}` blocks.** Every piece of code, domain predicate, goal definition, or JSON/RESTConf schema must use `academicbox`.
- **Title Convention:** `Listing <Chapter>.<#>: <Descriptive Title>` (e.g., `Listing 3.1: Formal PDDL Domain Type Hierarchy`).
- **Syntax:**
  ```latex
  \begin{academicbox}{Listing 3.1: Formal PDDL Domain Type Hierarchy}
  (define (domain optical-routing-v5)
    (:requirements :strips :typing :equality :conditional-effects)
    (:types
      node - object
      roadm transponder - node
      link - object
    )
  )
  \end{academicbox}
  ```

### Pattern B: Mathematical Grammars & Formal Specifications (`formalbox`)
- **Engine:** `tcolorbox` supporting LaTeX math mode, align, text, and tables.
- **Rule:** Use for formal language production rules (CFG/BNF), algorithmic invariants, optimization models, or multi-line definition sets.
- **Title Convention:** `Formal Specification <Chapter>.<#>: <Descriptive Title>` (e.g., `Formal Specification 3.1: Context-Free Grammar Production Rules ($R$)`).
- **Syntax:**
  ```latex
  \begin{formalbox}[label=spec:cfg_production_rules]{Formal Specification 3.1: Context-Free Grammar Production Rules ($R$)}
  \begin{align*}
  S_0 &\to \texttt{(define (problem } \text{SingleNode}\texttt{)} \\
      &\quad\quad \text{DomainBlock} \; \text{ObjectsBlock} \; \text{InitBlock} \; \text{GoalBlock}\texttt{)} \\[4pt]
  \text{GoalBlock} &\to \texttt{(:goal (and } \text{ExprList}\texttt{))} \;\mid\; \texttt{(:goal } \text{Predicate}\texttt{)} \\[4pt]
  \text{Predicate} &\to \texttt{(route } \text{NodePair}\texttt{)} \\
      &\;\mid\; \texttt{(avoid-node } \text{SingleNode}\texttt{)}
  \end{align*}
  \end{formalbox}
  ```

---

## 3. Float Management & Barrier Protection (`placeins`)

### The Float Intrusion Anti-Pattern
In LaTeX, figures with `[htbp]` are floats. When a large figure cannot fit on the current page, LaTeX queues it and continues typesetting text and subsection headings. At the next page break, LaTeX flushes the queued figure at `[t]` (top of page), frequently cutting between a section header and its corresponding listing or paragraph.

### Prevention Protocol
1. **Priority Specifier:** Always declare figures with `[!htbp]` to instruct LaTeX to relax vertical spacing penalties and place the figure immediately.
2. **Dimension Ceiling:** Keep figure widths between `0.85\textwidth` and `0.92\textwidth` (avoid `0.98\textwidth` or `\linewidth` unless the aspect ratio is extremely wide).
3. **Mandatory Float Barriers:** Place `\FloatBarrier` immediately before major `\subsection` or `\subsubsection` headings that introduce code listings or specifications:
   ```latex
   \begin{figure}[!htbp]
       \centering
       \includegraphics[width=0.88\textwidth]{Figures/figs_<Chapter>/<semantic_name>.pdf}
       \caption{...}
       \label{fig:<semantic_name>}
   \end{figure}

   \FloatBarrier
   \subsection{<Next Subsection Title>}
   ```

---

## 4. Formal Grammar (CFG / EBNF) Formatting Rules

- **Anti-Pattern:** Never embed multi-line `align` blocks inside `\begin{itemize}` items. Bullet indents squeeze the available text width, triggering severe `Overfull \hbox` and breaking right margins.
- **Standard Layout:**
  1. Define the grammar 4-tuple: $\mathcal{G} = (V_N, \Sigma, R, S_0)$.
  2. Enumerate non-terminals $V_N$, terminals $\Sigma$, and start symbol $S_0$ cleanly in a descriptive list.
  3. Extract production rules $R$ into a standalone `formalbox`.
  4. Use `\texttt{...}` for terminal strings/keywords and `\text{...}` for non-terminals.
  5. Wrap long production rules across multiple lines using `\quad\quad` for visual hierarchy.

---

## 5. Chapter File Purity

Every merged chapter file (`chapter_<#>_<slug>.txt`) must:
1. Start directly at line 1 with `\chapter{<Chapter Title>}` and `\label{chap:<slug>}`.
2. Rely strictly on `config.tex` for all package imports and macro declarations.
3. Contain zero plain-text / ASCII-art diagrams.
4. Use dynamic cross-references exclusively (`Figure~\ref{fig:...}`, `Listing~\ref{lst:...}`, `Equation~\eqref{eq:...}`).
