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
   - `approve` → `hitl_approved=True`, graph continues to Semantic Gate for $U_{sem}$ evaluation
   - `refine` → `hitl_approved=False`, `error_context=feedback`, graph continues to Semantic Gate which will route back to `pddl_parser`

In V5, the 3-way routing logic has been removed from this node. The `reverse_prompt` node purely focuses on reconstruction and the interrupt checkpoint, delegating routing decisions to the downstream `semantic_gate`.

## 4. V4 vs V5 HITL Strategy
| Version | HITL Trigger |
|---------|-------------|
| V4 | Always-on, 3-way routing (approve/refine/reject) directly in this node |
| V5 | Simplified schema (approve/refine). Routing is delegated to the Semantic Gate (Phase 3). |

In Sprint 3, the `hitl_route` conditional edge was replaced by `semantic_gate_route`.

## 5. LangGraph interrupt() Pattern
`interrupt()` requires a **checkpointer** to be set. Without a checkpointer, `interrupt()` raises an error. The `compile_graph()` function in `src/core/graph.py` accepts an optional checkpointer; `main.py` passes `InMemorySaver()` for development.

```python
# Pattern used:
response = interrupt({
    "reconstruction": reconstruction,
    "options": ["approve", "refine"],
    "message": "Please review my understanding of your request. If accurate, approve to proceed. If not, choose 'refine' and provide feedback.",
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
