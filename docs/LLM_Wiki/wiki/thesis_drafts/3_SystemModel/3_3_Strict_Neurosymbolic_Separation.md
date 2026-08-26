---
title: "Chapter 3 - Section 3.3: Strict Neurosymbolic Separation"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, neurosymbolic, pddl, cfg-validator, separation-of-concerns]
status: draft
---

# 3.3 Strict Neurosymbolic Separation

## 3.3.1 The "LLMs Reason, Tools Calculate" Paradigm

A central design tenet of the proposed architecture is **Strict Neurosymbolic Separation**. In complex telecommunications domains, neural generative models and symbolic algorithms possess complementary, non-overlapping strengths:

- **Large Language Models (Neural):** Excel at high-level semantic reasoning, natural language ambiguity resolution, contextual synthesis, and unstructured intent extraction. However, they are fundamentally unreliable at deterministic numerical computation, combinatorial graph exploration, and constraint satisfaction over physical systems.
- **Symbolic and Analytical Solvers (Symbolic):** Excel at deterministic path optimization, exact graph traversal ($K$-shortest paths), mathematical constraint enforcement, and numerical physics modeling (e.g., non-linear optical propagation). However, they require rigid, structured formal syntax as input and cannot directly interpret unstructured human operators.

Attempting to force an LLM to compute optical lightpath feasibility natively results in severe hallucination, producing non-existent fiber spans or violating physical conservation laws. Conversely, restricting network operators to rigid command-line scripts defeats the purpose of autonomous Intent-Based Networking (IBN).

To reconcile this tension, our architecture enforces a strict boundary: **the LLM functions exclusively as a semantic compiler that translates linguistic intent into formal symbolic logic, while all topological search and physical calculations are delegated to deterministic external engines**.

```
  ┌──────────────────────────────────────────────────────────────┐
  │                    NEURAL SUBSYSTEM                          │
  │  • Natural Language Interpretation                           │
  │  • Contextual Disambiguation via Optical RAG                 │
  │  • Formal Semantic Translation (NL → PDDL)                   │
  │  • Reverse Prompting Semantic Agreement Judge                │
  └──────────────────────────────┬───────────────────────────────┘
                                 │
                     Formal PDDL Predicates &
                     CFG Structural Validation
                                 │
                                 ▼
  ┌──────────────────────────────────────────────────────────────┐
  │                   SYMBOLIC SUBSYSTEM                         │
  │  • Deterministic Graph Traversal (Yen's K-Shortest Paths)    │
  │  • Hard Constraint Filtering (Node/Link Exclusions, Max-Hops)│
  │  • Analytical Physics Engine (Gaussian Noise Model / GSNR)   │
  │  • Risk-Adaptive Decision Gate (RADG Logic)                  │
  └──────────────────────────────────────────────────────────────┘
```

---

## 3.3.2 PDDL Domain Formalization for Optical Routing

To establish a standard formal intermediate representation, we define an optical routing subset within the Planning Domain Definition Language (PDDL). The domain defines the types, predicates, and constraint structures required to model optical path establishment.

### Formal Type Hierarchy

```pddl
(define (domain optical-routing-v5)
  (:requirements :strips :typing :equality :conditional-effects)
  (:types
    node - object
    roadm transponder - node
    link - object
  )
)
```

### Predicate Definitions

The state and intent constraints are expressed using a minimal, closed set of first-order predicates:

$$\mathcal{P} = \{ \text{connected}(u, v), \text{route}(s, d), \text{avoid-node}(u), \text{avoid-link}(u, v), \text{max-hops}(h), \text{min-gsnr}(g) \}$$

Formally declared in PDDL syntax:

```pddl
(:predicates
  (connected ?u - node ?v - node)
  (route ?s - node ?d - node)
  (avoid-node ?n - node)
  (avoid-link ?u - node ?v - node)
  (max-hops ?h - object)
  (min-gsnr ?g - object)
)
```

### Intent Translation Mapping

When the operator submits an intent such as:
> *"Provision a lightpath from Hamburg to Leipzig with at least 15 dB GSNR, strictly avoiding Hannover due to maintenance."*

The neural translator produces the formal goal specification:

```pddl
(:goal
  (and
    (route Hamburg Leipzig)
    (avoid-node Hannover)
    (min-gsnr 15.0)
  )
)
```

---

## 3.3.3 Context-Free Grammar (CFG) Structural Validation

To guarantee that the neural translation output contains zero structural or syntactical hallucinations, the generated string is immediately audited by a deterministic Context-Free Grammar (CFG) validator.

Let the grammar $\mathcal{G}_{pddl}$ be defined by the 4-tuple:

$$\mathcal{G}_{pddl} = (V_N, \Sigma, R, S_0)$$

where:
- $V_N = \{ S_0, \text{GoalBlock}, \text{ExprList}, \text{Predicate}, \text{NodePair}, \text{SingleNode}, \text{NumericVal} \}$ is the set of non-terminal symbols.
- $\Sigma = \{ \text{'(', ')', 'and', 'route', 'avoid-node', 'avoid-link', 'max-hops', 'min-gsnr', [A-Z][a-z0-9\_]*, [0-9]+(\.[0-9]+)?} \}$ is the terminal alphabet.
- $R$ is the set of production rules:
  $$\begin{aligned}
  S_0 &\to \text{'('} \text{':goal'} \text{'('} \text{'and'} \; \text{ExprList} \; \text{')'} \text{')'} \\
  \text{ExprList} &\to \text{Predicate} \; \text{ExprList} \mid \text{Predicate} \\
  \text{Predicate} &\to \text{'('} \text{'route'} \; \text{NodePair} \text{')'} \\
  &\mid \text{'('} \text{'avoid-node'} \; \text{SingleNode} \text{')'} \\
  &\mid \text{'('} \text{'avoid-link'} \; \text{NodePair} \text{')'} \\
  &\mid \text{'('} \text{'max-hops'} \; \text{NumericVal} \text{')'} \\
  &\mid \text{'('} \text{'min-gsnr'} \; \text{NumericVal} \text{')'}
  \end{aligned}$$
- $S_0$ is the start symbol.

The CFG validator computes the structural indicator $v_{struct} \in \{0, 1\}$:

$$v_{struct} = \begin{cases} 1 & \text{if } \mathcal{S}_{PDDL} \in \mathcal{L}(\mathcal{G}_{pddl}) \land \text{EndpointsValid}(\mathcal{S}_{PDDL}, V_{sub}) \\ 0 & \text{otherwise} \end{cases}$$

If $v_{struct} = 0$, the plan fails the structural audit immediately, assigning maximum semantic uncertainty ($U_{sem} = 1.0$) without wasting downstream computational resources.

---

## 3.3.4 Deterministic Symbolic Solver and Graph Traversal

Once validated by the CFG gate, the PDDL predicates are translated into graph filtering operations executed over the extracted subtopology $G_{sub}(V_{sub}, E_{sub})$:

1. **Topological Pruning:**
   $$\widetilde{V}_{sub} = V_{sub} \setminus \{ u \mid \text{avoid-node}(u) \in \mathcal{S}_{PDDL} \}$$
   $$\widetilde{E}_{sub} = \{ (u, v) \in E_{sub} \mid u, v \in \widetilde{V}_{sub} \land (u, v) \notin \{ (x, y) \mid \text{avoid-link}(x, y) \in \mathcal{S}_{PDDL} \} \}$$

2. **$K$-Shortest Paths Search:**
   Using the pruned graph $\widetilde{G}_{sub} = (\widetilde{V}_{sub}, \widetilde{E}_{sub})$, the solver executes Yen's algorithm to compute the $K$ loopless paths minimizing total fiber length:
   $$\mathcal{K}_{path} = \text{YenKSP}\left(\widetilde{G}_{sub}, s, d, K=3\right)$$

3. **Hop Constraint Enforcement:**
   Any path $\pi \in \mathcal{K}_{path}$ whose hop length $|\pi| > h_{max}$ (if $\text{max-hops}(h_{max}) \in \mathcal{S}_{PDDL}$) is strictly removed.

By delegating path exploration to Yen's deterministic algorithm, the architecture guarantees $100\%$ topological validity, eliminating loop errors, non-existent link traversal, and disconnected paths.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.3 Placement:** Include a side-by-side comparison diagram:
> - *Left:* Conventional End-to-End LLM approach (Input $\to$ LLM $\to$ Hallucinated Path $\to$ Deployment Failure).
> - *Right:* Our Neurosymbolic Separation (Input $\to$ LLM Compiler $\to$ PDDL $\to$ CFG Check $\to$ Yen's Solver $\to$ GN Model).
> 
> **Mathematical Verification:** Ensure all PDDL predicate names correspond directly to the regex patterns implemented in `src/core/pddl_validator.py` and `src/core/symbolic_solver.py`.
