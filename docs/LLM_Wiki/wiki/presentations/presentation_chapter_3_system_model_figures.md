---
title: "Presentation: Chapter 3 System Model and Architecture"
date: 2026-09-06
tags: [presentation, slides, chapter-3, system-model, figures, drawio, architecture]
status: active
---

# Chapter 3: System Model and Neurosymbolic Architecture
## Advisor Progress Review & Visual Architecture Walkthrough

---

## Slide 1: Title Slide

> [!LAYOUT]
> Title and subtitle centered. Student name, master thesis affiliation, and date at the bottom.

# Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks
## Chapter 3 System Model & Complete Visual Architecture Suite

- **Student:** Felipe Abadia
- **Focus:** System Model, Two-Gate Fail-Fast Verification, and 7 Publication-Ready Architectural Figures
- **Date:** September 2026

<!-- Speaker Notes: Good morning, Professor. Today I am presenting the completed System Model for Chapter 3 of my master's thesis. We have fully formalized the mathematical framework, decoupled the two-gate validation logic, and completed all seven publication-ready vector figures. -->

---

## Slide 2: Architectural Problem in LLM-Driven Optical Networking

> [!LAYOUT]
> Two-column layout. Left: 5 Failure Modes of Pure Generative LLMs. Right: Core Architectural Invariant.

### The Challenge of Pure LLM Intent Planning

- **Token Saturation:** Injecting complete network state (NETCONF/RESTCONF YANG payloads) triggers "lost-in-the-middle" attention loss.
- **Physical Hallucination:** LLMs lack internal physics engines and invent non-existent fiber links or unfeasible GSNR paths.
- **Semantic Drift:** Unconstrained multi-turn chat drops operational constraints over time.
- **Reactive Failure Latency:** Trial-and-error deployment causes service-disrupting controller errors.
- **Cognitive Fatigue:** Unbounded, always-on HITL review bottlenecks network operations.

> [!NOTE]
> **Foundational Pre-Deployment Invariant:** No configuration directive is dispatched to the optical controller until it satisfies both Semantic Certainty ($U_{sem} \le \tau_{sem}$) and Physical Feasibility ($\text{QoT}_{valid} = 1$).

<!-- Speaker Notes: In telecommunications, pure LLM agents fail because they predict text rather than solving physical wave equations. Forcing an LLM to calculate lightpaths leads to catastrophic optical hallucinations. Our system resolves this through a strict pre-deployment fail-fast paradigm. -->

---

## Slide 3: Problem Formulation Pipeline (Figure 3.1)

> [!LAYOUT]
> Left column: Theoretical optimization problem. Right: Vector figure embed.

### Formal Problem Formulation

$$\min_{\mathcal{S}_{PDDL}, \pi^*} \mathcal{J} = \alpha \cdot N_{hitl}(\mathcal{I}_{NL}) + \beta \cdot T_{tokens}(\mathcal{I}_{NL})$$

$$\text{subject to:} \quad D\left( U_{sem}, \text{QoT}_{valid}(\pi^*) \right) = \text{approve}$$

- **Inputs:** Unstructured intent $\mathcal{I}_{NL}$, optical network graph $G(V, E)$, physical parameters $\mathbf{P}$, feasibility target $\text{GSNR}_{th}$.
- **Output Action:** $a \in \{\text{approve}, \text{clarify}, \text{replan}\}$.
- **Objective:** Minimizes operational human friction and computational inference costs under non-negotiable physical safety.

![Figure: Problem Formulation Block Diagram](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/problem_formulation.png)

<!-- Speaker Notes: Figure 3.1 illustrates the high-level formulation. The system ingests natural language intent and optical graph state, compiling them into formal PDDL constraints before executing deterministic K-shortest paths and GN-model physics. -->

---

## Slide 4: The 7-Phase Fail-Fast Pipeline (Figure 3.2)

> [!LAYOUT]
> Top: Architectural principles. Center: Full pipeline flow diagram. Bottom: Gate 1 and Gate 2 summary.

### The 7-Phase Orchestration Pipeline & Two-Gate Model

- **Phase 1:** Intent Ingestion & Optical RAG ($k$-hop subtopology bounding).
- **Phase 2:** CFG-Validated PDDL Parsing (LLM as semantic compiler).
- **Phase 3:** Reverse Prompting & **Gate 1: Semantic Gate ($U_{sem} \le 0.30$)**.
- **Phase 4:** Deterministic Symbolic Solver (Yen's KSP over pruned $\widetilde{G}_{sub}$).
- **Phase 5:** Quality of Transmission (GN-model physics engine).
- **Phase 6:** **Gate 2: Physical Risk Gate ($\text{QoT}_{valid} = 1$)**.
- **Phase 7:** Auditable Plan Synthesis & Provisioning.

![Figure: Conceptual Framework](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/conceptual_framework.png)

<!-- Speaker Notes: Figure 3.2 is the core architecture. Notice the two distinct gates: Gate 1 catches semantic misunderstandings early with zero physical simulation cost. Only semantically certified plans reach Gate 2, where deterministic GN-model calculations evaluate ASE and Kerr non-linear interference. -->

---

## Slide 5: Strict Neurosymbolic Separation (Figures 3.3 & 3.4)

> [!LAYOUT]
> Two-column comparison. Left: Subsystem division of responsibilities. Right: Baseline vs. proposed framework.

### "LLMs Reason, Tools Calculate"

- **Neural Subsystem:** Natural language interpretation, optical context scoping, PDDL compilation, semantic agreement scoring.
- **Formal Contract:** Typed PDDL predicates (`route`, `avoid-node`, `avoid-link`, `min-gsnr`) audited by a Context-Free Grammar ($v_{struct} \in \{0, 1\}$).
- **Symbolic Subsystem:** Topological graph pruning, Yen's KSP loopless routing, coherent GN model, RADG decision logic.

![Figure: Subsystems](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/neural_symbolic_subsystems.png)
![Figure: Comparison](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/neurosymbolic_comparison.png)

<!-- Speaker Notes: We decoupled Section 3.3 into two figures. The first shows the subsystem division across the PDDL boundary. The second compares our pipeline against an unconstrained LLM baseline, demonstrating how we eliminate physical hallucinations and post-deployment rollback costs. -->

---

## Slide 6: Risk-Adaptive Decision Gate State Space (Figure 3.5)

> [!LAYOUT]
> Left: Mathematical piecewise decision function. Right: 2D operational space plot.

### 2D RADG Operational State Space

$$D\left(U_{sem}, \text{QoT}_{valid}\right) = \begin{cases} 
\text{clarify} & \text{if } U_{sem} > 0.30 \\ 
\text{replan} & \text{if } U_{sem} \le 0.30 \land \text{QoT}_{valid} = 0 \\ 
\text{approve} & \text{if } U_{sem} \le 0.30 \land \text{QoT}_{valid} = 1 
\end{cases}$$

- **Zone I (Auto-Approve):** $U_{sem} \le 0.30 \land \Delta\text{GSNR} \ge 0\text{ dB} \implies$ zero human friction.
- **Zone II (Suggest Replan):** Transmission infeasible $\implies$ targeted constraint relaxation.
- **Zone III (Early Clarify):** High ambiguity or syntax violation $\implies$ physics engine strictly bypassed.

![Figure: RADG 2D Operational Space](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/radg_decision_space.png)

<!-- Speaker Notes: Figure 3.5 shows the 2D operational state space of the RADG. The horizontal axis is semantic uncertainty, and the vertical axis is the GSNR margin. This cleanly visualizes our three operational regimes: auto-approval, physical replan, and early clarification. -->

---

## Slide 7: Formal HITL via Closed-Loop Reverse Prompting (Figures 3.6 & 3.7)

> [!LAYOUT]
> Two-column layout. Left: Reverse Prompting closed-loop. Right: Stateful sequence diagram.

### Closed-Loop Invariant & Stateful Interruption

- **Reverse Prompting:** Primary LLM translates $I_{NL} \to S_{PDDL}$; independent generation reconstructs $S_{PDDL} \to I_{recon}$; evaluator scores divergence $d_{sem}$.
- **Zero-Token Interruption:** When $U_{sem} > \tau_{sem}$, LangGraph `interrupt()` serializes state into checkpointer, releasing memory and compute threads during human dwell time.
- **Convergence Guarantee:** Monotonic constraint preservation bounds clarification cycles to $N_{max} = 3$.

![Figure: Reverse Prompting Loop](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/reverse_prompting_loop.png)
![Figure: HITL Sequence](docs/LLM_Wiki/wiki/thesis_drafts/3_SystemModel/figs_SystemModel/png/hitl_sequence.png)

<!-- Speaker Notes: Section 3.5 also contains two figures. Figure 3.6 shows the closed-loop reverse prompting cycle. Figure 3.7 details the sequence diagram showing how LangGraph suspends execution without token consumption, awaiting operator clarification before resuming cleanly. -->

---

## Slide 8: Status & Next Milestones (Sprint 4)

> [!LAYOUT]
> Left: Chapter 3 deliverables completed. Right: Next research and experimentation steps.

### Completed Deliverables & Transition to Sprint 4

- **Chapter 3 Ready for Overleaf:** All 5 sections drafted ([[thesis_drafts/3_SystemModel/3_1_Formal_Problem_Definition|Section 3.1]]–[[thesis_drafts/3_SystemModel/3_5_Formal_HITL_Reverse_Prompting|3.5]]) and consolidated into `chapter_3_system_model.txt` ([[thesis_drafts/3_SystemModel/chapter_3_system_model.txt]]) with LaTeX cross-references.
- **Visual Suite Complete:** 7 figures (6 Draw.io models, 1 Matplotlib plot documented in [[thesis_drafts/3_SystemModel/figs_SystemModel/README]]) exported to vector PDF and 300 DPI PNG.
- **Immediate Next Steps (Sprint 4):**
  1. Synthetic test corpus construction across 17-node [[session_summary/session_20260817_Nobel_Germany_Topology_Migration|Nobel-Germany optical topology]] (`test_corpus.json`).
  2. Benchmarking against non-adaptive baselines (No-HITL, Always-HITL) measuring token overhead and GSNR accuracy.
  3. Drafting Chapter 4: Implementation and System Integration according to [[thesis_drafts/Writing_Roadmap_v1|Writing Roadmap]].

<!-- Speaker Notes: In summary, Chapter 3 is 100% complete and consolidated for Overleaf. We are now transitioning directly into Sprint 4 evaluation benchmarks on the Nobel-Germany optical topology. Thank you, and I welcome any questions. -->
