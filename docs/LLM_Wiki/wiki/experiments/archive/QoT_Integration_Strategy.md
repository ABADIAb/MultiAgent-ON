---
title: "QoT Integration Strategy: Pure Python Physics Port"
date: 2026-05-13
tags: [experiment, architecture, python, qot, digital-twin]
status: active
---
# Integration Strategy: QoT Simulator in LangGraph

## 1. Goal and Context
The MultiAgentON framework requires a mechanism to evaluate the physical feasibility of optical light paths proposed by the LLM agents. The original provided QoT codebase (`Code_for_Felipe`) is a comprehensive C++ application designed for global network optimization using Genetic Algorithms. 

However, our [[Architecture_Workflow_20260427_Felipe_Abadia|LangGraph agents]] do not require a global optimizer; they act as the optimizers themselves via reasoning. The agents simply need a deterministic "physics calculator" to tell them if a specific proposed path (e.g., Node A -> Node B -> Node C) is viable based on Signal-to-Noise Ratio (SNR) and receiver power.

## 2. Architectural Analysis & Justification

We evaluated three potential integration options. We selected **Option 2** as the only viable architecture for a high-performance agentic system.

### Rejected: Option 1 (The Subprocess Wrapper)
*Creating `.dat` files dynamically, running the `./NBGA` executable, and parsing the text output.*
- **Why it was rejected:** The C++ tool is a heavy Genetic Algorithm solver. Spawning a subprocess to run a global optimization loop just to evaluate a single path is a massive architectural anti-pattern. It introduces severe latency, heavy file I/O overhead, and brittle regex parsing.

### Rejected: Option 3 (C++ Shared Library / bindings)
*Compiling `Network.cpp` as a `.so` library and calling it via `pybind11` or `ctypes`.*
- **Why it was rejected:** The C++ codebase is highly coupled with object-oriented structures (`Node`, `Graph`, `Unifiber`). Exposing the SNR functions requires complex C++ bindings and memory management that complicates the Python deployment without significant benefits over a pure math port.

### Approved: Option 2 (Pure Python Physics Port)
*Extracting the core mathematical equations from `Network.cpp` and rewriting them as a pure Python function (`qot_tool.py`).*
- **Justification:** This approach completely decouples the physics evaluation from the monolithic C++ solver. By executing pure math in Python, the LangGraph agents can evaluate thousands of paths instantly in memory. It eliminates file I/O, subprocesses, and parsing, resulting in a clean, scalable LangGraph `@tool`.

---

## 3. Step-by-Step Integration Guide

### Step 1: Extracting Network Topology (The Digital Twin Link)
Instead of relying on static C++ `.dat` files or direct API requests from the math port, our Python tool will read from a shared digital twin representation.
- **Implementation:** The orchestrator's **Topology Agent** will dynamically fetch physical testbed data (fiber spans, EDFA locations, and active channels) from the controller's NBI via **RESTConf API (GET)**. This data is mapped to update our shared **Knowledge Graph (Pillar 2)** in real-time. The **QoT Physics Agent** then queries the Knowledge Graph to extract the topology parameters, ensuring perfect decoupling and a live network model.

### Step 2: Porting the Physics Engine
We will extract the Gaussian Noise (GN) model calculations from `Network.cpp`.
- **Target Functions:** `calculateDemandSNR`, `calculatePropagatedSNR`, and `spanSNR`.
- **Goal:** Translate the attenuation, ASE noise, and NLI noise equations into a standalone Python utility.

### Step 3: Defining the Tool Schema
We will create `[[tools_wiki/QoT_Tool|src/tools/qot_tool.py]]` aligned with the ECOC 2024 RESTConf schemas (`lightpath_schema.json` and `measurement_schema.json`):
- **Inputs Required:** 
  - `service_id` (string): The identifier of the lightpath request.
  - `route_nodes` (list of node names representing the path): Aligns with `lightpath_schema.json` route definitions.
  - `channel_id` (string/int): The wavelength or channel index being evaluated.
- **Outputs Returned to Agent:**
  - `snr_db` (float): The final Signal-to-Noise ratio.
  - `receiver_power_dbm` (float): The final power level at the destination.
  - `feasible` (boolean): `True` if `snr_db > threshold` and `receiver_power_dbm > receiver_power_min`.

*Note: Providing the numeric SNR and Power values allows the LLM to understand "how close" it is to the threshold, enabling it to reason and optimize its next routing attempt.*

### Step 4: Binding to the Orchestrator & Fast Loop Error Handling
The tool will be decorated with LangChain's `@tool` and added to the [[Tool_Registry]]. If the QoT feasibility check fails (`feasible: False`), the agent returns specific physical bottlenecks (e.g., `"Span 3 SNR degraded below 12dB"`) alongside the metrics. This output is captured by the LangGraph supervisor node, triggering a **conditional routing edge (the Fast Loop)** to automatically recalculate the path or adjust launch power.

---

## 4. Questions for the Professor (To Unblock Implementation)

Before writing the Python port, we need clarification on the physical environment. Please discuss the following with your professor or lab assistants:

1. **Testbed Data Access [RESOLVED]:** We will use the RESTConf Northbound Interface (NBI) of the controller to dynamically query active network topology via the `TopologyAgent` and construct our `Knowledge Graph` digital twin.
2. **Model Constants:** "In `Network.cpp`, there are several constants (e.g., `filter_loss_dB = 6`, `connector_loss_dB`, `att_coeff_dB_km`). Are these constants fixed for the testbed hardware (and can we map them to the `measurement_schema.json` context), or do we need to query them dynamically as well?"
3. **Verification Baseline:** "Could you provide a RESTConf JSON payload dump of an active, verified service in the testbed, along with its measured SNR? This will allow me to write a rigorous unit-test for the Python math port to guarantee it perfectly matches the laboratory's active calibration."
