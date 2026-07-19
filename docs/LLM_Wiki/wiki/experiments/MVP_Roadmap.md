---
title: "MVP Roadmap: Sprints and Experiments"
date: 2026-07-17
tags: [experiments, roadmap, sprints, timeline, neurosymbolic, risk-adaptive, radg, evaluation, mvp]
status: active
supersedes: "[[literature/recommendations]]"
---

# MVP Roadmap: Sprints and Experiments (Target: August 25)

This document outlines the execution plan, timeline, and structured experiments to build the **Risk-Adaptive Neurosymbolic Intent Planning MVP** (Architecture V5). The roadmap targets a minimal, fully functional system that connects to the laboratory testbed by **August 25, 2026**, followed by a code freeze and thesis writing until **September 20, 2026**.

The V5 evolution (see [[Scope_Pivot_20260706]]) adds two critical deliverables beyond V4: the **Risk-Adaptive Decision Gate (RADG)** and a **formal baseline evaluation** with defined metrics.

---

## Gantt / Sprint Timeline Overview

| Phase | Timeline | Primary Objective |
|---|---|---|
| **Sprint 1: Foundation & Tooling** | July 06 – July 18 | Infrastructure verification, Python QoT port, and SSH testbed hook. |
| **Sprint 2: Neurosymbolic Logic** | July 19 – August 01 | PDDL parser, Reverse Prompting HITL logic, Symbolic Solver, and Mock GraphRAG. |
| **Sprint 3: RADG & Orchestrator Integration** | August 02 – August 15 | Risk-Adaptive Decision Gate, full LangGraph pipeline assembly, state persistence. |
| **Sprint 4: Evaluation & Polish** | August 16 – August 25 | Baseline comparison, test corpus execution, live testbed validation, metrics collection. |
| **Post-MVP: Writing Phase** | August 26 – September 20 | 100% Code Freeze. Thesis writing. |

---

## Sprint 1: Foundation & Tooling (July 06 – July 18)

### ~~Exp 1.0: LLM Connection Verification~~ ✅ (Completed)
- **Objective:** ~~Verify robust connection with the Kimi LLM endpoint provided by the professor.~~
- **Deliverable:** ~~Verified connection and structured output test script.~~

### ~~Exp 1.1: QoT C++ to Python Port~~ ✅ (Completed)
- **Objective:** ~~Translate the core physics equations from the C++ simulator into pure Python.~~
- **Deliverable:** ~~`src/core/qot_calculator.py` with passing unit tests.~~

### ~~Exp 1.2: QoT Tool Wrapping~~ ✅ (Completed)
- **Objective:** ~~Expose the Python QoT calculator as a LangChain `@tool` compatible with the agent framework.~~
- **Deliverable:** ~~Exposable `qot_check` tool in the MultiAgentON tool registry.~~

### Exp 1.3: SSH Testbed Connectivity Hook
- **Objective:** Establish the integration channel with the physical laboratory testbed.
- **Action:** Write a secure Python adapter (using `paramiko` or `httpx` depending on the testbed's API/NBI) to fetch the physical topology and push configuration changes.
- **Deliverable:** `src/services/testbed_ssh_client.py` capable of sending mock path allocations.

---

## Sprint 2: Neurosymbolic Node Development (July 19 – August 01)

### ~~Exp 2.1: PDDL Intent Parser~~ ✅ (Completed)
- **Objective:** ~~Translate natural language operator intents into formal PDDL constraint strings.~~
- **Deliverable:** ~~`src/agents/pddl_parser.py` and grammar validator.~~

### ~~Exp 2.2: Reverse Prompting HITL Node~~ ✅ (Completed)
- **Objective:** ~~Enforce intent convergence and prevent semantic drift using Reverse Prompting.~~
- **Deliverable:** ~~Interactive HITL node in `src/agents/reverse_prompt.py`.~~

### Exp 2.3: Symbolic Solver & Mock GraphRAG
- **Objective:** Filter topological paths deterministically before executing physical simulations, preventing token saturation.
- **Action:**
  1. Build a local Python dictionary representing the network topology (Mock GraphRAG) to dynamically extract only the $k$-hop neighborhood.
  2. Write a lightweight symbolic routing function (e.g., Dijkstra or Yen's K-Shortest Paths with custom PDDL constraint validation) to extract 3 to 5 candidate paths.
- **Deliverable:** `src/core/symbolic_solver.py` and `src/core/mock_graphrag.py`.

---

## Sprint 3: RADG & Orchestrator Integration (August 02 – August 15)

### Exp 3.0: LangGraph State Pipeline Assembly
- **Objective:** Connect all generative and symbolic modules into a cohesive, fail-fast StateGraph.
- **Action:** Wire all components together in `src/core/graph.py`:
  `Ingest → RAG → PDDL → Semantic Gate (U_sem) → [HITL if needed] → Symbolic Solver → QoT Tool → Physical Gate (R_qot) → Synthesizer → Testbed Push`.
- Configure the LangGraph Memory Checkpointer to ensure state persistence across human interruptions.
- **Deliverable:** Fully compiled `StateGraph` in `src/core/graph.py`.

### Exp 3.1: Two-Stage Risk-Adaptive Gates
- **Objective:** Implement the pre-deployment decision mechanism that sequentially evaluates semantic uncertainty and QoT risk margin.
- **Action:**
  1. **Semantic Gate ($U_{sem}$):**
     - Evaluates Layer 1 (Structural CFG) and Layer 2 (Semantic Embedding).
     - If $U_{sem}$ is high, triggers "Clarify" to prompt the operator for missing data.
  2. **Physical Risk Gate:**
     - Binary evaluation: $\text{GSNR}_{computed} \ge \text{GSNR}_{threshold}$.
     - Routes to `Auto-Approve` (Valid) or `Suggest Replan` via HITL (Invalid).
  3. **Integration:** Implemented as two separate LangGraph conditional routing nodes in `src/core/radg.py`.
- **Deliverable:** `src/core/radg.py` containing both decision gate logics.

### Exp 3.2: Early Conditional HITL Routing
- **Objective:** Modify the LangGraph to make Reverse Prompting an early conditional branch — invoked only when the Semantic Gate detects ambiguity.
- **Action:**
  1. The Reverse Prompting node (`src/agents/reverse_prompt.py`) identifies missing PDDL constraints to suggest to the user.
  2. The graph routing loops back to PDDL parsing upon refinement.
- **Deliverable:** Updated `src/core/graph.py` with early HITL routing.

---

## Sprint 4: Evaluation & Polish (August 16 – August 25)

### Exp 4.0: Test Corpus Design
- **Objective:** Create a structured set of synthetic operator intents for baseline evaluation.
- **Action:** Design 20–30 intents spanning four risk categories:

| Category | Example Intent | Expected RADG Decision |
|----------|---------------|----------------------|
| **Safe + Clear** | "Route from Milan to Rome, min 25 dB GSNR" (physically feasible) | Auto-Approve |
| **Ambiguous** | "Set up a fast connection somewhere in the north" (missing constraints) | Clarify (Early HITL) |
| **Infeasible** | "Route from Milan to Rome, min 40 dB GSNR, single span" (impossible physics) | Suggest Replan (Late HITL) |

- **Deliverable:** `tests/evaluation/test_corpus.json` — structured intent corpus with expected outcomes.

### Exp 4.1: Baseline Comparison Evaluation
- **Objective:** Quantitatively demonstrate that Risk-Adaptive HITL outperforms the three baselines.
- **Action:** Run each intent from the test corpus through four system configurations:

| Baseline | Configuration |
|----------|--------------|
| **No-HITL** | Disable all HITL checks — system auto-approves everything. |
| **Always-HITL** | Every intent triggers mandatory Reverse Prompting `interrupt()`. |
| **Fixed-Retry (N=3)** | System generates plan, simulates deployment check, retries up to 3 times on failure. |
| **Risk-Adaptive HITL (Ours)** | RADG decides per-intent based on $U_{sem}$ and $R_{qot}$. |

- **Metrics Collected Per Run:**

| Metric | Symbol | Definition | Target |
|--------|--------|------------|--------|
| **Unsafe Approval Rate** | UAR | Fraction of intents producing physically infeasible lightpaths that get approved | 0% |
| **Human Interaction Count** | HIC | Number of operator interruptions per intent | Lower than Always-HITL |
| **QoT Feasibility Rate** | QFR | Fraction of final approved plans that pass QoT validation | 100% |
| **End-to-End Latency** | E2EL | Wall-clock time from intent submission to final plan approval | Competitive |
| **Token Cost** | TC | Total LLM tokens consumed per intent | Lower than retry-based |

- **Deliverable:** `tests/evaluation/baseline_evaluation.py` — automated evaluation harness. Results table and analysis in thesis.

### Exp 4.2: Live E2E Lab Testbed Execution
- **Objective:** Validate the complete orchestrator against the physical laboratory nodes.
- **Action:** Execute representative intents from each risk category and verify:
  1. The LLM parses the intent correctly into PDDL.
  2. The RADG routes to the correct decision.
  3. For approved plans, configurations are successfully pushed to the testbed.
  4. For clarify/replan/reject, the operator interaction flows correctly.
- **Deliverable:** Working MVP demo recording, execution logs, and final benchmark reports.

---

## Post-MVP: Thesis Writing (August 26 – September 20)

- **Code Freeze:** Zero code changes to protect system stability.
- **Thesis Authoring:** Dedicate 100% of effort to writing the thesis document, focusing on:
  - The limitations of purely generative and post-deployment retry models in optical networking.
  - The math and design behind the Risk-Adaptive Neurosymbolic Intent Planning V5 architecture.
  - The RADG decision function and its joint semantic + QoT risk assessment.
  - The empirical results: baseline comparison tables, UAR/HIC/QFR/E2EL/TC metrics, and analysis of when and why each baseline fails.

---

## Cross-References

- [[Architecture_v5]] — System architecture with RADG.
- [[ProblemStatement_v5]] — Thesis problem definition with evaluation framework.
- [[Scope_Pivot_20260706]] — Architectural evolution from V2 through V5.
- [[literature/sota_gap_analysis]] — Gap analysis against SOTA.
