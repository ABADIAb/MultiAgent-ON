"""Integration benchmark tests for OpenAI API model configurations.

Evaluates and compares latency, token consumption (including reasoning tokens
and cached prompt tokens), and PDDL output validity across multiple OpenAI parameter
configurations and reasoning effort levels:
1. reasoning-effort-none (reasoning_effort="none") — strictly zero reasoning token overhead
2. reasoning-effort-low (reasoning_effort="low") — economical reasoning baseline
3. reasoning-effort-medium (reasoning_effort="medium") — standard reasoning depth

Requires:
    - OPENAI_API_KEY environment variable set.
    - Network connectivity to https://api.openai.com/v1.

Run with:
    uv run pytest tests/integration/test_openai_configurations.py -v -m integration -rs -s
"""

from __future__ import annotations

import os
import time
from typing import Any

import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm import create_openai_llm
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
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set — skipping live OpenAI configurations benchmark.",
)
class TestOpenAIConfigurations:
    """Benchmark suite for different OpenAI parameter and reasoning effort configurations."""

    @pytest.mark.parametrize(
        ("config_name", "config_kwargs"),
        [
            (
                "effort-none",
                {"reasoning_effort": "none", "max_tokens": 2000},
            ),
            (
                "effort-low",
                {"reasoning_effort": "low", "max_tokens": 2000},
            ),
            (
                "effort-medium",
                {"reasoning_effort": "medium", "max_tokens": 2000},
            ),
        ],
    )
    def test_openai_configuration_pddl_generation(
        self,
        config_name: str,
        config_kwargs: dict[str, Any],
    ) -> None:
        """Verify latency, token usage, reasoning tokens, and PDDL syntax validity."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("OPENAI_MODEL", "gpt-6-luna")

        llm = create_openai_llm(
            api_key=api_key,
            model=model,
            **config_kwargs,
        )

        messages = [
            SystemMessage(content=PDDL_SYSTEM_PROMPT),
            HumanMessage(content=BENCHMARK_INTENT),
        ]

        # Polite pacing between test runs
        time.sleep(1.0)

        start_time = time.perf_counter()
        try:
            response = llm.invoke(messages)
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenAI quota / rate limit hit: {err_msg}")
            raise

        latency = time.perf_counter() - start_time

        raw_content = response.content if isinstance(response.content, str) else str(response.content)
        clean_pddl = _strip_fences(raw_content)

        usage = response.response_metadata.get("token_usage", {})
        comp_tokens = usage.get("completion_tokens", len(clean_pddl) // 4)
        prompt_tokens = usage.get("prompt_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        comp_details = usage.get("completion_tokens_details") or {}
        reasoning_tokens = comp_details.get("reasoning_tokens", 0)

        prompt_details = usage.get("prompt_tokens_details") or {}
        cached_tokens = prompt_details.get("cached_tokens", 0)
        cache_write_tokens = prompt_details.get("cache_write_tokens", 0)

        is_valid, errors = validate_pddl_syntax(clean_pddl)

        print(f"\n{'='*20} OpenAI Benchmark: {config_name} {'='*20}")
        print(f"Model:               {model}")
        print(f"Latency:             {latency:.2f}s")
        print(f"Prompt Tokens:       {prompt_tokens} (Cached: {cached_tokens}, Cache Writes: {cache_write_tokens})")
        print(f"Completion Tokens:   {comp_tokens} (Reasoning: {reasoning_tokens})")
        print(f"Total Tokens:        {total_tokens}")
        print(f"PDDL Valid:          {is_valid}")
        if errors:
            print(f"Validation Errors:   {errors}")
        print(f"Generated PDDL Preview:\n{clean_pddl[:220]}...\n{'='*65}")

        assert len(clean_pddl) > 0, f"Empty output for {config_name}"
        assert is_valid, f"PDDL syntax invalid for {config_name}: {errors}"
        assert latency < 60.0, f"Latency too high for {config_name}: {latency:.2f}s"

    def test_openai_structured_intent_ingest(self) -> None:
        """Verify structured output parsing with IntentSummary using native json_schema/tool-calling."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        model = os.getenv("OPENAI_MODEL", "gpt-6-luna")

        llm = create_openai_llm(
            api_key=api_key,
            model=model,
            reasoning_effort="none",
            max_tokens=2000,
        )

        structured_llm = llm.with_structured_output(IntentSummary)

        messages = [
            SystemMessage(content=INTENT_SYSTEM_PROMPT),
            HumanMessage(content=BENCHMARK_INTENT),
        ]

        start_time = time.perf_counter()
        try:
            summary = structured_llm.invoke(messages)
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenAI quota / rate limit hit: {err_msg}")
            raise

        latency = time.perf_counter() - start_time

        print(f"\n{'='*20} OpenAI Structured Output {'='*20}")
        print(f"Model:      {model}")
        print(f"Latency:    {latency:.2f}s")
        print(f"Parsed:     {summary}")
        print(f"{'='*60}")

        assert isinstance(summary, IntentSummary)
        assert summary.source_node.lower() == "berlin"
        assert summary.target_node.lower() == "frankfurt"
