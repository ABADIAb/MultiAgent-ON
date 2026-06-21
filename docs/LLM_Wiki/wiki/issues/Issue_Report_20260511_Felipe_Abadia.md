---
title: "Issue Report 2026-05-11"
date: 2026-05-11
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
Architecture Design & Tool Integration

## Date:
2026-05-11

---

### Solved Issues

#### Solved Issue 1 (Carry forward from May 4)
- **Original issue:** The QoT estimator tool has not been delivered yet.
- **What was tried:** Followed up with the professor and received the repository (`Code_for_Felipe`).
- **Resolution / outcome:** The code was delivered and analyzed. It was identified as a C++ Genetic Algorithm simulator. An integration strategy (Python wrapper) was designed and documented in `experiments/QoT_Integration_Strategy.md`.

---

### Pending Issues

#### Pending Issue 1
- **Issue:** No application code exists yet in `src/`. The LangGraph agents, tools, and graph definition have not been started.
- **What has already been tried:** Defined the folder structure and developed the concept of the Hybrid Memory Architecture.
- **Result:** Delayed due to other priorities (QoT tool analysis).
- **Estimated possible solution:** Begin with a minimal LangGraph `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool.

#### Pending Issue 2
- **Issue:** Remote Workspace Access.
- **What has already been tried:** Connected to the VPN and received SSH credentials (`ssh qiaolun@10.79.26.43`).
- **Result:** Credentials received, but connection hasn't been tested yet.
- **Estimated possible solution:** Use the "Remote - SSH" extension in VS Code to connect to the machine and verify the environment.

#### Pending Issue 3
- **Issue:** Orchestrator Script Review.
- **What has already been tried:** The script was provided by the professor.
- **Result:** Delayed due to time constraints.
- **Estimated possible solution:** Dedicate time next week to review the script and align it with the project's architectural design.

#### Pending Issue 4
- **Issue:** The [[Research_Plan_MultiAgentON|Research Plan]] literature review is still in progress (Phases 1 and 2).
- **Estimated possible solution:** Execute the remaining research phases to complete the state-of-the-art review.

---

### Additional Notes
This week was critical for the technical understanding of the physical-layer constraints. The shift from "Python script" to "C++ GA Simulator" for the QoT tool requires a robust adapter pattern implementation to maintain the "Orchestrator as a Reasoning Engine" paradigm.
