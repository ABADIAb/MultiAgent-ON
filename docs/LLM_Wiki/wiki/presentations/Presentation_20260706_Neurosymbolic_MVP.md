---
title: "Presentation: Neurosymbolic Intent Orchestration MVP"
date: 2026-07-06
tags: [presentation, neurosymbolic, mvp, roadmap]
status: active
---

# Presentation: Neurosymbolic Intent Orchestration MVP

*(Draft slide deck to be presented to the professor. Format according to the `presentation-designer` skill if exporting to a slide generator).*

---

## Slide 1: Title
**Neurosymbolic Intent Orchestration**
*A Graph-Aware Human-in-the-Loop Approach*
MVP Roadmap & Architecture Pivot
Date: 2026-07-06

---

## Slide 2: The Generative Bottleneck
**Why Purely Generative LLMs Fail in Optical Routing**
- **Token Saturation:** Injecting full RESTConf topologies causes context limits and "lost-in-the-middle" hallucinations.
- **Hallucinated Physics:** LLMs are statistical text engines, not physics calculators. They cannot natively respect GSNR or nonlinear optical constraints.
- **Semantic Drift:** Open-ended conversation for Human-in-the-Loop (HITL) lacks mathematical convergence, leading to dropped constraints.

---

## Slide 3: The Solution (Architecture V4)
**Strict "Sistema 1 + Sistema 2" Separation**
- **LLM as Translator:** Parses unstructured intent into formal PDDL (Planning Domain Definition Language).
- **Reverse Prompting:** The system translates PDDL back to natural language. The operator approves the precise logical reconstruction, guaranteeing convergence.
- **Mock GraphRAG:** Injects only the $k$-hop local neighborhood, protecting the token budget.
- **Symbolic Solver:** Deterministically extracts structurally valid paths *before* any heavy physics simulations.

---

## Slide 4: The Neurosymbolic Pipeline
**Visual Flow**
1. **Ingest:** Operator Intent (NL)
2. **Translate:** LLM outputs PDDL
3. **Verify (HITL):** Reverse Prompting + Operator Approval
4. **Filter:** Symbolic Solver + Mock GraphRAG extracts 3-5 paths
5. **Calculate:** Python QoT Tool (GN-model) evaluates physical layer
6. **Provision:** Orchestrator pushes to testbed via SSH

---

## Slide 5: Proof of Concept — Deterministic Tooling
**Python QoT Calculator (GN-model)**
- **Achievement:** Successfully ported the core C++ physics engine to pure Python.
- **Strict TDD:** Validated with 95% test coverage against hand-computed C++ baselines.
- **LangChain Integration:** Wrapped as a deterministic `@tool` (`qot_check`) ready for the LangGraph orchestrator.
- **Impact:** Proves we can fully isolate complex physical-layer calculations from the LLM, eliminating hallucinated SNR errors.

---

## Slide 6: The MVP Roadmap (Aug 25 Deadline)
**Focus: Functional Integration over Optimization**
- **Sprint 1 (Tooling):** Translate C++ QoT to Python; establish SSH testbed hook.
- **Sprint 2 (Logic):** PDDL parser prompt engineering; Reverse Prompting (`interrupt()`) implementation.
- **Sprint 3 (Integration):** Compile the E2E LangGraph orchestrator.
- **Sprint 4 (Validation):** Live testbed provisioning and error handling polish.
- **Post Aug 25:** Code freeze. 100% focus on writing the thesis document (delivery Sept 20).
