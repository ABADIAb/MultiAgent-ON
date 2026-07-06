---
title: "Scope Pivot: Neurosymbolic Intent Orchestration"
date: 2026-07-06
tags: [architecture, scope, pivot, planning-loop, neurosymbolic, thesis]
status: active
supersedes: "[[archive/Scope_Pivot_20260621]]"
---

# Scope Pivot: From Generative Loop to Neurosymbolic Intent Orchestration

## 1. Decision Summary

On 2026-07-06, after evaluating the V3 Intent Planning Loop against the realities of token budget saturation, mathematical intent convergence, and physical hallucination risks, the thesis scope has been formally updated:

- **Previous scope (V3)**: "QoT-Informed Intent Planning for Optical Networks" — a generative loop relying on LLM-to-Pydantic parsing, naive topology insertion, and heuristic GNPy calls.
- **New scope (V4)**: **"Neurosymbolic Orchestration of Intents"** — a deterministic, structured pipeline utilizing PDDL for constraint generation, Optical GraphRAG for context compression, and Reverse Prompting for mathematically bounded Human-in-the-Loop (HITL) convergence.

## 2. Research Evidence Motivating the Pivot

### 2.1 The "Hallucinated Physics" Dilemma
LLMs are probabilistic text engines; they do not natively respect physical constraints (e.g., Stimulated Raman Scattering, Generalized SNR margins). Allowing an LLM to heuristically query a heavy simulator like GNPy to find valid paths is computationally unscalable and prone to generating structurally invalid paths.

### 2.2 Token Budget Saturation
Extracting an entire optical topology via RESTConf and placing it in a JSON string within the LLM context causes context saturation, lost tokens (lost-in-the-middle phenomenon), and massive inference costs.

### 2.3 Semantic Drift in Multi-Turn HITL
Using unstructured conversational interactions for intent refinement lacks convergence guarantees. A user's correction can lead the LLM to inadvertently drop prior constraints, creating an infinite loop of unverified plan states.

## 3. The New Neurosymbolic Pipeline (V4)

The planning intelligence has been restructured into a rigid "Sistema 1 (Generative) + Sistema 2 (Symbolic)" pipeline:

1. **Intent Ingestion + Optical RAG:** The NL request is semantically enriched with specific constraints (e.g., ITU-T standards) before LLM processing.
2. **PDDL Intent Parsing (CFG Validated):** The LLM acts purely as a translator, outputting formal Planning Domain Definition Language (PDDL) states instead of a naive Pydantic SLA matrix.
3. **Formal HITL (Reverse Prompting):** The PDDL state is translated back into natural language by an inverse model, forcing the operator to explicitly approve the exact logical constraints the system understood.
4. **Symbolic Solver + GraphRAG:** A deterministic symbolic solver extracts 3-5 valid path candidates from a locally compressed GraphRAG topology based on the PDDL constraints.
5. **QoT Validation:** Only these mathematically bounded candidates are sent to the Python GNPy port for QoT viability checks.

## 4. MVP Roadmap Constraint
Given the August 25 deadline, the MVP will utilize a **simplified Python symbolic solver** and a **mock GraphRAG** structure (e.g., Python dictionary traversals) rather than requiring heavy third-party installations like Neo4j or complex PDDL engines. This ensures a functional, verifiable prototype that modifies the simple lab testbed correctly.

## 5. Cross-References
- [[Architecture_v4]] — The updated architecture document.
- [[ProblemStatement_v4]] — The refined problem statement.
