# Master's Thesis Defense: Slide Deck Specification

- **Thesis Title:** Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
- **Subtitle:** A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment
- **Candidate:** Felipe Abadía
- **Academic Advisor:** Prof. Massimo Tornatore
- **Institution:** Politecnico di Milano — Dipartimento di Elettronica, Informazione e Bioingegneria
- **Target Presentation Time:** 15 minutes (16 slides $\approx$ 55s per slide)
- **Formatting Rule:** Strict compliance with the 15 Golden Rules (no terminal periods on bullet points, thesis-specific ToC, explicit contributions, high visual contrast)

---

## Slide 1: Title Slide

> [!LAYOUT]
> Template Layout 0 (Title Slide). Official Politecnico di Milano header and logo. Burgundy accent for title, Navy blue for subtitle and metadata.

- **Title:** Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
- **Subtitle:** A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment
- **Candidate:** Felipe Abadía
- **Advisor:** Prof. Massimo Tornatore
- **Institution:** Politecnico di Milano — Dipartimento di Elettronica, Informazione e Bioingegneria

<!-- Speaker Notes:
[Estimated Time]: 30s
[Key Message]: Welcome the committee and introduce the thesis title and research focus.
[Spoken Script]: Good morning members of the committee and Professor Tornatore. Today I present my Master's thesis entitled "Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment". In this work, we address the challenge of bridging high-level operator intent with physical optical layer realities using a robust, fail-fast neurosymbolic architecture.
[Bridge to Next Slide]: Let us begin with the specific roadmap of problems and solutions covered in this presentation.
-->

---

## Slide 2: Outline

> [!LAYOUT]
> Template Layout 1 (Title and Content). 5 distinct thematic cards representing the thesis problem progression.

- **The Optical Intent Bottleneck** — Physical constraints and LLM failure modes
- **Neurosymbolic Planning Architecture** — Decoupling reasoning from deterministic physics
- **Pre-Deployment Risk Gates** — Sequential semantic ($U_{sem}$) and physical (QoT) validation
- **Experimental Testbed Validation** — 17-node German backbone network evaluation
- **Key Takeaways & Future Outlook** — Architectural guarantees and roadmap

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Establish a thesis-specific narrative instead of a generic agenda.
[Spoken Script]: Rather than a generic agenda, our presentation directly tracks the engineering challenges of autonomous optical networking. We begin by examining why general-purpose LLMs fail when controlling optical backbones. Next, we present our neurosymbolic architecture that cleanly separates natural language reasoning from optical physics. We then delve into the pre-deployment risk gates that protect the physical network before showing experimental validation on a 17-node optical topology and concluding with our primary takeaways.
[Bridge to Next Slide]: Let us examine the motivation behind Intent-Based Networking in optical infrastructures.
-->

---

## Slide 3: Motivation: The Vision of Intent-Based Optical Networks

> [!LAYOUT]
> Template Layout 3 (Two Content). Left column: Operational shifts in optical networks. Right column: The operational vision (Natural Language Intent to Physical Lightpaths).

- **Operational Paradigm Shift**
  - Next-generation optical backbones demand rapid, dynamic provisioning
  - Traditional workflow: manual CLI configuration and vendor-specific RESTConf scripts
  - Vision: Autonomous Intent-Based Networking (IBN) via natural language
- **The Operational Promise**
  - Empower network operators to state *what* they need, not *how* to configure it
  - Example: "Establish a 400G lightpath between Milan and Rome with high reliability"
  - Accelerate service turn-up from hours to seconds while reducing human error

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: The promise of autonomous IBN is compelling, but optical networks impose strict physical constraints.
[Spoken Script]: Optical networks form the backbone of modern telecommunications, carrying terabits of traffic across core routes. Traditionally, provisioning lightpaths requires expert network operators to manually write vendor-specific RESTConf payloads or CLI scripts. Intent-Based Networking promises to revolutionize this by allowing operators to express high-level operational goals in natural language. While this vision is promising, direct deployment of Large Language Models to optical control planes exposes critical vulnerabilities.
[Bridge to Next Slide]: Let us look at a concrete illustrative failure example to see why.
-->

---

## Slide 4: Illustrative Failure: Why Standard LLMs Break Optical Backbones

> [!LAYOUT]
> Template Layout 3 (Two Content / Two Cards). Side-by-side comparison of the two primary LLM failure modes: Token Saturation vs Hallucinated Physics.

- **Challenge 1: Token Budget Saturation**
  - Injecting full optical topologies into LLM context windows causes attention degradation
  - In a 100-node core network, raw RESTConf JSON exceeds context limits
  - Leads to "lost-in-the-middle" effects and dropped operational constraints
- **Challenge 2: Hallucinated Physics**
  - LLMs are probabilistic text predictors, not optical physics calculators
  - Cannot evaluate nonlinear Generalized Signal-to-Noise Ratio (GSNR) or power margins
  - Result: The LLM generates lightpaths that violate the physical layer, crashing the controller

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Standard LLMs cannot calculate optical physics and choke on massive topology payloads.
[Spoken Script]: Consider what happens if an operator asks a standard LLM to provision a 400G demand. First, we face Token Budget Saturation: dumping full topology states with hundreds of ROADMs and EDFA amplifier parameters degrades the LLM's attention, causing it to drop explicit constraints like link exclusions. Second, and more dangerously, LLMs suffer from Hallucinated Physics. Because they predict text probabilities rather than calculating nonlinear optical impairments, they will confidently propose routes that drop light below the required GSNR threshold, leading to service disruption.
[Bridge to Next Slide]: This fundamental gap defines our formal problem statement.
-->

---

## Slide 5: Problem Statement: Inputs, Constraints & Objectives

> [!LAYOUT]
> Template Layout 5 (Title Only) with 3 structured container boxes (Inputs, Constraints, Objectives).

- **Given Inputs**
  - High-level, unstructured Natural Language intent ($I_{NL}$) from the network operator
  - Physical optical network topology graph $G(V, E)$ via testbed RESTConf telemetry
  - Optical link physical parameters: span lengths, EDFA noise figures, fiber attenuation
- **Physical & Semantic Constraints**
  - Semantic alignment: formal interpretation must match operator intent ($U_{sem} \le \tau_{sem}$)
  - Optical feasibility: path GSNR must exceed modulation threshold ($\text{GSNR} \ge \text{GSNR}_{req}$)
  - Power budget: optical receiver power must meet sensitivity ($P_{rx} \ge P_{rx,min}$)
- **Core Objectives**
  - Zero unfeasible or hallucinated configurations reaching the optical controller
  - Fail-fast pre-deployment validation to minimize computational waste
  - Selective, risk-proportional Human-in-the-Loop engagement

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: Formally state the problem across three distinct pillars: inputs, constraints, and objectives.
[Spoken Script]: To tackle this challenge rigorously, we formalize the problem into three concrete pillars. Our system receives an unstructured operator intent, the physical topology graph G(V, E), and optical layer parameters. It must satisfy two orthogonal constraint classes: semantic consistency to prevent intent drift, and deterministic optical physics, specifically GSNR and receiver power thresholds. Our core objective is simple yet strict: ensure zero physically unfeasible configurations ever reach the network controller, while engaging the operator only when genuine ambiguity exists.
[Bridge to Next Slide]: To achieve this, we introduce our core neurosymbolic architectural philosophy.
-->

---

## Slide 6: Proposed Solution: Neurosymbolic Decoupling

> [!LAYOUT]
> Template Layout 3 (Two Content). Left: Core architectural philosophy. Right: Structural division of responsibilities.

- **Architectural Philosophy: Strict Separation of Concerns**
  - **LLMs Reason, Deterministic Tools Calculate**
  - Prohibit LLMs from computing physics or performing heuristic graph routing
  - Constrain the LLM strictly to formal linguistic translation into PDDL
- **The Four Core Contributions**
  - **1. Neurosymbolic Pipeline:** LLM translates NL intent to Planning Domain Definition Language
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
> Template Layout 5 (Title Only). High-level horizontal pipeline flowchart showing Phases 1 through 7 with sequential gate checkpoints.

- **Phase 1: Intent Ingest & Optical RAG** — Context enrichment via ITU-T optical standards
- **Phase 2: PDDL Parsing** — Few-shot semantic translation into formal PDDL constraints
- **Phase 3: Semantic Gate** — Layer 1 CFG regex validation & Layer 2 Reverse Prompting
- **Phase 4: Symbolic Solver** — Scoped GraphRAG $k$-hop extraction + Yen's KSP path generation
- **Phase 5: QoT Validation** — Deterministic GN-model calculation of GSNR and $P_{rx}$
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
> Template Layout 3 (Two Content). Left: Subtopology extraction concept. Right: Quantitative token and latency impact.

- **The Problem: Full Topology Bloat**
  - Transmitting the entire 17-node or 100-node network state saturates the LLM context
  - Causes attention dilution and inflated token costs
- **The Solution: Deterministic $k$-hop Neighborhood Scoping**
  - Mock GraphRAG extracts only relevant optical subtopologies between source and target
  - Filters out unneeded ROADMs, transponders, and fiber spans
- **Impact & Benefits**
  - Over 75% reduction in prompt token payload
  - Deterministic $O(V + E)$ graph extraction in Python via NetworkX
  - Guarantees high attention focus on active constraints

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Scoped GraphRAG extracts only relevant k-hop subtopologies, eliminating attention degradation.
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with hundreds of network nodes and links, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. This reduces the prompt token footprint by over 75 percent, completely eliminating lost-in-the-middle phenomena while keeping the graph search computationally light.
[Bridge to Next Slide]: Now let us examine how we eliminate semantic drift before any physics calculations occur.
-->

---

## Slide 9: Overcoming Semantic Drift: Reverse Prompting & HITL Loop

> [!LAYOUT]
> Template Layout 3 (Two Content). Left: Dual-layer semantic uncertainty calculation. Right: The closed-loop HITL clarification mechanism.

- **Two-Layer Semantic Uncertainty Gate ($U_{sem}$)**
  - **Layer 1 (Structural):** Context-Free Grammar (CFG) regex validation catches syntax hallucinations
  - **Layer 2 (Semantic):** Reverse Prompting reconstructs natural language from generated PDDL
- **Formal Semantic Divergence**
  - LLM judge measures semantic discrepancy $d_{sem} \in [0, 1]$ between original intent and reconstruction
  - Uncertainty metric: $U_{sem} = 1$ if structural failure, else $U_{sem} = d_{sem}$
- **Fail-Fast Clarification Trigger**
  - If $U_{sem} > \tau_{sem}$, the pipeline pauses via LangGraph `interrupt()`
  - Directly prompts the operator to clarify ambiguous intent before executing solvers

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: The semantic gate prevents unverified assumptions from entering downstream tools.
[Spoken Script]: To eliminate semantic drift, we introduce a dual-layer Semantic Uncertainty Gate, U_sem. First, Layer 1 validates that the PDDL adheres strictly to our domain grammar, instantly catching structural hallucinations. Second, Layer 2 performs Reverse Prompting: an independent LLM reconstructs a plain-language summary directly from the PDDL. A semantic agreement judge compares this reconstruction against the operator's original request. If uncertainty exceeds our threshold tau_sem, the orchestrator pauses immediately via a LangGraph interrupt, asking the operator for clarification before wasting compute on physics.
[Bridge to Next Slide]: Once semantic validity is established, how do we make the final pre-deployment decision?
-->

---

## Slide 10: Pre-Deployment Risk Gate: The RADG Decision Function

> [!LAYOUT]
> Template Layout 5 (Title Only). Formal mathematical decision function and state mapping diagram.

- **Formal Decision Space: $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$**
  - Evaluates semantic uncertainty $U_{sem}$ and deterministic physical feasibility $\text{QoT}_{valid}$
- **Piecewise Decision Formulation**
  $$D(U_{sem}, \text{QoT}_{valid}) = \begin{cases} \text{clarify} & \text{if } U_{sem} > \tau_{sem} \\ \text{replan} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0 \\ \text{approve} & \text{if } U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1 \end{cases}$$
- **Key Architectural Guarantees**
  - **Auto-Approve:** Feasible paths with clear semantics deploy autonomously without operator fatigue
  - **Suggest Replan:** Unfeasible physics prompt constraint relaxation (e.g., lower baud rate or bypass link)
  - **Zero Unverified States:** No configuration reaches the controller without mathematical validation

<!-- Speaker Notes:
[Estimated Time]: 60s
[Key Message]: The RADG function mathematically maps semantic and physical signals to optimal actions.
[Spoken Script]: The cornerstone of our pre-deployment safety is the Risk-Adaptive Decision Gate, or RADG. We formalize this as a piecewise decision function, D. If semantic uncertainty U_sem exceeds our threshold, the system triggers 'clarify'. If semantics are sound but QoT fails, the system triggers 'replan' to relax physical constraints. Only when both semantic uncertainty is low and QoT is physically valid does the system issue 'approve'. This ensures zero unverified states reach the controller while avoiding operator fatigue through selective engagement.
[Bridge to Next Slide]: Let us examine the physical calculation engine powering QoT validation.
-->

---

## Slide 11: Deterministic Physical Layer: GN-Model QoT Validation

> [!LAYOUT]
> Template Layout 3 (Two Content). Left: Physical impairment formulas. Right: Validation criteria and execution speed.

- **Deterministic Physics via Gaussian Noise (GN) Model**
  - Pure Python physics engine: zero LLM involvement in physical calculations
  - Computes Accumulated Amplified Spontaneous Emission (ASE) noise:
    $$P_{\text{ASE}} = (G - 1) \, h \, \nu \, F \, B_{\text{ref}}$$
  - Computes Nonlinear Interference (NLI) noise power per span:
    $$P_{\text{NLI}} \approx \eta \, P_{\text{ch}}^3$$
- **Rigorous Optical Feasibility Check**
  $$\text{GSNR} = \frac{P_{\text{ch}}}{P_{\text{ASE}} + P_{\text{NLI}}} \ge \text{GSNR}_{\text{threshold}}$$
  $$P_{rx} = P_{\text{launch}} - A_{\text{total}} + G_{\text{total}} \ge P_{rx, \text{min}}$$
- **Execution Performance:** Sub-millisecond validation per candidate lightpath

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Pure Python GN-model computes real GSNR and receiver power deterministically in milliseconds.
[Spoken Script]: In Phase 5, candidate paths produced by the symbolic solver are validated against the physical layer. We port the analytical Gaussian Noise model into pure Python. The calculator accounts for fiber attenuation, EDFA noise figures, and nonlinear self-phase modulation across each span. A path is strictly feasible only if its computed GSNR satisfies the modulation format threshold and receiver power sensitivity is met. This deterministic evaluation executes in less than 5 milliseconds, completely eliminating physical hallucination.
[Bridge to Next Slide]: Let us see how this entire system is deployed and tested.
-->

---

## Slide 12: Experimental Setup & Testbed Environment

> [!LAYOUT]
> Template Layout 3 (Two Content). Left: German 17-Node backbone topology card. Right: Software stack and testbed specifications.

- **Network Topology: 17-Node German Core**
  - 17 ROADM optical nodes, 26 bidirectional fiber links
  - Standard Single Mode Fiber (SMF-28): $\alpha = 0.2$ dB/km, $D = 16.7$ ps/(nm$\cdot$km)
  - Spans equipped with dual-stage EDFAs and realistic noise figures ($F = 5.5$ dB)
- **Software Orchestration Stack**
  - **Pipeline Orchestrator:** LangGraph StateGraph with checkpointed interrupt states
  - **Physics & Graph Engine:** Pure Python GN-model and NetworkX KSP solver
  - **Telemetry Interface:** Mock & RESTConf Testbed Client matching SDON lab standards
  - **Inference Models:** GPT-4o / Claude 3.5 Sonnet evaluated across uniform intent suites

<!-- Speaker Notes:
[Estimated Time]: 50s
[Key Message]: Realistic evaluation using the standard 17-node German optical topology and RESTConf testbed.
[Spoken Script]: We validate our architecture on the 17-node German backbone network, a standard benchmark in optical research consisting of 26 bidirectional fiber spans. All spans model standard SMF-28 fiber with realistic attenuation, dispersion, and EDFA noise figures. The orchestrator is implemented in Python using LangGraph, interfacing with the optical testbed via RESTConf APIs, and benchmarked using state-of-the-art LLMs as semantic translators.
[Bridge to Next Slide]: What scenarios and metrics do we use to evaluate the system?
-->

---

## Slide 13: Evaluation Framework & Benchmark Scenarios

> [!LAYOUT]
> Template Layout 1 (Title and Content) with comparison table: Baselines vs Test Scenarios vs Metrics.

- **Baseline Comparative Architectures**
  - **Baseline A (LLM-Only):** Direct prompt-to-configuration generation with heuristic validation
  - **Baseline B (Static Rule-Based):** Strict regex parser with always-on human review
  - **Proposed (Neurosymbolic RADG):** Decoupled translation + sequential risk gates
- **Evaluation Scenarios (100 Test Demands)**
  - *Nominal Intents:* Unambiguous valid routing requests with feasible physics
  - *Ambiguous Intents:* Under-specified constraints triggering semantic divergence ($U_{sem}$)
  - *Physically Infeasible Intents:* Demands demanding high modulation over long unamplified reaches
  - *Adversarial Prompts:* Inputs designed to induce syntax or optical hallucinations
- **Target Metrics:** Pre-deployment blocking accuracy, HITL intervention rate, end-to-end planning latency

<!-- Speaker Notes:
[Estimated Time]: 55s
[Key Message]: Rigorous benchmarking across 100 diverse intent scenarios against LLM-only and rule-based baselines.
[Spoken Script]: Our evaluation framework tests 100 diverse intent requests across four operational categories: nominal intents, ambiguous intents with missing constraints, physically unfeasible demands, and adversarial prompts designed to induce hallucinations. We compare our neurosymbolic architecture against two baselines: an unconstrained LLM-only pipeline, and a rigid rule-based system. We measure three core dimensions: safety against unfeasible deployments, reduction in operator fatigue, and end-to-end execution latency.
[Bridge to Next Slide]: Let us analyze the key findings and trade-offs.
-->

---

## Slide 14: Key Findings & Pre-Deployment Guarantees

> [!LAYOUT]
> Template Layout 3 (Two Content / Two Cards). Left: Safety and reliability guarantees. Right: Operational efficiency gains.

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
> Template Layout 1 (Title and Content). 4 high-impact synthesis cards summarizing the thesis contributions.

- **Decoupling is Essential**
  - Probabilistic LLMs must never calculate physical impairments or route lightpaths
  - Natural language reasoning cleanly bridges to formal PDDL planning
- **Sequential Risk Gates Prevent Infeasible Deployments**
  - Early semantic evaluation ($U_{sem}$) eliminates drift before physics computation
  - Deterministic GN-model verification ($QoT_{valid}$) ensures 100% physical feasibility
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
> Template Layout 0 (Title / Closing Slide). Closing remarks, future research directions, and Q&A invitation.

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
