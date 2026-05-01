---
name: langgraph-expert
description: Protocol for enforcing documentation lookups before writing LangGraph/LangChain code.
triggers:
  - "langgraph"
  - "langchain"
  - "agent"
  - "graph"
  - "orchestrator"
  - "src/agents"
  - "src/graph.py"
---

# LangGraph Expert Protocol

As Archimedes, you must write production-ready, master's level code for the optical network orchestrator. LangGraph and LangChain APIs evolve rapidly. To prevent hallucinations and syntax errors, you MUST follow this protocol.

## 1. Documentation Lookup Rule
BEFORE writing or modifying any significant LangGraph or LangChain code (such as defining `StateGraph`, `ToolNode`, conditionals, or graph compilation), you MUST:
1. Call the `mcp_context7_resolve-library-id` tool for "LangGraph" or "LangChain" (if you don't already have the exact ID).
2. Call the `mcp_context7_query-docs` tool to verify the specific syntax you intend to use (e.g., "How to define a conditional edge in LangGraph", "How to use ToolNode").

## 2. Prohibition on Guessing
- DO NOT rely solely on your training data for LangGraph syntax. The API has changed from `v0.1` to `v0.2`, and guessing will result in broken code.
- If the Context7 search fails or doesn't provide the answer, inform the user that you need to find the correct documentation before proceeding.

## 3. Implementation Standards
- Use typed `State` definitions (via `TypedDict` or `Pydantic`).
- Separate tools into deterministic Python functions with `@tool`.
- The LLM should only act as a reasoning engine, delegating physical operations to tools.
