---
title: "Project Agenda & Execution Plan"
date: 2026-05-25
tags: [agenda, planning, tasks]
status: active
---

# Project Agenda & Tasks

## Track A: Documentation & Wiki Organization
- [x] Execute Wiki reorganization (update [[ArchitectureV2]], archive proposals).
- [ ] Update [[Tool_Registry]] to formally include the new [[tools_wiki/QoT_Tool|qot_tool.py]].
- [ ] Document the RESTConf schema models as Pydantic classes in the wiki.
- [ ] **Team Request (Zheng):** Document examples of different end-to-end "Intents" and how they map to the [[ArchitectureV2|orchestrator pipelines]].

## Track B: Implementation Progress (Code)
- [ ] **Task 1: Topology Agent & Graph Building.** Implement the RESTConf GET queries to the SDON controller and populate the in-memory [[Hybrid_Memory_Architecture|Knowledge Graph]].
- [ ] **Task 2: [[QoT_Physics_Port|QoT Python Port]].** Translate the C++ GN model equations (`calculateDemandSNR`, etc.) into [[tools_wiki/QoT_Tool|qot_tool.py]].
- [ ] **Task 3: Unit Testing QoT.** Validate the Python tool's output against the "Gold Standard Benchmark" (active service RESTConf payload dump). Note: *Until Alberto provides the longer fiber, test paths will have artificially high SNR, so we treat all paths as feasible for now.*
- [ ] **Task 4: LangGraph State Machine.** Implement the Supervisor Node, HITL check, and state routing.

## Track C: Project Management & Coordination
- [ ] **Team Request (Access):** Remind Mam to grant access to the SDON Test Bed.
- [ ] **Team Request (NDA):** Coordinate with Professor and Aryanaz regarding Zheng signing the NDA to view the C++ codebase.
