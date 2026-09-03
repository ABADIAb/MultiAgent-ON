---
title: "Chapter 3 - Section 3.2: Conceptual Framework"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, conceptual-framework, fail-fast, architecture-v5]
status: draft
---

# 3.2 Conceptual Framework

## 3.2.1 The Fail-Fast Pre-Deployment Paradigm

To overcome the latency penalties and operational risks of trial-and-error network configuration, the proposed architecture introduces a **Fail-Fast Risk-Adaptive Neurosymbolic Framework**. The foundational premise rests on a strict pre-deployment verification invariant: *no configuration directive shall be dispatched to the physical or virtual optical controller until it has been verified through a sequence of orthogonal, risk-bounded validation gates*.

Unlike reactive paradigms—which execute unverified configurations and rely on controller error logs to trigger iterative regeneration—our framework evaluates plan viability along two distinct axes:
1. **Linguistic and Structural Certainty (Semantic Domain):** Ensuring the high-level intent is fully disambiguated and faithfully translated into formal mathematical constraints.
2. **Physical-Layer Transmission Feasibility (Optical Domain):** Verifying that candidate lightpaths satisfy deterministic Generalized Signal-to-Noise Ratio (GSNR) margins and dynamic range limits under realistic fiber propagation models.

By decoupling and ordering these validation checks sequentially, the architecture implements a **fail-fast operational hierarchy**: computationally cheap semantic verification is executed early to catch misunderstandings and missing parameters before invoking non-linear physical simulations or path-finding algorithms.

```
       [ Unstructured Intent ]
                  │
                  ▼
      ┌───────────────────────┐
      │  Phase 1: Optical RAG │  ◄── Injects Localized k-hop Topology Context
      └───────────┬───────────┘
                  ▼
      ┌───────────────────────┐
      │ Phase 2: PDDL Parsing │  ◄── Constrained LLM Translation (Intent → PDDL)
      └───────────┬───────────┘
                  ▼
      ┌───────────────────────┐
      │Phase 3a: Rev. Prompt  │  ◄── Automated PDDL → NL Reconstruction (0 interrupts)
      └───────────┬───────────┘
                  ▼
    ═════════════════════════════
    GATE 1: Semantic Gate ($U_{sem}$)
    ═════════════════════════════
          │               │
    [U_sem > τ_sem] [U_sem ≤ τ_sem] (Autonomous Pass)
          │               │
          ▼               ▼
    ┌───────────┐   ┌─────────────────────────┐
    │ Phase 3b: │   │ Phase 4: Symbolic Solver│ ◄── Deterministic K-Shortest Paths
    │ HITL      │   └────────────┬────────────┘
    │ (Clarify) │                ▼
    └─────┬─────┘   ┌─────────────────────────┐
          │         │ Phase 5: QoT Validation │ ◄── Deterministic GN-Model Physics
          └────────►└────────────┬────────────┘
          (Loops back to Phase 2)▼
                    ═════════════════════════════
                    GATE 2: Physical Risk Gate ($QoT_{valid}$)
                    ═════════════════════════════
                          │               │
                    [QoT Invalid]   [QoT Valid] (Auto-Approve)
                          │               │
                          ▼               ▼
                    ┌───────────┐   ┌─────────────────────────┐
                    │  Suggest  │   │   Phase 7: Synthesis    │
                    │  Replan   │   │     & Provisioning      │
                    └─────┬─────┘   └─────────────────────────┘
                          │
                          └────────► (Refines Constraints to Phase 2)
```

---

## 3.2.2 End-to-End Pipeline Overview

The framework operates through seven interconnected functional phases managed by a stateful orchestration graph:

- **Phase 1: Intent Ingestion and Optical Retrieval-Augmented Generation (Optical RAG):**
  The raw operator intent $\mathcal{I}_{NL}$ is ingested. To prevent token context exhaustion, an optical topological retriever queries the active network state to extract a localized $k$-hop subtopology $G_{sub} \subseteq G$ encompassing the candidate endpoints. Relevant ITU-T optical grid specifications and amplifier parameters are merged into an enriched intent schema.
- **Phase 2: Context-Free Grammar (CFG) Validated PDDL Parsing:**
  The enriched intent is processed by an LLM acting strictly as a linguistic compiler, translating the operational requirements into Planning Domain Definition Language (PDDL) goal predicates and constraint clauses. A deterministic Context-Free Grammar (CFG) validator immediately audits the output to eliminate structural hallucinations ($v_{struct} \in \{0, 1\}$).
- **Phase 3: Automated Reverse Prompting & Semantic Uncertainty Gate ($U_{sem}$ Evaluation):**
  - **Phase 3a (Automated Reverse Prompting):** The LLM reconstructs the PDDL specification back into natural language $\mathcal{I}_{recon}$ autonomously without pausing execution.
  - **Semantic Gate:** The gate computes the composite semantic uncertainty metric $U_{sem} = f(v_{struct}, d_{sem})$, measuring syntactic integrity and semantic divergence against the original intent. If $U_{sem} \le \tau_{sem}$, the pipeline proceeds autonomously to Phase 4 with **zero human intervention**.
  - **Phase 3b (HITL Clarification):** If $U_{sem} > \tau_{sem}$ (due to syntax invalidity or high ambiguity), execution interrupts, prompting the human operator for explicit clarification and looping back to Phase 2 with operator guidance.
- **Phase 4: Deterministic Symbolic Solver:**
  Once semantic clarity is established ($U_{sem} \le \tau_{sem}$), the validated PDDL constraints are passed to a non-neural symbolic graph engine. The solver executes Yen's $K$-Shortest Paths algorithm over $G_{sub}$, pruning paths that violate topological constraints (e.g., node/link exclusions, maximum hop bounds).
- **Phase 5: Deterministic Quality of Transmission (QoT) Validation:**
  Each structurally valid candidate path $\pi_k \in \mathcal{K}_{path}$ is evaluated by a standalone physics engine implementing the analytical coherent Gaussian Noise (GN) model. The engine computes span-by-span amplifier noise accumulation, fiber attenuation, and non-linear interference (NLI), yielding exact GSNR predictions.
- **Phase 6: Physical Risk Decision Gate (RADG):**
  The physical feasibility vector $\text{QoT}_{valid}$ is evaluated. If at least one candidate path satisfies $\text{GSNR}(\pi) \ge \text{GSNR}_{th}$, the plan is marked as valid and **auto-approved**. If all paths violate transmission thresholds, the gate triggers a *Suggest Replan* signal via HITL interrupt, querying the operator to relax constraints (e.g., lower GSNR target, alternative modulation, or split bandwidth) and looping back to Phase 2.
- **Phase 7: Plan Synthesis and Configuration Provisioning:**
  Approved paths, complete with their deterministic physical telemetry and full verification traces, are formatted into an auditable Planning Report. Upon final confirmation, configuration payloads are dispatched to the SDON controller via RESTCONF/SSH interfaces.

---

## 3.2.3 State Representation and Transaction Lifecycle

The pipeline state $\mathcal{S}_{state}$ is managed as an immutable, append-only data structure within the orchestration runtime:

$$\mathcal{S}_{state} = \langle \mathcal{I}_{enriched}, G_{sub}, \mathcal{S}_{PDDL}, U_{sem}, \mathcal{K}_{path}, \mathbf{\Gamma}_{QoT}, \mathcal{D}_{action}, \mathcal{H}_{trace} \rangle$$

where:
- $\mathcal{I}_{enriched}$ is the operator intent after contextual enrichment.
- $G_{sub} = (V_{sub}, E_{sub})$ is the extracted $k$-hop subgraph context.
- $\mathcal{S}_{PDDL}$ represents the generated PDDL constraint specification.
- $U_{sem} \in [0, 1]$ stores the quantified semantic uncertainty score.
- $\mathcal{K}_{path}$ is the set of topological candidate paths.
- $\mathbf{\Gamma}_{QoT} = \{ (\pi_k, \text{GSNR}_k, P_{rx, k}, \text{QoT}_{valid, k}) \}_{k=1}^K$ stores the computed physical metrics.
- $\mathcal{D}_{action} \in \{ \text{approve}, \text{replan} \}$ is the resolved decision outcome.
- $\mathcal{H}_{trace}$ is the append-only message list preserving the chronological execution trace.

State transitions are governed by deterministic guard functions, ensuring that backward loopbacks (e.g., Phase 3b $\to$ Phase 2 or Phase 6 $\to$ Phase 2) preserve the audit history while resetting transient execution variables, preventing infinite recursion and memory leaks.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.2 Placement:** Insert the complete Swimlane/Flowchart diagram representing the 7 phases, highlighting the two decision gates with distinct visual boundaries.
> 
> **Key Distinctions to Emphasize:** Highlight how the 2-gate sequential model differs from traditional single-pass LLM wrappers (such as raw ReAct agents or stateless chatbot interfaces).
