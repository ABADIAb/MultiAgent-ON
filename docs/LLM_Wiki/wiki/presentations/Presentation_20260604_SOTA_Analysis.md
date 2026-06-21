---
title: "Presentation: SOTA Comparison"
date: 2026-06-21
tags: [presentation, sota, literature, intent-based, optical-networks]
status: active
---

# Agentic AI for Intent-Based Optical Networks: SOTA Comparison

---

## Slide 1: Introduction to the SOTA Analysis

> [!LAYOUT]
> Title centered. Bullet points highlighting the scope of the literature review on the left. Relevant research icons on the right.

- **Objective:** Establish the state-of-the-art (SOTA) in Agentic AI for Intent-Based Optical Networks (2024–2026).
- **Scope:** Analyzed recent advances in multi-agent systems, intent parsing, and optical network orchestration.
- **Goal:** Identify the unique positioning and research gap for the MultiAgentON thesis.

![Image Suggestion: Conceptual icon showing a magnifying glass over network research papers]

<!-- Speaker Notes: Good morning/afternoon, Professor Zhang. Today I want to present a comprehensive analysis of the current state-of-the-art regarding Agentic AI in optical networks. The goal of this analysis was to see exactly what has been done between 2024 and 2026, and more importantly, what has NOT been done, to firmly establish the unique contribution of our thesis. -->

---

## Slide 2: The 5 Architectural Families

> [!LAYOUT]
> A horizontal timeline or 5-pillar diagram showing the distinct areas of research.

1. **Hyperscale Multi-Agent** (e.g., Meta's Confucius, IP/Datacenter focus)
2. **Field-Trial Pipelines** (e.g., PoliMi ECOC 2024, Single-agent execution)
3. **L4 Autonomous Networks** (e.g., SJTU AutoLight, Operational optical optimization)
4. **IBN Security & Standards** (e.g., EU MARE, IETF GenAI draft)
5. **Edge Orchestration** (e.g., HearthNet, conflict resolution at the edge)

![Image Suggestion: Diagram of 5 pillars representing the architectural families]

<!-- Speaker Notes: We can categorize the recent literature into five main families. We see hyperscale frameworks like Meta's Confucius focusing on IP networks, field-trial pipelines like your ECOC 2024 work focusing on single-agent optical automation, and L4 autonomous systems like SJTU's AutoLight focusing on optical operational tasks. There is also work on security and edge orchestration. Each family solves a piece of the puzzle, but none solves our specific problem. -->

---

## Slide 3: Feature Matrix Overview

> [!LAYOUT]
> A simplified comparative table highlighting key capabilities.

| Capability | PoliMi ECOC'24 | Confucius (Meta) | AutoLight (SJTU) | **MultiAgentON** |
| :--- | :--- | :--- | :--- | :--- |
| **Domain** | Optical | IP/Datacenter | Optical | **Optical** |
| **NL Intent Parsing** | ✅ | ✅ | ❌ | **✅** |
| **Multi-Agent Arch.** | ❌ | ✅ | ✅ | **✅** |
| **QoT-Aware Routing** | ❌ | ❌ | ✅ | **✅** |
| **Formal HITL Safety**| ❌ | ❌ | ❌ | **✅** |

![Image Suggestion: Highlight box over the 'MultiAgentON' column showing it has all capabilities]

<!-- Speaker Notes: Here is a high-level feature matrix comparing our approach against the primary competitors. As you can see, PoliMi laid the groundwork for optical intent parsing but lacks multi-agent coordination. Meta has the multi-agent orchestration but applies it to IP networks. SJTU has multi-agent systems in optical but doesn't handle natural language intent parsing or formal HITL protocols. Only MultiAgentON aims to cover all these bases. -->

---

## Slide 4: The Positioning Gap

> [!LAYOUT]
> A Venn diagram or intersection graphic showing three overlapping circles: NL Intent Parsing, QoT-Aware Routing, and Formal HITL. MultiAgentON is in the center.

- **The Missing Link:** Current research treats operational autonomy, physical-layer validation, and human safety constraints as separate problems.
- **The Contribution:** Integrating natural language parsing, deterministic physical-layer simulation, and operator validation into one unified workflow.
- **The Outcome:** A safe, transparent "Slow Loop" orchestrator that prevents LLM hallucination from reaching the physical testbed.

![Image Suggestion: Venn diagram showing MultiAgentON at the intersection of Intent Parsing, QoT Routing, and Formal HITL]

<!-- Speaker Notes: This brings us to the core positioning gap. No existing work combines Natural Language intent parsing, deterministic QoT-aware optical routing, AND a formal Human-in-the-Loop validation protocol within a single multi-agent LLM framework. Our thesis fills this exact void, treating the network orchestration as a joint cognitive and physical problem solved by specialized AI agents with safety guardrails. -->

---

## Slide 5: Our Unique Selling Points (USPs)

> [!LAYOUT]
> Three large icons, each with a bold title and a short descriptive sentence below.

- **Neurosymbolic Separation:** "LLMs reason, tools calculate." We strictly separate stochastic reasoning from deterministic physics (Python GN model).
- **Tri-Partite Memory:** A principled architecture (Wiki + Graph + RAG) avoiding the pitfalls of naive, context-losing conversational agents.
- **HITL Anti-GIGO:** A formal `interrupt()` safety mechanism to prevent LLM hallucinations from reaching the physical testbed.

![Image Suggestion: Icons for a brain/gears (Neurosymbolic), three interconnected blocks (Memory), and a stop sign with a checkmark (HITL)]

<!-- Speaker Notes: What makes our architecture stand out? First, our strict neurosymbolic separation ensures we don't rely on LLMs to do math; they delegate to deterministic tools like our Python GN model. Second, our Tri-Partite Memory is far more robust than standard RAG. And third, our Human-in-the-Loop validation is a formal safety mechanism to prevent Garbage-In, Garbage-Out, which is critical for real network deployment. -->

---

## Slide 6: Recommended Next Steps

> [!LAYOUT]
> A roadmap or step-by-step path graphic leading towards the thesis defense.

1. **Ideate Experiment 002:** Integrate the Routing Agent and the Python GN model QoT tool into the current LangGraph MVP.
2. **Formal HITL Implementation:** Design and code the `interrupt()` mechanism to allow operator validation of parsed intent before execution.
3. **AutoONBench Evaluation:** Adopt standardized evaluation categories to give our results maximum academic credibility.

![Image Suggestion: Roadmap graphic with 3 milestones]

<!-- Speaker Notes: Based on this analysis, our immediate next steps are clear. We need to design Experiment 002 to test the Routing Agent with real QoT physics. Simultaneously, we must formally implement the HITL protocol to guarantee operator safety. Finally, when we have results, we will evaluate them against the AutoONBench standards to ensure our work is comparable to the rest of the academic community. -->

---

## Slide 7: References

> [!LAYOUT]
> A simple list of the key documents in our knowledge base.

- [[literature/lit_comparison]]: Full systematic comparison matrix and references.
- [[literature/recommendations]]: Detailed breakdown of our immediate and strategic next steps.
- [[Architecture_v2]]: Our unified system design.
- [[ProblemStatement_20260427_Felipe_Abadia]]: The core problem we are solving.

<!-- Speaker Notes: Thank you for your time. The full comparison matrix, the 17 key references, and our detailed research recommendations are all documented in our LLM Wiki for your review. -->

---
