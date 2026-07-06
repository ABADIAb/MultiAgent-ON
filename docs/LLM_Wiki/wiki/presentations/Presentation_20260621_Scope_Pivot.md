---
title: "Presentation: Scope Pivot — From Full MAS to Intent Planning Loop"
date: 2026-06-22
tags: [presentation, scope-pivot, planning-loop, sota, professor]
status: active
---

# Scope Pivot: From Full MAS to QoT-Informed Intent Planning

---

## Slide 1: Recap — Where We Were

> [!LAYOUT]
> Title centered. Two-column layout: left shows the original Architecture V2 diagram (simplified), right shows the original thesis scope bullets.

**Original Thesis Scope:**
- "Agentic AI for Joint Routing and Compute Scheduling in Optical Networks"
- Full multi-agent system covering Day-0 through Day-N lifecycle
- Orchestrator + Topology Agent + Routing Agent + Lightpath Agent
- Tri-Partite Hybrid Memory (Wiki + Graph + RAG)

**What we built so far:**
- Architecture V2 with LangGraph
- Experiment 001: Topology Query MVP (validated with Kimi API)
- Comprehensive SOTA analysis

![Image Suggestion: Simplified Architecture V2 diagram showing the full system scope]

<!-- Speaker Notes: Professor Zhang, let me start by reminding you of where we were. Our original thesis scope was ambitious — a full multi-agent system for optical network lifecycle management, from intent parsing through provisioning and error recovery. We had designed the Architecture V2, validated the Topology Agent with a working MVP, and completed a comprehensive SOTA analysis. But that SOTA analysis revealed something important that I want to discuss today. -->

---

## Slide 2: The SOTA Reality Check

> [!LAYOUT]
> Three cards or columns, each showing a key competitor with their achievement. Use visual emphasis (icons, color) to show these are strong, validated systems.

### What the SOTA Already Demonstrates

| System | Achievement | Framework |
|:---|:---|:---|
| **Confucius** (Meta, SIGCOMM 2025) | 60+ production apps, 4,160 users, 31.62M messages | Custom DAG + LangChain |
| **AutoLight** (SJTU, ECOC 2025) | ~98% task completion, 3.2× single-agent, field trial (440 km) | **LangGraph** |
| **SJTU Tutorial** (JOCN 2026) | 225+ reference survey, hierarchical MAS, DT toolset, MCP | — |

**Key insight:** AutoLight is built on LangGraph — the same framework we chose. Our framework choice is validated but **not novel**.

![Image Suggestion: Three logos or cards representing Confucius, AutoLight, and SJTU Tutorial with their key metrics]

<!-- Speaker Notes: When I completed the deep analysis of these three key works, I realized something critical. Meta's Confucius already has multi-agent orchestration running in production at hyperscale. More importantly, SJTU's AutoLight — published at ECOC 2025 — already demonstrates a hierarchical multi-agent system for optical networks built on LangGraph, the exact same framework we chose. They achieved 98% task completion in a real field trial. Presenting a "full multi-agent system for optical networks" as our novelty is no longer defensible. -->

---

## Slide 3: But They Don't Do This

> [!LAYOUT]
> Gap analysis quadrant diagram (QoT-Aware vs NL Intent axes) on the left. Three gap bullets on the right with checkmark icons.

```
                    QoT-Aware
                        ▲
                        │
              SJTU ●    │    ● MultiAgentON (ours)
                        │         ▲ + Multi-turn HITL
                        │         │ + NL Intent Parsing
                        │         │ + Planning Report
                        │
    ────────────────────┼────────────────────► NL Intent
                        │
       IntentLLM ●      │      ● PoliMi
                        │
          HearthNet ●   │   ● Confucius
                        │
                 Not QoT-Aware
```

**Three verified gaps no existing work fills:**
1. ✅ **NL Intent Parsing** with formal reverse prompting in the optical domain
2. ✅ **QoT-Aware Path Evaluation** via neurosymbolic GN model delegation
3. ✅ **Multi-Turn HITL Refinement** as an architectural primitive

**All three converge in one phase: the planning phase.**

<!-- Speaker Notes: However, when I mapped the specific capabilities of each system, I found three clear gaps that no existing work addresses. AutoLight receives structured task inputs — they don't parse natural language. Confucius has a Collector primitive for human interaction, but it's single-turn structured Q&A, not iterative refinement. And critically, none of them produce a structured planning report that the operator can review and refine through multiple iterations. All three of these gaps live in the planning phase — the phase where the operator expresses intent and the system builds a validated plan. -->

---

## Slide 4: The Pivot — Intent Planning Loop

> [!LAYOUT]
> Full-width flow diagram showing the Intent Planning Loop. Use arrows and a clear feedback loop to show the iterative nature.

**New Thesis Framing:**
> *"QoT-Informed Intent Planning for Optical Networks: A Neurosymbolic Human-in-the-Loop Approach"*

**Neurosymbolic approach**: LLM for reasoning (neural) + GN model for deterministic physics (symbolic) = Zero physics hallucination.

```
Operator Intent (Natural Language)
    → Orchestrator parses → sla_matrix
    → Topology Agent fetches network state
    → Routing Agent evaluates candidate paths (QoT tool)
    → Orchestrator synthesizes Planning Report
        → Candidate paths with SNR scores
        → SLA constraint satisfaction
        → Trade-off analysis
    → HITL interrupt(): present to operator
        → Operator approves → approved_plan ✓
        → Operator refines → loop back ↺
```

**The output is NOT a network configuration. It is a validated Planning Report.**

<!-- Speaker Notes: So instead of presenting a full multi-agent lifecycle system — where we'd be competing with SJTU's proven field trial — I'm proposing we zoom into the planning phase. The new thesis title is "QoT-Informed Intent Planning for Optical Networks." The system takes natural language from the operator, parses it into structured constraints, queries the topology, evaluates candidate paths using the deterministic GN model, and synthesizes a Planning Report. This report is then presented to the operator via our formal interrupt mechanism. The operator can approve, refine, or reject — and the loop continues until we have a validated plan. The key innovation is that this is a multi-turn, conversational process, not a single approve/reject checkpoint. -->

---

## Slide 5: The Novelty & The Gap

> [!LAYOUT]
> Two columns: Left (What they do) vs Right (What we do). Emphasize the specific combination as the novelty.

### Why This Is Novel
- **Confucius** uses single-turn Q&A without physics.
- **AutoLight** executes structured tasks without natural language or formal HITL.
- **Novelty:** The *combination*. Bridging ambiguous natural language intent to deterministic optical physics via an iterative HITL refinement loop.

<!-- Speaker Notes: To directly answer the question of novelty: it's not just intent parsing, and it's not just QoT. The specific research gap is the absence of a hallucination-free, iterative methodology that bridges high-level human ambiguity to strict physical-layer optical constraints. Confucius has no physics, AutoLight has no natural language or multi-turn HITL. We combine them into one safe "Slow Loop". -->

---

## Slide 6: Evaluation Methodology

> [!LAYOUT]
> Three columns: Metrics, Baselines, and Report Quality.

### How We Will Evaluate This
- **Metrics:**
  - *Intent Fidelity:* % of SLA constraints correctly extracted.
  - *HITL Convergence Rate:* Average iterations to an approved plan.
  - *QoT Validation Accuracy:* 100% adherence to physical limits.
  - *Benchmark:* AutoONBench categories adapted to planning.
- **Baselines for Comparison:**
  - *Zero-Shot LLM Planner* (proves necessity of QoT tool).
  - *Single-Turn Planner* (proves necessity of multi-turn HITL).

<!-- Speaker Notes: We can evaluate this rigorously without a physical testbed. We will measure intent fidelity, HITL convergence rate, and QoT validation accuracy against AutoONBench. We'll compare our loop against a Zero-Shot LLM (to show why the GN model tool is needed) and against a Single-Turn Planner (to show why the iterative interrupt loop is necessary). -->

---

## Slide 7: What Changes

> [!LAYOUT]
> Two-column layout. Left: "Stays In Scope" (green checkmarks). Right: "Future Work" (gray with arrows).

### ✅ Stays In Scope
- NL Intent Parsing → `sla_matrix`
- Orchestrator (LangGraph StateGraph)
- Topology Agent (RESTConf NBI)
- Routing Agent + QoT Tool (GN model)
- Multi-turn HITL (`interrupt()`)
- Neurosymbolic separation
- Planning Report (new structured output)

### ➡️ Moves to Future Work
- Lightpath Provisioning Agent
- Compute Scheduling
- Full Day-N Lifecycle Operations
- Vector RAG (Memory Pillar 3)
- Knowledge Graph DB graduation

![Image Suggestion: Two-column comparison with green checkmarks on left and gray arrows on right]

<!-- Speaker Notes: Let me be concrete about what changes. Everything in the planning loop stays — the intent parser, the topology and routing agents, the QoT tool, and most importantly, the HITL mechanism. What moves to future work is the provisioning phase — we won't generate RESTConf calls. Instead, our output is a validated Planning Report that a downstream system could consume. Compute scheduling was already deferred. The memory substrate is simplified to just Wiki and Pydantic state, which is sufficient for planning. -->

---

## Slide 8: Why This Is Stronger

> [!LAYOUT]
> Three key arguments, each with a bold statement and supporting evidence. Use visual hierarchy (large text for the statement, smaller for evidence).

### 1. Focused contribution > Diffuse contribution
- A deep, novel planning methodology beats a broad system that competes with AutoLight's field trial.
- Depth in one phase is more publishable than breadth across many.

### 2. Evaluable without a field trial
- The planning loop can be validated entirely on a mock testbed.
- Metrics: intent fidelity, QoT prediction accuracy, HITL convergence speed.
- SSH access to the real testbed becomes a bonus, not a blocker.

### 3. SOTA-justified positioning
- The pivot is driven by evidence, not retreat.
- We identified WHERE the gaps are and focused there.
- The professor can verify this against the SOTA comparison matrix.

<!-- Speaker Notes: I want to emphasize why this narrower scope is actually stronger. First, a deep contribution in one phase is more defensible and publishable than competing with AutoLight across the full lifecycle. Second, we can evaluate the planning loop entirely with mock data — we don't need SSH access to the real testbed to validate our core contribution. And third, this pivot is evidence-driven. I can point to specific papers and say: "This is what they do, this is what they don't do, and this is what we do." That's a much stronger thesis defense position. -->

---

## Slide 9: New Experiment Roadmap

> [!LAYOUT]
> A horizontal timeline or roadmap with 4 experiments. Experiment 001 has a green checkmark. Experiments 002-004 are sequential milestones.

| # | Experiment | Focus | Status |
|:---|:---|:---|:---|
| 001 | Topology Query MVP | Supervisor + Topology Agent + mock testbed | ✅ Done |
| 002 | Intent Parsing + HITL | NL → `sla_matrix` with multi-turn reverse prompting | Next |
| 003 | QoT Path Selection | Routing Agent + GN model tool → Planning Report | Next |
| 004 | Full Planning Loop | End-to-end: intent → topology → QoT → HITL → approved plan | Integration |

**Evaluation metrics:**
- Task completion rate (per AutoONBench categories)
- HITL iterations to convergence
- QoT validation accuracy (SNR prediction vs. ground truth)
- Intent fidelity (SLA constraint coverage)

![Image Suggestion: Horizontal roadmap with 4 milestones, first one checked off]

<!-- Speaker Notes: Here's the updated experiment roadmap. Experiment 001 is already done — the Topology Query MVP validated our LangGraph pipeline with the Kimi API. The next experiments are focused entirely on the planning loop: first intent parsing with HITL in isolation, then QoT path selection in isolation, and finally the full integration. Each experiment has clear, quantitative success criteria that we can measure without a field trial. -->

---

## Slide 10: Summary & Next Steps

> [!LAYOUT]
> Clean summary slide with three key takeaways and immediate action items.

### Key Takeaways
1. The SOTA analysis revealed that full MAS for optical networks is **validated but not novel**.
2. Our three research gaps — NL parsing, QoT-aware planning, multi-turn HITL — **all converge in the planning phase**.
3. The new scope is **more focused, more defensible, and easier to evaluate**.

### Immediate Next Steps
1. Implement Experiment 002 (Intent Parsing + HITL)
2. Design the `PlanningReport` Pydantic schema
3. Implement the QoT tool (Python GN model port)

<!-- Speaker Notes: To summarize: the SOTA taught us that the full multi-agent system is no longer novel — it's been demonstrated by Meta and SJTU with real field trials. But the planning intelligence — how a system goes from natural language to a QoT-validated, operator-approved plan — that's where we have a genuine contribution. The new scope is focused, the experiments are clear, and we can validate everything on a mock testbed. I'd appreciate your feedback on this direction. -->

---

## Slide 11: References

> [!LAYOUT]
> Simple reference list with links to wiki documents.

- [[lit_comparison]]: Full systematic comparison matrix
- [[sota_gap_analysis]]: Gap analysis with planning-loop positioning
- [[Scope_Pivot_20260621]]: Formal scope pivot document
- [[Architecture_v3]]: New Intent Planning System architecture
- [[ProblemStatement_v3]]: Updated thesis problem definition

<!-- Speaker Notes: The full comparison matrix, gap analysis, and all supporting documents are available in our wiki for your review. Thank you. -->

---
