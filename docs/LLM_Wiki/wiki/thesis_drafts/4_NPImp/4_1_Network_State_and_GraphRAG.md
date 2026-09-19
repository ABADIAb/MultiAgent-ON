---
title: "Chapter 4 - Section 4.1: Network State and Knowledge Graph (GraphRAG)"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, graphrag, testbed, nobel-germany, restconf, token-budget]
status: draft
---

# 4.1 Network State and Knowledge Graph (GraphRAG)

## 4.1.1 Optical Network Abstraction and Physical Testbed Modeling

The translation of high-level operator intent into operational lightpaths requires a faithful software representation of the underlying optical transport infrastructure. In our neurosymbolic architecture, physical network state ingestion is decoupled from generative model execution and encapsulated within dedicated service adapters and domain models implemented in `src/services/testbed_client.py` and `src/core/state.py`.

The optical topology is abstracted as an undirected graph $G(V, E)$ populated by two fundamental data structures:

1. **Network Nodes ($V$):** Represented by the `NetworkNode` model, each network element corresponds to a Reconfigurable Optical Add-Drop Multiplexer (ROADM) or optical cross-connect (OXC) hub. A node is parameterized by an invariant identifier (`node_id`), a human-readable geographic label (`name`), and a list of physical port interfaces (`interfaces`):
   $$v_i = \left( \text{id}_i, \text{label}_i, \mathcal{I}_i \right), \quad v_i \in V$$
2. **Fiber Links ($E$):** Encapsulated by the `FiberLink` model, each edge represents an optical fiber transmission line connecting node pairs. To ensure physical fidelity during downstream Quality of Transmission (QoT) estimation, each link record stores structural and physical attributes:
   $$e_{ij} = \left( \text{link\_id}, v_i, v_j, L_{ij}, M_{ij}, N_{ch}, A_{port}, \mathcal{A}_{ij} \right)$$
   where $L_{ij} \in \mathbb{R}^+$ denotes the total span length in kilometers, $M_{ij} \in \mathbb{N}$ is the count of optical amplifiers deployed along the link, $N_{ch} \in \mathbb{N}$ denotes the active WDM channel count, $A_{port}$ is the optical port insertion loss (configured to $0.5\text{ dB}$), and $\mathcal{A}_{ij}$ specifies the ordered chain of Erbium-Doped Fiber Amplifiers (EDFAs).

To establish an experimentally reproducible evaluation baseline matching carrier-grade transport networks, the primary topology utilized throughout this work is the **Nobel-Germany optical backbone network** sourced from SNDlib \cite{orlowski_sndlib_2010}. The topology comprises $|V| = 17$ core ROADM switching nodes and $|E| = 26$ bidirectional physical fiber links (yielding 52 directed optical spans), interconnecting Germany's primary telecommunications hubs: Hannover, Frankfurt, Hamburg, Norden, Bremen, Berlin, Munich, Ulm, Nuremberg, Stuttgart, Karlsruhe, Mannheim, Essen, Dortmund, Dusseldorf, Cologne, and Leipzig. Link physical lengths range from short regional spans such as Essen--Dusseldorf ($37.5\text{ km}$) to long-haul inter-city trunks including Frankfurt--Leipzig ($381.9\text{ km}$) and Hannover--Frankfurt ($341.2\text{ km}$).

```
                                [Norden]
                               /        \
                    156.5 km  /          \  303.0 km
                             /            \
                     [Bremen]              [Dortmund] --- 44.4 km --- [Essen]
                    /    |   \            /    |                     |
          129.7 km /     |    \ 132.7 km /     | 95.3 km             | 37.5 km
                  /      |     \        /      |                     |
          [Hamburg]      |     [Hannover]      [Cologne]             [Dusseldorf]
                  \      |     /   |    \      /      \              /
          330.9 km \     |    /    |     \    /        \ 48.1 km    /
                    \    |   /     |      \  / 188.9 km \__________/
                     [Berlin]      |     [Frankfurt]
                         \         |     /    |     \
                 196.7 km \   275.8 km  /     |      \  246.8 km
                           \       |   /      | 95.3 km\
                            [Leipzig]--       |         [Nuremberg]
                                 \     381.9  |         /    |     \
                         298.3 km \     km    |        /     |      \ 193.2 km
                                   \     [Mannheim]   /      |       \
                                    \         |      /       | 212.7  [Munich]
                                     \        | 69.8/        |  km    /
                                      \  [Karlsruhe]         |       / 154.4 km
                                       \      | 78.7 km      |      /
                                        \ [Stuttgart] ---- [Ulm] --/
                                               95.9 km
```

To model real-world optical amplification along continuous spans without relying on external proprietary link planning databases, `src/services/testbed_client.py` implements an analytical amplifier layout generator (`_build_link_amplifiers`). For any given link length $L_{ij}$, the generator synthesizes an engineered EDFA chain:

$$\mathcal{A}_{ij} = \left[ a_{ij, 0}, a_{ij, 1}, \dots, a_{ij, M-1} \right]$$

The placement follows a deterministic optical power budgeting heuristic:
- **Booster Amplifier ($a_{ij, 0}$):** Placed at position $z = 0.0\text{ km}$ at the ingress of each span, configured with a nominal gain of $G_{booster} = 3.0\text{ dB}$ to overcome ROADM multiplexer and optical patch-cord connector losses before launch into the standard single-mode fiber (SMF).
- **Single-Span Links ($L_{ij} \le 55.0\text{ km}$):** Links of short physical length require no intermediate inline amplification. A single terminal pre-amplifier is positioned at the link egress ($z = L_{ij}$), with gain calibrated to match the total span insertion loss and connector penalties:
  $$G_{preamp} = \alpha_{dB} \cdot L_{ij} + A_{conn} = 0.25 \cdot L_{ij} + 1.0 \quad [\text{dB}]$$
- **Multi-Span Links ($L_{ij} > 55.0\text{ km}$):** For long-haul links, the span is partitioned into $N_{spans} = \max(2, \lfloor L_{ij} / 70.0 \rceil)$ equal sub-spans of length $L_{span} = L_{ij} / N_{spans}$. Inline Amplifiers (ILAs) are deployed at positions $z_k = k \cdot L_{span}$ for $k \in \{1, \dots, N_{spans} - 1\}$, where each ILA provides gain compensating fiber attenuation and two optical connector interfaces:
  $$G_{ILA} = \alpha_{dB} \cdot L_{span} + 2 \cdot A_{conn} = 0.25 \cdot L_{span} + 2.0 \quad [\text{dB}]$$
  A terminal pre-amplifier is placed at $z = L_{ij}$ with gain $G_{preamp} = 0.25 \cdot L_{span} + 1.0\text{ dB}$.

Physical network access is unified behind the `TestbedClient` abstract base class, exposing `get_topology() -> TopologySnapshot` and `health_check() -> bool`. Two client implementations are provided:
- `MockTestbedClient`: Supplies the static, fully parameterized 17-node Nobel-Germany topology snapshot with analytical EDFA chains, executing entirely in memory for continuous integration and deterministic benchmarking.
- `RESTConfTestbedClient`: Connects to physical optical hardware via the SM Optics Optical Network Controller (ONC) Northbound Interface (NBI). The adapter integrates HTTP cookie-based session management authenticated against a Central Authentication Service (CAS) Single Sign-On (SSO) endpoint. It queries `/onc/nbi/ne` to discover operational Network Elements and `/onc/nbi/connection` to retrieve established cross-connects, isolating target testbed subtopologies through regex filtering on NE name labels (e.g., `ne_filter="Qiaolun"`). Because production RESTConf controllers abstract DWDM physical-layer parameters (such as raw amplifier noise figures and chromatic dispersion coefficients), the adapter merges live topological adjacency with the physical parameters defined in `_DEFAULT_LINK_PHYSICS`.

---

## 4.1.2 The Token Saturation Problem in Optical Control Planes

Modern optical transport controllers represent network state using standard YANG data models serialized into extensive JSON or XML structures via RESTConf or NETCONF protocols \cite{cruzes_telemetry_2026} \cite{ahmadian_t-api-compliant_2026}. A comprehensive JSON payload capturing a 17-node optical backbone—complete with transponder interface arrays, wavelength assignment bitmaps, optical multiplex section (OMS) power levels, and amplifier telemetry—frequently spans between 3,500 and 8,000 serialized lines, corresponding to 15,000--35,000 tokens.

Injecting full network configuration payloads directly into the context window of a Large Language Model (LLM) triggers three operational and computational bottlenecks:

1. **Context Window Exhaustion ($T_{prompt} \ge T_{max}$):** In production carrier environments containing hundreds of ROADMs and thousands of fiber links, raw topology serialization immediately exceeds the context limits of state-of-the-art models, precluding real-time prompt generation.
2. **Attention Degradation ("Lost-in-the-Middle"):** Autoregressive language models experience substantial attention dispersion when relevant constraints are buried within voluminous, highly structured JSON payloads \cite{di_cicco_open_2024} \cite{du_memory_2026}. When prompted with a full topology dump, LLMs frequently overlook negative routing constraints (e.g., `avoid-node`, `avoid-link`) located in distant sections of the context, generating invalid topological paths.
3. **Inference Latency and Financial Cost Inflation:** Generative inference latency scales with prompt length. Pushing tens of thousands of tokens per planning transaction yields unacceptable turnaround latencies ($T_{infer} > 30\text{ s}$) and unsustainable API operational expenses, conflicting with the requirements of dynamic control planes.

Consequently, bounding the context size before invoking the linguistic reasoning engine is an absolute architectural invariant.

---

## 4.1.3 Scoped Subtopology Extraction via Lightweight GraphRAG

To overcome token saturation without sacrificing topological awareness, the pipeline implements a localized subtopology extraction layer termed **Mock GraphRAG**, located in `src/core/mock_graphrag.py`. The "mock" designation reflects that the extraction operates via an in-memory graph traversal algorithm implemented in `networkx` rather than an external vector database, minimizing architectural complexity while ensuring deterministic execution.

### Graph Construction and Neighborhood Scoping

Upon topology ingestion, `build_adjacency_graph(topology: TopologySnapshot)` converts the snapshot into an undirected graph $G = (V, E)$. Node attributes store human-readable names, while edge attribute dictionaries preserve all physical transmission parameters ($L_{ij}, M_{ij}, N_{ch}, A_{port}, \mathcal{A}_{ij}$).

When an operator intent specifies a communication request between an origin node $s \in V$ and a destination node $d \in V$, the system scopes the context using $k$-hop neighborhood extraction (`extract_k_hop_neighborhood`):

```python
def extract_k_hop_neighborhood(
    graph: nx.Graph,
    source_node: str,
    target_node: str,
    k: int = 2,
) -> nx.Graph:
    source_neighbors = nx.single_source_shortest_path_length(graph, source_node, cutoff=k)
    target_neighbors = nx.single_source_shortest_path_length(graph, target_node, cutoff=k)
    relevant_nodes = set(source_neighbors.keys()) | set(target_neighbors.keys())
    return graph.subgraph(relevant_nodes).copy()
```

Formally, let $\text{dist}_G(u, v)$ represent the shortest path hop distance between vertices $u$ and $v$ in $G$. The $k$-hop neighborhood centered at vertex $u$ with radius $k \in \mathbb{N}$ is defined as:

$$N_k(u) = \left\{ v \in V \mid \text{dist}_G(u, v) \le k \right\}$$

The relevant subtopology node set $V_{sub} \subseteq V$ is the union of the $k$-hop neighborhoods centered on the source and target endpoints:

$$V_{sub} = N_k(s) \cup N_k(d)$$

The scoped subtopology $G_{sub} = (V_{sub}, E_{sub})$ is the node-induced subgraph of $G$:

$$E_{sub} = \left\{ (u, v) \in E \mid u \in V_{sub} \land v \in V_{sub} \right\}$$

By default, the radius is configured to $k = 2$. For the Nobel-Germany network, this bounds the candidate vertex set to the immediate switching neighborhood of the source and destination nodes, discarding irrelevant peripheral links (such as Munich and Ulm when routing between Hamburg and Berlin).

### Compact Context Serialization

To inject $G_{sub}$ into the LLM system prompt with maximum token density, `graph_to_context_string(graph)` serializes the subgraph into a structured, human-readable plain text schema:

```text
Nodes: Hamburg, Bremen, Hannover, Berlin
Links:
  - Hamburg ↔ Bremen | 129.7 km | 3 amp(s) | link_id: link_hamburg_bremen
  - Hamburg ↔ Hannover | 169.4 km | 3 amp(s) | link_id: link_hannover_hamburg
  - Hamburg ↔ Berlin | 330.9 km | 6 amp(s) | link_id: link_hamburg_berlin
  - Hannover ↔ Berlin | 324.7 km | 6 amp(s) | link_id: link_hannover_berlin
  - Hannover ↔ Bremen | 132.7 km | 3 amp(s) | link_id: link_hannover_bremen
```

Compared to a raw RESTConf JSON payload exceeding 15,000 tokens, the serialized scoped context string consumes fewer than **350 tokens**—representing a **$>97\%$ reduction in prompt token consumption** while retaining complete physical transparency over link lengths, amplifier counts, and topological identifiers.

### Implementation Clarifications and Backlog Resolutions

*Remark 1 (Optical RAG Standard Specification Bypass):* In the conceptual framework of Chapter 3, Phase 1 (Intent Ingestion and Optical RAG) encompasses two distinct retrieval mechanisms: (i) dynamic topological scoping via graph traversal, and (ii) vector-based document retrieval over ITU-T standard specifications (e.g., ITU-T G.694.1 spectral grids, G.652 fiber parameters). In the implemented codebase, the document retrieval branch was bypassed. Physical constants governing the optical grid (C-band central frequency $\nu_0 = 193.4\text{ THz}$, channel spacing $\Delta f = 50\text{ GHz}$, symbol rate $R_s = 32\text{ GBaud}$) and SMF-28 parameters are statically instantiated as immutable constants in `src/core/constants.py`. This engineering decision eliminates non-deterministic variance originating from vector search embeddings, isolating the performance and evaluation of the Risk-Adaptive Decision Gates (RADGs). Dynamic retrieval of non-standard optical equipment specifications is documented as Future Work in Chapter 6.

*Remark 2 (Ellipsoid Subtopology Scoping for Large Diameters):* In topologies where the topological diameter $\text{diam}(G)$ satisfies $\text{dist}_G(s, d) > 2k$, a naive static union $N_k(s) \cup N_k(d)$ can yield a disconnected subgraph where no physical path connects $s$ and $d$, artificially causing the symbolic solver to report path infeasibility. To guarantee connectivity across arbitrary network diameters while maintaining optimal token bounds, the architecture incorporates an adaptive fallback: when $\text{dist}_G(s, d) > 2k$, the node inclusion criterion shifts to an **Ellipsoid Subtopology Scope**:

$$V_{ellipsoid} = \left\{ v \in V \mid \text{dist}_G(s, v) + \text{dist}_G(v, d) \le \text{dist}_G(s, d) + \Delta \right\}$$

where $\Delta \in \mathbb{N}$ denotes an allowable detouring slack (typically $\Delta = 1$ or $\Delta = 2$). This formulation guarantees that all shortest paths and near-shortest detour paths are preserved within $G_{sub}$ while continuing to suppress topologically irrelevant nodes.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 4.1 Placement:** Architectural diagram illustrating the Optical Network Abstraction and GraphRAG extraction pipeline: showing the conversion of raw RESTConf JSON / SNDlib Nobel-Germany topology into the `networkx` graph, the dual-ball $k$-hop neighborhood expansion ($N_k(s) \cup N_k(d)$), and the serialized text prompt injection.
> - **Artifact Path:** `figs_NPImp/src/diagrams/graphrag_subtopology_extraction.drawio`
> - **Semantic Name:** `graphrag_subtopology_extraction`
> - **LaTeX Figure Reference:** `Figure~\ref{fig:graphrag_subtopology_extraction}`
> - **Implementation Grounding:** Verified against `src/services/testbed_client.py`, `src/core/mock_graphrag.py`, and `src/core/state.py`.
