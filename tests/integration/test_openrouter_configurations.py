"""Integration benchmark tests for OpenRouter API model configurations.

Evaluates and compares latency, token consumption, and PDDL output validity
across multiple OpenRouter parameter configurations for the model:
inclusionai/ling-3.0-flash-vl:free

Tested configurations:
1. ling-temp-0.0 (temperature=0.0, max_tokens=2000) — strictly deterministic
2. ling-temp-0.2 (temperature=0.2, max_tokens=2000) — recommended baseline
3. ling-temp-0.6 (temperature=0.6, max_tokens=2000) — moderate sampling
4. ling-tokens-1000 (temperature=0.2, max_tokens=1000) — constrained budget

Requires:
    - OPENROUTER_API_KEY environment variable set.
    - Network connectivity to https://openrouter.ai/api/v1.

Run with:
    uv run pytest tests/integration/test_openrouter_configurations.py -v -m integration -rs -s
"""

from __future__ import annotations

import os
import time
from typing import Any

import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm import create_openrouter_llm
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


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set — skipping live OpenRouter configurations benchmark.",
)
class TestOpenRouterConfigurations:
    """Benchmark suite for different OpenRouter parameter configurations."""

    @pytest.mark.parametrize(
        ("config_name", "config_kwargs"),
        [
            (
                "ling-temp-0.0",
                {"temperature": 0.0, "max_tokens": 2000},
            ),
            (
                "ling-temp-0.2",
                {"temperature": 0.2, "max_tokens": 2000},
            ),
            (
                "ling-temp-0.6",
                {"temperature": 0.6, "max_tokens": 2000},
            ),
            (
                "ling-tokens-1000",
                {"temperature": 0.2, "max_tokens": 1000},
            ),
        ],
    )
    def test_openrouter_configuration_pddl_generation(
        self,
        config_name: str,
        config_kwargs: dict[str, Any],
    ) -> None:
        """Verify latency, token usage, and PDDL syntax validity for each configuration."""
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("OP_LING_MODEL")

        llm = create_openrouter_llm(
            api_key=api_key,
            model=model,
            **config_kwargs,
        )

        messages = [
            SystemMessage(content=PDDL_SYSTEM_PROMPT),
            HumanMessage(content=BENCHMARK_INTENT),
        ]

        # Pacing to respect free-tier upstream rate limits
        time.sleep(2.0)

        start_time = time.perf_counter()
        try:
            response = llm.invoke(messages)
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenRouter quota / rate limit hit: {err_msg}")
            raise

        latency = time.perf_counter() - start_time

        raw_content = response.content if isinstance(response.content, str) else str(response.content)
        clean_pddl = _strip_fences(raw_content)

        usage = response.response_metadata.get("token_usage", {})
        comp_tokens = usage.get("completion_tokens", len(clean_pddl) // 4)

        is_valid, errors = validate_pddl_syntax(clean_pddl)

        print(f"\n{'='*20} OpenRouter Benchmark: {config_name} {'='*20}")
        print(f"Model:            {model or 'inclusionai/ling-3.0-flash-vl:free'}")
        print(f"Latency:          {latency:.2f}s")
        print(f"Comp Tokens:      {comp_tokens}")
        print(f"PDDL Valid:       {is_valid}")
        if errors:
            print(f"Validation Errs:  {errors}")
        print(f"Generated PDDL:\n{clean_pddl[:250]}...\n{'='*65}")

        assert len(clean_pddl) > 0, f"Empty output for {config_name}"
        assert is_valid, f"PDDL syntax invalid for {config_name}: {errors}"
        assert latency < 60.0, f"Latency too high for {config_name}: {latency:.2f}s"

    def test_openrouter_structured_intent_ingest(self) -> None:
        """Verify structured output parsing with IntentSummary using function calling."""
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("OP_LING_MODEL")

        llm = create_openrouter_llm(
            api_key=api_key,
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

        time.sleep(2.0)
        start_time = time.perf_counter()
        try:
            summary = structured_llm.invoke(messages)
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenRouter quota / rate limit hit: {err_msg}")
            raise
        latency = time.perf_counter() - start_time

        print(f"\n{'='*20} OpenRouter Structured Output Benchmark {'='*20}")
        print(f"Latency:          {latency:.2f}s")
        print(f"Extracted Intent: {summary}")
        print(f"{'='*65}")

        assert isinstance(summary, IntentSummary)
        assert summary.target_node == "Frankfurt"
        assert summary.summary != ""
