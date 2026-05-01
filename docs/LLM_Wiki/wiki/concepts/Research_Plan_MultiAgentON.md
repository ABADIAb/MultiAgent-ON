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

## Phase 3: Synthesizing the Unified Cost Function
**Goal:** Find standard models that couple optical variables (spectrum fragmentation, EDFA power) with compute variables (GPU utilization, inference cost) into a unified system cost function $C_{sys}(r_i^*, b_i^*, c_i^*)$.

### Database Queries (IEEE Xplore, arXiv, Scopus)
- `"joint communication and computation" AND "resource allocation" AND "optical networks"`
- `"multi-objective optimization" AND "compute and network" AND "cost function"`
- `"edge computing" AND "optical routing" AND "GPU resource allocation"`

### Gemini Web Deep Research Prompts
> **Prompt 3:** "Perform a comprehensive literature review on the mathematical formulation of cost functions in 'joint communication and computation resource allocation' within optical networks. I am looking for specific equations where researchers combine optical network costs (such as spectrum fragmentation, link utilization, or EDFA power consumption) with compute node costs (such as GPU cycle utilization or VRAM allocation). Provide the explicit mathematical models used to balance these heterogeneous variables."

---

## Phase 4: State-of-the-Art Memory Management in Intent-Based Optical Networks
**Goal:** Research current strategies for managing context, memory, and state when using Large Language Models in complex telecommunication environments, specifically [[Concepts_and_Terminology|Intent-Based Optical Networks (IBON)]]. We need to validate if our "Hybrid Memory" approach (LLM Wiki + Vector RAG) aligns with or improves upon the state of the art.

### Database Queries (IEEE Xplore, arXiv, Scopus)
- `"large language model" AND "intent-based networking" AND ("memory management" OR "context window" OR "state management")`
- `"generative AI" AND "optical networks" AND "RAG" AND "knowledge graph"`
- `"multi-agent systems" AND "LLM" AND "persistent memory"`

### Gemini Web Deep Research Prompts
> **Prompt 4:** "Conduct a deep research review on the state-of-the-art memory management techniques used by Large Language Models operating within Intent-Based Optical Networks or complex SDN orchestrators. Specifically, investigate how researchers handle the context window limitation when the agent needs access to both structured operational policies and unstructured, extensive hardware documentation. How are architectures combining RAG (Retrieval-Augmented Generation) with structural state memory (like Knowledge Graphs or hierarchical wikis)? Provide concrete examples of architectures from recent literature."
