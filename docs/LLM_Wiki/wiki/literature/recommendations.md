---
title: "Research Recommendations: Next Steps for MultiAgentON SOTA Analysis"
date: 2026-06-04
tags: [literature, recommendations, research, next-steps, thesis]
status: active
---

# Research Recommendations for MultiAgentON Thesis

This document lists actionable research directions, follow-up investigations, and strategic recommendations based on the findings from [[literature/lit_comparison|lit_comparison.md]]. These are ordered by priority for the thesis.

---

## Priority 1: Immediate Actions (This Week / Next Week)

### 1.1 Read the Full Confucius Paper (SIGCOMM 2025)

- **Paper**: Wang et al., "Intent-Driven Network Management with Multi-Agent LLMs: The Confucius Framework."
- **Access**: https://minlanyu.seas.harvard.edu/writeup/sigcomm25.pdf
- **Why**: This is the single most important reference for our architecture. We need to understand their DAG decomposition, hibernate-and-wake mechanism, and RAG integration in detail. Our Related Work section MUST clearly articulate the delta between Confucius (IP/datacenter) and MultiAgentON (optical + [[ProblemStatement_20260427_Felipe_Abadia|joint routing/compute]]).
- **Action**: Ingest into `raw/`, create wiki note, map design decisions to our [[Architecture_v2]].

### 1.2 Read the SJTU Invited Tutorial (JOCN 2026)

- **Paper**: Zhuge et al., "AI agent for autonomous optical networks: architectures, technologies, and prospects." JOCN, Vol. 18(2), A159.
- **Access**: https://opg.optica.org/jocn/abstract.cfm?URI=jocn-18-2-A159
- **Why**: This is the authoritative survey from the group producing the most relevant competing work (AutoLight, Expertise-Guided Agent). Reading it will reveal their full research roadmap and help us position against them precisely.
- **Action**: Ingest into `raw/`, create wiki note with detailed comparison points.

### 1.3 Prepare the SOTA Comparison Slides for Prof. Zhang

- **Why**: This was requested in the weekly report (Goal 1) and has been deferred twice.
- **Format**: Create a presentation in `docs/LLM_Wiki/wiki/presentations/` using the [[literature/lit_comparison]] as the data source.
- **Content**: Feature matrix table, positioning diagram, and 3 key differentiators. Keep it under 10 slides.

---

## Priority 2: Medium-Term Research (Next 2–4 Weeks)

### 2.1 Investigate the Compute Scheduling Dimension

- **Problem**: Our thesis title includes "compute scheduling" but the current architecture focuses on routing. This is both a risk and our biggest opportunity.
- **Research Questions**:
  1. What does "compute scheduling" mean concretely in the optical network context? Edge compute node selection? GPU/VRAM allocation? Service function chain placement?
  2. Are there existing works on LLM-based compute resource allocation in transport networks?
  3. How do we model the compute node as a vertex with capacity constraints in $G(V,E)$?
- **Suggested Search Terms**: "compute-aware optical networking", "joint RWA and compute allocation", "service function chaining optical network", "computing-communication integrated network", "edge compute placement SDN optical"
- **Action**: Conduct a focused sub-literature review on this topic. This may require a separate wiki note: `wiki/literature/compute_scheduling_review.md`.

### 2.2 Study the AutoONBench Evaluation Methodology

- **Paper**: Wu et al., "AutoONBench: a benchmark for large language model agents in autonomous optical networks." JOCN, Vol. 18(9), 2026.
- **Access**: https://opg.optica.org/jocn/abstract.cfm?uri=jocn-18-9-D1
- **Why**: We need a rigorous evaluation framework. AutoONBench provides the first standardized benchmark for LLM agents in optical networks. Even if we can't run their exact benchmark, adopting their evaluation categories (service mgmt, maintenance, failure handling, physical-layer, optimization) gives our results academic credibility.
- **Action**: Read the paper, extract evaluation metrics, map them to our experiment design.

### 2.3 Explore the IETF IBN+GenAI Framework in Depth

- **Document**: `draft-cgfabk-nmrg-ibn-generative-ai-02`
- **Access**: https://datatracker.ietf.org/doc/draft-cgfabk-nmrg-ibn-generative-ai/
- **Why**: Positioning our work within an IETF standardization effort dramatically increases its relevance. The MTSF/MRF/MFCF concepts can frame our Supervisor as an "Intent Transformer" and our agents as domain-specific "LoRA adapters" (conceptually, even if we don't fine-tune).
- **Action**: Read the draft, create a wiki note mapping our components to their logical architecture.

---

## Priority 3: Strategic Research Directions (Thesis Lifetime)

### 3.1 Formalize the Neurosymbolic Separation

- **Opportunity**: The "LLMs reason, tools calculate" principle is mentioned across the SOTA but never formally defined with rigor. We can contribute a **formal framework** for neurosymbolic task decomposition in optical networks.
- **Concrete Contribution**: Define a taxonomy of decision points: which decisions are "symbolic" (deterministic, tool-delegated: SNR calculation, spectrum assignment, graph pathfinding) vs. "neural" (stochastic, LLM-delegated: intent parsing, anomaly interpretation, workflow planning).
- **Academic Value**: This directly addresses the "confidently wrong" research gap flagged by multiple SOTA works.

### 3.2 Design the Compute Agent Architecture

- **Opportunity**: This is the CORE differentiator. No existing work combines optical routing + compute scheduling in a multi-agent LLM framework.
- **Suggested Architecture**:
  1. **Compute Agent** as a new LangGraph node, peers with Routing Agent.
  2. Receives the parsed [[Concepts_and_Terminology|SLA]] constraints (compute requirements: FLOPs, VRAM, latency).
  3. Queries a compute resource inventory (edge servers, their locations in the topology, available GPU capacity).
  4. Proposes compute node $c^*$, which is then fed to the Routing Agent as a destination constraint.
  5. **Conflict Resolution**: If the QoT-optimal route doesn't reach the compute-optimal server, the Supervisor mediates a negotiation loop.
- **Related Work to Read**: "Computing-Communication Integrated Networks" literature, SFC placement in optical networks.

### 3.3 Topology-Aware Memory (GraphRAG for Optical)

- **Opportunity**: The transition from Pydantic-based state (current MVP) to a proper Knowledge Graph is architecturally planned but not designed.
- **Research Direction**: Apply the "Topology Chunking" technique from the TD Commons paper to our SDON testbed topology. This would allow the Routing Agent to perform multi-hop reasoning over the physical network graph.
- **Technical Path**: Neo4j or Memgraph with Cypher queries, exposed as a LangGraph tool. The topology chunks would be embedded for semantic search (Pillar 3 integration).

### 3.4 Benchmark Against AutoONBench Categories

- **Action**: Once Experiment 002 (Routing + QoT) is complete, map results to AutoONBench's 5 evaluation categories.
- **Metrics to Report**: Task completion rate, number of LLM calls per task, total tokens consumed, end-to-end latency, QoT validation accuracy.

---

## Priority 4: Things to Monitor (Not Investigate Deeply)

These are active research areas worth tracking but not worth deep investigation for the thesis:

| Topic | Why Monitor | Where to Track |
|---|---|---|
| **MCP (Model Context Protocol) Evolution** | May become the standard agent-to-tool interface. Could replace our custom tool binding. | IETF / Anthropic specs |
| **A2A (Agent-to-Agent) Protocol** | If standardized, could define how our agents communicate. Currently too nascent. | Google DeepMind / IETF |
| **GNPy Multiband Extensions** | Only relevant if our testbed supports C+L+S. Currently C-band only. | TIP / GNPy GitHub |
| **Optical Computing / Photonic AI** | Fascinating long-term direction but 5+ years out. Not thesis-relevant. | Nature Photonics |

---

## Summary of Recommended Reading List

| # | Paper / Document | Priority | Purpose |
|---|---|---|---|
| 1 | Confucius (SIGCOMM 2025) | 🔴 Immediate | Primary competitor, architectural reference |
| 2 | SJTU Invited Tutorial (JOCN 2026) | 🔴 Immediate | Optical SOTA survey from key competitor |
| 3 | ECOC 2024 PDP (PoliMi) | ✅ Done | Already analyzed in [[OrchestratorScriptReport]] |
| 4 | AutoONBench (JOCN 2026) | 🟡 Medium | Evaluation methodology |
| 5 | IETF IBN+GenAI draft | 🟡 Medium | Standards positioning |
| 6 | AutoLight (ECOC 2025) | 🟡 Medium | L4 autonomy comparison |
| 7 | Expertise-Guided Agent (JOCN 2026) | 🟡 Medium | DT+LLM pattern |
| 8 | EU MARE (arXiv 2026) | 🟢 Low | Security context only |
| 9 | HearthNet (arXiv 2026) | 🟢 Low | Conflict resolution patterns |
| 10 | STEP Framework (IEEE 2025) | 🟢 Low | RL-based alternative |

---

## Cross-References

- [[literature/lit_comparison]] — Detailed SOTA comparison
- [[Architecture_v2]] — Our unified system design
- [[ProblemStatement_20260427_Felipe_Abadia]] — Thesis problem definition
- [[experiments/Experiment_001_Topology_Query_MVP]] — Completed experiment
