# Project Skills Catalog

Technical capabilities and automated protocols for the MultiAgentON orchestrator.

## Core Skills

| Skill | Trigger | Description | Path |
|-------|---------|-------------|------|
| `wiki-protocol` | `docs/LLM_Wiki`, `ingest` | 2-layer Wiki management (Raw/Wiki), indexing, and session debriefs. | [.agent/skills/wiki-protocol/SKILL.md](skills/wiki-protocol/SKILL.md) |
| `langgraph-expert` | `langgraph`, `src/graph.py` | Strict documentation-first protocol for LangGraph/LangChain development. | [.agent/skills/langgraph-expert/SKILL.md](skills/langgraph-expert/SKILL.md) |
| `pdf-ingest` | `extract pdf`, `ingest pdf` | High-fidelity PDF to Markdown extraction using `pymupdf4llm`. | [.agent/skills/pdf-ingest/SKILL.md](skills/pdf-ingest/SKILL.md) |

---

> [!NOTE]
> This catalog separates technical tools from the agent's persona. For high-level interaction protocols and persona details, refer to [[AGENTS.md]].
