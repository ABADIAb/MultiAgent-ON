---
title: "Presentation: Dev Environment Restructuring"
date: 2026-04-30
tags: [presentation, architecture, devops]
status: active
---
# Development Environment Restructuring

**Presenter:** Felipe Abadia  
**Date:** April 30, 2026  
**Project:** Agentic AI for joint routing and compute scheduling in optical networks

---

## 1. The Problem

The repository had a **flat structure** with no separation of concerns:

- Application code, documentation, AI assistant configuration, and tooling definitions were all mixed in the project root.
- The `AGENTS.md` file was a monolithic blob containing persona, writing rules, thesis context, AND wiki operational workflows.
- The `Skills.md` file confused AI assistant capabilities with the deterministic tools being built for the optical network.
- Scaling the project with more agents, tools, and research documents would have been chaotic.

---

## 2. The Solution: Screaming Architecture

"Screaming Architecture" is a pattern where the **top-level directory structure screams the purpose of each component** at first glance.

### Before (Flat):
```
MultiAgentON/
├── AGENTS.md          # Everything mixed
├── Skills.md          # Ambiguous scope
├── LLM_Wiki/          # Root-level wiki
├── main.py            # ???
└── ...
```

### After (Screaming):
```
MultiAgentON/
├── src/               # APPLICATION CODE
│   ├── agents/        # LangGraph agent definitions
│   ├── tools/         # Deterministic tools (QoT, routing)
│   ├── core/          # Shared state, schemas
│   ├── services/      # External integrations
│   └── main.py        # Entry point
├── docs/              # DOCUMENTATION
│   └── LLM_Wiki/     # 2-layer knowledge base
├── .agent/            # AI ASSISTANT CONFIG
│   ├── AGENTS.md      # Persona & protocols only
│   └── skills/        # Modular operational workflows
└── tests/             # TEST SUITE
```

---

## 3. Repo Map — Component Responsibilities

| Directory | Responsibility | Who Owns It |
|-----------|---------------|-------------|
| `src/` | All Python application code: agents, tools, state, services | Developer |
| `docs/LLM_Wiki/` | Research knowledge base with 2-layer architecture (raw sources → wiki pages) | AI + Developer |
| `.agent/` | AI assistant identity, interaction protocols, and operational skills | AI + Developer |
| `tests/` | Strict TDD test suite | Developer |

---

## 4. Wiki System — 2-Layer Architecture

The LLM Wiki follows a strict 2-layer separation:

- **`raw/`** — Immutable source documents: papers, notes, raw data. Read-only.
- **`wiki/`** — LLM-generated knowledge base with strict YAML metadata and aggressive interlinking. Categories include:
  - `concepts/` — Definitions, glossary, problem statements
  - `architecture/` — System workflows, tool registries
  - `literature/` — Paper summaries and reviews
  - `experiments/` — Experimental results and analysis
  - `weekly_reports/` — Structured progress reports
  - `issues/` — Formal issue tracking
  - `presentations/` — Meeting materials

**Navigation files:** `index.md` (content catalog) and `log.md` (operational history).

---

## 5. Issue Tracking System

Formal issue reports follow a structured template:

- **Solved Issues**: What was wrong → What was tried → How it was resolved.
- **Pending Issues**: What is wrong → What has been tried → Result → Estimated solution.

Each report is named: `Issue_Report_YYYYMMDD_Felipe_Abadia.md` and linked in the wiki index.

---

## 6. Next Steps

1. **LangGraph Prototyping:** Implement a minimal `StateGraph` with a single Orchestrator node and one dummy tool to validate the pipeline.
2. **Literature Ingestion:** Ingest foundational papers into the wiki.
3. **QoT Tool Integration:** Obtain the QoT tool script and design the tool bindings for LangGraph.
