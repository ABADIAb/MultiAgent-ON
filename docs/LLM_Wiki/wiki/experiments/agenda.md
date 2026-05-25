---
title: "Development Agenda"
date: 2026-05-25
tags: [experiments, agenda, planning]
status: active
---

# Development Agenda (Post-May 19 Meeting)

Based on the latest meeting with Prof. Zhang and Aryanaz, here is the prioritized action plan to unblock development and advance the MultiAgentON project.

## 1. Administrative & Hardware Blockers (High Priority)
Before we can write the physics port or run physical tests, we need these resolved:
- [ ] **Codebase NDA / Access**: Follow up with Aryanaz regarding permission to share the `Network.cpp` codebase (see [[tools_wiki/QoT_Tool]]). We need those exact equations to write `qot_tool.py`.
- [ ] **Workspace SSH Access**: Remote SSH connection is failing. Ping the lab assistants to get the VPN/jump-host config sorted immediately.
- [ ] **Fiber Hardware Update**: Aryanaz mentioned the current testbed fibers are too short, which makes the SNR artificially high (always feasible). Follow up with her to see if they successfully borrowed the longer fiber from Alberto's group to allow for real QoT degradation testing.

## 2. SOTA & Literature Comparison (Professor Qiaolun's Request)
Prof. Qiaolun Zhang specifically requested this at the start (8:19) and close (39:33) of the meeting to position our work against existing research:
- [ ] **Summarize Differences with Literature**: Create a comparison table and 1-2 slides summarizing the differences of our MultiAgentON (LangGraph-based cyclic "Slow Loop" semantic orchestrator) compared to existing agentic AI systems in literature for optical routing and scheduling.

## 3. Architecture & Design (Professor's Request)
Zheng explicitly requested this during the meeting:
- [ ] **Define Intent Request Examples**: Document 3-5 concrete examples of user intents (e.g., simple routing vs. constrained SLA routing). Show how the [[LangGraph_Orchestrator_V2|LangGraph pipeline]] would handle each differently. This will prove the flexibility of our cyclic architecture compared to the linear [[literature/OrchestratorScriptReport|ECOC 2024 script]].

## 4. LangGraph Execution (What we can do right now)
While we wait for the C++ code, we continue the LLM and Graph scaffolding:
- [ ] **Pydantic Schemas**: Map the provided baseline JSON schemas (`lightpath_schema.json`, `measurement_schema.json`) into Python Pydantic classes to be used by the Lightpath Agent (see [[Tool_Registry]]).
- [ ] **Supervisor LLM Integration**: Replace the mock code in `supervisor.py` with actual LangChain/LangGraph LLM calls to parse the intent into the `sla_matrix`.
- [ ] **RESTConf NBI Exploration**: Since the Topology Agent will use RESTConf, we need the controller's exact API documentation or a JSON response dump to start writing the real `GET` requests in `topology.py`.

