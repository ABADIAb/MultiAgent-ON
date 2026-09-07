---
title: "Feature: Semantic Gate ($U_{sem}$)"
date: 2026-09-01
tags: [feature, semantic-gate, hitl, phase3, nodes, core]
status: active
---

# Feature: Semantic Gate ($U_{sem}$)

## 1. Architecture Placement
**Phase 3: Semantic Gate** | [[Architecture_v5]]

The Semantic Gate implements the fail-fast Semantic Uncertainty mechanism from Architecture V5. It evaluates the clarity of the operator's intent *before* running the expensive Symbolic Solver and QoT physics engine. If the intent is ambiguous or structurally invalid, it routes to [[architecture/features/reverse_prompt]] (`hitl_clarify`) for human intervention. If clear ($U_{sem} \le \tau_{sem}$), it passes autonomously to the Symbolic Solver with **0 human interruptions**.

## 2. Overview
The gate computes a Semantic Uncertainty score ($U_{sem}$) based on two layers of validation:
- **Layer 1 (Structural)**: Did the PDDL string pass Context-Free Grammar (CFG) validation? ($v_{struct} \in \{0, 1\}$)
- **Layer 2 (Semantic)**: How much does the system's reverse-prompt reconstruction diverge from the original natural language intent? ($d_{sem} \in [0.0, 1.0]$)

If $U_{sem} \le \tau_{sem}$ (default $\tau_{sem} = 0.3$), the gate passes (`usem_passed=True`) and routes directly to `"symbolic_solver"`. Otherwise (`usem_passed=False`), it routes to `"hitl_clarify"` (Phase 3b).

## 3. How it Works
The logic is implemented as a piecewise mathematical formula in `src/core/semantic_gate.py`:
- If `v_struct == False` (structural failure), $U_{sem} = 1.0$.
- If `v_struct == True`, $U_{sem} = d_{sem}$ (where $d_{sem}$ is the semantic divergence score in $[0.0, 1.0]$).

The LangGraph node `semantic_gate_node.py` manages the LLM call to compute $d_{sem}$. It provides the original intent and the automated reverse-prompt reconstruction to a judge LLM, asking for a divergence score between 0.0 (perfect agreement) and 1.0 (complete divergence). 

*Conditional Routing (`semantic_gate_route`)*:
- `usem_passed is True` $\implies$ `"symbolic_solver"` (Phase 4)
- `usem_passed is False` or `None` $\implies$ `"hitl_clarify"` (Phase 3b)

## 4. Associated Files
- **Core Logic**: [src/core/semantic_gate.py](file:///home/felipeab/MultiAgentON/src/core/semantic_gate.py) — `compute_usem()`, `evaluate_semantic_gate()`
- **LangGraph Node**: [src/nodes/semantic_gate_node.py](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py) — `semantic_gate_node()`, `semantic_gate_route()`
- **Tests**: [tests/unit/test_semantic_gate.py](file:///home/felipeab/MultiAgentON/tests/unit/test_semantic_gate.py), [tests/unit/test_graph_v5.py](file:///home/felipeab/MultiAgentON/tests/unit/test_graph_v5.py)

## 5. Inputs / Outputs
- **Input (State)**: `pddl_valid` (bool), `enriched_intent` (str), `hitl_reconstruction` (str).
- **Output (State)**: `usem_score` (float), `usem_passed` (bool), `messages` (AIMessage with trace).

## 6. How to Test
```bash
uv run pytest tests/unit/test_semantic_gate.py -v
```

## 7. Cross-References
- [[Architecture_v5]] — System architecture and Phase 3 description
- [[architecture/features/reverse_prompt]] — Automated reverse prompting (Phase 3a) and HITL clarify node (Phase 3b)
- [[architecture/features/symbolic_solver]] — Executed autonomously if the gate passes
- [[architecture/features/pipeline_graph]] — Contains the conditional routing logic in StateGraph
