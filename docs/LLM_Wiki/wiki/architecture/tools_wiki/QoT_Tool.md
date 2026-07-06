---
title: "QoT Tool Documentation"
date: 2026-05-13
tags: [tools, architecture, physical-layer, simulator, python]
status: active
---
# QoT (Quality of Transmission) Estimator Tool

This document centralizes both the conceptual boundaries and the specific implementation details of the QoT tool based on the Aryanaz meeting transcript and the revised pure-Python integration strategy.

## 1. Conceptual Boundaries ([[QoT_Awareness]])

[[QoT_Awareness]] ensures that generated optical routes (light paths) are physically feasible for data transmission. The evaluation relies on a **network-based calculation** leveraging the **Gaussian Noise (GN) model**.

### Feasibility Criteria
A light path is strictly evaluated against two parameters at the destination node:
1. **Receiver Power Threshold:** Must be `> -18 dBm`.
2. **SNR (Signal-to-Noise Ratio):** Must exceed the dynamically defined `SNR_threshold`.

If both conditions are met, the path is **feasible**. Otherwise, it is **not feasible**.

---

## 2. Implementation Strategy: Pure Python Physics Port

Initially, the strategy involved wrapping the complex C++ Genetic Algorithm (GA) simulator (`Code_for_Felipe`). We have pivoted to a **Pure Python Physics Port** to decouple the necessary physics calculations from the monolithic C++ solver, ensuring low latency and native LangGraph integration.

### Key Components to Port
The LangGraph orchestrator only needs the "Physics Engine," not the global optimizer. We will extract the following core logic from `Network.cpp` into a standalone Python file (`qot_tool.py`):
- **`calculateDemandSNR`**: The master function that calculates transmission impairments across specific fibers.
- **`calculatePropagatedSNR`**: Handles noise leakage in filterless network scenarios.
- **`spanSNR`**: The function computing noise for individual segments of fiber.

### [[Architecture_v3|LangGraph Orchestration Context]]
The interaction flow will be:
1. Agent proposes a route.
2. The orchestrator fetches the current network topology (fiber lengths, optical amplifiers).
3. The proposed route and topology data are fed into the pure Python `qot_tool.py`.
4. The Python tool returns a dictionary with exact values: `{"feasible": bool, "snr": float, "power": float, "cost": float}`.
5. The Agent uses this numeric feedback to proceed or to reason about a better route.

---

## 3. Pending Clarifications (Action Required)

<mark>**PENDING PROFESSOR GUIDANCE:**</mark> Before finalizing the implementation of the Python port, the following critical points must be clarified:

1. <mark>**Testbed Topology Extraction:** How exactly will we extract real-time fiber lengths (km) and Optical Amplifier (OA) locations from the testbed? (e.g., REST API, JSON file, NETCONF)?</mark>
2. <mark>**Hardware Constants:** Are the physical constants currently hardcoded in C++ (like `filter_loss_dB = 6` or `connector_loss_dB`) static for the testbed, or do they need to be queried dynamically?</mark>
3. <mark>**Verification Baseline:** We need a simple, "known-good" scenario (e.g., exact expected SNR for a 50km path with 1 amplifier) to unit-test the Python port and guarantee it matches the original C++ math.</mark>
