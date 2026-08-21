"""Integration benchmark tests for Kimi API model configurations.

Evaluates and compares latency, token consumption (including reasoning tokens),
and PDDL output validity across multiple Kimi model variants and thinking modes:
1. kimi-for-coding-highspeed (Ultra-fast reasoning)
2. k3 (default think_effort)
3. k3 (think_effort="low")
4. k3 (thinking_disabled=True)

Requires:
    - KIMI_API_KEY environment variable set.
    - KIMI_BASE_URL environment variable set.

Run with:
    uv run pytest tests/integration/test_kimi_configurations.py -v -m integration -rs
"""

from __future__ import annotations

import os
import time
from typing import Any

import pytest
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage

from src.core.llm import create_kimi_llm
from src.core.pddl_validator import validate_pddl_syntax

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

PDDL_SYSTEM_PROMPT = """\
You are the PDDL Parser module of a Neurosymbolic Orchestrator for an optical network.
Translate the operator's enriched intent into a formal PDDL problem string using the provided topology.
Output ONLY the PDDL string, no markdown fences or explanations.
"""


def _strip_fences(text: str) -> str:
    """Helper to strip markdown code blocks if emitted."""
    lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
    return "\n".join(lines).strip()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("KIMI_API_KEY"),
    reason="KIMI_API_KEY not set — skipping live Kimi configurations benchmark.",
)
class TestKimiConfigurations:
    """Benchmark suite for different Kimi models and reasoning settings."""

    @pytest.mark.parametrize(
        ("config_name", "config_kwargs"),
        [
            (
                "kimi-for-coding-highspeed",
                {"model": "kimi-for-coding-highspeed", "max_tokens": 2500},
            ),
            (
                "k3-default-effort",
                {"model": "k3", "max_tokens": 2500},
            ),
            (
                "k3-low-effort",
                {"model": "k3", "think_effort": "low", "max_tokens": 2500},
            ),
            (
                "k3-thinking-disabled",
                {"model": "k3", "thinking_disabled": True, "max_tokens": 2500},
            ),
        ],
    )
    def test_kimi_configuration_pddl_generation(
        self,
        config_name: str,
        config_kwargs: dict[str, Any],
    ) -> None:
        """Verify latency, token usage, and PDDL syntax validity for each configuration."""
        api_key = os.getenv("KIMI_API_KEY", "")
        base_url = os.getenv("KIMI_BASE_URL", "")

        llm = create_kimi_llm(
            api_key=api_key,
            base_url=base_url,
            **config_kwargs,
        )

        messages = [
            SystemMessage(content=PDDL_SYSTEM_PROMPT),
            HumanMessage(content=BENCHMARK_INTENT),
        ]

        start_time = time.time()
        try:
            response = llm.invoke(messages)
        except Exception as err:
            err_msg = str(err)
            if "usage limit" in err_msg or "403" in err_msg or "access_terminated" in err_msg:
                pytest.skip(f"Kimi API quota exceeded for billing cycle: {err_msg}")
            raise

        latency = time.time() - start_time

        raw_content = response.content if isinstance(response.content, str) else str(response.content)
        clean_pddl = _strip_fences(raw_content)

        usage = response.response_metadata.get("token_usage", {})
        comp_tokens = usage.get("completion_tokens", 0)
        details = usage.get("completion_tokens_details") or {}
        reasoning_tokens = details.get("reasoning_tokens", "N/A")

        is_valid, errors = validate_pddl_syntax(clean_pddl)

        print(f"\n{'='*20} Benchmark: {config_name} {'='*20}")
        print(f"Latency:          {latency:.2f}s")
        print(f"Completion Tokens:{comp_tokens} (Reasoning: {reasoning_tokens})")
        print(f"PDDL Valid:       {is_valid}")
        if errors:
            print(f"Validation Errs:  {errors}")
        print(f"Generated PDDL:\n{clean_pddl[:250]}...\n{'='*55}")

        assert len(clean_pddl) > 0, f"Empty output for {config_name}"
        assert is_valid, f"PDDL syntax invalid for {config_name}: {errors}"
        assert latency < 60.0, f"Latency too high for {config_name}: {latency:.2f}s"

