---
title: "Research Plan"
date: 2026-04-27
tags: [research, planning, literature_review]
status: active
---
# Research Plan: Joint Routing & Compute Scheduling with Agentic AI

This research plan is designed to gather literature supporting the mathematical formulations of semantic distortion, latency budgets, and cost functions in LLM-assisted optical networks. 

## Phase 1: Semantic Distortion in LLMs for Networking
**Goal:** Find papers that quantify information loss or [[ProblemStatement_20260427_Felipe_Abadia|semantic distortion]] when converting network telemetry (timeseries, graphs) into LLM prompts. We need to ground the constraint $D_{sem} = || S_{true} - \hat{S}_{LLM} ||^2 \le D_{max}$.

### Database Queries (IEEE Xplore, arXiv, Scopus)
- `"large language model" AND "network telemetry" AND ("semantic distortion" OR "information loss" OR "state reconstruction")`
- `"LLM" AND "intent-based networking" AND "telemetry compression"`
- `"generative AI" AND "optical networks" AND "representation learning"`

### Gemini Web Deep Research Prompts
> **Prompt 1:** "Conduct a deep research review on how recent academic papers quantify the loss of information (semantic distortion) when raw network telemetry—like optical SNR, link utilization, or routing graphs—is compressed or translated into natural language prompts for Large Language Models. Focus on how researchers mathematically define this reconstruction error or degradation in task performance. Provide specific equations and cite the sources."

---

## Phase 2: Latency Budgets in LLM-driven Orchestration
**Goal:** Identify standard operational time tolerances for different network management tasks to justify the task-dependent latency budget constraint $T_{total, i} \le T_{budget}(type(i))$.

### Database Queries (IEEE Xplore, arXiv, Scopus)
- `"intent-based networking" AND "LLM" AND ("latency budget" OR "reaction time" OR "inference latency")`
- `"software defined optical networking" AND "control loop latency"`
- `"AI agents" AND "network orchestration" AND "time constraints"`

### Gemini Web Deep Research Prompts
> **Prompt 2:** "Search for literature regarding control loop latency constraints in Software-Defined Optical Networks (SDON) when using Agentic AI or LLMs. Specifically, look for papers that categorize latency budgets based on task type—differentiating the time tolerance for 'intent parsing and global planning' (which might take seconds or minutes) versus 'operational reactions and failure recovery' (which require sub-second responses). Summarize the typical time thresholds proposed by researchers for these different task categories."

---

## Phase 3: State-of-the-Art Memory Management in Multi-Agent LLM Systems
**Goal:** Research current strategies for managing context, memory, and state when using Large Language Models in complex environments. This includes specific applications in [[Concepts_and_Terminology|Intent-Based Optical Networks (IBON)]] and broader cross-domain applications of multi-agent systems (e.g., autonomous agents, software engineering, and complex system orchestration). We need to validate if our "Hybrid Memory" approach (LLM Wiki + Vector RAG) aligns with or improves upon the state of the art in memory architectures.

### Database Queries (IEEE Xplore, arXiv, Scopus)
- `"large language model" AND "intent-based networking" AND ("memory management" OR "context window" OR "state management")`
- `"multi-agent systems" AND "LLM" AND ("persistent memory" OR "long-term memory" OR "episodic memory")`
- `"generative AI" AND "cross-domain agents" AND "memory architecture" AND "RAG"`
- `"autonomous LLM agents" AND "state management" AND "distributed memory"`

### Gemini Web Deep Research Prompts
> **Prompt 3:** "Conduct a deep research review on the state-of-the-art memory management techniques used by Large Language Models and Multi-Agent Systems (MAS). While the primary focus is Intent-Based Optical Networks, broaden the search to include other domains like autonomous robotics, software engineering agents, and complex system orchestration. Investigate how researchers handle long-term memory, episodic memory, and context window limitations. Specifically, look for architectures that combine RAG (Retrieval-Augmented Generation) with structural memory (Knowledge Graphs, Hierarchical Wikis, or Vector Databases) to maintain persistent state across agent interactions. Provide concrete examples and comparative analyses from recent literature."

