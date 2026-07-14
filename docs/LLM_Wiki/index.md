# LLM Wiki Index

Content-oriented catalog of everything in the wiki.

## Concepts
- [[ProblemStatement_v4]]: **Active** — Neurosymbolic Intent Orchestration problem definition, token saturation boundaries, mathematically convergent HITL.
- [[Concepts_and_Terminology]]: Glossary of terms for Intent-Based Optical Networks.
- [[QoT_Awareness]]: Concept of Quality of Transmission awareness and feasibility metrics.

### Archived Concept Documents
- [[concepts/archive/ProblemStatement_v3]]: (archived) V3 Intent Planning loop. Superseded by ProblemStatement_v4.
- [[concepts/archive/ProblemStatement_20260427_Felipe_Abadia]]: (archived) Original problem statement. Superseded by ProblemStatement_v3.

## Architecture
- [[Architecture_v4]]: **Active unified V4 design** — Neurosymbolic Intent Pipeline, PDDL constraint parser, Reverse Prompting, Symbolic Solver, GraphRAG.
- [[Scope_Pivot_20260706]]: Formal scope pivot document — rationale for shifting from generative loop to neurosymbolic pipeline.
- [[Tool_Registry]]: Registry of deterministic tools/skills for the optical network.
- [[tools_wiki/QoT_Tool]]: Centralized documentation for the QoT C++ simulator and its physical-layer parameters.

### Archived Architecture Documents
- [[architecture/archive/Scope_Pivot_20260621]]: (archived) V3 scope pivot. Superseded by Scope_Pivot_20260706.
- [[architecture/archive/Architecture_v3]]: (archived) V3 Intent Planning Loop design. Superseded by Architecture_v4.
- [[architecture/archive/Architecture_v2]]: (archived) V2 unified system design. Superseded by Architecture_v3.
- [[architecture/archive/Architecture_Workflow_20260427_Felipe_Abadia]]: (archived) V1 LangGraph workflow. Superseded by Architecture_v2.
- [[architecture/archive/Hybrid_Memory_Architecture]]: (archived) Tri-partite memory architecture. Superseded by Architecture_v2.

## Weekly Reports
- [[weekly_reports/Weekly_Report_20260720_Felipe_Abadia]]: Weekly report July 20, 2026. Sprint 2 progress, PDDL Parser and HITL implementation.
- [[weekly_reports/Weekly_Report_20260713_Felipe_Abadia]]: Weekly report July 13, 2026. Architecture V4 refactor, Exp 1.0, and HITL.
- [[weekly_reports/Weekly_Report_20260706_Felipe_Abadia]]: Weekly report July 06, 2026. Neurosymbolic MVP pivot.
- [[Weekly_Report_20260622_Felipe_Abadia]]: Weekly report June 08 – June 22, 2026.
- [[Weekly_Report_20260608_Felipe_Abadia]]: Weekly report May 26 – June 08, 2026.
- [[Weekly_Report_20260526_Felipe_Abadia]]: Weekly report May 19 – May 26, 2026.
- [[Weekly_Report_20260519_Felipe_Abadia]]: Weekly report May 12 – May 19, 2026.
- [[Weekly_Report_20260511_Felipe_Abadia]]: Weekly report May 5 – May 11, 2026.
- [[Weekly_Report_20260504_Felipe_Abadia]]: Weekly report April 28 – May 4, 2026.
- [[Weekly_Report_20260427_Felipe_Abadia]]: Weekly report April 25-27, 2026.
- [[Weekly_Report_20260424_Felipe_Abadia]]: Weekly report April 18-24, 2026.

## Literature
- [[literature/OrchestratorScriptReport]]: Analysis of the ECOC 2024 orchestrator codebase, Claude RAG memory paper, and comparison with our architecture.
- [[literature/lit_comparison]]: Systematic SOTA comparison of Agentic AI approaches for IBON (2024–2026) — feature matrix, planning-loop positioning, and key references.
- [[literature/recommendations]]: Prioritized research directions focused on the Intent Planning Loop experiments.
- [[literature/sota_gap_analysis]]: Gap analysis positioning MultiAgentON's Intent Planning Loop against Confucius, SJTU, PoliMi, IntentLLM, and HearthNet.
- [[literature/Confucius_SIGCOMM2025]]: Detailed analysis of Meta's Confucius multi-agent LLM framework (SIGCOMM 2025). DAG workflows, Collector primitive, Ensemble, RAG.
- [[literature/SJTU_Invited_Tutorial_JOCN2026]]: Comprehensive summary of the SJTU invited tutorial on AI agents for AONs (JOCN 2026). Hierarchical MAS, DT toolset, MCP, field trials.
- [[literature/AutoLight_ECOC2025]]: Field trial of SJTU's AutoLight — L4 autonomous optical network for distributed AI training (ECOC 2025). LangGraph-based hierarchical MAS, Chain of Identity (CoI), ~98% task completion.

## Issues
- [[issues/Issue_Report_20260714_Felipe_Abadia]]: Solved PDDL feedback bug; pending virtual testbed RESTConf API.
- [[issues/Issue_Report_20260710_Felipe_Abadia]]: Solved C++ QoT translation; pending virtual testbed RESTConf API.
- [[issues/Issue_Report_20260706_Felipe_Abadia]]: Solved QoT Python port; pending SSH testbed connection.
- [[Issue_Report_20260622_Felipe_Abadia]]: SSH workspace access pending testing.
- [[Issue_Report_20260511_Felipe_Abadia]]: Solved QoT code delivery; pending SSH access, Python wrapper implementation, and Orchestrator review.
- [[Issue_Report_20260504_Felipe_Abadia]]: Hybrid Memory designed; pending LangGraph prototyping, QoT tool, and KG technology research.
- [[Issue_Report_20260430_Felipe_Abadia]]: Solved repo structure confusion; pending LangGraph prototyping and QoT tool.

## Presentations
- [[presentations/Presentation_20260706_Neurosymbolic_MVP]]: Slide deck proposing the Neurosymbolic Intent Orchestration MVP roadmap.
- [[Presentation_20260621_Scope_Pivot]]: Slide deck presenting the SOTA-driven scope pivot from full MAS to Intent Planning Loop for Prof. Zhang.
- [[Presentation_20260604_SOTA_Analysis]]: Slide deck summarizing the Agentic AI for IBON SOTA comparison (pre-pivot).
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
- [[experiments/MVP_Roadmap]]: **Active** — Detailed sprint plan and experimental roadmap targeting the August 25 MVP deadline.
- [[experiments/Experiment_1_1_QoT_Port]]: QoT C++ to Python Port — execution specification for Sprint 1.
- [[experiments/Experiment_001_Topology_Query_MVP]]: Topology Query MVP — first end-to-end LangGraph pipeline (Supervisor + Topology Agent + mock testbed).

### Archived Experiment Documents
- [[experiments/archive/Proposal_Orchestrator_Integration]]: (archived) Formal proposal for modernizing the ECOC 2024 orchestrator. Superseded by Architecture_v2.
- [[experiments/archive/Proposal_QoT_Integration]]: (archived) Formal proposal for the Python Physics Port integration. Superseded by Architecture_v2.
- [[experiments/archive/QoT_Integration_Strategy]]: (archived) Comprehensive strategy for porting the C++ physics equations. Superseded by Architecture_v2.


## Thesis Drafts
*(Empty)*

## Session Summaries
- [[session_summary/session_20260714_Sprint2_PDDL_HITL]]: Sprint 2, PDDL Parser and Reverse Prompting HITL.
- [[session_summary/session_20260710_Architecture_V4_Refactor]]: Architecture V4 Refactor & HITL Integration.
