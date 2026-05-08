---
title: "Agentic Skills Registry"
date: 2026-04-30
tags: [architecture, tools, registry]
status: active
---
# Agentic Skills Registry

This document serves as the registry for the modular capabilities ("Skills") integrated into the MultiAgentON project. We follow the principle of modular tools that the orchestrator or sub-agents can call deterministically, rather than relying on LLM hallucination for complex or mathematical tasks.

> **Note:** We can integrate the official `skills.sh` CLI (via `npx skills`) in the future to manage community-built skills. For now, this registry manually tracks our custom tools.

## 1. Installed Skills / Tools

### A. Quality of Transmission (QoT) Estimator
- **Status:** Pending Integration (Simplified 3-function codebase expected)
- **Description:** A deterministic Python script/tool to validate the feasibility of generated light paths across the optical network. Uses a network-based evaluation with the Gaussian Noise (GN) model.
- **Agent Assigned:** Routing Agent / Orchestrator
- **Dependencies:** Physical layer Python codebase (to be provided by the team)
- **Evaluation Criteria:**
  - **Receiver Power:** Must be greater than `-18 dB`.
  - **SNR (Signal-to-Noise Ratio):** Must exceed a dynamically defined threshold.
- **Usage Example:** Agent parses user intent -> identifies a need for QoT -> calls the QoT feasibility functions for the proposed paths -> receives feasibility status (1 or 0) -> reasons over the result to make a routing decision.

## 2. Pending Skills to Implement

- [ ] `fetch_topology`: A skill to retrieve the current state of the optical network test-bed.
- [ ] `schedule_compute`: A skill to interface with the compute nodes to allocate processing tasks.
- [ ] `github_sync`: A skill to automatically push updates or read from the Git repository.

## 3. How to Add a New Skill
1. Define the skill's purpose and deterministic nature.
2. Implement the tool using LangChain/LangGraph `@tool` decorators.
3. Test the tool in isolation.
4. Add it to this registry.
5. Provide the tool to the relevant sub-agent in the LangGraph setup.
