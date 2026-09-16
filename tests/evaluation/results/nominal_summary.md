# Nominal Intents Evaluation Summary (qwen2.5:3b)

- **Date:** 2026-09-16 12:32:37
- **Model:** `qwen2.5:3b` via Ollama
- **Total Intents Evaluated:** 5
- **Autonomous Pass Rate (First Try):** 2/5 (40.0%)
- **Intents Requiring HITL Follow-Up:** 3/5
- **Mean End-to-End Latency:** 14.15s
- **Request Timeout Configured:** 120.0 seconds

## Detailed Results Matrix

| ID | Intent | Expected | Initial Action | Final Action | 1st Try? | HITL | Latency | $U_{sem}$ | CFG Valid | RADG |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | -: | -: | :---: | :---: |
| `intent_nom_01` | "Establish an optical connection from Hamburg ..." | `approve` | `clarify` | `failed` | ⚠️ HITL | 3 | 14.11s | 0.500 | ✓ | `None` |
| `intent_nom_02` | "Establish an optical connection from Hamburg ..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 6.64s | 0.200 | ✓ | `approve` |
| `intent_nom_03` | "Route traffic from Frankfurt to Cologne avoid..." | `approve` | `clarify` | `approve` | ⚠️ HITL | 1 | 21.99s | 0.200 | ✓ | `approve` |
| `intent_nom_04` | "Provision an optical channel from Munich to S..." | `approve` | `clarify` | `failed` | ⚠️ HITL | 3 | 25.05s | 0.500 | ✓ | `None` |
| `intent_nom_05` | "Connect Hannover to Bremen with minimum 16 dB..." | `approve` | `approve` | `approve` | ✓ PASS | 0 | 2.94s | 0.200 | ✓ | `approve` |
