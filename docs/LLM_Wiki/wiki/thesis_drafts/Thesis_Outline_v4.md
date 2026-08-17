---
title: "Thesis Outline Draft - V4"
date: 2026-08-12
tags: [thesis, outline, draft, citations]
status: active
---

# Summary
This document provides the fourth iteration of the thesis outline, incorporating structural feedback to elevate the theoretical discussion. The Problem Statement (Section 3.1) rigorously defines the system's inputs, constraints, and optimization objectives, reflecting the V5 architecture. Experimental setup uses a mock 17-node German topology.

# **Abstract** 

# **Abstract in lingua italiana** 

# **Contents** 
# **List of Figures** 
# **List of Tables** 

--------------------------------------------------------------------------------
# **1 Introduction** 
- **1.1 Overview and Motivation:** The shift from manual configuration towards Level-4 (L4) autonomous operations and Intent-Based Networking (IBN). How Large Language Models (LLMs) and Agentic AI are being adopted to interpret operator intents, alongside the severe physical and computational risks they introduce (Token Budget Saturation and Hallucinated Physics). The specific bottlenecks in translating human intent into physical optical configurations.
  - *Citations:* `[SOTA] ETSI_AI_in_the_evolution_of_Autonomous_Networks.pdf`; `[SOTA] Assurance_and_Conflict_Detection_in_Intent-Based_Networking...pdf`; `[SOTA] Netconfeval-Can_llms_facilitate_network_configuration.pdf`; `[SOTA] Open_Implementation_of_a_Large_Language_Model_Pipeline..._POLIMI.pdf`; `[[ProblemStatement_v5]]` (Formalizing the five bottlenecks).
- **1.2 Proposed Solution and Contributions:** Introduction of the Risk-Adaptive Decision Gate (RADG) and the strict separation of semantic reasoning from symbolic physical calculation.
  - *Citations:* `[[Architecture_v5]]` and `[[Scope_Pivot_20260706]]`.
- **1.3 Thesis Structure:** Brief description of the remaining chapters.

--------------------------------------------------------------------------------
# **2 Background and State of the Art** 

- **2.1 Agentic AI and Multi-Agent Systems in Intent-Driven Networks:** The evolution from monolithic LLMs to distributed, cooperative Multi-Agent Systems (MAS) for intent translation and network orchestration.
  - *Citations:* `[SOTA] Intent-Driven Network Management with Multi-Agent LLMs The.pdf`; `[SOTA] Field_trial_of_an_LLM-powered_AI_agent..._full-lifecycle_demonstration.pdf`; `[SOTA] LLM-Based_Multi-Agent_Architecture_for_Transport_Networks.pdf`; `[SOTA] Enhancing_Secure_Intent-Based_Networking_with_an_Agentic_AI_The_EU_Project_MARE.pdf`; `[SOTA] Agentic_AI_for_Scalable_and_Robust_Optical.pdf`; `[SOTA] IntentLLM_An_AI_Chatbot_to_Create_Find_and_Explain_Slice_Intents_in_TeraFlowSDN.pdf`.
- **2.2 Physical-Layer Constraints and QoT Estimation in Optical Network Planning:** Traditional physical-layer modeling (GN-model) and the fundamental limitations of purely generative LLMs in deterministic numerical analysis ("hallucinated physics").
  - *Citations:* `[SOTA] Network_Planning_With_Actual_Margins.pdf`; `[SOTA] GNPy_as_a_benchmark_for_open_and_disaggregated_optical_networks.pdf`; `[SOTA] JOCN2026_AutoONBench_a_benchmark_for_large_language_model_agents_in_autonomous_optical_networks 1.pdf`; `[SOTA] Scientific_Knowledge-driven_Decoding_Constraints_Improving_the_Reliability_of_LLMs.pdf`.
- **2.3 Intent Verification, Service Assurance, and Deployment Correction Strategies:** Contrasting closed-loop service assurance and pre-execution formal validation (CFG, PDDL) against reactive post-deployment retry paradigms.
  - *Citations:* `[SOTA] Assurance_and_Conflict_Detection_in_Intent-Based_Networking...Survey.pdf`; `[SOTA] ETSI_AI_in_the_evolution_of_Autonomous_Networks.pdf`; `[SOTA] Bridging_Language_Models_and_Formal_Methods_for_Intent-Driven_OpticalNetwork_Design.pdf`; `[SOTA] Flow-Rule_Generation_for_SDN_Using_LLMs_with_Retry-Based_Deployment_Validation.pdf`.
- **2.4 The Research Gap: Pre-Deployment Risk-Adaptive Neurosymbolic Verification:** The lack of joint sequential estimation of semantic uncertainty and physical-layer deterministic risk prior to deployment.
  - *Citations:* `[SOTA] Bridging_Language_Models_and_Formal_Methods_for_Intent-Driven_OpticalNetwork_Design.pdf`; `[SOTA] LOOP-A_Plug-and-Play_Neuro-Symbolic_Framework_for_Enhancing_Planning.pdf`.

--------------------------------------------------------------------------------
# **3 System Model: The Risk-Adaptive Neurosymbolic Architecture** 
- **3.1 Formal Problem Definition:** Detailed breakdown of Token Saturation, Hallucinated Physics, Semantic Drift, Post-Deployment Failure, and Suboptimal HITL Engagement. The core intent translation problem is rigorously formalized as:
  - **Given:** The initial physical network state $G(V,E)$ (extracted via GraphRAG), precise physical QoT parameters (fiber attenuation, amplifier gains), and the unstructured high-level operator intent.
  - **Resource Constraints:** LLM context window limits $T_{max}$ (protecting against Token Budget Saturation), API latency limits, and symbolic solver computation time bounds.
  - **Decide:** The optimal translation of linguistic intent into an executable, structurally valid sequence of physical configurations, OR the decision to fall back and engage the operator for clarification.
  - **Constrained by:** Deterministic physical QoT requirements ($\text{GSNR}_{computed} \ge \text{GSNR}_{threshold}$, receiver power thresholds) and strict semantic ambiguity thresholds ($U_{sem}$).
  - **Objective:** Minimize operational friction ($N_{hitl}$) and computational cost ($T_{tokens}$) subject to strict physical and semantic safety constraints. Physical safety is treated as a hard constraint (UAR = $0$) rather than a maximizable variable.
  - *Citations:* `[[ProblemStatement_v5]]`.
- **3.2 Conceptual Framework:** High-level introduction of the Risk-Adaptive Neurosymbolic Intent Planning system.
  - *Citations:* `[[Architecture_v5]]`.
- **3.3 Strict Neurosymbolic Separation:** Constraining the LLM to linguistic parsing (Intent $\to$ PDDL) and isolating the physics computations to deterministic symbolic solvers.
  - *Citations:* `[[Scope_Pivot_20260706]]`.
- **3.4 The Risk-Adaptive Decision Gate (RADG):** The core mathematical/logical pipeline evaluating semantic uncertainty ($U_{sem}$) and physical-layer QoT feasibility ($\text{QoT}_{valid}$) before deployment.
  - *Citations:* `[[Architecture_v5]]`.
- **3.5 Formal Human-In-The-Loop (HITL) via Reverse Prompting:** Bounding operator approvals to exact logical constraints to eliminate semantic drift during clarification.
  - *Citations:* `[[Architecture_v5]]`.

--------------------------------------------------------------------------------
# **4 Neurosymbolic Pipeline Implementation** 
- **4.1 Network State and Knowledge Graph (GraphRAG):** Solving token budget saturation by implementing a k-hop compressed topological GraphRAG to provide localized context.
  - *Citations:* `[[Architecture_v5]]`; `[SOTA] INTEGRATION_OF_LIVE_NETWORK_KNOWLEDGE_GRAPHS_WITH_RAG...pdf` (validating topology chunks and state embeddings); `[SOTA] How to improve multi-hop reasoning with knowledge graphs and LLMs` (general GraphRAG mechanics).
- **4.2 Semantic and QoT Validation Modules:** The mechanics of the threshold-based decision functions, specifically integrating a deterministic GN-model for exact GSNR and receiver power feasibility.
  - *Citations:* `[[ProblemStatement_v5]]`; `[SOTA] GNPy_as_a_benchmark_for_open_and_disaggregated_optical_networks.pdf` (to validate GN-model usage); `[SOTA] A_T-API-Compliant_ReAct_Agentic_Loop_for_Optical_Networks.pdf` (for T-API/GNPy integration).
- **4.3 Decision Outcomes:** The specific workflows resulting from the RADG: Auto-Approve, Clarify, and Suggest Replan.
  - *Citations:* `[[Architecture_v5]]`.

--------------------------------------------------------------------------------
# **5 Experimental Evaluation and Results** 
- **5.1 Experimental Setup:** Definition of the synthetic intent dataset, utilizing a **17-node German Mock Topology** to evaluate realistic fiber lengths and EDFA amplifier placement.
  - *Citations:* `[[Scope_Pivot_20260706]]` (experimental design).
- **5.2 Performance Metrics:** Unsafe Approval Rate (UAR), Human Interaction Count (HIC), QoT Feasibility Rate (QFR), End-to-End Latency (E2EL), and Token Cost (TC).
  - *Citations:* `[[Scope_Pivot_20260706]]`.
- **5.3 Performance under Safe Conditions:** Results data of the architecture autonomously processing unambiguous, QoT-valid intents. Integrates comparison against No-HITL and Always-HITL baselines.
- **5.4 Performance under Ambiguity:** Results data of the system engaging the HITL proportionally via reverse prompting when constraints are missing. Integrates comparison against the reactive-retry baseline.
- **5.5 Summary of Findings:** The computational and operational savings achieved by avoiding post-deployment failures and applying pre-deployment verification.
  - *Citations:* `[SOTA] Cost_and_accuracy_of_long-term_graph_memory_in_distributed_LLM-based_multi-agent_systems.pdf` (cross-referencing Token Cost savings).

--------------------------------------------------------------------------------
# **6 Conclusion and Future Work** 
- **6.1 Summary of Contributions:** Reiteration of the value of merging LLM semantic reasoning with formal PDDL constraint solving via the RADG.
- **6.2 Future Work:** Expanding the lightweight Python symbolic solver and Mock GraphRAG into production-grade orchestration platforms.
