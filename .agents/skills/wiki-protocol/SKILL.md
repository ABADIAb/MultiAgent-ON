---
name: wiki-protocol
description: >
  Rules and workflows for managing the LLM_Wiki (Ingest, Query, Lint, Debrief).
  Trigger: "ingest", "wiki", "lint", "debrief", "/debrief1", "/debrief2", "docs/LLM_Wiki"
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- When managing any file under `docs/LLM_Wiki/`.
- When asked to ingest new PDFs, raw documents, or notes.
- When performing queries across the knowledge base.
- When executing the end-of-session debriefing protocols (`/debrief1` and `/debrief2`).

## Critical Patterns

### 1. 2-Layer Architecture
- **Raw sources (`docs/LLM_Wiki/raw/`)**: Immutable data. Source documents, papers, raw notes. Read-only.
- **The wiki (`docs/LLM_Wiki/wiki/`)**: A directory of LLM-generated markdown files (Concepts, Architecture, Literature, Experiments, Weekly Reports, Drafts, Issues, Presentations). You own this layer.
- **Special Navigation Files (`docs/LLM_Wiki/`)**: 
  - `index.md`: A content-oriented catalog of everything in the wiki, grouped by category with a 1-line summary per page. Update on every ingest. Always read this first before querying.
  - `log.md`: A chronological append-only record of operations (Ingests, Queries, Lints). E.g., `## [YYYY-MM-DD] ingest | Title`.

### 2. Core Operations (Workflows)
- **Ingest**: Process a new source from `raw/` interactively. Read it, discuss key takeaways with the user, write/update pages in `wiki/`, update `index.md`, update cross-references `[[wikilinks]]`, and append an entry to `log.md`.
- **Query**: Read `index.md`, find relevant pages, read them, synthesize an answer. If the answer is highly valuable (e.g. a new analysis), file it back into the wiki as a new page.
- **Lint**: Periodically check the wiki for contradictions, orphan pages, missing links, or stale claims, and propose fixes or web searches to fill data gaps.
- **Debrief Phase 1 (`/debrief1`)**: Session content planning routine. Execute the following steps:
  1. **Analyze Session**: Review what was accomplished.
  2. **Draft Recommendations**: Propose updates for the Weekly Report and the Issue Report. Ask the user which items should be included.
  3. **Presentation Proposal**: If applicable, suggest a structure and content for a presentation to the professor (to be saved as a `.md` in `docs/LLM_Wiki/wiki/presentations/`).
  4. **Create Implementation Plan**: Generate an `implementation_plan.md` to edit or create these files. Await user feedback and iterate until approved.
- **Debrief Phase 2 (`/debrief2`)**: Session closure routine. Execute **ONLY** after `/debrief1`'s plan is approved and executed:
  1. **Wiki Deep Lint**: Identify all files created or modified during the session. For each file, perform a rigorous deep lint to proactively identify and add `[[wikilinks]]` to any core concepts or existing wiki pages mentioned in the text. Ensure `index.md` and all relevant cross-references are updated to maintain total wiki interconnectedness and persistence.
  2. **Engram Session Summary**: Execute `mem_session_summary` to persist state in long-term memory.
  3. **Log Entry**: Append `## [YYYY-MM-DD] debrief | Session Summary` to `log.md`.

### 3. Strict Rules
- **Strict Metadata Rule**: EVERY note you create or edit in `wiki/` MUST contain a YAML frontmatter block at the top with `title`, `date`, `tags`, and `status`.
- **Strict Report Continuity Rule**: Before creating or proposing ANY new Weekly Report, Issue Report, or Presentation, you MUST read the most recent previous report of the same type. New reports must be consistent with the narrative arc: reference what was planned, account for what was or wasn't done, and carry forward unresolved items. If a planned goal was not achieved, explicitly state why and whether it is deferred or dropped.
- **Strict Linking Rule**: You MUST aggressively interlink concepts using `[[wikilinks]]`. If a concept exists, link to it.

## Code Examples

**Example Wiki Note Frontmatter:**
```yaml
---
title: "Concept: QoT Awareness"
date: 2026-05-18
tags: [physical-layer, qot, concepts]
status: active
---
```

## Commands

No specific bash commands required. These are workflow rules.

## Resources

- **Index**: See `docs/LLM_Wiki/index.md` for the catalog.
- **Log**: See `docs/LLM_Wiki/log.md` for the operation history.
