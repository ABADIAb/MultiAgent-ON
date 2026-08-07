---
title: "Feature: PDDL Parser & CFG Validator"
date: 2026-08-07
tags: [feature, pddl, parser, validator, llm, phase2, core, nodes]
status: active
---

# Feature: PDDL Parser & CFG Validator

## 1. Architecture Placement
**Phase 2: PDDL Parsing (CFG Validated)** | [[Architecture_v5]]

Implements the neurosymbolic "LLM as translator" principle: the LLM acts ONLY as a natural language → formal PDDL converter. It does NOT decide routes or compute physics. A deterministic CFG regex validator then checks structural correctness, catching the most common LLM hallucination patterns before any downstream computation.

## 2. Associated Files
- **Node**: [src/nodes/pddl_parser.py](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) — `pddl_parser_node(state) -> dict`
- **Validator**: [src/core/pddl_validator.py](file:///home/felipeab/MultiAgentON/src/core/pddl_validator.py) — `validate_pddl_syntax()`, `extract_pddl_sections()`
- **State fields written**: `pddl_constraints: str | None`, `pddl_valid: bool | None`, `error_context: str | None`
- **Tests**: [tests/unit/test_pipeline_nodes.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pipeline_nodes.py), [tests/unit/test_pddl_validator.py](file:///home/felipeab/MultiAgentON/tests/unit/test_pddl_validator.py)

## 3. PDDL Subset Used
The system uses a simplified PDDL problem domain for optical routing:

```pddl
(define (problem <name>)
  (:domain optical-network)
  (:objects <nodes> - node)
  (:init <topology predicates: (connected A B), (link-active A B), ...>)
  (:goal
    (and
      (route <source> <target>)
      (min-gsnr <value>)      ; optional
      (avoid-link <src> <dst>) ; optional
      (max-hops <n>)           ; optional
    )
  )
)
```

## 4. How it Works
1. Reads `enriched_intent` (which contains the dynamically injected `Topology Context:` from Phase 1 Optical RAG) from state. If `error_context` exists (refinement loop), appends operator feedback to the prompt.
2. Calls Kimi LLM with `PDDL_SYSTEM_PROMPT` — instructs the model to use the topology provided dynamically in `enriched_intent` and output ONLY PDDL, no markdown.
3. Strips markdown code fences if the LLM wraps the output (common LLM behavior).
4. Validates via `validate_pddl_syntax()` — checks: balanced parentheses, `(define ...)` wrapper, and presence of `:domain`, `:objects`, `:init`, `:goal` sections.
5. Returns `pddl_valid=True/False` and `error_context` with any CFG error messages.

### Refinement Loop Support
When the Reverse Prompt node returns `action="refine"`, the operator's feedback is stored in `error_context`. On the next call, `pddl_parser_node` detects the presence of both `pddl_constraints` and `error_context` and includes both the previous PDDL and the feedback in the LLM prompt — enabling convergent iterative refinement.

## 5. CFG Validator Details (`src/core/pddl_validator.py`)
- **Layer 1 (Structural)**: Feeds into $U_{sem}$ Layer 1 check
- Checks performed:
  1. Non-empty string
  2. Balanced parentheses
  3. `(define (problem <name>)...)` wrapper
  4. All required sections: `:domain`, `:objects`, `:init`, `:goal`
- Design: permissive on unknown sections (`:constraints`, `:metric`) for domain extensibility

## 6. How to Test
```bash
uv run pytest tests/unit/test_pddl_validator.py tests/unit/test_pipeline_nodes.py::TestPDDLParserNode -v
```

## 7. Cross-References
- [[Architecture_v5]] — Phase 2 description
- [[architecture/features/intent_ingest]] — Produces `enriched_intent` consumed here
- [[architecture/features/reverse_prompt]] — Phase 3: validates semantic correctness after CFG validation
- [[architecture/features/symbolic_solver]] — Consumes `pddl_constraints` for path search
