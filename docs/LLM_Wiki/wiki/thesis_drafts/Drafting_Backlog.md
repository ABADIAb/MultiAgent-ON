---
title: "Thesis Drafting Backlog"
date: 2026-09-01
tags: [thesis, drafts, backlog, reminders]
status: active
---

# Thesis Drafting Backlog

This document serves as a registry and reminder of all assumptions, clarifications, and engineering details that shall be included in thesis chapters and sections.

Review this list before writing or finalizing each chapter. If an item is resolved, remove it.

---

### 1. Dynamic Subtopology Scoping (Ellipsoid GraphRAG)
- **Context:** In Phase 1 and 4, the initial theoretical design proposed a naive static $k$-hop neighborhood extraction to bound the context size. However, if the shortest path distance $d > 2k$, the extracted subgraph becomes disconnected, causing the LLM to falsely conclude infeasibility.
- **Action:** Ensure that in future work section clarifies the migration from naive $k$-hop to an Ellipsoid Subtopology Scoping or dynamic $k$-hop, where nodes are extracted conditionally based on $d(S, v) + d(v, T) \le d(S, T) + \Delta$ to guarantee subgraph connectivity and optimal token efficiency regardless of network diameter.
