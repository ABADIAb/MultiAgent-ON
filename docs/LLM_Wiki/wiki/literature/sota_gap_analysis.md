---
title: "SOTA Gap Analysis: Agentic AI in Optical Networks"
date: 2026-07-17
tags: [literature, gap-analysis, sota, comparison, planning-loop, risk-adaptive, radg]
status: active
---

# SOTA Gap Analysis: Agentic AI in Optical Networks

This document synthesizes the conclusions from our literature comparison ([[lit_comparison]]), the detailed paper analyses ([[Confucius_SIGCOMM2025]], [[SJTU_Invited_Tutorial_JOCN2026]], [[AutoLight_ECOC2025]]), and the [[Scope_Pivot_20260706|scope pivot decisions]] to position our [[Architecture_v5|Risk-Adaptive Neurosymbolic Intent Planning System]].

---

## Key Questions Answered

### 1. What problem does each existing work solve?

- **Confucius (Meta, SIGCOMM 2025):** Solves orchestration of complex, long-horizon tasks at hyperscale for IP and datacenter networks. Production-grade with 60+ applications, 4,160 users, 31.62M messages. DAG-based workflows, RAG memory, Collector primitive for structured human disambiguation. See [[Confucius_SIGCOMM2025]].
- **PoliMi/EURECOM Pipeline:** Automates the full lifecycle (Day-0 to Day-N) of SDONs using LLMs to translate intent into configuration. Single-agent, stateless, GBNF grammar-constrained.
- **PoliMi/CNSM 2025 (El Hachimi et al.):** Translates natural language intents into SDN flow rules using LLMs with an iterative clarification module and a retry-based correction mechanism that monitors deployment attempts. Achieves 96.7% deployment accuracy at ~$0.08/100 configs. Model-agnostic pipeline with RAG and intermediate YAML representation. See Section 3 below.
- **AutoLight / SJTU (ECOC 2025 + JOCN 2026):** Hierarchical multi-agent system **built on LangGraph** achieving ~98% task completion for L4 autonomous optical network operations. Chain of Identity (CoI) for inter-agent coordination. Cross-domain field trial (440 km backbone + DCI + intra-DC). See [[AutoLight_ECOC2025]] and [[SJTU_Invited_Tutorial_JOCN2026]].
- **IntentLLM:** Chatbot interface for SDN slice intent management (create/find/explain). Single agent, no QoT.
- **HearthNet:** Conflict resolution and actuation auditing at the edge for IoT environments.

### 2. What are the limitations of existing approaches?

Current approaches have the following gaps **specifically in the planning and pre-deployment decision phase**:

- **Confucius:** Production-proven orchestration but **completely unaware of optical physical-layer constraints**. No SNR, no GN model, no QoT estimation. Their documented failure modes (context loss, hallucination) directly motivate our [[Constraint_Isolation|neurosymbolic constraint isolation]].
- **PoliMi/EURECOM Pipeline:** Lacks multi-agent coordination, long-term memory, and formal [[HITL_Refinement|HITL]] safety. The planning phase is a single-pass LLM call — no iterative refinement with the operator.
- **PoliMi/CNSM 2025 (El Hachimi et al.):** Implements intent clarification and retry-based correction, but:
  - The retry mechanism is **post-deployment**: configurations are sent to the controller, and only after observing a deployment failure does the system provide feedback to the LLM for regeneration.
  - No **pre-deployment risk assessment** — physically infeasible configurations reach the controller before correction.
  - Fixed retry count (N attempts) with no adaptive decision logic — no distinction between semantic ambiguity and physical infeasibility.
  - Targets SDN flow rules (IP domain), not optical physical-layer constraints (GSNR, GN model).
  - No formal HITL convergence guarantee — the clarification is conversational, not formally bounded.
- **SJTU (AutoLight):** The most complete optical-domain work but:
  - Relies on **structured task definitions** rather than natural language intent parsing.
  - **No HITL mechanism** — the tutorial mentions HITL as essential but AutoLight implements no formal operator validation.
  - Their planning agents orchestrate pre-defined task sequences, not intent-to-plan refinement loops.
  - Does not produce a structured Planning Report artifact for operator review.
- **IntentLLM:** No multi-agent coordination, no QoT validation, no iterative refinement.

### 3. What is the specific research gap addressed by this project?

The **MultiAgentON** project targets the **pre-deployment intent planning decision** — the phase where unstructured operator intent must be assessed for both semantic correctness and physical feasibility BEFORE any configuration reaches the network.

The gap is defined by combining four capabilities absent in current literature:

1. **Joint Semantic + QoT Risk Assessment (RADG).** No existing system evaluates BOTH semantic uncertainty (did the LLM correctly interpret the intent?) AND physical-layer QoT risk (is the lightpath feasible?) as a joint pre-deployment decision. PoliMi/CNSM 2025 retries after failure; our system prevents failure by diagnosing the risk class and routing to the appropriate corrective action.

2. **Risk-Adaptive HITL Engagement.** Existing systems are either always-on HITL (Confucius Collector, PoliMi/CNSM 2025 clarification) or no HITL (AutoLight). Our RADG engages the human operator proportionally to the assessed risk — auto-approving safe intents, clarifying ambiguous ones, suggesting replans for marginal ones, and rejecting infeasible ones.

3. **Neurosymbolic Constraint Isolation.** The LLM is restricted to linguistics (Intent → PDDL). A deterministic Symbolic Solver and GN-model tool handle the physics, guaranteeing 100% physically viable routes in the approved set.

4. **Formal Evaluation Framework.** V5 includes a structured comparison against No-HITL, Always-HITL, and Fixed-Retry baselines using five metrics (UAR, HIC, QFR, E2EL, TC), enabling measurable validation of the contribution.

> **Scope note:** The thesis focuses exclusively on the planning and pre-deployment decision phase. Lightpath provisioning, compute scheduling, and operational lifecycle management are documented as future work. See [[Scope_Pivot_20260706]].

### 4. Why not a full MAS?

The decision to focus on the planning phase rather than a full multi-agent lifecycle system is a direct consequence of SOTA analysis:

| Capability | Already Demonstrated By | Our Position |
|:---|:---|:---|
| Multi-agent LLM orchestration | Confucius (60+ production apps) | Framework validated, not novel |
| LangGraph-based optical MAS | AutoLight (98% task completion) | Framework choice confirmed, not novel |
| Hierarchical agent coordination | AutoLight CoI, Confucius DAG | Patterns established |
| Full lifecycle automation | AutoLight (Day-0 to Day-N) | Covered by SJTU group |
| Intent clarification + retry | PoliMi/CNSM 2025 (96.7% accuracy) | Mechanism exists, but post-deployment and non-adaptive |

What IS novel is the **pre-deployment risk-adaptive decision intelligence**: how a system jointly assesses semantic and physical-layer risk to determine the appropriate action BEFORE deployment — a space no existing system covers.

---

## Gap-Oriented SOTA Comparison Table

| Work | Scenario | NL Intent Parsing | QoT-Aware Planning | Risk-Adaptive HITL | Pre-Deployment Decision | Planning Report |
|:---|:---|:---|:---|:---|:---|:---|
| **Confucius (Meta)** | Hyperscale IP/DC | Collector (structured Q&A) | ❌ None | ❌ Always-on | ❌ | ❌ |
| **PoliMi Pipeline** | Optical lifecycle | ✅ Basic NL parsing | Partial (controller) | ❌ None | ❌ | ❌ |
| **PoliMi/CNSM 2025** | SDN flow rules | ✅ NL + clarification | ❌ None (IP domain) | ❌ Fixed retry (post-deploy) | ❌ Post-deployment | ❌ |
| **SJTU (AutoLight)** | Cross-domain optical | ❌ Structured tasks | ✅ DT toolset | ❌ None | ❌ | ❌ |
| **IntentLLM** | SDN Slicing | ✅ NL intent | ❌ None | ❌ None | ❌ | ❌ |
| **MultiAgentON (ours)** | Optical planning | ✅ NL → PDDL + Reverse Prompting | ✅ Neurosymbolic Solver + GN model | ✅ RADG ($U_{sem}$ + $R_{qot}$) | ✅ Joint pre-deployment gate | ✅ Structured artifact |

---

## Visual Gap Positioning

```
                 Risk-Adaptive
                 Pre-Deployment
                     Decision
                        ▲
                        │
                        │              ● MultiAgentON V5 (ours)
                        │                ▲ + Joint U_sem + R_qot
                        │                │ + 4-outcome decision gate
                        │                │ + Formal evaluation
                        │
    ────────────────────┼────────────────────► QoT-Aware
                        │                       Planning
     PoliMi/CNSM ●     │         ● SJTU
     (post-deploy       │         (no HITL)
      retry)            │
                        │
       IntentLLM ●      │      ● PoliMi Pipeline
                        │
          HearthNet ●   │   ● Confucius
                        │     (no QoT)
                        │
                  No Pre-Deployment
                     Decision
```

Our work occupies the **upper-right quadrant**: combining QoT-aware planning with a risk-adaptive pre-deployment decision mechanism — a space no existing system covers.

---

## Cross-References

- [[Architecture_v5]] — Risk-Adaptive Neurosymbolic Intent Planning architecture
- [[ProblemStatement_v5]] — Thesis problem definition with evaluation framework
- [[Scope_Pivot_20260706]] — Rationale for the architectural evolution (V2 → V5)
- [[experiments/MVP_Roadmap]] — Sprint plan with RADG and evaluation experiments
- [[lit_comparison]] — Detailed SOTA comparison
- [[Confucius_SIGCOMM2025]] — Meta's multi-agent framework
- [[AutoLight_ECOC2025]] — SJTU's L4 autonomous optical network
- [[SJTU_Invited_Tutorial_JOCN2026]] — SJTU's comprehensive tutorial
