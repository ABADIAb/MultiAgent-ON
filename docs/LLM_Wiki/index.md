# LLM Wiki Index

Content-oriented catalog of everything in the wiki.

## Concepts
- [[Concepts_and_Terminology]]: Glossary of terms for Intent-Based Optical Networks.
- [[QoT_Awareness]]: Concept of Quality of Transmission awareness and feasibility metrics.
- [[Human_in_the_Loop]]: Pre-deployment safety backstop, reverse prompting, bounded refinement, and LangGraph interrupts.
- [[Constraint_Isolation]]: Architectural separation principle ("LLMs reason, tools calculate") isolating physics and graph algorithms.
- [[PDDL]]: Optical network Planning Domain Definition Language subset and Context-Free Grammar AST validation.

## Features
*(Moved to Architecture section — see below)*


## Architecture
- [[ProblemStatement_v5]]: **Active** — LLM-Assisted Risk-Adaptive Decision Gates problem definition, RADG decision function, formal evaluation framework (UAR, HIC, QFR, E2EL, TC), baselines.
- [[Scope_Pivot_20260706]]: Formal scope pivot document — complete evolution from V2 through V5, including PoliMi/CNSM 2025 positioning.
- [[architecture/tools_wiki/QoT_Tool]]: Centralized documentation for the QoT C++ simulator and its physical-layer parameters.

### Feature Docs (`docs/LLM_Wiki/wiki/architecture/features/`)
- [[architecture/features/intent_ingest]]: Phase 1 — NL intent parsing node, IntentSummary schema, LLM structured output.
- [[architecture/features/intent_reconciler]]: Phase 2 (Refinement) — LLM-assisted intent reconciliation and reasoning (full replacement vs partial update).
- [[architecture/features/pddl_parser]]: Phase 2 — PDDL Parser node + CFG Validator. LLM as translator, refinement loop.
- [[architecture/features/reverse_prompt]]: Phase 3 (HITL) — Reverse Prompting HITL node, LLM reconstruction, `interrupt()` pattern.
- [[architecture/features/semantic_gate]]: Phase 3 (Gate) — Semantic RADG node computing $U_{sem}$ with 2-layer validation. Routes to Phase 4 or clarifies.
- [[architecture/features/symbolic_solver]]: Phase 4 — Symbolic Solver (Yen's K-SP) + Mock GraphRAG (k-hop neighborhood extraction).
- [[architecture/features/qot_tool]]: Phase 5 — QoT Physics Engine (GN model), `@tool` wrapper, real physics integration in `qot_validation_node.py`.
- [[architecture/features/radg]]: Phase 6 — Physical RADG, evaluates physical risk, maps QoT to `{approve, replan}`.
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
- [[weekly_reports/Weekly_Report_20260923_Felipe_Abadia]]: Weekly report September 23, 2026. Architecture and implementation of modular comparative baselines (Proposed RADG, Always-On HITL, LLM-Only) reusing production pipeline modules, unified interactive and benchmark CLI (`tests/evaluation/main.py`), 16 new unit tests (337 passing under Strict TDD), live local LLM empirical verification, and Four Pillars evaluation framework telemetry alignment.
- [[weekly_reports/Weekly_Report_20260922_Felipe_Abadia]]: Weekly report September 22, 2026. Full 20-demand benchmark evaluation across all 4 risk classes with 100% Gate Decision Accuracy ($UAR=0.0\%$, 20/20 demands, 17.46s latency) on the 17-node Nobel-Germany topology using local `qwen2.5:3b`, diagnosis and elimination of multi-turn ghost constraint leakage in intent reconciliation and PDDL parsing, nominal benchmark timestamped isolation, and 321 passing unit tests under Strict TDD.
- [[weekly_reports/Weekly_Report_20260915_Felipe_Abadia]]: Weekly report September 15, 2026. Authoring of presentation-coauthor skill, headless Windows PowerPoint COM export pipeline (PDF/PNG) without file locking, 16-slide thesis defense deck, empirical hardware profiling and integration of local Ollama models (qwen2.5:3b, phi4-mini:latest, qwen3:4b, qwen3.5:4b, gemma4:e4b), live 7-phase neurosymbolic pipeline verification, and 347 passing unit tests.
- [[weekly_reports/Weekly_Report_20260908_Felipe_Abadia]]: Weekly report September 08, 2026. Thesis Chapter 3 figures restructuring, Draw.io XML authoring, vector/raster batch export, Overleaf LaTeX consolidation, custom academicbox/formalbox environments, float barriers, resolution of BUG-009 & BUG-010, Planning Report visual redesign, and presentation rehearsal scheduling.
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
- [[issues/Issue_Report_20260922_Felipe_Abadia]]: Solved multi-turn ghost constraint leakage and reconciler misclassification on recovery slices, benchmark run artifact overwriting, PDDL Parser dummy constraint injection on SLMs, Reverse Prompting prompt-example echoing (`avoid-node Leipzig`), Reverse Prompting topology context overload, lossy numerical abstraction in Intent Ingest, and defensive bitrate fallback in QoT validation; 0 pending issues.
- [[issues/Issue_Report_20260915_Felipe_Abadia]]: Solved Windows PowerPoint file-locking, multi-stage banner overflow, DrawingML shape text inversion, native OMML math, manual visual reverse-engineering, LLM-assisted intent reconciliation, ternary RADG action space enforcement, HITL interruption metrics bugfix, 20-demand compact benchmark corpus, local reasoning model thinking tokens disruption, and local multi-model expansion (`phi4-mini:latest` & `qwen3:4b`); 0 pending issues.
- [[issues/Issue_Report_20260908_Felipe_Abadia]]: Solved BUG-009 (Monotonic Refinement Semantic Drift) and BUG-010 (Planning Report Stale Intent & Raw Subtopology Dump); 0 pending issues.
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
- [[presentations/thesis_defense/deck_spec]]: **Active** — Master's Thesis Defense Slide Deck (16 slides, PoliMi template, Prof. Tornatore's 15 Golden Rules, native OMML equations, visual diagrams, and empirical placeholders).

### Archived Presentations (`docs/LLM_Wiki/wiki/presentations/archive/`)
- [[presentations/archive/presentation_chapter_3_system_model_figures]]: (archived) Advisor slide deck for Thesis Chapter 3 System Model, 7-phase architecture, two-gate fail-fast model, and 7-figure visual suite.
- [[presentations/archive/Presentation_Proposal_20260729]]: (archived) Proposal deck on Testbed Integration, Symbolic Solver, and physical parameter questions.
- [[presentations/archive/Presentation_20260706_Neurosymbolic_MVP]]: (archived) Slide deck proposing the Neurosymbolic Intent Orchestration MVP roadmap.
- [[presentations/archive/Presentation_20260621_Scope_Pivot]]: (archived) Slide deck presenting the SOTA-driven scope pivot from full MAS to Intent Planning Loop for Prof. Zhang.
- [[presentations/archive/Presentation_20260604_SOTA_Analysis]]: (archived) Slide deck summarizing the Agentic AI for IBON SOTA comparison (pre-pivot).
- [[presentations/archive/Presentation_20260519_QoT_&_Orchestrator_Integration]]: (archived) Unified slide deck combining Orchestrator V2 architecture and QoT physics port for professor review.
- [[presentations/archive/Presentation_20260519_Orchestrator_Architecture]]: (archived) V2 LangGraph Orchestrator architecture slide deck for professor review.
- [[presentations/archive/Presentation_20260511_QoT_Integration]]: (archived) Technical analysis of the C++ QoT simulator and the Pure Python Port integration proposal.
- [[presentations/archive/Presentation_Hybrid_Memory_Architecture_and_Implementation]]: (archived) Presentation outline proposing the Hybrid Memory Architecture to the professor.

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
- [[experiments/bugs/bug009_Semantic_Gate_Refinement_Drift]]: BUG-009 — Monotonic Semantic Gate drift on multi-turn refinement comparing against stale initial intent.
- [[experiments/bugs/bug010_Planning_Report_Intent_and_Topology]]: BUG-010 — Stale initial intent, raw subtopology dump, and keyword repetition in Planning Report.

### Archived Experiment Documents
- [[experiments/archive/Proposal_Orchestrator_Integration]]: (archived) Formal proposal for modernizing the ECOC 2024 orchestrator. Superseded by Architecture_v2.
- [[experiments/archive/Proposal_QoT_Integration]]: (archived) Formal proposal for the Python Physics Port integration. Superseded by Architecture_v2.
- [[experiments/archive/QoT_Integration_Strategy]]: (archived) Comprehensive strategy for porting the C++ physics equations. Superseded by Architecture_v2.


## Thesis Drafts
- [[thesis_drafts/Drafting_Backlog]]: Backlog of pending clarifications and assumptions to include in unwritten chapters.
- [[thesis_drafts/Writing_Roadmap_v1]]: Writing roadmap and strategy for using NotebookLM/Antigravity.
- [[thesis_drafts/Thesis_Outline_v4]]: Active V4 draft with problem formalization and mapped citations based on NotebookLM structural recommendations.
- [[thesis_drafts/3_SystemModel/3_1_Formal_Problem_Definition]]: Chapter 3 Section 3.1 — Formal Problem Definition, architectural vulnerabilities, physical parameters, and optimization objective.
- [[thesis_drafts/3_SystemModel/3_2_Proposed_Neurosymbolic_Framework]]: Chapter 3 Section 3.2 — Proposed Neurosymbolic Framework, 7-phase fail-fast pipeline, and complexity bounds.
- [[thesis_drafts/3_SystemModel/3_3_Strict_Neurosymbolic_Separation]]: Chapter 3 Section 3.3 — Strict Neurosymbolic Separation, CFG validator AST parsing, and token context bounds.
- [[thesis_drafts/3_SystemModel/3_4_Risk_Adaptive_Decision_Gates]]: Chapter 3 Section 3.4 — Risk-Adaptive Decision Gates (RADGs) decision function, GN model physics integration, and Formal HITL Reverse Prompting execution policies.
- [[thesis_drafts/3_SystemModel/chapter_3_system_model.txt]]: Complete merged $\text{\LaTeX}$ source for Chapter 3 (Overleaf-ready).
- [[thesis_drafts/4_NPImp/chapter_4_implementation.txt]]: Complete merged $\text{\LaTeX}$ source for Chapter 4 (Overleaf-ready).
- [[thesis_drafts/3_SystemModel/figs_SystemModel/README]]: Vector figures catalog, Overleaf $\text{\LaTeX}$ snippet guide for Chapter 3 core figures, and academicbox/formalbox environment usage.
- [[thesis_drafts/4_NPImp/figs_NPImp/README]]: Vector figures catalog, Overleaf $\text{\LaTeX}$ snippet guide for Chapter 4 core figures, and bounding box specifications.
- [[thesis_drafts/4_NPImp/4_1_The_LangGraph_Orchestrator]]: Chapter 4 Section 4.1 — LangGraph StateGraph pipeline architecture, AgentState channels, conditional routing, and HITL interrupt mechanics.
- [[thesis_drafts/4_NPImp/4_2_Network_Context_and_Subtopology_Extraction]]: Chapter 4 Section 4.2 — Network State Abstraction, Nobel-Germany topology, and Mock GraphRAG k-hop subtopology scoping.
- [[thesis_drafts/4_NPImp/4_3_The_Semantic_Engine]]: Chapter 4 Section 4.3 — Intent Ingest, Intent Reconciler, AST CFG Validator ($v_{struct}$), Two-Layer Reverse Prompting, and Semantic RADG ($U_{sem}$).
- [[thesis_drafts/4_NPImp/4_4_The_Physical_Engine_and_System_Resilience]]: Chapter 4 Section 4.4 — Deterministic KSP Symbolic Solver, GN-model QoT physics calculation, and Physical RADG gate.
- [[thesis_drafts/4_NPImp/4_5_Plan_Synthesis_and_Verification]]: Chapter 4 Section 4.5 — Multi-turn plan synthesis, JSON/PDF report generation, and E2E execution paths.
- [[thesis_drafts/archive/Thesis_Outline_v3]]: (archived) V3 outline draft.
- [[thesis_drafts/archive/Thesis_Outline_v2]]: (archived) V2 outline draft.

## Session Summaries
- [[session_summary/session_20260923_Modular_Baselines_and_Evaluation_CLI]]: Modular baseline architecture (Proposed RADG, Always-On HITL, LLM-Only) in `tests/evaluation/baselines/`, Four Pillars metrics engine, unified interactive and evaluation CLI in `tests/evaluation/main.py`, 16 unit tests, and live verification with `qwen2.5:3b`.
- [[session_summary/session_20260923_Chapter4_Figures_and_Orchestration_Integration]]: Chapter 4 architectural visual suite design (langgraph_execution_flow, semantic_engine), standalone Python AST exporters, in-text narrative integration, Overleaf LaTeX chapter consolidation (\FloatBarrier, \includegraphics), and zero broken references.
- [[session_summary/session_20260923_Chapter3_Figure_Refinement_and_Caption_Styling]]: Chapter 3 visual suite refactoring (stripping redundant cards and enlarging typography on conceptual_framework, archiving subsystems and reverse prompting diagrams), narrative and LaTeX synchronization, standalone batch export script, caption styling standardization (\small\itshape), and thesis-coauthor skill upgrades.
- [[session_summary/session_20260922_Chapter4_Improvement]]: Overleaf $\text{\LaTeX}$ chapter consolidation (Chapters 3 & 4), in-text woven figure narrative integration across all 5 diagrams/placeholders, strict tone refactor eliminating AI clichés, upgrade of thesis-coauthor skill and references, and 1:1 Markdown-to-LaTeX synchronization.
- [[session_summary/session_20260921_Chapter4_Restructure_and_Tone_Refactor]]: Chapter 4 structural expansion to 5 sections aligning with the 7-phase LangGraph pipeline, rigorous tone refactor of Chapters 3 and 4 eliminating AI clichés, update to `thesis-coauthor` skill enforcing precision and technical density.
- [[session_summary/session_20260920_Chapter3_Storytelling_Refactor]]: Chapter 3 top-down storytelling restructure (renaming/reordering framework sections), elimination of AI clichés, terminology consolidation (operational integrity), and CFG/GN-model simplification.
- [[session_summary/session_20260919_Thesis_Chapter4_Neurosymbolic_Pipeline_Implementation]]: Consolidated session summary: major restructuring of Chapters 3 and 4 for narrative fluidity. Consolidated all mathematical formulations (GN-model physics, $U_{sem}$) and formal grammars (PDDL CFG) into Chapter 3. Completely redesigned Chapter 4 into four execution sections (4.1 to 4.4 in `docs/LLM_Wiki/wiki/thesis_drafts/4_NPImp/`), covering Orchestration and Network Context, The Semantic Engine, The Physical Engine and System Resilience, and Plan Synthesis and Verification, abstracting raw PDDL and code blocks to improve storytelling.
- [[session_summary/session_20260918_Architecture_Tone_Refactor]]: Architecture tone refactor to emphasize HITL optimization and operational integrity, thesis title alignment, and consolidation of EvaluationFramework_v5.
- [[session_summary/session_20260916_Benchmark_Harness_SLM_Hardening_and_Full_Corpus_Evaluation]]: Consolidated session summary: automated benchmark harness with run isolation and non-destructive snapshotting, Four Core Validation Pillars telemetry integration (`run_evaluation.py`), prompt/context hardening for local SLM (`qwen2.5:3b`), elimination of ghost constraint leakage in intent reconciliation, achieving 100% first-attempt pass rate on Nominal intents, 94.1% CRR, 0% FPR, 0% UAR (Strict Safety Invariant), and 95.0% Gate Decision Accuracy across the full 20-demand compact corpus.
- [[session_summary/session_20260914_Sprint4_Evaluation_Modernization_and_Follow_Up_Protocol]]: Sprint 4 evaluation framework modernization: automated follow-up recovery protocol (`STANDARD_FOLLOW_UP_INTENT`) via `Command(resume=...)` for true E2E latency and cumulative token accounting through to synthesis per intent risk class, dual-action tracking (`initial_action` vs `final_action`), consolidation to a 4-baseline comparative matrix (Proposed, Baseline A, Baseline B, Baseline C), complete removal of Baseline C (Always-Off HITL), refinement of Pillar 2 (UAR=0%, PIIR=100%) and Pillar 3 (latency, tokens, $\Delta N_{hitl}$), and formalization of Traditional SDON / PCE as a static industrial reference (hours to days/weeks, 0 tokens, UAR=0.0%).
- [[session_summary/session_20260914_Local_Ollama_Multi_Model_Profiling_and_Provider_Integration]]: Consolidated session summary: local open-weights Ollama integration (`OllamaChatOpenAI`, WSL2 gateway discovery, multi-provider dispatch), hardware architecture audit on RTX 3050 (4GB VRAM) proving `qwen2.5:3b` as optimal 100% VRAM default (~1.5s latency, 70 tok/s), profiling of `phi4-mini:latest` and `qwen3:4b` with dynamic token budgeting (3000 tokens) and native `<think>` token filtering, and Phase 3 Semantic Gate hardening eliminating topology leakage.
- [[session_summary/session_20260913_Evaluation_Optimization_Compact_Corpus_and_RADG_Action_Space_Formalization]]: Optimization of the benchmark harness with a 20-intent compact corpus, strict ternary RADG action space enforcement ($\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$), and HITL interruption origin attribution bugfix in `metrics.py`.
- [[session_summary/session_20260913_Automated_Evaluation_Harness_and_Sprint4_Benchmarking]]: Design, implementation, and empirical verification of the Sprint 4 Automated Evaluation Harness (`run_benchmark.py`, `metrics.py`, `plotter.py`), Strict TDD testing (10 unit tests, 324 total passing tests), export of raw telemetry (JSON/CSV) and publication-quality figures (IEEE/PoliMi style in PDF and PNG), and empirical proof of the strict 0% Unsafe Approval Rate ($UAR = 0.0\%$) invariant for the Proposed Neurosymbolic RADG across 107 benchmark intents.
- [[session_summary/session_20260913_Comparative_Baselines_Redesign_and_Polymorphic_Harness]]: Redesign and formalization of the 4 comparative evaluation baselines (Monolithic LLM, Always-On HITL, Always-Off HITL, Traditional SDON) vs Proposed Neurosymbolic RADG, implementation of the decoupled polymorphic execution package in `tests/evaluation/baselines/` with standardized `BaselineResult` schema, and 314 passing unit tests under Strict TDD.
- [[session_summary/session_20260912_Bandwidth_SLA_Mapping_Corpus_Balancing_and_RADG_Action_Normalization]]: Bandwidth and capacity SLA constraint mapping into PDDL and GN-model physics (400G 21.5 dB threshold), Reverse Prompting prompt calibration, benchmark corpus expansion to 107 sequentially categorized demands, publication-ready Excel summary spreadsheet generation in `raw/`, normalization of the RADG action space to strictly ternary $\{\text{approve}, \text{clarify}, \text{replan}\}$, and 294 passing tests.
- [[session_summary/session_20260912_LLM_Assisted_Intent_Reconciliation_and_Refinement]]: Implementation of the LLM-assisted Intent Reconciler (`intent_reconciler.py`), structured prompt engineering with Chain-of-Thought taxonomy (`FULL_REPLACEMENT` vs `PARTIAL_UPDATE`), dynamic GraphRAG subtopology rescoping upon endpoint alteration, unification of operational `active_intent` across Phase 2, Semantic Gate, and Plan Synthesizer, and 291 passing tests.
- [[session_summary/session_20260912_Benchmark_Corpus_Balancing_Baseline_C_and_Evaluation_Scaffolding]]: Formalization of Baseline C (traditional SDON / PCE without LLM), optical topology JSON and GraphRAG token economy validation (>90% savings), benchmark corpus balancing (25 demands per class across 4 classes), evaluation environment scaffolding (test_corpus.json, README.md), and defense presentation Slide 13 synchronization.
- [[session_summary/session_20260911_Evaluation_Framework_and_Slide13_Refinement]]: Formalization of the Four Core Validation Pillars and comparative baselines (Baseline A LLM-only, Baseline B static rule-based), analysis of Always-Off HITL ablation, Slide 13 visual enhancements (parallel baseline comparison pills, DrawingML run color fix, structured 3-column benchmark table), and headless vector PDF / 1080p slide export.
- [[session_summary/session_20260910_Thesis_Title_Modernization_and_Presentation_Alignment]]: Formal update of the thesis title to "LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks", cross-ecosystem synchronization (architecture, drafts, rules, config, code docstrings), PowerPoint deck re-compilation, vector PDF/PNG export, and two-way sync workflow clarification.
- [[session_summary/session_20260909_Presentation_CoAuthor_Skill_and_Thesis_Defense_Deck]]: Creation of presentation-coauthor skill, headless Windows PowerPoint COM export automation (vector PDF and 1080p PNG previews), and complete 16-slide Master's thesis defense deck adhering strictly to Prof. Tornatore's 15 Golden Rules.
- [[session_summary/session_20260908_BUG009_Semantic_Gate_Refinement_Drift_and_Thesis_Alignment]]: Diagnosis and resolution of BUG-009 (monotonic refinement semantic drift) and BUG-010 (stale intent in planning report with horizontal lightpath graph redesign), Thesis Chapter 3 drafts / Overleaf LaTeX synchronization, and presentation rehearsal scheduling.
- [[session_summary/session_20260907_CLI_Modernization_HITL_Bypass_and_Serialization]]: Interactive CLI modernization (Rich/Questionary), ghost placeholder styling, Phase 3b fast-track approval routing to symbolic solver, LangGraph MsgPack deserialization whitelist, Thesis Chapter 3 synchronization, Draw.io diagram updates, and automated export tooling.
- [[session_summary/session_20260906_Thesis_Chapter3_Figures_and_LaTeX_Consolidation]]: Publication-ready restructuring of Chapter 3 figures, Draw.io vector exports, Overleaf LaTeX source (`chapter_3_system_model.txt`), academicbox listings, formalbox specifications, float barrier controls, and margin overflow normalization.
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

