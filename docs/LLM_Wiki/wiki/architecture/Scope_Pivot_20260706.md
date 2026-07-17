---
title: "Scope Pivot: The Journey to Neurosymbolic Intent Orchestration (V2 → V4)"
date: 2026-07-06
tags: [architecture, scope, pivot, planning-loop, neurosymbolic, thesis]
status: active
supersedes: "[[archive/Scope_Pivot_20260621]]"
---

# Scope Pivot: The Journey to Neurosymbolic Intent Orchestration (V2 → V4)

## 1. Executive Summary

This document consolidates the complete architectural evolution of the thesis from its initial V2 conception to the final V4 design. It details the two major scope pivots driven by State of the Art (SOTA) research and technical limitations discovered during development.

The progression follows:
- **V2 (Full MAS)**: End-to-end multi-agent orchestration for Day-0 to Day-N.
- **V3 (Planning Loop Focus)**: Narrowed scope to the Intent Planning phase due to SOTA saturation.
- **V4 (Neurosymbolic Pipeline)**: Introduction of deterministic PDDL, GraphRAG, and formal Reverse Prompting to solve physical hallucinations and token saturation.

## 2. First Pivot: V2 to V3 (SOTA-Driven Scope Reduction)

**Date:** 2026-06-21
**Transition:** From "Agentic AI for Joint Routing and Compute Scheduling" (V2) to "QoT-Informed Intent Planning" (V3).

### 2.1 The Problem
In early 2026, the architecture aimed to be a full Multi-Agent System (MAS) covering the entire lifecycle of optical networks. However, a rigorous SOTA analysis revealed that this broad framing was no longer novel:
- **Confucius (Meta, SIGCOMM 2025):** Validated multi-agent orchestration at hyperscale (60+ applications, 4k+ users, 31.62M messages), proving that MAS architectures in networking are solved at scale.
- **AutoLight (SJTU, ECOC 2025):** Demonstrated an L4 autonomous optical network using a LangGraph-based hierarchical MAS, proving that MAS is already applied successfully to the optical domain.

### 2.2 The V3 Solution
Since full MAS was no longer a novel contribution, the thesis scope was narrowed specifically to the **Planning Phase**. The system would no longer provision network paths directly (no RESTConf writes). Instead, it focused on the novel intersection of:
1. Natural Language Intent Parsing.
2. Multi-turn Human-in-the-Loop (HITL) refinement.
3. [[QoT_Awareness|QoT-aware]] path evaluation.

The output shifted from a network configuration command to a validated **Planning Report** containing candidate paths and SLA trade-offs.

## 3. Second Pivot: V3 to V4 (Technical Feasibility & Hallucination)

**Date:** 2026-07-06
**Transition:** From a "Generative Planning Loop" (V3) to a "Neurosymbolic Intent Orchestration Pipeline" (V4).

### 3.1 The Problem
While V3 successfully isolated the planning phase, prototyping revealed severe bottlenecks inherent to purely generative LLM pipelines:
- **Token Budget Saturation:** Extracting an entire optical topology via RESTConf and placing it in a JSON string within the LLM context caused context saturation, the lost-in-the-middle phenomenon, and massive inference costs.
- **The "Hallucinated Physics" Dilemma:** LLMs are probabilistic text engines; they do not natively respect physical constraints (e.g., Stimulated Raman Scattering, Generalized SNR margins). Allowing an LLM to heuristically query a heavy simulator like GNPy to find valid paths is computationally unscalable and prone to generating structurally invalid paths.
- **Semantic Drift in Multi-Turn HITL:** Using unstructured conversational interactions for intent refinement lacked convergence guarantees. A user's correction could lead the LLM to inadvertently drop prior constraints, creating an infinite loop of unverified plan states.

### 3.2 The V4 Solution (Neurosymbolic Pipeline)
The planning intelligence was restructured into a rigid "Sistema 1 (Generative) + Sistema 2 (Symbolic)" pipeline to enforce strict boundaries between reasoning and calculation:
1. **Intent Ingestion + Optical RAG:** The NL request is semantically enriched with specific constraints (e.g., ITU-T standards) before LLM processing.
2. **PDDL Intent Parsing (CFG Validated):** The LLM acts purely as a translator, outputting formal Planning Domain Definition Language (PDDL) states instead of a naive Pydantic SLA matrix.
3. **Formal HITL (Reverse Prompting):** The PDDL state is translated back into natural language by an inverse model, forcing the operator to explicitly approve the exact logical constraints the system understood, thereby mathematically bounding convergence.
4. **Symbolic Solver + GraphRAG:** A deterministic symbolic solver extracts 3-5 valid path candidates from a locally compressed GraphRAG topology based on the PDDL constraints.
5. **QoT Validation:** Only these mathematically bounded candidates are sent to the Python GNPy port for precise physical-layer QoT viability checks.

## 4. Novelty and Added Value (Unique Selling Points)

The pivot to V4 establishes a highly focused, academically novel contribution that avoids competing with hyperscale MAS frameworks (like Meta's Confucius) while addressing critical gaps in current optical AI research (like SJTU's AutoLight and PoliMi's LoRA models):

1. **Formal HITL Convergence via Reverse Prompting:** While other systems use basic chatbot loops that suffer from "semantic drift" (dropping constraints across turns), V4 uses model inversion to translate the generated PDDL back to natural language. This mathematically bounds the operator's approval to the exact logical constraints the system will execute.
2. **Eradication of "Hallucinated Physics":** By enforcing a strict Neurosymbolic (NeSy) separation, the LLM is restricted to linguistics (Intent → PDDL). It is completely blocked from guessing physical parameters. A deterministic Symbolic Solver and GNPy handle the physics, guaranteeing 100% physically viable route proposals.
3. **Optical GraphRAG for Token Efficiency:** Serializing RESTConf topology JSONs causes massive LLM attention degradation (the "lost-in-the-middle" problem). V4's use of a k-hop compressed topological GraphRAG provides highly efficient, localized network context, solving the context window bottleneck for optical networks.
4. **Computational Pre-Filtering:** Directly querying GNPy via LLM heuristics is computationally unscalable. V4 introduces a symbolic constraint solver that whitelists only structurally valid paths *before* heavy physical simulation, drastically reducing the computational cost of the planning loop.

## 5. MVP Roadmap Constraint

Given the August 25 deadline, the V4 MVP will utilize a **simplified Python symbolic solver** and a **mock GraphRAG** structure (e.g., Python dictionary traversals) rather than requiring heavy third-party installations like Neo4j or complex PDDL engines. This ensures a functional, verifiable prototype that modifies the simple lab testbed correctly.

## 6. Cross-References

- [[Architecture_v4]] — The final active architecture document.
- [[ProblemStatement_v4]] — The refined thesis problem definition.
- [[archive/Scope_Pivot_20260621]] — Original V2 to V3 pivot document.
- [[archive/Architecture_v3]] — Archived V3 architecture.
- [[archive/Architecture_v2]] — Archived V2 architecture.
