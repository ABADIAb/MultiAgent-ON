---
title: "Session Summary: Bandwidth SLA Mapping, Corpus Rebalancing & RADG Action Normalization"
date: 2026-09-12
tags: [session-summary, bandwidth, sla, pddl, qot, gn-model, test-corpus, radg, excel]
status: active
---

# Session Summary: Bandwidth SLA Mapping, Corpus Rebalancing & RADG Action Normalization

## Overview
This session integrated real-world optical bandwidth and capacity SLA constraints into the neurosymbolic intent planning pipeline, calibrated the physical GN-model SNR threshold for 400G transmission, expanded the synthetic benchmark corpus to 107 balanced demands, generated a publication-ready Excel spreadsheet in `docs/LLM_Wiki/raw/`, and normalized the benchmark action space to strictly adhere to the thesis's formal ternary RADG action space $\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$.

---

## 1. Key Accomplishments

### 1.1 Bandwidth & Capacity SLA Constraint Mapping
- **Context-Free Grammar (CFG) Extension**: Updated [`src/core/pddl_validator.py`](file:///home/felipeab/MultiAgentON/src/core/pddl_validator.py) with the production rule `(bandwidth <int>)` in the S-expression tokenizer and goal predicate validator.
- **Symbolic Solver Adaptation**: Updated [`src/core/symbolic_solver.py`](file:///home/felipeab/MultiAgentON/src/core/symbolic_solver.py) to parse `(bandwidth <n>)` and preserve it in `pddl_parsed_constraints["bandwidth"]`.

### 1.2 Adaptive Physical-Layer GN-Model Thresholding
- **Physical Constants Calibration**: Added `snr_threshold_400g_dB = 21.5` in [`src/core/constants.py`](file:///home/felipeab/MultiAgentON/src/core/constants.py) to account for higher-order modulation (e.g. 16-QAM vs QPSK/100G at $14.5\text{ dB}$).
- **QoT Validation Node Wiring**: Connected dynamic threshold selection in [`src/nodes/qot_validation.py`](file:///home/felipeab/MultiAgentON/src/nodes/qot_validation.py):
  $$\text{threshold} = \begin{cases} 21.5\text{ dB} & \text{if } \text{bandwidth} \ge 400 \\ 14.5\text{ dB} & \text{otherwise} \end{cases}$$
  This enables deterministic detection of physical infeasibility on long multi-hop paths on Nobel-Germany 17-node topology without requiring mock workarounds.

### 1.3 LLM Prompt Alignment (Reverse Prompting Calibration)
- **Problem**: When testing the initial intent *"Establish an optical connection from Hamburg to Berlin with 100G capacity"*, the Reverse Prompting node omitted the capacity in its natural language reconstruction $\mathcal{I}_{recon}$, causing the Semantic Gate to calculate a high divergence ($d_{sem} > \tau_{sem}$) and trigger an unnecessary HITL clarification loop.
- **Fix**: Calibrated system prompts in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py) and [`src/nodes/reverse_prompt.py`](file:///home/felipeab/MultiAgentON/src/nodes/reverse_prompt.py) to explicitly mandate tracking and verbalizing bitrate/capacity SLA requirements, ensuring seamless automated approval for nominal intents.

### 1.4 Synthetic Benchmark Corpus Expansion & Categorization
- Expanded [`tests/evaluation/test_corpus.json`](file:///home/felipeab/MultiAgentON/tests/evaluation/test_corpus.json) to **107 intents**, sequentially ordered and numbered by category:
  - **Class I (`I_Nominal`)**: 28 intents (`intent_nom_01` to `intent_nom_28`)
  - **Class II (`II_Ambiguous`)**: 26 intents (`intent_amb_01` to `intent_amb_26`)
  - **Class III (`III_Infeasible`)**: 27 intents (`intent_inf_01` to `intent_inf_27`)
  - **Class IV (`IV_Adversarial`)**: 26 intents (`intent_adv_01` to `intent_adv_26`)
- Injected diverse bandwidth SLA test cases across all four categories:
  - 100G/200G nominal lightpaths (`intent_nom_01`, `intent_nom_27`, `intent_nom_28`).
  - Ambiguous soft bandwidth SLA (`intent_amb_26`).
  - Infeasible 400G demands across long multi-hop routes exceeding SNR budgets (`intent_inf_26`, `intent_inf_27`).
  - Adversarial bandwidth injection ("infinite bandwidth", `intent_adv_26`).

### 1.5 Excel Corpus Summary Workbook Generation
- Programmatically generated [`docs/LLM_Wiki/raw/test_corpus_summary.xlsx`](file:///home/felipeab/MultiAgentON/docs/LLM_Wiki/raw/test_corpus_summary.xlsx) using `openpyxl`.
- Structured with columns: *Intent ID*, *Class*, *Intent Text*, *Expected U_sem Action*, *Expected RADG Action*, and *Rationale*.
- Formatted with frozen header pane, soft pastel color coding per risk class, and auto-adjusted column dimensions.

### 1.6 RADG Action Space Normalization
- **Resolution of Inconsistency**: Identified that 24 intents in Class IV were erroneously marked with `"expected_radg_action": "reject"`.
- As proven by [`src/core/radg.py`](file:///home/felipeab/MultiAgentON/src/core/radg.py) and [[ProblemStatement_v5]], the formal RADG action space is ternary:
  $$\mathcal{A} = \{\text{approve}, \text{clarify}, \text{replan}\}$$
  Adversarial intents are intercepted early at Phase 3b via the fail-fast principle ($U_{sem} > \tau_{sem} \lor v_{struct} = 0$), yielding action `clarify`.
- Normalized all 107 records in `test_corpus.json`, updated the Excel summary sheet, and updated [`tests/evaluation/README.md`](file:///home/felipeab/MultiAgentON/tests/evaluation/README.md).

---

## 2. Verification & Test Outcomes
- All **294 unit tests** passed with 100% success (`uv run pytest`).
- Zero regressions in existing pipeline flows or testbed adapters.

---

## 3. Related Documents
- [[weekly_reports/Weekly_Report_20260915_Felipe_Abadia]]
- [[issues/Issue_Report_20260915_Felipe_Abadia]]
- [[architecture/features/pddl_parser]]
- [[architecture/features/symbolic_solver]]
- [[architecture/features/qot_tool]]
- [[architecture/Architecture_v5]]
- [[architecture/ProblemStatement_v5]]
