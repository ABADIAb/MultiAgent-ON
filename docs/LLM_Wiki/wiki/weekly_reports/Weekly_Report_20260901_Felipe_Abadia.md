---
title: "Weekly Report 2026-09-01"
date: 2026-09-01
tags: [weekly, report, thesis, chapter-3, system-model, cfg-validator, avoid-node, reverse-prompting, optical-networks]
status: active
---

# Weekly Report

---

## Student Name: 
Felipe Abadia

## Project Title:
Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment

## Date: 
2026-09-01

---

## 1. What did I plan to accomplish this week?

*(Carried forward from the previous sprint & Thesis Writing Plan)*
1. **Thesis Chapter 3 Drafting & Refinement:** Initiate and refine formal drafting of Chapter 3 (*System Model: The Risk-Adaptive Neurosymbolic Architecture*), prioritizing Sections 3.1 (*Formal Problem Definition*), 3.2 (*Conceptual Framework*), and 3.3 (*Strict Neurosymbolic Separation*).
2. **Mathematical Formulation & Verification:** Formalize the optical intent planning optimization problem, system inputs, physical/semantic boundary constraints, and rigorously validate the formulation against the `src/` codebase.
3. **Pipeline Architecture & HITL Refinement:** Resolve pipeline coupling issues to ensure true risk-adaptive HITL engagement without unnecessary human friction.
4. **Sprint 4 Preparation:** Prepare the structured synthetic test corpus and baseline evaluation infrastructure for Sprint 4.

---

## 2. What did I actually accomplish?

1. **Thesis Chapter 3 Drafting & Section-by-Section Refinement:**
   - **Roadmap Structuring:** Mapped the master thesis roadmap in [[thesis_drafts/Writing_Roadmap_v1]] across 5 phased milestones with strict academic, non-AI cliché, and LaTeX standards.
   - **Section 3.1 Formal Problem Definition:** Validated the optimization problem $\min \mathcal{J} = \alpha N_{hitl} + \beta T_{tokens}$ subject to $D(U_{sem}, \text{QoT}_{valid}) = \text{approve}$ against `src/core/`. Formally grounded the model with Assumption 1 (Homogeneous SMF-28 Fiber Profile) and Assumption 2 (Zero Equalization Loss in Filtered ROADM Networks), aligning `ProblemStatement_v5.md` with receiver floor verification $P_{rx}(\pi) \ge P_{rx, min}$.
   - **Section 3.2 Conceptual Framework:** Refined the 7-phase fail-fast pipeline description, architectural separation invariants, and asymptotic complexity bounds.
   - **Section 3.3 Strict Neurosymbolic Separation:** Detailed the formal PDDL grammar, predicate typing, and added rigorous mathematical explanations for Section 3.3.4 (Token Budget and Context Scoping), bounding context size $\mathcal{O}(|V_{sub}| + |E_{sub}|)$ to eliminate LLM attention degradation ("lost-in-the-middle").
   - **Section 3.4 Risk-Adaptive Decision Gate:** Rigorously refined the mathematical formulation of $D(U_{sem}, \text{QoT}_{valid}) \to \{\text{approve}, \text{clarify}, \text{replan}\}$ and GN model equations ($P_{ASE}$, $P_{NLI}$, $\text{GSNR}_{dB}$). Explicitly formalized the architectural mapping between the unified theoretical decision function and its decoupled fail-fast realization across Phase 3 (Semantic Gate) and Phase 6 (Physical Risk Gate), meeting IEEE Transactions / ACM SIGCOMM rigor and Flesch readability standards.
   - **Section 3.5 Formal HITL via Reverse Prompting:** Rigorously drafted and formalized Section 3.5, defining Reverse Translation Invariance $T_{inv}$, Layer 2 semantic divergence $d_{sem} = \text{Score}_{divergence}$, conditional triggering $Trig_{clarify}$, and Theorem 3.1 (Finite HITL Refinement Convergence). Aligned Section 3.4.2 $d_{sem}$ notation with codebase reality.
   - **Drafting Backlog:** Created [[thesis_drafts/Drafting_Backlog]] to capture forward-looking clarifications (e.g., Phase 1 ITU-T grid enrichment) for future chapters.

2. **Decoupled Reverse Prompting & Conditional Risk-Adaptive HITL:**
   - **Phase 3a (`reverse_prompt_node`):** Decoupled automated PDDL $\to$ NL reconstruction ($\mathcal{I}_{recon}$), running autonomously with **0 human interrupts**.
   - **Phase 3 (`semantic_gate_node`):** Evaluates semantic uncertainty $U_{sem}$. If $U_{sem} \le \tau_{sem}$ (0.3), routes directly to `symbolic_solver` (Phase 4) with **0 human pauses**.
   - **Phase 3b (`hitl_clarify_node`):** Pauses via `interrupt()` only when semantic clarity is compromised ($U_{sem} > \tau_{sem}$ or grammar failure), allowing targeted operator feedback to loop back to `pddl_parser`.
   - **Phase 3b Hardening (BUG-008):** Eliminated inadmissible `"approve"` action from Phase 3b clarification interrupt options (`hitl_clarify_node`), ensuring rejected PDDL constraints cannot bypass the Semantic Gate, with defensive fallback to `hitl_approved=False` and synchronized unit tests.
   - Updated graph topology in `src/core/graph.py` and synchronized feature docs (`reverse_prompt.md`, `semantic_gate.md`, `pipeline_graph.md`, `Architecture_v5.md`).

3. **Full CFG AST Parser & Deterministic Node Exclusion (`avoid-node`):**
   - **S-expression AST Parser (`src/core/pddl_validator.py`):** Replaced legacy regex checking with a full recursive S-expression tokenizer and AST parser (`parse_pddl_ast()`), strictly enforcing balanced parentheses, required sections (`:domain`, `:objects`, `:init`, `:goal`), and formal predicate typing/arity.
   - **Symbolic Solver Node Pruning (`src/core/symbolic_solver.py`):** Implemented parsing for `(avoid-node <node>)` / `(avoid-nodes ...)` and topological vertex pruning ($\widetilde{V}_{sub} = V_{sub} \setminus \{ u \mid \text{avoid-node}(u) \in \mathcal{S}_{PDDL} \}$), verifying intermediate node traversals and returning clean diagnostics if endpoints are excluded.

4. **Kimi API Optimization & Test Suite Expansion:**
   - Handled dynamic model kwargs in `src/core/llm.py` (`temperature=0.6` when thinking disabled, `1.0` when reasoning enabled) to avoid API rejection.
   - Expanded unit test coverage in `test_pddl_validator.py` and `test_symbolic_solver.py`, bringing the test suite to **268 passing tests** (100% success rate, +13 new tests).

---

## 3. Issue List This Week

### Issue 1 (SOLVED)
- **Issue:** Theoretical formulation in Section 3.1 initially asserted per-link heterogeneous parameters and dual-sided receiver power bounds not enforced in code.
- **What has already been tried:** Audited `models.py` and `qot_calculator.py`, formalized Assumptions 1 and 2, and updated the receiver bound to $P_{rx}(\pi) \ge P_{rx, min}$.
- **Result:** SOLVED. Perfect alignment between thesis mathematics and codebase.

### Issue 2 (SOLVED)
- **Issue:** Regex-based PDDL validation permitted structural malformations and lacked predicate arity enforcement.
- **What has already been tried:** Built a recursive S-expression lexer and AST parser in `src/core/pddl_validator.py`.
- **Result:** SOLVED. Syntactic hallucinations are blocked deterministically.

### Issue 3 (SOLVED)
- **Issue:** Symbolic solver lacked support for operator node exclusion constraints (`avoid-node`).
- **What has already been tried:** Added constraint parsing and graph vertex pruning in `src/core/symbolic_solver.py`.
- **Result:** SOLVED. Validated with dedicated unit tests.

### Issue 4 (SOLVED)
- **Issue:** Reverse Prompting coupled reconstruction with mandatory `interrupt()`, violating the risk-adaptive principle.
- **What has already been tried:** Decoupled reconstruction (Phase 3a, automated) from human clarification (Phase 3b, conditional on $U_{sem} > \tau_{sem}$).
- **Result:** SOLVED. Zero-interrupt pass achieved for unambiguous intents.

### Issue 5 (SOLVED)
- **Issue:** Kimi API rejected requests when `temperature` did not match thinking status.
- **What has already been tried:** Added dynamic temperature configuration in `src/core/llm.py`.
- **Result:** SOLVED. Stabilized both reasoning and highspeed modes.

### Issue 6 (PENDING)
- **Issue:** Physical testbed returns 0 connections for `infrastructure-eth`.
- **What has already been tried:** Handled gracefully via `MockTestbedClient`.
- **Result:** PENDING provisioning for live run (Exp 4.3).

### Issue 7 (PENDING)
- **Issue:** Kimi API billing cycle quota exhaustion during live benchmark runs.
- **What has already been tried:** Added test guards (`pytest.skip`) to prevent build failures.
- **Result:** PENDING quota refresh or key renewal.

### Issue 8 (SOLVED)
- **Issue:** In Phase 3b (`hitl_clarify_node`), the interrupt options included `"approve"`, allowing operators to bypass semantic gate rejection and risk deploying unrefined or contradictory PDDL constraints.
- **What has already been tried:** Removed `"approve"` from interrupt options (`["clarify", "refine", "cancel"]`), forced `hitl_approved=False` on clarification, and added test assertions.
- **Result:** SOLVED. Fully validated with zero regressions across all 268 tests.

---

## 4. Plan for Next Week

1. **Sprint 4 Test Corpus Preparation (Exp 4.0 & Exp 4.1):** Finalize the 20–30 intent synthetic test corpus on the 17-node German network and execute offline baseline benchmarks comparing Risk-Adaptive HITL vs No-HITL vs Always-HITL.
2. **Drafting Chapter 4:** Begin drafting Section 4.1 and Section 4.2 detailing the LangGraph orchestrator implementation and physical engine port.

---

## 5. Do I Need Support?

No blockers at this time. The thesis drafts, architectural refactoring, AST CFG parser, and test suite are fully synchronized and progressing on schedule.

---

## 6. One-Sentence Summary

I completed and refined Sections 3.1 through 3.5 of Chapter 3, formalized HITL Reverse Prompting and convergence guarantees, hardened Phase 3b against invalid operator approval (BUG-008), and maintained 100% passing status across 268 unit tests.

---

## 7. Self-Check Before Submission

- [x] I have clearly written the planned goals and actual progress for this week
- [x] I have listed all issues encountered this week
- [x] I have clearly written my plan for next week
- [x] I have indicated whether I need support
