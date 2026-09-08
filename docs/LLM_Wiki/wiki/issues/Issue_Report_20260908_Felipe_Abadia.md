---
title: "Issue Report 2026-09-08"
date: 2026-09-08
tags: [issues, semantic-gate, reverse-prompt, hitl, refinement, token-budget, bug-009]
status: active
---

# Issue Report

---

## Student Name:
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Current Stage:
> Execution / Pipeline Hardening & Thesis Chapter 3 Refinement

## Date:
2026-09-08

---

### Solved Issues

#### Solved Issue 1: Monotonic Refinement Semantic Drift in Semantic Gate ([[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift|BUG-009]])

- **Original issue:** During multi-turn Human-in-the-Loop (HITL) refinement (Phase 3b or Phase 6), when an operator provided clarifications altering, relaxing, or adding constraints (e.g., relaxing GSNR threshold or changing target nodes), $U_{sem}$ monotonically increased on subsequent passes ($U_{sem} > \tau_{sem}$), indefinitely triggering the clarification `interrupt()`.
- **What was tried:** Traced state transformations across `src/nodes/pddl_parser.py` and `src/nodes/semantic_gate_node.py`. Diagnosed that `enriched_intent` was static at $k=0$, `error_context` was cleared on Phase 2 re-parsing, and the LLM agreement judge prompt explicitly penalized any modified or added constraints ("0.6 = Some constraints are missing or changed") as hallucinated divergence.
- **Resolution / outcome:**
  1. Extended `AgentState` in `src/core/state.py` with `refinement_history: list[str] | None` and `refinement_count: int | None`.
  2. Injected full `refinement_history` into `pddl_parser_node` prompt context to ensure updated constraints reflect operator directions.
  3. Formulated effective reference intent $\mathcal{I}_{\text{eff}}^{(k)} = \mathcal{I}_{NL} \oplus \mathcal{H}_{refine}$ in `semantic_gate_node.py`.
  4. Calibrated `_AGREEMENT_SYSTEM_PROMPT` so the evaluator LLM treats faithful incorporation of operator feedback as high semantic agreement ($d_{sem} \to 0.0$).

---

#### Solved Issue 2: Unbounded Clarification Loops and Context Window Exhaustion

- **Original issue:** Without an explicit convergence guard or iteration ceiling, repeated non-convergent operator feedback loops risked unbounded execution, exhausting token budgets and polluting LLM context windows.
- **What was tried:** Analyzed LangGraph execution loops and HITL state management. Determined that when an operator fails to resolve semantic ambiguity after a set number of turns, human intervention should be formally aborted rather than continuing in an indefinite spin.
- **Resolution / outcome:**
  1. Enforced a hard upper bound $N_{max} = 3$ in `src/nodes/reverse_prompt.py` (`MAX_REFINEMENTS = 3`) and Phase 6 RADG replan.
  2. Upon reaching $N_{max}$, the orchestrator triggers an explicit cancellation `interrupt(status="aborted")` detailing the reason (preventing context window saturation and preserving token budget).
  3. Updated `hitl_clarify_route` to gracefully terminate execution at `__end__` when aborted or cancelled.
  4. Validated with dedicated unit and end-to-end tests (`tests/unit/test_semantic_gate.py`, `tests/unit/test_pipeline_nodes.py`, `tests/unit/test_e2e_pipeline_flow.py`).

---

#### Solved Issue 3: Stale Initial Intent and Raw Subtopology Context Dump in Planning Report ([[experiments/bugs/bug010_Planning_Report_Intent_and_Topology|BUG-010]])

- **Original issue:** The final Planning Report synthesized in Phase 7 (`plan_synthesizer_node`) printed the static initial intent from $k=0$, ignoring operator clarifications and constraint relaxations submitted during HITL interrupts. Additionally, it printed the duplicate prefix `"Intent: Intent:"`, dumped the raw $k$-hop subtopology JSON text into the report body, and lacked visual topological representation of the lightpath.
- **What was tried:** Traced state transformations in `src/nodes/plan_synthesizer.py`. Diagnosed that `plan_synthesizer_node` extracted the intent solely from `enriched_intent` without stripping topology context and never read `refinement_history` or `refinement_count`.
- **Resolution / outcome:**
  1. Implemented `_extract_clean_base_intent` to prioritize clean human messages and strip `\nTopology Context:` and redundant `"Intent: "` prefixes.
  2. Integrated `refinement_history` and `refinement_count` into the report, enumerating applied refinements turn-by-turn and presenting the synthesized **Active Operational Intent**.
  3. Implemented `_format_horizontal_path` to correlate the selected lightpath with `candidate_paths` and render a horizontal ASCII/Unicode path graph with span distances (km), inline EDFA counts, cumulative metrics, and hop-by-hop link breakdowns.
  4. Structured the report into 5 executive Markdown sections and added 3 regression tests in `TestPlanSynthesizerNode` ([`tests/unit/test_pipeline_nodes.py`](file:///home/felipeab/MultiAgentON/tests/unit/test_pipeline_nodes.py)).

---

### Pending Issues

> None. All detected pipeline edge cases, convergence bounds, auditable report outputs, and thesis draft synchronizations are verified and passing tests.

---

### Additional Notes

The mathematical framework and convergence guarantees for bounded refinement and effective intent have been integrated directly into:
- Thesis Section 3.2.3: Extended State Vector $\mathcal{S}_{\text{state}}$ ([[thesis_drafts/3_SystemModel/3_2_Conceptual_Framework]])
- Thesis Section 3.5.2: Effective Reference Intent Formulation ([[thesis_drafts/3_SystemModel/3_5_Formal_HITL_Reverse_Prompting]])
- Thesis Section 3.5.3: Bounded Refinement and Token Protection ([[thesis_drafts/3_SystemModel/3_5_Formal_HITL_Reverse_Prompting]])
- Overleaf Consolidated Document: [[thesis_drafts/3_SystemModel/chapter_3_system_model.txt]]
