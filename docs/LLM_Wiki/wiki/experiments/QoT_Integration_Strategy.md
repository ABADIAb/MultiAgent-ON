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
Instead of relying on static C++ `.dat` files, our Python tool needs to read the current state of the network (nodes, fiber span lengths in km, and optical amplifier locations).
- **Implementation:** We will extract this information from the Testbed or Digital Twin. For prototyping, we will use a static `topology.json` file. When the real testbed is connected, we will use REST API calls or NETCONF/YANG to dynamically pull the topology state.

### Step 2: Porting the Physics Engine
We will extract the Gaussian Noise (GN) model calculations from `Network.cpp`.
- **Target Functions:** `calculateDemandSNR`, `calculatePropagatedSNR`, and `spanSNR`.
- **Goal:** Translate the attenuation, ASE noise, and NLI noise equations into a standalone Python utility.

### Step 3: Defining the Tool Schema
We will create `[[tools_wiki/QoT_Tool|src/tools/qot_tool.py]]`.
- **Inputs Required:** 
  - `path` (list of nodes in the proposed route)
  - `span_lengths` (list of fiber lengths in km between the nodes)
  - `amplifier_locations` (list of active OAs on those spans)
- **Outputs Returned to Agent:**
  - `snr_db` (float): The final Signal-to-Noise ratio.
  - `receiver_power_dbm` (float): The final power level at the destination.
  - `feasible` (boolean): `True` if `snr_db > threshold` and `receiver_power_dbm > -18 dBm`.

*Note: Providing the numeric SNR and Power values allows the LLM to understand "how close" it is to the threshold, enabling it to reason and optimize its next routing attempt.*

### Step 4: Binding to the Orchestrator
The tool will be decorated with LangChain's `@tool` and added to the [[Tool_Registry]], making it deterministically available to the Routing Agent.

---

## 4. Questions for the Professor (To Unblock Implementation)

Before writing the Python port, we need clarification on the physical environment. Please discuss the following with your professor or lab assistants:

1. **Testbed Data Access:** "To feed the python tool, how exactly will we extract the real-time fiber lengths (km) and optical amplifier (OA) locations from the testbed? Is there a REST API, a configuration JSON, or a NETCONF interface we can query?"
2. **Model Constants:** "In `Network.cpp`, there are several constants (e.g., `filter_loss_dB = 6`, `connector_loss_dB`, `att_coeff_dB_km`). Are these constants fixed for the testbed hardware, or do we need to query them dynamically as well?"
3. **Verification Baseline:** "Can you provide a simple, known-good scenario? For example, 'A path from Node 1 to Node 2 of 50km with one amplifier should yield an SNR of exactly X and a Power of Y'. This will allow me to unit-test my Python math port and guarantee it matches the C++ calculations perfectly."
