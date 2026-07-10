---
title: "Weekly Report 2026-07-10"
date: 2026-07-10
tags: [weekly, report, architecture-v4, langgraph, hitl]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Neurosymbolic Orchestration of Intents for Optical Networks: A Graph-Aware Human-in-the-Loop Approach

## Date: 
2026-07-10

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the July 06 report)*
1. **Execute Sprint 1 (Exp 1.0, 1.1, 1.2, 1.3):** Verify Kimi LLM connection, translate QoT to Python, and establish the RESTConf testbed connection.
2. **Begin Sprint 2 (Exp 2.1):** Prompt engineering for the PDDL Intent Parser.

## 2. What did I actually accomplish?

I successfully transitioned the codebase to the new Architecture V4 pipeline, completing the necessary refactoring to move away from the legacy hub-and-spoke model. 

1. **Architecture V4 Refactoring:** 
   - I successfully refactored the entire `src/` directory from the legacy V3 supervisor model to the V4 linear Neurosymbolic Intent Pipeline. All legacy V3 files were archived.

2. **Exp 1.0 Completed (Logic-wise):** 
   - I implemented the `intent_ingest_node` which successfully verifies the Kimi LLM connection using structured outputs (`with_structured_output`) to accurately parse operator intents.

3. **LangGraph HITL Integration:** 
   - I re-wrote `graph.py` to support state persistence via `InMemorySaver` and implemented the Human-in-the-Loop (HITL) pause mechanism using LangGraph's `interrupt()` API inside a new reverse prompting node. This establishes the safety verification flow required for the orchestrator.

4. **Exp 1.3 (Testbed Connectivity) Update:** 
   - I confirmed that the virtual testbed will use the RESTConf protocol rather than SSH. I implemented a structural `RESTConfTestbedClient` stub and formulated 7 critical technical questions for the professor regarding the API details.

5. **Strict TDD Compliance:** 
   - The entire refactor was executed under Strict TDD, resulting in a 100% passing test suite (94 tests, 0 failures), ensuring that the GN Model physics port (Exp 1.1 & 1.2) remains fully intact.

## 3. Issue List This Week

### Issue 1
- **Issue:** C++ to Python QoT translation is pending (Carried over from July 06).
- **What has already been tried:** We mapped the constants and polynomial NF computations from the original C++ simulator.
- **Result:** **SOLVED**. The translation was successfully maintained and integrated into the V4 refactor with 100% test coverage.

### Issue 2
- **Issue:** RESTConf Hook to Virtual Testbed.
- **What has already been tried:** We identified that the testbed uses RESTConf rather than SSH. I implemented a structural `RESTConfTestbedClient` stub in Python, but lack the exact endpoint details.
- **Result:** PENDING (Blocks Exp 1.3).
- **Estimated possible solution:** Await the professor's response with the virtual testbed API details (URL, Auth, Endpoints) to complete the `get_topology` and `health_check` methods.

---

## 4. Plan for Next Week

1. Run the pipeline live with the `KIMI_API_KEY` to definitively close Exp 1.0.
2. Execute Sprint 2 (Exp 2.1 and 2.2): Implement the PDDL Parser (with CFG validator) and the Reverse Prompting LLM reconstruction.
3. Finalize Exp 1.3 (`RESTConfTestbedClient`) as soon as the professor provides the virtual testbed API documentation.

---

## 5. Do I Need Support?

Write here: Yes, I need the professor to provide the API documentation (Base URL, Authentication, and Topology Endpoints) for the virtual RESTConf testbed to complete Exp 1.3.

---

## 6. One-Sentence Summary

I successfully refactored the entire LangGraph orchestration codebase into a linear Neurosymbolic pipeline equipped with Human-in-the-Loop interrupts and strict TDD validation, leaving only the virtual testbed RESTConf API details pending for Sprint 1 completion.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
