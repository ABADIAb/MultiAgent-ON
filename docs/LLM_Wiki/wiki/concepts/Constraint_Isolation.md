---
title: "Concept: Constraint Isolation"
date: 2026-09-19
tags: [concepts, neurosymbolic, constraint-isolation, physics-engine, deterministic]
status: active
---

# Concept: Constraint Isolation

## 1. Definition and Rationale

**Constraint Isolation** is the core neurosymbolic design pattern underpinning this thesis: **"LLMs reason, tools calculate."**

Large Language Models (LLMs) are probabilistic next-token predictors optimized for semantic comprehension, syntactic manipulation, and translation across modalities. However, they lack arithmetic precision and cannot reliably compute complex physical-layer integrals, non-linear fiber propagation equations, or combinatorial graph traversals without hallucinating.

Constraint Isolation strictly isolates all deterministic mathematical, physical, and algorithmic tasks into pure, verifiable software modules:
- **Physical-layer physics:** Gaussian Noise (GN) model calculations (Amplified Spontaneous Emission, Kerr non-linear interference, GSNR accumulation) are isolated in `src/core/qot_calculator.py`.
- **Topological route optimization:** Yen's $K$-Shortest Paths and vertex/edge pruning are isolated in `src/core/symbolic_solver.py`.
- **PDDL syntax validation:** Context-Free Grammar AST parsing is isolated in `src/core/pddl_validator.py`.
- **Topological scoping:** $k$-hop neighborhood extraction is isolated in `src/core/mock_graphrag.py`.

The LLM is restricted exclusively to semantic translation (converting natural language operator intent into formal PDDL predicates and back) and semantic agreement judging.

---

## 2. Architectural Boundary

The architecture enforces a strict bidirectional boundary between the Neural Subsystem and the Symbolic Subsystem:

| Subsystem | Components | Operational Responsibility | Failure Mitigation |
| :--- | :--- | :--- | :--- |
| **Neural (Probabilistic)** | `intent_ingest_node`, `pddl_parser_node`, `semantic_gate_node` (Judge) | Natural language understanding, PDDL translation, semantic divergence estimation | Reverse Prompting, Context-Free Grammar AST validation, Two-Layer Semantic RADG |
| **Symbolic (Deterministic)** | `pddl_validator`, `mock_graphrag`, `symbolic_solver`, `qot_calculator`, `radg` | Grammatical syntax verification, graph scoping, Yen's K-SP route search, GN-model SNR accumulation, piecewise decision gates | Deterministic execution, mathematical precision, guaranteed termination |

---

## 3. Impact on System Safety

By isolating constraints from the LLM:
1. **Zero Hallucinated Physics:** The LLM never predicts or calculates SNR, noise power, or dispersion values. All physical decisions are computed deterministically from immutable parameters in `src/core/constants.py` and physical fiber link attributes.
2. **Unfeasible Approval Rate (UAR) Minimization:** Even if an LLM generates invalid routing intents, the deterministic downstream gates (`pddl_validator`, `symbolic_solver`, and `qot_validation`) guarantee that unfeasible configurations cannot be deployed into the optical data plane.
3. **Token Efficiency:** Graph traversal and physical equations do not saturate prompt token contexts, eliminating attention degradation.

---

## 4. Cross-References

- [[Architecture_v5]] — System architecture and strict neurosymbolic separation.
- [[concepts/QoT_Awareness]] — Physical-layer Quality of Transmission metrics.
- [[concepts/Human_in_the_Loop]] — Human-in-the-loop intervention mechanisms.
- [[concepts/PDDL]] — Planning Domain Definition Language subset formalization.
- [[thesis_drafts/3_SystemModel/3_3_Strict_Neurosymbolic_Separation]] — Formal thesis chapter on strict neurosymbolic boundaries.
- [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates]] — The Risk-Adaptive Decision Gates formulation.
