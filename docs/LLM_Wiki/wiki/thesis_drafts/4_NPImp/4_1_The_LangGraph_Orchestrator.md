---
title: "Chapter 4 - Section 4.1: Orchestration and Network Context"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, langgraph, graphrag, testbed, orchestration]
status: draft
---

# 4.1 Orchestration and Network Context

## 4.1.1 LangGraph State Machine Architecture and State Schema

The end-to-end coordination of the seven-phase neurosymbolic pipeline is orchestrated via a directed acyclic state machine implemented in `src/core/graph.py`, leveraging the `langgraph` framework \cite{langgraph_2024}. Unlike conventional autonomous agent loops that rely on unconstrained while-loops or monolithic prompt chains, our architecture structures intent planning as an explicit, state-preserving computational graph where transitions between linguistic reasoning, symbolic solvers, and physical physics engines are deterministically governed by conditional routing edges.

### State Schema (`AgentState`)

The shared memory across all execution stages is encapsulated within `AgentState`, a typed dictionary schema defined in `src/core/state.py`. Every pipeline node operates as a pure or state-transforming function returning partial updates that LangGraph merges into the global checkpointed state. This design guarantees complete immutability of historical snapshots, facilitates modular unit testing, and ensures execution determinism. The state payload contains the active operator intent, topological context, PDDL constraints, quality of transmission (QoT) results, and historical execution traces.

### State Persistence and Atomic Checkpointing

To support asynchronous Human-in-the-Loop (HITL) engagement without thread blocking or memory loss, the orchestrator integrates an atomic state checkpointer. When a decision gate suspends execution via an interrupt, the checkpointer writes a serialized snapshot of the state indexed by a unique transaction thread identifier. The operating thread is released immediately, allowing the orchestrator to remain completely dormant until the human operator supplies clarification or approval, whereupon execution resumes from the exact saved checkpoint.

---

## 4.1.2 Pipeline-to-Node Execution Mapping

The theoretical 7-phase pipeline introduced in Chapter 3 is mapped directly to Python functions decorated as LangGraph nodes within `src/nodes/`. The orchestrator executes them sequentially, conditionally looping back based on RADG evaluations:

1. **Phase 1 (Network Context Extraction):** Executed implicitly before node processing via `Mock GraphRAG` to seed the `AgentState` with the topological context.
2. **Phase 2 (Intent Ingestion & PDDL Parsing):** Implemented by `intent_ingest_node` and `pddl_parser_node`. Translates the natural language intent into structured PDDL.
3. **Phase 3 (Semantic RADG):** Implemented by `semantic_gate_node` and `reverse_prompt_node`. Evaluates $U_{sem}$. Triggers `interrupt()` if clarification is required.
4. **Phase 4 (Symbolic Solver):** Invokes the non-neural deterministic Yen's K-Shortest Paths algorithm over the pruned topology.
5. **Phase 5 (GN-Model QoT Validation):** Implemented by `qot_validation_node`. Computes GSNR for candidate paths using the physical engine.
6. **Phase 6 (Physical RADG):** Implemented by `radg_node`. Evaluates $\text{QoT}_{valid}$. Triggers `interrupt()` if the paths are physically unfeasible.
7. **Phase 7 (Plan Synthesis):** Implemented by `plan_synthesizer_node`. Compiles the final verified paths into an auditable provisioning trace.

By structurally aligning the codebase nodes with the theoretical phases, the orchestrator guarantees a 1:1 trace between the Risk-Adaptive conceptual model and the executed software lifecycle.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 4.1 Placement:** LangGraph State Machine execution graph.
> - **Artifact Path:** `figs_NPImp/src/diagrams/langgraph_execution_flow.drawio`
> - **LaTeX Figure Reference:** `Figure~\ref{fig:langgraph_execution_flow}`
