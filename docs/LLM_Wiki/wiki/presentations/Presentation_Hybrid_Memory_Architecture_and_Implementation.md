---
title: "Presentation: Hybrid Memory Architecture and Implementation"
date: 2026-05-04
tags: [presentation, memory, architecture, langgraph, implementation]
status: active
---

# Hybrid Memory Architecture and Implementation in MultiAgentON

**Presenter:** Felipe Abadia  
**Target Audience:** Thesis Professor  
**Objective:** Validate the necessity of the Tri-Partite Hybrid Memory approach for complex Intent-Based Optical Networks (IBON) and demonstrate its concrete implementation within the project's codebase.

---

## Slide 1: The Bottleneck in Stateful Agents
* **The Problem:** Modern multi-agent systems, particularly in critical infrastructure like IBON, require strict state tracking and long-term planning.
* **The Constraint:** Standard LLM context windows degrade rapidly over long tasks and suffer from the "Lost in the Middle" phenomenon.
* **The Naive Solution:** Just throwing a Vector Database (RAG) at the problem.

> [!TIP]
> **Design Suggestion:** Keep text minimal. Use an icon showing a generic LLM "forgetting" long contexts to visualize the constraint.

---

## Slide 2: The Fallacy of "Everything is a Vector"
* **Semantic vs. Deterministic:** Explain that vector embeddings capture *semantic proximity*, not logical dependencies.
* **The IBON Example:** "If Router A fails, what happens to the optical slice X?" A vector database cannot reliably trace this graph. It might return unrelated routers with similar names.
* **Conclusion:** Pure RAG is an architectural mistake for strict state management.

> [!TIP]
> **Design Suggestion:** Contrast a vector database icon with a large red 'X' to symbolize that basic semantic search is insufficient for logical dependencies.

---

## Slide 3: The Tri-Partite Solution
* Propose the **Hybrid Memory Architecture** dividing cognition into three functional pillars:
  1. **Hierarchical Wikis**: For *Procedural Knowledge* (Rules, Personas, Skills). Deterministic and highly structured.
  2. **Knowledge Graphs**: For *State & Topology*. Technology-agnostic nodes and edges for exact multi-hop reasoning. Stores factual knowledge and relationships about the world.
  3. **Vector RAG**: For *Episodic Memory*. Pattern matching across historical errors and unstructured telecom documentation.

> [!TIP]
> **Design Suggestion:** Use a triad diagram or three columns. Assign distinct colors to each pillar (e.g., Blue for Wiki, Green for Graph, Orange for Vector) and use them consistently throughout.

---

## Slide 4: LangGraph Execution Flow
* **Visual Aid Request:** Flowchart diagram showing the LangGraph Supervisor pipeline.
* **Flow:**
  - Agent boots $\rightarrow$ Reads **Wiki** (How to act).
  - Agent receives SLA constraint $\rightarrow$ Queries/Updates **Graph** (What is the current state).
  - Agent hits an error $\rightarrow$ Queries **Vector DB** (Have we seen this before?).

> [!TIP]
> **Design Suggestion:** Include a clear flowchart showing the sequential pipeline: Boot (Wiki) → Execute (Graph) → Fallback (Vector RAG).

---

## Slide 5: Implementing the Architecture - "Screaming" Repository Structure
* **Concept Connection:** To build a Tri-Partite Hybrid Memory, the codebase itself must cleanly separate procedural knowledge (Wiki) from executable state (Graph) and integrations (Vector).
* **The Solution:** A "Screaming Architecture" where the `src/` directory screams its purpose, completely separating the memory logic from external documentation.
* **The `src/` Folder Structure:**
  - `src/agents/`: LangGraph agent definitions (Execution nodes).
  - `src/tools/`: Deterministic tools (e.g., QoT evaluation).
  - `src/core/`: Shared state, schemas, and **`src/core/wiki/`** (System procedural memory).
  - `src/services/`: External integrations (Vector DB connections).

> [!TIP]
> **Design Suggestion:** Use a side-by-side comparison. Left: The abstract memory pillars. Right: The concrete `src/` folder tree structure. Use arrows to link concepts to code.

---

## Slide 6: Summary - Memory Implementation in MultiAgentON
* **Pillar 1 (Procedural):** Hierarchical Wiki stored in **`src/core/wiki/`**, designed specifically for the agents (different from the project's documentation wiki). Agents read these immutable network rules and protocols at boot.
* **Pillar 2 (State/Topology):** The Knowledge Graph tracks network state, implemented within the LangGraph state in `src/core/` and queried by `src/agents/`.
* **Pillar 3 (Episodic):** Vector DB queries integrated via `src/services/` for fallback historical precedents.
* **Outcome:** A highly scalable, stateful agentic system mapped cleanly onto a domain-driven codebase.

> [!TIP]
> **Design Suggestion:** Use a structured summary matrix or a cohesive diagram showing how `src/core`, `src/agents`, and the Wiki interact to create the final system.
