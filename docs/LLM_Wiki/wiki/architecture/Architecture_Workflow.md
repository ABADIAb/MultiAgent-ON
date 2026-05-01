---
title: "Architecture Workflow"
date: 2026-04-24
tags: [architecture, workflow, multi-agent]
status: active
---
# Proposed Architecture: Sequential Multi-Agent Workflow

This document details the step-by-step workflow of the "Slow Loop" Orchestrator in an Intent-Based Optical Network. It defines how semantic intents are translated, validated, and delegated to specialized multi-agent sub-systems to solve joint routing and compute scheduling.

## Phase 1: Intent Parsing & Translation
1. **The Human Intent:** The process begins with a network operator inputting a high-level, unstructured semantic command (e.g., *"Provide a highly reliable, low-latency network slice to stream 4K VR data from the central database to an edge node for rendering"*).
2. **LLM Translation:** The Orchestrator Agent (The Brain) parses the text using semantic reasoning. It translates abstract concepts ("low-latency", "VR data") into strict, numerical [[Concepts_and_Terminology|Service Level Agreement (SLA)]] constraints (e.g., `< 10ms` latency, `5 Gbps` bandwidth). It generates a provisional structured constraint matrix.

## Phase 2: Human-in-the-Loop (HITL) Refinement
3. **Reverse Prompting:** Because LLMs are probabilistic reasoning engines, allowing them to directly execute unverified intents introduces severe [[ProblemStatement_20260427_Felipe_Abadia|Garbage In, Garbage Out (GIGO)]] risks. The Orchestrator enters a refinement loop. It uses reverse prompting to explain its mathematical interpretation of the intent back to the user:
   > *"I interpreted your request as needing a 5 Gbps optical path with a strict 10ms end-to-end latency constraint, terminating at an A100 GPU. Do you authorize this constraint matrix?"*
4. **Validation:** The user validates or adjusts the matrix. The system only proceeds to the execution phase once the human operator gives explicit authorization.

## Phase 3: Delegation to Multi-Agent Sub-Systems
To avoid the "exploding state space" of legacy ILP solvers, the Orchestrator does not attempt to solve the placement simultaneously. It delegates to two specialized multi-agent sub-systems sequentially.

5. **The Routing Agent (Optical Specialist):** 
   - The Orchestrator passes the validated constraint matrix to the Routing Agent.
   - **Deterministic Tool Use:** LLMs cannot calculate physical layer impairments or Dijkstra's shortest path. The Routing Agent leverages *deterministic external tools* (e.g., Python graph algorithms, SNR calculators) to evaluate the physical network graph $G(V,E)$ and real-time telemetry.
   - It outputs feasible optical paths (e.g., *"Path $P_1$ on Wavelength 45 is available with a 4ms propagation delay"*).

6. **The Compute Agent (Edge Specialist):**
   - The Orchestrator takes the feasible paths and hands them to the Compute Agent.
   - **Deterministic Tool Use:** The Compute Agent uses external APIs to query the real-time VRAM, CPU load, and energy limits at the destination nodes of the proposed paths.
   - It calculates the remaining latency budget. (e.g., *"If optical delay is 4ms, I have 6ms left to render. Does node $C_j$ have the GPU capacity to render a VR frame in 6ms?"*).

## Phase 4: Conflict Resolution
7. **Iterative Feedback:** If the Compute Agent determines that the destination node for Path $P_1$ is at 99% capacity (SLA violation), it reports a conflict back to the Orchestrator. The Orchestrator intercepts this failure and commands the Routing Agent to propose the next best path ($P_2$). This loop iterates until a joint solution is found.

## Phase 5: Fast Loop Handoff
8. **Final Configuration Tuple:** Once the multi-agent sub-systems agree, the Orchestrator synthesizes the optimal configuration tuple: $A^* = (r^*, b^*, c^*)$ (representing the source node, spectrum/lightpath, and target compute node).
9. **Execution:** The Orchestrator formats this tuple into a strict API payload and pushes it down to the SDN Controller (The Fast Loop), which physically configures the optical switches and allocates the edge VMs in milliseconds.