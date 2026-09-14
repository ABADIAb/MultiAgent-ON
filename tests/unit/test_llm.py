"""Tests for the shared LLM configuration module.

Validates the get/set pattern and factory function for the Kimi LLM,
ensuring the module provides a clean singleton-like configuration
that multiple pipeline nodes can consume.
"""

from __future__ import annotations

import pytest
from langchain_core.language_models import BaseChatModel
from unittest.mock import MagicMock


class TestSetGetLLM:
    """Test the global LLM get/set pattern."""

    def test_get_llm_raises_when_not_configured(self):
        """get_llm() must raise RuntimeError if set_llm() was never called."""
        from src.core import llm as llm_module

        # Reset module state
        llm_module._llm = None
        with pytest.raises(RuntimeError, match="LLM not configured"):
            llm_module.get_llm()

    def test_set_and_get_llm_roundtrip(self):
        """set_llm() followed by get_llm() returns the same instance."""
        from src.core import llm as llm_module

        mock_llm = MagicMock(spec=BaseChatModel)
        llm_module.set_llm(mock_llm)
        assert llm_module.get_llm() is mock_llm

        # Cleanup
        llm_module._llm = None

    def test_set_llm_overwrites_previous(self):
        """Calling set_llm() twice replaces the previous LLM."""
        from src.core import llm as llm_module

        first = MagicMock(spec=BaseChatModel)
        second = MagicMock(spec=BaseChatModel)
        llm_module.set_llm(first)
        llm_module.set_llm(second)
        assert llm_module.get_llm() is second

        # Cleanup
        llm_module._llm = None


class TestCreateKimiLLM:
    """Test the Kimi LLM factory function."""

    def test_create_kimi_llm_returns_chat_openai(self):
        """Factory returns a ChatOpenAI instance."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(api_key="test-key", base_url="https://test.example.com")
        # ChatOpenAI is a BaseChatModel
        assert isinstance(llm, BaseChatModel)

    def test_create_kimi_llm_uses_provided_api_key(self):
        """The API key is correctly passed to the ChatOpenAI instance."""
        from pydantic import SecretStr
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(api_key="my-secret-key", base_url="https://test.example.com")
        # langchain_openai stores the key as a SecretStr
        assert isinstance(llm.openai_api_key, SecretStr)
        assert llm.openai_api_key.get_secret_value() == "my-secret-key"

    def test_create_kimi_llm_default_temperature(self):
        """Default temperature is 1.0 when thinking is enabled, 0.6 when disabled."""
        from src.core.llm import create_kimi_llm

        llm_default = create_kimi_llm(api_key="test-key", base_url="https://test.example.com")
        assert llm_default.temperature == 1.0

        llm_disabled = create_kimi_llm(
            api_key="test-key", base_url="https://test.example.com", thinking_disabled=True
        )
        assert llm_disabled.temperature == 0.6

        llm_custom = create_kimi_llm(
            api_key="test-key", base_url="https://test.example.com", temperature=0.7
        )
        assert llm_custom.temperature == 0.7

    def test_create_kimi_llm_default_model(self, monkeypatch):
        """Default model is kimi-for-coding-highspeed when env var is unset."""
        from src.core.llm import DEFAULT_KIMI_MODEL, create_kimi_llm

        monkeypatch.delenv("KIMI_MODEL", raising=False)
        llm = create_kimi_llm(api_key="test-key", base_url="https://test.example.com")
        assert llm.model_name == DEFAULT_KIMI_MODEL
        assert llm.model_name == "kimi-for-coding-highspeed"

    def test_create_kimi_llm_model_from_env(self, monkeypatch):
        """Model identifier is read from KIMI_MODEL environment variable if not passed."""
        from src.core.llm import create_kimi_llm

        monkeypatch.setenv("KIMI_MODEL", "k3")
        llm = create_kimi_llm(api_key="test-key", base_url="https://test.example.com")
        assert llm.model_name == "k3"

    def test_create_kimi_llm_custom_model_overrides_env(self, monkeypatch):
        """Explicit model argument overrides KIMI_MODEL environment variable."""
        from src.core.llm import create_kimi_llm

        monkeypatch.setenv("KIMI_MODEL", "k3")
        llm = create_kimi_llm(
            api_key="test-key",
            base_url="https://test.example.com",
            model="custom-model",
        )
        assert llm.model_name == "custom-model"

    def test_create_kimi_llm_think_effort(self):
        """think_effort is passed into extra_body."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(
            api_key="test-key",
            base_url="https://test.example.com",
            model="k3",
            think_effort="low",
        )
        assert getattr(llm, "extra_body", None) == {"think_effort": "low"}

    def test_create_kimi_llm_thinking_disabled(self):
        """thinking_disabled sets thinking type to disabled in extra_body."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(
            api_key="test-key",
            base_url="https://test.example.com",
            model="k3",
            thinking_disabled=True,
        )
        assert getattr(llm, "extra_body", None) == {"thinking": {"type": "disabled"}}

    def test_create_kimi_llm_merges_extra_body(self):
        """Custom extra_body keys are preserved alongside reasoning options."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(
            api_key="test-key",
            base_url="https://test.example.com",
            model="k3",
            think_effort="high",
            extra_body={"custom_field": "custom_value"},
        )
        assert getattr(llm, "extra_body", None) == {
            "custom_field": "custom_value",
            "think_effort": "high",
        }

    def test_create_kimi_llm_without_base_url(self):
        """Factory works when base_url is None (uses OpenAI default)."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(api_key="test-key")
        assert isinstance(llm, BaseChatModel)

    def test_create_kimi_llm_max_tokens_default(self):
        """Default max_tokens is 8000 for highspeed model and 2500 for other models."""
        from src.core.llm import create_kimi_llm

        llm_highspeed = create_kimi_llm(api_key="test-key", model="kimi-for-coding-highspeed")
        assert llm_highspeed.max_tokens == 8000

        llm_k3 = create_kimi_llm(api_key="test-key", model="k3")
        assert llm_k3.max_tokens == 2500

        llm_custom = create_kimi_llm(api_key="test-key", model="kimi-for-coding-highspeed", max_tokens=4000)
        assert llm_custom.max_tokens == 4000


class TestCreateOpenRouterLLM:
    """Test the OpenRouter LLM factory and wrapper class."""

    def test_create_openrouter_llm_returns_instance(self):
        """Factory returns an OpenRouterChatOpenAI instance."""
        from src.core.llm import OpenRouterChatOpenAI, create_openrouter_llm

        llm = create_openrouter_llm(api_key="test-key")
        assert isinstance(llm, OpenRouterChatOpenAI)
        assert isinstance(llm, BaseChatModel)

    def test_create_openrouter_llm_defaults(self, monkeypatch):
        """Factory uses expected default values for OpenRouter."""
        from src.core.llm import (
            DEFAULT_OPENROUTER_BASE_URL,
            DEFAULT_OPENROUTER_MODEL,
            create_openrouter_llm,
        )

        monkeypatch.delenv("OPENROUTER_MODEL", raising=False)
        monkeypatch.delenv("OP_LING_MODEL", raising=False)
        monkeypatch.delenv("OPENROUTER_BASE_URL", raising=False)

        llm = create_openrouter_llm(api_key="test-key")
        assert llm.model_name == DEFAULT_OPENROUTER_MODEL
        assert llm.model_name == "inclusionai/ling-3.0-flash-vl:free"
        assert str(llm.openai_api_base).rstrip("/") == DEFAULT_OPENROUTER_BASE_URL
        assert llm.temperature == 0.2
        assert llm.max_tokens == 2000

    def test_create_openrouter_llm_custom_params(self):
        """Explicit parameters override defaults."""
        from src.core.llm import create_openrouter_llm

        llm = create_openrouter_llm(
            api_key="test-key",
            base_url="https://custom.openrouter.ai/v1",
            model="custom/model:free",
            temperature=0.7,
            max_tokens=3500,
        )
        assert llm.model_name == "custom/model:free"
        assert str(llm.openai_api_base).rstrip("/") == "https://custom.openrouter.ai/v1"
        assert llm.temperature == 0.7
        assert llm.max_tokens == 3500

    def test_create_openrouter_llm_default_headers(self):
        """Headers for ranking and attribution are properly configured."""
        from src.core.llm import create_openrouter_llm

        llm = create_openrouter_llm(
            api_key="test-key",
            http_referer="https://myrepo.com",
            title="MySpecialApp",
        )
        assert llm.default_headers.get("HTTP-Referer") == "https://myrepo.com"
        assert llm.default_headers.get("X-Title") == "MySpecialApp"

    def test_openrouter_chat_openai_structured_output_defaults_to_function_calling(self, monkeypatch):
        """with_structured_output injects method='function_calling' by default."""
        from pydantic import BaseModel
        from src.core.llm import OpenRouterChatOpenAI

        class DummySchema(BaseModel):
            query: str

        llm = OpenRouterChatOpenAI(api_key="test-key")

        # Mock super().with_structured_output
        mock_super_call = MagicMock()
        monkeypatch.setattr(
            "langchain_openai.ChatOpenAI.with_structured_output",
            mock_super_call,
        )

        llm.with_structured_output(DummySchema)
        mock_super_call.assert_called_once_with(DummySchema, method="function_calling")

        # Verify explicit method is preserved
        mock_super_call.reset_mock()
        llm.with_structured_output(DummySchema, method="json_mode")
        mock_super_call.assert_called_once_with(DummySchema, method="json_mode")


class TestCreateOllamaLLM:
    """Test the local Ollama LLM factory function."""

    def test_create_ollama_llm_returns_ollama_chat_openai(self):
        """Factory returns an OllamaChatOpenAI instance."""
        from src.core.llm import OllamaChatOpenAI, create_ollama_llm

        llm = create_ollama_llm(base_url="http://localhost:11434/v1")
        assert isinstance(llm, OllamaChatOpenAI)
        assert llm.model_name == "qwen2.5:3b"
        assert llm.temperature == 0.2

    def test_create_ollama_llm_custom_params(self):
        """Custom parameters are respected."""
        from src.core.llm import create_ollama_llm

        llm = create_ollama_llm(
            model="custom-model:latest",
            base_url="http://10.0.0.1:11434/v1",
            temperature=0.7,
            max_tokens=1500,
        )
        assert llm.model_name == "custom-model:latest"
        assert llm.temperature == 0.7
        assert llm.max_tokens == 1500

    def test_resolve_ollama_base_url_env(self, monkeypatch):
        """OLLAMA_BASE_URL env var overrides default resolution."""
        from src.core.llm import resolve_ollama_base_url

        monkeypatch.setenv("OLLAMA_BASE_URL", "http://my-host:11434/v1")
        assert resolve_ollama_base_url() == "http://my-host:11434/v1"


class TestCreateConfiguredLLM:
    """Test the multi-provider LLM dispatcher."""

    def test_create_configured_llm_ollama(self, monkeypatch):
        """create_configured_llm creates OllamaChatOpenAI when provider is ollama."""
        from src.core.llm import OllamaChatOpenAI, create_configured_llm

        monkeypatch.setenv("LLM_PROVIDER", "ollama")
        llm = create_configured_llm(provider="ollama")
        assert isinstance(llm, OllamaChatOpenAI)

    def test_create_configured_llm_openrouter(self, monkeypatch):
        """create_configured_llm creates OpenRouterChatOpenAI when provider is openrouter."""
        from src.core.llm import OpenRouterChatOpenAI, create_configured_llm

        monkeypatch.setenv("OPENROUTER_API_KEY", "test-or-key")
        llm = create_configured_llm(provider="openrouter")
        assert isinstance(llm, OpenRouterChatOpenAI)

    def test_create_configured_llm_kimi(self, monkeypatch):
        """create_configured_llm creates ChatOpenAI when provider is kimi."""
        from langchain_openai import ChatOpenAI
        from src.core.llm import OpenRouterChatOpenAI, create_configured_llm

        monkeypatch.setenv("KIMI_API_KEY", "test-kimi-key")
        monkeypatch.setenv("KIMI_BASE_URL", "https://api.kimi.com/coding/v1")
        llm = create_configured_llm(provider="kimi")
        assert isinstance(llm, ChatOpenAI)
        assert not isinstance(llm, OpenRouterChatOpenAI)

    def test_create_configured_llm_from_env_provider(self, monkeypatch):
        """create_configured_llm reads LLM_PROVIDER from environment."""
        from src.core.llm import OpenRouterChatOpenAI, create_configured_llm

        monkeypatch.setenv("LLM_PROVIDER", "openrouter")
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-or-key")
        llm = create_configured_llm()
        assert isinstance(llm, OpenRouterChatOpenAI)

    def test_create_configured_llm_unsupported_provider_raises(self):
        """Unsupported provider raises ValueError with helpful message."""
        from src.core.llm import create_configured_llm

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_configured_llm(provider="unsupported_provider")



