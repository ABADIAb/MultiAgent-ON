---
title: "Weekly Report 2026-05-11"
date: 2026-05-11
tags: [report, weekly]
status: active
---
# Master's Weekly Report

---

## Student Name:
Felipe Abadia

## Project Title:
Agentic AI for joint routing and compute scheduling in optical networks

## Current Stage:
Architecture Design & Tool Integration

## Date Range:
May 5, 2026 - May 11, 2026

---

## 1. Planned Goals for This Week

*Carried forward from [[Weekly_Report_20260504_Felipe_Abadia|previous report]]:*
1. **LangGraph Prototyping:** Implement a minimal `StateGraph` in `src/graph.py` with a single Orchestrator node and one dummy tool to validate the end-to-end pipeline.
2. **QoT Tool & Virtual Environment Follow-up:** Request the QoT tool script and track the status of the virtual environment setup.
3. **Orchestrator Script Review:** Review the initial Orchestrator script provided by the professor, analyze it, and decide if it aligns with the architectural design; refine it based on feedback.

---

## 2. Actual Progress This Week

1. **QoT Tool & Virtual Environment (Goal 2 — Completed):** Received the QoT tool repository (`Code_for_Felipe`). We identified that it is a complex C++ Genetic Algorithm simulator rather than a simple Python script.
2. **QoT Tool Structure Deep Dive (Goal 2 — Completed):** Had a meeting with Aryanaz to explain the structure of the QoT tool. The transcript was ingested and the `tools_wiki/QoT_Tool.md` was created to centralize knowledge about `calculate_demand_SNR`, OA initialization, and physical constraints. Formulated an integration strategy (Python wrapper).
3. **Orchestrator Script Review (Goal 3 — Pending):** Delayed due to time constraints.
4. **LangGraph Prototyping (Goal 1 — Pending):** Could not start LangGraph prototyping due to time constraints.

---

## 3. Issue List This Week

### Issue 1
- **Issue:** Remote Workspace Access. Connected to the VPN but did not know how to access the remote workspace provided by the professor (`ssh qiaolun@10.79.26.43`).
- **What has already been tried:** Checked VPN connection successfully.
- **Estimated possible solution:** Ask for instructions to follow.

### Issue 2
- **Issue:** The QoT tool is a C++ simulator (`NBGA`), meaning it cannot be imported directly into Python/LangGraph as a standard module.
- **Estimated possible solution:** Designed a wrapper strategy (documented in `experiments/QoT_Integration_Strategy.md`). The LangGraph agent will call a Python tool that generates `.dat` and `.txt` input files, runs the `./NBGA` executable via `subprocess`, parses the output, and returns the feasibility status.

---

## 4. Plan for Next Week

1. **Resolve Workspace Access:** Connect to the remote environment using VS Code Remote SSH and verify the setup.
2. **Implement QoT C++ Wrapper:** Build the Python adapter for the QoT tool based on the integration strategy, ensuring it can read/write the correct files (`OA_GA_init_v3.txt`, `.dat` files) and parse `result_25`.
3. **LangGraph Prototyping:** Implement the minimal Orchestrator `StateGraph` and bind the new QoT wrapper tool to it to validate end-to-end execution.

---

## 5. Do You Need Support?

Write here: No additional support needed at this exact moment, aside from confirming the SSH connection works as expected.

---

## 6. One-Sentence Summary

Write here: Analyzed the newly received C++ QoT simulator with Aryanaz, devised a Python wrapper integration strategy, and identified the steps needed to unblock remote workspace access. Orchestrator review pending.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
