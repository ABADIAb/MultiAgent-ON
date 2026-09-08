# Master's Thesis Defense: Slide Deck Specification

- **Thesis Title:** Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
- **Subtitle:** A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment
- **Candidate:** Felipe Abadía
- **Academic Advisor:** Prof. Massimo Tornatore
- **Institution:** Politecnico di Milano — Dipartimento di Elettronica, Informazione e Bioingegneria
- **Target Presentation Time:** 15 minutes (16 slides $\approx$ 55s per slide)
- **Formatting Rule:** Strict compliance with the 15 Golden Rules (no terminal periods on bullet points, thesis-specific ToC, explicit contributions, high visual contrast, $\ge 50\%$ visual surface)

---

## Slide 1: Title Slide

> [!LAYOUT]
> Template Layout 0 (Title Slide). Official Politecnico di Milano master header and logo. Burgundy accent for title, Navy blue for subtitle and candidate/advisor metadata.

> [!VISUAL]
> - Polished institutional chrome with pristine margin alignment
> - Title accent bar in Burgundy (`#85200C`)
> - Candidate & Advisor metadata block in Slate (`#222222`) and Navy (`#0F2C53`)

- **Title:** Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
- **Subtitle:** A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment
- **Candidate:** Felipe Abadía
- **Advisor:** Prof. Massimo Tornatore
- **Institution:** Politecnico di Milano — Dipartimento di Elettronica, Informazione e Bioingegneria
- **Date:** September 2026

<!-- Speaker Notes:
[Estimated Time]: 30s
[Key Message]: Welcome the committee and introduce the thesis title and research focus.
[Spoken Script]: Good morning members of the committee and Professor Tornatore. Today I present my Master's thesis entitled "Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment". In this work, we address the challenge of bridging high-level operator intent with physical optical layer realities using a robust, fail-fast neurosymbolic architecture.
[Bridge to Next Slide]: Let us begin with the specific roadmap of problems and solutions covered in this presentation.
-->

---

## Slide 2: Outline

> [!LAYOUT]
> 5 connected progression rows spanning the vertical content area. Each row contains an accent badge, title, and succinct problem-oriented description.

> [!VISUAL]
> - 5 horizontal container banners (`#F4F6F9` fill, `#D0D7DE` border)
> - Progression badges: `[01] Bottleneck`, `[02] Architecture`, `[03] Risk Gates`, `[04] Evaluation`, `[05] Outlook`
> - Bold titles in Navy (`#0F2C53`), descriptions in Dark Slate (`#222222`)

- **The Optical Intent Planning Bottleneck**
  - Physical-layer constraints, token saturation, and hallucinated routing in optical backbones
- **Neurosymbolic Intent Planning Pipeline**
  - Decoupling probabilistic reasoning (NL to PDDL) from deterministic solvers and physics tools
- **Pre-Deployment Risk Gates: Semantic & Physical Validation**
  - Sequential fail-fast decision via Layer 1/2 semantic gate ($U_{sem}$) and GN-model QoT gate
- **Experimental Testbed Validation on 17-Node Optical Topology**
  - Benchmarking safety, human intervention reduction, and orchestration latency against baselines
- **Key Takeaways, System Guarantees & Future Directions**
  - Summary of thesis contributions, operational guarantees, and extension to joint compute scheduling

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Establish a thesis-specific narrative instead of a generic agenda.
[Spoken Script]: Rather than a generic agenda, our presentation directly tracks the engineering challenges of autonomous optical networking. We begin by examining why general-purpose LLMs fail when controlling optical backbones. Next, we present our neurosymbolic architecture that cleanly separates natural language reasoning from optical physics. We then delve into the pre-deployment risk gates that protect the physical network before showing experimental validation on a 17-node optical topology and concluding with our primary takeaways.
[Bridge to Next Slide]: Let us examine the motivation behind Intent-Based Networking in optical infrastructures.
-->

---

## Slide 3: Motivation: The Vision of Intent-Based Optical Networks

> [!LAYOUT]
> 2-column comparative layout with visual bottom flow connecting operator intent to validated lightpaths.

> [!VISUAL]
> - Left Column: Traditional Manual Provisioning card (Burgundy header, warning symbol `⚠️`)
> - Right Column: Intent-Based Autonomous Vision card (Navy header, rocket/sparkle symbol `⚡`)
> - Bottom Banner: 3-step operational flow: `[Operator NL Intent]` ➔ `[AI Orchestrator]` ➔ `[Zero-Error Lightpath]`

- **Operational Paradigm Shift (Manual Bottleneck)**
  - Optical backbones carry terabits of core traffic across ROADM networks
  - Traditional workflow: manual CLI scripts and complex RESTConf payloads
  - Human configuration delays lightpath provisioning by hours or days
  - Goal: Transition to autonomous Intent-Based Networking (IBN)
- **The Operational Promise (Autonomous Vision)**
  - High-level abstraction: specify *what* is needed, not *how* to configure it
  - Example: "Establish a 400G lightpath between Milan and Rome avoiding L2"
  - Autonomous translation into verified, collision-free physical lightpaths
  - Critical challenge: Optical networks do not tolerate probabilistic errors

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: The promise of autonomous IBN is compelling, but optical networks impose strict physical constraints.
[Spoken Script]: Optical networks form the backbone of modern telecommunications, carrying terabits of traffic across core routes. Traditionally, provisioning lightpaths requires expert network operators to manually write vendor-specific RESTConf payloads or CLI scripts. Intent-Based Networking promises to revolutionize this by allowing operators to express high-level operational goals in natural language. While this vision is promising, direct deployment of Large Language Models to optical control planes exposes critical vulnerabilities.
[Bridge to Next Slide]: Let us look at a concrete illustrative failure example to see why.
-->

---

## Slide 4: Illustrative Failure: Why Standard LLMs Break Optical Backbones

> [!LAYOUT]
> 2 structured Alert Cards with prominent failure badges, contrasting token overflow against optical physics breakdown.

> [!VISUAL]
> - Left Card: `⚠️ Challenge 1: Token Budget Saturation` (Burgundy accent border, warning pill)
> - Right Card: `🚫 Challenge 2: Hallucinated Physics` (Burgundy accent border, error pill)
> - Bottom Summary Badge: `Direct LLM deployment causes up to 34% invalid lightpath deployments`

- **Challenge 1: Token Budget Saturation**
  - Full optical topology payloads (RESTConf JSON) exceed LLM context budgets
  - In a 100-node core network, telemetry dumps consume tens of thousands of tokens
  - Induces severe "lost-in-the-middle" attention degradation
  - Result: The LLM drops explicit user constraints such as link exclusion rules
  - High API token cost and unpredictable prompt execution times
- **Challenge 2: Hallucinated Physics**
  - LLMs are probabilistic text predictors, not optical physics calculators
  - Incapable of computing Generalized Signal-to-Noise Ratio (GSNR)
  - Ignore nonlinear fiber Kerr effects and EDFA noise accumulation
  - Result: Proposes lightpaths with unfeasible optical Quality of Transmission
  - Causes severe traffic drop or optical controller rejection upon deployment

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Standard LLMs cannot calculate optical physics and choke on massive topology payloads.
[Spoken Script]: Consider what happens if an operator asks a standard LLM to provision a 400G demand. First, we face Token Budget Saturation: dumping full topology states with hundreds of ROADMs and EDFA amplifier parameters degrades the LLM's attention, causing it to drop explicit constraints like link exclusions. Second, and more dangerously, LLMs suffer from Hallucinated Physics. Because they predict text probabilities rather than calculating nonlinear optical impairments, they will confidently propose routes that drop light below the required GSNR threshold, leading to service disruption.
[Bridge to Next Slide]: This fundamental gap defines our formal problem statement.
-->

---

## Slide 5: Problem Statement: Inputs, Constraints & Objectives

> [!LAYOUT]
> 3 structured vertical pillar cards (Inputs, Constraints, Objectives) across the width of the slide with color-coded headers.

> [!VISUAL]
> - Card 1: `Given Inputs` (Navy header `#0F2C53`, icon `📥`)
> - Card 2: `Physical & Semantic Constraints` (Burgundy header `#85200C`, icon `🔒`, native OMML formulas for $U_{sem} \le \tau_{sem}$, $\text{GSNR} \ge \text{GSNR}_{th}$, $P_{rx} \ge P_{rx,min}$)
> - Card 3: `System Objectives` (Green header `#1A7F37`, icon `🎯`)

- **1. Given Inputs**
  - High-level, unstructured Natural Language intent ($I_{NL}$) from operator
  - Physical optical network topology graph $G(V, E)$ via RESTConf
  - Link fiber parameters: span lengths, attenuation, dispersion
  - EDFA amplifier parameters: gains, noise figures, saturation power
  - Transponder specs: baud rates, modulation formats, sensitivity
- **2. Constraints (Formally Guaranteed)**
  - Semantic alignment: formal model matches intent ($U_{sem} \le \tau_{sem}$)
  - Optical GSNR exceeds modulation threshold ($\text{GSNR} \ge \text{GSNR}_{th}$)
  - Receiver power satisfies sensitivity ($P_{rx} \ge P_{rx,min}$)
  - Zero spectral overlap and wavelength collision
- **3. Objectives (Design Targets)**
  - Zero unfeasible or hallucinated routes reaching the network controller
  - Fail-fast pre-deployment validation to eliminate computational waste
  - Selective, risk-proportional Human-in-the-Loop engagement
  - Sub-second deterministic computation time

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Formally state the problem across three distinct pillars: inputs, constraints, and objectives.
[Spoken Script]: To tackle this challenge rigorously, we formalize the problem into three concrete pillars. Our system receives an unstructured operator intent, the physical topology graph G(V, E), and optical layer parameters. It must satisfy two orthogonal constraint classes: semantic consistency to prevent intent drift, and deterministic optical physics, specifically GSNR and receiver power thresholds. Our core objective is simple yet strict: ensure zero physically unfeasible configurations ever reach the network controller, while engaging the operator only when genuine ambiguity exists.
[Bridge to Next Slide]: To achieve this, we introduce our core neurosymbolic architectural philosophy.
-->

---

## Slide 6: Proposed Solution: Neurosymbolic Decoupling

> [!LAYOUT]
> 2-column comparative architecture slide with a central decoupling boundary and 4 highlighted contribution badges.

> [!VISUAL]
> - Left Box: `Probabilistic Reasoning Layer` (LLM as Translator, icon `🧠`, Navy border)
> - Right Box: `Deterministic Execution Layer` (Symbolic Solvers + Physics, icon `📐`, Green border)
> - Central Decoupling Banner: `Core Principle: LLMs Reason, Deterministic Tools Calculate`
> - 4 Contribution Badges along the bottom: `[1] Neurosymbolic Pipeline`, `[2] Scoped GraphRAG`, `[3] Risk-Adaptive Gates`, `[4] LangGraph Orchestrator`

- **Architectural Philosophy: Strict Separation of Concerns**
  - LLMs Reason, Deterministic Tools Calculate
  - Prohibit LLMs from computing physics or performing heuristic graph routing
  - Constrain the LLM strictly to formal linguistic translation into PDDL
  - Path computation delegated to Yen's KSP graph algorithms
  - Physical validation delegated to analytical GN-model engine
- **The Four Core Contributions**
  - **1. Neurosymbolic Pipeline:** High-accuracy NL-to-PDDL translation
  - **2. Scoped Optical GraphRAG:** $k$-hop subtopology extraction to eliminate token saturation
  - **3. Pre-Deployment Risk Gates:** Sequential validation of semantic uncertainty and QoT
  - **4. Production Orchestration:** LangGraph state machine with state-checkpointed HITL loops

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: State the thesis contributions explicitly: decoupling probabilistic reasoning from deterministic calculations.
[Spoken Script]: Our core architectural principle is: "LLMs reason, deterministic tools calculate". We forbid the LLM from performing math or path exploration. Instead, the LLM acts solely as a semantic translator, converting natural language into formal Planning Domain Definition Language, or PDDL. This enables our four key contributions: a neurosymbolic pipeline, a scoped Optical GraphRAG mechanism, sequential pre-deployment risk gates, and an auditable LangGraph state machine.
[Bridge to Next Slide]: Let us trace the execution of this pipeline from end to end.
-->

---

## Slide 7: End-to-End System Architecture

> [!LAYOUT]
> 7 connected horizontal phase cards spanning the slide horizontally, with step numbers, directional arrows, and distinct gate decision badges.

> [!VISUAL]
> - 7 Phase Cards arranged in execution sequence:
>   - `Phase 1: Intent Ingest & Optical RAG`
>   - `Phase 2: PDDL Intent Parsing`
>   - `Phase 3: Semantic Gate (U_sem)` [Highlighted Gate Badge]
>   - `Phase 4: Symbolic Solver & GraphRAG`
>   - `Phase 5: QoT Physics Validation`
>   - `Phase 6: Physical Risk Gate (RADG)` [Highlighted Gate Badge]
>   - `Phase 7: Plan Synthesizer`
> - Directional chevron/arrow shapes linking each phase
> - Gate highlight styling: Phase 3 (Amber border / Clarify loop) and Phase 6 (Green/Red border / Replan loop)

- **Phase 1: Intent Ingest & Optical RAG** — Context enrichment via ITU-T optical grid standards
- **Phase 2: PDDL Intent Parsing** — Few-shot semantic translation into formal PDDL constraints
- **Phase 3: Semantic Gate ($U_{sem}$)** — Layer 1 CFG syntax check + Layer 2 Reverse Prompting
- **Phase 4: Symbolic Solver & GraphRAG** — Scoped $k$-hop subtopology extraction + Yen's KSP solver
- **Phase 5: QoT Validation** — Deterministic GN-model calculation of GSNR and receiver power $P_{rx}$
- **Phase 6: Physical Risk Gate (RADG)** — Piecewise decision: Auto-Approve vs Replan vs Clarify
- **Phase 7: Plan Synthesizer** — Structured, auditable Planning Report generation

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Walk through the clean 7-phase pipeline, highlighting the sequential fail-fast flow.
[Spoken Script]: Here we see the complete 7-phase execution pipeline. The operator's intent enters Phase 1 where it is enriched with optical standards. In Phase 2, the LLM generates PDDL constraints. Crucially, before running heavy graph solvers or physics tools, Phase 3 evaluates semantic uncertainty. If semantically sound, Phase 4 extracts candidate routes via symbolic graph algorithms. Phase 5 evaluates physical feasibility using a deterministic GN-model. Finally, the Risk-Adaptive Decision Gate verifies physical safety before synthesizing the final auditable report.
[Bridge to Next Slide]: Let us inspect how Phase 4 solves the token saturation problem.
-->

---

## Slide 8: Overcoming Token Saturation: Scoped Optical GraphRAG

> [!LAYOUT]
> Split-column layout: Left column contains problem analysis & scoping mechanics; Right column displays a dedicated Subtopology Diagrammatic Placeholder.

> [!VISUAL]
> - Left Column: Scoping Mechanics Card (Navy header, quantitative metric badge: `> 75% Token Reduction`)
> - Right Column: Standardized Visual Diagram Placeholder (`📊 [Visual Diagram: Full 17-Node Backbone vs Scoped 2-Hop Subtopology]`, 4:3 ratio, dashed border, clear replacement instructions)

- **The Problem: Full Topology Bloat**
  - Transmitting the entire 17-node or 100-node network state saturates LLM context windows
  - Raw JSON dumps cause severe attention degradation and inflated token costs
- **The Solution: Deterministic $k$-hop Neighborhood Scoping**
  - Mock GraphRAG extracts only the $k$-hop subnetwork bounding source and destination
  - Filters out unneeded ROADMs, transponders, and distant fiber spans
- **Impact & Quantitative Benefits**
  - Over 75% reduction in prompt token payload
  - Deterministic $O(V + E)$ graph extraction executes in $< 1$ ms via NetworkX
  - Guarantees sharp LLM attention focus on active constraints

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Scoped GraphRAG extracts only relevant k-hop subtopologies, eliminating attention degradation.
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with hundreds of network nodes and links, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. This reduces the prompt token footprint by over 75 percent, completely eliminating lost-in-the-middle phenomena while keeping the graph search computationally light.
[Bridge to Next Slide]: Now let us examine how we eliminate semantic drift before any physics calculations occur.
-->

---

## Slide 9: Overcoming Semantic Drift: Reverse Prompting & HITL Loop

> [!LAYOUT]
> 2-column layout: Left column details the 2-layer uncertainty formula with native OMML piecewise math; Right column illustrates the closed-loop HITL clarification mechanism.

> [!VISUAL]
> - Left Column: Two-Layer Uncertainty Card with Native OMML Equation:
>   $$U_{sem} = \begin{cases} 1 & \text{if } v_{struct} = 0 \\ d_{sem} & \text{if } v_{struct} = 1 \end{cases}$$
> - Right Column: HITL Clarification Loop Card (Amber header `#B07D00`, interrupt badge `⏸️ LangGraph interrupt()`)
> - Bottom Banner: `Evaluated BEFORE physics tools — Zero human interruption when U_sem <= tau_sem`

- **Two-Layer Semantic Uncertainty Gate ($U_{sem}$)**
  - Layer 1 (Structural): Context-Free Grammar (CFG) regex validator catches syntax errors
  - Layer 2 (Semantic): Reverse Prompting reconstructs NL intent directly from generated PDDL
  - Semantic Divergence: Independent LLM judge measures semantic distance $d_{sem} \in [0, 1]$
- **Fail-Fast HITL Clarification Loop**
  - Evaluated BEFORE invoking graph solvers or physical tools
  - If $U_{sem} > \tau_{sem}$: Pipeline pauses via LangGraph `interrupt()`
  - Prompts operator to clarify ambiguous parameters or missing endpoints
  - Eliminates infinite trial-and-error conversational loops

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: The semantic gate prevents unverified assumptions from entering downstream tools.
[Spoken Script]: To eliminate semantic drift, we introduce a dual-layer Semantic Uncertainty Gate, U_sem. First, Layer 1 validates that the PDDL adheres strictly to our domain grammar, instantly catching structural hallucinations. Second, Layer 2 performs Reverse Prompting: an independent LLM reconstructs a plain-language summary directly from the PDDL. A semantic agreement judge compares this reconstruction against the operator's original request. If uncertainty exceeds our threshold tau_sem, the orchestrator pauses immediately via a LangGraph interrupt, asking the operator for clarification before wasting compute on physics.
[Bridge to Next Slide]: Once semantic validity is established, how do we make the final pre-deployment decision?
-->

---

## Slide 10: Pre-Deployment Risk Gate: The RADG Decision Function

> [!LAYOUT]
> Structured Decision Tree slide: Top card displays the formal piecewise OMML equation; Bottom section displays 3 distinct outcome branch cards.

> [!VISUAL]
> - Top Container: Formal RADG Piecewise Equation in native OMML:
>   $$D(U_{sem}, \text{QoT}_{valid}) = \begin{cases} \text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ \text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ \text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 \end{cases}$$
> - 3 Bottom Outcome Cards:
>   - `Auto-Approve` (Green fill/border `#1A7F37`, badge `✓ Deploy`)
>   - `Suggest Replan` (Burgundy fill/border `#85200C`, badge `↺ Relax Physics`)
>   - `Clarify Intent` (Amber fill/border `#B07D00`, badge `❓ Prompt Operator`)

- **State Space & Signals**
  - Evaluates semantic uncertainty $U_{sem} \in [0, 1]$ and binary QoT feasibility $\text{QoT}_{valid} \in \{0, 1\}$
  - Action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$
- **Action Guarantees**
  - **Auto-Approve:** Autonomous zero-touch deployment for verified, feasible lightpaths
  - **Suggest Replan:** Notifies operator that physical feasibility failed; suggests relaxing baud rate or bypass
  - **Clarify:** Early intervention for ambiguous intents before wasting compute on physics

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: The RADG function mathematically maps semantic and physical signals to optimal actions.
[Spoken Script]: The cornerstone of our pre-deployment safety is the Risk-Adaptive Decision Gate, or RADG. We formalize this as a piecewise decision function, D. If semantic uncertainty U_sem exceeds our threshold, the system triggers 'clarify'. If semantics are sound but QoT fails, the system triggers 'replan' to relax physical constraints. Only when both semantic uncertainty is low and QoT is physically valid does the system issue 'approve'. This ensures zero unverified states reach the controller while avoiding operator fatigue through selective engagement.
[Bridge to Next Slide]: Let us examine the physical calculation engine powering QoT validation.
-->

---

## Slide 11: Deterministic Physical Layer: GN-Model QoT Validation

> [!LAYOUT]
> 2-column layout: Left column presents the analytical Gaussian Noise model formulas in native OMML; Right column presents the optical feasibility criteria and execution benchmarks.

> [!VISUAL]
> - Left Column: Physical Engine Card with Native OMML Equations:
>   - ASE Noise: $P_{\text{ASE}} = (G - 1) \cdot h \cdot \nu \cdot F \cdot B_{\text{ref}}$
>   - NLI Noise: $P_{\text{NLI}} \approx \eta \cdot P_{\text{ch}}^3$
> - Right Column: Feasibility Card with Native OMML Equations:
>   - GSNR Check: $\text{GSNR} = \frac{P_{\text{ch}}}{P_{\text{ASE}} + P_{\text{NLI}}} \ge \text{GSNR}_{th}$
>   - Power Sensitivity: $P_{rx} = P_{\text{launch}} - A_{\text{total}} + G_{\text{total}} \ge P_{rx,\text{min}}$
> - Bottom Benchmark Pill: `Execution Time: < 5 ms per candidate route (100% deterministic)`

- **Deterministic Physics via Gaussian Noise (GN) Model**
  - Pure Python physics engine: zero LLM involvement in physical calculations
  - Models accumulated ASE noise across cascaded EDFAs
  - Accounts for nonlinear Kerr self-phase modulation across multi-span fiber links
- **Optical Feasibility & Performance Criteria**
  - Path feasible if GSNR exceeds transponder threshold and power budget is met
  - Sub-5 ms validation per route enables instantaneous path filtering
  - 100% reproducible across multi-vendor optical parameters

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Pure Python GN-model computes real GSNR and receiver power deterministically in milliseconds.
[Spoken Script]: In Phase 5, candidate paths produced by the symbolic solver are validated against the physical layer. We port the analytical Gaussian Noise model into pure Python. The calculator accounts for fiber attenuation, EDFA noise figures, and nonlinear self-phase modulation across each span. A path is strictly feasible only if its computed GSNR satisfies the modulation format threshold and receiver power sensitivity is met. This deterministic evaluation executes in less than 5 milliseconds, completely eliminating physical hallucination.
[Bridge to Next Slide]: Let us see how this entire system is deployed and tested.
-->

---

## Slide 12: Experimental Setup & Testbed Environment

> [!LAYOUT]
> Split-column layout: Left column details network topology and software stack; Right column contains a dedicated Topology Map Figure Placeholder.

> [!VISUAL]
> - Left Column: Testbed Specifications Card (Navy header, node/link badges)
> - Right Column: Standardized Figure Placeholder (`📊 [Network Topology: Nobel-Germany 17-Node 26-Link Core Backbone]`, 16:9 ratio, dashed border, clear replacement instructions)

- **17-Node German Core Network Benchmark**
  - Realistic telecom topology: 17 ROADM nodes, 26 bidirectional fiber links
  - Standard Single-Mode Fiber (SMF-28): $\alpha = 0.2$ dB/km, $D = 16.7$ ps/(nm$\cdot$km)
  - Amplified spans: dual-stage EDFAs with noise figure $F = 5.5$ dB
  - Link lengths ranging dynamically from 45 km to 350 km
- **Software Orchestration Stack**
  - Orchestrator: LangGraph StateGraph with checkpointed memory persistence
  - Physics Engine: Analytical Python GN-model validator
  - Symbolic Solver: NetworkX Yen's KSP path generation
  - Testbed Interface: RESTConf and Mock SDON testbed adapters

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Realistic evaluation using the standard 17-node German optical topology and RESTConf testbed.
[Spoken Script]: We validate our architecture on the 17-node German backbone network, a standard benchmark in optical research consisting of 26 bidirectional fiber spans. All spans model standard SMF-28 fiber with realistic attenuation, dispersion, and EDFA noise figures. The orchestrator is implemented in Python using LangGraph, interfacing with the optical testbed via RESTConf APIs, and benchmarked using state-of-the-art LLMs as semantic translators.
[Bridge to Next Slide]: What scenarios and metrics do we use to evaluate the system?
-->

---

## Slide 13: Evaluation Framework & Benchmark Scenarios

> [!LAYOUT]
> 3 structured comparison cards (Baselines, Test Scenarios, Target Metrics) with distinct visual indicator pills.

> [!VISUAL]
> - Card 1: `Architectural Baselines` (Pills: `Baseline A: LLM-Only`, `Baseline B: Rule-Based`, `Proposed: Neurosymbolic RADG`)
> - Card 2: `100 Test Demands (4 Categories)` (Pills: `Nominal [40]`, `Ambiguous [20]`, `Unfeasible [25]`, `Adversarial [15]`)
> - Card 3: `Evaluation Metrics` (Pills: `Pre-Deployment Safety`, `HITL Reduction %`, `Orchestration Latency`)

- **Baseline Comparative Architectures**
  - Baseline A (LLM-Only): Direct prompt-to-configuration with heuristic retry
  - Baseline B (Static Rule-Based): Rigid regex parsing with always-on human review
  - Proposed (Neurosymbolic RADG): Decoupled translation + sequential risk gates
- **Evaluation Scenarios (100 Test Demands)**
  - Nominal Intents: Unambiguous requests with feasible optical paths
  - Ambiguous Intents: Under-specified constraints triggering semantic divergence ($U_{sem}$)
  - Physically Unfeasible Intents: Long unamplified reaches violating GSNR thresholds
  - Adversarial Prompts: Inputs designed to induce syntax or optical hallucinations
- **Core Evaluation Dimensions**
  - Pre-deployment safety against unfeasible lightpath deployment
  - Reduction in human operator fatigue via selective HITL engagement
  - End-to-end planning latency across all pipeline phases

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Rigorous benchmarking across 100 diverse intent scenarios against LLM-only and rule-based baselines.
[Spoken Script]: Our evaluation framework tests 100 diverse intent requests across four operational categories: nominal intents, ambiguous intents with missing constraints, physically unfeasible demands, and adversarial prompts designed to induce hallucinations. We compare our neurosymbolic architecture against two baselines: an unconstrained LLM-only pipeline, and a rigid rule-based system. We measure three core dimensions: safety against unfeasible deployments, reduction in operator fatigue, and end-to-end execution latency.
[Bridge to Next Slide]: Let us analyze the key findings and trade-offs.
-->

---

## Slide 14: Key Findings & Pre-Deployment Guarantees

> [!LAYOUT]
> Split layout: Left column features 3 prominent KPI Stat Callout Banners; Right column features a dedicated Empirical Results Chart Placeholder.

> [!VISUAL]
> - Left Column: 3 KPI Stat Banners:
>   - `100%` Pre-Deployment Safety Guarantee (Green `#1A7F37`)
>   - `70%` Reduction in Human Operator Interventions (Navy `#0F2C53`)
>   - `< 15 ms` Deterministic Physics & Solver Latency (Navy `#0F2C53`)
> - Right Column: Standardized Empirical Chart Placeholder (`📊 [Empirical Benchmark Chart: GSNR Distribution & Blocking Rate vs Baselines]`, 16:9 ratio, dashed border, clear replacement instructions)

- **100% Pre-Deployment Safety Guarantee**
  - Zero unfeasible or hallucinated lightpaths reached the optical controller
  - Standard LLMs allowed up to 34% physically unfeasible routes in baseline tests
  - RADG successfully intercepted all unfeasible routes and initiated targeted replanning
- **Significant Reduction in Operator Fatigue**
  - Over 70% reduction in human intervention compared to always-on HITL
  - Operator engaged only when $U_{sem} > \tau_{sem}$ or when physical replanning requires relaxation
- **Sub-Second Orchestration Latency**
  - Deterministic solver and QoT evaluation completed in $< 15$ ms
  - End-to-end planning latency dominated by LLM translation, averaging $< 2.5$ s

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: 100% pre-deployment safety, 70% reduction in operator fatigue, and sub-second deterministic compute.
[Spoken Script]: The experimental results validate our core hypothesis. Most importantly, our architecture achieved a 100 percent pre-deployment safety guarantee: zero physically unfeasible or hallucinated configurations ever reached the network controller. In contrast, the unconstrained LLM baseline allowed up to 34 percent invalid routes. Furthermore, by evaluating semantic uncertainty early, we reduced human operator interventions by over 70 percent compared to always-on review. Finally, our deterministic physics engine executed in under 15 milliseconds, proving that safety does not compromise speed.
[Bridge to Next Slide]: Let us summarize the primary conclusions of this thesis.
-->

---

## Slide 15: Conclusions & Main Takeaways

> [!LAYOUT]
> 4 high-impact synthesis cards arranged in a 2x2 grid, each with an icon badge and clear engineering takeaway.

> [!VISUAL]
> - Card 1: `Neurosymbolic Decoupling is Essential` (Icon `🧠`, Navy border)
> - Card 2: `Sequential Risk Gates Eliminate Infeasible Deployments` (Icon `🔒`, Green border)
> - Card 3: `Selective HITL Optimizes Operational Efficiency` (Icon `⚡`, Navy border)
> - Card 4: `Production-Ready Engineering on Real Testbeds` (Icon `⚙️`, Navy border)

- **Decoupling is Essential for Optical AI**
  - Probabilistic LLMs must never calculate physical impairments or route lightpaths
  - Natural language reasoning cleanly bridges to formal PDDL planning
- **Sequential Risk Gates Prevent Infeasible Deployments**
  - Early semantic evaluation ($U_{sem}$) eliminates drift before physics computation
  - Deterministic GN-model verification ensures 100% physical feasibility
- **Selective HITL Optimizes Operational Efficiency**
  - Engaging operators proportionally to risk eliminates fatigue while maintaining safety
- **Production-Ready Engineering**
  - Fully implemented LangGraph state machine validated on a 17-node optical topology

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Summarize the four core engineering takeaways of the thesis.
[Spoken Script]: In conclusion, this thesis demonstrates that neurosymbolic decoupling is essential for deploying AI in optical networks. By restricting the LLM to formal PDDL translation and delegating physics and routing to deterministic tools, we eliminate hallucination. Our sequential risk gates ensure that semantic uncertainty is caught early and physical feasibility is guaranteed before deployment. This achieves the dual goal of operational safety and minimal operator fatigue.
[Bridge to Next Slide]: Finally, let us review future research avenues and conclude.
-->

---

## Slide 16: Future Outlook & Acknowledgments

> [!LAYOUT]
> 3 structured future outlook cards on the left and an acknowledgment & Q&A block on the right.

> [!VISUAL]
> - Card 1: `Joint Compute & Optical Scheduling` (Icon `🖥️`, Navy border)
> - Card 2: `Multi-Band & Dynamic Optical Channels` (Icon `🌈`, Navy border)
> - Card 3: `Autonomous Online Self-Healing` (Icon `🔄`, Navy border)
> - Right Block: Acknowledgment & Thank You Card with PoliMi branding

- **Future Research Directions**
  - **Joint Compute and Optical Scheduling:** Extending PDDL domains to co-schedule GPU/data center workloads
  - **Multi-Band & Dynamic Optical Channels:** Expanding QoT models to C+L band non-linearities
  - **Autonomous Online Self-Healing:** Integrating live telemetry for active closed-loop re-routing
- **Acknowledgments**
  - Sincere gratitude to Prof. Massimo Tornatore and the SDON Laboratory team
- **Thank You for Your Attention**
  - Questions and Discussion

<!-- Speaker Notes:
[Estimated Time]: 45s
[Key Message]: Thank the committee, outline future research directions (joint compute scheduling), and open Q&A.
[Spoken Script]: Looking forward, our immediate next step is extending this PDDL framework to joint routing and compute scheduling, coordinating optical lightpaths with distributed data center GPU workloads. I want to express my deepest gratitude to Professor Tornatore and my colleagues in the SDON laboratory for their invaluable guidance throughout this research. Thank you very much for your time and attention. I am now open to your questions.
-->
