---
title: "QoT Physics Port Integration"
date: 2026-05-25
tags: [architecture, python, qot, digital-twin]
status: active
---

# QoT Physics Port Integration

## 1. Overview
Instead of wrapping the entire C++ simulator (`Code_for_Felipe`), we are implementing a **Pure Python Physics Port** ([[tools_wiki/QoT_Tool|qot_tool.py]]). This decouples the physics evaluation from the monolithic global optimizer, allowing LangGraph agents to evaluate thousands of paths instantly in memory without subprocess overhead or file I/O. This tool is central to the [[ArchitectureV2|V2 LangGraph Architecture]].

## 2. Core Equations Ported
We are extracting the Gaussian Noise (GN) model calculations from `Network.cpp`:
- `calculateDemandSNR`: Computes the end-to-end signal-to-noise ratio for a lightpath.
- `calculatePropagatedSNR`: Models the accumulation of linear and nonlinear noise across successive spans.
- `spanSNR`: Evaluates the physical impairment contributions (ASE and NLI) per individual fiber/amplifier span.

## 3. Dynamic Topology via Knowledge Graph
The tool will **not** rely on static C++ `.dat` files. Instead, it reads directly from the shared digital twin representation (Pillar 2 of the [[Hybrid_Memory_Architecture]]):
- The **Topology Agent** fetches physical testbed data via RESTConf NBI.
- It populates the **Knowledge Graph**.
- The [[tools_wiki/QoT_Tool|qot_tool.py]] queries the Knowledge Graph to extract live topology parameters for the math.

## 4. Tool Schema & Output
Aligned with ECOC 2024 RESTConf schemas (`lightpath_schema.json` and `measurement_schema.json`):
- **Inputs:** `service_id`, `route_nodes`, `channel_id`.
- **Numeric Outputs returned to Agent:** 
  - `snr_db` (float): The final [[QoT_Awareness|Signal-to-Noise ratio]].
  - `receiver_power_dbm` (float)
  - `feasible` (boolean)
