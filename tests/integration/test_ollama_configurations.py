"""Integration benchmark tests for local Ollama API model configurations.

Evaluates and compares latency, token consumption, and PDDL output validity
across multiple Ollama parameter configurations for the local model:
qwen2.5:3b (executed on local NVIDIA GeForce RTX 3050 GPU via Ollama).

Tested configurations:
1. qwen-temp-0.0 (temperature=0.0, max_tokens=2000) — strictly deterministic
2. qwen-temp-0.2 (temperature=0.2, max_tokens=2000) — recommended baseline
3. qwen-temp-0.6 (temperature=0.6, max_tokens=2000) — moderate sampling
4. qwen-tokens-1000 (temperature=0.2, max_tokens=1000) — constrained budget

Requires:
    - Ollama server running with qwen2.5:3b model pulled.
    - OLLAMA_BASE_URL (or auto-resolved Windows host IP).

Run with:
    uv run pytest tests/integration/test_ollama_configurations.py -v -m integration -rs -s
"""

from __future__ import annotations

import os
import time
from typing import Any

import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm import create_ollama_llm, resolve_ollama_base_url
from src.core.pddl_validator import validate_pddl_syntax
from src.nodes.intent_ingest import INTENT_SYSTEM_PROMPT, IntentSummary
from src.nodes.pddl_parser import PDDL_SYSTEM_PROMPT

load_dotenv()

BENCHMARK_INTENT = """\
Intent: Route 100G optical circuit from Berlin to Frankfurt with at least 15 dB GSNR.
Topology Context:
Nodes: Berlin, Frankfurt, Munich, Hamburg, Cologne
Links:
  - Berlin <-> Frankfurt (Length: 550.0 km)
  - Frankfurt <-> Munich (Length: 390.0 km)
  - Berlin <-> Hamburg (Length: 290.0 km)
"""


def _strip_fences(text: str) -> str:
    """Helper to strip markdown code blocks if emitted."""
    lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
    return "\n".join(lines).strip()


def _is_ollama_available() -> bool:
    """Check if Ollama is reachable."""
    import urllib.request
    url = resolve_ollama_base_url().replace("/v1", "") + "/api/tags"
    try:
        with urllib.request.urlopen(url, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(
    not _is_ollama_available(),
    reason="Local Ollama server not reachable — skipping Ollama configurations benchmark.",
)
class TestOllamaConfigurations:
    """Benchmark suite for different Ollama parameter configurations."""

    @pytest.mark.parametrize(
        ("config_name", "config_kwargs"),
        [
            (
                "qwen-temp-0.0",
                {"temperature": 0.0, "max_tokens": 2000},
            ),
            (
                "qwen-temp-0.2",
                {"temperature": 0.2, "max_tokens": 2000},
            ),
            (
                "qwen-temp-0.6",
                {"temperature": 0.6, "max_tokens": 2000},
            ),
            (
                "qwen-tokens-1000",
                {"temperature": 0.2, "max_tokens": 1000},
            ),
        ],
    )
    def test_ollama_configuration_pddl_generation(
        self,
        config_name: str,
        config_kwargs: dict[str, Any],
    ) -> None:
        """Verify latency, token usage, and PDDL syntax validity for each configuration."""
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

        llm = create_ollama_llm(
            model=model,
            **config_kwargs,
        )

        messages = [
            SystemMessage(content=PDDL_SYSTEM_PROMPT),
            HumanMessage(content=BENCHMARK_INTENT),
        ]

        start_time = time.perf_counter()
        response = llm.invoke(messages)
        latency = time.perf_counter() - start_time

        raw_content = response.content if isinstance(response.content, str) else str(response.content)
        clean_pddl = _strip_fences(raw_content)

        usage = response.response_metadata.get("token_usage", {})
        comp_tokens = usage.get("completion_tokens", len(clean_pddl) // 4)

        is_valid, errors = validate_pddl_syntax(clean_pddl)

        print(f"\n{'='*20} Ollama Benchmark: {config_name} {'='*20}")
        print(f"Model:            {model}")
        print(f"Latency:          {latency:.2f}s")
        print(f"Comp Tokens:      {comp_tokens}")
        print(f"PDDL Valid:       {is_valid}")
        if errors:
            print(f"Validation Errs:  {errors}")
        print(f"Generated PDDL:\n{clean_pddl[:250]}...\n{'='*65}")

        assert len(clean_pddl) > 0, f"Empty output for {config_name}"
        assert is_valid, f"PDDL syntax invalid for {config_name}: {errors}"
        assert latency < 30.0, f"Latency too high for local {config_name}: {latency:.2f}s"

    def test_ollama_structured_intent_ingest(self) -> None:
        """Verify structured output parsing with IntentSummary using local Ollama model."""
        model = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")

        llm = create_ollama_llm(
            model=model,
            temperature=0.0,
            max_tokens=2000,
        )

        structured_llm = llm.with_structured_output(IntentSummary)
        messages = [
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(
                content="Route 100G optical circuit from Berlin to Frankfurt with at least 15 dB GSNR, avoiding Cologne"
            ),
        ]

        start_time = time.perf_counter()
        summary = structured_llm.invoke(messages)
        latency = time.perf_counter() - start_time

        print(f"\n{'='*20} Ollama Structured Output Benchmark {'='*20}")
        print(f"Latency:          {latency:.2f}s")
        print(f"Extracted Intent: {summary}")
        print(f"{'='*65}")

        assert isinstance(summary, IntentSummary)
        assert summary.target_node == "Frankfurt"
        assert summary.source_node == "Berlin"
        assert summary.summary != ""
