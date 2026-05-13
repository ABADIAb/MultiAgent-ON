---
title: "Proposal: QoT Tool Integration for LangGraph Agent"
date: 2026-05-13
tags: [proposal, architecture, qot, thesis]
status: pending-review
---

# Proposal: Integration Strategy for QoT Feasibility in Multi-Agent Systems

Dear Professor,

Following your feedback on the initial report, I have refined the strategy for integrating the [[QoT_Awareness|Quality of Transmission (QoT) feasibility check]] into the [[Architecture_Workflow_20260427_Felipe_Abadia|LangGraph orchestrator]]. My goal is to ensure the agentic system can evaluate light paths with high precision and low latency. 

Below is a proposal for our implementation path. I would appreciate your guidance on whether this approach aligns with the laboratory's objectives.

## 1. The Challenge
The provided C++ codebase (`Code_for_Felipe`) is a powerful simulator designed for global network optimization. However, for a real-time Multi-Agent System (MAS), using the full simulator as a "black box" presents some operational hurdles that I have analyzed based on your questions:

*   **Minimum Input Requirements:** Currently, to evaluate even a single path, the C++ tool requires the construction of an entire environment, including a complete `.dat` topology file and an OA initialization file. It is designed as a global solver rather than a queryable calculator, making it difficult to pass a *specific* path proposed by an agent without aggressive file hacking.
*   **Agent Output Requirements:** For the LangGraph agent to function as a reasoning engine, receiving a simple Boolean "Pass/Fail" is insufficient. The agent needs the **exact SNR value, receiver power (dBm), and path cost.** This numeric feedback allows the LLM to understand *how close* it is to the threshold, enabling it to optimize its next routing attempt rather than guessing blindly.
*   **Execution Overhead:** Launching the full C++ optimization binary and performing disk-based I/O for every agent query creates significant latency, which would bottleneck the real-time interaction of the multi-agent system.

## 2. The Suggestion: Python Physics Port
Instead of wrapping the entire C++ simulator or focusing on file generation/parsing scripts, I suggest that **the most useful part to rewrite in Python is the core SNR calculation logic.** 

Specifically, I propose extracting the mathematical equations from the **Gaussian Noise (GN) Model** functions in `Network.cpp` (specifically `calculateDemandSNR`, `calculatePropagatedSNR`, and `spanSNR`) and implementing them as a native Python utility (`qot_tool.py`).

### Why this path?
*   **Strategic Rewrite:** We are NOT rewriting the Genetic Algorithm or the optimization logic. We are only porting the physics equations. This gives the agent an "in-memory" calculator to validate its own routing decisions instantly.
*   **Performance:** The agent can evaluate a path in milliseconds without spawning subprocesses or reading/writing temporary files.
*   **Direct Feedback:** The Python tool will return a structured dictionary: `{"feasible": bool, "snr": float, "power": float, "cost": float}`, giving the agent the full context it needs.

## 3. Alternative Approach
We could still proceed with a **Subprocess Wrapper** (compiling the C++ code and calling it via Python). This would ensure 100% fidelity to the original code but would keep the system slow and dependent on external binary execution. I am open to your recommendation if you believe the complexity of the C++ logic makes a Python port risky.

## 4. Proposed Implementation Steps
1.  **Topology Mapping:** Define a `topology.json` representing the testbed (span lengths and OA locations).
2.  **Logic Port:** Translate the SNR/Power equations from C++ to Python.
3.  **Validation:** Run the same path through both the original C++ simulator and the new Python tool to ensure the results match.
4.  **Integration:** Bind the tool to the LangGraph Routing Agent.

## 5. Technical Questions for Guidance
To ensure the accuracy of the Python model, I have a few questions regarding the testbed configuration:
1.  **Topology Extraction:** What is the best way to extract the real-time fiber lengths (km) and amplifier locations from the lab environment (API, JSON config, etc.)?
2.  **Hardware Constants:** Are the physical constants in the C++ code (e.g., `filter_loss_dB = 6`, `connector_loss_dB`, `att_coeff_dB_km`) static for the current testbed setup?
3.  **Gold Standard Scenario:** Could you provide a "known good" scenario (e.g., a specific path that should yield a specific SNR) so I can validate my Python implementation against your established results?

Thank you for your time and support in refining this architecture.

Best regards,
Felipe Abadia Bermeo
