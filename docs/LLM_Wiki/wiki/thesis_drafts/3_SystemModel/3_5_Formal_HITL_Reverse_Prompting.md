---
title: "Chapter 3 - Section 3.5: Formal Human-in-the-Loop (HITL) via Reverse Prompting"
date: 2026-08-24
tags: [thesis, chapter-3, system-model, hitl, reverse-prompting, langgraph, interrupt, semantic-drift]
status: draft
---

# 3.5 Formal Human-in-the-Loop (HITL) via Reverse Prompting

## 3.5.1 The Semantic Drift Problem in Conversational Networking

In conversational Intent-Based Networking (IBN), intent refinement is frequently implemented via unconstrained multi-turn chat sessions. While intuitive, open-ended conversational memory introduces a critical vulnerability known as **Semantic Drift**:

When an operator corrects or adds a requirement during turn $t_k$ (e.g., *"also ensure the route avoids link L4"*), an autoregressive LLM may inadvertently drop or mutate non-salient constraints specified in earlier turns $t_0, \dots, t_{k-1}$ (such as a minimum GSNR threshold or a strict maximum-hop bound). Because standard conversational contexts treat all tokens probabilistically, there is no mathematical guarantee that previous hard constraints remain active.

This leads to two severe failure modes:
1. **Constraint Erosion:** Hard operational rules vanish during multi-turn negotiation.
2. **Infinite Negotiation Cycles:** The operator repeatedly corrects dropped constraints, increasing token consumption and control-plane latency without reaching a validated configuration.

---

## 3.5.2 The Reverse Prompting Invariant

To guarantee formal semantic convergence, our architecture introduces **Reverse Prompting** as a closed-loop validation contract. Rather than maintaining an unstructured dialogue history, the intent refinement loop operates over explicit, immutable symbolic state.

```
       Operator Intent (NL) :  I_NL
                 │
                 ▼
      ┌─────────────────────┐
      │ Forward Translation │  ──► PDDL Predicates : S_PDDL
      └─────────────────────┘              │
                 ▲                         ▼
                 │               ┌───────────────────────┐
                 │               │ Reverse Reconstruction│
                 │               └──────────┬────────────┘
                 │                          │
                 │                          ▼
                 │               Reconstructed Intent : I_recon
                 │                          │
                 │                          ▼
          Refined Feedback       ═════════════════════════
                 │               Semantic Agreement Engine
                 │               ═════════════════════════
                 │                          │
                 │                 [d_sem > τ_sem]
                 │                          │
                 │                          ▼
                 └─────────────────── LangGraph interrupt()
                                      (Operator Review)
```

The protocol proceeds in three deterministic steps:

1. **Forward Formal Translation:**
   $$\mathcal{S}_{PDDL} = \mathcal{M}_{forward}(\mathcal{I}_{NL}, G_{sub})$$
   where the LLM translates linguistic intent into formal PDDL predicates.

2. **Reverse Natural Language Reconstruction:**
   $$\mathcal{I}_{recon} = \mathcal{M}_{reverse}(\mathcal{S}_{PDDL})$$
   An independent generative prompt translates the formal PDDL syntax back into a clean, unambiguous natural language statement describing *exactly* what the system understood and intends to configure.

3. **Closed-Loop Agreement Verification:**
   The divergence $d_{sem} = 1 - \text{Score}_{agreement}(\mathcal{I}_{NL}, \mathcal{I}_{recon})$ is computed. If $d_{sem} > \tau_{sem}$, the reconstructed intent $\mathcal{I}_{recon}$ is presented to the operator alongside the specific extracted parameters:
   $$\mathcal{C}_{contract} = \langle \text{Source}, \text{Destination}, \text{AvoidNodes}, \text{AvoidLinks}, \text{MinGSNR}, \text{MaxHops} \rangle$$

By presenting $\mathcal{I}_{recon}$ rather than raw PDDL code, the operator can immediately verify if the system's formal interpretation aligns with operational reality without needing expertise in PDDL syntax.

---

## 3.5.3 State-Preserving Execution Pausing via LangGraph `interrupt()`

Traditional asynchronous web servers rely on polling loops or stateless HTTP webhooks to collect human input, which often leads to orphaned execution threads or race conditions in network controllers.

Our framework leverages native LangGraph **stateful interrupts** (`interrupt()`), enabling deterministic execution suspension:

```python
# Conceptual LangGraph Interrupt Pattern in Semantic Gate / RADG Node
if usem > tau_sem:
    # Suspend graph execution and persist state snapshot to checkpointer
    operator_response = interrupt({
        "status": "clarification_required",
        "usem": usem,
        "reconstructed_intent": reconstructed_text,
        "pddl_draft": pddl_string,
        "prompt": "Please confirm the extracted routing constraints or provide clarifications."
    })
    
    # Upon thread resumption, ingest explicit human feedback
    return {
        "error_context": operator_response.get("feedback"),
        "hitl_approved": operator_response.get("approved", False)
    }
```

### Execution Lifecyle under Interruption:
1. **Atomic Checkpoint Serialization:** When `interrupt()` is invoked, the execution engine halts node processing and serializes the complete `AgentState` tuple $\mathcal{S}_{state}$ into a persistent storage checkpointer (keyed by unique `thread_id`).
2. **Resource Freeing:** Memory and compute threads are released; no active LLM or server polling is maintained while waiting for human response.
3. **Resumption and Feedback Merging:** When the operator submits feedback through the CLI or management UI, the graph is reloaded from its exact checkpoint. The human feedback is injected directly into `state["error_context"]`, and the graph routes cleanly to Phase 2 for targeted PDDL re-parsing.

---

## 3.5.4 Monotonic Constraint Preservation and Convergence Guarantees

To ensure that multi-turn refinement strictly terminates, we define a **Monotonic Constraint Preservation** invariant:

Let $\mathcal{C}_k$ denote the set of active hard constraints in iteration $k$. When the operator introduces feedback $\mathcal{F}_k$, the new constraint set satisfies:

$$\mathcal{C}_{k+1} = \mathcal{C}_k \cup \text{ExtractConstraints}(\mathcal{F}_k) \setminus \text{ExplicitRevocations}(\mathcal{F}_k)$$

By storing $\mathcal{C}_k$ in a structured state dictionary rather than relying on unstructured chat history:
- **Zero Constraint Erosion:** Previously established rules cannot be silently dropped by the LLM.
- **Strict Turn Bounding:** The maximum number of HITL clarification turns is strictly bounded by $N_{max} = 3$. If an intent fails to achieve $U_{sem} \le \tau_{sem}$ after $N_{max}$ iterations, the transaction is rejected gracefully to prevent operational deadlocks.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 3.5 Placement:** Insert a Sequence Diagram showing the interaction between Operator, Orchestrator Graph, State Checkpointer, and LLM across a full interruption and resumption cycle.
> 
> **Implementation Reference:** Point out that this formal interrupt pattern is verified by the end-to-end test suite in `tests/unit/test_e2e_pipeline_flow.py` covering multi-turn checkpoint recovery.
