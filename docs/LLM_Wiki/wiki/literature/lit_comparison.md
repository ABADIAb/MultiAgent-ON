---
title: "Literature Comparison: Agentic AI for Intent-Based Optical Networks"
date: 2026-06-21
tags: [literature, comparison, SOTA, agentic-ai, optical-networks, multi-agent, intent-based]
status: active
---

# Literature Comparison: Agentic AI Approaches for Intent-Based Optical Networks (2024–2026)

This document provides a systematic comparison of the state-of-the-art (SOTA) approaches in **Agentic AI for Intent-Based Optical Networks (IBON)** against the **MultiAgentON** architecture defined in [[Architecture_v2]]. The goal is to identify where our work fits within the research landscape, what differentiates it, and what strategic direction to take for the thesis.

---

## 1. Taxonomy of Existing Approaches

The current SOTA can be categorized into **five main architectural families**. Each family solves a different slice of the IBON problem, and no single work covers the full scope of our thesis.

### 1.1 Hyperscale Intent-Driven Multi-Agent Frameworks

| Work | Key Innovation | Venue |
|---|---|---|
| **Confucius** (Meta, Wang et al.) | DAG-based workflow orchestration, hibernate-and-wake for long-horizon tasks, RAG for long-term memory. 60+ production network applications. | ACM SIGCOMM 2025 |

- **Detailed Analysis**: See [[Confucius_SIGCOMM2025]] for the full paper summary.
- **Relevance to MultiAgentON**: Confucius validates the core premise of our work — that multi-agent LLM systems can manage real networks at scale. Their DAG-based workflow modeling parallels our LangGraph `StateGraph`. Their **Collector primitive** independently validates our HITL reverse prompting pattern.
- **Key Difference**: Confucius operates on hyperscale IP/datacenter networks, NOT optical transport. It does not deal with physical-layer constraints (SNR, GN model, spectrum assignment). Our contribution is bringing this paradigm into the **optical domain** with [[QoT_Awareness|QoT-aware]] agents.
- **What We Can Reuse**: The hibernate-and-wake pattern is directly applicable to our future long-horizon operations (e.g., waiting for testbed responses). The **Ensemble primitive** (multi-model consensus) could improve critical routing decisions. Their documented failure modes (context loss, hallucination) directly motivate our [[Constraint_Isolation]] design.

### 1.2 Field-Trial LLM Pipelines for Optical Lifecycle Automation

| Work | Key Innovation | Venue |
|---|---|---|
| **PoliMi/EURECOM Pipeline** (Di Cicco, Tornatore et al.) | LoRA fine-tuning of Mistral-7B, GBNF grammar-constrained generation, 100% API accuracy, 83% resource reduction. Full lifecycle (Day-0 to Day-N). | ECOC 2024 (PDP) |
| **AI-Light DT** (related PoliMi work) | Neural-network-enhanced GN model for real-time SNR prediction (0.3 dB RMSE). Pre-verified power re-equalization. | ECOC 2024 |
| **ETSI PoC** | AI agents for monitoring and automation in multi-vendor scenarios. Proof-of-concept at OFC 2026. | OFC 2026 |

- **Relevance to MultiAgentON**: The ECOC 2024 PoliMi pipeline is our **direct baseline** (see [[OrchestratorScriptReport]]). We extend their Planning→Execution→Error Handling pipeline into a full multi-agent architecture.
- **Key Difference**: Their system is a **single-agent, stateless script** using `llama_cpp` with GBNF grammars. No memory across turns, no multi-agent coordination, no HITL validation. Our architecture adds: (1) multi-agent specialization via LangGraph, (2) tri-partite hybrid memory, (3) formal HITL interrupt, (4) QoT-aware routing agent.
- **What We Can Reuse**: Their JSON schemas are already integrated into our Pydantic models. Their LoRA fine-tuning results inform our future model specialization strategy.

### 1.3 L4 Autonomous Optical Networks (Multi-AI-Agent)

| Work | Key Innovation | Venue |
|---|---|---|
| **AutoLight** (SJTU, Zhang, Qiu, Zhuge et al.) | Multi-AI-agent for L4 autonomy targeting distributed AI training. ~98% task completion (3.2× single-agent). Novel **Chain of Identity (CoI)** for inter-agent coordination. Built on **LangGraph**. Cross-domain management (440 km field-deployed backbone + DCI + intra-DC). | ECOC 2025 |
| **Expertise-Guided LLM Agent** (SJTU, Qiu, Zhuge et al.) | LLM agent with human expertise injection + Digital Twin for optical power optimization. 5.9 adjustments avg (5.8× fewer than Bayesian, 27.9× fewer than GA). | JOCN 2026 |
| **SJTU Invited Tutorial** (Zhang, Qiu, Zhuge et al.) | Comprehensive 20-page survey (225+ refs) of AI agents for AONs. Covers full agentic stack: domain adaptation, advanced prompting, RAG, hierarchical MAS, MCP, monitoring/DT/control toolsets. | JOCN 2026 (Invited) |

- **Detailed Analysis**: See [[AutoLight_ECOC2025]] for the field trial paper summary and [[SJTU_Invited_Tutorial_JOCN2026]] for the full tutorial summary.
- **Relevance to MultiAgentON**: These works from the SJTU group represent the **closest competitors** in the optical domain. They validate multi-agent LLM systems for optical network operations. The tutorial is the most authoritative survey on the topic. Critically, AutoLight is **built on LangGraph** — the same framework we use — independently validating our technology choice.
- **Key Difference**: AutoLight focuses on **operational lifecycle management** (resource allocation, wavelength establishment, failure management) across multiple domains. Our thesis targets **QoT-aware optical routing driven by natural language intent** with formal HITL validation. Their agents receive structured task definitions, not natural language intents. Their **Chain of Identity (CoI)** coordination technique (identity injection via ToolMessages) is novel but addresses a different problem than our hub-and-spoke Supervisor pattern — CoI handles identity coherence in semi-autonomous ReAct agents, while our Supervisor maintains full state centrally.
- **Critical Gap We Fill**: No SJTU work explicitly addresses the **intent-to-configuration translation** problem with HITL validation. Their agents receive structured inputs, not natural language intents. Our formal `interrupt()` protocol and reverse prompting pattern are novel contributions.

### 1.4 Intent-Based Networking with Security / Multi-Domain Focus

| Work | Key Innovation | Venue |
|---|---|---|
| **EU MARE Project** | Agentic AI for multi-domain security intents. Zero-Trust, MITRE ATT&CK integration, Security Plane concept with DOTs primitives. | Horizon Europe (2025–2027) |
| **IntentLLM / TeraFlowSDN** (Chalmers/CTTC) | LLM chatbot integrated into cloud-native SDN controller. Create/Find/Explain slice intents. | NetSoft 2024 |
| **IETF `draft-cgfabk-nmrg-ibn-generative-ai-02`** | Logical architecture for GenAI in IBN: Model Training & Specialization Function (MTSF), Model Repository (MRF), LoRA adapter fusion ("Flow"). | IETF NMRG 2025–2026 |

- **Relevance to MultiAgentON**: These works define the **normative and conceptual frameworks** for IBN+AI. The IETF draft is particularly important for positioning our work within the standards landscape.
- **Key Difference**: MARE focuses on security intents (not optical routing). IntentLLM is a chatbot interface (no multi-agent coordination, no QoT validation). The IETF draft is a framework specification (no implementation).
- **What We Can Reuse**: The IETF Model Hub / LoRA adapter fusion concept maps directly to our future model specialization roadmap. IntentLLM's "Create/Find/Explain" intent taxonomy can inform our Supervisor prompt design.

### 1.5 Edge Orchestration and Conflict Resolution

| Work | Key Innovation | Venue |
|---|---|---|
| **HearthNet** | Git-backed shared state, MQTT bus, actuation leases, Librarian-as-Observer for auditability. Edge multi-agent orchestration. | arXiv 2026 |
| **STEP Framework** (MADRL for O-RAN) | Multi-Agent Deep RL with information bottleneck for 6G O-RAN slicing. 6.06× inter-slice conflict reduction. | IEEE 2025 |

- **Relevance to MultiAgentON**: These works address the **conflict resolution** problem that we will inevitably face when our Routing Agent and (future) Compute Agent propose conflicting resource allocations.
- **Key Difference**: HearthNet is IoT/smart-home focused. STEP is RL-based (no LLM reasoning). Neither operates in the optical domain.
- **What We Can Reuse**: HearthNet's actuation lease mechanism is an elegant solution for preventing race conditions in RESTConf API calls — directly applicable to our Lightpath Agent. The STEP framework's information bottleneck approach could inform how we compress telemetry data for LLM consumption (addressing our $D_{sem} \le D_{max}$ constraint).

---

## 2. Comparative Feature Matrix

This matrix maps key capabilities across the SOTA and our MultiAgentON architecture.

| Feature | PoliMi ECOC'24 | Confucius (Meta) | AutoLight (SJTU) | IntentLLM (Chalmers) | MARE (EU) | **MultiAgentON (Ours)** |
|---|---|---|---|---|---|---|
| **Domain** | Optical (SDON) | IP/Datacenter | Optical | SDN Slicing | 6G Security | **Optical (SDON)** |
| **NL Intent Parsing** | ✅ (single-pass) | ✅ (DAG decomposition) | ❌ (structured input) | ✅ (chatbot) | ✅ (security intents) | **✅ ([[Concepts_and_Terminology|SLA matrix]] + task list)** |
| **Multi-Agent Architecture** | ❌ (single script) | ✅ (60+ apps) | ✅ (multi-agent) | ❌ (single chatbot) | ✅ (multi-domain) | **✅ (LangGraph hub-and-spoke)** |
| **QoT-Aware Routing** | ❌ | ❌ | ✅ (power optim.) | ❌ | ❌ | **✅ (GN model tool)** |
| **Compute Scheduling** | ❌ | ❌ | ❌ | ❌ | ❌ | **Future work** |
| **Joint Routing + Compute** | ❌ | ❌ | ❌ | ❌ | ❌ | **Future work** |
| **HITL Validation** | ❌ | ✅ (primitives) | ❌ | ❌ | ❌ | **✅ (interrupt() + GIGO prevention)** |
| **Hybrid Memory** | ❌ | ✅ (RAG) | ❌ (unclear) | ❌ | ❌ | **✅ (tri-partite: Wiki+Graph+RAG)** |
| **Digital Twin / Simulator** | ✅ (DT + GN) | ❌ | ✅ (DT) | ❌ | ✅ (PASTE DT) | **✅ (pure Python GN port)** |
| **Neurosymbolic Separation** | Partial (GBNF) | ❌ | Partial | ❌ | ❌ | **✅ (strict: LLMs reason, tools calculate)** |
| **Error Recovery Loop** | ✅ (re-prompt) | ✅ | ✅ | ❌ | ❌ | **✅ (conditional edges + RAG fallback)** |
| **Orchestration Framework** | None (raw scripts) | Custom DAG | **LangGraph** | TeraFlowSDN | Custom | **LangGraph** |
| **Real Testbed Validation** | ✅ (field trial) | ✅ (production) | ✅ (field trial) | ✅ (TeraFlow) | PoC | **Planned (RESTConf NBI)** |
| **Open Source / Reproducible** | Partial (schemas shared) | ❌ (proprietary) | ❌ | ✅ (TeraFlow) | ❌ | **✅ (full codebase)** |

---

## 3. Positioning: Where MultiAgentON Fits

### 3.1 The Gap We Fill

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

**No existing work combines ALL THREE**: (1) Natural language intent parsing with formal HITL, (2) QoT-aware optical routing with neurosymbolic separation, AND (3) a multi-agent LLM framework covering Day-0 through Day-N. This is our thesis's unique contribution. Compute scheduling is documented as **future work** (scope refinement).

### 3.2 Our Unique Selling Points (USPs)

1. **NL Intent Parsing with Formal HITL**: We are the first to implement NL → `sla_matrix` conversion with reverse prompting and a formal `interrupt()` protocol in the optical network domain. This addresses the "confidently wrong" problem (Confucius failure modes) and the HITL gap (SJTU acknowledges it as essential but lacks formal specification).
2. **Neurosymbolic Design Discipline**: While others use LLMs end-to-end (risking hallucinated physics), we enforce a strict "LLMs reason, tools calculate" separation. The QoT tool is a pure Python GN model, not an LLM approximation. Aligned with SJTU's recommended gray-box paradigm.
3. **Tri-Partite Hybrid Memory**: Our three-pillar memory (Wiki/Procedural + Graph/Semantic + RAG/Episodic) is architecturally more principled than the ad-hoc RAG used by Confucius or the memory-less PoliMi pipeline.
4. **Day-0 to Day-N Coverage**: Our approach covers the full lifecycle — from initial service provisioning to continuous optimization and failure response — not limited to Day-0 configuration or Day-1 operations.
5. **ECOC Baseline Bridge**: By building on top of the PoliMi pipeline's proven JSON schemas, we provide a clear lineage from validated industry work to our novel architecture.

---

## 4. Areas to Avoid (Saturated / Out of Scope)

Based on the SOTA analysis, the following areas are either well-covered or tangential to our thesis:

| Area | Reason to Avoid | Who Owns It |
|---|---|---|
| **LoRA Fine-Tuning for Optical** | Thoroughly validated by PoliMi (100% accuracy). We should USE their results, not replicate them. | PoliMi / EURECOM |
| **Security / Zero-Trust** | Deep specialization required. MARE has 3 years of EU funding. | EU MARE Project |
| **MADRL for Conflict Resolution** | RL-based approach is orthogonal to LLM-based reasoning. Requires different methodology. | STEP Framework |
| **Production-Scale Deployment** | Confucius has 2+ years of Meta production. We cannot compete on scale. | Meta |
| **GNPy Development** | Mature open-source tool. We should integrate, not reinvent. | Telecom Infra Project |
| **Multi-band (C+L+S) Physics** | Hardware-specific, needs lab access beyond our testbed. | NEC Labs / PoliTo |

---

## 5. Opportunities to Leverage from Existing Work

| Opportunity | Source | How to Apply |
|---|---|---|
| **GBNF/Grammar Constrained Generation** | PoliMi ECOC'24 | Consider adding schema-level validation beyond Pydantic. Could improve reliability of LLM outputs for RESTConf payloads. |
| **Hibernate-and-Wake Pattern** | Confucius (Meta) | Implement for long-running testbed operations. Map to LangGraph's checkpointer + async patterns. |
| **Actuation Leases** | HearthNet | Apply to RESTConf write operations. Before provisioning, acquire a "lease" that validates state freshness and prevents stale writes. |
| **AutoONBench Evaluation** | SJTU | Use their 5-category evaluation framework (service mgmt, maintenance, failure handling, physical-layer, optimization) to evaluate MultiAgentON. |
| **IETF Model Hub Concept** | `draft-cgfabk-nmrg-ibn-generative-ai` | Frame our future model specialization strategy within the IETF's MTSF/MRF/MFCF architecture. Provides academic legitimacy. |
| **Topology Chunking for GraphRAG** | TD Commons / Neo4j research | When implementing Pillar 2 (KG), use topology-aware chunking instead of naive text chunking for RAG over network state. |

---

## 6. Critical Analysis: Strengths and Weaknesses of Our Approach

### 6.1 Strengths

| Strength | Evidence |
|---|---|
| **Architecturally novel scope** | No prior work addresses joint routing + compute scheduling with agentic AI in optical networks. |
| **Principled neurosymbolic design** | The "LLMs reason, tools calculate" separation is increasingly recognized as the correct approach (see SJTU expertise-guided agent, PoliMi GBNF). |
| **Framework maturity** | LangGraph is the most widely adopted stateful agent framework (2024–2026). Our choice aligns with industry direction. |
| **Reproducibility** | Full open-source codebase with Strict TDD. Most SOTA works are proprietary. |
| **HITL formalization** | `interrupt()` + GIGO prevention is a concrete engineering contribution, not just a design principle. |

### 6.2 Weaknesses to Address

| Weakness | Mitigation Strategy |
|---|---|
| **No field-trial validation yet** | Priority: Experiment 002 (Routing + QoT) on mock testbed. Goal: establish quantitative baselines before real testbed access. |
| **Compute scheduling deferred** | Documented as future work (scope refinement). Thesis focuses on routing + QoT + HITL. |
| **Single LLM provider (Kimi)** | Provider-agnostic via LangChain. Run experiments with multiple backends to demonstrate portability. |
| **No benchmark comparison** | Adopt AutoONBench's 5-category evaluation. Create comparable metrics. |
| **Memory Pillar 2 (KG) is still Pydantic-only** | Acceptable for MVP. Document the graduation path to Neo4j/Memgraph. |

---

## 7. Key References (Organized by Relevance)

### Tier 1: Must-Cite (Directly Relevant)

1. **Wang et al.** "Intent-Driven Network Management with Multi-Agent LLMs: The Confucius Framework." ACM SIGCOMM 2025.
2. **Di Cicco, Tornatore et al.** "First Experimental Demonstration of Full Lifecycle Automation of Optical Network through Fine-Tuned LLM and Digital Twin." ECOC 2024 (PDP).
3. **Di Cicco et al.** "Open Implementation of a Large Language Model Pipeline for Automated Configuration of Software-Defined Optical Networks." ECOC 2024.
4. **Zhang, Qiu, Zhuge et al.** "Field-trial demonstration of L4 autonomous optical network managed by multi-AI-agent system." ECOC 2025.
5. **Qiu, Zhuge et al.** "Expertise-guided LLM agent for autonomous optical power optimization in field-deployed optical networks." JOCN, Vol. 18(5), 2026.
6. **Zhuge et al.** "AI agent for autonomous optical networks: architectures, technologies, and prospects." JOCN, Vol. 18(2), 2026 (Invited Tutorial).
7. **Wu et al.** "AutoONBench: a benchmark for large language model agents in autonomous optical networks." JOCN, Vol. 18(9), 2026.
8. **IETF.** "draft-cgfabk-nmrg-ibn-generative-ai-02: Generative AI for Intent-Based Networking." NMRG, 2026.

### Tier 2: Should-Cite (Conceptual Foundations)

9. **Rafique et al.** "Telemetry and Agentic AI: Foundations for Optical Network Automation." IEEE Access, 2025.
10. **Paolucci et al.** "Enhancing Secure Intent-Based Networking with an Agentic AI: The EU Project MARE Approach." arXiv:2604.06856, 2026.
11. **IntentLLM authors (Chalmers/CTTC).** "IntentLLM: An AI Chatbot to Create, Find, and Explain Slice Intents in TeraFlowSDN." NetSoft 2024.
12. **HearthNet authors.** "HearthNet: Edge Multi-Agent Orchestration for Smart Homes." arXiv:2604.09618, 2026.
13. **ORCH authors.** "ORCH: many analyses, one merge — a deterministic multi-agent orchestrator for discrete-choice reasoning." Frontiers in AI, 2026.

### Tier 3: Contextual (Broader SOTA)

14. **Agentic AI Empowered IBN for 6G.** arXiv:2601.06640, 2026.
15. **Multi-Agent Collaboration Mechanisms Survey.** arXiv:2501.06322, 2025.
16. **ITU-T GSTR-ION-2030.** "Technical report on international optical networks towards 2030 and beyond." 2025.
17. **LLM Agent Memory Survey.** Preprints.org 202603.0359, 2026.

---

## 8. Cross-References

- [[Architecture_v2]] — Our unified system design
- [[ProblemStatement_20260427_Felipe_Abadia]] — Thesis problem definition
- [[OrchestratorScriptReport]] — Analysis of the ECOC 2024 baseline codebase
- [[QoT_Awareness]] — QoT concept documentation
- [[Concepts_and_Terminology]] — Glossary of terms
- [[literature/recommendations]] — Follow-up research recommendations
- [[Confucius_SIGCOMM2025]] — Detailed Confucius paper analysis
- [[SJTU_Invited_Tutorial_JOCN2026]] — Detailed SJTU tutorial analysis
- [[sota_gap_analysis]] — Gap analysis with updated positioning
