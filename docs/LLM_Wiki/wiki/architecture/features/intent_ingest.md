---
title: "Feature: Intent Ingest Node"
date: 2026-07-31
tags: [feature, intent, ingest, llm, phase1, nodes]
status: active
---

# Feature: Intent Ingest Node

## 1. Architecture Placement
**Phase 1: Intent Ingestion & Optical RAG** | [[Architecture_v5]]

Entry point of the neurosymbolic pipeline. The operator submits a natural language request; this node parses it into a structured `IntentSummary` and populates `enriched_intent` in the shared `AgentState`. Future work: add Optical RAG enrichment (ITU-T spec lookup, transponder datasheets) before the LLM call.

## 2. Associated Files
- **Node**: [src/nodes/intent_ingest.py](file:///home/felipeab/MultiAgentON/src/nodes/intent_ingest.py) — `intent_ingest_node(state) -> dict`
- **State field written**: `enriched_intent: str | None`
- **Tests**: [tests/unit/test_intent_ingest.py](file:///home/felipeab/MultiAgentON/tests/unit/test_intent_ingest.py)

## 3. How it Works
1. Extracts the latest `HumanMessage` from `state["messages"]`.
2. Calls the Kimi LLM with `with_structured_output(IntentSummary)` — guarantees a Pydantic-validated response with `summary`, `source_node`, and `target_node`.
3. Builds an `enriched_intent` string in the format: `"Intent: <summary> | Source: <node> | Target: <node>"`.
4. Returns a partial state update with `enriched_intent` and an `AIMessage` named `"intent_ingest"`.

### IntentSummary Schema
```python
class IntentSummary(BaseModel):
    summary: str          # One-sentence intent description
    source_node: str | None  # e.g., "Milano-A"
    target_node: str | None  # e.g., "Milano-D"
```

## 4. LLM Usage
- **Model**: Kimi (`moonshot-v1-8k`) via `langchain_openai.ChatOpenAI`
- **Pattern**: `structured_output` — no free-form parsing required
- **System prompt**: Hardcoded in `INTENT_SYSTEM_PROMPT` — includes testbed topology description (4-node linear: Milano-A ↔ B ↔ C ↔ D)

## 5. Known Limitations / Sprint 3 TODOs
- **No Optical RAG enrichment yet.** The architecture specifies that ITU-T standards and transponder specs should be injected into the prompt before LLM processing. Currently, only the raw intent is sent.
- **Fixed topology description.** The testbed topology is hardcoded in the system prompt. After Exp 1.3 (TestbedClient), this should pull from the live topology.

## 6. How to Test
```bash
uv run pytest tests/unit/test_intent_ingest.py -v
```

## 7. Cross-References
- [[Architecture_v5]] — Phase 1 description
- [[features/pddl_parser]] — Phase 2 consumes `enriched_intent`
- [[features/pipeline_graph]] — Graph wiring
