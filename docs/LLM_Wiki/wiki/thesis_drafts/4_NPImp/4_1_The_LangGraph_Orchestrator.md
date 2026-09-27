---
title: "Chapter 4 - Section 4.1: Orchestration and Network Context"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, langgraph, graphrag, testbed, orchestration]
status: draft
---

# 4.1 Orchestration and Network Context

This chapter details the software implementation of the system model and decision gates from Chapter~\ref{chap:system_model}. It describes the LangGraph state machine, network context extraction, the semantic and physical engines, and the testbed verification.

## 4.1.1 LangGraph State Machine Architecture and State Schema

The end-to-end coordination of the seven-phase neurosymbolic pipeline is orchestrated via a directed acyclic state machine using the `langgraph` framework \cite{langgraph_2024}. The LangGraph state machine is the direct 1:1 software realization of the conceptual framework established in Chapter~\ref{chap:system_model} (Figure~\ref{fig:conceptual_framework}). This architecture structures intent planning as a state-preserving computational graph where transitions between linguistic reasoning, symbolic solvers, and physical engines are directed by conditional routing edges.

The state machine coordinates the seven functional phases as Python nodes interconnected by forward state transitions and conditional feedback loops. The pipeline execution flow incorporates two primary decision checkpoints—the Semantic RADG after Phase 3 and the Physical RADG after Phase 6 (corresponding to Gate 1 and Gate 2 in Figure~\ref{fig:conceptual_framework}). At each gate, conditional routing edges determine whether execution advances autonomously or triggers an asynchronous interrupt (`interrupt()`) for human-in-the-loop intervention. When an interrupt is triggered, the active thread serializes its state into the checkpointer and establishes a feedback path to route refined parameters back to Phase 2 for re-parsing.

### State Schema (`AgentState`)

The shared memory across all execution stages is managed via `AgentState`, a typed dictionary schema directly implementing the mathematical state tuple $\mathcal{S}_{state}$ formalized in Section~\ref{subsec:state_representation}. Every pipeline node operates as a state-transforming function returning partial updates that LangGraph merges into the global checkpointed state. This design maintains historical snapshots, facilitates modular unit testing, and ensures execution determinism. The state payload contains the active operator intent, topological context, PDDL constraints, quality of transmission (QoT) results, and historical execution traces.

### State Persistence and Checkpointing

To support asynchronous Human-in-the-Loop (HITL) engagement without thread blocking, the orchestrator integrates a state preservation mechanism. When a decision gate suspends execution via an interrupt, the checkpointer writes a serialized snapshot of the state indexed by a unique thread identifier. The operating thread is released immediately, allowing the orchestrator to remain paused until the human operator supplies clarification or approval. After intervention, execution resumes from the saved checkpoint.

---

## 4.1.2 Pipeline-to-Node Execution Mapping

The 7-phase pipeline introduced in Chapter~\ref{chap:system_model} is mapped directly to Python functions decorated as LangGraph nodes. Following the sequential progression in Figure~\ref{fig:conceptual_framework}, each theoretical phase corresponds to an orchestrated node with explicit operational boundaries:

1. **Phase 1 (Intent Ingestion & Topological Scoping):** Ingests the raw operator intent and seeds `AgentState` with the scoped $k$-hop subtopology extracted from the active network state (detailed in Section~\ref{sec:network_context}).
2. **Phase 2 (Intent Ingestion & PDDL Parsing):** Receives the enriched intent and invokes the translation LLM, compiling operational requirements into formal PDDL goal predicates. This node also serves as the re-entry target whenever downstream gates trigger refinement loops.
3. **Phase 3 (Semantic RADG):** Executes the two-layer semantic validation check (Gate 1). If $U_{sem} \le \tau_{sem}$, execution transitions autonomously to Phase 4; if $U_{sem} > \tau_{sem}$, the graph halts at the Phase 3b checkpoint for operator clarification.
4. **Phase 4 (Symbolic Solver):** Receives verified PDDL constraints and executes the non-neural deterministic Yen's K-Shortest Paths algorithm over the pruned topology context.
5. **Phase 5 (GN-Model QoT Validation):** Computes exact GSNR and power metrics for each candidate path using the deterministic physical engine.
6. **Phase 6 (Physical RADG):** Evaluates physical transmission feasibility ($\text{QoT}_{valid}$, Gate 2). If valid paths exist ($\text{QoT}_{valid} = 1$), execution proceeds to Phase 7; otherwise, the node halts at the Phase 6 interrupt for parameter relaxation, routing feedback back to Phase 2.
7. **Phase 7 (Plan Synthesis):** Compiles the verified routing paths, physical telemetry, and audit logs into an auditable provisioning trace.

By structurally aligning the codebase modules with the theoretical phases, the orchestrator provides a direct trace between the Risk-Adaptive conceptual model and the software execution. To ground the state machine in physical network reality, Section~\ref{sec:network_context} introduces the optical transport abstraction and the Mock GraphRAG topological scoping engine.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure Alignment:** Section 4.1 maps directly to `Figure~\ref{fig:conceptual_framework}` (Chapter 3). No redundant state machine figure is needed in this section.
