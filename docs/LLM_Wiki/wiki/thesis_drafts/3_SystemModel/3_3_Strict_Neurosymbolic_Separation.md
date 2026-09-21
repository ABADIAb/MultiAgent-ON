---
title: "Chapter 3 - Section 3.2: Strict Neurosymbolic Separation"
date: 2026-09-02
tags: [thesis, chapter-3, system-model, neurosymbolic, pddl, cfg-validator, separation-of-concerns]
status: active
---

# 3.3 Strict Neurosymbolic Separation

## 3.3.1 Functional Delegation in Network Configuration

Forcing an LLM to compute optical lightpath feasibility natively induces severe hallucination, yielding non-existent fiber spans or violating physical conservation laws. Conversely, restricting network operators to rigid command-line scripts nullifies the core objective of autonomous Intent-Based Networking (IBN). 

The proposed architecture isolates functional responsibilities. To prevent the fabrication of physical parameters—such as inaccurately predicting the GSNR over a non-linear optical span—the neural component is restricted entirely to semantic translation. The architecture delegates all path computation, wavelength assignment, and non-linear quality-of-transmission (QoT) validations to deterministic symbolic algorithms.

<!-- FIGURE_PLACEHOLDER: neural_symbolic_subsystems -->
> **Figure: Neurosymbolic Subsystem Architecture & PDDL Interface** (`figs_SystemModel/pdf/neural_symbolic_subsystems.pdf`)
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

To guarantee that the neural translation output contains zero structural or syntactical hallucinations, a deterministic Context-Free Grammar (CFG) validator immediately audits the generated string. This parser applies formal language rules to enforce that the PDDL syntax is strictly compliant before any subsequent processing occurs. If the CFG validator detects malformed parentheses, undefined predicates, or invalid node references, it sets $v_{struct} = 0$, explicitly triggering the semantic decision gate to halt execution.

The CFG parses the PDDL text into an Abstract Syntax Tree (AST) by checking the hierarchical S-expression structure against a predefined grammar (e.g., ensuring `(:goal (and ...))` blocks only contain valid predicates like `route`, `avoid-node`, or `min-gsnr`). It computes the structural indicator $v_{struct} \in \{0, 1\}$:

$$v_{struct} = \begin{cases} 1 & \text{if the PDDL string is syntactically valid} \\ 0 & \text{otherwise} \end{cases}$$

If $v_{struct} = 0$, the plan fails the structural audit. The system assigns maximum semantic uncertainty ($U_{sem} = 1.0$) and triggers a clarification request, avoiding wasted downstream computational resources.

## 3.3.4 Deterministic Symbolic Solver and Graph Traversal

Upon validation by the CFG gate, the system translates the PDDL predicates into topological graph pruning and constraint filtering operations. These execute over the $k$-hop subtopology $G_{sub}(V_{sub}, E_{sub})$ extracted by the topological context extractor:

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

Delegating path exploration to Yen's deterministic algorithm over the pruned topology $\widetilde{G}_{sub}$ mathematically precludes routing loops, traversal of non-existent links, or constraint violations prior GN-model QoT evaluation. Importantly, topological pruning is employed as a strategy to restrict the search space and strictly bound the context window size, ensuring that downstream calculations only consider valid topological subgraphs.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure Placement:** The structural division of responsibilities is illustrated in `Figure~\ref{fig:neural_symbolic_subsystems}`. The comparative analysis against conventional end-to-end LLM architectures is documented in the literature gap analysis (Chapter 2).

> [!TIP]
> **Code Alignment Note:** To maintain full transparency regarding the implementation, the production rules defined for $\mathcal{G}_{pddl}$ mirror the AST parsing logic strictly located in `src/core/pddl_validator.py`. The vertex/edge pruning mathematics ($\widetilde{G}_{sub}$) directly correspond to the constraints filtered dynamically in `src/core/symbolic_solver.py`.

