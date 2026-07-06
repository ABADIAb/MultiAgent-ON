---
title: "Research Recommendations: Next Steps for MultiAgentON"
date: 2026-06-22
tags: [literature, recommendations, research, next-steps, thesis, planning-loop]
status: active
---

# Research Recommendations for MultiAgentON Thesis

This document lists actionable research directions based on the findings from [[lit_comparison]] and the [[Scope_Pivot_20260621|scope pivot]] to the Intent Planning Loop. Ordered by priority.

---

## Priority 1: Immediate Actions (Next 1–2 Weeks)

### 1.1 ~~Read Confucius (SIGCOMM 2025)~~ ✅ DONE
See [[Confucius_SIGCOMM2025]].

### 1.2 ~~Read SJTU Invited Tutorial (JOCN 2026)~~ ✅ DONE
See [[SJTU_Invited_Tutorial_JOCN2026]].

### 1.3 ~~Read AutoLight (ECOC 2025)~~ ✅ DONE
See [[AutoLight_ECOC2025]].

### 1.4 ~~SOTA Comparison Presentation~~ ✅ DONE
See [[Presentation_20260604_SOTA_Analysis]].

### 1.5 Experiment 002: Intent Parsing + HITL Reverse Prompting

- **Why**: The NL intent parsing with multi-turn HITL is the **first core differentiator**. Must be validated in isolation before integration.
- **Action**: Implement the Orchestrator's intent parser (NL → `sla_matrix`) and the `interrupt()` HITL mechanism. Test with 3–5 concrete operator intent examples. Validate that reverse prompting catches ambiguous or incomplete intents.
- **Deliverable**: Working HITL loop that iterates until the operator approves a validated `sla_matrix`.

### 1.6 Experiment 003: QoT-Informed Path Selection

- **Why**: The QoT-aware path evaluation is the **second core differentiator**. The Routing Agent + GN model tool must produce deterministic, verifiable results.
- **Action**: Implement the Routing Agent with `qot_check` tool. Given a topology snapshot and SLA constraints, identify candidate paths and evaluate QoT feasibility. Generate a structured Planning Report.
- **Deliverable**: Working prototype of topology → candidate paths → QoT evaluation → Planning Report.
- **Dependencies**: Experiment 001 (topology data).

### 1.7 Design the Planning Report Artifact

- **Why**: The Planning Report is the **primary output** of the system. Its Pydantic schema must be designed before Experiments 002–004.
- **Action**: Define `PlanningReport`, `CandidatePath`, and `SLAMatrix` Pydantic models. Include fields for QoT scores, SLA satisfaction, trade-off analysis, and HITL conversation trace.
- **Deliverable**: Pydantic schema definitions in `src/core/models.py`.

---

## Priority 2: Medium-Term Research (Next 2–4 Weeks)

### 2.1 Experiment 004: Full Intent Planning Loop

- **Why**: The end-to-end integration validates the complete thesis contribution.
- **Action**: Integrate Experiments 002 + 003 into a single planning loop: NL intent → parse → topology → QoT path evaluation → Planning Report → HITL refinement → approved plan.
- **Deliverable**: End-to-end planning loop with quantitative metrics (iterations to convergence, QoT accuracy).

### 2.2 Study AutoONBench Evaluation Methodology

- **Paper**: Wu et al., "AutoONBench: a benchmark for LLM agents in autonomous optical networks." JOCN, Vol. 18(9), 2026.
- **Why**: We need evaluation metrics. Even if our scope is planning-only, adopting recognized evaluation categories gives academic credibility.
- **Action**: Read the paper, extract metrics applicable to planning (task completion rate, iterations, QoT validation accuracy).

### 2.3 Explore IETF IBN+GenAI Framework

- **Document**: `draft-cgfabk-nmrg-ibn-generative-ai-02`
- **Why**: Positioning within an IETF standardization effort increases relevance. Our Intent Planning Loop maps naturally to their "Intent Transformer" concept.

---

## Priority 3: Strategic Research Directions (Thesis Lifetime)

### 3.1 Compute Scheduling (Deferred — Future Work)

Already deferred from previous pivot. Not part of the planning loop scope.

### 3.2 Formalize the Neurosymbolic Separation

- **Opportunity**: Define a formal taxonomy of decision points — which are "symbolic" (tool-delegated: SNR calculation, pathfinding) vs. "neural" (LLM-delegated: intent parsing, trade-off reasoning). This directly addresses the "confidently wrong" research gap.
- **Academic Value**: A reusable framework, not just an implementation detail.

### 3.3 Provisioning Agent (Deferred — Future Work)

Would consume the `approved_plan` output and generate RESTConf API calls. Documented in [[Architecture_v3]] Phase 3 as future work.

### 3.4 Benchmark Against AutoONBench Categories

Once Experiment 004 is complete, map results to AutoONBench's evaluation categories. Planning-specific metrics: intent fidelity, QoT prediction accuracy, HITL convergence speed.

---

## Priority 4: Things to Monitor (Not Investigate Deeply)

| Topic | Why Monitor | Where to Track |
|---|---|---|
| **MCP (Model Context Protocol)** | May standardize agent-to-tool interface | IETF / Anthropic |
| **A2A Protocol** | Could define inter-agent communication standards | Google / IETF |
| **GNPy Multiband Extensions** | Only relevant if testbed supports C+L+S | TIP / GNPy GitHub |

---

## Summary of Recommended Reading List

| # | Paper / Document | Priority | Status |
|---|---|---|---|
| 1 | Confucius (SIGCOMM 2025) | ✅ Done | [[Confucius_SIGCOMM2025]] |
| 2 | SJTU Invited Tutorial (JOCN 2026) | ✅ Done | [[SJTU_Invited_Tutorial_JOCN2026]] |
| 3 | ECOC 2024 PDP (PoliMi) | ✅ Done | [[OrchestratorScriptReport]] |
| 4 | AutoLight (ECOC 2025) | ✅ Done | [[AutoLight_ECOC2025]] |
| 5 | AutoONBench (JOCN 2026) | 🟡 Medium | Evaluation methodology |
| 6 | IETF IBN+GenAI draft | 🟡 Medium | Standards positioning |
| 7 | Expertise-Guided Agent (JOCN 2026) | 🟡 Medium | DT+LLM pattern |
| 8 | EU MARE (arXiv 2026) | 🟢 Low | Security context only |

---

## Cross-References

- [[lit_comparison]] — Detailed SOTA comparison
- [[sota_gap_analysis]] — Gap analysis with planning-loop positioning
- [[Architecture_v3]] — Intent Planning System architecture
- [[ProblemStatement_v3]] — Thesis problem definition
- [[Scope_Pivot_20260621]] — Rationale for scope change
- [[experiments/Experiment_001_Topology_Query_MVP]] — Completed experiment
