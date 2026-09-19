---
title: "Chapter 4 - Section 4.2: The Semantic Engine"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, pddl, cfg-ast, reverse-prompting, semantic-gate]
status: draft
---

# 4.2 The Semantic Engine

## 4.2.1 Natural Language Intent Ingestion and Structured Extraction

The initial phase of the pipeline bridges informal operator communication with structured computational planning. Implemented in `src/nodes/intent_ingest.py`, the ingestion node accepts the raw operator prompt string alongside the active network topology snapshot.

Rather than immediately translating unconstrained language into symbolic execution code, the module executes a two-step parsing routine:
1. **Dynamic Context Injection:** The localized subtopology context string produced by the Mock GraphRAG extractor (Section 4.1.3) is injected into the LLM system prompt, grounding the language model in valid node identifiers and active fiber links.
2. **Constrained Schema Extraction:** The LLM is queried using structured outputs (enforced via Pydantic schema validation) to produce a structured summary of the intent, encapsulating endpoints, required bandwidth, and avoidance constraints.

### Prevention of Lossy Numerical Abstraction

Early iterations of the ingestion module exhibited a critical failure mode: when downstream verification modules evaluated intent fidelity against the structured summary rather than the verbatim operator message, subtle constraints and domain qualifiers were lost. This lossy numerical abstraction generated artificial semantic divergence, triggering unnecessary operator clarification interruptions.

To prevent this distortion, the pipeline enforces the **Verbatim Intent Preservation Invariant**: the ingestion node instantiates the state variable tracking the active intent using the exact, unmodified operator input string. The structured summary serves exclusively to guide downstream prompt templating and initialize subtopology scoping, while the raw text remains the single immutable reference for semantic agreement scoring throughout the pipeline lifecycle.

---

## 4.2.2 Multi-Turn Intent Reconciliation and Disambiguation Reasoning

When an intent triggers an operational interruption, the operator submits corrective feedback. In multi-turn conversational architectures, language models frequently conflate prior constraints with new instructions, producing contaminated intent states (e.g., retaining a previously requested avoidance of a node when the operator explicitly requested a completely new route). This phenomenon is known as ghost constraint leakage.

To eliminate ghost constraint contamination, `src/nodes/intent_reconciler.py` implements a formal intent reconciliation engine powered by a structured classification model. The reconciler executes a deterministic taxonomy:
- **Full Replacement:** Triggered when the operator explicitly aborts the previous request, provides a self-contained routing statement with a new endpoint pair, or supplies complete instructions following an incomplete turn. Under this branch, all prior endpoints, exclusions, and numerical thresholds are discarded, resetting the state to the new intent.
- **Partial Update:** Triggered when the operator adjusts, relaxes, or removes specific constraints while maintaining the general request context. The module merges the modification into the existing constraint set.

Furthermore, if the reconciler identifies modified endpoint nodes, it dynamically invokes the GraphRAG extractor to rescope the subtopology to the new geographic region, preventing downstream routing failures caused by stale topological context.

---

## 4.2.3 Context-Free Grammar (CFG) AST PDDL Validation

To strictly enforce neurosymbolic separation, Phase 2 (`src/nodes/pddl_parser.py`) prompts the model to act as a pure linguistic translator, mapping the natural language intent into a simplified Planning Domain Definition Language (PDDL) problem specification.

Because autoregressive models can generate syntactically corrupted expressions or unbalanced parentheses, accepting raw PDDL into the symbolic solver introduces catastrophic control-plane failure risks. Rather than relying on fragile regular expression heuristics, `src/core/pddl_validator.py` implements a rigorous Context-Free Grammar (CFG) parser based on S-expression abstract syntax trees (AST).

The parser operates through two formal software stages:
1. **Tokenization and Nesting Depth Tracking:** The raw string is stripped of comments and scanned character-by-character. The lexer tracks parenthesis depth. An invariant condition is enforced: the depth must never drop below zero, and must return to exactly zero at string termination.
2. **Recursive AST Builder:** Lexical tokens are parsed into nested Python lists representing the S-expression tree. The top-level expression must conform to the formal domain structure, extracting mandatory sections (domain, objects, init, goal).

Within the goal section, the parser isolates logical conjunctions and applies formal type- and arity-checking against the optical routing domain grammar defined in Section 3.2.2. If any parenthesis fails to balance or a predicate violates the grammar, the parser returns a detailed list of syntax violations, immediately halting downstream execution and flagging a structural failure.

---

## 4.2.4 Automated Reverse Prompting and Semantic Agreement Scoring

To prevent semantic drift while eliminating human interruption for unambiguous intents, Phase 3 implements an automated Reverse Prompting protocol coupled to the Semantic RADG logic (`src/nodes/reverse_prompt.py`, `src/nodes/semantic_gate_node.py`).

### Automated PDDL-to-NL Reconstruction

Immediately following PDDL parsing, the pipeline invokes an automated reconstruction turn involving **zero human intervention**. A secondary prompt presents the generated PDDL string back to the language model, instructing it to translate the formal symbolic constraints back into natural language.

To ensure the reconstruction reflects only genuine routing constraints without prompt contamination, a filtering utility strips verbose topological connectivity predicates prior to reconstruction, presenting only the operational goal constraints.

### Semantic Agreement Evaluation

Next, the reconstructed intent and the original operator intent are supplied to an independent LLM Agreement Judge. The judge evaluates the semantic correspondence between the two statements and outputs an agreement score, from which the semantic divergence is derived.

The software gate then evaluates the composite Semantic Uncertainty ($U_{sem}$) against the operator-defined tolerance threshold, implementing the decision matrix established in Section 3.3.4:
- **Autonomous Pass:** If structural parsing succeeds and semantic divergence is low, the pipeline proceeds directly to the Symbolic Solver with **zero human interruptions**.
- **Fail-Fast Interruption:** If structural parsing fails or semantic divergence exceeds the threshold, execution suspends via LangGraph's interrupt primitive, presenting the reconstructed intent, the identified discrepancies, and the uncertainty score to the human operator for disambiguation.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 4.2 Placement:** Flowchart illustrating the Two-Layer Semantic Engine: showing intent ingestion, structural AST verification, automated PDDL-to-NL reconstruction, and the final Semantic RADG decision routing.
> - **Artifact Path:** `figs_NPImp/src/diagrams/semantic_engine.drawio`
> - **LaTeX Figure Reference:** `Figure~\ref{fig:semantic_engine}`
