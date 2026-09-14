"""Integration test for the Kimi LLM connection.

Validates that a live connection to the Kimi API can be established
and that the model returns a non-empty response.

Requires:
    - KIMI_API_KEY environment variable set.
    - KIMI_BASE_URL environment variable set.
    - Network connectivity to the Kimi API endpoint.

Run with:
    uv run pytest tests/integration/test_llm_connection.py -v -m integration -rs
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

        llm = create_kimi_llm(api_key=api_key, base_url=base_url)
        prompt = "What is the capital of France? Reply in one word."
        try:
            response = llm.invoke(prompt)
        except Exception as err:
            err_msg = str(err)
            if "usage limit" in err_msg or "403" in err_msg or "access_terminated" in err_msg:
                pytest.skip(f"Kimi API quota exceeded: {err_msg}")
            raise

        print(f"\n--- Prompt (Test 1) ---\n{prompt}")
        print(f"--- Model Response (Test 1) ---\n{response.content}\n-------------------------------")

        assert response is not None
        assert hasattr(response, "content")
        assert len(str(response.content).strip()) > 0

    def test_llm_response_contains_text(self) -> None:
        """Verify the response content is a non-whitespace string."""
        from src.core.llm import create_kimi_llm

        api_key = os.getenv("KIMI_API_KEY", "")
        base_url = os.getenv("KIMI_BASE_URL", "")

        llm = create_kimi_llm(api_key=api_key, base_url=base_url)
        prompt = "What are the primary colors? Keep it brief."
        try:
            response = llm.invoke(prompt)
        except Exception as err:
            err_msg = str(err)
            if "usage limit" in err_msg or "403" in err_msg or "access_terminated" in err_msg:
                pytest.skip(f"Kimi API quota exceeded: {err_msg}")
            raise

        print(f"\n--- Prompt (Test 2) ---\n{prompt}")
        print(f"--- Model Response (Test 2) ---\n{response.content}\n-------------------------------")

        assert str(response.content).strip() != ""

    def test_llm_structured_output(self) -> None:
        """Verify the LLM supports structured Pydantic extraction."""
        from pydantic import BaseModel, Field
        from src.core.llm import create_kimi_llm

        class RouteIntent(BaseModel):
            source: str = Field(description="Source city")
            target: str = Field(description="Target city")

        api_key = os.getenv("KIMI_API_KEY", "")
        base_url = os.getenv("KIMI_BASE_URL", "")

        llm = create_kimi_llm(api_key=api_key, base_url=base_url)
        structured_llm = llm.with_structured_output(RouteIntent)
        try:
            result = structured_llm.invoke("Provision a 100G circuit from Berlin to Munich")
        except Exception as err:
            err_msg = str(err)
            if "usage limit" in err_msg or "403" in err_msg or "access_terminated" in err_msg:
                pytest.skip(f"Kimi API quota exceeded: {err_msg}")
            raise

        print(f"\n--- Structured Output ---\n{result}\n-------------------------------")
        assert isinstance(result, RouteIntent)
        assert result.source == "Berlin"
        assert result.target == "Munich"


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set — skipping live OpenRouter integration test.",
)
class TestOpenRouterConnection:
    """Live connectivity tests for the OpenRouter LLM API."""

    def test_openrouter_llm_returns_non_empty_response(self) -> None:
        """Verify OpenRouter LLM can be invoked and returns a non-empty string."""
        from src.core.llm import create_openrouter_llm

        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("OP_LING_MODEL")

        llm = create_openrouter_llm(api_key=api_key, model=model)
        prompt = "What is the capital of France? Reply in one word."
        try:
            response = llm.invoke(prompt)
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenRouter quota / rate limit hit: {err_msg}")
            raise

        print(f"\n--- Prompt (OpenRouter Test 1) ---\n{prompt}")
        print(f"--- Model Response (OpenRouter Test 1) ---\n{response.content}\n-------------------------------")

        assert response is not None
        assert hasattr(response, "content")
        assert len(str(response.content).strip()) > 0

    def test_openrouter_llm_response_contains_text(self) -> None:
        """Verify the OpenRouter response content is a non-whitespace string."""
        from src.core.llm import create_openrouter_llm

        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("OP_LING_MODEL")

        llm = create_openrouter_llm(api_key=api_key, model=model)
        prompt = "What are the primary colors? Keep it brief."
        try:
            response = llm.invoke(prompt)
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenRouter quota / rate limit hit: {err_msg}")
            raise

        print(f"\n--- Prompt (OpenRouter Test 2) ---\n{prompt}")
        print(f"--- Model Response (OpenRouter Test 2) ---\n{response.content}\n-------------------------------")

        assert str(response.content).strip() != ""

    def test_openrouter_llm_structured_output(self) -> None:
        """Verify the OpenRouter LLM supports structured Pydantic extraction via function calling."""
        from pydantic import BaseModel, Field
        from src.core.llm import create_openrouter_llm

        class RouteIntent(BaseModel):
            source: str = Field(description="Source city")
            target: str = Field(description="Target city")

        api_key = os.getenv("OPENROUTER_API_KEY", "")
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("OP_LING_MODEL")

        llm = create_openrouter_llm(api_key=api_key, model=model)
        structured_llm = llm.with_structured_output(RouteIntent)
        try:
            result = structured_llm.invoke("Provision a 100G circuit from Berlin to Munich")
        except Exception as err:
            err_msg = str(err)
            if "quota" in err_msg.lower() or "429" in err_msg or "rate limit" in err_msg.lower():
                pytest.skip(f"OpenRouter quota / rate limit hit: {err_msg}")
            raise

        print(f"\n--- Structured Output (OpenRouter) ---\n{result}\n-------------------------------")
        assert isinstance(result, RouteIntent)
        assert result.source == "Berlin"
        assert result.target == "Munich"


@pytest.mark.integration
class TestOllamaConnection:
    """Live connectivity tests for the local Ollama LLM."""

    def test_ollama_llm_returns_non_empty_response(self) -> None:
        """Verify local Ollama LLM can be invoked and returns a non-empty string."""
        from src.core.llm import create_ollama_llm

        llm = create_ollama_llm()
        prompt = "What is the capital of France? Reply in one word."
        response = llm.invoke(prompt)

        print(f"\n--- Prompt (Ollama Test 1) ---\n{prompt}")
        print(f"--- Model Response (Ollama Test 1) ---\n{response.content}\n-------------------------------")

        assert response is not None
        assert hasattr(response, "content")
        assert len(str(response.content).strip()) > 0

    def test_ollama_llm_structured_output(self) -> None:
        """Verify the local Ollama LLM supports structured Pydantic extraction."""
        from pydantic import BaseModel, Field
        from src.core.llm import create_ollama_llm

        class RouteIntent(BaseModel):
            source: str = Field(description="Source city")
            target: str = Field(description="Target city")

        llm = create_ollama_llm()
        structured_llm = llm.with_structured_output(RouteIntent)
        result = structured_llm.invoke("Provision a 100G circuit from Berlin to Munich")

        print(f"\n--- Structured Output (Ollama) ---\n{result}\n-------------------------------")
        assert isinstance(result, RouteIntent)
        assert result.source == "Berlin"
        assert result.target == "Munich"




