# LLM Wiki Index

Content-oriented catalog of everything in the wiki.

## Concepts
- [[Concepts_and_Terminology]]: Glossary of terms for Intent-Based Optical Networks.
- [[QoT_Awareness]]: Concept of Quality of Transmission awareness and feasibility metrics.

## Features
*(Moved to Architecture section — see below)*


## Architecture
- [[Architecture_v5]]: **Active V5 design** — Risk-Adaptive Neurosymbolic Intent Planning, RADG (joint semantic + QoT risk gate), conditional HITL, 4-outcome decision function.
- [[ProblemStatement_v5]]: **Active** — Risk-Adaptive Neurosymbolic problem definition, RADG decision function, formal evaluation framework (UAR, HIC, QFR, E2EL, TC), baselines.
- [[Scope_Pivot_20260706]]: Formal scope pivot document — complete evolution from V2 through V5, including PoliMi/CNSM 2025 positioning.
- [[tools_wiki/QoT_Tool]]: Centralized documentation for the QoT C++ simulator and its physical-layer parameters.

### Feature Docs (`docs/LLM_Wiki/wiki/architecture/features/`)
- [[architecture/features/intent_ingest]]: Phase 1 — NL intent parsing node, IntentSummary schema, LLM structured output.
- [[architecture/features/pddl_parser]]: Phase 2 — PDDL Parser node + CFG Validator. LLM as translator, refinement loop.
- [[architecture/features/reverse_prompt]]: Phase 3 (HITL) — Reverse Prompting HITL node, LLM reconstruction, `interrupt()` pattern.
- [[architecture/features/semantic_gate]]: Phase 3 (Gate) — Semantic Gate node computing $U_{sem}$ with 2-layer validation. Routes to Phase 4 or clarifies.
- [[architecture/features/symbolic_solver]]: Phase 4 — Symbolic Solver (Yen's K-SP) + Mock GraphRAG (k-hop neighborhood extraction).
- [[architecture/features/qot_tool]]: Phase 5 — QoT Physics Engine (GN model), `@tool` wrapper, real physics integration in `qot_validation_node.py`.
- [[architecture/features/radg]]: Phase 6 — Risk-Adaptive Decision Gate (RADG), evaluates physical risk, maps QoT to `{approve, replan}`.
- [[architecture/features/plan_synthesizer]]: Phase 7 — Plan Synthesizer, compiles auditable trace of $U_{sem}$ and QoT decisions.
- [[architecture/features/testbed_client]]: Testbed NBI — RESTConf client with CAS SSO, MockTestbedClient, topology assembly.
- [[architecture/features/pipeline_graph]]: Pipeline wiring — LangGraph StateGraph, AgentState schema, full V5 active topology.

### Archived Architecture Documents
- [[architecture/archive/Architecture_v4]]: (archived) V4 Neurosymbolic Intent Orchestration. Superseded by Architecture_v5.
- [[architecture/archive/ProblemStatement_v4]]: (archived) V4 problem statement. Superseded by ProblemStatement_v5.
- [[architecture/archive/Scope_Pivot_20260621]]: (archived) V3 scope pivot. Superseded by Scope_Pivot_20260706.
- [[architecture/archive/Architecture_v3]]: (archived) V3 Intent Planning Loop design. Superseded by Architecture_v5.
- [[architecture/archive/ProblemStatement_v3]]: (archived) V3 Intent Planning loop. Superseded by ProblemStatement_v5.
- [[architecture/archive/ProblemStatement_20260427_Felipe_Abadia]]: (archived) Original problem statement. Superseded by ProblemStatement_v3.
- [[architecture/archive/Architecture_v2]]: (archived) V2 unified system design. Superseded by Architecture_v3.
- [[architecture/archive/Architecture_Workflow_20260427_Felipe_Abadia]]: (archived) V1 LangGraph workflow. Superseded by Architecture_v2.
- [[architecture/archive/Hybrid_Memory_Architecture]]: (archived) Tri-partite memory architecture. Superseded by Architecture_v2.

## Weekly Reports
- [[weekly_reports/Weekly_Report_20260908_Felipe_Abadia]]: Weekly report September 08, 2026. Thesis Chapter 3 figures restructuring, Draw.io XML authoring, vector/raster batch export, plain-text diagram purging, and Overleaf LaTeX consolidation.
- [[weekly_reports/Weekly_Report_20260901_Felipe_Abadia]]: Weekly report September 01, 2026. Thesis Chapter 3 drafting & refinement (Sections 3.1–3.3), Reverse Prompting decoupling, full CFG AST PDDL parser, symbolic solver node exclusion (`avoid-node`), and 268 passing tests.
- [[weekly_reports/Weekly_Report_20260811_Felipe_Abadia]]: Weekly report August 11, 2026. Sprint 3 completion, RADG integration, QoT physics, and Architecture V5 wiring.
- [[weekly_reports/Weekly_Report_20260803_Felipe_Abadia]]: Weekly report August 03, 2026. RESTConf Testbed integration, Symbolic Solver, Codebase Reorganization, and Feature Documentation Hub.

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
- [[literature/sota_gap_analysis]]: Gap analysis positioning MultiAgentON's Risk-Adaptive RADG against Confucius, SJTU, PoliMi, PoliMi/CNSM 2025, IntentLLM, and HearthNet.
- [[literature/Confucius_SIGCOMM2025]]: Detailed analysis of Meta's Confucius multi-agent LLM framework (SIGCOMM 2025). DAG workflows, Collector primitive, Ensemble, RAG.
- [[literature/SJTU_Invited_Tutorial_JOCN2026]]: Comprehensive summary of the SJTU invited tutorial on AI agents for AONs (JOCN 2026). Hierarchical MAS, DT toolset, MCP, field trials.
- [[literature/AutoLight_ECOC2025]]: Field trial of SJTU's AutoLight — L4 autonomous optical network for distributed AI training (ECOC 2025). LangGraph-based hierarchical MAS, Chain of Identity (CoI), ~98% task completion.

## Issues
- [[issues/Issue_Report_20260906_Felipe_Abadia]]: Solved Draw.io temporary lock/backup files cluttering workspace via permanent .gitignore rules; 0 pending issues.
- [[issues/Issue_Report_20260824_Felipe_Abadia]]: Solved 3-node numerical evaluation limitation via Nobel-Germany 17-node topology; solved multi-hop power accumulation; solved BUG-006 solver endpoint parsing; pending testbed link provisioning; in progress Sprint 4 test corpus.
- [[issues/Issue_Report_20260811_Felipe_Abadia]]: Sprint 3 blockers resolved (RADG, Pipeline); Pending unprovisioned testbed connections.
- [[issues/Issue_Report_20260803_Felipe_Abadia]]: Solved RESTConf hook & codebase reorganization; pending physical link provisioning and LangGraph V5 RADG wiring.

- [[issues/Issue_Report_20260720_Felipe_Abadia]]: Pending virtual testbed RESTConf API; Pending LangGraph refactor for Fail-Fast Architecture V5.
- [[issues/Issue_Report_20260714_Felipe_Abadia]]: Solved PDDL feedback bug; pending virtual testbed RESTConf API.
- [[issues/Issue_Report_20260710_Felipe_Abadia]]: Solved C++ QoT translation; pending virtual testbed RESTConf API.
- [[issues/Issue_Report_20260706_Felipe_Abadia]]: Solved QoT Python port; pending SSH testbed connection.
- [[Issue_Report_20260622_Felipe_Abadia]]: SSH workspace access pending testing.
- [[Issue_Report_20260511_Felipe_Abadia]]: Solved QoT code delivery; pending SSH access, Python wrapper implementation, and Orchestrator review.
- [[Issue_Report_20260504_Felipe_Abadia]]: Hybrid Memory designed; pending LangGraph prototyping, QoT tool, and KG technology research.
- [[Issue_Report_20260430_Felipe_Abadia]]: Solved repo structure confusion; pending LangGraph prototyping and QoT tool.

## Presentations
- [[presentations/presentation_chapter_3_system_model_figures]]: Advisor slide deck for Thesis Chapter 3 System Model, 7-phase architecture, two-gate fail-fast model, and complete 7-figure visual suite walkthrough.
- [[presentations/Presentation_Proposal_20260729]]: Proposal deck on Testbed Integration, Symbolic Solver, and physical parameter questions.

- [[presentations/Presentation_20260706_Neurosymbolic_MVP]]: Slide deck proposing the Neurosymbolic Intent Orchestration MVP roadmap.
- [[Presentation_20260621_Scope_Pivot]]: Slide deck presenting the SOTA-driven scope pivot from full MAS to Intent Planning Loop for Prof. Zhang.
- [[Presentation_20260604_SOTA_Analysis]]: Slide deck summarizing the Agentic AI for IBON SOTA comparison (pre-pivot).
- [[Presentation_20260519_QoT_&_Orchestrator_Integration]]: Unified slide deck combining Orchestrator V2 architecture and QoT physics port for professor review.
- [[Presentation_20260519_Orchestrator_Architecture]]: V2 LangGraph Orchestrator architecture slide deck for professor review.
- [[Presentation_20260511_QoT_Integration]]: Technical analysis of the C++ QoT simulator and the Pure Python Port integration proposal.
- [[Presentation_Hybrid_Memory_MAS]]: Presentation outline proposing the Hybrid Memory Architecture to the professor.
- [[Presentation_20260430_DevEnvironment]]: Dev environment restructuring (Screaming Architecture, Wiki system, Issue tracking).

## Transcriptions
- [[transcriptions/Transcript_20260811_ThesisOutline_MockTopology]]: Meeting with team on thesis outline feedback (introduction, baseline integration, October defense timeline) and shifting from physical testbed RESTConf topology to mock topologies (17-node German / 14-node Japan).
- [[Transcript_20260519_Orchestrator&QoT_ArchitectureV2]]: Meeting regarding Orchestrator API access and progress update.
- [[Transcript_20260505_QoT-Script]]: Meeting with Aryanaz explaining the QoT tool repo structure and SNR/Power functions.
- [[Transcript_20260423_QoT-Meeting]]: Meeting with Aryanaz and Qiaolun about QoT feasibility tool and GN model.

## Experiments
- [[experiments/Bug_Registry]]: **Active** — Registry and resolution index of system bugs, physical-layer edge cases, and pipeline loopback fixes.
- [[experiments/MVP_Roadmap]]: **Active** — Detailed sprint plan and experimental roadmap targeting the August 25 MVP deadline.
- [[experiments/Experiment_1_1_QoT_Port]]: QoT C++ to Python Port — execution specification for Sprint 1.
- [[experiments/Experiment_001_Topology_Query_MVP]]: Topology Query MVP — first end-to-end LangGraph pipeline (Supervisor + Topology Agent + mock testbed).

### Bug Reports (`docs/LLM_Wiki/wiki/experiments/bugs/`)
- [[experiments/bugs/bug001_GSNR_Threshold]]: BUG-001 — GSNR threshold constraint parsing in Symbolic Solver & QoT calculator.
- [[experiments/bugs/bug002_Refinement_Loopback]]: BUG-002 — HITL interrupt feedback capture in RADG loopback.
- [[experiments/bugs/bug003_NLI_Explosion]]: BUG-003 — GN-model NLI saturation and EDFA gain calibration.
- [[experiments/bugs/bug004_Node_ID_Leakage]]: BUG-004 — Synthetic node ID leakage in Reverse Prompting.
- [[experiments/bugs/bug005_Schema_Duplication]]: BUG-005 — Schema unification between state.py and models.py.
- [[experiments/bugs/bug006_Source_Target_Loss]]: BUG-006 — Source and Target endpoint parsing in Symbolic Solver.
- [[experiments/bugs/bug007_Semantic_Gate_Refinement_Loop]]: BUG-007 — Semantic Gate refinement loopback infinite cycle and routing fix.
- [[experiments/bugs/bug008_Inadmissible_HITL_Approval_on_Gate_Failure]]: BUG-008 — Inadmissible operator approval on Semantic Gate clarification failure in Phase 3b interrupt.

### Archived Experiment Documents
- [[experiments/archive/Proposal_Orchestrator_Integration]]: (archived) Formal proposal for modernizing the ECOC 2024 orchestrator. Superseded by Architecture_v2.
- [[experiments/archive/Proposal_QoT_Integration]]: (archived) Formal proposal for the Python Physics Port integration. Superseded by Architecture_v2.
- [[experiments/archive/QoT_Integration_Strategy]]: (archived) Comprehensive strategy for porting the C++ physics equations. Superseded by Architecture_v2.


## Thesis Drafts
- [[thesis_drafts/Drafting_Backlog]]: Backlog of pending clarifications and assumptions to include in unwritten chapters.
- [[thesis_drafts/Writing_Roadmap_v1]]: Writing roadmap and strategy for using NotebookLM/Antigravity.
- [[thesis_drafts/Thesis_Outline_v4]]: Active V4 draft with problem formalization and mapped citations based on NotebookLM structural recommendations.
- [[thesis_drafts/3_SystemModel/3_1_Formal_Problem_Definition]]: Chapter 3 Section 3.1 — Formal Problem Definition, architectural vulnerabilities, physical parameters, and optimization objective.
- [[thesis_drafts/3_SystemModel/3_2_Conceptual_Framework]]: Chapter 3 Section 3.2 — Conceptual Framework, 7-phase fail-fast pipeline, and complexity bounds.
- [[thesis_drafts/3_SystemModel/3_3_Strict_Neurosymbolic_Separation]]: Chapter 3 Section 3.3 — Strict Neurosymbolic Separation, CFG validator, and token context bounds.
- [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gate]]: Chapter 3 Section 3.4 — Risk-Adaptive Decision Gate (RADG) decision function and GN model physics integration.
- [[thesis_drafts/3_SystemModel/3_5_Formal_HITL_Reverse_Prompting]]: Chapter 3 Section 3.5 — Formal HITL Reverse Prompting, Reverse Translation Invariance, divergence metric alignment, state preservation, and convergence proofs.
- [[thesis_drafts/3_SystemModel/chapter_3_system_model.txt]]: Complete merged $\text{\LaTeX}$ source for Chapter 3 (Overleaf-ready).
- [[thesis_drafts/3_SystemModel/figs/README]]: Vector figures catalog and Overleaf $\text{\LaTeX}$ snippet guide for all 7 Chapter 3 figures.
- [[thesis_drafts/archive/Thesis_Outline_v3]]: (archived) V3 outline draft.
- [[thesis_drafts/archive/Thesis_Outline_v2]]: (archived) V2 outline draft.

## Session Summaries
- [[session_summary/session_20260906_Thesis_Chapter3_Figures_and_LaTeX_Consolidation]]: Publication-ready restructuring of Chapter 3 figures into `figs/src/`, `figs/pdf/`, and `figs/png/`, semantic naming standard, authoring missing Draw.io models (neural/symbolic subsystems, reverse prompting closed-loop), purging all plain text diagrams, batch vector compilation via Draw.io CLI, and rebuilding Overleaf LaTeX source (`chapter_3_system_model.txt`).
- [[session_summary/session_20260905_Thesis_Section_3_5_HITL_Refinement_and_Bugfix]]: Mathematical refinement of Chapter 3 Section 3.5 (HITL Reverse Prompting), cross-section alignment of semantic divergence $d_{sem}$, resolution of BUG-008, Chapter 3 LaTeX Overleaf export (`chapter_3_system_model.txt`), vector figures and Draw.io XML workflow with HTML math subscripts, and unified `thesis-coauthor` skill authoring.
- [[session_summary/session_20260904_Thesis_Section_3_4_RADG_Refinement]]: Mathematical refinement of Chapter 3 Section 3.4 (RADG), GN model GSNR accumulation equations, and formalization of theoretical vs. pipeline execution decoupling across Phase 3 and Phase 6.
- [[session_summary/session_20260903_Architecture_Refactoring_CFG_Validation_and_Chapter3_Refinement]]: Decoupling Reverse Prompting & conditional HITL, full S-expression CFG AST PDDL validator, symbolic solver node exclusion (avoid-node), Kimi API dynamic parameters, and Thesis Chapter 3 (Sections 3.2 & 3.3) formal refinement.
- [[session_summary/session_20260826_Thesis_Chapter3_Drafting_and_Formal_Problem_Definition]]: Thesis Chapter 3 kick-off, drafting Sections 3.1-3.5, rigorous validation of Section 3.1 math vs codebase, and engineering assumptions formalization.
- [[session_summary/session_20260821_QA_Pipeline_Verification_and_Bug007]]: Comprehensive QA flow validation across all 7 execution paths, BUG-007 resolution, avoid-link quote parsing fix, and test suite expansion to 255 tests.
- [[session_summary/session_20260820_Kimi_LLM_Optimization_and_Benchmarking]]: Diagnostic of Kimi LLM latency bottleneck (~189s to 2-4s), factory upgrade with reasoning controls (think_effort, thinking_disabled), and multi-model benchmark suite.
- [[session_summary/session_20260819_Bug006_Source_Target_Loss_and_Bug_Registry]]: Diagnostic and resolution of BUG-006 (symbolic solver source/target loss), Bug Registry modularization, and bug-debugger skill creation.
- [[session_summary/session_20260817_Nobel_Germany_Topology_Migration]]: Adoption of 17-node Nobel-Germany optical backbone topology, EDFA physical calibration, and test suite expansion.
- [[session_summary/session_20260807_GraphRAG_Integration]]: Optical RAG integration for dynamic topology injection in Phase 1 and Phase 2.
- [[session_summary/session_20260806_Sprint3_RADG_Integration]]: Sprint 3 completion, V5 Risk-Adaptive Pipeline integration (RADG, $U_{sem}$, and real QoT physics).
- [[session_summary/session_20260731_Code_Reorganization]]: Codebase Reorganization, src/ Methodology Enactment, Feature Documentation Hub, and Architecture V5 Alignment.
- [[session_summary/session_20260729_RESTConf_Integration]]: RESTConf Testbed Integration, CAS SSO auth flow on port 8443, and empty connections handling.
- [[session_summary/session_20260719_Architecture_V5_Fail_Fast]]: Architecture V5 Simplification, Fail-Fast Semantic Gate, and Binary QoT.
- [[session_summary/session_20260717_Pivot_V5]]: Scope Pivot to V5 Risk-Adaptive Neurosymbolic Intent Planning.
- [[session_summary/session_20260714_Sprint2_PDDL_HITL]]: Sprint 2, PDDL Parser and Reverse Prompting HITL.
- [[session_summary/session_20260710_Architecture_V4_Refactor]]: Architecture V4 Refactor & HITL Integration.

