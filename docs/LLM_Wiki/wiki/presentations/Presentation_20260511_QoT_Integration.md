---
title: "Presentation: QoT Tool Integration Strategy"
date: 2026-05-19
tags: [presentation, architecture, tools, physical-layer]
status: active
---
# Presentation: QoT Tool Analysis & [[Architecture_Workflow_20260427_Felipe_Abadia|LangGraph Integration]]

**Objective:** Communicate the deep dive into the delivered QoT simulator and the architecture for its integration into the agentic system.

---

## Slide 1: Introduction to the QoT Codebase
- **Delivery:** Received the `Code_for_Felipe` repository.
- **Analysis:** Identified as a C++ Genetic Algorithm (GA) simulator based on the Gaussian Noise (GN) model.
- **Key Files:** `Network.cpp` (core physics logic), `NB_GA_Main.cpp` (GA entry point).
- **Complexity:** The tool is designed for global optimization, whereas our MAS requires per-path feasibility checks.

---

## Slide 2: Physics Decoupled from Optimization
- **The Core Math:** Feasibility is determined by the GN model equations in `calculateDemandSNR` and `spanSNR`.
- **Pivot:** Instead of wrapping the whole GA solver, we propose extracting these equations into a native **Python Physics Port**.
- **Benefits:** 
  - **Latency:** In-memory execution vs. subprocess/file I/O.
  - **Granularity:** Returns `SNR`, `Power`, and `Cost` directly to the LLM for reasoning.

---

## Slide 3: Integration Strategy: The Python Port
- **Implementation:** Create `[[tools_wiki/QoT_Tool|src/tools/qot_tool.py]]` as a native LangGraph `@tool` (ECOC 2024 JSON schemas mapped).
- **Interaction Flow:**
  1. Routing Agent proposes a path.
  2. **TopologyAgent** dynamically fetches RESTConf payloads and updates the **Knowledge Graph** (Digital Twin).
  3. Python Physics Tool queries the Graph and calculates SNR/Power in milliseconds.
  4. Agent receives numeric data (or triggers a Fast Loop on failure) to validate/refine the route.

---

## Slide 4: Critical Questions for the Lab
1. **Topology Extraction [RESOLVED]:** We will pull real-time fiber lengths and OA locations using RESTConf NBI `GET` requests to maintain our Graph.
2. **Hardware Constants:** Are the constants in `Network.cpp` (losses, attenuation) static for the lab hardware, and can we map them to the `measurement_schema.json`?
3. **Verification Baseline:** Can we get a RESTConf JSON payload dump of an active, verified service in the testbed to validate the Python math against the original C++ results?

---

## Slide 5: Next Steps
1. **Acknowledge Strategy:** Obtain approval for the Python-native port.
2. **Implementation:** Translate `calculateDemandSNR`, `calculatePropagatedSNR`, and `spanSNR` to Python.
3. **Graph Binding:** Integrate the tool into the LangGraph Orchestrator for end-to-end routing validation.
