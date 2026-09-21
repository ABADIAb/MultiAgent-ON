---
title: "Chapter 4 - Section 4.2: Network Context and Subtopology Extraction"
date: 2026-09-21
tags: [thesis, chapter-4, implementation, graphrag, testbed, orchestration, network-context]
status: active
---

# 4.2 Network Context and Subtopology Extraction

## 4.2.1 Optical Network Abstraction and Physical Testbed Modeling

The translation of high-level operator intent into operational lightpaths requires a faithful software representation of the underlying optical transport infrastructure. In our neurosymbolic architecture, physical network state ingestion is decoupled from generative model execution and encapsulated within dedicated service adapters and domain models implemented in `src/services/testbed_client.py` and `src/core/state.py`.

The optical topology is abstracted as an undirected graph $G(V, E)$ populated by two fundamental data structures:

1. **Network Nodes ($V$):** Represented by the `NetworkNode` model, each network element corresponds to a Reconfigurable Optical Add-Drop Multiplexer (ROADM) or optical cross-connect (OXC) hub.
2. **Fiber Links ($E$):** Encapsulated by the `FiberLink` model, each edge represents an optical fiber transmission line connecting node pairs. To ensure physical fidelity during downstream Quality of Transmission (QoT) estimation, each link record stores structural and physical attributes, including the total span length in kilometers, the count of optical amplifiers, active WDM channels, port insertion loss, and the ordered chain of Erbium-Doped Fiber Amplifiers (EDFAs).

To establish an experimentally reproducible evaluation baseline matching carrier-grade transport networks, the primary topology utilized throughout this work is the **Nobel-Germany optical backbone network** sourced from SNDlib \cite{orlowski_sndlib_2010}. The topology comprises 17 core ROADM switching nodes and 26 bidirectional physical fiber links interconnecting Germany's primary telecommunications hubs.

Physical network access is unified behind an abstract client interface, which provides implementations for both a static memory-backed topology for continuous benchmarking and a production-grade RESTConf adapter connecting to physical optical hardware via the SM Optics Optical Network Controller (ONC).

---

## 4.2.2 Scoped Subtopology Extraction via Mock GraphRAG

Modern optical transport controllers represent network state using standard YANG data models serialized into extensive JSON or XML structures via RESTConf or NETCONF protocols. A comprehensive payload capturing a 17-node optical backbone frequently spans between 15,000 and 35,000 tokens.

Injecting full network configuration payloads directly into the context window of an LLM exhausts token budgets, triggers attention degradation, and inflates inference latency. Bounding the context size before invoking the linguistic reasoning engine is an absolute architectural invariant.

To overcome token saturation without sacrificing topological awareness, the pipeline implements a localized subtopology extraction layer termed **Mock GraphRAG**, located in `src/core/mock_graphrag.py`. 

When an operator intent specifies a communication request between an origin node $s$ and a destination node $d$, the system scopes the context using $k$-hop neighborhood extraction. The relevant subtopology node set $V_{sub}$ is the union of the $k$-hop neighborhoods centered on the source and target endpoints. By default, the radius is configured to $k = 2$, bounding the candidate vertex set to the immediate switching neighborhood and discarding irrelevant peripheral links.

To inject the extracted subtopology into the LLM system prompt with maximum token density, the subgraph is serialized into a structured plain text schema. Compared to a raw RESTConf JSON payload exceeding 15,000 tokens, the serialized scoped context string consumes fewer than **350 tokens**—representing a $>97\%$ reduction in prompt token consumption while retaining complete physical transparency over link lengths, amplifier counts, and topological identifiers.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 4.2 Placement:** Architectural diagram illustrating the Optical Network Abstraction and GraphRAG extraction pipeline.
> - **Artifact Path:** `figs_NPImp/src/diagrams/graphrag_subtopology_extraction.drawio`
> - **LaTeX Figure Reference:** `Figure~\ref{fig:graphrag_subtopology_extraction}`
