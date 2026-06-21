---
title: "Literature: Confucius — Intent-Driven Network Management with Multi-Agent LLMs (Meta, SIGCOMM 2025)"
date: 2026-06-21
tags: [literature, multi-agent, llm, intent-based, network-management, meta, sigcomm]
status: active
---

# Confucius: Intent-Driven Network Management with Multi-Agent LLMs

**Authors:** Zhaodong Wang, Samuel Lin, Guanqing Yan, Soudeh Ghorbani, Minlan Yu, Jiawei Zhou, Nathan Hu, Lopa Baruah, Sam Peters, Srikanth Kamath, Jerry Yang, Ying Zhang
**Venue:** ACM SIGCOMM 2025, Coimbra, Portugal
**Affiliation:** Meta, Johns Hopkins University, Harvard University, Stony Brook University

---

## Summary for Professor

Confucius is the **first published production-grade multi-agent LLM framework for hyper-scale network management**, deployed at Meta for over two years with 60+ applications, 4,160 users, and 31.62 million messages processed. The paper provides a comprehensive experience report on building and operating LLM-based agents for real-world network infrastructure.

### Core Problem

Large-scale network management at Meta involves **complex, multi-step tasks** (capacity planning, fault diagnosis, configuration changes) that require deep domain expertise and the orchestration of numerous specialized tools. A single LLM call is insufficient for these tasks — they require decomposition, iterative refinement, and tool integration.

### Architecture

Confucius adopts a **multi-agent framework** built on four pillars:

1. **Planning (Workflows as DAGs):** Network management procedures (MOPs/runbooks) are modeled as Directed Acyclic Graphs. Each node is a "building block" (BB) — a modular subtask. The LLM plans by selecting and composing these BBs, using RAG to search over hundreds of existing workflows. Independent subtasks run in parallel.

2. **Tools (Domain-Specific Languages):** Rather than building new tools, Confucius bridges LLMs with existing tools via three foundational DSLs:
   - **TML (Topology Modification Language):** Python-based DSL for graph manipulations.
   - **ODS (Operations Data Store):** Key-value time-series data with aggregations.
   - **Robotron Data Model:** Object-relational mapping for network source-of-truth data.
   Three primitives facilitate translation: **Translator** (NL → structured output), **Selector** (narrowing options from a large set), and **Collector** (disambiguation via follow-up questions — a form of [[HITL_Refinement|HITL refinement]]).

3. **Memory:**
   - **Short-term:** A hierarchical tree of messages shared across Analects (agents), with each agent controlling access to its own context.
   - **Long-term:** [[RAG]]-based retrieval over massive databases (e.g., 118.6K vectors for Netgram, 3.3M vectors for Wiki Q&A). Hybrid RAG (coarse → fine-grained filtering) improves accuracy by 3%.

4. **Validation & Human Oversight:**
   - Built-in parsers with error-feedback loops for self-correction.
   - Dry-run modes and external validators (graph invariant checks).
   - **Collector primitive** gathers structured human input, enforcing approval for sensitive operations.

### Programming Model

The framework is built on **Pydantic** (Python schema language) with a core abstraction called the **Analect** (analogous to a typed function with logging, tracing, and I/O). Key primitives:
- **Ensemble:** Calls multiple LLMs in parallel and selects/combines outputs (reduces variance by up to 57.6%).
- **Orchestrator:** Allows LLMs to autonomously create workflows step-by-step (similar to ReAct).

### Key Design Principles

1. **Separate reasoning from factual knowledge** — LLMs reason; databases/tools provide facts.
2. **Leverage existing expertise** — reuse hundreds of production tools rather than building new ones.
3. **Orchestrate with engineered prompts** — "cognitive architecture" decomposition.
4. **No fine-tuning required** — works with foundation models out of the box; prompt engineering + RAG instead.
5. **Prioritize iterative improvement** — ship basic, refine continuously.

### Evaluation Results

- **DSL Translation:** Confucius outperforms a fine-tuned baseline by up to **35% (TML), 22.4% (ODS), 23% (ODS Reduction)** using prompt engineering alone.
- **Ensemble reasoning:** Multi-model ensemble (Llama + Claude + Gemini) achieves **0.87–0.98** mean score, reducing standard error by 34–57.6%.
- **RAG:** Outperforms fine-tuned baselines on all retrieval tasks; Hybrid RAG improves by 3%.
- **Production impact:** Saves an average of **17 engineer-hours/week** across applications.

### Lessons Learned (Section 8)

1. **RAG + Summarization works well** for network problems that match "find similar, generate new."
2. **Integration with existing tools** is the key driver of adoption — LLMs must plug into existing automation pipelines.
3. **Iterative step-by-step workflows** are essential — showing intermediate artifacts enables developers to refine progressively.
4. **Troubleshooting is the hardest domain** — unstructured, expert-dependent tasks where LLMs still fall short of domain experts.
5. **Failure modes:** Context loss in long sessions, hallucination (fabricating answers instead of failing early), privacy risks from unintentional PII exposure.

---

## Relevance to MultiAgentON

| Aspect | Confucius | MultiAgentON |
|:---|:---|:---|
| **Domain** | IP / Datacenter (Meta) | Optical transport networks |
| **Agent framework** | Custom Analect-based (LangChain underneath) | [[Architecture_v2\|LangGraph-based]] Semantic Orchestrator |
| **Planning** | DAG workflows from runbooks | $A^*$-aware routing with QoT constraints |
| **Physical-layer awareness** | None (no SNR, no GN model) | [[QoT_Awareness\|Neurosymbolic QoT]] — LLM reasons, Python calculates |
| **HITL** | Collector primitive (structured Q&A) | Formal `interrupt()` with [[HITL_Refinement\|Reverse Prompting]] |
| **Memory** | Hierarchical tree (short-term) + RAG (long-term) | Tri-Partite Hybrid Memory (wiki + graph + vector) |
| **Validation** | Built-in parsers + dry-run + external validators | [[Constraint_Isolation\|Neurosymbolic constraint isolation]] |

### Key Takeaways for Our Work

1. The **Collector primitive** validates our HITL reverse prompting design — Confucius independently arrived at a similar pattern for disambiguation.
2. The **"no fine-tuning" principle** aligns with our prompt-engineering + tool-delegation approach.
3. Their **Ensemble** primitive is a production-proven version of multi-model consensus that we could adopt for critical routing decisions.
4. The **failure modes** they document (context loss, hallucination, privacy) are exactly the risks our [[HITL_Refinement]] and [[Constraint_Isolation]] are designed to mitigate.
5. Confucius is **not optical-network-aware** — this is our primary differentiator. They have no QoT estimation, no physical-layer constraints, no GN model integration.

---

## Citation

```bibtex
@inproceedings{wang2025confucius,
  title={Intent-Driven Network Management with Multi-Agent LLMs: The Confucius Framework},
  author={Wang, Zhaodong and Lin, Samuel and Yan, Guanqing and Ghorbani, Soudeh and Yu, Minlan and Zhou, Jiawei and Hu, Nathan and Baruah, Lopa and Peters, Sam and Kamath, Srikanth and Yang, Jerry and Zhang, Ying},
  booktitle={ACM SIGCOMM 2025},
  year={2025},
  doi={10.1145/3718958.3750537}
}
```
