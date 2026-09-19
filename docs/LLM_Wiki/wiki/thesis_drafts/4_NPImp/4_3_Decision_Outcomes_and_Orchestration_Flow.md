---
title: "Chapter 4 - Section 4.3: Decision Outcomes and Orchestration Flow"
date: 2026-09-19
tags: [thesis, chapter-4, implementation, langgraph, radg, hitl, state-machine, orchestration, e2e-flows]
status: draft
---

# 4.3 Decision Outcomes and Orchestration Flow

## 4.3.1 LangGraph StateGraph Architecture and State Schema

The end-to-end coordination of the seven-phase neurosymbolic pipeline is orchestrated via a directed acyclic state machine implemented in `src/core/graph.py`, leveraging the `langgraph` framework \cite{langgraph_2024}. Unlike conventional autonomous agent loops that rely on unconstrained while-loops or monolithic prompt chains, our architecture structures intent planning as an explicit, state-preserving computational graph where transitions between linguistic reasoning, symbolic solvers, and physical physics engines are deterministically governed by conditional routing edges.

### State Schema (`AgentState`)

The shared memory across all execution stages is encapsulated within `AgentState`, a `TypedDict` schema defined in `src/core/state.py`:

```python
class AgentState(TypedDict):
    messages: list[Any]
    active_intent: str | None
    enriched_intent: str | None
    pddl_constraints: str | None
    pddl_valid: bool | None
    hitl_reconstruction: str | None
    hitl_approved: bool | None
    topology_snapshot: TopologySnapshot | None
    topology_context: str | None
    candidate_paths: list[list[str]] | None
    qot_results: list[dict[str, Any]] | None
    planning_report: str | None
    error_context: str | None
    usem_score: float | None
    usem_passed: bool | None
    radg_decision: str | None
```

Every pipeline node operates as a pure or state-transforming function with signature:
$$\text{node\_fn}: \text{AgentState} \longrightarrow \Delta\text{AgentState}$$
Nodes return partial dictionary updates that LangGraph merges into the global checkpointed state. This design guarantees complete immutability of historical snapshots, facilitates modular unit testing, and ensures execution determinism.

### State Persistence and Atomic Checkpointing

To support asynchronous Human-in-the-Loop (HITL) engagement without thread blocking or memory loss, `compile_graph` integrates an atomic state checkpointer (`InMemorySaver` for local benchmarking and development, or `SqliteSaver` / `PostgresSaver` for production deployments). When a decision gate suspends execution via `interrupt()`, the checkpointer writes a serialized snapshot of `AgentState` indexed by a unique `thread_id`. The operating thread is released immediately, allowing the orchestrator to remain completely dormant until the human operator supplies clarification or approval, whereupon execution resumes from the exact saved checkpoint.

```
       +-------------------------------------------------------------------------------+
       |                               START (main.py)                                 |
       +-------------------------------------------------------------------------------+
                                               |
                                               v
                               +-------------------------------+
                               | Phase 1: Intent Ingest & RAG  |
                               | (intent_ingest_node)          |
                               +-------------------------------+
                                               |
                                               v
                               +-------------------------------+
           +------------------>| Phase 2: PDDL Parsing         |<---------------------+
           |                   | (pddl_parser_node)            |                      |
           |                   +-------------------------------+                      |
           |                                   |                                      |
           |                                   v                                      |
           |                   +-------------------------------+                      |
           |                   | Phase 3a: Reverse Prompting   |                      |
           |                   | (reverse_prompt_node)         |                      |
           |                   +-------------------------------+                      |
           |                                   |                                      |
           |                                   v                                      |
           |                   +-------------------------------+                      |
           |                   | Phase 3: Semantic RADG        |                      |
           |                   | (semantic_gate_node)          |                      |
           |                   +-------------------------------+                      |
           |                                   |                                      |
           |                 [U_sem > tau_sem] | [U_sem <= tau_sem]                   |
           |                                   v                                      |
           |         +---------------------------------------------------+            |
           |         | Phase 3b: HITL Clarify (hitl_clarify_node)        |            |
           |         | State Suspended via interrupt()                   |            |
           |         +---------------------------------------------------+            |
           |             |                                   |                        |
           | (Clarify /  |                                   | (Fast-Track Override   |
           |  Feedback)  |                                   |  v_struct = 1)         |
           +-------------+                                   |                        |
                                                             v                        |
                               +---------------------------------------------------+  |
                               | Phase 4: Symbolic Solver (symbolic_solver_node)   |  |
                               | Yen's K-Shortest Paths with Constraint Pruning    |  |
                               +---------------------------------------------------+  |
                                                       |                              |
                                                       v                              |
                               +---------------------------------------------------+  |
                               | Phase 5: QoT Validation (qot_validation_node)     |  |
                               | GN-Model Physics Engine (span_snr, demand_snr)    |  |
                               +---------------------------------------------------+  |
                                                       |                              |
                                                       v                              |
                               +---------------------------------------------------+  |
                               | Phase 6: Physical RADG (radg_node)                |  |
                               | evaluate_radg: {approve, replan}                  |  |
                               +---------------------------------------------------+  |
                                         |                                            |
                         [Any QoT_valid] | [All QoT_invalid]                          |
                                         v                                            |
                               +-------------------+                                  |
                               | Phase 7:          |                                  |
                               | Plan Synthesizer  |                                  |
                               | (Synthesis)       |                                  |
                               +-------------------+                                  |
                                         |                                            |
                                         v                                            |
                               +-------------------+                                  |
                               |        END        |                                  |
                               +-------------------+                                  |
                                                                                      |
                        +------------------------------------+                        |
                        | Phase 6: HITL Replan               |                        |
                        | State Suspended via interrupt()    |------------------------+
                        +------------------------------------+ (Constraint Relaxation)
```

---

## 4.3.2 Physical RADG Execution Mechanics

The core pre-deployment validation module governing physical safety is the **Physical RADG**, implemented across `src/core/radg.py` and `src/nodes/radg_node.py`.

### Pure Deterministic Decision Function

Adhering strictly to our architectural methodology, the decision logic in `evaluate_radg` is completely devoid of framework dependencies and language model calls:

```python
def evaluate_radg(qot_results: list[dict]) -> str:
    if not qot_results:
        return "replan"
    any_feasible = any(result.get("feasible", False) for result in qot_results)
    return "approve" if any_feasible else "replan"
```

The function accepts the list of physical evaluation dictionaries emitted by Phase 5. Each entry encapsulates the analytical results computed by the GN model for a candidate lightpath:
$$\mathcal{R}_{QoT} = \left\{ \left( \pi_k, \text{GSNR}_k, P_{rx, k}, \text{QoT}_{valid, k} \right) \mid k = 1, \dots, K \right\}$$

The gate applies the deterministic decision mapping:

$$D_{phys}\left( \mathcal{R}_{QoT} \right) = \begin{cases}
\text{approve} & \text{if } \exists k \in \{1, \dots, K\} \text{ such that } \text{QoT}_{valid, k} = 1 \\
\text{replan} & \text{if } \forall k \in \{1, \dots, K\}, \text{QoT}_{valid, k} = 0 \quad (\text{or } K = 0)
\end{cases}$$

### Conditional Routing Transitions

In `src/nodes/radg_node.py`, the execution branching is handled by `radg_route`:
- **Branch A (`approve`):** If at least one candidate lightpath meets or exceeds the required GSNR threshold and optical power budget, the physical risk is certified as zero ($UAR = 0.0\%$). Execution transitions directly to Phase 7 (`plan_synthesizer`) with **zero human intervention**.
- **Branch B (`replan`):** If all candidate paths violate physical feasibility (e.g., severe non-linear distortion over long-haul multi-span distances, or excessive attenuation across degraded fiber links), the system halts. The node invokes LangGraph's `interrupt()` primitive:

```python
replan_feedback = interrupt({
    "action": "replan",
    "reason": "All candidate paths failed physical QoT constraints.",
    "qot_results": qot_results,
    "prompt": "Please relax constraints (e.g., lower GSNR threshold, change bitrate, or remove node exclusions)."
})
```

Execution is suspended, saving the state to the checkpointer and presenting the operator with the calculated telemetry. When the operator responds with relaxed parameters, execution resumes and loops back to Phase 2 (`pddl_parser`).

---

## 4.3.3 Human-in-the-Loop Interaction and Re-Entry Protocols

Existing literature exhibits a polarization between fully autonomous systems that risk unfeasible deployments and rigid frameworks that interrupt operators for every transaction \cite{zhang_ai_2026} \cite{hachimi_flow-rule_2025}. Our architecture resolves this dichotomy through **Proportional HITL Engagement**: human operators are engaged if and only if evaluated risk signals exceed acceptable tolerances.

### Two Orthogonal Interruption Checkpoints

The architecture establishes two strictly decoupled HITL interruption checkpoints:

| Interruption Checkpoint | Trigger Condition | Operational Risk Managed | Available Operator Resumption Actions | Re-entry Target |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 3b (`hitl_clarify`)** | $U_{sem} > \tau_{sem}$ (Semantic ambiguity or CFG AST error) | Semantic Drift & Misunderstood Intents | (1) Disambiguate / clarify intent<br/>(2) Fast-track manual override (allowed if $v_{struct}=1$) | (1) $\to$ Phase 2 (`pddl_parser`)<br/>(2) $\to$ Phase 4 (`symbolic_solver`) |
| **Phase 6 (`radg_node`)** | $QoT_{valid} = 0$ for all candidate paths | Transmission Failure & Unfeasible Approvals | Relax physical margins, lower bitrate, or adjust routing exclusions | $\to$ Phase 2 (`pddl_parser`) |

### Fast-Track Manual Override Protocol

In Phase 3b, the system provides an engineered **Fast-Track Override**: if the PDDL specification is structurally valid ($v_{struct} = 1$) but the semantic divergence score is marginally elevated due to natural language phrasing variations ($d_{sem} > \tau_{sem}$), the operator can inspect $\mathcal{I}_{recon}$ and issue an affirmative approval command:
$$\text{resume\_payload} = \{ \text{'approved'}: \text{True} \}$$
Upon receiving approval, `hitl_clarify_route` bypasses PDDL re-parsing entirely and routes directly to Phase 4 (`symbolic_solver`), saving an entire LLM inference cycle ($~1,500$ tokens and $2.5\text{ s}$ of latency). If $v_{struct} = 0$, however, the override is blocked programmatically, forcing structural correction.

### Cycle Bounding and Prevention of Infinite Drift Loops

Multi-turn refinement in conversational AI frequently suffers from infinite negotiation loops \cite{wang_intent-driven_nodate}. To prevent non-terminating cycles, the orchestrator implements:
1. **Turn Counters:** `AgentState` tracks loop iterations ($N_{turns}$). If iterations exceed a configurable bound ($N_{max} = 3$), execution terminates with an explicit escalation exception.
2. **Reconciliation Invariants:** As demonstrated in Section 4.2.2, `intent_reconciler_node` computes an atomic `active_intent` on each turn. This eliminated BUG-009 (Monotonic Refinement Semantic Drift), where iterative corrections were mistakenly compared against the original turn $t_0$ intent, artificially inflating $U_{sem}$.

---

## 4.3.4 Plan Synthesis and Auditable Provisioning Trace

The terminal phase of the pipeline is executed by `plan_synthesizer_node` (`src/nodes/plan_synthesizer.py`). When the Physical RADG approves the verified candidate paths, the synthesizer constructs a comprehensive, auditable `PlanningReport`:

```markdown
# Optical Lightpath Planning Report

## Executive Summary
- Operational Decision: APPROVED
- Routing Status: Physically feasible lightpath identified.
- Safety Verification: Pre-deployment RADGs certified (UAR = 0.0%).

## Intent Traceability
- Active Intent: "Route traffic from Hamburg to Munich avoiding Frankfurt."
- Ingress Node: Hamburg (node_3)
- Egress Node: Munich (node_7)

## Primary Allocated Lightpath
- Path: Hamburg -> Bremen -> Hannover -> Leipzig -> Nuremberg -> Munich
- Physical Span Length: 1,029.8 km
- Active Channels: 100 (C-band 50 GHz grid)
- Computed GSNR: 18.42 dB (Threshold: 15.20 dB, Margin: +3.22 dB)
- Received Optical Power: -13.45 dBm (Sensitivity: -18.00 dBm)
- Status: FEASIBLE

## Secondary Protection Lightpath
- Path: Hamburg -> Berlin -> Leipzig -> Nuremberg -> Munich
- Physical Span Length: 1,019.1 km
- Computed GSNR: 17.85 dB (Margin: +2.65 dB)
- Status: FEASIBLE

## Auditable Decision Metrics
- Structural AST Validation (v_struct): 1 (PASS)
- Semantic Divergence (d_sem): 0.08
- Composite Semantic Uncertainty (U_sem): 0.08 <= 0.30 (PASS)
- Human Interruptions (N_hitl): 0
- Total Cumulative Token Consumption: 2,415 tokens
```

The report serves as a cryptographically auditable log for network operators. Crucially, the planning report encapsulates the machine-readable provisioning payload formatted for direct dispatch to the optical controller (e.g., RESTConf `POST /onc/nbi/connection` or OpenConfig NETCONF RPCs), completing the pre-deployment intent translation loop.

---

## 4.3.5 Verification of the Seven Canonical Execution Paths

To guarantee that the orchestrated state machine handles all operational contingencies deterministically, the pipeline was subjected to a comprehensive verification test suite implemented in `tests/unit/test_e2e_pipeline_flow.py`.

The test harness executes the fully compiled StateGraph with an `InMemorySaver` checkpointer, mocking the LLM via context-aware dispatchers while exercising the genuine `networkx` GraphRAG layer, CFG PDDL validator, Yen's symbolic solver, and GN-model physics engine.

Across 715 lines of test assertions, seven canonical execution paths were verified:

```
+-----------------------------------------------------------------------------------------------------------------------+
| ID | Canonical Execution Path         | Trigger Condition               | Trajectory Sequence                         |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P1 | Single-Pass Auto-Approve         | U_sem <= tau_sem, QoT_valid = 1 | Ingest -> Parse -> RP -> Gate -> Solver ->  |
|    | (Happy Path)                     | (Unambiguous, physically valid) | QoT -> RADG -> Synth -> END (0 HITL)        |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P2 | Semantic RADG Clarification &    | U_sem > tau_sem (d_sem = 0.85)  | Ingest -> Parse -> RP -> Gate -> Clarify    |
|    | Multi-Turn Refinement            | (Missing constraints/ambiguity) | [HITL 1] -> Reconcile -> Parse -> Gate ->   |
|    |                                  |                                 | Solver -> QoT -> RADG -> Synth -> END       |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P3 | Semantic RADG Fast-Track         | U_sem > tau_sem, v_struct = 1   | Ingest -> Parse -> RP -> Gate -> Clarify    |
|    | Manual Override                  | (Operator forces approval)      | [HITL 1: Approved] -> Solver -> QoT ->      |
|    |                                  |                                 | RADG -> Synth -> END                        |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P4 | Physical RADG Replan             | U_sem <= tau_sem, QoT_valid = 0 | Ingest -> Parse -> RP -> Gate -> Solver ->  |
|    | & Constraint Relaxation          | (Physics failure, e.g. GSNR<th) | QoT -> RADG [HITL 1] -> Reconcile ->        |
|    |                                  |                                 | Parse -> Solver -> QoT -> RADG -> Synth     |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P5 | Complex Topological Constraints  | Explicit negative constraints   | Ingest -> Parse -> Gate -> Solver (Prunes   |
|    | (Avoid-Links & Max-Hops)         | (e.g. avoid-link, max-hops)     | excluded links) -> QoT -> RADG -> Synth     |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P6 | Topology Edge Cases & Disconnect | Partitioned or unreachable node | Ingest -> Parse -> Gate -> Solver (Returns  |
|    | Graceful Degradation             | pair in graph                   | empty paths) -> QoT -> RADG [HITL Replan]   |
+----+----------------------------------+---------------------------------+---------------------------------------------+
| P7 | Multi-Interruption Checkpointer  | Sequential semantic ambiguity   | Ingest -> Parse -> Clarify [HITL 1] ->      |
|    | Persistence Across Session       | followed by physical infeas.    | Reconcile -> Solver -> QoT -> RADG [HITL 2] |
|    |                                  |                                 | -> Reconcile -> Parse -> Synth -> END       |
+----+----------------------------------+---------------------------------+---------------------------------------------+
```

### Detailed Path Analysis

1. **Path 1 (Happy Path / Single-Pass Autonomous Pass):** Represents nominal operations. When an operator submits a clear intent with physically viable endpoints, the Semantic RADG clears $U_{sem} \le 0.30$ and the Physical RADG evaluates $\text{QoT}_{valid} = 1$. The entire workflow completes from natural language input to synthesized provisioning report in a single pass with **zero human interruptions** ($N_{hitl} = 0$), validating the primary optimization objective of reducing operator cognitive fatigue.
2. **Path 2 (Semantic Clarification Loop):** When an input is underspecified (e.g., omitting ingress or egress nodes), the Semantic RADG intercepts the ambiguity ($U_{sem} = 0.85 > 0.30$), routing to `hitl_clarify`. The operator supplies the missing endpoint via `Command(resume=...)`. The reconciler updates `active_intent`, the PDDL parser regenerates formal rules, and the pipeline executes to successful completion.
3. **Path 3 (Fast-Track Manual Override):** Verifies the bypass route: when an operator confirms that the LLM's natural language reconstruction $\mathcal{I}_{recon}$ correctly captures operational intent despite minor scoring divergence, the operator issues an approval command. If $v_{struct} = 1$, execution immediately skips reparsing and engages the symbolic solver directly.
4. **Path 4 (Physical Replan Loop):** When requested lightpaths cross excessive span distances without adequate optical amplification, the GN-model reports negative GSNR margins. The Physical RADG suspends execution at Phase 6. The operator relaxes the required bitrate or lowers the target GSNR margin. The update loops back to Phase 2, yielding an approved alternative configuration.
5. **Path 5 (Topological Constraint Enforcement):** Verifies that negative routing constraints (`avoid-node`, `avoid-link`, `max-hops`) parsed into PDDL are strictly honored by the symbolic solver, preventing traffic from traversing excluded core nodes.
6. **Path 6 (Topological Disconnection Handling):** Verifies graceful failure handling: if an intent requests a route between disconnected topological partitions or targets non-existent nodes, the symbolic solver produces an empty candidate set ($K = 0$). The Physical RADG catches the empty set, preventing null pointer crashes, and prompts the operator to select viable endpoints.
7. **Path 7 (Multi-Interruption Persistence):** Verifies state persistence under compound stress: an intent triggers a Phase 3b semantic clarification, is resumed, and subsequently triggers a Phase 6 physical replanning interruption. The LangGraph checkpointer maintains thread integrity across multiple suspensions and resumptions without data corruption.

All 321 unit tests across these execution flows pass consistently under Strict TDD, confirming the robust operational grounding of the neurosymbolic architecture.

---

## Drafting Recommendations & Figure Placement

> [!NOTE]
> **Figure 4.3 Placement:** Detailed state machine diagram illustrating the seven canonical execution paths of the LangGraph StateGraph, highlighting the conditional branching at `semantic_gate` and `radg`, the two `interrupt()` suspension checkpoints, and the state-preserving checkpointer loopbacks.
> - **Artifact Path:** `figs_NPImp/src/diagrams/langgraph_state_machine.drawio`
> - **Semantic Name:** `langgraph_state_machine`
> - **LaTeX Figure Reference:** `Figure~\ref{fig:langgraph_state_machine}`
> - **Implementation Grounding:** Verified against `src/core/graph.py`, `src/nodes/radg_node.py`, `src/nodes/reverse_prompt.py`, and `tests/unit/test_e2e_pipeline_flow.py`.
