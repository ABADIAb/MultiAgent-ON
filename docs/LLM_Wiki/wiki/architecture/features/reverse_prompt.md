---
title: "Feature: Reverse Prompting HITL Node"
date: 2026-07-31
tags: [feature, hitl, reverse-prompting, interrupt, semantic-gate, phase3, nodes]
status: active
---

# Feature: Reverse Prompting HITL Node

## 1. Architecture Placement
**Phase 3: Semantic Gate & HITL ($U_{sem}$)** | [[Architecture_v5]]

Implements the formal Human-in-the-Loop convergence mechanism that prevents **semantic drift** in intent refinement. Rather than showing the operator raw PDDL (opaque, error-prone), the system translates PDDL back to natural language and asks the operator to approve exactly what the system will execute. This mathematically bounds the operator's approval to the logical constraints the solver will use.

## 2. Associated Files
- **Node**: [src/nodes/reverse_prompt.py](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) — `reverse_prompt_node(state) -> dict`
- **Router**: [src/nodes/reverse_prompt.py](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) — `hitl_route(state) -> str`
- **State fields written**: `hitl_reconstruction: str | None`, `hitl_approved: bool | None`, `error_context: str | None`
- **Tests**: [tests/unit/test_pipeline_nodes.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pipeline_nodes.py)

## 3. How it Works
1. Calls the LLM with `REVERSE_PROMPT_SYSTEM` — instructs it to translate the PDDL constraints into a plain English paragraph starting with "I understand you want to..."
2. Presents the reconstruction to the operator via `interrupt()` — LangGraph pauses the graph here, waiting for the CLI/UI to resume it.
3. The operator's response (`approve` / `refine` / `reject`) resumes the graph:
   - `approve` → `hitl_approved=True`, proceeds to Phase 4
   - `refine` → `hitl_approved=False`, `error_context=feedback`, routes back to `pddl_parser`
   - `reject` → `hitl_approved=False`, routes to `__end__`

### HITL Routing Function (`hitl_route`)
```python
def hitl_route(state: AgentState) -> str:
    if state["hitl_approved"] is True:
        return "symbolic_solver"
    if state["hitl_approved"] is False and state.get("error_context"):
        return "pddl_parser"   # refinement loop
    return "__end__"           # rejected
```

## 4. V4 vs V5 HITL Strategy
| Version | HITL Trigger |
|---------|-------------|
| V4 | Always-on — every intent triggers `interrupt()` |
| V5 (planned) | Risk-adaptive — HITL triggered only when $U_{sem}$ is high (Sprint 3, Exp 3.2) |

Currently (end of Sprint 2), the node still uses always-on HITL. The RADG semantic gate (which will make this conditional) is the key Sprint 3 deliverable.

## 5. LangGraph interrupt() Pattern
`interrupt()` requires a **checkpointer** to be set. Without a checkpointer, `interrupt()` raises an error. The `compile_graph()` function in `src/core/graph.py` accepts an optional checkpointer; `main.py` passes `InMemorySaver()` for development.

```python
# Pattern used:
response = interrupt({
    "reconstruction": reconstruction,
    "options": ["approve", "refine", "reject"],
    "message": "Please review the parsed constraints and choose an action.",
})
```

## 6. How to Test
```bash
uv run pytest tests/unit/test_pipeline_nodes.py -k "reverse_prompt" -v
```

## 7. Cross-References
- [[Architecture_v5]] — Phase 3 description and V5 conditional HITL goal
- [[architecture/features/pddl_parser]] — Produces PDDL consumed here; receives operator feedback on refine
- [[architecture/features/symbolic_solver]] — Phase 4 executed on `approve`
- [[architecture/features/pipeline_graph]] — `hitl_route` is registered as a conditional edge
