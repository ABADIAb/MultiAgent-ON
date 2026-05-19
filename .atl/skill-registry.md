# Skill Registry

**Delegator use only.**

## User Skills

| Trigger | Skill | Path |
|---------|-------|------|
| `docs/LLM_Wiki`, `ingest` | `wiki-protocol` | `/home/felipeab/MultiAgentON/.agents/skills/wiki-protocol/SKILL.md` |
| `langgraph`, `src/graph.py` | `langgraph-expert` | `/home/felipeab/MultiAgentON/.agents/skills/langgraph-expert/SKILL.md` |
| `extract pdf`, `ingest pdf` | `pdf-ingest` | `/home/felipeab/MultiAgentON/.agents/skills/pdf-ingest/SKILL.md` |
| `presentation`, `slides`, `powerpoint` | `presentation-designer` | `/home/felipeab/MultiAgentON/.agents/skills/presentation-designer/SKILL.md` |

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

### presentation-designer
- Use `---` for slide separators.
- Keep content scannable (no long paragraphs).
- Use `> [!LAYOUT]` blockquotes for visual distribution suggestions.
- Use HTML comments `<!-- Speaker Notes: ... -->` for presenter notes.

## Project Conventions

| File | Path | Notes |
|------|------|-------|
