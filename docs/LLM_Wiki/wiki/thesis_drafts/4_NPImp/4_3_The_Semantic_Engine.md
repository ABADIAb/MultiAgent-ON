---
title: "Chapter 4 - Section 4.2: The Semantic Engine"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, pddl, cfg-ast, reverse-prompting, semantic-gate]
status: draft
---

# 4.3 The Semantic Engine

The Semantic Engine comprises Phases 2 and 3 of the neurosymbolic pipeline, embodying the software realization of the linguistic reasoning domain and the first decision barrier (Gate 1: Semantic RADG) established in Chapter~\ref{chap:system_model} (Figure~\ref{fig:conceptual_framework}). It coordinates intent ingestion, multi-turn disambiguation, Context-Free Grammar (CFG) AST structural verification, and automated closed-loop Reverse Prompting. Intent processing is executed in two consecutive stages: Layer 1 validates the structural syntax of the translated PDDL through a deterministic AST parser to guarantee well-formed S-expressions; Layer 2 verifies semantic alignment by reconstructing natural language from the validated PDDL and scoring semantic divergence ($d_{sem}$) against the original intent via an independent judge. The outputs of both layers converge at the Semantic RADG decision multiplexer, which either routes execution autonomously forward into the symbolic solver (Phase 4) or triggers an asynchronous Human-in-the-Loop (HITL) interrupt (Phase 3b) for operator clarification.

## 4.3.1 Natural Language Intent Ingestion and Structured Extraction

Phase 2 begins by ingesting the informal operator communication. The ingestion module accepts the raw operator prompt string alongside the active network topology snapshot.

The module executes a two-step parsing routine:
1. **Dynamic Context Injection:** The localized subtopology context string produced by the Mock GraphRAG extractor (Section~\ref{subsec:graphrag_extraction}) is injected into the LLM system prompt, grounding the language model in valid node identifiers and active fiber links.
2. **Constrained Schema Extraction:** The LLM is queried using structured outputs (enforced via Pydantic schema validation) to produce a structured summary of the intent, encapsulating endpoints, required bandwidth, and avoidance constraints.

### Prevention of Lossy Numerical Abstraction

When downstream verification modules evaluate intent fidelity against a structured summary rather than the verbatim operator message, subtle constraints and domain qualifiers are susceptible to loss. This generates artificial semantic divergence, triggering unnecessary operator interruptions.

To prevent this distortion, the ingestion module instantiates the `active_intent` state variable using the exact, unmodified operator input string. The structured summary serves to guide downstream prompt templating and initialize subtopology scoping, while the raw text remains the reference for semantic agreement scoring throughout the pipeline lifecycle.

---

## 4.3.2 Multi-Turn Intent Reconciliation and Disambiguation Reasoning

When an intent triggers an operational interruption, the operator submits corrective feedback. In multi-turn conversational architectures, language models frequently mix prior constraints with new instructions, producing contaminated intent states (e.g., retaining a previously requested avoidance of a node when the operator explicitly requested a new route). This phenomenon is known as ghost constraint leakage.

To eliminate ghost constraint contamination, the pipeline implements a formal intent reconciliation engine powered by a structured classification model. The reconciler evaluates the feedback according to two resolution paths:
- **Full Replacement:** Triggered when the operator explicitly aborts the previous request, provides a self-contained routing statement with a new endpoint pair, or supplies complete instructions following an incomplete turn. Under this branch, all prior endpoints, exclusions, and numerical thresholds are discarded, resetting the state to the new intent.
- **Partial Update:** Triggered when the operator adjusts, relaxes, or removes specific constraints while maintaining the general request context. The module merges the modification into the existing constraint set.

If the reconciler identifies modified endpoint nodes, it dynamically invokes the GraphRAG extractor to rescope the subtopology to the new geographic region, preventing downstream routing failures caused by stale topological context.

---

## 4.3.3 Context-Free Grammar (CFG) AST PDDL Validation

To maintain neurosymbolic separation, the parser module in Phase 2 prompts the model to act as a linguistic translator, mapping the natural language intent into a simplified Planning Domain Definition Language (PDDL) problem specification.

Because autoregressive models can generate syntactically corrupted expressions or unbalanced parentheses, accepting raw PDDL into the symbolic solver introduces operational risks. Following the two-layer validation hierarchy of Gate 1 (Figure~\ref{fig:conceptual_framework}), the generated PDDL constraint specification is immediately intercepted by a deterministic Context-Free Grammar (CFG) parser based on S-expression abstract syntax trees (AST) to verify structural integrity before any semantic evaluation occurs.

The parser operates through two formal software stages:
1. **Tokenization and Nesting Depth Tracking:** The raw string is stripped of comments and scanned character-by-character. The lexer tracks parenthesis depth. An invariant condition is established: the depth must never drop below zero, and must return to exactly zero at string termination.
2. **Recursive AST Builder:** Lexical tokens are parsed into nested Python lists representing the S-expression tree. The top-level expression must conform to the formal domain structure, extracting mandatory sections (domain, objects, init, goal).

Within the goal section, the parser isolates logical conjunctions and applies formal type- and arity-checking against the optical routing domain grammar defined in Section~\ref{subsec:pddl_formalization} and Section~\ref{subsec:cfg_validation}. If any parenthesis fails to balance or a predicate violates the grammar, the parser returns a detailed list of syntax violations and flags a structural failure ($v_{struct} = 0$), preventing further execution along the current trace.

---

## 4.3.4 Automated Reverse Prompting and Semantic Agreement Scoring

To prevent semantic drift, Phase 3 implements an automated Reverse Prompting protocol, realizing the closed-loop validation contract of Phase 3a. Following structural confirmation ($v_{struct} = 1$), execution enters Layer 2 semantic evaluation, where the PDDL specification is audited for linguistic fidelity without human involvement.

### Automated PDDL-to-NL Reconstruction

Immediately following PDDL parsing, the pipeline invokes an automated reconstruction turn involving **zero human intervention**. As designed in the closed-loop architecture, a secondary prompt presents the generated PDDL goal string back to the language model, instructing it to translate the formal symbolic constraints back into natural language.

To ensure the reconstruction reflects only genuine routing constraints without prompt contamination, a filtering utility removes verbose topological statements prior to reconstruction, presenting only the operational goal constraints.

### Semantic Agreement Evaluation

Next, the reconstructed intent and the original operator intent are supplied to an independent LLM Agreement Judge. The judge evaluates the semantic correspondence between the two statements and outputs an agreement score, from which the semantic divergence $d_{sem}$ is derived (Equation~\eqref{eq:d_sem}).

## 4.3.5 Semantic RADG Execution

At the Gate 1 decision point (Figure~\ref{fig:conceptual_framework}), the software gate evaluates the overall Semantic Uncertainty ($U_{sem}$) against the operator-defined tolerance threshold, implementing the decision function established in Section~\ref{subsec:radg_formulation} (Equation~\eqref{eq:radg_decision}):
- **Branch A (Autonomous Pass):** If structural parsing succeeds ($v_{struct} = 1$) and semantic divergence is low ($d_{sem} \le \tau_{sem}$), the intent is classified into Zone I (Auto-Approve / Safe) of the RADG decision space (Figure~\ref{fig:radg_decision_space}), and the pipeline proceeds directly to the Symbolic Solver with **zero human interruptions**.
- **Branch B (Fail-Fast Interruption):** If structural parsing fails ($v_{struct} = 0$) or semantic divergence exceeds the threshold ($d_{sem} > \tau_{sem}$), execution falls into Zone III (Clarify) and suspends via an interrupt mechanism, presenting the reconstructed intent, the identified discrepancies, and the uncertainty score to the human operator for disambiguation.

Once the intent passes the Semantic RADG ($U_{sem} \le \tau_{sem}$), execution transitions to the physical-layer pipeline. Section~\ref{sec:physical_engine} details the Symbolic Solver, the GN-model physics calculator, and Physical RADG execution.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure Alignment:** Section 4.3 maps directly to Phases 2 & 3 and Gate 1 of `Figure~\ref{fig:conceptual_framework}` (Chapter 3). No redundant semantic engine figure is needed in this section.
