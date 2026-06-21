---
title: "Issue Report 2026-05-04"
date: 2026-05-04
tags: [issues, weekly]
status: active
---
# Issue Report

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
Exploration & Architecture

## Date:
2026-05-04

---

### Solved Issues

#### Solved Issue 1

- Original issue: Lack of clear state tracking mechanism for the LangGraph Orchestrator (Vector RAG alone causes hallucinations in topology mapping).
- What was tried: Ingested State-of-the-Art research on MAS memory management.
- Resolution / outcome: Designed and documented the Tri-Partite [[Hybrid_Memory_Architecture]] (Hierarchical Wikis, Knowledge Graphs, and Vector RAG) to explicitly separate procedural rules from topological state.

#### Solved Issue 2

- Original issue: The QoT (Quality of Transmission) estimator tool lacked any specification or architecture boundary.
- What was tried: Held a meeting to discuss the QoT-aware constraints and ingested the transcription.
- Resolution / outcome: Extracted and documented the functional requirements (GN model, SNR threshold, -18 dBm power) in `QoT_Awareness.md` and updated the `Tool_Registry.md`.

---

### Pending Issues

#### Pending Issue 1

- Issue: No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- What has already been tried: Defined the folder structure (`src/agents/`, `src/tools/`, `src/core/`, `src/services/`, `src/graph.py`).
- Result: The skeleton is ready, but no Python code has been written.
- Estimated possible solution: Begin with a minimal LangGraph `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the pipeline end-to-end.

#### Pending Issue 2

- Issue: The QoT estimator tool has not been delivered yet, and the virtual environment (digital twin) is being set up.
- What has already been tried: Secured VPN access to the university network and clarified functional specifications.
- Result: VPN is active, but we are waiting for the professor to complete the virtual environment setup to begin prototyping.
- Estimated possible solution: Follow up on the virtual environment setup status next week and integrate the simplified Python scripts once available.


#### Pending Issue 3

- Issue: I have to research how to integrate the knowledge graph and search for state of the art technologies.
- What has already been tried: The [[Hybrid_Memory_Architecture]] conceptually defines the need for a Knowledge Graph (technology-agnostic for now).
- Result: We have the concept, but no concrete graph database or library chosen.
- Estimated possible solution: Conduct research on available Graph Databases or libraries suitable for Python/LangGraph integration (e.g., Neo4j, NetworkX, Memgraph) and select the most appropriate one for the thesis prototype.

#### Pending Issue 4

- Issue: The [[Research_Plan_MultiAgentON|Research Plan]] literature review is still in progress.
- What has already been tried: Defined three deep research phases and initiated execution.
- Result: Currently, only Phase 3 (State-of-the-Art Memory Management) has been accomplished.
- Estimated possible solution: Execute the remaining research phases (Phases 1 and 2) to complete the literature review.



---

### Additional Notes

This session shifted from repository infrastructure to deep architectural design regarding memory management. The next phase must focus heavily on code prototyping in `src/` to validate these architectural decisions.
