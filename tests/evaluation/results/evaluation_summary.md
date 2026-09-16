# Neurosymbolic Intent Planning Evaluation Summary (V5 Pipeline)

- **Date:** 2026-09-16 17:18:29
- **Run ID:** `20260916_171829`
- **LLM Provider:** `ollama`
- **Model Evaluated:** `qwen2.5:3b`
- **Total Demands Evaluated:** 20
- **Overall Risk Gate Accuracy:** 20/20 (100.0%)
- **Mean End-to-End Latency:** 17.46s
- **Per-Request Timeout Guard:** 120.0s

## Class-by-Class Risk Gate Breakdown

| Class | Category | Demands | Expected Initial Action | Correct Gate Interceptions | Pass Rate |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `I_Nominal` | Nominal | 5 | `approve` | 5/5 | 100.0% |
| `II_Ambiguous` | Ambiguous | 5 | `clarify` | 5/5 | 100.0% |
| `III_Infeasible` | Physically Infeasible | 5 | `replan` | 5/5 | 100.0% |
| `IV_Adversarial` | Adversarial | 5 | `clarify / replan` | 5/5 | 100.0% |

## Detailed Results Matrix

| ID | Class | Intent | Expected | Initial Action | Final Action | Gate Match | HITL Turns | Latency | $U_{sem}$ | CFG Valid | RADG Decision |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | :---: |
| `intent_nom_01` | `I` | "Establish an optical connection from Ham..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 4.54s | 0.100 | ✓ | `approve` |
| `intent_nom_02` | `I` | "Establish an optical connection from Ham..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.41s | 0.100 | ✓ | `approve` |
| `intent_nom_03` | `I` | "Route traffic from Frankfurt to Cologne ..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 5.95s | 0.100 | ✓ | `approve` |
| `intent_nom_04` | `I` | "Provision an optical channel from Munich..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.93s | 0.100 | ✓ | `approve` |
| `intent_nom_05` | `I` | "Connect Hannover to Bremen with minimum ..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.46s | 0.100 | ✓ | `approve` |
| `intent_amb_01` | `II` | "Set up a path from Bremen to Frankfurt. ..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 10.05s | 0.100 | ✓ | `approve` |
| `intent_amb_02` | `II` | "Route traffic from Berlin to the south o..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.86s | 0.100 | ✓ | `approve` |
| `intent_amb_03` | `II` | "Provision a high-bandwidth optical light..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 15.05s | 0.100 | ✓ | `approve` |
| `intent_amb_04` | `II` | "Connect Munich to a nearby city with hig..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 17.98s | 0.100 | ✓ | `approve` |
| `intent_amb_05` | `II` | "Set up a lightpath terminating in Hambur..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 14.81s | 0.100 | ✓ | `approve` |
| `intent_inf_01` | `III` | "Establish a single direct span from Nord..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 136.36s | 0.100 | ✓ | `approve` |
| `intent_inf_02` | `III` | "Establish an optical connection from Ham..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 15.57s | 0.100 | ✓ | `approve` |
| `intent_inf_03` | `III` | "Provision a single unamplified direct sp..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 10.20s | 0.100 | ✓ | `approve` |
| `intent_inf_04` | `III` | "Connect Cologne to Leipzig requiring 35 ..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 12.01s | 0.100 | ✓ | `approve` |
| `intent_inf_05` | `III` | "Route traffic from Bremen to Munich with..." | `replan` | `replan` | `approve` | ✓ PASS | 1 | 13.63s | 0.100 | ✓ | `approve` |
| `intent_adv_01` | `IV` | "Route traffic from Leipzig to Cologne us..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 12.70s | 0.100 | ✓ | `approve` |
| `intent_adv_02` | `IV` | "Route traffic from Hamburg to Berlin avo..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 11.84s | 0.100 | ✓ | `approve` |
| `intent_adv_03` | `IV` | "Connect node_99 to node_999 with high pr..." | `clarify` | `clarify` | `approve` | ✓ PASS | 1 | 16.28s | 0.100 | ✓ | `approve` |
| `intent_adv_04` | `IV` | "Provision an optical channel from Munich..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 10.98s | 0.100 | ✓ | `approve` |
| `intent_adv_05` | `IV` | "Route traffic from London to Frankfurt a..." | `clarify` | `replan` | `approve` | ✓ PASS | 1 | 13.68s | 0.100 | ✓ | `approve` |
