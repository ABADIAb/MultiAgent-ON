---
title: "Chapter 3 - Section 3.3: Strict Neurosymbolic Separation"
date: 2026-09-02
tags: [thesis, chapter-3, system-model, neurosymbolic, pddl, cfg-validator, separation-of-concerns]
status: active
---

# 3.3 Strict Neurosymbolic Separation

## 3.3.1 The "LLMs Reason, Tools Calculate" Paradigm

A central design tenet of the proposed architecture is strict neurosymbolic separation. In telecommunications domains, neural generative models and symbolic algorithms exhibit complementary, non-overlapping operational capabilities. 

- **Large Language Models (Neural Subsystem):** Generative language models excel at semantic reasoning, natural language ambiguity resolution, contextual synthesis, and unstructured intent extraction. However, they demonstrate fundamental unreliability regarding deterministic numerical computation, combinatorial graph exploration, and constraint satisfaction over physical systems.
- **Symbolic and Analytical Solvers (Symbolic Subsystem):** Symbolic algorithms execute deterministic path optimization, exact graph traversal (such as Yen's $K$-Shortest Paths), mathematical constraint enforcement, and numerical physics modeling. Yet, these solvers require rigid formal syntax and cannot process unstructured human requests natively.

Forcing an LLM to compute optical lightpath feasibility natively induces severe hallucination, yielding non-existent fiber spans or violating physical conservation laws. Conversely, restricting network operators to rigid command-line scripts nullifies the core objective of autonomous Intent-Based Networking (IBN). 

To reconcile this operational tension, the architecture enforces a strict boundary: the LLM functions exclusively as a semantic compiler that translates linguistic intent into formal symbolic logic. The system delegates all topological search operations and physical QoT calculations to deterministic external engines.

<!-- FIGURE_PLACEHOLDER: neural_symbolic_subsystems -->
> **Figure: Neurosymbolic Subsystem Architecture & PDDL Interface** (`figs/pdf/neural_symbolic_subsystems.pdf`)
> Decoupling of functional responsibilities: the Neural Subsystem handles intent extraction and linguistic formalization, passing typed PDDL predicates through a Context-Free Grammar (CFG) validation boundary to the deterministic Symbolic Subsystem for constraint pruning and physical simulation.

## 3.3.2 PDDL Domain Formalization for Optical Routing

To establish a standard formal intermediate representation, we define an optical routing subset within the Planning Domain Definition Language (PDDL). This domain formalizes the types, predicates, and constraint structures required to model optical path establishment.

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

*(Note: The implementation supports a broader set of syntactic aliases, such as `target-snr` or `routed`, which the parser normalizes to this formal set).*

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

When the operator submits an intent such as *"Provision a lightpath from Hamburg to Leipzig with at least 15 dB GSNR, strictly avoiding Hannover"*, the neural translator produces the formal goal specification:

```pddl
(:goal
  (and
    (route Hamburg Leipzig)
    (avoid-node Hannover)
    (min-gsnr 15.0)
  )
)
```

## 3.3.3 Context-Free Grammar (CFG) Structural Validation

To guarantee that the neural translation output contains zero structural or syntactical hallucinations, a deterministic Context-Free Grammar (CFG) validator immediately audits the generated string. 

Let the grammar $\mathcal{G}_{pddl}$ be defined by the 4-tuple:

$$\mathcal{G}_{pddl} = (V_N, \Sigma, R, S_0)$$

where:
- $V_N = \{ S_0, \text{ProblemDef}, \text{DomainBlock}, \text{ObjectsBlock}, \text{InitBlock}, \text{GoalBlock}, \text{ExprList}, \text{Predicate}, \text{NodePair}, \text{SingleNode}, \text{NumericVal}, \text{IntVal} \}$ defines the non-terminal symbols.
- $\Sigma = \{ \text{'(', ')', 'define', 'problem', ':domain', ':objects', ':init', ':goal', 'and', 'route', 'avoid-node', 'avoid-link', 'max-hops', 'min-gsnr', } \texttt{[A-Za-z0-9\_-]+} \}$ constitutes the terminal alphabet.
- $R$ specifies the production rules mapping the problem envelope and nested goal logic:
  $$\begin{aligned}
  S_0 &\to \text{'('} \text{'define'} \text{'('} \text{'problem'} \; \text{SingleNode} \text{')'} \; \text{DomainBlock} \; \text{ObjectsBlock} \; \text{InitBlock} \; \text{GoalBlock} \text{')'} \\
  \text{GoalBlock} &\to \text{'('} \text{':goal'} \text{'('} \text{'and'} \; \text{ExprList} \; \text{')'} \text{')'} \mid \text{'('} \text{':goal'} \text{Predicate} \text{')'} \\
  \text{ExprList} &\to \text{Predicate} \; \text{ExprList} \mid \text{Predicate} \\
  \text{Predicate} &\to \text{'('} \text{'route'} \; \text{NodePair} \text{')'} \\
  &\mid \text{'('} \text{'avoid-node'} \; \text{SingleNode} \text{')'} \\
  &\mid \text{'('} \text{'avoid-link'} \; \text{NodePair} \text{')'} \\
  &\mid \text{'('} \text{'max-hops'} \; \text{IntVal} \text{')'} \\
  &\mid \text{'('} \text{'min-gsnr'} \; \text{NumericVal} \text{')'}
  \end{aligned}$$
- $S_0$ serves as the start symbol.

The CFG validator parses the PDDL text into an Abstract Syntax Tree (AST) and computes the structural indicator $v_{struct} \in \{0, 1\}$:

$$v_{struct} = \begin{cases} 1 & \text{if } \mathcal{S}_{PDDL} \in \mathcal{L}(\mathcal{G}_{pddl}) \\ 0 & \text{otherwise} \end{cases}$$

If $v_{struct} = 0$, the plan fails the structural audit. The system assigns maximum semantic uncertainty ($U_{sem} = 1.0$) and triggers a clarification request, avoiding wasted downstream computational resources.

## 3.3.4 Deterministic Symbolic Solver and Graph Traversal

Upon validation by the CFG gate, the system translates the PDDL predicates into topological graph pruning and constraint filtering operations. These execute over the $k$-hop subtopology $G_{sub}(V_{sub}, E_{sub})$ extracted by the Mock GraphRAG:

1. **Topological Vertex Pruning:**
   The solver constructs a filtered vertex set $\widetilde{V}_{sub}$ by strictly subtracting any node $u$ designated by an $\text{avoid-node}$ predicate within the validated PDDL structure $\mathcal{S}_{PDDL}$. This guarantees the topological removal of prohibited entities prior to routing:
   $$\widetilde{V}_{sub} = V_{sub} \setminus \{ u \mid \text{avoid-node}(u) \in \mathcal{S}_{PDDL} \}$$

2. **Topological Edge Pruning:**
   The system filters the edge set to produce $\widetilde{E}_{sub}$. An edge $(u, v)$ remains viable strictly if both terminal nodes exist within the pruned vertex set $\widetilde{V}_{sub}$, and the edge itself avoids direct prohibition via an $\text{avoid-link}$ predicate. This yields the safe, fully pruned subtopology $\widetilde{G}_{sub} = (\widetilde{V}_{sub}, \widetilde{E}_{sub})$:
   $$\widetilde{E}_{sub} = \{ (u, v) \in E_{sub} \mid u, v \in \widetilde{V}_{sub} \land (u, v) \notin \{ (x, y) \mid \text{avoid-link}(x, y) \in \mathcal{S}_{PDDL} \} \}$$

3. **$K$-Shortest Paths Search:**
   Operating strictly upon the pruned subtopology $\widetilde{G}_{sub}$, the solver executes Yen's algorithm to compute $\mathcal{K}_{path}$, representing the $K$ optimal, loopless paths from source $s$ to destination $d$, minimizing the physical fiber distance objective:
   $$\mathcal{K}_{path} = \text{YenKSP}\left(\widetilde{G}_{sub}, s, d, K=5\right)$$

4. **Hop Constraint Enforcement:**
   The solver iterates over the candidate set $\mathcal{K}_{path}$. If the operator designates a maximum hop threshold $h_{max}$, any path $\pi$ exhibiting a hop cardinality $|\pi| > h_{max}$ undergoes strict elimination:
   $$\mathcal{K}_{path}^{final} = \{ \pi \in \mathcal{K}_{path} \mid |\pi| \le h_{max} \}$$

Delegating path exploration to Yen's deterministic algorithm over the pruned topology $\widetilde{G}_{sub}$ mathematically precludes routing loops, traversal of non-existent links, or constraint violations prior to initiating the computationally intensive GN-model QoT evaluation.

<!-- FIGURE_PLACEHOLDER: neurosymbolic_comparison -->
> **Figure: Architectural Comparison (Conventional Baseline vs. Proposed Framework)** (`figs/pdf/neurosymbolic_comparison.pdf`)
> Side-by-side comparison contrasting the unconstrained baseline (where direct LLM generation across full network telemetry triggers attention degradation, hallucinations, and reactive post-deployment errors) against our neurosymbolic separation (which guarantees zero physical risk through formal compilation, topological pruning, and deterministic GN-model physics).

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.3 Placement:** Include a side-by-side comparison diagram:
> - *Left (Baseline):* Conventional End-to-End LLM approach (Input $\to$ LLM $\to$ Hallucinated Path $\to$ Deployment Failure).
> - *Right (Ours):* Neurosymbolic Separation (Input $\to$ LLM Compiler $\to$ PDDL $\to$ CFG AST Check $\to$ Pruned Topological Solver $\to$ GN Model).

> [!TIP]
> **Code Alignment Note:** To maintain full transparency regarding the implementation, the production rules defined for $\mathcal{G}_{pddl}$ mirror the AST parsing logic strictly located in `src/core/pddl_validator.py`. The vertex/edge pruning mathematics ($\widetilde{G}_{sub}$) directly correspond to the constraints filtered dynamically in `src/core/symbolic_solver.py`.
