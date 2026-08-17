---
title: "Session Summary: Nobel-Germany 17-Node Topology Migration"
date: 2026-08-17
tags: [session, summary, mock-topology, nobel-germany, edfa, qot, graphrag, sprint3]
status: active
---

# Session Summary: Nobel-Germany 17-Node Topology Migration

## Date: 2026-08-17

## Overview
Following the recommendations from the August 11 advisory meeting ([[transcriptions/Transcript_20260811_ThesisOutline_MockTopology]]), this session focused on migrating the mock testbed from the simplified 3-node linear lab topology (`Milano-A ↔ Milano-B ↔ Milano-C`) to the standard **Nobel-Germany 17-node, 26-link optical backbone network** (SNDlib benchmark). This equips the Neurosymbolic Intent Planning Orchestrator with a realistic meshed topology, long-distance multi-span fiber links, intermediate inline amplifiers (ILAs), and calibrated physical power levels for accurate Quality of Transmission (QoT) assessment via the GN-model.

## What was Accomplished?

1. **Nobel-Germany Topology Implementation in `MockTestbedClient`:**
   - Authored the complete 17-node optical topology in [testbed_client.py](file:///home/felipeab/MultiAgentON/src/services/testbed_client.py) using standardized English city names: `Hannover`, `Frankfurt`, `Hamburg`, `Norden`, `Bremen`, `Berlin`, `Munich`, `Ulm`, `Nuremberg`, `Stuttgart`, `Karlsruhe`, `Mannheim`, `Essen`, `Dortmund`, `Dusseldorf`, `Cologne`, `Leipzig`.
   - Modeled 26 standard physical bidirectional fiber links with realistic distances (spanning 37.5 km to 381.9 km).

2. **Optical Physical Calibration (EDFA & GN-Model):**
   - Implemented `_build_link_amplifiers()` with realistic physical amplifier placement:
     - **Booster EDFA** ($0.0\text{ km}$): Calibrated at $3.0\text{ dB}$ gain to offset intermediate node traversal loss without power accumulation across multi-hop paths.
     - **Inline Amplifiers (ILAs)**: Placed every $\approx 70\text{ km}$ on links $> 55\text{ km}$, compensating span attenuation ($\alpha = 0.25\text{ dB/km}$) and connector losses ($2.0\text{ dB}$).
     - **Preamplifier EDFA** ($L\text{ km}$): Compensates final span loss before drop/demux.
   - Maintained stable channel power levels throughout multi-hop lightpaths ($-15\text{ dBm}$ to $-11\text{ dBm}$), guaranteeing physically feasible GSNR ($11\text{ dB}$ to $23\text{ dB}$) at 100G and realistic infeasibility at 200G/strict GSNR constraints without Kerr non-linear saturation.

3. **Pipeline Prompt & CLI Synchronization:**
   - Updated system prompts and structured output models in [intent_ingest.py](file:///home/felipeab/MultiAgentON/src/nodes/intent_ingest.py) and [pddl_parser.py](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) to reference core German cities.
   - Updated [main.py](file:///home/felipeab/MultiAgentON/src/main.py) CLI entrypoint with Nobel-Germany routing queries.

4. **Test Suite Expansion (Strict TDD):**
   - Added `TestNobelGermanySymbolicSolver` in `test_symbolic_solver.py` verifying multi-path enumeration ($K$-shortest paths) and `avoid-link` constraint filtering on the meshed German network.
   - Added `TestNobelGermanyGraphRAG` in `test_mock_graphrag.py` verifying $k$-hop subgraph context bounding.
   - Added `TestNobelGermanyQoT` in `test_qot_calculator.py` verifying QoT feasibility across single links and a $>1000\text{ km}$ 4-hop trans-Germany route (`Hamburg → Berlin → Leipzig → Nuremberg → Munich`).
   - All **233 unit tests** passing with 100% success.

5. **Version Control & Documentation:**
   - Committed pending wiki documentation to `main` and pushed to remote.
   - Created and published feature branch `feat/17-node-german-mock-topology`.
   - Updated feature documentation in [[architecture/features/testbed_client]].

## Next Steps: Sprint 4 Readiness

With the 17-node German backbone topology fully operational in the orchestrator pipeline, the preparatory scaffolding is complete. **Sprint 4 is ready to begin in the next session:**

1. **Sprint 4 (Exp 4.0):** Design and formalize the structured **Synthetic Test Corpus (20–30 intents)** spanning the three risk categories mapped to the 17-node German topology:
   - *Safe & Clear*: Feasible lightpaths with low semantic ambiguity $\to$ Expected outcome: `auto-approve`.
   - *Ambiguous Intent*: Missing constraints or contradictory requests $\to$ Expected outcome: early `clarify` via $U_{sem}$.
   - *Infeasible Physical QoT*: Overly long lightpaths or strict GSNR/bitrate targets exceeding physical limits $\to$ Expected outcome: `suggest-replan` via RADG.
2. **Sprint 4 (Exp 4.1):** Execute baseline comparisons evaluating the Risk-Adaptive HITL pipeline against No-HITL and Always-HITL baselines across the evaluation metrics: Unsafe Approval Rate (UAR), Human Interaction Count (HIC), QoT Feasibility Rate (QFR), and Token Cost (TC).
