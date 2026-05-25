---
title: "LangGraph Orchestrator Architecture (V2)"
date: 2026-05-24
tags: [architecture, workflow, multi-agent, langgraph, orchestrator, SDON]
status: active
---

# LangGraph Orchestrator Architecture (V2)

## 1. Executive Summary
This document defines the definitive architectural workflow of the "Slow Loop" Orchestrator in an Intent-Based Optical Network. It builds upon the initial LangGraph workflow design and integrates the logical pipeline and RESTConf interaction models from the [[literature/OrchestratorScriptReport|ECOC 2024 baseline]]. The system translates semantic intents into structured tasks, validates them via Human-in-the-Loop (HITL), and delegates them to specialized agents using a LangGraph topology supported by a [[Hybrid_Memory_Architecture]].

## 2. Phase 0: Memory & Knowledge Substrate
Before parsing intents, the system relies on a [[Hybrid_Memory_Architecture]] foundation to manage state and scalability.
1. **Structural Memory (LLM Wiki):** Acts as the deterministic, structured state memory (Procedural Rules and Skills).
2. **Knowledge Graph (State Tracker):** A technology-agnostic graph system that explicitly tracks the current live topology, agent dependencies, and numerical SLA constraints. It acts as a Digital Twin.
3. **Vector Memory (RAG):** Episodic memory for retrieving extended unstructured documentation and dynamically fetching specific tool schemas.

## 3. Phase 1: Intent Parsing & Human-in-the-Loop (HITL)
1. **The Human Intent:** A network operator inputs a high-level semantic command.
2. **Supervisor Node (Replaces `planning.py`):** Translates high-level semantic commands into a numerical SLA matrix and a structured task list. 
3. **Validation Node (HITL):** The graph halts here. The Orchestrator explains its mathematical interpretation of the intent to the human operator. The state only proceeds to execution once authorized (`is_authorized = True`).

## 4. Phase 2: LangGraph-Driven Multi-Agent Delegation
The Supervisor routes tasks to specialized sub-agents based on the generated task list. The agents maintain dynamic access to the memory:

- **Topology Agent:** Executes HTTP `GET` requests to the SDON Testbed's RESTConf NBI. Parses the JSON/YAML responses to dynamically extract physical testbed data (fiber lengths, OAs) and actively updates the Knowledge Graph state.
- **Routing Agent:** Responsible for path selection. Wraps the native Python Physics model (`qot_tool.py`, see [[QoT_Integration_Architecture]]) to execute deterministic mathematical [[QoT_Awareness|QoT validation]].
- **Lightpath Agent (Replaces `execution.py`):** Uses JSON schemas imported from the baseline (e.g., `lightpath_schema.json`, `measurement_schema.json`) mapped via Pydantic to ensure valid RESTConf payload generation for establishing connections. Tools registered in the [[Tool_Registry]].

## 5. Phase 3: Conflict Resolution & The "Fast Loop" Handoff
- **Iterative Feedback:** If the SDON Testbed returns a REST error or if the Routing Agent's QoT tool flags an infeasible path, a **Conditional Edge** routes the graph back to the responsible agent for self-correction.
- **Episodic Fallback (Dynamic RAG Access):** During self-correction, if a standard fix isn't obvious, the agent dynamically queries the Vector RAG with the error context to fetch the correct historical workaround.
- **Execution:** Once the multi-agent graph resolves all constraints, the Orchestrator pushes the final optimal configuration tuple formatted as a strict RESTConf API payload down to the SDN Controller (The Fast Loop), physically configuring optical switches.
