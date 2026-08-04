---
title: "Feature: LangGraph Pipeline & AgentState"
date: 2026-07-31
tags: [feature, langgraph, state, graph, pipeline, core, sprint3]
status: active
---

# Feature: LangGraph Pipeline & AgentState

## 1. Architecture Placement
**Pipeline Wiring (All Phases)** | [[Architecture_v5]]

This feature defines the backbone of the entire orchestrator: the LangGraph `StateGraph` and the shared `AgentState`. Every pipeline node communicates exclusively through `AgentState` — there are no direct function calls between nodes.

## 2. Associated Files
- **Graph**: [src/core/graph.py](file:///home/felipeab/MultiAgentON/src/core/graph.py) — `build_graph()`, `compile_graph(checkpointer)`
- **State**: [src/core/state.py](file:///home/felipeab/MultiAgentON/src/core/state.py) — `AgentState` TypedDict + topology domain models
- **Entry point**: [src/main.py](file:///home/felipeab/MultiAgentON/src/main.py) — CLI runner with HITL interrupt/resume loop
- **Tests**: [tests/unit/test_graph_v4.py](file:///home/felipeab/MultiAgentON/tests/unit/test_graph_v4.py), [tests/unit/test_state_v4.py](file:///home/felipeab/MultiAgentON/tests/unit/test_state_v4.py)

## 3. AgentState Schema

```python
class AgentState(TypedDict):
    # Core message history (append-only via operator.add reducer)
    messages: Annotated[list, operator.add]

    # Phase 1 — Intent Ingest
    enriched_intent: str | None

    # Phase 2 — PDDL Parser
    pddl_constraints: str | None
    pddl_valid: bool | None
    pddl_parsed_constraints: dict | None  # structured: source, dest, avoid_links, max_hops

    # Phase 3 — HITL
    hitl_reconstruction: str | None
    hitl_approved: bool | None

    # Phase 4 — Symbolic Solver (topology input)
    topology_snapshot: TopologySnapshot | None
    candidate_paths: list | None

    # Phase 5 — QoT Validation
    qot_results: list | None

    # Phase 7 — Plan Synthesizer
    planning_report: str | None

    # Error tracking
    error_context: str | None
```

## 4. Current Graph Topology (V4 — Sprint 2 complete)

```
START → intent_ingest → pddl_parser → reverse_prompt
    ├─ [approve]  → symbolic_solver → qot_validation → plan_synthesizer → END
    ├─ [refine]   → pddl_parser (loop)
    └─ [reject]   → END
```

## 5. V5 Target Graph Topology (Sprint 3)

```
START → intent_ingest → pddl_parser → semantic_gate
    ├─ [U_sem High]  → reverse_prompt (HITL clarify) → pddl_parser (loop)
    └─ [U_sem Low]   → symbolic_solver → qot_validation → physical_risk_gate (RADG)
                              ├─ [Valid]    → plan_synthesizer → provisioning → END
                              └─ [Invalid]  → reverse_prompt (HITL replan) → pddl_parser (loop)
```

Key Sprint 3 additions to `graph.py`:
- `src/nodes/semantic_gate_node.py` — Phase 3 conditional HITL routing
- `src/nodes/radg_node.py` — Phase 6 physical risk gate
- `src/core/radg.py` — Decision function `D(U_sem, QoT_valid)`

## 6. Checkpointer & HITL Pattern
`compile_graph(checkpointer=InMemorySaver())` is required for `interrupt()` to work. Without a checkpointer, `interrupt()` in `reverse_prompt_node` will raise a `RuntimeError`.

For persistence across sessions, swap `InMemorySaver` for `SqliteSaver`.

## 7. How to Test
```bash
uv run pytest tests/unit/test_graph_v4.py tests/unit/test_state_v4.py -v
```

## 8. Cross-References
- [[Architecture_v5]] — Full pipeline diagram and phase descriptions
- [[features/reverse_prompt]] — Uses `interrupt()` which requires checkpointer
- [[features/symbolic_solver]] — Wired directly into StateGraph from `src/core/`
- [[experiments/MVP_Roadmap]] — Sprint 3 Exp 3.0: LangGraph assembly
