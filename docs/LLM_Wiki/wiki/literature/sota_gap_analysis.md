---
title: "SOTA Gap Analysis: Agentic AI in Optical Networks"
date: 2026-06-22
tags: [literature, gap-analysis, sota, comparison, planning-loop]
status: active
---

# SOTA Gap Analysis: Agentic AI in Optical Networks

This document synthesizes the conclusions from our literature comparison ([[lit_comparison]]), the detailed paper analyses ([[Confucius_SIGCOMM2025]], [[SJTU_Invited_Tutorial_JOCN2026]], [[AutoLight_ECOC2025]]), and the [[Scope_Pivot_20260621|scope pivot decision]] to position our [[Architecture_v3|Intent Planning System]].

---

## Key Questions Answered

### 1. What problem does each existing work solve?

- **Confucius (Meta, SIGCOMM 2025):** Solves orchestration of complex, long-horizon tasks at hyperscale for IP and datacenter networks. Production-grade with 60+ applications, 4,160 users, 31.62M messages. DAG-based workflows, RAG memory, Collector primitive for structured human disambiguation. See [[Confucius_SIGCOMM2025]].
- **PoliMi/EURECOM Pipeline:** Automates the full lifecycle (Day-0 to Day-N) of SDONs using LLMs to translate intent into configuration. Single-agent, stateless, GBNF grammar-constrained.
- **AutoLight / SJTU (ECOC 2025 + JOCN 2026):** Hierarchical multi-agent system **built on LangGraph** achieving ~98% task completion for L4 autonomous optical network operations. Chain of Identity (CoI) for inter-agent coordination. Cross-domain field trial (440 km backbone + DCI + intra-DC). See [[AutoLight_ECOC2025]] and [[SJTU_Invited_Tutorial_JOCN2026]].
- **IntentLLM:** Chatbot interface for SDN slice intent management (create/find/explain). Single agent, no QoT.
- **HearthNet:** Conflict resolution and actuation auditing at the edge for IoT environments.

### 2. What are the limitations of existing approaches?

Current approaches have the following gaps **specifically in the planning phase**:

- **Confucius:** Production-proven orchestration but **completely unaware of optical physical-layer constraints**. No SNR, no GN model, no QoT estimation. Their documented failure modes (context loss, hallucination) directly motivate our [[Constraint_Isolation|neurosymbolic constraint isolation]].
- **PoliMi Pipeline:** Lacks multi-agent coordination, long-term memory, and formal [[HITL_Refinement|HITL]] safety. The planning phase is a single-pass LLM call — no iterative refinement with the operator.
- **SJTU (AutoLight):** The most complete optical-domain work but:
  - Relies on **structured task definitions** rather than natural language intent parsing.
  - **No HITL mechanism** — the tutorial mentions HITL as essential but AutoLight implements no formal operator validation.
  - Their planning agents (Planner agents) orchestrate pre-defined task sequences, not intent-to-plan refinement loops.
  - Does not produce a structured Planning Report artifact for operator review.
- **IntentLLM:** No multi-agent coordination, no QoT validation, no iterative refinement.

### 3. What is the specific research gap addressed by this project?

The **MultiAgentON** project targets the **Intent Planning Loop** — the iterative phase where unstructured operator intent is translated into a QoT-validated optical routing plan through multi-turn HITL refinement.

The gap is defined by combining three capabilities absent in current literature:

1. **Natural language intent parsing** with formal reverse prompting — converting unstructured operator intent into a validated `sla_matrix` via [[HITL_Refinement|Reverse Prompting]] and `interrupt()`. No existing work implements this as a first-class capability in the optical domain.

2. **[[QoT_Awareness|QoT-aware]] path evaluation** with strict [[Constraint_Isolation|neurosymbolic separation]] — LLMs reason over topology and intent; deterministic Python GN model tools calculate physical-layer constraints (SNR, OSNR). This avoids the hallucination risks documented by Confucius and the reasoning limitations acknowledged by SJTU.

3. **Multi-turn HITL planning refinement** — not a single approve/reject checkpoint (Confucius Collector), not a transitional mechanism (SJTU), but an **iterative conversational loop** where the operator and the system co-construct the routing plan through successive refinements. Each iteration produces a structured [[Architecture_v3|Planning Report]] with QoT feasibility data.

> **Scope note:** The thesis focuses exclusively on the planning phase. Lightpath provisioning, compute scheduling, and operational lifecycle management are documented as future work. See [[Scope_Pivot_20260621]].

### 4. Why not a full MAS?

The decision to focus on the planning phase rather than a full multi-agent lifecycle system is a direct consequence of SOTA analysis:

| Capability | Already Demonstrated By | Our Position |
|:---|:---|:---|
| Multi-agent LLM orchestration | Confucius (60+ production apps) | Framework validated, not novel |
| LangGraph-based optical MAS | AutoLight (98% task completion) | Framework choice confirmed, not novel |
| Hierarchical agent coordination | AutoLight CoI, Confucius DAG | Patterns established |
| Full lifecycle automation | AutoLight (Day-0 to Day-N) | Covered by SJTU group |

What IS novel is the **planning intelligence**: how a system reasons from natural language through physics-constrained path selection to an operator-approved plan. This is the intersection where our three gaps converge.

---

## Gap-Oriented SOTA Comparison Table

| Work | Scenario | NL Intent Parsing | QoT-Aware Planning | Multi-Turn HITL | Planning Report |
|:---|:---|:---|:---|:---|:---|
| **Confucius (Meta)** | Hyperscale IP/DC | Collector (structured Q&A) | ❌ None | ❌ Single-pass | ❌ |
| **PoliMi Pipeline** | Optical lifecycle | ✅ Basic NL parsing | Partial (controller) | ❌ None | ❌ |
| **SJTU (AutoLight)** | Cross-domain optical | ❌ Structured tasks | ✅ DT toolset | ❌ None | ❌ |
| **IntentLLM** | SDN Slicing | ✅ NL intent | ❌ None | ❌ None | ❌ |
| **MultiAgentON (ours)** | Optical planning | ✅ NL → `sla_matrix` + reverse prompting | ✅ [[QoT_Awareness\|Neurosymbolic GN model]] | ✅ `interrupt()` loop | ✅ Structured artifact |

---

## Visual Gap Positioning

```
                        QoT-Aware
                            ▲
                            │
                  SJTU ●    │    ● MultiAgentON (ours)
                            │         ▲ + Multi-turn HITL
                            │         │ + NL Intent Parsing
                            │         │ + Planning Report
                            │
        ────────────────────┼────────────────────► NL Intent
                            │
           IntentLLM ●      │      ● PoliMi
                            │
              HearthNet ●   │   ● Confucius
                            │
                     Not QoT-Aware
```

Our work occupies the **upper-right quadrant**: combining NL intent parsing with QoT-aware planning, augmented by multi-turn HITL and a structured Planning Report — a space no existing system covers.

---

## Cross-References

- [[Architecture_v3]] — Intent Planning System architecture
- [[ProblemStatement_v3]] — Thesis problem definition
- [[Scope_Pivot_20260621]] — Rationale for the planning-focused scope
- [[lit_comparison]] — Detailed SOTA comparison
- [[Confucius_SIGCOMM2025]] — Meta's multi-agent framework
- [[AutoLight_ECOC2025]] — SJTU's L4 autonomous optical network
- [[SJTU_Invited_Tutorial_JOCN2026]] — SJTU's comprehensive tutorial
