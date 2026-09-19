---
title: "Chapter 4 - Section 4.2: Semantic and QoT Validation Modules"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, pddl, cfg-ast, reverse-prompting, semantic-gate, qot, gn-model, physics]
status: draft
---

# 4.2 Semantic and QoT Validation Modules

## 4.2.1 Natural Language Intent Ingestion and Structured Extraction

The initial phase of the pipeline bridges informal operator communication with structured computational planning. Implemented in `src/nodes/intent_ingest.py`, the `intent_ingest_node` accepts the raw operator prompt string ($\mathcal{I}_{NL}$) alongside the active `TopologySnapshot`.

Rather than immediately translating unconstrained language into symbolic execution code, the module executes a two-step parsing routine:
1. **Dynamic Context Injection:** The localized subtopology context string produced by `graph_to_context_string` (Section 4.1.3) is injected into the LLM system prompt, grounding the language model in valid node identifiers and active fiber links.
2. **Constrained Schema Extraction:** The LLM is queried using structured outputs (enforced via Pydantic schema validation or model-native function calling) to produce an instance of `IntentSummary`:

```python
class IntentSummary(BaseModel):
    source: str | None = Field(description="Ingress node name or ID")
    target: str | None = Field(description="Egress node name or ID")
    bandwidth_gbps: int | None = Field(default=None, description="Required bitrate in Gbps")
    max_hops: int | None = Field(default=None, description="Maximum allowable hop count")
    min_gsnr: float | None = Field(default=None, description="Minimum GSNR threshold in dB")
    avoid_nodes: list[str] = Field(default_factory=list, description="Nodes to exclude")
    avoid_links: list[str] = Field(default_factory=list, description="Links to exclude")
    raw_intent: str = Field(description="Original intent text")
```

### Prevention of Lossy Numerical Abstraction

Early iterations of the ingestion module exhibited a critical failure mode: when downstream verification modules evaluated intent fidelity against the extracted `IntentSummary` rather than the verbatim operator message, subtle constraints were lost. For example, if an operator requested:
> *"Provision an optical circuit between Hamburg and Munich, avoiding Frankfurt, with a strict margin of at least 15.5 dB GSNR."*

an extractor might round the floating-point value to an integer (`min_gsnr: 15`), or abstract away domain qualifiers. In downstream reverse prompting, this lossy numerical abstraction generated an artificial semantic divergence ($d_{sem} > \tau_{sem}$), triggering unnecessary operator clarification interruptions.

To prevent this distortion, the pipeline enforces the **Verbatim Intent Preservation Invariant**: `intent_ingest_node` instantiates the state variable `active_intent` using the exact, unmodified operator input string. The structured `IntentSummary` serves exclusively to guide downstream prompt templating and initialize subtopology scoping, while `active_intent` remains the single immutable reference for semantic agreement scoring throughout the pipeline lifecycle.

---

## 4.2.2 Multi-Turn Intent Reconciliation and Disambiguation Reasoning

When an intent triggers an operational interruption—either during semantic clarification in Phase 3b or physical replanning in Phase 6—the operator submits corrective feedback. In multi-turn conversational architectures, Small Language Models (SLMs, e.g., 3B to 7B parameter models such as `qwen2.5:3b`) exhibit severe vulnerability to **ghost constraint leakage** \cite{bekri_bridging_2025}. When presented with conversational history, SLMs frequently conflate prior constraints with new instructions, producing contaminated intent states (e.g., retaining a previously requested avoidance of Leipzig when the operator explicitly requested a completely new route from Berlin to Frankfurt).

To eliminate ghost constraint contamination, `src/nodes/intent_reconciler.py` implements a formal intent reconciliation engine powered by the `RefinedIntentAnalysis` structured model:

```python
class IntentUpdateType(str, Enum):
    FULL_REPLACEMENT = "full_replacement"
    PARTIAL_UPDATE = "partial_update"

class RefinedIntentAnalysis(BaseModel):
    update_type: IntentUpdateType
    reasoning: str
    updated_intent: str
    source_node: str | None = None
    target_node: str | None = None
    modified_constraints: list[str] = Field(default_factory=list)
```

The reconciler executes a deterministic classification taxonomy:
- **Full Replacement (`full_replacement`):** Triggered when the operator explicitly aborts the previous request (e.g., *"Cancel that. Route from Cologne to Frankfurt"*), provides a self-contained routing statement with a new endpoint pair, or supplies complete instructions following an incomplete turn. Under this branch, all prior endpoints, exclusions, and numerical thresholds are discarded, resetting the state to the new intent.
- **Partial Update (`partial_update`):** Triggered when the operator adjusts, relaxes, or removes specific constraints while maintaining the general request context (e.g., *"Relax the GSNR threshold to 12 dB"* or *"Remove the avoidance on Frankfurt"*). The module merges the modification into the existing constraint set.

Furthermore, if the reconciler identifies modified endpoint nodes ($s' \ne s$ or $d' \ne d$), it dynamically invokes `extract_k_hop_neighborhood` to rescope the subtopology $G_{sub}$ to the new geographic region, preventing downstream routing failures caused by stale topological context.

---

## 4.2.3 Context-Free Grammar (CFG) AST PDDL Validation ($v_{struct}$)

To strictly enforce neurosymbolic separation, the LLM does not generate graph paths or optical device configurations directly. Instead, Phase 2 (`src/nodes/pddl_parser.py`) prompts the model to act as a pure linguistic translator, mapping the natural language intent into a simplified Planning Domain Definition Language (PDDL) problem specification \cite{fox_pddl21_2003}.

An illustrative translation generated by the model takes the following formal structure:

```lisp
(define (problem optical-routing-hamburg-munich)
  (:domain optical-network)
  (:objects
    node_3 node_7 node_2 - node
  )
  (:init
    (traffic-demand node_3 node_7)
  )
  (:goal
    (and
      (route node_3 node_7)
      (avoid-node node_2)
      (min-gsnr 15.0)
    )
  )
)
```

### Deterministic S-Expression Tokenization and AST Construction

Because autoregressive models can generate syntactically corrupted expressions, unbalanced parentheses, or hallucinated predicates, accepting raw PDDL into the symbolic solver introduces catastrophic control-plane failure risks. Rather than relying on fragile regular expression heuristics, `src/core/pddl_validator.py` implements a rigorous Context-Free Grammar (CFG) parser based on S-expression abstract syntax trees (AST).

The parser operates through two formal stages:

1. **Tokenization and Nesting Depth Tracking (`_tokenize`):** The raw string is stripped of comments (semicolon prefixes) and scanned character-by-character. The lexer tracks parenthesis depth:
   $$\text{depth}(i) = \sum_{k=0}^{i} \left( \mathbb{I}(c_k = \text{'('}) - \mathbb{I}(c_k = \text{')'}) \right)$$
   An invariant condition $\text{depth}(i) \ge 0$ is enforced for all character indices $i$; any violation ($\text{depth} < 0$) immediately flags an unbalanced closing parenthesis. At string termination, the lexer verifies $\text{depth} = 0$.
2. **Recursive AST Builder (`_parse_s_expressions`):** Lexical tokens are parsed into nested Python lists representing the S-expression tree. The top-level expression must conform to `(define (problem <name>) ...)`. Mandatory sections defined by the grammar:
   $$\mathcal{S}_{required} = \{ \text{domain}, \text{objects}, \text{init}, \text{goal} \}$$
   are extracted and validated.

### Routing Predicate Grammar Production Rules

Within the `:goal` section, the parser isolates the logical conjunction `(and ...)` and applies formal type- and arity-checking against the domain grammar production rules:

$$\begin{aligned}
\langle\text{Predicate}\rangle &::= \langle\text{RoutePred}\rangle \mid \langle\text{AvoidNodePred}\rangle \mid \langle\text{AvoidLinkPred}\rangle \mid \langle\text{MaxHopsPred}\rangle \mid \langle\text{MinGSNRPred}\rangle \\
\langle\text{RoutePred}\rangle &::= \text{'(' } (\text{'route'} \mid \text{'path'}) \text{ } \langle\text{NodeId}\rangle \text{ } \langle\text{NodeId}\rangle \text{ ')'} \\
\langle\text{AvoidNodePred}\rangle &::= \text{'(' } (\text{'avoid-node'} \mid \text{'avoid'}) \text{ } \langle\text{NodeId}\rangle \text{ ')'} \\
\langle\text{AvoidLinkPred}\rangle &::= \text{'(' } \text{'avoid-link'} \text{ } (\langle\text{LinkId}\rangle \mid \langle\text{NodeId}\rangle \text{ } \langle\text{NodeId}\rangle) \text{ ')'} \\
\langle\text{MaxHopsPred}\rangle &::= \text{'(' } \text{'max-hops'} \text{ } \langle\text{Integer}\rangle \text{ ')'} \\
\langle\text{MinGSNRPred}\rangle &::= \text{'(' } \text{'min-gsnr'} \text{ } \langle\text{Float}\rangle \text{ ')'}
\end{aligned}$$

The validator outputs the binary structural validity indicator:

$$v_{struct} = \begin{cases} 1 & \text{if all parentheses balance and all predicates satisfy } \mathcal{G}_{pddl} \\ 0 & \text{otherwise} \end{cases}$$

If $v_{struct} = 0$, the parser returns the detailed list of syntax and arity violations, immediately halting downstream execution.

---

## 4.2.4 Automated Reverse Prompting and the Two-Layer Semantic RADG ($U_{sem}$)

To prevent semantic drift while eliminating human interruption for unambiguous intents, Phase 3 implements an automated Reverse Prompting protocol coupled to a mathematical Semantic Uncertainty Gate (`src/nodes/reverse_prompt.py`, `src/nodes/semantic_gate_node.py`, and `src/core/semantic_gate.py`).

### Automated PDDL-to-NL Reconstruction ($\mathcal{I}_{recon}$)

Immediately following PDDL parsing, the pipeline invokes an automated reconstruction turn (`reverse_prompt_node`). Crucially, this execution involves **zero human intervention**. A secondary prompt presents the generated PDDL string back to the language model, instructing it to translate the formal symbolic constraints back into natural language:

$$\mathcal{I}_{recon} = \text{LLM}_{recon}\left( \mathcal{S}_{PDDL} \right)$$

To ensure the reconstruction reflects only genuine routing constraints without prompt contamination, `_clean_pddl_for_reverse_prompt()` filters out verbose topological connectivity predicates (such as `(connected node_1 node_2)` or `(link-active link_12)`) prior to reconstruction, presenting only the operational `:goal` constraints.

### Semantic Agreement Evaluation and Divergence Computation

Next, the reconstructed intent $\mathcal{I}_{recon}$ and the original operator intent $\mathcal{I}_{NL}$ (retrieved from `active_intent`) are supplied to an independent LLM Agreement Judge. The judge evaluates the semantic correspondence between the two statements and outputs an agreement score:

$$S_{agree} \in [0.0, 1.0]$$

where $S_{agree} = 1.0$ indicates identical routing requirements, and $S_{agree} = 0.0$ signifies contradictory or missing constraints. The semantic divergence score is defined as:

$$d_{sem} = 1.0 - S_{agree}$$

### The Two-Layer Uncertainty Formulation

The Semantic Uncertainty metric $U_{sem} \in [0.0, 1.0]$ is computed deterministically via the pure decision function in `src/core/semantic_gate.py`:

$$U_{sem} = \begin{cases} 1.0 & \text{if } v_{struct} = 0 \quad (\text{Layer 1: Structural AST Failure}) \\ d_{sem} & \text{if } v_{struct} = 1 \quad (\text{Layer 2: Semantic Divergence}) \end{cases}$$

The gate evaluates $U_{sem}$ against the operator-defined tolerance threshold $\tau_{sem}$ (configured by default to $\tau_{sem} = 0.30$):
- **Autonomous Pass ($U_{sem} \le \tau_{sem}$):** The intent is validated as semantically unambiguous and structurally sound. The pipeline proceeds directly to Phase 4 (Symbolic Solver) with **zero human interruptions** ($N_{hitl} = 0$).
- **Fail-Fast Interruption ($U_{sem} > \tau_{sem}$):** The intent contains irreconcilable ambiguity, missing parameters, or a structural parsing failure. Execution suspends via LangGraph's `interrupt()` primitive at `hitl_clarify_node`, presenting $\mathcal{I}_{recon}$, the identified discrepancies, and the computed $U_{sem}$ score to the human operator for disambiguation.

---

## 4.2.5 Deterministic GN-Model Physical-Layer Physics Engine

When candidate lightpaths are extracted by the symbolic solver in Phase 4 (utilizing Yen's $K$-Shortest Paths with topological constraint pruning over $G_{sub}$), their transmission feasibility must be verified against the physical optical layer. Delegating this verification to an LLM introduces hallucinated physics. In our architecture, physical validation is strictly isolated within the **QoT Calculator** (`src/core/qot_calculator.py`), an analytical engine ported directly from the C++ GNPy-compliant research simulator \cite{damico_gnpy_2026}.

### Analytical Formulations of the Incoherent GN Model

The calculator implements the incoherent Gaussian Noise (GN) model for wavelength-division multiplexed (WDM) systems operating over non-dispersion-managed standard single-mode fiber \cite{poggiolini_gn_2014}.

The non-linear interference (NLI) power spectral density constant $\eta_0$ is pre-computed via `_compute_constant_nli()`:

$$\eta_0 = \frac{8}{27} \cdot \frac{\alpha \cdot \gamma^2 \cdot \ln\left( \frac{\pi^2 |\beta_2| R_s^2 N_{ch}^{2 R_s / \Delta f}}{\alpha} \right)}{\pi |\beta_2| R_s^2}$$

where physical constants are instantiated from `src/core/constants.py`:
- $\alpha = 0.25\text{ dB/km} \implies \alpha_{lin} = \frac{0.25}{10 \log_{10}(e) \cdot 10^3} \approx 5.756 \times 10^{-5}\text{ m}^{-1}$ (attenuation coefficient).
- $\gamma = 1.27 \times 10^{-3}\text{ W}^{-1}\text{m}^{-1}$ (fiber non-linear Kerr coefficient).
- $\beta_2 = 21.7 \times 10^{-27}\text{ s}^2/\text{m}$ (group velocity dispersion parameter).
- $R_s = 32 \times 10^9\text{ Baud}$ (symbol rate).
- $\Delta f = 50 \times 10^9\text{ Hz}$ (channel grid spacing).
- $N_{ch} = B_{c} / \Delta f = 5 \times 10^{12} / 50 \times 10^9 = 100$ (active channels across the 5 THz C-band).

### Per-Span Noise and Power Accumulation

For each amplified fiber span of physical length $L_{span}$, `span_snr()` evaluates the effective non-linear length:

$$L_{eff} = \frac{1 - e^{-\alpha_{lin} \cdot L_{span} \cdot 10^3}}{\alpha_{lin}} \quad [\text{m}]$$

The non-linear interference coefficient is:

$$\mu_{NLI} = \eta_0 \cdot L_{eff}^2$$

The Amplified Spontaneous Emission (ASE) noise generated by an EDFA of linear gain $G = 10^{G_{dB}/10}$ and linear noise figure $NF = 10^{NF_{dB}/10}$ is calculated as:

$$P_{ASE} = h \cdot \nu_0 \cdot R_s \cdot (G - 1) \cdot NF \quad [\text{W}]$$

where $h = 6.626 \times 10^{-34}\text{ J}\cdot\text{s}$ is Planck's constant and $\nu_0 = 193.4 \times 10^{12}\text{ Hz}$ is the optical carrier frequency. Given signal launch power $P_{out}$ (in Watts), the Noise-to-Signal Ratio ($\text{NSR} = \text{SNR}^{-1}$) contributed by the span is:

$$\text{NSR}_{span} = \frac{P_{ASE} + \mu_{NLI} \cdot P_{out}^3}{P_{out}}$$

For terminal fiber sections lacking a destination pre-amplifier (`last_span_no_preamp=True`), optical amplification is absent ($P_{ASE} = 0$), and the span contributes purely non-linear distortion:

$$\text{NSR}_{last} = \mu_{NLI} \cdot P_{out}^2$$

### End-to-End Demand Path Traversal

In `calculate_demand_snr(path: list[FiberLink])`, the pipeline traces the continuous optical path across cascading spans and intermediate ROADM nodes:
1. **Transponder Noise Floor:** Ingress modulation noise is bounded by the back-to-back transponder SNR ($\text{SNR}_{trx} = 26.0\text{ dB}$):
   $$\text{NSR}_{total} = \frac{1}{10^{\text{SNR}_{trx} / 10}} + \sum_{k=1}^{N_{spans}} \text{NSR}_{span, k}$$
2. **Node Insertion and Filter Losses:** Optical signal power is attenuated by ROADM ingress/egress connectors ($A_{conn} = 1.0\text{ dB}$), internal port switching losses ($A_{port} = 0.5\text{ dB}$), and wavelength multiplexer/demultiplexer filter cascades ($A_{filter} = 6.0\text{ dB}$).
3. **Trans-Node NLI Continuity:** For fiber spans crossing intermediate nodes without optical regeneration, leftover unamplified fiber lengths are tracked across link boundaries to preserve non-linear phase accumulation.

The final end-to-end Generalized Signal-to-Noise Ratio (GSNR) and received optical power $P_{rx}$ are computed as:

$$\text{GSNR}_{computed} = 10 \log_{10}\left( \frac{1}{\text{NSR}_{total}} \right) \quad [\text{dB}]$$

$$P_{rx} = P_{tx} - \sum A_{losses} + \sum G_{amplifiers} \quad [\text{dBm}]$$

### Optical Power Calibration and Prevention of Non-Linear Explosion

During Sprint 1 integration, an initial physical calibration issue was diagnosed and resolved (documented in `docs/LLM_Wiki/wiki/experiments/bugs/bug003_NLI_Explosion.md`). If transponder launch powers or EDFA gains are configured improperly, signal powers entering fiber spans can exceed $+3\text{ dBm}$, causing the cubic term $\mu_{NLI} P_{out}^3$ to dominate and artificially collapse the calculated GSNR by over $15\text{ dB}$.

The physics engine establishes calibrated operating limits matching industrial dense WDM transmission:
- Nominal transponder output power: $P_{tx} = +1.0\text{ dBm}$.
- Booster and ILA gains calibrated such that per-channel launch powers entering transmission spans remain strictly within the optimal linear regime:
  $$P_{launch} \in [-15.0, -11.0] \quad [\text{dBm}]$$
- Transceiver sensitivity floor: $P_{rx, min} = -18.0\text{ dBm}$.

### Feasibility Verdict ($QoT_{valid}$)

The top-level evaluation function `assess_qot()` compares the computed physical metrics against modulation-specific thresholds defined in `ThresholdConstants`:

$$\text{GSNR}_{th}(\text{bitrate}) = \begin{cases}
12.2\text{ dB} & \text{for } 10\text{ Gbps (OOK / QPSK)} \\
8.6\text{ dB} & \text{for } 100\text{ Gbps (DP-QPSK)} \\
15.2\text{ dB} & \text{for } 200\text{ Gbps (DP-16QAM)} \\
21.5\text{ dB} & \text{for } 400\text{ Gbps (DP-64QAM)}
\end{cases}$$

A candidate path is verified as physically feasible if and only if both the GSNR margin and the optical power budget are satisfied:

$$\text{QoT}_{valid} = \mathbb{I}\left( \text{GSNR}_{computed} \ge \max\left( \text{GSNR}_{th}, \text{GSNR}_{target} \right) \land P_{rx} \ge P_{rx, min} \right)$$

This calculation executes in under **$1.5\text{ ms}$ per candidate path**, providing deterministic, auditable physical validation before any configuration reaches the network control plane.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 4.2 Placement:** Two-part technical diagram: (a) The Two-Layer Semantic RADG flowchart showing $v_{struct}$ AST verification and $d_{sem}$ Reverse Prompting comparison routing; (b) The GN-Model Physics Engine schematic showing EDFA gain compensation, ASE noise generation, and non-linear Kerr effect accumulation across intermediate spans.
> - **Artifact Path:** `figs_NPImp/src/diagrams/semantic_gate_and_qot_engine.drawio`
> - **Semantic Name:** `semantic_gate_and_qot_engine`
> - **LaTeX Figure Reference:** `Figure~\ref{fig:semantic_gate_and_qot_engine}`
> - **Implementation Grounding:** Verified against `src/core/pddl_validator.py`, `src/core/semantic_gate.py`, `src/core/qot_calculator.py`, and `src/core/constants.py`.
