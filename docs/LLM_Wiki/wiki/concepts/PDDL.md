---
title: "Concept: Planning Domain Definition Language (PDDL)"
date: 2026-09-19
tags: [concepts, pddl, cfg, formal-methods, symbolic-solver, grammar]
status: active
---

# Concept: Planning Domain Definition Language (PDDL)

## 1. Role in the Neurosymbolic Pipeline

The **Planning Domain Definition Language (PDDL)** serves as the unambiguous, formal intermediate representation (IR) bridging the probabilistic Neural Subsystem and the deterministic Symbolic Subsystem.

When an operator provides a high-level natural language intent (e.g., *"Provision a 100G circuit from Berlin to Frankfurt avoiding Munich with at least 15 dB GSNR"*), unconstrained natural language cannot be ingested by deterministic graph routing algorithms. The LLM translates this intent into a standardized PDDL problem definition containing typed predicates.

---

## 2. Optical Network PDDL Subset

To prevent open-ended grammatical hallucinations and maintain strict computational complexity bounds, the architecture restricts the PDDL domain to a specialized subset of predicates within the `:goal (and ...)` block:

| Predicate | Arity & Arguments | Semantics | Target Module |
| :--- | :--- | :--- | :--- |
| `(route ?src ?dst)` | 2 (Node, Node) | Establishes the source and destination nodes for the lightpath. | `symbolic_solver` (Yen's K-SP) |
| `(avoid-node ?node)` | 1 (Node) | Prunes specified vertex and incident edges from the routing graph. | `symbolic_solver` (Graph Pruning) |
| `(avoid-link ?src ?dst)` | 2 (Node, Node) | Prunes specified bidirectional physical fiber link. | `symbolic_solver` (Graph Pruning) |
| `(max-hops ?h)` | 1 (Integer) | Sets maximum allowable topological hop count. | `symbolic_solver` (Candidate Path Filter) |
| `(min-gsnr ?g)` | 1 (Float/Int dB) | Establishes the physical Generalized SNR threshold ($\text{GSNR}_{th}$). | `qot_validation` / `radg` |

### Example PDDL Problem Specification

```lisp
(define (problem optical-intent-001)
  (:domain optical-network)
  (:objects
    Berlin Frankfurt Munich - node
  )
  (:goal (and
    (route Berlin Frankfurt)
    (avoid-node Munich)
    (min-gsnr 15.0)
    (max-hops 4)
  ))
)
```

---

## 3. Context-Free Grammar (CFG) AST Validation ($v_{struct}$)

To guarantee that malformed or hallucinated PDDL cannot enter the symbolic solver or crash the control plane, the pipeline enforces Context-Free Grammar (CFG) validation in `src/core/pddl_validator.py` and `src/nodes/pddl_parser.py`:

1. **S-Expression Tokenizer:** Tokenizes parentheses, symbols, and literal values.
2. **Depth & Balance Verifier:** Verifies balanced parenthesis nesting.
3. **Recursive AST Parser:** Validates predicate signatures against the formal optical grammar:
   $$S_0 \to \text{"(:goal (and "} P^* \text{"))"}$$
   $$P \to \text{"(route "} \text{node } \text{node")"} \mid \text{"(avoid-node "} \text{node")"} \mid \dots$$
4. **Structural Validity Indicator ($v_{struct}$):**
   $$v_{struct} = \begin{cases} 1 & \text{if AST parse succeeds and all constraints are valid} \\ 0 & \text{otherwise} \end{cases}$$

If $v_{struct} = 0$, semantic uncertainty is clamped to maximum ($U_{sem} = 1.0$), immediately triggering Phase 3b HITL clarification without executing graph searches.

---

## 4. Cross-References

- [[architecture/features/pddl_parser]] — Implementation of the PDDL parser node and CFG validator.
- [[architecture/features/symbolic_solver]] — Deterministic solver consuming PDDL goals.
- [[concepts/Constraint_Isolation]] — Foundational separation of neural translation and deterministic solvers.
- [[thesis_drafts/3_SystemModel/3_3_Strict_Neurosymbolic_Separation]] — Formal mathematical specification of the CFG grammar $\mathcal{G}_{pddl}$.
