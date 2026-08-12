---
title: "Bug Registry & Resolution Log"
date: 2026-08-07
tags: [experiments, bugs, fixes, neurosymbolic, qot, radg, pddl]
status: active
---

# Bug Registry & Resolution Log

This document tracks technical bugs, edge cases, semantic drifts, and physical-layer anomalies discovered during interactive testing and execution of the [[wiki/architecture/Architecture_v5|Neurosymbolic Intent Orchestration Pipeline]], along with their root cause analyses and verified resolutions.

---

## 1. Bug Index & Summary

| Bug ID | Component / Phase | Summary | Status | Date Resolved | Commit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-001** | `qot_calculator` / `symbolic_solver` | GSNR threshold from PDDL constraints ignored during QoT validation | **Resolved** | 2026-08-07 | `c441318` |
| **BUG-002** | `radg_node` / `pddl_parser` | Refinement loopback ignored human `interrupt()` input and retained stale constraints | **Resolved** | 2026-08-07 | `c441318` |
| **BUG-003** | `qot_calculator` / `models` | GN-model NLI explosion (-47 dB GSNR) on short spans due to fixed +43 dB EDFA gain | **Resolved** | 2026-08-07 | `d79e400` |
| **BUG-004** | `mock_graphrag` / `pddl_parser` | Synthetic node ID leakage (`node_1`) in Reverse Prompting instead of human-readable names | **Resolved** | 2026-08-07 | `d79e400` |
| **BUG-005** | `core/state.py` & `core/models.py` | Schema duplication & type warnings between domain models and state schema | **Resolved** | 2026-08-07 | `d79e400` |

---

## 2. Detailed Bug Reports & Resolutions

### BUG-001: GSNR Threshold Ignored in Symbolic Solver & QoT Calculator

- **Discovered By**: User CLI testing (`Route traffic from Milano-A to Milano-C requiring 40 dB GSNR`).
- **Symptom**: Intent explicitly demanded a high GSNR threshold (40 dB). The [[wiki/concepts/Semantic_Gate|Semantic Gate]] approved the intent, but the [[wiki/concepts/RADG|RADG]] node also approved the physical path even though the calculated GSNR was **21.76 dB** (unfeasible).
- **Root Cause**:
  1. `src/core/symbolic_solver.py` did not extract `min-gsnr` from the PDDL string regex.
  2. `src/core/qot_calculator.py` (`assess_qot`) ignored `target_snr_dB` and defaulted to a static 15.0 dB safety threshold.
  3. `src/nodes/qot_validation.py` failed to forward the extracted `min_gsnr` constraint from `pddl_constraints` to the physics engine.
- **Resolution**:
  - Updated PDDL constraint extraction in `symbolic_solver.py` to parse `(>= (gsnr-db) X)`.
  - Updated `assess_qot()` in `qot_calculator.py` to accept `target_snr_dB` and enforce `max(target_snr_dB, DEFAULT_THRESHOLD)`.
  - Updated `qot_validation_node` to pass `min_gsnr` directly to `assess_qot()`.
- **Verification**: `tests/unit/test_symbolic_solver.py` and `tests/unit/test_qot_calculator.py` test cases added.

---

### BUG-002: Refinement Feedback Loop Ignored Human `interrupt()` Input

- **Discovered By**: User CLI testing during HITL refinement (`Not 40dB but 15dB`).
- **Symptom**: When RADG flagged an unfeasible GSNR and triggered `interrupt()` for user refinement, the user provided updated constraints. However, the system re-executed the pipeline using the **old** 40 dB constraint, generating an endless failure loop.
- **Root Cause**:
  - `src/nodes/radg_node.py` called `interrupt()`, but failed to capture the return value (the user's response string) and did not update `state["error_context"]`.
  - As a result, when routing back to `pddl_parser_node`, `error_context` was empty, causing the parser to regenerate constraints from scratch without incorporating the user's intent refinement.
- **Resolution**:
  - Captured `user_response = interrupt(...)` inside `radg_node.py`.
  - Formatted a comprehensive error/refinement message and updated `state["error_context"]`.
  - Allowed `pddl_parser_node` to read `error_context` and prompt the LLM to refine the PDDL parameters dynamically.
- **Verification**: Unit tests in `tests/unit/test_radg.py` and E2E script `scratch/test_refine_loopback.py`.

---

### BUG-003: GN-Model NLI Explosion (-47 dB GSNR) on Short Spans

- **Discovered By**: Automated unit tests & physical verification of 3-node testbed topology.
- **Symptom**: Short fiber spans (e.g., 5 km - 10 km) yielded negative GSNR values (-47 dB) or crashed the GN-model calculation due to extreme Non-Linear Interference (NLI).
- **Root Cause**:
  - Amplifier gains (EDFA boosters and preamps) were hardcoded to fixed +43 dB gains regardless of span attenuation.
  - On a 10 km span with ~2 dB attenuation, a +43 dB gain boosted optical channel power to ~2 Watts (33 dBm), pushing the fiber deep into non-linear saturation where NLI noise dominated the signal.
- **Resolution**:
  - Calibrated booster and preamp gains in `src/core/models.py` and `qot_calculator.py` to match exact span attenuation (~7 dB for short spans), ensuring channel launch power remains near optimal (~0 dBm / 1 mW).
- **Verification**: `tests/unit/test_qot_calculator.py` passing with realistic GSNR values (20 dB - 28 dB).

---

### BUG-004: Node ID Leakage (`node_1`) in Reverse Prompting

- **Discovered By**: E2E pipeline runs during Phase 3 (Reverse Prompting).
- **Symptom**: LLM reconstructed NL intent using synthetic IDs like `node_1` and `node_2` instead of human-readable topology locations (`Milano-A`, `Milano-C`).
- **Root Cause**:
  - `src/core/mock_graphrag.py` and internal topology snapshots exposed generic node IDs (`node_1`, `node_2`), which propagated into PDDL constraint generation and reverse prompt templates.
- **Resolution**:
  - Standardized node naming across `mock_graphrag.py`, `pddl_parser.py`, and `state.py` to strictly use human-readable optical site labels (e.g. `Milano-A`, `Milano-B`, `Milano-C`, `Roma-A`).
- **Verification**: Verified via `test_pipeline_nodes.py` and CLI execution logs.

---

### BUG-005: Schema Duplication Across `state.py` and `models.py`

- **Discovered By**: Static type checker (`pyright` / `mypy`) audit.
- **Symptom**: Type warnings and schema drift caused by dual definitions of `FiberLink` and `NetworkNode` in both `src/core/state.py` and `src/core/models.py`.
- **Root Cause**: `state.py` created independent dataclasses/TypedDicts instead of importing canonical Pydantic domain models from `models.py`.
- **Resolution**:
  - Centralized domain models into `src/core/models.py`.
  - Updated `src/core/state.py` to import and reference models from `models.py`.
- **Verification**: 227 passing unit tests (`pytest`).
