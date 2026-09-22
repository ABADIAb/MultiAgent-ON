---
title: "Chapter 4 - Section 4.2: Network Context and Subtopology Extraction"
date: 2026-09-21
tags: [thesis, chapter-4, implementation, graphrag, testbed, orchestration, network-context]
status: active
---

# 4.2 Network Context and Subtopology Extraction

## 4.2.1 Optical Network Abstraction and Physical Testbed Modeling

The translation of high-level operator intent into operational lightpaths requires a faithful software representation of the underlying optical transport infrastructure. In our neurosymbolic architecture, physical network state ingestion is decoupled from generative model execution and encapsulated within dedicated service adapters and domain models.

The optical topology is abstracted as an undirected graph $G(V, E)$ populated by two data structures:

1. **Network Nodes ($V$):** Represented by the `NetworkNode` model, each network element corresponds to a Reconfigurable Optical Add-Drop Multiplexer (ROADM) or optical cross-connect (OXC) hub.
2. **Fiber Links ($E$):** Encapsulated by the `FiberLink` model, each edge represents an optical fiber transmission line connecting node pairs. To ensure physical fidelity during downstream Quality of Transmission (QoT) estimation, each link record stores structural and physical attributes, including the total span length in kilometers, the count of optical amplifiers, active WDM channels, port insertion loss, and the ordered chain of Erbium-Doped Fiber Amplifiers (EDFAs).

To establish an experimentally reproducible evaluation baseline, the primary topology utilized throughout this work is a simulated version of the **Nobel-Germany optical backbone network** sourced from SNDlib \cite{orlowski_sndlib_2010}. The topology comprises 17 core ROADM switching nodes and 26 bidirectional physical fiber links interconnecting Germany's primary telecommunications hubs. Physical network access is unified behind an abstract client interface, which provides a static memory-backed topology for continuous benchmarking.

---

## 4.2.2 Scoped Subtopology Extraction via Mock GraphRAG

Modern optical transport controllers represent network state using standard YANG data models serialized into extensive JSON or XML structures via RESTConf or NETCONF protocols. Raw RESTConf JSON payloads can grow exponentially with network scale, easily exceeding standard context limits. Injecting full network configuration payloads directly into the context window of an LLM exhausts token budgets, triggers attention degradation, and inflates inference latency. 

To mitigate token saturation without sacrificing topological awareness, the pipeline implements a localized subtopology extraction layer termed **Mock GraphRAG**.

When an operator intent specifies a communication request between an origin node $s$ and a destination node $d$, the system scopes the context using $k$-hop neighborhood extraction. The relevant subtopology node set $V_{sub}$ is the union of the $k$-hop neighborhoods centered on the source and target endpoints. By default, the radius is configured to $k = 2$, bounding the candidate vertex set to the immediate switching neighborhood and discarding irrelevant peripheral links.

To provide the language model with topological context while limiting prompt size, the subgraph is serialized into plain text. This keeps the prompt within the token bound $T_{prompt}(\mathcal{I}_{NL}, G_{sub}) \le T_{max} \ll T_{full}(G)$ from Equation~\eqref{eq:token_budget}, avoiding attention loss while preserving link lengths, amplifier counts, and node identifiers.

Once the topological context is extracted and bounded, the orchestrator passes control to Phase 2. Section~\ref{sec:semantic_engine} details the Semantic Engine, describing how raw natural language intents are ingested, parsed into AST-verified PDDL, and audited via automated Reverse Prompting.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Subtopology Scoping:** The plain text serialization format preserves all physical parameters required by downstream GN-model physics calculations without inflating prompt token counts.

