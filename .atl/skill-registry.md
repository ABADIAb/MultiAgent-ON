# Skill Registry

**Delegator use only.**

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| `docs/LLM_Wiki`, `ingest` | `wiki-protocol` | `/home/felipeab/MultiAgentON/.agent/skills/wiki-protocol/SKILL.md` |
| `langgraph`, `src/graph.py` | `langgraph-expert` | `/home/felipeab/MultiAgentON/.agent/skills/langgraph-expert/SKILL.md` |
| `extract pdf`, `ingest pdf` | `pdf-ingest` | `/home/felipeab/MultiAgentON/.agent/skills/pdf-ingest/SKILL.md` |

## Compact Rules

### wiki-protocol
- Every note in `wiki/` MUST have YAML frontmatter (`title`, `date`, `tags`, `status`).
- Maintain report continuity by reading previous reports before creating new ones.
- Aggressively interlink concepts using `[[wikilinks]]`.

### langgraph-expert
- Documentation-first: query Context7 BEFORE writing LangGraph code.
- No guessing on syntax; the API changes rapidly.
- Use typed `State` and deterministic tools.

### pdf-ingest
- Use `pymupdf4llm` via `uv run` for extraction.
- Save `.md` in the same directory as source PDF.
- NEVER delete the source PDF.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
| `AGENTS.md` | `.agent/AGENTS.md` | Core Persona & Protocols |
| `SKILLS.md` | `.agent/SKILLS.md` | Technical Skills Catalog |
