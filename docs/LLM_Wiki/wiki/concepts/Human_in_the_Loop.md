---
title: "Concept: Human-in-the-Loop (HITL) Refinement"
date: 2026-09-19
tags: [concepts, hitl, reverse-prompting, human-in-the-loop, interrupt, radg, langgraph]
status: active
---

# Concept: Human-in-the-Loop (HITL) Refinement

## 1. Overview and Core Philosophy

In intent-based optical network automation, **Human-in-the-Loop (HITL)** refinement serves as the pre-deployment safety backstop bridging high-level operator intent and physical-layer configuration. Unconstrained Large Language Models (LLMs) are inherently prone to semantic drift, hallucinated constraints, and linguistic misalignment when interpreting natural language specifications. The HITL architecture resolves these failure modes by enforcing a strict **Reverse Prompting** validation loop and state-preserving execution pausing via LangGraph `interrupt()` primitives.

Rather than interrupting operators indiscriminately, the architecture introduces **Risk-Adaptive Decision Gates (RADGs)** that dynamically trigger human intervention only when quantified semantic uncertainty ($U_{sem} > \tau_{sem}$) or physical transmission unfeasibility ($\text{QoT}_{valid} = 0$) requires cognitive adjudication.

---

## 2. Architectural Placement and Decoupled Gates

HITL intervention is hierarchically decoupled across two discrete stages of the 7-phase neurosymbolic pipeline:

```
[Natural Language Intent]
           │
           ▼
 Phase 1: Intent Ingest & GraphRAG
           │
           ▼
 Phase 2: PDDL Translation
           │
           ▼
 Phase 3: Semantic RADG ───────► (U_sem > τ_sem) ──► Phase 3b: HITL Clarify
           │ (Pass)                                            │
           ▼                                                   │ approve / refine
 Phase 4: Symbolic Solver ◄────────────────────────────────────┘
           │
           ▼
 Phase 5: QoT Physics Engine
           │
           ▼
 Phase 6: Physical RADG ───────► (QoT_valid = 0) ──► Phase 6b: HITL Replan
           │ (Pass)                                            │
           ▼                                                   │ relax / re-route
 Phase 7: Plan Synthesis ◄─────────────────────────────────────┘
```

### 2.1 Phase 3b: Semantic Clarification Gate (`hitl_clarify_node`)
- **Trigger:** Evaluated when $U_{sem} > \tau_{sem} = 0.30$, indicating structural syntax errors in PDDL ($v_{struct} = 0$) or semantic divergence between the original intent and the reconstructed interpretation ($d_{sem} > 0.30$).
- **Mechanism:** The system performs automated PDDL-to-NL reconstruction ($\mathcal{I}_{recon}$) and pauses execution via `interrupt()`, presenting the operator with the reconstructed understanding, divergence score, and exact PDDL output.
- **Operator Actions ($\mathcal{A}_{clarify}$):**
  1. `approve`: Allowed only when $v_{struct} = 1$; provides an operator fast-track override directly into Phase 4 (`symbolic_solver`), bypassing redundant re-parsing.
  2. `refine`: Injects corrective feedback into `refinement_history`, increments `refinement_count`, and loops back to Phase 2 (`pddl_parser`).
  3. `cancel`: Aborts workflow gracefully (`__end__`).

### 2.2 Phase 6b: Physical Replanning Gate (`radg_node`)
- **Trigger:** Evaluated when candidate lightpaths satisfy semantic constraints but fail physical Quality of Transmission feasibility ($\text{QoT}_{valid} = 0$, due to insufficient GSNR margin or optical receiver power below sensitivity floor $P_{rx} < -18\text{ dBm}$).
- **Mechanism:** Raises a physical replan `interrupt()`, presenting link-by-link impairments (e.g., non-linear Kerr phase shift, ASE noise accumulation) and offering constraint relaxation options (e.g., relax GSNR threshold, bypass congested spans, allow higher hop count).

---

## 3. Mathematical Guarantees and Bounded Refinement

### 3.1 Context Window Protection ($N_{max} = 3$)
Unbounded multi-turn dialogue between an operator and an LLM leads to attention degradation ("lost-in-the-middle") and context window saturation. The architecture enforces an upper bound:
$$N_{max} = 3$$
If an intent fails to achieve $U_{sem} \le \tau_{sem}$ or physical feasibility within $N_{max}$ cycles, the system halts with an explicit cancellation interrupt (`status="aborted"`), guaranteeing finite convergence and preventing control-plane deadlocks.

### 3.2 Effective Reference Intent ($\mathcal{I}_{\text{eff}}^{(k)}$)
To eliminate monotonic refinement drift (BUG-009)—where operator relaxations are mistakenly classified by the evaluator LLM as hallucinations—the semantic agreement is evaluated against the accumulated effective intent:
$$\mathcal{I}_{\text{eff}}^{(k)} = \mathcal{I}_{NL} \oplus \bigoplus_{j=1}^{k} \delta_j$$
where $\delta_j$ represents operator modifications recorded in `refinement_history`.

---

## 4. State-Preserving Execution Pausing (`interrupt()`)

Unlike stateless procedural scripts or polling daemons, the orchestrator leverages LangGraph state checkpointers (`InMemorySaver` or `SqliteSaver` with `JsonPlusSerializer`):
1. **Atomic Serialization:** When `interrupt()` is called, the complete `AgentState` vector (topology subgraphs, candidate paths, PDDL structures, refinement history) is frozen and serialized to disk/memory.
2. **Zero Resource Consumption:** During operator dwell time (seconds to hours), compute threads and LLM token budgets are fully released.
3. **Deterministic Resumption:** The execution thread is resumed by passing operator decisions into `Command(resume=...)`, restoring the exact state and continuing along deterministic conditional routing edges.

---

## 5. Cross-References

- [[architecture/features/reverse_prompt]] — Feature documentation for Phase 3b Reverse Prompting.
- [[architecture/features/radg]] — Feature documentation for Phase 6 Physical RADG.
- [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates]] — Theoretical formulation of the piecewise RADGs decision function.
- [[concepts/Constraint_Isolation]] — Foundational principle separating reasoning from calculation.
- [[concepts/QoT_Awareness]] — Quality of Transmission physical constraints.
- [[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift]] — RCA and resolution for bounded refinement loops.
