---
name: langgraph-expert
description: >
  Protocol for enforcing documentation lookups before writing LangGraph/LangChain code.
  Trigger: "langgraph", "langchain", "agent", "graph", "orchestrator", "src/agents", "src/graph.py"
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- When writing or modifying LangGraph state machines (`StateGraph`).
- When implementing LangChain agents, tools, or runnables.
- When structuring orchestrator logic.

## Critical Patterns

- **Documentation Lookup Mandatory**: BEFORE writing significant LangGraph/LangChain code, you MUST use `mcp_context7_resolve-library-id` and `mcp_context7_query-docs` tools to verify syntax.
- **No Guessing**: The LangGraph API changes rapidly. Guessing syntax based on training data will result in broken code. 
- **Typed State**: Always use `TypedDict` or `Pydantic` for `State` definitions.
- **Deterministic Tools**: Separate physical actions into deterministic Python `@tool` functions. The LLM only acts as a reasoning engine, not a calculator.

## Code Examples

**Example State Definition:**
```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    current_path: list[str]
    is_feasible: bool
```

## Commands

No bash commands. Use the `mcp_context7` tools for API lookups.

## Resources

- None currently required. Use external documentation via tools.
