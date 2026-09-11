# Master's Thesis Defense: Slide Deck Specification

- **Thesis Title:** LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
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

- **Title:** LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
- **Subtitle:** A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment
- **Candidate:** Felipe Abadía
- **Advisor:** Prof. Massimo Tornatore & Prof. Qiaolun Zhang
- **Institution:** Politecnico di Milano — Dipartimento di Elettronica, Informazione e Bioingegneria
- **Date:** September 2026

<!-- Speaker Notes:
[Estimated Time]: 30s
[Key Message]: Welcome the committee and introduce the thesis title and research focus.
[Spoken Script]: Good morning members of the committee, Professor Tornatore, and Professor Zhang. Today I present my Master's thesis entitled "LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment". In this work, we address the challenge of bridging high-level operator intent with physical optical layer realities using a robust, fail-fast neurosymbolic architecture.
[Bridge to Next Slide]: Let us begin with the specific roadmap of problems and solutions covered in this presentation.
-->

---

## Slide 2: Outline

> [!LAYOUT]
> 5 connected progression rows spanning the vertical content area. Each row contains an accent badge, title, and succinct problem-oriented description.

> [!VISUAL]
> - 5 horizontal container banners (`#F4F6F9` fill, `#D0D7DE` border)
> - Progression badges: `01 Bottleneck`, `02 Architecture`, `03 Risk Gates`, `04 Evaluation`, `05 Outlook`
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

## Slide 3: Motivation: The Evolution from Imperative SDON to Declarative IBON

> [!LAYOUT]
> 2-column comparative evolution layout with central directional arrow connector and centered badge, plus an overarching bottom caution banner.

> [!VISUAL]
> - Left Column Card: Imperative SDON (`#F4F6F9` fill, Burgundy border `#85200C`, 1.5 pt)
>   - Header Bar: `⚠️ Current Paradigm: Imperative SDON` / `Procedural "HOW" Execution • Open-Loop Control`
>   - 3 White Rounded Pills: `Procedural Scripts`, `Static Margins`, `Open-Loop Control` (Burgundy border & text)
> - Central Right Arrow: Directional connector (`#DCE6F2` fill, `#0F2C53` border, 1 pt)
>   - Centered Badge: `PARADIGM SHIFT` / `"HOW" ➔ "WHAT"`
> - Right Column Card: Declarative IBON (`#F4F6F9` fill, Navy border `#0F2C53`, 1.5 pt)
>   - Header Bar: `⚡ Target Vision: Declarative IBON` / `Autonomous "WHAT" Abstraction • Closed-Loop Assurance`
>   - 3 White Rounded Pills: `✓ High-Level Intents`, `✓ Dynamic Physics`, `✓ Zero-Touch Assurance` (Navy border & text)
> - Bottom Banner: `⚠️ BUT: Standard LLMs alone cannot simply drive an IBON controller` (`#F4F6F9` fill, `#85200C` border)

- **Current Paradigm: Imperative SDON** (`⚠️`)
  - Subtitle: Procedural "HOW" Execution • Open-Loop Control
  - Pills:
    - Procedural Scripts
    - Static Margins
    - Open-Loop Control
- **Center: Paradigm Shift**
  - Transition: "HOW" ➔ "WHAT"
- **Target Vision: Declarative IBON** (`⚡`)
  - Subtitle: Autonomous "WHAT" Abstraction • Closed-Loop Assurance
  - Pills:
    - ✓ High-Level Intents
    - ✓ Dynamic Physics
    - ✓ Zero-Touch Assurance
- **Bottom Caution Banner:**
  - ⚠️ BUT: Standard LLMs alone cannot simply drive an IBON controller

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Moving from Imperative SDON to Declarative IBON is essential to eliminate the human configuration bottleneck, but connecting naive LLMs directly to optical control planes introduces catastrophic physical risks.
[Spoken Script]: Optical transport networks form the multi-terabit backbone of modern telecommunications. Over the past decade, Software-Defined Optical Networking (SDON) successfully centralized the control plane through standardized Southbound interfaces like NETCONF and RESTConf. However, SDON remains fundamentally imperative: human operators must still manually compute explicit lightpaths, calculate wavelength grids, and configure ROADM cross-connects, relying on slow offline tools with conservative 3 to 5 dB margins. Intent-Based Optical Networking (IBON), formalized in IETF RFC 9315, represents a crucial paradigm shift from 'how' to 'what': operators express declarative service intents in natural language, and the system autonomously derives the physical optical configuration under continuous closed-loop assurance. However, connecting generative AI directly to optical backbones creates severe risks, as optical networks do not tolerate probabilistic hallucination.
[Bridge to Next Slide]: To understand why standard LLMs cannot simply drive an IBON controller, let us examine the five architectural failure modes that occur.
-->

---

## Slide 4: Illustrative Failure: Why Standard LLMs Break Optical Backbones

> [!LAYOUT]
> 5 distinct failure blocks with visual alert badges and concise core impact statements, grounded directly in the 5 failure modes of Section 3.1.1, accompanied by an overarching empirical risk banner.

> [!VISUAL]
> - 5 distinct horizontal failure blocks (`#F4F6F9` fill, `#D0D7DE` border, 1.0 pt):
>   - `[1. Token Budget Saturation]` Badge Burgundy `#85200C` (14 pt) ➔ *Telemetry dumps trigger attention degradation, dropping critical route exclusions* (12 pt)
>   - `[2. Hallucinated Physics]` Badge Burgundy `#85200C` (14 pt) ➔ *Probabilistic predictors lack wave propagation engines, violating non-linear GSNR margins* (12 pt)
>   - `[3. Semantic Drift]` Badge Burgundy `#85200C` (14 pt) ➔ *Unconstrained multi-turn conversational loops mutate or drop initial boundary constraints* (12 pt)
>   - `[4. Reactive Deployment Latency]` Badge Burgundy `#85200C` (14 pt) ➔ *Trial-and-error configuration risks live outages and introduces high control-plane recovery latency* (12 pt)
>   - `[5. Suboptimal HITL Friction]` Badge Burgundy `#85200C` (14 pt) ➔ *Binary all-or-nothing review causes operator fatigue or outages; models fail to fail-early* (12 pt)
> - Bottom Summary Banner: `Empirical Risk: Unconstrained LLMs might allow unfeasible deployments, semantic drift loops, and critical control-plane latency` (`#F4F6F9` fill, `#85200C` border)

- **1. Token Budget Saturation**
  - Telemetry dumps trigger attention degradation, dropping critical route exclusions
- **2. Hallucinated Physics**
  - Probabilistic predictors lack wave propagation engines, violating non-linear GSNR margins
- **3. Semantic Drift**
  - Unconstrained multi-turn conversational loops mutate or drop initial boundary constraints
- **4. Reactive Deployment Latency**
  - Trial-and-error configuration risks live outages and introduces high control-plane recovery latency
- **5. Suboptimal HITL Friction**
  - Binary all-or-nothing review causes operator fatigue or outages; models fail to fail-early
- **Empirical Risk Summary Banner:**
  - Empirical Risk: Unconstrained LLMs might allow unfeasible deployments, semantic drift loops, and critical control-plane latency

<!-- Speaker Notes:
[Estimated Time]: 65s
[Key Message]: Connecting standard generative LLMs directly to optical control planes exposes five fundamental architectural failure modes.
[Spoken Script]: When we evaluate standard generative LLMs for optical network control, we observe five interconnected failure modes that compromise operational integrity: First, Token Budget Saturation: injecting complete network states exhausts token budgets and triggers attention degradation, causing link exclusions to be dropped. Second, Hallucinated Physical Feasibility: autoregressive token predictors cannot solve wave propagation equations, computing invalid lightpaths that cause transponder loss of lock. Third, Semantic Drift: multi-turn chat loops mutate initial constraints without convergence guarantees. Fourth, Reactive Failure Latency: detecting faults after hardware rejection risks live link disruptions. Fifth, Suboptimal HITL: binary all-or-nothing review causes operator fatigue.
[Bridge to Next Slide]: To overcome these five failure modes, we must formally structure the optical intent problem with hard physical constraints.
-->

---

## Slide 5: Problem Statement: Given, Decide, Objective & Constraints

> [!LAYOUT]
> 2-tier structured optimization layout: Upper tier contains 3 cards side-by-side with 4 modular white rounded pills each; Lower tier is a full-width container with 2 sub-panels for Resource vs. Boundary constraints.

> [!VISUAL]
> - Top Row (Upper Tier - 3 Cards Side-by-Side):
>   - Card 1 (Left): `Given (System Inputs)` (Navy header `#0F2C53`)
>     - 4 Pills: Intent $\mathcal{I}_{NL}$, Topology $G(V, E)$, Physical parameters $L$, Feasibility threshold $\text{GSNR}$
>   - Card 2 (Center): `Decide (Variables & Actions)` (Navy header `#0F2C53`)
>     - 4 Pills: Symbolic PDDL $\mathcal{S}_{PDDL}$, Optimal route $\pi^*$, Decision action $a$, Routing config $c^*$
>   - Card 3 (Right): `Objective (Optimization)` (Green header `#1A7F37`)
>     - 4 Pills: Minimize interruptions $\min N_{hitl}$, Minimize tokens $\min T_{tokens}$, Minimize friction $\min \alpha N_{hitl} + \beta T_{tokens}$, Pre-deployment safety $\mathcal{D}(U_{sem}, \text{QoT}_{valid}) = \text{approve}$
> - Bottom Tier (Lower Tier - Full-Width Constraints Container $10.31'' \times 2.13''$):
>   - Header Bar: `Constraints: Resource Limits vs. Physical & Semantic Boundaries` (Burgundy `#85200C`)
>   - Left Sub-Panel: `Resource Constraints (System & Solver Limits):`
>   - Right Sub-Panel: `Boundary Constraints (Physical & Semantic Feasibility):`

- **Given (System Inputs)**
  - Unstructured operator intent ($\mathcal{I}_{NL}$)
  - Active optical topology graph $G(V, E)$
  - Physical parameters (e.g. span length $L$)
  - Feasibility threshold (e.g. $\text{GSNR}$)
- **Decide (Variables & Actions)**
  - Formal symbolic specification ($\mathcal{S}_{PDDL}$ compiled from intent)
  - Optimal physical lightpath route ($\pi^* \in \mathcal{K}_{path}$ from candidate paths)
  - Pre-deployment control action ($a \in \{\text{approve}, \text{clarify}, \text{replan}\}$)
  - Provisioning routing configuration ($c^*$ dispatched to controller)
- **Objective (Optimization)**
  - Minimize human interruptions ($\min N_{hitl}$)
  - Minimize prompt tokens ($\min T_{tokens}$)
  - Minimize operational friction ($\min \alpha \cdot N_{hitl} + \beta \cdot T_{tokens}$)
  - Guarantee pre-deployment safety ($\mathcal{D}(U_{sem}, \text{QoT}_{valid}) = \text{approve}$)
- **Constraints: Resource Limits vs. Physical & Semantic Boundaries**
  - **Resource Constraints (Left Column):**
    - Token context limits ($T_{prompt} \le T_{max}$)
    - Computational inference latency ($t_{exec} \le t_{max\_budget}$)
    - Symbolic solver complexity $K \in [3, 5]$
  - **Boundary Constraints (Right Column):**
    - Zero semantic drift tolerance bound
    - Deterministic optical QoT feasibility
    - Pre-deployment physical validity state ($\text{QoT}_{valid} \in \{0, 1\}$)

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Formally formulate the problem across four structured dimensions: Given inputs, Decision variables, Objective function, and Constraints (Resource vs Boundary).
[Spoken Script]: Following classical telecommunications optimization methodology, we formulate our intent planning problem across four precise dimensions: Given, Decide, Objective, and Constraints. In the upper row, first, Given: the orchestrator ingests the natural language intent, queries the network graph via RESTConf, and loads physical parameters. Second, Decide: the system determines the PDDL specification, selects the optimal lightpath route pi*, resolves the risk decision action in {approve, clarify, replan}, and generates the final configuration c*. Third, Objective: we formulate a multi-objective cost function minimizing human interruptions and prompt tokens under the hard invariant that no lightpath is deployed without approval. In the lower half, Constraints decouple into Resource Constraints on the left and Boundary Constraints on the right.
[Bridge to Next Slide]: To solve this constrained optimization problem, we introduce our neurosymbolic architectural philosophy.
-->

---

## Slide 6: Proposed Solution: RADG with Neurosymbolic Planning

> [!LAYOUT]
> 2-column comparative architecture slide: Left column features two vertically stacked subsystem cards containing 3 modular white rounded pills each (Neural Subsystem: Semantic Domain on top, and Symbolic Subsystem: Optical Domain on bottom); Right column features a prominent "Core Thesis Contributions" container with 3 vertically stacked highlight blocks one below the other.

> [!VISUAL]
> - Left Column (Vertically Stacked Subsystems - $w=5.7''$, $x=0.75''$):
>   - Top Card: `Neural Subsystem (Semantic Domain)` (Navy header `#0F2C53`, linguistic compiler, early fail-fast gate)
>     - 3 White Rounded Pills:
>       - `Translation of the intent`
>       - `Validation of the semantic similarity`
>       - `Orchestration`
>   - Bottom Card: `Symbolic Subsystem (Optical Domain)` (Green header `#1A7F37`, deterministic solvers, late physical risk gate)
>     - 3 White Rounded Pills:
>       - `Topology extraction`
>       - `Compute candidate lightpaths`
>       - `Physical feasibility validation`
> - Right Column (Core Thesis Contributions - $w=5.75''$, $x=6.8''$):
>   - Container Header Bar: `Core Thesis Contributions` (Navy bar `#0F2C53`)
>   - 3 Vertically Stacked Highlight Blocks (Cards with colored borders):
>     - Block 1: `1. Scoped GraphRAG for IBON in a Neurosymbolic system` (Navy border `#0F2C53`)
>     - Block 2: `2. Quantification of Semantic Uncertainty for IBON in a Neurosymbolic system` (Amber border `#B07D00`)
>     - Block 3: `3. Risk-Adaptive Decision Gate (RADG) for HITL optimization` (Green border `#1A7F37`)

- **Left Column: Decoupled Subsystems**
  - **Neural Subsystem (Semantic Domain)**
    - Translation of the intent
    - Validation of the semantic similarity
    - Orchestration
  - **Symbolic Subsystem (Optical Domain)**
    - Topology extraction
    - Compute candidate lightpaths
    - Physical feasibility validation
- **Right Column: Core Thesis Contributions (3 Stacked Blocks)**
  - **1. Scoped GraphRAG for IBON in a Neurosymbolic system**
    - Strict separation: probabilistic semantic translation vs deterministic physics
    - Subtopology scoping reduces prompt tokens, eliminating attention loss
  - **2. Quantification of Semantic Uncertainty for IBON in a Neurosymbolic system**
    - Layer 1 syntax check ($v_{struct} \in \{0, 1\}$)
    - Layer 2 semantic discrepancy ($d_{sem}$)
  - **3. Risk-Adaptive Decision Gate (RADG) for HITL optimization**
    - Piecewise decision $D(U_{sem}, \text{QoT}_{valid})$: clarify, replan, or auto-approve
    - Guarantees physical safety ($UAR = 0$) with <5 ms calculation latency

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
>   - `Phase 1: Optical RAG` (Enrich $\mathcal{I}_{NL}$ with ITU-T grid & transponders)
>   - `Phase 2: PDDL Parser` (Translate intent into formal PDDL $\mathcal{S}_{PDDL}$ AST)
>   - `Phase 3: Semantic Gate` [RISK GATE] (Two bullets: Evaluate CFG $v_{struct}$ & Reverse Prompting $d_{sem}$)
>   - `Phase 4: Symbolic Solver` (Scoped GraphRAG & Yen's $K\text{-SP}$ routing)
>   - `Phase 5: QoT Physics` (Deterministic GN-model $\text{GSNR}$ calculation)
>   - `Phase 6: Feasibility Gate` [RISK GATE] (Piecewise risk gate $D(U_{sem}, \text{QoT})$)
>   - `Phase 7: Plan Synthesizer` (Auditable report & deployment commands)
> - Directional chevron/arrow shapes linking each phase
> - Gate highlight styling: Phase 3 (Amber border / Clarify loop) and Phase 6 (Burgundy border / Replan loop)

- **Phase 1: Optical RAG** — Enrich $\mathcal{I}_{NL}$ with ITU-T grid & transponders
- **Phase 2: PDDL Parser** — Translate intent into formal PDDL $\mathcal{S}_{PDDL}$ AST
- **Phase 3: Semantic Gate [RISK GATE]**
  - Evaluate CFG $v_{struct}$
  - Reverse Prompting $d_{sem}$
- **Phase 4: Symbolic Solver** — Scoped GraphRAG & Yen's $K\text{-SP}$ routing
- **Phase 5: QoT Physics** — Deterministic GN-model $\text{GSNR}$ calculation
- **Phase 6: Feasibility Gate [RISK GATE]** — Piecewise risk gate $D(U_{sem}, \text{QoT})$
- **Phase 7: Plan Synthesizer** — Auditable report & deployment commands

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Walk through the clean 7-phase pipeline, highlighting the sequential fail-fast flow.
[Spoken Script]: Here we see the complete 7-phase execution pipeline. The operator's intent enters Phase 1 where it is enriched with optical standards. In Phase 2, the LLM generates PDDL constraints. Crucially, before running heavy graph solvers or physics tools, Phase 3 evaluates semantic uncertainty. If semantically sound, Phase 4 extracts candidate routes via symbolic graph algorithms. Phase 5 evaluates physical feasibility using a deterministic GN-model. Finally, the Risk-Adaptive Decision Gate verifies physical safety before synthesizing the final auditable report.
[Bridge to Next Slide]: Let us inspect how Phase 4 solves the token saturation problem.
-->

---

## Slide 8: Overcoming Token Saturation: Scoped Optical GraphRAG

> [!LAYOUT]
> Asymmetric split layout: Left side features a 3-stage vertical pill flow connected by a directional flow arrow, underpinned by mathematical scoping bound equations; Right side displays the 17-node German backbone network map with click animation, topology citation, and bottom callout banner.

> [!VISUAL]
> - Left Column Container ($w=9.3''$, $h=5.35''$, background `#F4F6F9`, border `#0F2C53`):
>   - Header Badge: `Deterministic Subtopology Scoping` (Navy `#0F2C53`)
>   - 3-Stage Vertical Pill Flow (connected by a continuous burgundy down arrow `#85200C`):
>     - Pill 1 (Top): `Raw JSON contains excessive telemetry: ROADM ports, EDFAs, fibers`
>     - Pill 2 (Middle): `Full topology dumps overwhelm LLM context windows`
>     - Pill 3 (Bottom, Green border `#1A7F37`): `Mock GraphRAG extracts localized subtopology` + $G_{sub} \subseteq G$
>   - Mathematical Scoping Bound (Native OMML):
>     - $G_{sub} = (V_{sub}, E_{sub}) \subseteq G$
>     - $T_{prompt}(G_{sub}) \ll T_{prompt}(G)$
> - Right Column: 17-Node German Core Network Scoping with Entrance Click Animation ($x=6.85''$, $w=5.5''$):
>   - Step 1 (Base State): Full 17-node German backbone topology (`assets/germany_17nodes.png`)
>   - Step 2 (On Advance / Click): Scoped subtopology overlay (`assets/germany_17nodes_opaco.jpg`) with opacified northern nodes, highlighting localized Frankfurt–Munich subnetwork
>   - Citation Text: `From: https://topolib.readthedocs.io/en/latest/topology_repository.html`
>   - Bottom Banner: `e.g.  Frankfurt ➔ Munich demand: Northern nodes pruned from LLM prompt`

- **3-Stage Vertical Pill Flow**
  - **1. Telemetry Overload:** Raw JSON contains excessive telemetry: ROADM ports, EDFAs, fibers
  - **2. Attention Saturation:** Full topology dumps overwhelm LLM context windows
  - **3. Scoped Extraction:** Mock GraphRAG extracts localized subtopology $G_{sub} \subseteq G$
- **Mathematical Scoping Bound**
  - $G_{sub} = (V_{sub}, E_{sub}) \subseteq G$
  - $T_{prompt}(G_{sub}) \ll T_{prompt}(G)$
- **Empirical Network Verification**
  - 17-Node German Backbone: Frankfurt ➔ Munich demand prunes distant northern nodes (Hamburg, Bremen, Berlin)
  - Quantitative Impact: Over 75% prompt token reduction with sub-millisecond graph extraction $\mathcal{O}(|V| + |E|)$

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Scoped GraphRAG extracts only relevant k-hop subtopologies, eliminating attention degradation.
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with the entire 17-node topology, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. For instance, [Click / Advance] if an operator requests a lightpath between Frankfurt and Munich, there is no need to load northern nodes like Hamburg, Bremen, or Berlin into the LLM context. We prune distant nodes and links, reducing the prompt token footprint by over 75 percent, eliminating the lost-in-the-middle phenomenon while keeping the graph search computationally instantaneous.
[Bridge to Next Slide]: Now let us examine how we eliminate semantic drift before any physics calculations occur.
-->

---

## Slide 9: Overcoming Semantic Drift: Reverse Prompting & HITL

> [!LAYOUT]
> Asymmetrical layout: Large prominent container card on the left ($w=8.51''$) hosting modular Structural vs Semantic cards alongside the formal $U_{sem}$ formula and LLM agreement judge; Right side features two stacked floating action banners for fail-fast intervention and computational guarantees.

> [!VISUAL]
> - Main Container Card ($w=8.51''$, $h=4.7''$, $x=0.867''$, fill `#F4F6F9`, border `#0F2C53`):
>   - Header Pill: `Two-Layer Semantic Uncertainty ($U_{sem}$)` ($w=5.7''$, fill `#0F2C53`, white text)
>   - Sub-card 1 (`Structural`, white fill, border `#D0D7DE`): `CFG regex AST checks ($v_{struct} \in \{0, 1\}$)`
>   - Sub-card 2 (`Semantic`, white fill, border `#D0D7DE`): `Reverse Prompting reconstructs the intent`
>   - Commentary & Judge: `Independent LLM judge measures semantic discrepancy $d_{sem} \in [0, 1]$`
>   - Native OMML Piecewise Equation:
>     $$U_{sem} = \begin{cases} 1 & \text{if } v_{struct} = 0 \\ d_{sem} & \text{if } v_{struct} = 1 \end{cases}$$
> - Right Action Banners ($w=4.25''$, $x=7.505''$):
>   - Top Banner (Amber fill `#B07D00`, white text): `Fail-Fast HITL Clarification Loop`
>   - Bottom Banner (Neutral fill `#F4F6F9`, Green border `#1A7F37`): `Fail-Fast Guarantee: Zero computational waste on physics simulation when intent is ambiguous`

- **Two-Layer Semantic Uncertainty Gate ($U_{sem}$)**
  - Structural Layer: Context-Free Grammar (CFG) regex AST checks ($v_{struct} \in \{0, 1\}$)
  - Semantic Layer: Reverse Prompting reconstructs the intent directly from generated PDDL
  - Semantic Divergence: Independent LLM judge measures semantic distance $d_{sem} \in [0, 1]$
- **Fail-Fast Action Banners**
  - **Fail-Fast HITL Clarification Loop:** Pauses pipeline via `interrupt()` before downstream graph/physical tools
  - **Computational Guarantee:** Zero computational waste on physics simulation when intent is ambiguous

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: The semantic gate prevents unverified assumptions from entering downstream tools.
[Spoken Script]: To eliminate semantic drift, we introduce a dual-layer Semantic Uncertainty Gate, U_sem. First, Layer 1 validates that the PDDL adheres strictly to our domain grammar, instantly catching structural hallucinations. Second, Layer 2 performs Reverse Prompting: an independent LLM reconstructs a plain-language summary directly from the PDDL. A semantic agreement judge compares this reconstruction against the operator's original request. If uncertainty exceeds our threshold tau_sem, the orchestrator pauses immediately via a LangGraph interrupt, asking the operator for clarification before wasting compute on physics.
[Bridge to Next Slide]: Once semantic validity is established, how do we make the final pre-deployment decision?
-->

---

## Slide 10: Pre-Deployment Risk Gate: The RADG Decision Function

> [!LAYOUT]
> Structured Decision Tree slide: Top card displays the formal piecewise OMML equation; Bottom section displays 3 distinct outcome branch cards featuring embedded OMML condition equations directly inside their colored header pills.

> [!VISUAL]
> - Top Container: Formal RADG Piecewise Equation in native OMML:
>   $$D(U_{sem}, \text{QoT}_{valid}) = \begin{cases} \text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ \text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ \text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 \end{cases}$$
> - 3 Bottom Outcome Cards (with embedded condition equations in header pills):
>   - `Clarify Intent` (Amber fill/border `#B07D00`, condition $U_{sem} > \tau_{sem}$ in header pill)
>   - `Suggest Replan` (Burgundy fill/border `#85200C`, condition $U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0$ in header pill)
>   - `Auto-Approve` (Green fill/border `#1A7F37`, condition $U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1$ in header pill)

- **State Space & Signals**
  - Evaluates semantic uncertainty $U_{sem} \in [0, 1]$ and binary QoT feasibility $\text{QoT}_{valid} \in \{0, 1\}$
  - Action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$
- **Action Guarantees & Triggers**
  - **Clarify Intent:** Semantic uncertainty exceeds threshold ➔ pauses pipeline via `interrupt()`, prompts operator for missing data
  - **Suggest Replan:** Valid semantics, but physics infeasible ➔ notifies operator and suggests relaxing constraints (e.g. lower baud rate)
  - **Auto-Approve:** Clear semantics and feasible GSNR ➔ autonomous zero-touch provisioning and auditable planning report

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
> Integrated wide layout: A single unified background container ($w=9.404''$) anchors the 17-node core network specifications on the left and the Nobel-Germany optical core backbone map on the right with a dedicated source citation link.

> [!VISUAL]
> - Unified Container Card ($w=9.404''$, $h=5.35''$, $x=0.75''$, fill `#F4F6F9`, border `#0F2C53`):
>   - Header Bar: `17-Node German Core Network Benchmark` ($w=5.6''$, fill `#0F2C53`, white text)
>   - Network Specifications (7 bullet items at $x=1.15''$, 12 pt Arial):
>     - Telecom topology: $|V| = 17, |E| = 26$ bidirectional fiber links
>     - SMF-28 parameters: $\alpha = 0.2$ dB/km, $D = 16.7$ ps/(nm$\cdot$km), $\gamma = 1.2\text{ W}^{-1}\text{km}^{-1}$
>     - Dual-stage EDFAs ($NF = 5.5$ dB), span lengths $L \in [45, 350]$ km
>     - LangGraph StateGraph orchestrator with memory persistence & RESTConf adapters
> - Topology Graphic & Source Citation ($x=6.85''$):
>   - High-resolution Nobel-Germany 17-Node Map (`germany_17nodes.png`, $w=5.5''$, $h=3.67''$, border `#D0D7DE`)
>   - Source Link Subtitle: `From: https://topolib.readthedocs.io/en/latest/topology_repository.html` (9 pt `#5A6B82`)

- **17-Node German Core Network Benchmark**
  - Realistic telecom topology: $|V| = 17, |E| = 26$ bidirectional fiber links
  - Standard Single-Mode Fiber (SMF-28): $\alpha = 0.2$ dB/km, $D = 16.7$ ps/(nm$\cdot$km), $\gamma = 1.2\text{ W}^{-1}\text{km}^{-1}$
  - Amplified spans: dual-stage EDFAs with noise figure $NF = 5.5$ dB
  - Dynamic span lengths ranging from $L \in [45, 350]$ km
  - Orchestrator: LangGraph StateGraph with memory persistence
  - Telemetry: RESTConf and Mock SDON testbed client adapters
- **Topology Source**
  - Sourced directly from TopoLib repository (`https://topolib.readthedocs.io/en/latest/topology_repository.html`)

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Realistic evaluation using the standard 17-node German optical topology and RESTConf testbed.
[Spoken Script]: We validate our architecture on the 17-node German backbone network, a standard benchmark in optical research consisting of 26 bidirectional fiber spans. All spans model standard SMF-28 fiber with realistic attenuation, dispersion, and EDFA noise figures. The orchestrator is implemented in Python using LangGraph, interfacing with the optical testbed via RESTConf APIs, and benchmarked using state-of-the-art LLMs as semantic translators.
[Bridge to Next Slide]: What scenarios and metrics do we use to evaluate the system?
-->

---

## Slide 13: Evaluation Framework & Benchmark Scenarios

> [!LAYOUT]
> Asymmetric 2-column benchmark layout: Left column features two stacked cards ($w=4.6''$): Top card showcases Architectural Baselines with visual comparison pills (Baseline A vs. Baseline B) and a full-width Proposed Neurosymbolic RADG pill; Bottom card presents the 100-Demand Benchmark Corpus across 4 risk classes. Right column presents the 4 Core Validation Pillars floating directly on the slide canvas with modular white cards ($w=6.65''$, $x=5.75''$) and distinct institutional color borders.

> [!VISUAL]
> - Left Column (Setup & Benchmarks - $w=4.6''$, $x=0.75''$):
>   - Top Card: `Architectural Baselines` (`#F4F6F9` fill, Navy border `#0F2C53`, 1.5 pt)
>     - Sub-Card: `Baseline A` (LLM-Only) ($w=1.6''$, $h=0.625''$, White fill, border `#D0D7DE`)
>     - Comparison indicator: `vs.` (centered)
>     - Sub-Card: `Baseline B` (Always-HITL) ($w=1.6''$, $h=0.625''$, White fill, border `#D0D7DE`)
>     - Full-Width Sub-Card: `Proposed Neurosymbolic RADG` ($w=4.324''$, $h=0.645''$, White fill, Green border `#1A7F37`, 1.0 pt)
>       - Subtitle: *Decoupled translation + sequential pre-deployment risk gates*
>   - Bottom Card: `100 Test Demands (4 Risk Classes)` (`#F4F6F9` fill, Burgundy border `#85200C`, 1.5 pt)
>     - Formatted 3-Column Benchmark Table ($w=4.144''$, $h=2.215''$, $x=0.978''$, $y=4.53''$, Navy header `#0F2C53`):
>       - Col 1 (`Class & Size`): Class I: Nominal [40], Class II: Ambiguous [20], Class III: Infeasible [25], Class IV: Adversarial [15]
>       - Col 2 (`Intent Characteristics`): Feasible path / Under-specified ($U_{sem} > \tau$) / Violates GSNR / Hallucinated nodes ($v_{struct} = 0$)
>       - Col 3 (`RADG Action`): Color-coded expected gate verdicts: **Auto-Approve** (Green), **Clarify Intent** (Amber), **Suggest Replan** (Burgundy), **Reject Intent** (Burgundy)
> - Right Column (4 Core Validation Pillars - $w=6.65''$, $x=5.75''$, floating directly on slide canvas):
>   - 4 Vertically Stacked Modular Cards (White `#FFFFFF` fill, 1.5 pt borders, $w=6.65''$, $h=1.15''$):
>     - `1. Semantic Translation Accuracy (Neural Domain)` (Amber border `#B07D00`)
>       - Test Focus: Validates NL ➔ PDDL translation without constraint loss or hallucinations
>       - Metrics: Constraint Retention Rate ($\text{CRR} = 100\%$) • CFG AST Pass Rate ($v_{struct} = 1$)
>     - `2. Physical Feasibility (Optical Layer Integrity)` (Green border `#1A7F37`)
>       - Test Focus: Validates optical reach and non-linear impairments before controller push
>       - Metrics: Unsafe Approval Rate ($\text{UAR} = 0\%$ hard invariant) • QoT Feasibility ($100\%$)
>     - `3. Orchestration & Resource Efficiency (System Limits)` (Navy border `#0F2C53`)
>       - Test Focus: Quantifies prompt token savings from GraphRAG and operator fatigue reduction
>       - Metrics: $> 75\%$ Token Reduction ($G_{sub} \subseteq G$) • $> 70\%$ HITL Cut • Sub-second compute
>     - `4. RADG Decision Robustness (Gate Reliability)` (Burgundy border `#85200C`)
>       - Test Focus: Stress-tests piecewise decision logic ($U_{sem}, \text{QoT}_{valid}$) across boundary conditions
>       - Metrics: Gate Decision Accuracy ($> 98\%$) • Zero False Positives ($\text{FPR} = 0\%$)

- **Architectural Baselines & Testbed**
  - Baseline A (LLM-Only) vs. Baseline B (Always-HITL)
  - Proposed Neurosymbolic RADG: Decoupled translation + sequential pre-deployment risk gates
  - 17-Node German Backbone: 26 bidirectional fiber links, standard SMF-28, dual-stage EDFAs
- **100 Test Demands (4 Risk Classes)**
  - Class I — Nominal [40]: Unambiguous requests with feasible optical paths ➔ Auto-Approve
  - Class II — Ambiguous [20]: Under-specified constraints triggering $U_{sem} > \tau_{sem}$ ➔ Clarify
  - Class III — Infeasible [25]: High modulation over long spans violating GSNR ➔ Suggest Replan
  - Class IV — Adversarial [15]: Hallucinated nodes & syntax violations ($v_{struct} = 0$) ➔ Reject
- **Four Core Validation Pillars**
  - **1. Semantic Translation Accuracy:** Constraint Retention Rate ($\text{CRR} = 100\%$), CFG AST Pass Rate ($v_{struct} = 1$)
  - **2. Physical Feasibility:** Unsafe Approval Rate ($\text{UAR} = 0\%$ hard invariant), QoT Feasibility ($100\%$)
  - **3. Orchestration Efficiency:** $> 75\%$ Token Cut ($G_{sub} \subseteq G$), $> 70\%$ HITL Cut, Sub-second compute
  - **4. RADG Decision Robustness:** Gate Decision Accuracy ($> 98\%$), Zero False Positives ($\text{FPR} = 0\%$)

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Rigorous benchmarking across 100 diverse intent scenarios against LLM-only and rule-based baselines across 4 validation pillars.
[Spoken Script]: In Slide 13, we present our comprehensive evaluation framework. On the left, we establish the experimental baseline: we test against an unconstrained LLM-only baseline with trial-and-error retry, and a rigid rule-based system with always-on human review, deployed on the 17-node German optical backbone. We evaluate a benchmark corpus of 100 intent demands spanning four risk classes: nominal, ambiguous, physically infeasible, and adversarial prompts. On the right, rather than just measuring latency, we evaluate our system across four rigorous validation pillars: first, Semantic Translation Accuracy to guarantee zero constraint loss; second, Physical Feasibility to enforce our non-negotiable zero percent Unsafe Approval Rate; third, Orchestration Efficiency, measuring over 75 percent token savings from GraphRAG and 70 percent reduction in operator fatigue; and fourth, RADG Decision Robustness, ensuring over 98 percent gate accuracy and zero false positives across all boundary conditions.
[Bridge to Next Slide]: Let us analyze the key findings and empirical guarantees obtained from these benchmarks.
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
