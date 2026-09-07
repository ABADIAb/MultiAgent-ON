---
title: "Chapter 3 - Section 3.1: Formal Problem Definition"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, problem-definition, mathematical-formulation, optical-networks]
status: draft
---

# 3.1 Formal Problem Definition

## 3.1.1 Architectural Vulnerabilities in LLM-Driven Optical Intent Planning

The automated translation of high-level operator intent into operational physical-layer configurations in Software-Defined Optical Networks (SDON) introduces fundamental architectural vulnerabilities when relying solely on generative Large Language Models (LLMs) \cite{bekri_bridging_2025} \cite{hachimi_flow-rule_2025} \cite{zacarias_enhancing_2026}. Optical transport networks operate under strict physical-layer limitations governed by nonlinear propagation physics, where configuration errors can cause widespread service degradation, optical amplifier saturation, or transponder damage \cite{soumplis_network_2017} \cite{cruzes_telemetry_2026} \cite{damico_gnpy_2026}. Current generative paradigms exhibit five interconnected failure modes that compromise operational integrity:

1. **Token Budget Saturation and Attention Degradation:** Modern optical topologies described via standard Network Configuration Protocol (NETCONF) or Representational State Transfer Configuration Protocol (RESTCONF) data models, or Transport API (T-API) northbound interfaces, generate extensive JSON/YANG payloads \cite{cruzes_telemetry_2026} \cite{gharbaoui_assurance_2026} \cite{ahmadian_t-api-compliant_2026}. Injecting complete network state representations into the LLM context window exhausts token budgets ($T_{context} \ge T_{max}$) and triggers attention degradation—commonly characterized as the "lost-in-the-middle" phenomenon \cite{ahmadian_t-api-compliant_2026} \cite{di_cicco_open_2024}. Consequently, long-horizon dependency constraints and critical intermediate node attributes are omitted during prompt synthesis \cite{du_memory_2026}.
2. **Hallucinated Physical Feasibility:** Generative autoregressive models operate as probabilistic token predictors trained on textual distributions; they lack internal mathematical physics engines and cannot solve wave propagation equations. When tasked with route determination, the LLM hallucinates topological paths that appear syntactically plausible but violate Generalized Signal-to-Noise Ratio (GSNR) margins \cite{bekri_bridging_2025} \cite{zhang_autoonbench_2026}.
3. **Semantic Drift in Iterative Intent Refinement:** Unconstrained multi-turn conversational interaction for intent disambiguation lacks formal convergence bounds \cite{bekri_bridging_2025} \cite{hachimi_flow-rule_2025}. When an operator introduces modifications in turn $t_k$, standard conversational memory may drop or mutate immutable boundary constraints established in turn $t_0$, causing semantic drift and infinite negotiation cycles \cite{wang_intent-driven_nodate} \cite{bekri_bridging_2025}.
4. **Reactive Post-Deployment Failure Latency:** Automated networking frameworks can rely on trial-and-error post-deployment execution. In such architectures, an unverified candidate configuration is pushed directly to the network controller or southbound interface (SBI); only after hardware or controller-level rejection does the system invoke an LLM retry loop \cite{hachimi_flow-rule_2025}. However, in high-capacity optical backbones, pushing unverified configurations introduces substantial control-plane latency and risks transient link disruptions \cite{cruzes_telemetry_2026}.
5. **Suboptimal Human-in-the-Loop Engagement:** Existing operational paradigms exhibit a binary interaction model: either mandatory operator review for every transaction (*always-on HITL*), causing cognitive fatigue and operational bottlenecks, or fully autonomous unverified deployment (*no-HITL*), exposing the transport layer to configuration faults \cite{zhang_ai_2026} \cite{zhang_autoonbench_2026} \cite{cruzes_telemetry_2026}. This is compounded by the fact that generative LLMs exhibit a documented failure to "fail early" and deterministically \cite{wang_intent-driven_nodate}. When presented with ambiguous operator inputs, rather than safely stopping and initiating a structured semantic clarification loop to resolve user-required errors, the model frequently fabricates missing physical parameters to force a deployment \cite{wang_intent-driven_nodate} \cite{bekri_bridging_2025}. Without mechanisms to dynamically assess the operational risk of a control command—distinguishing low-risk telemetry collection from high-risk optical power optimization—the agent cannot adapt its gating threshold to engage operators solely when calculated risks exceed acceptable safety boundaries \cite{cruzes_telemetry_2026} \cite{zhang_autoonbench_2026} \cite{liu_field_2026}.

To resolve these vulnerabilities, the intent-to-configuration lifecycle must be formulated as a pre-deployment, risk-bounded optimization problem that evaluates both linguistic ambiguity and physical transmission feasibility prior to network actuation.

---

## 3.1.2 Formal Mathematical Formulation

Given an unstructured natural language intent ($\mathcal{I}_{NL}$), an active topological and physical network state ($G, \mathbf{P}$), and a physical-layer feasibility threshold ($\text{GSNR}_{th}$), decide the formal symbolic specification ($\mathcal{S}_{PDDL}$), the optimal lightpath ($\pi^*$), and the pre-deployment control action ($a \in \mathcal{A}$), with the objective of minimizing the composite operational and computational friction ($\mathcal{J}$). The constraints of the problem are: maximum bounded token context limit, finite computational inference latency, restriction to $K$-shortest loopless paths, deterministic physical Quality of Transmission (QoT) feasibility, strict optical receiver dynamic range compliance, and bounded semantic ambiguity tolerance.

Let the optical physical topology be represented as a directed graph:

$$G = (V, E)$$

where $V = \{v_1, v_2, \dots, v_{|V|}\}$ denotes the set of optical network elements (Reconfigurable Optical Add-Drop Multiplexers, ROADMs, and transponder nodes) and $E = \{e_{ij} = (v_i, v_j) \mid v_i, v_j \in V\}$ represents the set of unidirectional fiber links connecting node pairs.

Each directed link $e_{ij} \in E$ is parameterized by a physical attribute tuple:

$$\mathbf{p}(e_{ij}) = \left( L_{ij}, \alpha_{ij}, D_{ij}, \gamma_{ij}, \mathcal{A}_{ij} \right)$$

where $L_{ij} \in \mathbb{R}^+$ denotes the link physical span length ($\text{km}$), $\alpha_{ij} \in \mathbb{R}^+$ represents the fiber attenuation coefficient ($\text{dB/km}$), $D_{ij}$ is the chromatic dispersion parameter ($\text{ps/(nm}\cdot\text{km)}$), $\gamma_{ij}$ is the nonlinear Kerr coefficient ($\text{W}^{-1}\text{km}^{-1}$), and $\mathcal{A}_{ij} = \{a_{ij, 1}, a_{ij, 2}, \dots, a_{ij, M}\}$ defines the ordered chain of $M$ optical inline amplifiers (Erbium-Doped Fiber Amplifiers, EDFAs) deployed along the link, each characterized by gain $G_{amp}$ ($\text{dB}$) and noise figure $NF$ ($\text{dB}$).

*Assumption 1 (Homogeneous Fiber Profile): While the formal model defines physical properties per link ($\alpha_{ij}, D_{ij}, \gamma_{ij}$), the practical evaluation testbed implemented in this thesis assumes a homogeneous standard single-mode fiber (e.g., SMF-28) across the entire topology, simplifying these parameters to global constants ($\alpha, D, \gamma$).*

### System Inputs (Given)

The intent planning architecture receives three primary inputs:

1. **Unstructured Natural Language Intent ($\mathcal{I}_{NL}$):** An informal string emitted by the network operator expressing routing requirements, explicit link exclusions, maximum latency constraints, and Quality of Service (QoS) specifications:
   $$\mathcal{I}_{NL} = \left( s, d, \mathcal{C}_{req} \right)$$
   where $s \in V$ is the source endpoint, $d \in V$ is the destination endpoint, and $\mathcal{C}_{req}$ denotes the set of expressed operational constraints.
2. **Topological and Physical Network State ($G, \mathbf{P}$):** The active topological graph $G(V, E)$ alongside the physical parameter space $\mathbf{P} = \{\mathbf{p}(e_{ij}) \mid e_{ij} \in E\}$.
3. **Physical-Layer Feasibility Threshold ($\text{GSNR}_{th}$):** The minimum acceptable Generalized Signal-to-Noise Ratio for the target modulation format:
   $$\text{GSNR}_{th} = \text{SNR}_{min} + \text{Margin}_{design} \quad [\text{dB}]$$

---

### Resource Constraints

The orchestration process is subject to finite operational and computational bounds:

1. **Token Context Limit:** The prompt context length $T_{prompt}$ supplied to the reasoning engine must remain bounded by the maximum effective attention threshold $T_{max}$:
   $$T_{prompt}(\mathcal{I}_{NL}, G_{sub}) \le T_{max} \ll T_{full}(G)$$
   where $G_{sub} \subseteq G$ represents a localized $k$-hop subtopology extracted via topological retrieval.
2. **Computational Inference Latency:** The end-to-end planning execution time $t_{exec}$ must satisfy:
   $$t_{exec} = t_{LLM} + t_{solver} + t_{QoT} \le t_{max\_budget}$$
   where $t_{LLM}$ is the cumulative generative inference latency of the LLM, $t_{solver}$ is the execution time of the deterministic path-finding algorithm, and $t_{QoT}$ is the physical feasibility computation time.
3. **Symbolic Solver Complexity:** Candidate path generation is restricted to the $K$-shortest loopless paths:
   $$\mathcal{K}_{path} = \{ \pi_1, \pi_2, \dots, \pi_K \}, \quad K \in [3, 5]$$
   Bounding $K$ mitigates the time complexity of Yen's algorithm in highly meshed topologies. A range of $K \in [3, 5]$ provides sufficient path diversity to ensure high probability of finding at least one physically feasible route, without violating the $t_{max\_budget}$.

---

### Decision Variables and Operational Action Space

The planning engine must determine:

1. The formal symbolic specification $\mathcal{S}_{PDDL}$ translating $\mathcal{I}_{NL}$ into Planning Domain Definition Language predicates:
   $$\mathcal{S}_{PDDL} = \mathcal{M}_{trans}(\mathcal{I}_{NL}, G_{sub})$$
2. The optimal lightpath $\pi^* \in \mathcal{K}_{path}$, defined as a sequence of connected nodes:
   $$\pi^* = (v_{(1)}, v_{(2)}, \dots, v_{(H)}), \quad v_{(1)} = s, \; v_{(H)} = d, \; (v_{(h)}, v_{(h+1)}) \in E$$
3. The pre-deployment control action $a \in \mathcal{A}$:
   $$\mathcal{A} = \{ \text{approve}, \text{clarify}, \text{replan} \}$$

---

### Physical and Semantic Boundary Constraints

A candidate path $\pi \in \mathcal{K}_{path}$ is strictly admissible if and only if it satisfies both deterministic physical-layer feasibility and semantic alignment:

1. **Deterministic Physical QoT Feasibility:** The accumulated Generalized Signal-to-Noise Ratio over path $\pi$, evaluated via the coherent Gaussian Noise (GN) model, and the received power $P_{rx}(\pi)$ at destination $d$ must meet their respective target thresholds to guarantee signal recovery. The combined physical validity indicator is defined as:
   $$\text{QoT}_{valid}(\pi) = \mathbb{I}\left( \text{GSNR}(\pi, \mathbf{P}) \ge \text{GSNR}_{th} \land P_{rx}(\pi) \ge P_{rx, min} \right) = 1$$

*Assumption 2 (Zero Equalization Loss & Filtered Network): The QoT GN-model evaluation assumes a filtered (ROADM-based) network architecture where equalization loss at intermediate nodes is neglected (all active channels are assumed to be equalized at uniform launch power).*

2. **Semantic Ambiguity Bound:** The semantic uncertainty metric $U_{sem} \in [0, 1]$, computed through structural CFG verification and reverse reconstruction alignment, must not exceed the tolerance threshold $\tau_{sem}$:
   $$U_{sem}(\mathcal{I}_{NL}, \mathcal{S}_{PDDL}) \le \tau_{sem}$$

---

### The Global Optimization Objective

In mission-critical optical transport, physical transmission safety is non-negotiable. Consequently, rather than formulating safety as a soft penalty within an unconstrained objective, physical feasibility and semantic certainty are enforced as strict pre-deployment hard constraints. 

The optimization objective minimizes composite operational and computational friction:

$$\min_{\mathcal{S}_{PDDL}, \pi^*} \mathcal{J} = \alpha \cdot N_{hitl}(\mathcal{I}_{NL}) + \beta \cdot T_{tokens}(\mathcal{I}_{NL})$$

$$\text{subject to:} \quad D\left( U_{sem}, \text{QoT}_{valid}(\pi^*) \right) = \text{approve}$$

$$\pi^* \in \mathcal{K}_{path}(G, \mathcal{S}_{PDDL})$$

where:
- $N_{hitl} \in \mathbb{N}_0$ denotes the number of operator interruptions triggered during the planning lifecycle.
- $T_{tokens} \in \mathbb{N}^+$ represents the total cumulative LLM token consumption.
- $\alpha \in \mathbb{R}^+$ and $\beta \in \mathbb{R}^+$ are weighting coefficients balancing human operator cognitive workload against computational inference costs. In this theoretical formulation, they act as operational policy parameters (OPEX) and normalization factors that project discrete human interaction events ($N_{hitl}$) and high-magnitude token consumption ($T_{tokens}$) into a unified evaluation scale. Exact empirical values for these parameters are defined by the specific testbed configuration during system evaluation.
- $D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$ enforces that no lightpath configuration reaches the network provisioning layer unless both semantic ambiguity and physical transmission infeasibility have been evaluated and resolved.

<!-- FIGURE_PLACEHOLDER: problem_formulation -->
> **Figure: Problem Formulation Block Diagram** (`figs_SystemModel/pdf/problem_formulation.pdf`)
> High-level transformation pipeline: unstructured operator intent $\mathcal{I}_{NL}$ and physical optical topology $G(V, E)$ mapped through the pre-deployment planning engine to yield admissible decision actions $a \in \{\text{approve}, \text{clarify}, \text{replan}\}$.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.1 Placement:** Place a high-level block diagram here illustrating the transformation flow: Unstructured Intent $\mathcal{I}_{NL}$ + Graph $G(V,E) \to$ Formal Formulation $\to$ Decision Action $a \in \{\text{approve}, \text{clarify}, \text{replan}\}$.
> 
> **Notation Consistency Check:** Ensure that $\text{GSNR}_{th}$, $U_{sem}$, and $\text{QoT}_{valid}$ symbols match identically across Chapter 3 and Chapter 5.
