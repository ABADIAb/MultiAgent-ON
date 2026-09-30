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
- **1.2 Proposed Solution and Contributions:** Introduction of the Risk-Adaptive Decision Gates (RADGs) and the strict separation of semantic reasoning from symbolic physical calculation.
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
- **2.4 The Research Gap: Pre-Deployment Risk-Adaptive Decision Gates and HITL Optimization:** The lack of a pre-deployment RADGs pipeline that jointly evaluates semantic certainty and physical-layer deterministic risk to fundamentally optimize Human-in-the-Loop (HITL) operator interventions, minimizing cognitive overload while ensuring deterministic physical feasibility.
  - *Citations:* `[SOTA] Bridging_Language_Models_and_Formal_Methods_for_Intent-Driven_OpticalNetwork_Design.pdf`; `[SOTA] LOOP-A_Plug-and-Play_Neuro-Symbolic_Framework_for_Enhancing_Planning.pdf`.

--------------------------------------------------------------------------------
# **3 System Model and Neurosymbolic Architecture**
- **3.1 Formal Problem Definition:** Formulation of the intent-to-configuration lifecycle as a pre-deployment constrained optimization problem.
  - *3.1.1 System Inputs:* Unstructured natural language intent $\mathcal{I}_{NL} = (s, d, \mathcal{C}_{req})$, topological network state $G(V,E)$ and physical parameter space $\mathbf{P} = \{\mathbf{p}(e_{ij}) \mid e_{ij} \in E\}$ with link attribute tuples $\mathbf{p}(e_{ij}) = (L_{ij}, \alpha_{ij}, D_{ij}, \gamma_{ij}, \mathcal{A}_{ij})$ (Remark on Homogeneous Fiber Profile assuming standard SMF-28 constants), and physical-layer feasibility threshold $\text{GSNR}_{th} = \text{SNR}_{min} + \text{Margin}_{design}$.
  - *3.1.2 Resource Constraints:* Token budget bounding $T_{prompt}(\mathcal{I}_{NL}, G_{sub}) \le T_{max} \ll T_{full}(G)$ via localized $k$-hop subtopology extraction, computational inference latency bound $t_{exec} = t_{LLM} + t_{solver} + t_{QoT} \le t_{max\_budget}$, and candidate path cardinality bounding $\mathcal{K}_{path} = \{\pi_1, \dots, \pi_K\}$ ($K \in [3, 5]$).
  - *3.1.3 Physical and Semantic Boundary Constraints:* Deterministic physical feasibility $\text{QoT}_{valid}(\pi) = \mathbb{I}(\text{GSNR}(\pi, \mathbf{P}) \ge \text{GSNR}_{th} \land P_{rx}(\pi) \ge P_{rx, min}) = 1$ (Remark on Zero Equalization Loss in ROADM-filtered network) and semantic ambiguity bound $U_{sem}(\mathcal{I}_{NL}, \mathcal{S}_{PDDL}) \le \tau_{sem}$.
  - *3.1.4 Decision Variables and Operational Action Space:* Symbolic specification $\mathcal{S}_{PDDL} = \mathcal{M}_{trans}(\mathcal{I}_{NL}, G_{sub})$, optimal lightpath $\pi^* \in \mathcal{K}_{path}$, and pre-deployment control action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$.
  - *3.1.5 The Global Optimization Objective:* Bi-objective formulation minimizing human operational friction and computational token consumption subject to strict pre-deployment hard gating:
    $$\min_{\mathcal{S}_{PDDL}, \pi^*} \mathcal{J} = w_1 \cdot N_{hitl}(\mathcal{I}_{NL}) + w_2 \cdot T_{tokens}(\mathcal{I}_{NL}) \quad \text{s.t.} \quad D(U_{sem}, \text{QoT}_{valid}(\pi^*)) = \text{approve}, \quad \pi^* \in \mathcal{K}_{path}$$
  - *Citations & Grounding:* `[[ProblemStatement_v5]]`, `[[Architecture_v5]]`.
- **3.2 Proposed Neurosymbolic Framework:**
  - *3.2.1 The Fail-Fast Pre-Deployment Architecture:* Contrasting the fail-fast pre-deployment hierarchy (evaluating linguistic certainty in the semantic domain before invoking optical simulations) against reactive post-deployment trial-and-error retry loops.
  - *3.2.2 End-to-End Pipeline Overview:* Walkthrough of the seven functional phases coordinated across the linguistic reasoning domain (Phases 1–3), deterministic physical domain (Phases 4–6), and control-plane synthesis interface (Phase 7):
    - *Phase 1 (Intent Ingestion & Optical RAG):* Raw intent ingestion and localized $k$-hop subtopology extraction ($G_{sub} \subseteq G$).
    - *Phase 2 (CFG-Validated PDDL Parsing):* LLM translation to PDDL goal clauses and immediate deterministic CFG validation ($v_{struct} \in \{0, 1\}$).
    - *Phase 3 (Automated Reverse Prompting & Semantic RADG):* Autonomous Phase 3a PDDL-to-NL reconstruction ($\mathcal{I}_{recon}$), Gate 1 $U_{sem}$ evaluation, and conditional Phase 3b HITL clarification interrupt.
    - *Phase 4 (Deterministic Symbolic Solver):* Yen's $K$-Shortest Paths over pruned subtopology $\widetilde{G}_{sub}$.
    - *Phase 5 (Deterministic QoT Validation):* Analytical GN-model physics calculation across candidate lightpaths.
    - *Phase 6 (Physical RADG):* Gate 2 binary feasibility verification ($\text{QoT}_{valid}$), auto-approval, or Phase 6 Suggest Replan interrupt for constraint relaxation.
    - *Phase 7 (Plan Synthesis & Provisioning):* Auditable Planning Report compilation.
    - *Visual Artifact:* `Figure~\ref{fig:conceptual_framework}` (`conceptual_framework.pdf`) depicting the 7-phase pipeline, Gate 1 ($U_{sem}$), Gate 2 ($\text{QoT}_{valid}$), and closed-loop feedback trajectories.
  - *3.2.3 State Representation and Transaction Lifecycle:* Append-only state tuple $\mathcal{S}_{state} = \langle \mathcal{I}_{enriched}, G_{sub}, \mathcal{S}_{PDDL}, U_{sem}, \mathcal{K}_{path}, \mathbf{\Gamma}_{QoT}, \mathcal{D}_{action}, \mathcal{H}_{trace}, \mathcal{H}_{refine}, \kappa_{refine} \rangle$, deterministic state transitions, audit trail preservation, and iteration bounding ($\kappa_{refine} \le N_{max} = 3$).
  - *Citations & Grounding:* `[[Architecture_v5]]`, `[[Scope_Pivot_20260706]]`.
- **3.3 Strict Neurosymbolic Separation:** Isolating neural translation from deterministic graph traversal and optical physics.
  - *3.3.1 Functional Delegation in Network Configuration:* Eliminating LLM hallucinated physics by restricting the neural engine strictly to semantic translation and delegating path-finding and QoT to deterministic symbolic modules.
  - *3.3.2 PDDL Domain Formalization for Optical Routing:* Optical routing domain specifications:
    - *Listing 3.1:* Formal PDDL Domain Type Hierarchy (`node`, `roadm`, `transponder`, `link`).
    - *Listing 3.2:* Predicate Definitions (`connected`, `route`, `avoid-node`, `avoid-link`, `max-hops`, `min-gsnr`).
    - *Listing 3.3:* Sample PDDL Goal Specification (`route`, `avoid-node`, `min-gsnr`).
  - *3.3.3 Context-Free Grammar Structural Validation:* Formal S-expression production rules $\mathcal{R}_{pddl}$ (Formal Specification 3.1) evaluating structural indicator $v_{struct} \in \{0, 1\}$. Structural invalidity ($v_{struct} = 0$) forces maximum uncertainty $U_{sem} = 1.0$.
  - *3.3.4 Deterministic Symbolic Solver and Graph Traversal:* Topological vertex pruning ($\widetilde{V}_{sub} = V_{sub} \setminus \{u \mid \text{avoid-node}(u)\}$), topological edge pruning ($\widetilde{E}_{sub}$ excluding $\text{avoid-link}$ pairs), Yen's $K$-Shortest Paths search ($K=5$), and hop constraint enforcement ($|\pi| \le h_{max}$).
  - *Citations & Grounding:* `src/core/pddl_validator.py`, `src/core/symbolic_solver.py`.
- **3.4 The Risk-Adaptive Decision Gates:** The core control logic evaluating operational risk across semantic and physical domains.
  - *3.4.1 Mathematical Formulation of the RADG Decision Function:* Deterministic piecewise decision function $D(U_{sem}, \text{QoT}_{valid})$ mapping to $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$ with calibrated tolerance threshold $\tau_{sem} = 0.30$. Software-level hierarchical decoupling (Phase 3 Gate 1 vs Phase 6 Gate 2).
    - *Visual Artifact:* `Figure~\ref{fig:radg_decision_space}` (`radg_decision_space.pdf`) mapping Zone I (Auto-Approve), Zone II (Suggest Replan), and Zone III (Early HITL Clarify) across $U_{sem}$ vs $\Delta\text{GSNR}$.
  - *3.4.2 Two-Layer Semantic Uncertainty Quantification:* Layer 1 CFG validity ($v_{struct}$) + Layer 2 Reverse Prompting semantic divergence ($d_{sem}$ via independent LLM-as-a-judge), aggregated as $U_{sem} = 1.0$ if $v_{struct}=0$ else $d_{sem}$.
  - *3.4.3 Deterministic Physical-Layer QoT Evaluation:* Analytical Gaussian Noise (GN) model for uncompensated optical transmission:
    - Amplified Spontaneous Emission (ASE) noise power: $P_{ASE,m} = (G_m - 1) h \nu R_s NF_m$, $\text{OSNR}_{ASE}^{-1}(e_{ij}) = \sum (P_{ASE,m}/P_{ch})$.
    - Non-Linear Interference (NLI) Kerr distortion: $\eta_0$, $P_{NLI,m} = \eta_0 L_{eff}^2 P_{ch}^3$, $\text{SNR}_{NLI}^{-1}(e_{ij}) = \sum (P_{NLI,m}/P_{ch})$.
    - Generalized SNR accumulation: $\text{GSNR}(\pi)^{-1} = \text{SNR}_{tx,lin}^{-1} + \sum (\text{OSNR}_{ASE}^{-1} + \text{SNR}_{NLI}^{-1})$ with transponder ceiling $\text{SNR}_{trx,dB} = 26.0\text{ dB}$, and $\text{GSNR}_{dB}(\pi)$.
    - Power allocation and launch strategy (static baseline profile).
    - Binary QoT feasibility indicator $\text{QoT}_{valid} \in \{0, 1\}$.
  - *3.4.4 Proportional Human-in-the-Loop Re-Entry:* Decoupled intervention checkpoints: Semantic Interrupt at Phase 3b ($U_{sem} > \tau_{sem}$) vs Physical Interrupt at Phase 6 ($\text{QoT}_{valid} = 0$) with failure telemetry and parameter relaxation suggestions.
  - *3.4.5 Constraint Preservation and Convergence Guarantees:* Monotonic constraint update equation $\mathcal{C}_{k+1} = \mathcal{C}_k \cup \text{Extract}(\mathcal{F}_k) \setminus \text{Revocations}(\mathcal{F}_k)$, state dictionary persistence, and strict iteration bound $N_{max} = 3$ preventing control-plane deadlocks.
  - *Citations & Grounding:* `src/core/radg.py`, `src/core/semantic_gate.py`, `src/core/qot_calculator.py`, `[SOTA] GNPy_as_a_benchmark...pdf`.

--------------------------------------------------------------------------------
# **4 Neurosymbolic Pipeline Implementation**
- **4.1 Orchestration and Pipeline Architecture:**
  - *4.1.1 LangGraph State Machine Architecture and State Schema:* Directed acyclic state machine realizing the 7-phase pipeline, conditional routing edges at Gate 1 (Phase 3) and Gate 2 (Phase 6), and asynchronous `interrupt()` suspension.
    - *Listing 4.1:* Master Orchestration State Schema (`AgentState` TypedDict).
    - *State Persistence and Checkpointing:* Thread-level serialized snapshots for pause/resume without thread blocking.
  - *4.1.2 Pipeline-to-Node Execution Mapping:* Direct 1:1 mapping of Phases 1 through 7 to decorated Python node functions (`intent_ingest_node`, `pddl_parser_node`, `semantic_gate_node`, `symbolic_solver_node`, `qot_validation_node`, `radg_node`, `plan_synthesizer_node`).
  - *Citations & Grounding:* `src/core/graph.py`, `src/core/state.py`, `[SOTA] LangGraph_2024`.
- **4.2 Network Context and Subtopology Extraction:**
  - *4.2.1 Optical Network Abstraction and Physical Testbed Modeling:* Undirected graph abstraction $G(V,E)$ modeling ROADM hubs (`NetworkNode`) and physical fiber lines (`FiberLink`, `Amplifier`).
    - *Listing 4.2:* Optical Network Domain Models (`Amplifier` and `FiberLink` with span length, EDFA gains/noise figures, active channels, port loss).
    - *Topology Grounding:* SNDlib 17-node German core backbone network (17 nodes, 26 bidirectional links, spans 37.5\,km to 381.9\,km).
  - *4.2.2 Scoped Subtopology Extraction via Mock GraphRAG:* Mitigating RESTConf/YANG token saturation via $k$-hop neighborhood extraction $V_{sub} = \mathcal{N}_k(s) \cup \mathcal{N}_k(d)$ ($k=2$). Bounding prompt size to $T_{prompt} \ll T_{full}(G)$ to eliminate attention degradation.
  - *Citations & Grounding:* `src/core/mock_graphrag.py`, `src/services/testbed_client.py`, `[SOTA] SNDlib_2010`.
- **4.3 The Semantic Engine:** Software implementation of linguistic reasoning and Gate 1.
  - *4.3.1 Natural Language Intent Ingestion and Structured Extraction:* Dynamic subtopology context injection and constrained Pydantic schema extraction.
    - *Prevention of Lossy Numerical Abstraction:* Preserving verbatim operator input in `active_intent` to avoid artificial semantic divergence.
  - *4.3.2 Multi-Turn Intent Reconciliation and Disambiguation:* Structured classification model eliminating ghost constraint leakage:
    - *Listing 4.3:* Intent Reconciliation Resolution Schema (`IntentResolutionType`: `FULL_REPLACEMENT` vs `PARTIAL_UPDATE`). Dynamic GraphRAG subtopology rescoping upon endpoint alteration.
  - *4.3.3 Context-Free Grammar (CFG) AST PDDL Validation:* Deterministic two-stage S-expression parser: Tokenization with nesting depth tracking, and Recursive AST Builder applying type- and arity-checking against $\mathcal{R}_{pddl}$ ($v_{struct} \in \{0, 1\}$).
  - *4.3.4 Automated Reverse Prompting and Semantic Agreement Scoring:* Closed-loop Phase 3a execution with zero human intervention.
    - *Automated PDDL-to-NL Reconstruction:* Prompt filtering stripping topological artifacts before reconstruction.
    - *Semantic Agreement Evaluation:* Independent LLM Agreement Judge computing semantic divergence $d_{sem}$.
  - *4.3.5 Semantic RADG Execution:* Gate 1 multiplexer implementing $D(U_{sem}, \text{QoT}_{valid})$: Branch A Autonomous Pass ($U_{sem} \le \tau_{sem}$) vs Branch B Fail-Fast Interruption ($U_{sem} > \tau_{sem}$) triggering Phase 3b `interrupt()`.
  - *Citations & Grounding:* `src/nodes/intent_ingest.py`, `src/nodes/pddl_parser.py`, `src/core/pddl_validator.py`, `src/nodes/reverse_prompt.py`, `src/core/semantic_gate.py`, `src/nodes/semantic_gate_node.py`.
- **4.4 The Physical Engine and Feasibility Validation:**
  - *4.4.1 The Deterministic Symbolic Solver:* Non-neural Yen's $K$-Shortest Paths over pruned graph $\widetilde{G}_{sub}$, enforcing topological vertex/edge pruning and hop limits prior to physical evaluation.
  - *4.4.2 GN-Model Quality of Transmission Engine:* Analytical Python implementation of the Gaussian Noise model:
    - *Listing 4.4:* Analytical GN calculation functions (`span_snr` per amplified span and `calculate_demand_snr` across cascaded links with ASE and NLI accumulation).
  - *4.4.3 Physical RADG Execution Mechanics:* Gate 2 execution: Branch A Approve ($\text{QoT}_{valid} = 1$) forward to Phase 7 vs Branch B Replan ($\text{QoT}_{valid} = 0$) suspending at Phase 6 `interrupt()` with telemetry for constraint relaxation.
  - *4.4.4 Proportional Human-in-the-Loop Engagement and Re-Entry Protocols:* Decoupled Phase 3b and Phase 6 checkpoints, fast-track manual override, safety bound $N_{max} = 3$, and constraint preservation enforcement.
  - *Citations & Grounding:* `src/core/symbolic_solver.py`, `src/core/qot_calculator.py`, `src/tools/qot_tool.py`, `src/core/radg.py`, `src/nodes/radg_node.py`.
- **4.5 Plan Synthesis and Verification:**
  - *4.5.1 Plan Synthesis and Auditable Provisioning Trace:* Synthesizing verified candidate paths, physical telemetry, and RADG decision metrics into an auditable Planning Report.
    - *Listing 4.5:* Structure of the Synthesized Planning Report (JSON schema).
  - *4.5.2 Verification of the Seven Execution Paths:* Verification suite validating the 7 canonical operational flows: (1) Single-Pass Auto-Approve, (2) Semantic Clarification Loop, (3) Fast-Track Manual Override, (4) Physical Replan Loop, (5) Complex Topological Constraints, (6) Topology Edge Cases & Disconnection, (7) Multi-Interruption Persistence.
  - *Citations & Grounding:* `src/nodes/plan_synthesizer.py`, `tests/unit/test_e2e_pipeline_flow.py`.

--------------------------------------------------------------------------------
# **5 Experimental Evaluation and Results**
- **5.1 Experimental Setup:**
  - *5.1.1 Network Topology and Physical Parameters:* Simulated 17-node German core backbone network (SNDlib), 26 bidirectional links (spans 37.5\,km to 381.9\,km), SMF-28 fiber ($\alpha = 0.25$\,dB/km, $\gamma = 1.27$\,W$^{-1}$km$^{-1}$, $|\beta_2| = 21.7\times 10^{-27}$\,s$^2$/m), polynomial EDFA gain/noise figure models (boosters/ILAs $[10, 23]$\,dB gain / $[6, 12]$\,dB NF, preamps $[18, 32]$\,dB gain / $[6.2, 10.5]$\,dB NF), transponder back-to-back 26\,dB floor, modulation-dependent GSNR thresholds (100G QPSK 8.6\,dB, 200G 16-QAM 15.2\,dB), and receiver sensitivity bounds $P_{rx} \in [-18.0, -8.0]$\,dBm.
    - *Visual Artifact:* `Figure~\ref{fig:17-node-german}` (`17_node_german.png`) depicting the national core topology and metropolitan switching centers.
  - *5.1.2 LLMs Under Evaluation:* Three distinct backends evaluated across the complete 120-demand corpus: Qwen 2.5 3B (local 3B SLM on RTX 3050), GPT-6 Luna (cloud SOTA reasoning), GPT-5 Nano (cloud high-throughput).
  - *5.1.3 Benchmark Corpus and Diurnal Risk Classes:* 24-hour diurnal operational shift model comprising 120 demands across 4 balanced risk classes (30 demands each): Class I (Nominal), Class II (Ambiguous), Class III (Physically Infeasible), Class IV (Adversarial).
  - *5.1.4 Baseline Architectures:* Proposed RADG (dual pre-deployment gates), Always-On HITL (mandatory review on all traffic), LLM-Only (un-gated with RFC 8040 RESTCONF controller rejection error payloads and reactive recovery loops).
  - *5.1.5 Performance Metrics: The Four Validation Pillars:*
    - Pillar 1 (Semantic Translation): Constraint Retention Rate ($\text{CRR}$), CFG Pass Rate ($\text{CFG-PR}$), Semantic Agreement ($1 - d_{sem}$).
    - Pillar 2 (Physical Feasibility & Transmission Integrity): False Positive Rate ($\text{FPR}$, target $0.0\%$), Physical Infeasibility Interception Rate ($\text{PIIR}$).
    - Pillar 3 (Efficiency & Operator Friction): End-to-End Latency ($T_{E2E}$, median & mean), Token Footprint ($T_{tokens}$, median & mean), Mean HITL Interventions ($\bar{N}_{hitl}$), Task Completion Rate ($\text{TCR}$).
    - Pillar 4 (Gate Reliability & Autonomy): Gate Decision Accuracy ($\text{GDA}$, target $\ge 95\%$), Selective HITL Precision.
- **5.2 Intra-Model Comparative Analysis:** (Representative backend: GPT-6 Luna over full 120-demand corpus).
  - *5.2.1 The Alert Fatigue Dilemma: Why Always-On HITL Fails:* 30 redundant nominal interrupts (116 vs 86 total), Selective HITL Precision collapses from 100.0\% to 74.1\%, +15.0\% token inflation (139k tokens wasted), +17.2\% latency increase.
    - *Table 5.1:* Operator friction and computational comparison on GPT-6 Luna.
    - *Visual Artifact:* `Figure~\ref{fig:scalability_projection_luna}` (`comparative_scalability_projection.pdf`) modeling cumulative operator intervention trajectory ($N_{hitl}$), proving 30 averted interventions and a 25.9\% fatigue reduction.
  - *5.2.2 The Post-Deployment Error Dilemma: Why LLM-Only Fails:* Forwarding 100\% of traffic to controller admission causes 90 controller incidents, $\text{FPR} = 100.0\%$, $\text{GDA} = 25.0\%$, and $\text{PIIR} = 0.0\%$. RFC 8040 error recovery inflates median token usage by 72.9\% (9,200 to 15,908 tok) and median latency by 85.8\% (15.89\,s to 29.52\,s).
    - *Table 5.2:* Transmission integrity and computational impact of LLM-Only.
    - *Visual Artifact:* `Figure~\ref{fig:comparative_deployment_flow_sankey}` (`comparative_deployment_flow_sankey.pdf`) 3-stage Sankey deployment flow contrasting 72\% pre-deployment interception (with transparent 4-leak bifurcation) against 90 blind controller failures in LLM-Only.
  - *5.2.3 Computational Efficiency: Latency Distribution and Token Footprint:*
    - *Visual Artifact:* `Figure~\ref{fig:comparative_efficiency_pillars}` (`comparative_efficiency_pillars.pdf`) boxplot turnaround latency distributions across risk classes and stacked bar token decomposition (useful compute vs wasted overhead).
    - Always-On HITL imposes a 121.5\% nominal latency penalty and 54.0\% wasted nominal tokens; LLM-Only wastes 41.5\%--44.1\% compute on unconverged recovery loops.
  - *5.2.4 The RADG Synthesis: Resolving Operational Tradeoffs:* Demonstrating Pareto optimality: 100.0\% nominal autonomy, 96.7\% GDA, 90.0\% PIIR, and FPR confined to 4.4\%.
    - *Table 5.3:* Executive Four-Pillar Summary for GPT-6 Luna across all 3 baselines.
- **5.3 Cross-Model Sensitivity Analysis:** (Multi-model evaluation across Qwen 2.5 3B, GPT-6 Luna, GPT-5 Nano on 120 demands).
  - *5.3.1 Gate Decision Accuracy and Risk Interception Across LLM Backends:*
    - *Visual Artifact:* `Figure~\ref{fig:cross_model_gate_accuracy}` (`cross_model_gate_accuracy.pdf`) per-class initial risk interception stacked action distribution + Cleveland lollipop scale for GDA and FPR against the $\text{GDA} \ge 95\%$ benchmark target.
    - Performance breakdown: Qwen 96.7\% GDA / 1.1\% FPR; Luna 96.7\% GDA / 4.4\% FPR; Nano 88.3\% GDA / 10.0\% FPR.
    - *Table 5.4:* Cross-model comparison of gate decision and integrity metrics.
  - *5.3.2 The Model-Agnostic Physical Integrity Invariant and Semantic Sensitivity:* Decomposition into a model-agnostic deterministic physical integrity floor ($\text{PIIR} \ge 83.3\%$) and an LLM-sensitive semantic discrimination boundary (governing FPR). Qwen's conservative ambiguity detection yields 1.1\% FPR.
  - *5.3.3 Efficiency Variability: Latency and Token Footprint Across Backends:*
    - *Table 5.5:* Computational efficiency across LLM backends.
    - Architectural stability of token footprint (~8.7k--9.2k median tokens). Local SLM execution dynamics: fastest median latency (13.19\,s) but tail latency on multi-turn adversarial demands (mean 25.76\,s, 2 timeouts) vs cloud API 100\% TCR.
- **5.4 Discussion and Limitations:**
  - *5.4.1 On the False Positive Rate and Architectural Levers:* Physics invariance (zero Class III unintercepted reach violations) and the semantic threshold lever ($\tau_{sem}$ calibration from 0.30 to 0.15 driving $\text{FPR} \to 0.0\%$).
  - *5.4.2 Corpus Scope and Topology Generalization:* 120-demand corpus representation and scaling from national core (17-node) to continental/transoceanic topologies.
  - *5.4.3 Threats to Validity:* Internal (programmatic HITL responses), external (3 LLM backends, GN-model formulation), and construct (uniform FPR weighting).
- **5.5 Summary of Findings:**
  - *Table 5.6:* Consolidated Four-Pillar comparative evaluation matrix ($3\text{ models} \times 3\text{ baselines} \times 4\text{ pillars}$, 120 demands).
  - Three core conclusions: (1) Pre-deployment gating prevents controller-side collapse, (2) Selective risk-adaptive gating eliminates operator alert fatigue, (3) Physical transmission integrity is an invariant architectural property.
  - Bridge to Chapter 6.
--------------------------------------------------------------------------------
# **6 Conclusion and Future Work** 
- **6.1 Summary of Contributions:** Reiteration of the value of merging LLM semantic reasoning with formal PDDL constraint solving via the RADGs.
- **6.2 Future Work:** Expanding the lightweight Python symbolic solver and Mock GraphRAG into production-grade orchestration platforms.
