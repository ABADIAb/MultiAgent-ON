---
title: "Literature: AutoLight — First Field-Trial Demonstration of L4 Autonomous Optical Network for Distributed AI Training (SJTU, ECOC 2025)"
date: 2026-06-21
tags: [literature, autolight, multi-agent, optical-networks, field-trial, sjtu, ecoc, langgraph, l4-autonomy]
status: active
---

# AutoLight: First Field-Trial Demonstration of L4 Autonomous Optical Network for Distributed AI Training Communication

**Authors:** Yihao Zhang, Qizhi Qiu, Xiaomin Liu, Dianxuan Fu, Xingyu Liu, Leyan Fei, Yuming Cheng, Lilin Yi, Weisheng Hu, Qunbi Zhuge
**Venue:** ECOC 2025 (European Conference on Optical Communication)
**Affiliation:** Shanghai Jiao Tong University (SJTU), State Key Laboratory of Photonics and Communications
**Open source:** https://github.com/AutoLight2025/AutoLight

---

## Summary

This paper presents the **first field-trial demonstration** of a Level-4 (L4) autonomous optical network, realized through AutoLight — an LLM-powered hierarchical multi-agent system. The demonstration targets the **distributed AI training communication lifecycle**: computing resource assessment, physical/network-layer resource allocation, cross-domain wavelength establishment, and proactive failure management. AutoLight achieves a **~98% task completion rate** across 40 trials (10 per task), representing a **~3.2× improvement** over single-agent approaches using advanced LLMs on identical tasks.

---

## Core Contributions

### 1. Chain of Identity (CoI) — Novel Inter-Agent Coordination Technique

The paper's primary technical contribution is **Chain of Identity (CoI)**, a three-mechanism technique for maintaining identity coherence across multi-agent interactions:

1. **Formatted handoffs:** Agents use structured text for inter-agent transfers — greeting identifying the target agent, a query, and a parameter section with essential arguments.
2. **Pseudo-SystemMessage injection:** Handoff transfers embed system-level instructions within `ToolMessages`, containing the identity and core responsibility of the target agent.
3. **Pre-execution declaration:** Before any action, agents issue an identity declaration and verify received `ToolMessage` content against handoffs and pseudo-SystemMessages.

**Why CoI matters:** Without CoI, "naive multi-agent" systems suffer **identity confusion** — agents lose track of their role after transfers, causing unexpected terminations. CoI ensures continuous identity awareness and contextual consistency.

### 2. Hierarchical Multi-Agent Architecture

AutoLight uses a **hierarchical** structure with two agent categories:

- **Planner agents:** High-level coordinators for problem decomposition and execution orchestration. Maintain a **plan tracking table** to record task progress and prevent anomalous task termination. Equipped with minimal toolsets for basic operations.
- **Task agents:** Specialized executors with comprehensive toolkits for specific functions — resource allocation, digital twin operations, failure handling.
- **Knowledge Retriever:** A specialized Task agent using RAG to access external documents and ensure operation reliability.

All agents are **ReAct agents** [Yao et al., ICLR 2023] powered by LLMs with tool access.

### 3. Framework: Built on LangGraph

AutoLight is explicitly **developed based on LangGraph** [Fig. 2 caption]. This is a significant alignment with our [[Architecture_v2]] choice.

---

## Experimental Setup

### Testbed Architecture (Cross-Domain, Cross-Layer)

The demonstration uses an integrated validation platform emulating a geo-distributed data center cluster:

| Domain | Infrastructure | Scale |
|:---|:---|:---|
| **Backbone** | 440 km field-deployed link (Shanghai → Hangzhou), 4 spans, G.652D fiber, C-band EDFAs, 30-wavelength transmission (6× 400/200 Gbps transponders + ASE dummy), 63.9 GBaud | Physical hardware |
| **DCI Metro** | 14-node topology [NSFNet-derived] | Emulated via OMNeT++ |
| **Intra-Datacenter** | 8 server groups × 8 servers, two-tier spine-leaf architecture | Emulated via OMNeT++ |

- **Hardware control:** NETCONF protocol with YANG models (backbone).
- **Simulation control:** Socket-based interface to OMNeT++ (metro/DC).
- **Physical-layer impairments:** IMDD system with 53 Gbps PAM-4 + multipath interference (MPI) via delayed reflection path.
- **Two isolated domains:** Information isolation between backbone domains — agents must coordinate without shared state.

### Evaluated Tasks (Distributed AI Training Lifecycle)

| Task | Description | Layer |
|:---|:---|:---|
| **Task 1** — Real-time resource allocation | DCI conducts resource allocation during distributed training at each epoch | Network |
| **Task 2** — Backbone wavelength establishment | Backbone network establishes inter-DCI transmission with new wavelengths | Physical |
| **Task 3** — DCI failure management | Detection and mitigation of physical-layer failures in DCI metro | Physical + Network |
| **Task 4** — Backbone failure management | Coordinated troubleshooting across two information-isolated backbone domains | Physical + Network |

### Results

| System | Avg. Completion Rate | Notes |
|:---|:---|:---|
| **AutoLight (w/ GPT-4o)** | **~98%** | Hierarchical MAS with CoI |
| Single agent (GPT-4o) | ~30% | Overwhelmed by cross-domain complexity |
| Single agent (other LLMs) | ~30% | Similar failure regardless of LLM |
| Naive multi-agent (no CoI) | Low (partial checkpoints) | Identity confusion → unexpected terminations |

**Key failure modes of baselines:**
- Single agents become **disoriented** when managing tools and information for all domains simultaneously.
- Single agents may **terminate unexpectedly** after generating lengthy outputs or performing numerous operations.
- Naive multi-agent without CoI suffers **identity confusion** after transfers — agents lose their role context.

---

## Relevance to MultiAgentON

| Aspect | AutoLight (ECOC 2025) | MultiAgentON |
|:---|:---|:---|
| **Framework** | LangGraph | LangGraph |
| **Agent pattern** | Hierarchical (Planner + Task agents, ReAct) | Hub-and-spoke (Supervisor + specialized nodes) |
| **Coordination** | Chain of Identity (CoI) via ToolMessages | Direct state sharing via `AgentState` |
| **Domain** | Cross-domain (backbone + DCI + DC) | Single-domain optical routing (SDON testbed) |
| **Input** | Structured tasks (no NL intent parsing) | Natural language → `sla_matrix` |
| **HITL** | Not implemented | Formal `interrupt()` protocol |
| **QoT validation** | Not the focus (failure mgmt + resource allocation) | [[QoT_Awareness\|Neurosymbolic GN model]] core |
| **Control protocol** | NETCONF/YANG | RESTConf |
| **Testbed scale** | 440 km field-deployed + OMNeT++ emulated | Laboratory SDON testbed |
| **LLM** | GPT-4o | Kimi (OpenAI-compatible) |

### Key Takeaways for Our Work

1. **LangGraph validation:** AutoLight's explicit use of LangGraph independently validates our framework choice. Both the most cited SOTA systems in optical networking (AutoLight) and IP networking (Confucius, which uses LangChain) converge on the LangGraph/LangChain ecosystem.

2. **CoI vs our Supervisor pattern:** AutoLight uses CoI (identity injection via ToolMessages) because their agents are semi-autonomous ReAct agents that need to maintain identity across hand-offs. Our hub-and-spoke Supervisor pattern avoids this problem entirely — all agents return to the Supervisor, which maintains full state. Our pattern is simpler but potentially less scalable for cross-domain scenarios.

3. **No NL intent parsing, no HITL:** This paper **confirms** our gap analysis — AutoLight receives structured task definitions, not natural language intents. There is no formal operator validation before network-modifying actions. Our NL → `sla_matrix` pipeline and `interrupt()` protocol remain **novel contributions** not addressed by this work.

4. **Plan tracking table:** AutoLight's Planner agents maintain a plan tracking table to prevent anomalous task termination. This is functionally similar to our `AgentState.task_list` — an ordered delegation plan tracked by the Supervisor. We could adopt their explicit "checkpoint tracking" mechanism to improve robustness.

5. **RAG for reliability:** AutoLight uses a dedicated Knowledge Retriever agent with RAG for operation reliability — aligning with our Pillar 3 (Vector RAG / Episodic Memory) design, even though both systems defer full RAG implementation to later stages.

6. **Scope difference is our positioning advantage:** AutoLight solves **operational lifecycle management** (resource allocation, failure handling) across multiple domains. We solve **intent-driven QoT-aware routing** with HITL safety in a single optical domain. These are complementary, not competing contributions.

---

## What Needs Updating in Our Wiki

After ingesting this paper, the following corrections and additions were identified in our existing wiki files:

1. **Orchestration framework:** AutoLight uses LangGraph, not a "Custom" framework as previously listed in [[lit_comparison]].
2. **Chain of Identity (CoI):** This novel technique was not documented. It should be referenced in our comparison as a coordination mechanism.
3. **HITL status for AutoLight:** Our feature matrix correctly marks AutoLight as ❌ for formal HITL — confirmed by the paper (no HITL mechanism is described).
4. **NL Intent Parsing:** Our feature matrix correctly marks AutoLight as ❌ — confirmed by the paper (tasks are predefined structured inputs).

---

## Citation

```bibtex
@inproceedings{zhang2025autolight,
  title={First Field-Trial Demonstration of L4 Autonomous Optical Network for Distributed AI Training Communication: An LLM-Powered Multi-AI-Agent Solution},
  author={Zhang, Yihao and Qiu, Qizhi and Liu, Xiaomin and Fu, Dianxuan and Liu, Xingyu and Fei, Leyan and Cheng, Yuming and Yi, Lilin and Hu, Weisheng and Zhuge, Qunbi},
  booktitle={European Conference on Optical Communication (ECOC)},
  year={2025},
  note={©2025 The Author(s)}
}
```

---

## Cross-References

- [[SJTU_Invited_Tutorial_JOCN2026]] — Comprehensive tutorial from the same group (survey, not field trial)
- [[lit_comparison]] — Systematic SOTA comparison
- [[sota_gap_analysis]] — Gap analysis positioning
- [[Architecture_v2]] — Our unified system design
- [[QoT_Awareness]] — QoT concept documentation
