# LLM Wiki Index

Content-oriented catalog of everything in the wiki.

## Concepts
- [[ProblemStatement_20260427_Felipe_Abadia]]: Definition of the thesis problem and objectives.
- [[Concepts_and_Terminology]]: Glossary of terms for Intent-Based Optical Networks.
- [[QoT_Awareness]]: Concept of Quality of Transmission awareness and feasibility metrics.

## Architecture
- [[Architecture_v2]]: **Unified V2 system design** — LangGraph multi-agent workflow, Hybrid Memory, QoT strategy, ECOC baseline bridge.
- [[Tool_Registry]]: Registry of deterministic tools/skills for the optical network.
- [[tools_wiki/QoT_Tool]]: Centralized documentation for the QoT C++ simulator and its physical-layer parameters.

### Archived Architecture Documents
- [[architecture/archive/Architecture_Workflow_20260427_Felipe_Abadia]]: (archived) V2 LangGraph implementation workflow. Superseded by Architecture_v2.
- [[architecture/archive/Hybrid_Memory_Architecture]]: (archived) Tri-partite memory architecture. Superseded by Architecture_v2.

## Weekly Reports
- [[Weekly_Report_20260622_Felipe_Abadia]]: Weekly report June 08 – June 22, 2026.
- [[Weekly_Report_20260608_Felipe_Abadia]]: Weekly report May 26 – June 08, 2026.
- [[Weekly_Report_20260526_Felipe_Abadia]]: Weekly report May 19 – May 26, 2026.
- [[Weekly_Report_20260519_Felipe_Abadia]]: Weekly report May 12 – May 19, 2026.
- [[Weekly_Report_20260511_Felipe_Abadia]]: Weekly report May 5 – May 11, 2026.
- [[Weekly_Report_20260504_Felipe_Abadia]]: Weekly report April 28 – May 4, 2026.
- [[Weekly_Report_20260427_Felipe_Abadia]]: Weekly report April 25-27, 2026.
- [[Weekly_Report_20260424_Felipe_Abadia]]: Weekly report April 18-24, 2026.

## Literature
- [[literature/OrchestratorScriptReport]]: Analysis of the ECOC 2024 orchestrator codebase, Claude RAG memory paper, and comparison with our Hybrid Memory Architecture.
- [[literature/lit_comparison]]: Systematic SOTA comparison of Agentic AI approaches for IBON (2024–2026) — feature matrix, positioning, and key references.
- [[literature/recommendations]]: Prioritized research directions and follow-up reading list based on the literature comparison.
- [[literature/sota_gap_analysis]]: Gap analysis positioning MultiAgentON against Confucius, SJTU, PoliMi, IntentLLM, and HearthNet. Updated for scope pivot (routing+QoT+HITL focus).
- [[literature/Confucius_SIGCOMM2025]]: Detailed analysis of Meta's Confucius multi-agent LLM framework (SIGCOMM 2025). DAG workflows, Collector primitive, Ensemble, RAG.
- [[literature/SJTU_Invited_Tutorial_JOCN2026]]: Comprehensive summary of the SJTU invited tutorial on AI agents for AONs (JOCN 2026). Hierarchical MAS, DT toolset, MCP, field trials.
- [[literature/AutoLight_ECOC2025]]: Field trial of SJTU's AutoLight — L4 autonomous optical network for distributed AI training (ECOC 2025). LangGraph-based hierarchical MAS, Chain of Identity (CoI), ~98% task completion.

## Issues
- [[Issue_Report_20260622_Felipe_Abadia]]: SSH workspace access pending testing.
- [[Issue_Report_20260511_Felipe_Abadia]]: Solved QoT code delivery; pending SSH access, Python wrapper implementation, and Orchestrator review.
- [[Issue_Report_20260504_Felipe_Abadia]]: Hybrid Memory designed; pending LangGraph prototyping, QoT tool, and KG technology research.
- [[Issue_Report_20260430_Felipe_Abadia]]: Solved repo structure confusion; pending LangGraph prototyping and QoT tool.

## Presentations
- [[Presentation_20260604_SOTA_Analysis]]: Slide deck for Prof. Zhang summarizing the Agentic AI for IBON SOTA comparison.
- [[Presentation_20260519_QoT_&_Orchestrator_Integration]]: Unified slide deck combining Orchestrator V2 architecture and QoT physics port for professor review.
- [[Presentation_20260519_Orchestrator_Architecture]]: V2 LangGraph Orchestrator architecture slide deck for professor review.
- [[Presentation_20260511_QoT_Integration]]: Technical analysis of the C++ QoT simulator and the Pure Python Port integration proposal.
- [[Presentation_Hybrid_Memory_MAS]]: Presentation outline proposing the Hybrid Memory Architecture to the professor.
- [[Presentation_20260430_DevEnvironment]]: Dev environment restructuring (Screaming Architecture, Wiki system, Issue tracking).

## Transcriptions
- [[Transcript_20260519_Orchestrator&QoT_ArchitectureV2]]: Meeting regarding Orchestrator API access and progress update.
- [[Transcript_20260505_QoT-Script]]: Meeting with Aryanaz explaining the QoT tool repo structure and SNR/Power functions.
- [[Transcript_20260423_QoT-Meeting]]: Meeting with Aryanaz and Qiaolun about QoT feasibility tool and GN model.

## Experiments
- [[experiments/Experiment_001_Topology_Query_MVP]]: Topology Query MVP — first end-to-end LangGraph pipeline (Supervisor + Topology Agent + mock testbed).

### Archived Experiment Documents
- [[experiments/archive/Proposal_Orchestrator_Integration]]: (archived) Formal proposal for modernizing the ECOC 2024 orchestrator. Superseded by Architecture_v2.
- [[experiments/archive/Proposal_QoT_Integration]]: (archived) Formal proposal for the Python Physics Port integration. Superseded by Architecture_v2.
- [[experiments/archive/QoT_Integration_Strategy]]: (archived) Comprehensive strategy for porting the C++ physics equations. Superseded by Architecture_v2.


## Thesis Drafts
*(Empty)*
