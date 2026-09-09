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
> 2-column comparative layout with dedicated highlight callout blocks at the base of each column card, and visual bottom flow connecting operator intent to validated lightpaths.

> [!VISUAL]
> - Left Column Card: Traditional Manual Provisioning (Burgundy header `#85200C`, warning icon `⚠️`)
>   - Bullets: core traffic scale, manual RESTConf/CLI workflows, human provisioning latency, multi-vendor friction
>   - Highlight Callout Block: `🎯 Goal: Transition to autonomous Intent-Based Networking (IBN)`
> - Right Column Card: Intent-Based Autonomous Vision (Navy header `#0F2C53`, lightning icon `⚡`)
>   - Bullets: declarative abstraction ("what" not "how"), 400G carrier intent example, sub-second translation, automated verification
>   - Highlight Callout Block: `⚠️ Critical Challenge: Optical networks do not tolerate probabilistic errors`
> - Bottom Banner: 3-step operational flow: `[Operator NL Intent]` ➔ `[AI Intent Orchestrator]` ➔ `[Zero-Error Physical Lightpath]`

- **Operational Shift: Manual Bottleneck**
  - Optical backbones carry terabits of core traffic across ROADM networks
  - Traditional workflow: manual CLI scripts and complex RESTConf payloads
  - Human configuration delays lightpath provisioning by hours or days
  - High cognitive load and misconfiguration risk across multi-vendor links
  - *Highlighted Callout Block:*
    - 🎯 **Goal:** Transition to autonomous Intent-Based Networking (IBN)
- **The Operational Promise: Autonomous Vision**
  - High-level abstraction: specify *what* is needed, not *how* to configure it
  - Realistic carrier intent: "Establish a 400G lightpath between Milan and Rome avoiding link L2"
  - Autonomous translation into verified, collision-free physical lightpaths
  - Rapid sub-second provisioning reducing operational delays by orders of magnitude
  - *Highlighted Callout Block:*
    - ⚠️ **Critical Challenge:** Optical networks do not tolerate probabilistic errors

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Autonomous IBN promises agile multi-terabit provisioning, but the physical optical layer strictly demands deterministic zero-error execution.
[Spoken Script]: Optical transport networks form the fundamental backbone of modern telecommunications, carrying tens of terabits per second across meshed ROADM topologies. In traditional carrier operations, establishing a single lightpath is a heavily bottlenecked manual process: engineers must spend hours or days drafting vendor-specific CLI scripts and intricate RESTConf payloads, incurring severe human error risks. Intent-Based Networking promises to revolutionize this paradigm by allowing operators to express declarative high-level intents in natural language—for example, asking to provision a 400G lightpath between Milan and Rome avoiding a specific maintenance link. However, while generative AI can interpret human language, optical transport networks operate under rigid physical constraints where even minor probabilistic errors lead to catastrophic link failures.
[Bridge to Next Slide]: To see why general-purpose AI cannot simply be connected to an optical control plane, let us examine the five architectural failure modes that occur.
-->

---

## Slide 4: Illustrative Failure: Why Standard LLMs Break Optical Backbones

> [!LAYOUT]
> 5 distinct failure blocks with visual alert badges and concise core impact statements, grounded directly in the 5 failure modes of Section 3.1.1, accompanied by an overarching empirical risk banner.

> [!VISUAL]
> - 5 distinct horizontal failure blocks (`#F4F6F9` fill, `#D0D7DE` border, 1.2 pt):
>   - `[⚠️ 1. Token Budget Saturation]` Badge Burgundy `#85200C` ➔ *Telemetry dumps trigger attention degradation, dropping critical route exclusions*
>   - `[🚫 2. Hallucinated Physical Feasibility]` Badge Burgundy `#85200C` ➔ *Probabilistic predictors lack wave propagation engines, violating non-linear GSNR margins*
>   - `[🔄 3. Semantic Drift in Refinement]` Badge Burgundy `#85200C` ➔ *Unconstrained multi-turn conversational loops mutate or drop initial boundary constraints*
>   - `[⏱️ 4. Reactive Post-Deployment Latency]` Badge Burgundy `#85200C` ➔ *Trial-and-error configuration risks live outages and introduces high control-plane recovery latency*
>   - `[👥 5. Suboptimal HITL Engagement]` Badge Burgundy `#85200C` ➔ *Binary all-or-nothing review causes operator fatigue or outages; models fail to fail-early*
> - Bottom Summary Banner: `Empirical Risk: Unconstrained LLMs allow up to 34% unfeasible deployments, semantic drift loops, and critical control-plane latency`

- **1. Token Budget Saturation & Attention Degradation** (`⚠️`)
  - Massive topology dumps trigger attention degradation, dropping critical operator route exclusions
- **2. Hallucinated Physical Feasibility** (`🚫`)
  - Probabilistic predictors lack wave propagation engines, violating non-linear GSNR and noise margins
- **3. Semantic Drift in Iterative Intent Refinement** (`🔄`)
  - Unconstrained conversational refinement lacks convergence bounds, mutating initial boundary constraints
- **4. Reactive Post-Deployment Failure Latency** (`⏱️`)
  - Trial-and-error configuration risks live service disruption and introduces high control-plane recovery latency
- **5. Suboptimal Human-in-the-Loop Engagement** (`👥`)
  - Binary all-or-nothing review causes operator fatigue or outages; models fail to fail-early on ambiguity
- **Empirical Risk Summary Banner:**
  - Empirical Risk: Unconstrained LLMs allow up to 34% unfeasible deployments, semantic drift loops, and critical control-plane latency

<!-- Speaker Notes:
[Estimated Time]: 65s
[Key Message]: Connecting standard generative LLMs directly to optical control planes exposes five fundamental architectural failure modes.
[Spoken Script]: When we evaluate standard generative LLMs for optical network control, we observe five interconnected failure modes that compromise operational integrity:

1. Token Budget Saturation and Attention Degradation:
   - Modern optical topologies described via RESTConf, NETCONF, or T-API generate massive JSON payloads with hundreds of links and amplifiers.
   - Injecting complete network states exhausts token budgets and triggers the "lost-in-the-middle" attention degradation phenomenon.
   - Crucial long-horizon constraints—such as explicit link exclusions—are quietly dropped during prompt synthesis.

2. Hallucinated Physical Feasibility:
   - LLMs are autoregressive token predictors trained on text, not numerical physics engines.
   - They cannot solve wave propagation equations, compute Generalized Signal-to-Noise Ratio (GSNR), or account for nonlinear Kerr effects and EDFA noise accumulation.
   - The LLM generates syntactically plausible paths that violate physical margins, causing transponder receiver lock failure.

3. Semantic Drift in Iterative Intent Refinement:
   - Unstructured multi-turn conversational chat lacks formal mathematical convergence guarantees.
   - When an operator requests adjustments in turn k, standard conversational memory often mutates or drops immutable boundary constraints established in turn 0.
   - This traps the operator in endless negotiation loops without reaching a valid configuration state.

4. Reactive Post-Deployment Failure Latency:
   - Existing LLM networking frameworks rely on trial-and-error post-deployment execution, pushing unverified configurations directly to the controller.
   - Configuration faults are detected only after hardware or SBI rejection, incurring high control-plane latency and risking transient optical link disruption.

5. Suboptimal Human-in-the-Loop Engagement:
   - Operational paradigms are locked into a flawed binary choice: either mandatory review for every single request (always-on HITL, causing operator fatigue) or fully autonomous deployment (no-HITL, risking catastrophic physical failures).
   - Furthermore, LLMs fail to "fail-early"; when presented with ambiguous intent, they fabricate missing parameters instead of initiating structured clarification.
   - There is no mechanism to engage the operator proportionally to the assessed operational risk.

[Bridge to Next Slide]: To overcome these five failure modes, we must formally structure the optical intent problem with hard physical constraints.
-->

---

## Slide 5: Problem Statement: Given, Decide, Objective & Constraints

> [!LAYOUT]
> 2-tier structured optimization layout: Upper half contains a 3-column row (Given, Decide, Objective) side-by-side; Lower half is dedicated to Constraints, split into Resource Constraints (left) and Boundary Constraints (right), with all mathematical variables and expressions in formal notation.

> [!VISUAL]
> - Top Row (Upper Half - 3 Cards Side-by-Side):
>   - Card 1 (Left): `[1] Given (System Inputs)` (Navy header `#0F2C53`, icon `📥`)
>   - Card 2 (Center): `[2] Decide (Variables & Actions)` (Navy header `#0F2C53`, icon `⚙️`)
>   - Card 3 (Right): `[3] Objective (Optimization Goal)` (Green header `#1A7F37`, icon `🎯`)
> - Bottom Tier (Lower Half - Full-Width Constraints Container with 2 Sub-Panels):
>   - Header Bar: `[4] Constraints (Resource Limits vs. Physical & Semantic Boundaries)` (Burgundy `#85200C`, icon `🔒`)
>   - Left Sub-Panel: `Resource Constraints (System & Solver Limits)`
>   - Right Sub-Panel: `Boundary Constraints (Physical & Semantic Feasibility)`

- **1. Given (System Inputs)**
  - Unstructured operator intent: $\mathcal{I}_{NL}$
  - Active optical topology graph: $G(V, E)$ via RESTConf
  - Physical parameters: link span length $L$, attenuation $\alpha$, amplifier gain $G_m$
  - Physical feasibility threshold: $\text{GSNR}_{th} = \text{SNR}_{min} + \text{Margin}$
- **2. Decide (Variables & Actions)**
  - Formal symbolic specification: $\mathcal{S}_{PDDL}$ compiled from intent
  - Optimal physical lightpath route: $\pi^* \in \mathcal{K}_{path}$ from candidate paths
  - Pre-deployment control action: $a \in \{\text{approve}, \text{clarify}, \text{replan}\}$
  - Provisioning routing configuration: $c^*$ dispatched to controller
- **3. Objective (Optimization Goal)**
  - Minimize composite operational friction: $\min \mathcal{J} = \alpha \cdot N_{hitl} + \beta \cdot T_{tokens}$
  - Cut operator cognitive fatigue: $\min N_{hitl}$ (minimize human interruptions)
  - Bound compute expense and latency: $\min T_{tokens}$ (minimize prompt tokens)
  - Hard pre-deployment safety guarantee: $\mathcal{D}(U_{sem}, \text{QoT}_{valid}) = \text{approve}$
- **4. Constraints (Resource Limits vs. Boundary Conditions)**
  - **Resource Constraints (Left Column):**
    - Localized prompt context window bound: $T_{prompt} \le T_{max} \ll T_{full}$ (via subtopology $G_{sub}$)
    - Strict end-to-end execution latency budget: $t_{exec} \le t_{max\_budget}$
    - Bounded path search complexity: $K\text{-SP}$ with $K \in [3, 5]$
  - **Boundary Constraints (Right Column):**
    - Zero semantic drift tolerance bound: $U_{sem} \le \tau_{sem}$
    - Deterministic optical QoT feasibility: $\text{GSNR}(\pi^*) \ge \text{GSNR}_{th} \land P_{rx}(\pi^*) \ge P_{rx,min}$
    - Pre-deployment physical validity state: $\text{QoT}_{valid} \in \{0, 1\}$

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Formally formulate the problem across four structured dimensions: Given inputs, Decision variables, Objective function, and Constraints (Resource vs Boundary).
[Spoken Script]: Following the classical telecommunications optimization methodology, we formulate our intent planning problem across four precise dimensions: Given, Decide, Objective, and Constraints.
In the upper row, first, Given: the orchestrator ingests the unstructured natural language intent I_NL from the operator, queries the active network graph G(V, E) via RESTConf, and loads physical parameters—fiber attenuation alpha, span lengths L, and EDFA amplifier gains G_m—along with the required transmission feasibility threshold GSNR_th.
Second, Decide: the system determines the formal symbolic PDDL specification S_PDDL, selects the optimal physical route pi* among candidate loopless paths, resolves the pre-deployment control action a in {approve, clarify, replan}, and generates the final configuration c*.
Third, Objective: we formulate a multi-objective cost function min J = alpha * N_hitl + beta * T_tokens. We explicitly minimize human operator interruptions N_hitl to prevent cognitive fatigue, while minimizing prompt token consumption T_tokens to bound compute costs and latency, under the hard invariant that no lightpath is deployed unless the pre-deployment risk decision equals approve.
In the lower half, our Constraints are decoupled into two distinct categories:
On the left, Resource Constraints bound the prompt context window T_prompt <= T_max << T_full through scoped subtopologies, enforce a strict execution latency budget t_exec <= t_max_budget, and limit the symbolic solver complexity to K-shortest paths.
On the right, Boundary Constraints enforce zero semantic drift tolerance (U_sem <= tau_sem), deterministic optical QoT feasibility (GSNR >= GSNR_th and P_rx >= P_rx,min), and binary pre-deployment validity QoT_valid in {0, 1}.
[Bridge to Next Slide]: To solve this constrained optimization problem, we introduce our neurosymbolic architectural philosophy.
-->

---

## Slide 6: Proposed Solution: Neurosymbolic Decoupling

> [!LAYOUT]
> 2-column comparative architecture slide: Left column features two vertically stacked subsystem cards (Neural Subsystem: Semantic Domain on top, and Symbolic Subsystem: Optical Domain on bottom); Right column features a prominent "Core Thesis Contributions (Architectural Novelties)" container with 3 vertically stacked highlight blocks one below the other.

> [!VISUAL]
> - Left Column (Vertically Stacked Subsystems - $w=5.7''$, $x=0.75''$):
>   - Top Card: `🧠 Neural Subsystem (Semantic Domain)` (Navy header `#0F2C53`, linguistic compiler, early fail-fast gate)
>   - Bottom Card: `📐 Symbolic Subsystem (Optical Domain)` (Green header `#1A7F37`, deterministic solvers, late physical risk gate)
> - Right Column (Core Thesis Contributions - $w=5.75''$, $x=6.8''$):
>   - Container Header Bar: `🎯 Core Thesis Contributions (Architectural Novelties)` (Navy bar `#0F2C53`)
>   - 3 Vertically Stacked Highlight Blocks (Cards with colored borders):
>     - Block 1: `1. Neurosymbolic Decoupling & Scoped GraphRAG` (Navy border `#0F2C53`)
>     - Block 2: `2. Dual-Layer Semantic Uncertainty Gate ($U_{sem}$)` (Amber border `#B07D00`)
>     - Block 3: `3. Risk-Adaptive Decision Gate (RADG) & QoT` (Green border `#1A7F37`)

- **Left Column: Decoupled Subsystems**
  - **Neural Subsystem (Semantic Domain)** (`🧠`)
    - Translates unstructured natural language $\mathcal{I}_{NL}$ into formal PDDL $\mathcal{S}_{PDDL}$
    - Zero routing arithmetic or physical SNR calculations performed by LLM
    - Reverse prompting reconstructs intent $\mathcal{I}_{recon}$ for validation
    - Interpretable intermediate representation prevents hallucinated configurations
  - **Symbolic Subsystem (Optical Domain)** (`📐`)
    - Subtopology extraction via scoped Mock GraphRAG ($k\text{-hop}$ neighborhood)
    - Deterministic routing via Yen's $K\text{-SP}$ constrained graph algorithm
    - Physical QoT validation via pure Python analytical GN-model engine
    - Evaluates $\text{GSNR} \ge \text{GSNR}_{th}$ and $P_{rx} \ge P_{rx,min}$ with zero hallucination
- **Right Column: Core Thesis Contributions (3 Stacked Blocks)**
  - **1. Neurosymbolic Decoupling & Scoped GraphRAG**
    - Strict separation: probabilistic semantic translation vs deterministic physics
    - Subtopology scoping reduces prompt tokens by >75%, eliminating attention loss
  - **2. Dual-Layer Semantic Uncertainty Gate ($U_{sem}$)**
    - Layer 1 syntax check ($v_{struct} \in \{0, 1\}$) + Layer 2 semantic discrepancy ($d_{sem}$)
    - Pauses via LangGraph `interrupt()` when $U_{sem} > \tau_{sem}$ to clarify ambiguity
  - **3. Risk-Adaptive Decision Gate (RADG) & QoT**
    - Piecewise decision $D(U_{sem}, \text{QoT}_{valid})$: clarify, replan, or auto-approve
    - Guarantees $\text{UAR} = 100\%$ physical safety with <5 ms calculation latency

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: State the thesis contributions explicitly: decoupling probabilistic reasoning from deterministic calculations.
[Spoken Script]: Our core architectural principle is: 'LLMs reason, deterministic tools calculate'. We forbid the LLM from performing math or path exploration. Instead, the LLM acts solely as a semantic translator, converting natural language into formal Planning Domain Definition Language, or PDDL. This enables our four key contributions: a neurosymbolic pipeline, a scoped Optical GraphRAG mechanism, sequential pre-deployment risk gates, and an auditable LangGraph state machine.
[Bridge to Next Slide]: Let us trace the execution of this pipeline from end to end across all seven phases.
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
> Split-column layout: Left column contains problem analysis & scoping mechanics; Right column displays an animated 17-node German network topology container with 2-step subnetwork scoping.

> [!VISUAL]
> - Left Column: Scoping Mechanics Card (Navy header, quantitative metric badge: `> 75% Token Reduction`)
> - Right Column: 17-Node German Core Network Scoping Card with Entrance Click Animation:
>   - Step 1 (Base State): Full 17-node German backbone topology (`assets/germany_17nodes.png`)
>   - Step 2 (On Advance / Click): Scoped subtopology overlay (`assets/germany_17nodes_opaco.jpg`) with opacified northern nodes, highlighting localized Frankfurt–Munich subnetwork
>   - Bottom Callout: `⚡ Frankfurt ➔ Munich demand: Northern nodes pruned from LLM prompt`

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
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with the entire 17-node topology, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. For instance, [Click / Advance] if an operator requests a lightpath between Frankfurt and Munich, there is no need to load northern nodes like Hamburg, Bremen, or Berlin into the LLM context. We prune distant nodes and links, reducing the prompt token footprint by over 75 percent, eliminating the lost-in-the-middle phenomenon while keeping the graph search computationally instantaneous.
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
  - Layer 1 (Structural): Context-Free Grammar (CFG) AST validator catches syntax errors
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
>   - ASE Noise: $P_{ASE, m} = (G_m - 1) \cdot h \nu \cdot R_s \cdot NF_m$
>   - NLI Noise: $P_{NLI, m} = \eta_0 L_{eff}^2 P_{ch}^3$
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
> - Right Column: 17-Node Nobel-Germany Core Network Topology Map (`germany_17nodes.png`, container card with Navy header bar and caption callout)

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
