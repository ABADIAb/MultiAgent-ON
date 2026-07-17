---
title: "MVP Roadmap: Sprints and Experiments"
date: 2026-07-06
tags: [experiments, roadmap, sprints, timeline, neurosymbolic, mvp]
status: active
supersedes: "[[literature/recommendations]]"
---

# MVP Roadmap: Sprints and Experiments (Target: August 25)

This document outlines the detailed execution plan, timeline, and structured experiments to build the **Neurosymbolic Intent Orchestration MVP** (Architecture V4). The roadmap is focused on a minimal, fully functional system that connects to the laboratory testbed by **August 25, 2026**, allowing for a code freeze followed by thesis writing until **September 20, 2026**.

---

## Gantt / Sprint Timeline Overview

| Phase | Timeline | Primary Objective |
|---|---|---|
| **Sprint 1: Foundation & Tooling** | July 06 - July 18 | Infrastructure verification, Python QoT port, and SSH testbed hook. |
| **Sprint 2: Neurosymbolic Logic** | July 19 - August 01 | PDDL parser, Reverse Prompting HITL logic, and Symbolic Solver. |
| **Sprint 3: Orchestrator Integration** | August 02 - August 15 | Compile the full LangGraph pipeline with state persistence. |
| **Sprint 4: Validation & Polish** | August 16 - August 25 | Live testbed execution, end-to-end testing, and error handling. |
| **Post-MVP: Writing Phase** | August 26 - September 20 | 100% Code Freeze. Focus on thesis writing. |

---

## Sprint 1: Foundation & Tooling (July 06 - July 18)

### ~~Exp 1.0: LLM Connection Verification~~ ✅ (Completado)
- **Objective:** ~~Verify robust connection with the Kimi LLM endpoint provided by the professor.~~
- **Action:** ~~Implement a small validation script using `langchain_openai.ChatOpenAI` configured with `KIMI_API_KEY` and `KIMI_BASE_URL` from the local `.env`. Ensure structured output parsing works.~~
- **Deliverable:** ~~Verified connection and structured output test script.~~

### ~~Exp 1.1: QoT C++ to Python Port~~ ✅ (Completado)
- **Objective:** ~~Translate the core physics equations from the C++ simulator into pure Python.~~
- **Action:** ~~Convert functions calculating Signal-to-Noise Ratio (SNR) and receiver power constraints (e.g., the -18 dBm threshold) into a modular Python module. Ensure exact numerical parity with C++ outputs.~~
- **Deliverable:** ~~`src/core/qot_calculator.py` with passing unit tests.~~

### ~~Exp 1.2: QoT Tool Wrapping~~ ✅ (Completado)
- **Objective:** ~~Expose the Python QoT calculator as a LangChain `@tool` compatible with the agent framework.~~
- **Action:** ~~Wrap the calculator in `src/tools/qot_tool.py`. It should take path coordinates and return GSNR and receiver power feasibility status.~~
- **Deliverable:** ~~Exposable `qot_check` tool in the MultiAgentON tool registry.~~

### Exp 1.3: SSH Testbed Connectivity Hook
- **Objective:** Establish the integration channel with the physical laboratory testbed.
- **Action:** Write a secure Python adapter (using `paramiko` or `httpx` depending on the testbed's API/NBI) to fetch the physical topology and push configuration changes.
- **Deliverable:** `src/services/testbed_ssh_client.py` capable of sending mock path allocations.

---

## Sprint 2: Neurosymbolic Node Development (July 19 - August 01)

### ~~Exp 2.1: PDDL Intent Parser~~ ✅ (Completado)
- **Objective:** ~~Translate natural language operator intents into formal PDDL (Planning Domain Definition Language) constraint strings.~~
- **Action:** ~~Prompt engineer the Kimi LLM to output a clean PDDL domain/problem representation from natural language intents. Implement a Context-Free Grammar (CFG) regex validator in Python to ensure structural syntax correctness.~~
- **Deliverable:** ~~`src/agents/pddl_parser.py` and grammar validator.~~

### ~~Exp 2.2: Reverse Prompting HITL Node~~ ✅ (Completado)
- **Objective:** ~~Enforce intent convergence and prevent semantic drift using Reverse Prompting.~~
- **Action:** ~~Create a LangGraph node that reads the PDDL state, uses an inverse LLM prompt to reconstruct it back into plain English (e.g., *"I understand you want to route from Milan to Rome avoiding links with active aging..."*), and uses LangGraph's `interrupt()` to await human approval.~~
- **Deliverable:** ~~Interactive HITL node in `src/agents/reverse_prompt.py`.~~

### Exp 2.3: Symbolic Solver & Mock GraphRAG
- **Objective:** Filter topological paths deterministically before executing physical simulations, preventing token saturation.
- **Action:** 
  1. Build a local Python dictionary representing the network topology (Mock GraphRAG) to dynamically extract only the $k$-hop neighborhood.
  2. Write a lightweight symbolic routing function (e.g., Dijkstra or Yen's K-Shortest Paths with custom PDDL constraint validation) to extract 3 to 5 candidate paths.
- **Deliverable:** `src/core/symbolic_solver.py` and `src/core/mock_graphrag.py`.

---

## Sprint 3: Orchestrator Integration (August 02 - August 15)

### Exp 3.0: LangGraph State Pipeline Assembly
- **Objective:** Connect the generative and symbolic modules into a cohesive StateGraph.
- **Action:** Wire all components together in `src/core/graph.py`:
  `Ingest (Intent) -> RAG -> LLM (PDDL) -> Reverse Prompting (HITL interrupt) -> Symbolic Solver -> Python QoT Tool -> Synthesizer -> Testbed Push`.
- Configure the LangGraph Memory Checkpointer to ensure state persistence across human interruptions.
- **Deliverable:** Fully compiled `StateGraph` in `src/core/graph.py`.

---

## Sprint 4: Validation & Polish (August 16 - August 25)

### Exp 4.0: Live E2E Lab Testbed Execution
- **Objective:** Validate the complete orchestrator against the physical laboratory nodes.
- **Action:** Execute end-to-end intent queries (e.g., routing under SNR constraints, link failures). Verify that:
  1. The LLM parses the intent correctly into PDDL.
  2. The reverse prompt correctly captures constraints.
  3. The symbolic solver filters paths.
  4. The configurations are successfully pushed to the testbed and physically provisioned.
- **Deliverable:** Working MVP demo recording, execution logs, and final benchmark reports.

---

## Post-MVP: Thesis Writing (August 26 - September 20)

- **Code Freeze:** Zero code changes to protect system stability.
- **Thesis Authoring:** Dedicate 100% of effort to writing the thesis document, focusing on:
  - The limitations of purely generative models in optical networking.
  - The math and design behind the Neurosymbolic Orchestration V4 architecture.
  - The empirical results of the sprints (context token savings, GNPy call reductions, intent convergence speed).
