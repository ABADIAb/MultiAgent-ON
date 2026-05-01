---
title: "Problem Statement"
date: 2026-04-27
tags: [thesis, definition, objective]
status: active
---
# Problem Statement: Agentic AI for Joint Routing and Compute Scheduling

## Context
- **Topic:** Agentic AI for joint routing and compute scheduling in optical networks.
- **Keywords:** Generative AI, Multi-agent LLM, Intent-based networking.
- **The Problem:** Joint optimization of communication and computation resources is heavily bottlenecked by heterogeneous constraints and dynamic demands. Current methods hopelessly fail to flexibly integrate service intent with resource allocation.
- **The Solution Architecture:** A multi-agent LLM system designed to decompose tasks and coordinate routing and compute scheduling utilizing fine-tuned/non-fine-tuned LLM models, specific tool/function calling, and Retrieval-Augmented Generation (RAG).

## Given
The orchestration agent is given three distinct, dynamic layers of input:
1. **The Natural Language Intent:** A high-level, unstructured semantic request from a human operator (e.g., "I want to establish a service between node one and node three").
2. **The Physical Network Graph $G(V,E)$:** A serialized representation of the underlying topology, encompassing vertices (edge servers, compute capacities) and edges (optical fiber characteristics, link capacities, latency limits).
3. **Dynamic State Observations:** Continuous, real-time environment telemetry, including link utilization, queue backlogs, [[Concepts_and_Terminology|Quality of Transmission (QoT)]] metrics like SNR, EDFA power profiles, and external hardware/power constraints.

## Decide
The agentic AI system employs a sequential coordination protocol to translate human intent into an optimal configuration. The algorithm decides the precise allocation in a structured, multi-stage workflow:
1. Intent Translation & Parsing: The Orchestrator LLM parses the natural language input to deduce numerical [[Concepts_and_Terminology|Service Level Agreement (SLA)]] boundaries, generating a provisional constraint matrix detailing required bandwidth, latency, and compute capacity (FLOPs/GPUs).
2. HITL Refinement (Reverse Prompting): To prevent Garbage-In, Garbage-Out (GIGO), the Orchestrator enters a Human-in-the-Loop refinement stage. It uses reverse prompting to present the interpreted constraint matrix back to the human operator for validation. 
3. Sequential Handoff to Multi-Agent Sub-Systems: Once approved, the Orchestrator delegates the problem sequentially to specialized multi-agent sub-systems (the Routing/Network Agent and the Computing Agent, could be more agents as well). Because LLMs are reasoning engines and not calculators, these specialist agents strictly delegate all mathematical operations, physics-bound constraint checks, and spectrum pathfinding to deterministic external tools (like Python scripts, etc). No hallucination allowed.

The final output of the agentic system might depend on the operator intent. For example if the operator intent is to establish a service between two nodes, the output of the agentic system is a structured configuration tuple $A^* = (r^*, b^*, c^*)$, where:
- $r^*$ is the selected access network node or sector.
- $b^*$ is the allocated spectrum band, wavelength, or path.
- $c^*$ is the designated compute node where the task ($T_i$) will actually be processed.

This final configuration is mapped directly into an automated API call to the physical SDN controller.

But if the operator intent is to consult the network state or documentation or make some queries, the output of the agentic system is a structured response to the operator's query. Response that is crafted after having executed the necessary actions (e.g. having called the tools or agents needed to satisfy the operator's query).

## Objective
As optical networks transition from bit-centric to intent-centric operations, the objective shifts to maximizing the [[Concepts_and_Terminology|Goal-Oriented Task (GoT) utility]] while minimizing system-level resource costs. 

The objective function of the Orchestrator LLM is to maximize:
$$ \max_{A^*} \sum_{i \in I} \Big( U_i(TSR_i) - w_c \cdot C_{sys}(r_i^*, b_i^*, c_i^*) \Big) $$

Where:
- $U_i(TSR_i)$ is the utility derived from the successful execution of task $i$ ([[Concepts_and_Terminology|Task Success Rate]]).
- $C_{sys}$ represents the total system costs, coupling optical variables (e.g., spectrum fragmentation, EDFA power consumption) and compute variables (e.g., GPU cycle utilization, VRAM allocation) for the assigned configuration $A^*$.
- $w_c$ is a weighting parameter balancing utility and cost.

## Constraints
Deploying LLMs at the orchestration layer shifts the bottleneck from purely optical bandwidth constraints to strict compute, cognitive, and latency boundaries:
1. **Task-Dependent Inference Latency Budget ($T_{total, i} \le T_{budget}(type(i))$):** Latency is modeled as a task-dependent budget rather than a fixed threshold. Intent parsing may tolerate relaxed budgets (seconds), while operational reactions (e.g., failure recovery) require strict, sub-second real-time bounds.
2. **Semantic Distortion Bound ($D_{sem} \le D_{max}$):** The loss of decision-relevant information during the telemetry-to-prompt transformation is strictly bounded. $D_{sem}$ is quantified as the reconstruction error on key state variables (e.g., QoT, load): $|| S_{true} - \hat{S}_{LLM} ||^2 \le D_{max}$, or as the measured degradation in task-level performance when using compressed vs. full telemetry.
3. **Context Window Saturation ($N_{tokens} \le N_{max}$):** Raw telemetry must be pre-compressed into a semantic Knowledge Graph or compact prompt template prior to inference to avoid context limits and hallucination.
4. **VRAM and Compute Limits ($M_{LLM} \le M_{Server}$):** The orchestrator is strictly constrained by the available GPU VRAM at the deployment site.
5. **Policy Safety & Grammar Validation:** Output policies must pass strict schema verification (grammar/syntax checks) before being deployed to physical optical controllers.