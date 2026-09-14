---
title: "Session Summary: Local Ollama Multi-Model Profiling, Hardware Architecture Audit & Reasoning Support"
date: 2026-09-14
tags: [session-summary, ollama, local-llm, qwen3.5, gemma4, qwen2.5, thinking, hardware-audit, rtx-3050, strict-tdd]
status: active
---

# Session Summary: Local Ollama Multi-Model Profiling, Hardware Architecture Audit & Reasoning Support

## 1. Executive Summary

In this session, I conducted a comprehensive hardware architecture audit, empirical profiling, and system-wide integration for local open-weights LLM inference via Ollama, targeting:
- **`qwen2.5:3b`** (Alibaba Qwen 2.5, 3.1B params, 1.9 GB binary) — **Recommended Default**.
- **`phi4-mini:latest`** (Microsoft Phi-4 Mini, 3.8B params, 2.49 GB binary, fast & structured).
- **`qwen3:4b`** (Alibaba Qwen 3 family, 4.0B params, 2.50 GB binary, native reasoning / `<think>`).
- **`qwen3.5:4b`** (Alibaba Qwen 3.5, 4.7B params, 3.4 GB binary, native reasoning).
- **`gemma4:e4b`** (Google Gemma 4, 8.0B params, 9.6 GB binary, heavy CPU offload).

Key architectural outcomes:
1. **Empirical Proof of Default Model Selection:** On NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM, 8 GB system RAM), **`qwen2.5:3b` is the optimal default** because it resides 100% in VRAM (2.15 GB), delivering ~1.5s latency at ~70 tok/s. `phi4-mini:latest` (~2.8 GB VRAM) serves as the strongest direct non-reasoning alternative (~12s latency, high structural compliance). `qwen3:4b` provides deep chain-of-thought reasoning but requires partial system RAM offloading and 3000 tokens budget.
2. **Native Reasoning / Thinking Token Support:** Maintained regex stripping of `<think>...</think>` in [`OllamaChatOpenAI.with_structured_output`](file:///home/felipeab/MultiAgentON/src/core/llm.py) and [`_strip_code_fences`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py), and scaled default completion tokens to 3000 for reasoning models (`qwen3`, `qwen3.5`, `gemma4`).
3. **Interactive CLI & Benchmark Integration:** Added full multi-model selection menus and CLI flags in [`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py) and [`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py).
4. **End-to-End Live Pipeline Verification:** Verified `phi4-mini:latest` through all 7 neurosymbolic pipeline phases in `src/main.py`, successfully triggering semantic clarification ($U_{sem}=0.50$), physical RADG replanning (0/5 feasible lightpaths at 15 dB GSNR), operator constraint relaxation (12 dB GSNR), and final auditable planning report generation with GN-model feasibility verification.

All 347 unit tests pass with zero regressions under Strict TDD, and the full codebase passes all `ruff` lint checks.

---

## 2. Key Accomplishments & Technical Deliverables

### 2.1 Hardware Architecture Audit & Empirical Profiling
- **Deployment Platform:** Intel Core i5-12450H, 8 GB system RAM (~5.3 GB available), NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM).
- **Physical Allocation & Performance Matrix:**
  | Metric | `qwen2.5:3b` (Default) | `phi4-mini:latest` (Direct) | `qwen3:4b` (Reasoning) | `qwen3.5:4b` (Reasoning) | `gemma4:e4b` (Heavy 8B) |
  | :--- | :--- | :--- | :--- | :--- | :--- |
  | **Parameter Count** | 3.1B | 3.8B | 4.0B | 4.7B | 8.0B |
  | **Binary Size (Q4_K_M)** | 1.9 GB | 2.49 GB | 2.50 GB | 3.4 GB | 9.6 GB |
  | **VRAM Consumption** | **2.15 GB (100% in VRAM)** | ~2.80 GB | ~2.35 GB | 1.87 GB | 1.46 GB |
  | **System RAM Offload** | **0.00 GB** | 0.00 GB (Low context) | ~1.18 GB | 1.85 GB | **8.04 GB (Paging / Swap)** |
  | **Native Thinking** | Direct | Direct | Yes (`<think>`) | Yes (`<think>`) | Yes (`<think>`) |
  | **Typical Latency** | **~1.5s - 2.0s** (~70 tok/s) | ~12.8s | ~30s - 90s | ~25s - 45s | ~20s - 60s |
  | **Architectural Verdict** | **GOLD STANDARD DEFAULT** | **Best Direct Alternative** | Selectable (Deep Reasoning) | Selectable (Reasoning) | Selectable (CPU Bound) |

### 2.2 Core LLM Engine Updates ([`src/core/llm.py`](file:///home/felipeab/MultiAgentON/src/core/llm.py))
- Expanded `SUPPORTED_OLLAMA_MODELS` to include `"qwen3:4b"` and `"phi4-mini:latest"`.
- Configured dynamic token budgeting in `create_ollama_llm()`: allocates 3000 max tokens for thinking models (`qwen3`, `qwen3.5`, `gemma4`) and 2000 tokens for direct models (`qwen2.5`, `phi4-mini`).

### 2.3 CLI & Benchmark Harness Integration
- **Interactive CLI ([`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py)):** Added explicit Questionary options and CLI flags (`--model phi4-mini:latest`, `--model qwen3:4b`).
- **Benchmark Runner ([`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py)):** Added model labels for `phi4-mini` (`🔬 3.8B Params | Fast & Structured`) and `qwen3` (`🧠 4.0B Params | Native Reasoning`).
- **Environment Reference ([`.env`](file:///home/felipeab/MultiAgentON/.env)):** Documented all local models and set `OLLAMA_MODEL="qwen2.5:3b"` as recommended default.

### 2.4 Integration Tests with Safe Memory Deallocation ([`tests/integration/test_ollama_configurations.py`](file:///home/felipeab/MultiAgentON/tests/integration/test_ollama_configurations.py))
- Parametrized `test_ollama_multi_model_pddl_comparison` across all five local models.
- Automated `_unload_model(model_name)` with `keep_alive=0` in teardown blocks for all non-default models to guarantee zero VRAM/RAM leakage.

---

## 3. Verification & Test Suite Status

- **Unit Tests:** `uv run pytest tests/unit/` $\to$ **347 passed, 3 warnings in 4.57s** (100% pass rate).
- **Integration Tests:**
  - `phi4-mini:latest` PDDL comparison $\to$ **PASSED in 13.85s** (Latency: 12.88s, PDDL Valid: True).
  - `qwen2.5:3b` PDDL comparison $\to$ **PASSED in 2.95s** (Latency: 2.02s, PDDL Valid: True).
- **End-to-End CLI Run with `phi4-mini:latest`:**
  - Executed full 7-phase neurosymbolic pipeline with interactive HITL clarify and RADG replanning loops.
  - Final Planning Report synthesized with valid GN-model GSNR margins (+1.93 dB on Berlin → Hannover → Frankfurt).
- **Linter & Code Style:** `uv run ruff check src/ tests/` $\to$ **All checks passed**.

---

## 4. Handover & Next Steps

1. **Thesis Defense Slide 14 Integration:** Embed empirical local GPU benchmark metrics and multi-model hardware comparison into defense deck.
2. **Sprint 4 Evaluation Corpus:** Execute evaluation harness across the balanced 20-demand compact corpus on Nobel-Germany 17-node topology.
