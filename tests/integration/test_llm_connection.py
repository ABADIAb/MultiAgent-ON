"""Integration test for the Kimi LLM connection.

Validates that a live connection to the Kimi API can be established
and that the model returns a non-empty response.

Requires:
    - KIMI_API_KEY environment variable set.
    - KIMI_BASE_URL environment variable set.
    - Network connectivity to the Kimi API endpoint.

Run with:
    uv run pytest tests/integration/test_llm_connection.py -v -s -m integration
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("KIMI_API_KEY"),
    reason="KIMI_API_KEY not set — skipping live LLM integration test.",
)
class TestLLMConnection:
    """Live connectivity tests for the Kimi LLM API."""

    def test_llm_returns_non_empty_response(self) -> None:
        """Verify the LLM can be invoked and returns a non-empty string."""
        from src.core.llm import create_kimi_llm

        api_key = os.getenv("KIMI_API_KEY", "")
        base_url = os.getenv("KIMI_BASE_URL", "")

        llm = create_kimi_llm(api_key=api_key, base_url=base_url, model="moonshot-v1-8k")
        prompt = "What is the capital of France? Reply in one word."
        response = llm.invoke(prompt)
        
        print(f"\n--- Prompt (Test 1) ---\n{prompt}")
        print(f"--- Model Response (Test 1) ---\n{response.content}\n-------------------------------")

        assert response is not None
        assert hasattr(response, "content")
        assert len(response.content) > 0

    def test_llm_response_contains_text(self) -> None:
        """Verify the response content is a non-whitespace string."""
        from src.core.llm import create_kimi_llm

        api_key = os.getenv("KIMI_API_KEY", "")
        base_url = os.getenv("KIMI_BASE_URL", "")

        llm = create_kimi_llm(api_key=api_key, base_url=base_url, model="moonshot-v1-8k")
        prompt = "What are the primary colors? Keep it brief."
        response = llm.invoke(prompt)
        
        print(f"\n--- Prompt (Test 2) ---\n{prompt}")
        print(f"--- Model Response (Test 2) ---\n{response.content}\n-------------------------------")
        
        assert str(response.content).strip() != ""
