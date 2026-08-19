---
title: "Issue Report 2026-08-24"
date: 2026-08-24
tags: [issues, report, mock-topology, nobel-germany, edfa, qot, symbolic-solver, pddl]
status: active
---

# Issue Report: 2026-08-24

## 1. 3-Node Testbed Numerical Evaluation Limitation (SOLVED)
- **Issue:** The physical lab testbed and previous mock consisted of only 3 nodes in a linear chain with short spans (<1 km in lab, 20/40 km in mock), lacking intermediate inline amplifiers (ILAs) and multi-path routing diversity for comprehensive baseline evaluation.
- **What has already been tried:** Migrated the mock environment to the 17-node, 26-link **Nobel-Germany** optical backbone network from SNDlib, modeling realistic span lengths (37.5 km to 381.9 km) and ILAs every ~70 km.
- **Result:** SOLVED. The symbolic solver now finds rich multi-path candidates and QoT calculations evaluate multi-hop long-distance routes realistically.

## 2. Multi-Hop Power Accumulation & NLI Distortion (SOLVED)
- **Issue:** On multi-hop lightpaths across the 17-node German topology, cascading booster and preamp gains caused optical power to accumulate (+7 dBm), triggering severe non-linear interference ($NLI \propto P^3$) in the GN-model and degrading SNR to negative values.
- **What has already been tried:** Calibrated booster gains to 3.0 dB (matching node pass-through loss) and set ILA/preamp gains to strictly offset preceding span attenuation and connector losses.
- **Result:** SOLVED. Channel power remains stable between $-15\text{ dBm}$ and $-11\text{ dBm}$ across $>1000\text{ km}$ routes, yielding feasible SNR ($11-23\text{ dB}$) at 100G.

## 3. Source & Target Loss in Symbolic Solver (BUG-006) (SOLVED)
- **Issue:** When the operator requested routing between two specific nodes (e.g., Munich to Cologne), `symbolic_solver_node` reported `from 'None' to 'None'` and returned paths between default endpoints (Hannover to Leipzig).
- **What has already been tried:** Traced the parsing failure to `_parse_pddl_constraints()`, which only searched for `(source ...)` / `(destination ...)`, failing on standard PDDL goals like `(route Munich Cologne)`. Additionally, `_resolve_node_id()` lacked case-insensitive matching, and missing endpoints triggered an unhandled silent fallback.
- **Result:** SOLVED. Expanded `_parse_pddl_constraints()` to support all PDDL route goal variations (`route`, `routed`, `path`, `target`), implemented case-insensitive node resolution, and added fallback to `state["enriched_intent"]`. Verified with 9 new unit tests.

## 4. Unprovisioned Infrastructure Connections on Testbed (PENDING)
- **Issue:** The physical ONC controller returns 0 connections for `infrastructure-eth` when queried via RESTConf.
- **What has already been tried:** Handled gracefully via the mocked topology layer (`MockTestbedClient`), unblocking all offline algorithmic and baseline evaluations.
- **Result:** PENDING provisioning for final live testbed execution (Exp 4.3).
- **Estimated possible solution:** Connect to the live server once brought back online and provision physical DWDM links in the SM Optics ONC.

## 5. Test Corpus Generation for Baseline Evaluation (IN PROGRESS / SPRINT 4)
- **Issue:** To execute Exp 4.1, a structured dataset of 20–30 synthetic operator intents spanning Safe, Ambiguous, and Infeasible risk categories mapped to the 17-node German topology is required.
- **What has already been tried:** Topology scaffolding and multi-hop validation completed.
- **Result:** IN PROGRESS. Scheduled as the primary task for Sprint 4.
- **Estimated possible solution:** Construct synthetic intent JSON dataset mapping semantic requests to ground-truth physical and semantic risk outcomes across the 17 German cities.
