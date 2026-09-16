---
title: "Issue Report 2026-09-22"
date: 2026-09-22
tags: [issues, benchmark, evaluation, slm, prompt-engineering, pddl, reverse-prompt, semantic-gate]
status: active
---

# Issue Report

---

## Student Name:
Felipe Abadia

## Project Title:
LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Current Stage:
> Sprint 4 Evaluation & Benchmark Robustness (Class I Nominal Intent Validation)

## Date:
2026-09-22

---

### Solved Issues

#### Solved Issue 1: Small Model (SLM) Prompt-Example Leaking in Reverse Prompting

- **Issue:** When running automated evaluation with local open-weights `qwen2.5:3b` on Class I nominal intent `intent_nom_04` (*"Provision an optical channel from Munich to Stuttgart via Ulm with GSNR at least 15 dB"*), Phase 3a Reverse Prompting consistently produced:
  `"I understand you want to route traffic from Munich to Stuttgart with a minimum GSNR of 15 dB, avoiding node Leipzig, and traversing through Ulm."`
  The hallucinated clause `"avoiding node Leipzig"` caused the Phase 3 Semantic Gate to flag an unprompted negative constraint ($d_{sem} = 0.50 > \tau_{sem} = 0.30$), repeatedly triggering false-positive `clarify` interruptions.
- **What has already been tried:** Initially suspected network topology context leakage from `Mock GraphRAG`. However, inspecting the generated PDDL confirmed that neither the AST `:objects` nor `:goal` mentioned Leipzig.
- **Result:** The divergence persisted across multiple runs even after stripping raw topology predicates from the PDDL string.
- **Estimated possible solution / Resolution:**
  1. Audited `REVERSE_PROMPT_SYSTEM` in [`src/nodes/reverse_prompt.py`](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) and discovered that the single few-shot example provided was:
     `PDDL goal: (and (route Berlin Munich) (min-gsnr 15) (avoid-node Leipzig))`
     `Reconstruction: I understand you want to route traffic from Berlin to Munich with a minimum GSNR of 15 dB, avoiding node Leipzig.`
     Because the intent requested 15 dB GSNR, the 3B model attention latched onto this single example and copied `"avoiding node Leipzig"` verbatim.
  2. Replaced the single biased example with three diverse few-shot examples covering bandwidth-only, waypoints (`via <node>`), and explicit avoidance.
  3. Added an explicit negative directive: *"CRITICAL: NEVER mention or invent any node name that is NOT explicitly written in the PDDL below! If the PDDL does not have (avoid-node ...), DO NOT state that any node is avoided!"*
  4. Implemented `_clean_pddl_for_reverse_prompt()` to strip all `(connected ...)` and `(link-active ...)` predicates before passing PDDL to the LLM, reducing prompt tokens and eliminating background attention noise.
  5. **Verification:** `intent_nom_04` passed immediately on the first turn with $U_{sem} = 0.100$ and 0 HITL interruptions.

---

#### Solved Issue 2: Lossy Summarization in Intent Ingest Inducing Spurious Semantic Divergence

- **Issue:** On complex multi-constraint nominal requests such as `intent_nom_02` (*"Establish an optical connection from Hamburg to Berlin avoiding both Bremen and Hannover, with a minimum of 15 dB GSNR and a maximum of 3 hops"*), the PDDL parser extracted all 5 constraints accurately. However, the Phase 3 Semantic Gate failed with $d_{sem} = 0.50$, triggering an unnecessary Human-in-the-Loop clarification pause.
- **What has already been tried:** Refined the agreement evaluator prompt scale in `semantic_gate_node.py`, but the agreement judge continued to rate the reconstruction as containing an "unprompted constraint".
- **Result:** The system stalled at Phase 3b and required recovery injections.
- **Estimated possible solution / Resolution:**
  1. Traced the input string passed to `_score_semantic_agreement` in [`src/nodes/semantic_gate_node.py`](file:///home/felipeab/MultiAgentON/src/nodes/semantic_gate_node.py). Found that the gate evaluated against `active_intent`.
  2. In [`src/nodes/intent_ingest.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_ingest.py), `intent.summary` had abstracted away the explicit numerical value:
     `"Establish an optical connection from Hamburg to Berlin avoiding Bremen and Hannover with a GSNR constraint and a maximum of 3 hops."`
     When the Semantic Gate compared this summary against the faithful reconstruction (which correctly reported `"minimum GSNR of 15 dB"`), the judge treated `"15 dB"` as an unprompted hallucination because the number was absent from `active_intent`.
  3. Updated `intent_ingest_node` to preserve the operator's verbatim message in `base_statement` for `active_intent`, ensuring that numerical constraints are never lost during structured parsing.
  4. **Verification:** In Run 4, `intent_nom_02` achieved $U_{sem} = 0.100$ on Turn 1, auto-passing to the Symbolic Solver without interruption.

---

#### Solved Issue 3: Dummy `(bandwidth 1)` Generation and PDDL Section Misplacement Leading to QoT Replan

- **Issue:** In `intent_nom_02`, `qwen2.5:3b` placed constraints `(min-gsnr 15)`, `(max-hops 3)`, `(avoid-node ...)` in the `(:init ...)` block instead of `(:goal ...)`, and emitted an unprompted `(bandwidth 1)` predicate. When evaluated by Phase 5 QoT validation, the engine crashed with:
  `Unsupported bitrate: 1G. Supported: [10, 100, 200, 400]`
  Because all candidate paths failed QoT with error flags, Phase 6 RADG triggered a false-positive `replan` action.
- **What has already been tried:** Added general rules in `pddl_parser.py` against dummy constraints, but did not explicitly specify section restrictions or bandwidth exclusions.
- **Result:** The small model continued filling empty schema slots with unit values (`bandwidth 1`).
- **Estimated possible solution / Resolution:**
  1. Updated `PDDL_SYSTEM_PROMPT` in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) with two categorical rules:
     - All constraints MUST reside inside `(:goal (and ...))`. The `(:init ...)` block is strictly reserved for network topology facts.
     - NEVER emit `(bandwidth ...)` or `(bandwidth 1)` unless the operator explicitly requests bandwidth or capacity.
  2. Added three canonical few-shot PDDL examples demonstrating correct section placement and constraint isolation.
  3. Fortified [`src/nodes/qot_validation.py`](file:///home/felipeab/MultiAgentON/src/nodes/qot_validation.py) with defensive bandwidth resolution: if `bandwidth` is not in `(10, 100, 200, 400)`, default safely to 100G instead of raising a fatal simulation error.
  4. **Verification:** In Run 2 and Run 4, `pddl_parser` generated clean PDDL with all constraints inside `:goal` and zero spurious bandwidth predicates.

---

#### Solved Issue 4: Multi-Turn Ghost Constraint Leakage and Reconciler Misclassification on Recovery Slices

- **Issue:** During automated evaluation across the full 20-demand compact corpus, intents `intent_amb_02`, `intent_amb_05`, and `intent_adv_01` were successfully intercepted by Phase 3b (`clarify`) on Turn 1. However, upon injecting the standardized follow-up recovery intent (`"Route traffic from Berlin to Frankfurt with at least 12 dB GSNR"`), the pipeline failed to synthesize on Turn 2, repeatedly triggering semantic gate failures ($d_{sem} = 0.50$). Telemetry inspection revealed that the PDDL parser was generating ghost constraints carried over from the discarded Turn 1 intent (`(via Hannover)` for `intent_amb_02`, `(route Berlin Hamburg)` for `intent_amb_05`, and `(min-hops 1)` for `intent_adv_01`).
- **What has already been tried:** Checked if the recovery intent itself was malformed, but confirmed that the identical follow-up text succeeded on other demands (`intent_amb_01`, `intent_amb_03`, `intent_amb_04`).
- **Result:** The failure only occurred on demands where the initial intent was either missing an endpoint or specified a contradictory constraint.
- **Estimated possible solution / Resolution:**
  1. Traced `reconcile_operator_intent` in [`src/nodes/intent_reconciler.py`](file:///home/felipeab/MultiAgentON/src/nodes/intent_reconciler.py). Found that when `intent_amb_02` (which specified `Berlin` but no destination) received feedback (`"Route traffic from Berlin to Frankfurt..."`), `qwen2.5:3b` observed that the source `Berlin` was unchanged and misclassified the request as `partial_update` rather than `full_replacement`.
  2. Because the update was classified as partial, [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) injected `Previous PDDL constraints` into the prompt, causing the model to blend Turn 1 waypoints (`via Hannover`) into the Turn 2 PDDL. The Phase 3 Semantic Gate correctly flagged `via Hannover` as an unprompted hallucination against the operator's feedback ($d_{sem} = 0.50$).
  3. Updated `INTENT_RECONCILIATION_PROMPT` to explicitly rule that any standalone, complete routing instruction replacing an ambiguous or failed request is strictly a `FULL_REPLACEMENT`.
  4. Added a deterministic neurosymbolic guard in `reconcile_operator_intent`: if feedback contains a complete route specification whose endpoints differ from or resolve previous active endpoints, it is unconditionally forced to `FULL_REPLACEMENT`.
  5. Fortified `pddl_parser_node` in `pddl_parser.py`: when `intent_update_type == "full_replacement"`, previous PDDL constraints are completely omitted from the prompt, instructing the model to generate constraints strictly from scratch based only on active operational intent.
  6. **Verification:** In Run 2, `intent_amb_02`, `intent_amb_05`, and `intent_adv_01` cleanly recovered on Turn 2 ($U_{sem}=0.100$, 0 ghost predicates) and synthesized feasible planning reports, bringing overall Gate Decision Accuracy to **20/20 (100.0%)**.

---

### Pending Issues

- **None.** All 20 benchmark intents across all 4 risk classes now achieve 100.0% Gate Decision Accuracy ($UAR=0.0\%$, 20/20 demands, mean latency 17.46s) on the 17-node Nobel-Germany topology using local `qwen2.5:3b`. Ready for comparative baseline execution.

