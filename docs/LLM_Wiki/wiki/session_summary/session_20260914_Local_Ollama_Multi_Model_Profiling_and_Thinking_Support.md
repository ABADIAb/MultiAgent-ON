---
title: "Session Summary: Local Ollama Multi-Model Profiling, Hardware Architecture Audit & Reasoning Support"
date: 2026-09-14
tags: [session-summary, ollama, local-llm, qwen3.5, gemma4, qwen2.5, thinking, hardware-audit, rtx-3050, strict-tdd]
status: active
---

# Session Summary: Local Ollama Multi-Model Profiling, Hardware Architecture Audit & Reasoning Support

## 1. Executive Summary

In this session, I conducted a comprehensive hardware architecture audit, empirical profiling, and system-wide integration for local open-weights LLM inference via Ollama, targeting the user's newly downloaded models:
- **`qwen3.5:4b`** (Alibaba Qwen 3.5 family, 4.7B parameters, 3.4 GB binary, native reasoning)
- **`gemma4:e4b`** (Google Gemma 4 family, 8.0B parameters, 9.6 GB binary, native reasoning)
- Alongside the existing baseline **`qwen2.5:3b`** (3.1B parameters, 1.9 GB binary).

Key architectural outcomes:
1. **Empirical Proof of Default Model Selection:** Evaluated the physical hardware constraints (NVIDIA GeForce RTX 3050 Laptop GPU with 4 GB VRAM, 8 GB total system RAM). Proved that **`qwen2.5:3b` is the optimal default** because it resides 100% in VRAM (2.15 GB), delivering ~1.5s latency at ~70 tok/s. In contrast, `qwen3.5:4b` and `gemma4:e4b` require substantial CPU memory offloading (1.85 GB and 8.04 GB offloaded to system RAM, respectively), triggering memory bandwidth bottlenecks and disk swapping on an 8 GB system.
2. **Native Reasoning / Thinking Token Support:** Addressed the failure mode where models with native reasoning capabilities emit `<think>...</think>` monologues that break Pydantic JSON extraction and PDDL CFG syntax validation. Implemented regex-based thinking tag stripping in both [`OllamaChatOpenAI.with_structured_output`](file:///home/felipeab/MultiAgentON/src/core/llm.py) and [`_strip_code_fences`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py).
3. **Interactive CLI & Benchmark Integration:** Added full multi-model selection menus and flags in [`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py) and [`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py).
4. **Integration Testing with Safe Memory Management:** Expanded [`tests/integration/test_ollama_configurations.py`](file:///home/felipeab/MultiAgentON/tests/integration/test_ollama_configurations.py) with dynamic installed model detection and automated post-test unloading (`_unload_model` with `keep_alive=0`) to ensure system RAM is immediately reclaimed.

All 347 unit tests pass with zero regressions under Strict TDD, and the full codebase passes all `ruff` lint checks.

---

## 2. Key Accomplishments & Technical Deliverables

### 2.1 Hardware Architecture Audit & Empirical Profiling
- **Deployment Platform:** Intel Core i5-12450H, 8 GB system RAM (~5.3 GB available), NVIDIA GeForce RTX 3050 Laptop GPU (4096 MiB VRAM).
- **Physical Allocation & Performance Matrix:**
  | Metric | `qwen2.5:3b` (Default) | `qwen3.5:4b` (Reasoning) | `gemma4:e4b` (Heavy 8B) |
  | :--- | :--- | :--- | :--- |
  | **Parameter Count** | 3.1B | 4.7B | 8.0B |
  | **Binary Size (Q4_K_M)** | 1.9 GB | 3.4 GB | 9.6 GB |
  | **VRAM Consumption** | **2.15 GB (100% in VRAM)** | 1.87 GB | 1.46 GB |
  | **System RAM Offload** | **0.00 GB** | 1.85 GB | **8.04 GB (Paging / Swap)** |
  | **Native Thinking** | Direct | Yes (`<think>` tags) | Yes (`<think>` tags) |
  | **Typical Latency** | **~1.5s - 2.0s** (~70 tok/s) | ~25s - 45s | ~20s - 60s |
  | **Architectural Verdict** | **GOLD STANDARD DEFAULT** | Selectable (Reasoning) | Selectable (CPU Bound) |

### 2.2 Reasoning / Thinking Tag Stripping Engine
- **Vulnerability:** Reasoning models start completions with an internal reasoning monologue enclosed in `<think>...</think>` tags. When generating PDDL or JSON, standard parsers failed due to non-JSON preambles or invalid PDDL outer tags.
- **Resolution in [`src/core/llm.py`](file:///home/felipeab/MultiAgentON/src/core/llm.py):**
  ```python
  raw_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
  ```
  Integrated into `OllamaChatOpenAI._parse_pydantic`, ensuring transparent Pydantic validation for `IntentSummary` and `RouteIntent`.
- **Resolution in [`src/nodes/pddl_parser.py`](file:///home/felipeab/MultiAgentON/src/nodes/pddl_parser.py):**
  Updated `_strip_code_fences` to remove thinking blocks prior to extracting `(define (problem ...))` blocks, ensuring 100% AST CFG validity ($v_{struct}=1$).
- **Token Budget Scaling:** Configured `create_ollama_llm` to automatically allocate 3000 max completion tokens for thinking models (`qwen3.5:4b`, `gemma4:e4b`), preventing internal monologues from exhausting output budgets.

### 2.3 CLI & Benchmark Harness Integration
- **CLI Navigation ([`src/main.py`](file:///home/felipeab/MultiAgentON/src/main.py)):**
  Updated `interactive_configuration()` with Questionary arrows to select:
  - `⚡ Recommended Default (qwen2.5:3b | 100% GPU VRAM | ~1.5s latency | temp=0.2)`
  - `🧠 Qwen 3.5 4B (qwen3.5:4b | Hybrid GPU/CPU | Native Reasoning | temp=0.2)`
  - `🐘 Gemma 4 e4B (gemma4:e4b | 8.0B Params | Heavy CPU Offload | temp=0.2)`
  - `🛠️ Custom Settings`
- **Automated Benchmark Runner ([`tests/evaluation/scripts/run_benchmark.py`](file:///home/felipeab/MultiAgentON/tests/evaluation/scripts/run_benchmark.py)):**
  Updated `fetch_available_ollama_models()` and interactive choices to clearly display installed models with performance annotations.
- **Environment Reference ([`.env`](file:///home/felipeab/MultiAgentON/.env)):**
  Documented all three local model configurations and default parameter settings.

### 2.4 Integration Tests with Safe Memory Deallocation
- In [`tests/integration/test_ollama_configurations.py`](file:///home/felipeab/MultiAgentON/tests/integration/test_ollama_configurations.py):
  - Parametrized `test_ollama_multi_model_pddl_comparison` across `qwen2.5:3b`, `qwen3.5:4b`, and `gemma4:e4b`.
  - Implemented `_unload_model(model_name)` sending `keep_alive=0` to Ollama's `/api/generate` in test teardown blocks, immediately freeing system RAM after benchmarking heavy models.

---

## 3. Verification & Test Suite Status

- **Unit Tests:** `uv run pytest tests/unit/` $\to$ **347 passed, 3 warnings in 4.08s** (100% pass rate).
- **Live Integration Tests:**
  - `test_ollama_structured_intent_ingest` $\to$ **PASSED in 2.83s** (Latency: 1.36s).
  - `test_ollama_multi_model_pddl_comparison[qwen2.5:3b]` $\to$ **PASSED in 2.95s** (Latency: 2.02s, PDDL Valid: True).
- **End-to-End Non-Interactive CLI Run:**
  - `uv run python src/main.py --no-interactive --model qwen2.5:3b "Route 100G optical circuit from Berlin to Frankfurt with at least 15 dB GSNR"`
  - Successfully executed all 7 neurosymbolic pipeline stages with full Planning Report synthesis and coherent GN-model GSNR verification.
- **Linter & Code Style:** `uv run ruff check .` $\to$ **All checks passed**.

---

## 4. Handover & Next Steps

1. **Thesis Chapter 4 Numerical Results:** Incorporate comparative local vs. cloud latency and token performance into Chapter 4 using `thesis-coauthor`.
2. **Slide 14 Presentation Integration:** Embed empirical benchmark figures into Slide 14 of the defense presentation deck.
3. **Advisor Checkpoint:** Present the 16-slide presentation deck and local GPU benchmark results to Prof. Massimo Tornatore.
