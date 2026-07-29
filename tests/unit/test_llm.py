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
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(api_key="my-secret-key", base_url="https://test.example.com")
        # langchain_openai stores the key as a SecretStr
        assert llm.openai_api_key.get_secret_value() == "my-secret-key"

    def test_create_kimi_llm_default_model(self):
        """Default model is kimi-k2-0711-preview."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(api_key="test-key", base_url="https://test.example.com")
        assert llm.model_name == "moonshot-v1-8k"

    def test_create_kimi_llm_custom_model(self):
        """Custom model name is respected."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(
            api_key="test-key",
            base_url="https://test.example.com",
            model="custom-model",
        )
        assert llm.model_name == "custom-model"

    def test_create_kimi_llm_without_base_url(self):
        """Factory works when base_url is None (uses OpenAI default)."""
        from src.core.llm import create_kimi_llm

        llm = create_kimi_llm(api_key="test-key")
        assert isinstance(llm, BaseChatModel)
