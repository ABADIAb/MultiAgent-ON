---
title: "SOTA Gap Analysis: Agentic AI in Optical Networks"
date: 2026-06-21
tags: [literature, gap-analysis, sota, comparison]
status: active
---

# SOTA Gap Analysis: Agentic AI in Optical Networks

This document synthesizes the conclusions from our literature comparison ([[lit_comparison]]), the detailed paper analyses ([[Confucius_SIGCOMM2025]], [[SJTU_Invited_Tutorial_JOCN2026]]), and the SOTA analysis presentation ([[Presentation_20260604_SOTA_Analysis]]) to clarify the key architectural families in Intent-Based Optical Networks (IBON) and position our [[Architecture_v2]].

---

## Key Questions Answered

### 1. What problem does each existing work solve?

- **Confucius (Meta, SIGCOMM 2025):** Solves the orchestration of complex, long-horizon tasks at a hyperscale level for IP and datacenter networks. A production-grade system with 60+ applications, 4,160 users, and 31.62M messages. Decomposes tasks into DAG-based workflows, integrates with existing tools via three DSLs (TML, ODS, Robotron), and uses RAG for long-term memory. Key contribution: the **Collector primitive** for structured human disambiguation — a form of HITL refinement.
- **PoliMi/EURECOM Pipeline:** Automates the full lifecycle (Day-0 to Day-N) of Software-Defined Optical Networks using LLMs to translate intent into configuration.
- **AutoLight / SJTU (ECOC 2025 + JOCN 2026):** The SJTU group has produced two complementary works. The **ECOC 2025 field trial** (see [[AutoLight_ECOC2025]]) demonstrates AutoLight — a hierarchical multi-agent system **built on LangGraph** that achieves ~98% task completion (3.2× single-agent) across cross-domain scenarios (440 km backbone + DCI + intra-DC). Key innovation: **Chain of Identity (CoI)** — a three-mechanism technique (formatted handoffs, pseudo-SystemMessage injection, pre-execution declaration) for maintaining identity coherence across agent interactions. The **JOCN 2026 invited tutorial** (see [[SJTU_Invited_Tutorial_JOCN2026]]) is a comprehensive 225+ reference survey covering the full agentic stack for AONs: domain adaptation, prompting, RAG, hierarchical MAS, MCP, and a three-part toolset (monitoring, DT, management & control).
- **IntentLLM:** Focuses on user interaction, enabling a chatbot interface to create, find, and explain SDN slice intents.
- **HearthNet:** Tackles conflict resolution and actuation auditing at the edge for smart home/IoT environments.

### 2. What type of agentic architecture does each work use?

- **Confucius:** DAG-based multi-agent workflow orchestration. Core abstraction is the Analect (typed function with tracing). Primitives: Translator, Selector, Collector, Ensemble (multi-model consensus), Orchestrator (autonomous step-by-step planning). Built on Pydantic + LangChain. **No fine-tuning required** — prompt engineering + RAG achieves up to 35% improvement over fine-tuned baselines.
- **PoliMi Pipeline:** A single-agent, stateless pipeline using a locally fine-tuned LLM with grammar-constrained generation (GBNF).
- **SJTU (AutoLight):** Hierarchical multi-AI-agent system **built on LangGraph**. **Planner agents** orchestrate workflows via plan tracking tables; **Task agents** handle specific functions (resource allocation, failure management, Knowledge Retriever with RAG). Uses **Chain of Identity (CoI)** for inter-agent coordination — identity injection via ToolMessages to maintain role coherence. All agents are ReAct agents powered by GPT-4o. Advocates for MCP as the interoperability standard.
- **IntentLLM:** A single conversational chatbot agent integrated with a cloud-native SDN controller.
- **HearthNet:** An edge multi-agent system utilizing Git-backed shared state and MQTT buses.

### 3. What network control function does each work support?

- **Confucius:** General network applications and workflow automation (capacity planning, fault diagnosis, configuration, monitoring). Uses three DSLs for tool integration but has **no optical transport or physical-layer awareness**.
- **PoliMi Pipeline:** Natural Language (NL) intent to RESTConf configuration parsing and optical lifecycle automation.
- **SJTU (AutoLight):** Cross-domain lifecycle management — real-time resource allocation during distributed training, backbone wavelength establishment, DCI failure management (detection + mitigation), backbone failure management across information-isolated domains. The tutorial additionally covers continuous optimization (power control, RWA) and emphasizes DT as indispensable.
- **IntentLLM:** SDN slicing and intent explanation.
- **HearthNet:** Conflict resolution via actuation leases in IoT.

### 4. What are the limitations of existing approaches?

Current approaches have the following gaps in the context of our thesis objectives (QoT-aware routing with HITL):

- **Confucius:** Production-proven multi-agent orchestration but **completely unaware of optical physical-layer constraints** (no SNR, no GN model, no QoT estimation). Their documented failure modes (context loss, hallucination, lack of early failure) directly motivate our [[Constraint_Isolation|neurosymbolic constraint isolation]].
- **PoliMi Pipeline:** Lacks multi-agent coordination, long-term memory, and formal [[HITL_Refinement|Human-in-the-Loop]] safety validations. Stateless design limits complex multi-step reasoning.
- **SJTU (AutoLight):** The most complete optical-domain work but:
  - Relies on **structured task definitions** rather than true natural language intent parsing.
  - Does not implement NL → `sla_matrix` conversion with reverse prompting.
  - **No HITL mechanism** — the tutorial mentions HITL as an essential *transition mechanism* but AutoLight itself implements no formal operator validation.
  - Uses **LangGraph** (same as us) but with a different coordination pattern: CoI (identity injection) vs. our hub-and-spoke Supervisor.
  - Focuses primarily on **operational tasks** (resource allocation, failure management) rather than **intent-driven routing** from natural language.
- **IntentLLM:** No multi-agent coordination or QoT validation.
- **HearthNet:** IoT-focused, non-optical domain.

### 5. What is the specific research gap addressed by this project?

The **MultiAgentON** project targets **QoT-aware optical routing driven by natural language intent** via a multi-agent framework. The gap is defined by combining three critical elements missing in current literature:

1. **Natural language intent parsing** with formal HITL refinement — converting unstructured operator intent into a validated `sla_matrix` via [[HITL_Refinement|Reverse Prompting]] and `interrupt()`. No existing work implements this as a first-class capability.
2. **[[QoT_Awareness|QoT-aware]] optical routing** with strict [[Constraint_Isolation|neurosymbolic separation]] — LLMs reason over topology and intent; deterministic Python GN model tools calculate physical-layer constraints (SNR, OSNR). This avoids the hallucination risks documented by Confucius and the reasoning limitations acknowledged by SJTU.
3. **Formal HITL safety validation** — not as a transitional mechanism (SJTU) or structured Q&A (Confucius Collector), but as an architectural primitive (`interrupt()`) embedded in the LangGraph workflow that enforces operator validation before any network-modifying action.

> **Note:** Compute scheduling is deferred as future work (documented scope refinement). The project covers Day-0 through Day-N for routing and QoT validation.

---

## Gap-Oriented SOTA Comparison Table

| Work | Scenario | Agent Architecture | Network Function | NL Intent Parsing | QoT Awareness | HITL Protocol | Key Limitation vs. Our Work |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Confucius (Meta)** | Hyperscale IP/DC | DAG orchestration, Ensemble, RAG | 60+ production apps | Collector (structured Q&A) | ❌ None | Collector (disambiguation) | No optical transport, no physics |
| **PoliMi Pipeline** | Optical lifecycle | Single-agent, GBNF | NL → RESTConf config | ✅ Basic NL parsing | Partial (relies on controller) | ❌ None | Stateless, no multi-agent, no HITL |
| **SJTU (AutoLight / Tutorial)** | Cross-domain optical lifecycle | LangGraph, Hierarchical MAS, CoI | Resource alloc, wavelength, failure | ❌ Structured tasks | ✅ Full DT toolset | ❌ None (Mentioned in tutorial) | No NL parsing, no formal HITL |
| **IntentLLM** | SDN Slicing | Single chatbot | Create/Find/Explain | ✅ NL intent | ❌ None | ❌ None | No multi-agent, no QoT |
| **HearthNet** | Edge IoT | Edge MAS (Git/MQTT) | Actuation leases | ❌ N/A | ❌ N/A | Audit leases | Non-optical domain |
| **MultiAgentON (ours)** | Optical routing | [[Architecture_v2\|LangGraph Orchestrator]] | Intent → QoT-validated route | ✅ NL → `sla_matrix` + reverse prompting | ✅ [[QoT_Awareness\|Neurosymbolic GN model]] | ✅ Formal `interrupt()` | — |

---

## Visual Gap Positioning

```
                        QoT-Aware
                            ▲
                            │
                  SJTU ●    │    ● MultiAgentON (ours)
                            │         ▲ + Formal HITL
                            │         │ + NL Intent Parsing
                            │
        ────────────────────┼────────────────────► NL Intent
                            │
           IntentLLM ●      │      ● PoliMi
                            │
              HearthNet ●   │   ● Confucius
                            │
                     Not QoT-Aware
```

Our work occupies the **upper-right quadrant**: combining NL intent parsing with QoT-aware routing, augmented by formal HITL — a space no existing system fully covers.
