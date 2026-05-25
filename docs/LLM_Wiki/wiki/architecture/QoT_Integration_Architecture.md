---
title: "QoT Integration Architecture: Python Physics Port"
date: 2026-05-24
tags: [architecture, python, qot, digital-twin]
status: active
---

# QoT Integration Architecture

## 1. Goal and Context
The [[LangGraph_Orchestrator_V2|LangGraph agents]] require a mechanism to evaluate the physical feasibility of optical light paths (see [[QoT_Awareness]]). To achieve high-performance evaluation, we decouple the physics calculations from the heavy monolithic C++ Genetic Algorithm solver (see [[tools_wiki/QoT_Tool]]). Instead, we port the core mathematical equations into a native Python utility (`qot_tool.py`), registered in the [[Tool_Registry]]. 

## 2. Integration Strategy: Pure Python Physics Port
We extract the Gaussian Noise (GN) model calculations from `Network.cpp` (documented in [[tools_wiki/QoT_Tool]]) into pure Python. This eliminates file I/O overhead, subprocesses, and text parsing, allowing the LangGraph agents to evaluate paths instantly in-memory.

### Targeted Equations for Porting
- `calculateDemandSNR`: Computes the end-to-end signal-to-noise ratio for a specific lightpath request.
- `calculatePropagatedSNR`: Models the accumulation of linear and nonlinear noise across successive spans.
- `spanSNR`: Evaluates the physical impairment contributions (ASE and NLI) per individual fiber/amplifier span.

## 3. Tool Workflow
### Step 1: Extracting Network Topology
The **Topology Agent** dynamically fetches physical testbed data from the controller via RESTConf API (GET) and updates the **Knowledge Graph** digital twin. The **Routing Agent** queries the Knowledge Graph to extract the topology parameters for `qot_tool.py`.

### Step 2: Tool Execution (`qot_tool.py`)
- **Inputs:** `service_id`, `route_nodes` (path), `channel_id`.
- **Outputs:** `snr_db` (float), `receiver_power_dbm` (float), `feasible` (boolean).
By providing exact numeric output, the LLM can understand "how close" a path is to the feasibility threshold and optimize its next routing attempt.

### Step 3: Fast Loop Error Handling
If the path is infeasible (`feasible: False`), the tool returns specific physical bottlenecks (e.g., "Span 3 SNR degraded below 12dB"). A **conditional edge** routes the state back to the Routing Agent for self-correction.

## 4. Testbed Context & Constraints
Based on lab discussions, the current physical implementation relies on:
- **Static Hardware Constants:** The physical constants in the C++ model (e.g., `filter_loss_dB`, `connector_loss_dB`) are considered static for the testbed hardware and do not need to be queried dynamically.
- **Short Fiber Environment:** The testbed currently utilizes very short fibers without inline amplifiers (only preamp and booster). Consequently, measured SNR will be very high and light paths will almost always be flagged as feasible. The tool must still execute the math flawlessly to ensure the logical architecture handles routing logic regardless of the physical limits.
