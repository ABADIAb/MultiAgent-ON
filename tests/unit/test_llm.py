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

