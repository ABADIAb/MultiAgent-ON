---
title: "Chapter 3 - Section 3.4: Conceptual Framework"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, conceptual-framework, fail-fast, architecture-v5]
status: draft
---

# 3.2 Proposed Neurosymbolic Framework

To address the optimization objective in Section~\ref{sec:problem_definition}—minimizing human interventions and token usage while ensuring zero unsafe approvals ($UAR = 0\%$)—the system separates intent translation from physical calculation. The framework applies deterministic checks at each stage before sending configurations to the network.

## 3.2.1 The Fail-Fast Pre-Deployment Paradigm

To overcome the latency penalties and rework inherent in trial-and-error network configuration, the proposed architecture introduces a **Fail-Fast Risk-Adaptive Neurosymbolic Framework**. The core principle is a pre-deployment verification condition: *no configuration directive is dispatched to the optical controller until it has been verified through a sequence of independent validation gates*.

Unlike reactive paradigms—which execute unverified configurations and rely on controller error logs to trigger iterative regeneration—our framework evaluates plan viability along two axes:
1. **Linguistic and Structural Certainty (Semantic Domain):** Ensuring the high-level intent is fully disambiguated and faithfully translated into formal mathematical constraints.
2. **Physical-Layer Transmission Feasibility (Optical Domain):** Verifying that candidate lightpaths satisfy deterministic Generalized Signal-to-Noise Ratio (GSNR) margins and dynamic range limits under realistic fiber propagation models.

By ordering these validation checks sequentially, the architecture implements a **fail-fast operational hierarchy**: semantic verification is executed early to catch missing parameters before invoking non-linear physical simulations or path-finding algorithms.

---

## 3.2.2 End-to-End Pipeline Overview

<!-- FIGURE_PLACEHOLDER: conceptual_framework -->
> **Figure: Proposed Framework & 7-Phase Orchestration Pipeline** (`figs_SystemModel/pdf/conceptual_framework.pdf`)
> End-to-end architecture of the Risk-Adaptive Neurosymbolic Intent Orchestrator, illustrating the two-gate validation hierarchy: Gate 1 (Semantic RADG $U_{sem} \le \tau_{sem}$) preventing semantic drift, and Gate 2 (Physical RADG $\text{QoT}_{valid} = 1$) ensuring deterministic optical transmission feasibility prior to provisioning.

Figure~\ref{fig:conceptual_framework} shows the end-to-end architecture of the 7-phase neurosymbolic pipeline. As illustrated, the workflow is structured across two decoupled operational domains: the linguistic reasoning domain (Phases 1–3) shown in the upper area, and the deterministic physical domain (Phases 4–6) shown in the lower area, culminating in the control-plane synthesis interface (Phase 7). The architecture evaluates candidate configurations along a two-gate fail-fast hierarchy: Gate 1 (Semantic RADG, $U_{sem} \le \tau_{sem}$) validates syntactic structure and linguistic alignment before path calculation, while Gate 2 (Physical RADG, $\text{QoT}_{valid} = 1$) verifies optical transmission feasibility before provisioning. When an intent fails verification, the diagram illustrates the closed-loop feedback trajectories: Phase 3b triggers human clarification looping back to Phase 2, and Phase 6 triggers parameter relaxation looping back to Phase 2. The framework operates through seven interconnected functional phases managed by a stateful orchestration graph:

- **Phase 1: Intent Ingestion and Optical Retrieval-Augmented Generation (Optical RAG):**
  The raw operator intent $\mathcal{I}_{NL}$ is ingested. To prevent token context exhaustion, an optical topological retriever queries the active network state to extract a localized $k$-hop subtopology $G_{sub} \subseteq G$ encompassing the candidate endpoints. This subtopology extraction acts as a token-reduction strategy, bounding the context window prior to downstream translation into an enriched intent schema.
- **Phase 2: Context-Free Grammar (CFG) Validated PDDL Parsing:**
  The enriched intent is processed by an LLM prompted to act as a linguistic compiler, translating the operational requirements into Planning Domain Definition Language (PDDL) goal predicates and constraint clauses. A deterministic Context-Free Grammar (CFG) validator immediately audits the output to eliminate structural hallucinations ($v_{struct} \in \{0, 1\}$).
- **Phase 3: Automated Reverse Prompting & Semantic RADG ($U_{sem}$ Evaluation):**
  - **Phase 3a (Automated Reverse Prompting):** A separate instance of the LLM translates the formal PDDL specification back into natural language $\mathcal{I}_{recon}$ autonomously without pausing execution.
  - **Semantic RADG:** The gate computes the semantic uncertainty metric $U_{sem} = f(v_{struct}, d_{sem})$, measuring syntactic integrity and semantic divergence against the original intent. If $U_{sem} \le \tau_{sem}$, the pipeline proceeds autonomously to Phase 4 with **zero human intervention**.
  - **Phase 3b (HITL Clarification):** If $U_{sem} > \tau_{sem}$ (due to syntax invalidity or high ambiguity), execution interrupts, prompting the human operator for explicit clarification. If the operator provides new instructions, the system loops back to Phase 2. However, if the intent is structurally valid ($v_{struct}=1$) and the operator explicitly approves the system's reconstructed understanding, execution bypasses re-parsing and proceeds directly to Phase 4.
- **Phase 4: Deterministic Symbolic Solver:**
  Once semantic clarity is established ($U_{sem} \le \tau_{sem}$), the validated PDDL constraints enter the non-neural symbolic engine. The solver executes Yen's $K$-Shortest Paths algorithm over $G_{sub}$, pruning paths that violate topological constraints (e.g., node/link exclusions, maximum hop bounds).
- **Phase 5: Deterministic Quality of Transmission (QoT) Validation:**
  Each structurally valid candidate path $\pi_k \in \mathcal{K}_{path}$ is evaluated by a standalone physics engine implementing the Gaussian Noise (GN) model. The engine computes span-by-span amplifier noise accumulation, fiber attenuation, and non-linear interference (NLI), yielding exact GSNR predictions.
- **Phase 6: Physical RADG:**
  The physical feasibility vector $\text{QoT}_{valid}$ is evaluated. If at least one candidate path satisfies $\text{GSNR}(\pi) \ge \text{GSNR}_{th}$, the plan is marked as valid and **auto-approved**. If all paths violate transmission thresholds, the gate triggers a *Suggest Replan* signal via HITL interrupt, querying the operator to relax constraints (e.g., lower GSNR target, alternative modulation, or split bandwidth) and looping back to Phase 2.
- **Phase 7: Plan Synthesis and Configuration Provisioning:**
  Approved paths and full verification traces are formatted into an auditable Planning Report. This report constitutes the final verified output of the system, acting as an assured routing decision ready to be consumed by downstream configuration agents that dispatch the payloads to the controller.

---

## 3.2.3 State Representation and Transaction Lifecycle

The pipeline state $\mathcal{S}_{state}$ is maintained as an append-only structure during orchestration:

$$\mathcal{S}_{state} = \langle \mathcal{I}_{enriched}, G_{sub}, \mathcal{S}_{PDDL}, U_{sem}, \mathcal{K}_{path}, \mathbf{\Gamma}_{QoT}, \mathcal{D}_{action}, \mathcal{H}_{trace}, \mathcal{H}_{refine}, \kappa_{refine} \rangle$$

where:
- $\mathcal{I}_{enriched}$ is the operator intent after contextual enrichment.
- $G_{sub} = (V_{sub}, E_{sub})$ is the extracted $k$-hop subgraph context.
- $\mathcal{S}_{PDDL}$ represents the generated PDDL constraint specification.
- $U_{sem} \in [0, 1]$ stores the quantified semantic uncertainty score.
- $\mathcal{K}_{path}$ is the set of topological candidate paths.
- $\mathbf{\Gamma}_{QoT} = \{ (\pi_k, \text{GSNR}_k, P_{rx, k}, \text{QoT}_{valid, k}) \}_{k=1}^K$ stores the computed physical metrics.
- $\mathcal{D}_{action} \in \{ \text{approve}, \text{replan} \}$ is the resolved decision outcome.
- $\mathcal{H}_{trace}$ is the append-only message list preserving the chronological execution trace.
- $\mathcal{H}_{refine} = (\mathcal{F}_1, \dots, \mathcal{F}_k)$ is the chronological sequence of operator clarification and replan feedback.
- $\kappa_{refine} \in \{0, \dots, N_{\max}\}$ is the active refinement counter bounded by $N_{\max} = 3$.

State transitions use deterministic rules to ensure that if a loopback occurs (e.g., from Phase 3b or Phase 6 back to Phase 2), the system preserves the audit history and operator feedback trail while resetting temporary execution variables. This prevents infinite loops and ensures that prior refinement constraints are maintained.

To formalize the architectural boundary that decouples neural intent translation from deterministic graph algorithms and physics simulations, Section~\ref{sec:neurosymbolic_separation} details the formal PDDL domain and Context-Free Grammar (CFG) validation layer.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure Placement (`conceptual_framework`):** Insert the complete flowchart diagram representing the 7 phases, highlighting the two decision gates with distinct visual boundaries.
> 
> **Key Distinctions to Emphasize:** Highlight how the 2-gate sequential model differs from traditional single-pass LLM wrappers (such as raw ReAct agents or stateless chatbot interfaces).
