---
title: "Concept: HITL Refinement"
date: 2026-09-19
tags: [concepts, hitl, reverse-prompting, refinement]
status: active
---

# Concept: HITL Refinement

> **Note:** This concept is formally elaborated in [[concepts/Human_in_the_Loop|Human-in-the-Loop (HITL) Refinement]].

**Human-in-the-Loop (HITL) Refinement** denotes the structured, iterative disambiguation loop wherein human operators adjudicate intent when the neurosymbolic orchestrator detects unacceptable semantic uncertainty ($U_{sem} > \tau_{sem}$) or physical unfeasibility ($\text{QoT}_{valid} = 0$).

### Core Mechanisms
- **Reverse Prompting:** Automated PDDL-to-NL reconstruction presented to the operator.
- **State-Preserving Interruption:** Atomic persistence of the execution thread using LangGraph `interrupt()`.
- **Bounded Refinement ($N_{max}=3$):** Hard termination guard preventing conversational deadlocks and context window exhaustion.

### See Also
- [[concepts/Human_in_the_Loop]] — Comprehensive concept specification.
- [[architecture/features/reverse_prompt]] — Implementation details in Phase 3b.
- [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates]] — RADGs decision function and action space.
