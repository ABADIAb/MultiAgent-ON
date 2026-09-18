---
title: "Session Summary: Local Ollama Multi-Model Profiling, Hardware Architecture Audit & Multi-Provider Integration"
date: 2026-09-14
tags: [session-summary, ollama, local-llm, qwen2.5, phi4-mini, qwen3, multi-provider, rtx-3050, strict-tdd]
status: active
---

# Session Summary: Local Ollama Multi-Model Profiling, Hardware Architecture Audit & Multi-Provider Integration

## 1. Executive Summary

In this consolidated session, I engineered and verified the local open-weights LLM inference layer via Ollama, targeting complete offline reproducibility, zero API costs, and native reasoning support for the Master's thesis:
> *"LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"*

Key technical outcomes:
1. **Multi-Provider Architecture (`src/core/llm.py`):** Extended `create_configured_llm()` to seamlessly dispatch across `ollama`, `openrouter`, and `kimi`. Engineered `OllamaChatOpenAI` with automatic WSL2 dynamic host gateway discovery and schema-aware prompt injection for reliable Pydantic structured output extraction.
2. **Hardware Architecture Audit & Empirical Profiling (RTX 3050 Laptop GPU, 4 GB VRAM, 8 GB RAM):**
   - **`qwen2.5:3b` (3.1B, 1.9 GB binary) — Optimal Default:** Fits 100% in VRAM (2.15 GB allocated), achieving ~1.5s latency at ~70 tok/s with zero RAM swapping and 100% PDDL CFG compliance.
   - **`phi4-mini:latest` (3.8B, 2.49 GB binary):** Serves as the top non-reasoning direct alternative with high structural adherence. Verified through all 7 pipeline phases in `src/main.py`.
   - **`qwen3:4b` / `qwen3.5:4b` (Native Reasoning):** Integrated dynamic completion token budgeting (3000 tokens) and `<think>.*?</think>` regex sanitization in `_parse_pydantic` and `_strip_code_fences` to enable chain-of-thought models without breaking downstream AST parsers.
3. **Phase 3 Semantic Gate Hardening:** Diagnosed and resolved recurring $U_{sem}=0.50$ false divergences on small SLMs caused by `:init` network topology leakage in [[reverse_prompt]]. Refactored `REVERSE_PROMPT_SYSTEM` to focus strictly on `(:goal ...)`.
4. **Testing & Memory Safety:** Authored integration tests in `tests/integration/test_ollama_configurations.py` with automated `_unload_model(keep_alive=0)` teardown routines to prevent VRAM/RAM leakage. All 351 unit tests passed under Strict TDD.

---

## 2. Hardware Allocation & Empirical Profiling Matrix

| Metric | `qwen2.5:3b` (Default) | `phi4-mini:latest` (Direct) | `qwen3:4b` (Reasoning) | `qwen3.5:4b` (Reasoning) | `gemma4:e4b` (Heavy 8B) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Parameter Count** | 3.1B | 3.8B | 4.0B | 4.7B | 8.0B |
| **Binary Size (Q4_K_M)** | 1.9 GB | 2.49 GB | 2.50 GB | 3.4 GB | 9.6 GB |
| **VRAM Consumption** | **2.15 GB (100% in VRAM)** | ~2.80 GB | ~2.35 GB | 1.87 GB | 1.46 GB |
| **System RAM Offload** | **0.00 GB** | 0.00 GB | ~1.18 GB | 1.85 GB | 8.04 GB (Paging / Swap) |
| **Native Thinking** | Direct | Direct | Yes (`<think>`) | Yes (`<think>`) | Yes (`<think>`) |
| **Typical Latency** | **~1.5s - 2.0s** (~70 tok/s) | ~12.8s | ~30s - 90s | ~25s - 45s | ~20s - 60s |
| **Architectural Verdict** | **GOLD STANDARD DEFAULT** | **Best Direct Alternative** | Deep Reasoning | Deep Reasoning | CPU Bound / Heavy |

---

## 3. Core Deliverables & Source Map

- **LLM Engine (`src/core/llm.py`):** `OllamaChatOpenAI`, dynamic token budgeting (2000 vs 3000 tokens), dynamic gateway discovery (`resolve_ollama_base_url()`), thinking tag sanitization.
- **PDDL Parser (`src/nodes/pddl_parser.py`):** `_strip_code_fences()` with thinking tag cleaning.
- **Reverse Prompting (`src/nodes/reverse_prompt.py`):** Goal-focused reconstruction prompt eliminating topology leakage.
- **Semantic Gate (`src/nodes/semantic_gate_node.py`):** `_score_semantic_agreement()` with typo tolerance and canonical entity mapping.
- **Interactive CLI & Benchmark (`src/main.py`, `tests/evaluation/scripts/run_benchmark.py`):** Multi-model menus and `--provider ollama --model <name>` flags.
- **Integration Test Suite (`tests/integration/test_ollama_configurations.py`):** Multi-model parameter evaluation and automated memory deallocation.
