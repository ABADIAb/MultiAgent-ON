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
- **Implementation:** Create `[[tools_wiki/QoT_Tool|src/tools/qot_tool.py]]` as a native LangGraph `@tool`.
- **Interaction Flow:**
  1. Routing Agent proposes a path.
  2. Orchestrator fetches current Testbed topology (fiber lengths, OA locations).
  3. Python Tool calculates SNR/Power in milliseconds.
  4. Agent receives numeric data to validate or refine the route.

---

## Slide 4: Critical Questions for the Lab
1. **Topology Extraction:** How do we pull real-time fiber lengths and OA locations from the testbed (REST API vs. Static Config)?
2. **Hardware Constants:** Are the constants in `Network.cpp` (losses, attenuation) static for the lab hardware?
3. **Verification Baseline:** Can we establish a "known-good" scenario to validate the Python math against the original C++ results?

---

## Slide 5: Next Steps
1. **Acknowledge Strategy:** Obtain approval for the Python-native port.
2. **Implementation:** Translate `calculateDemandSNR`, `calculatePropagatedSNR`, and `spanSNR` to Python.
3. **Graph Binding:** Integrate the tool into the LangGraph Orchestrator for end-to-end routing validation.
