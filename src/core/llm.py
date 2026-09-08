"""Shared LLM configuration for the Neurosymbolic Intent Pipeline.

Provides a module-level LLM instance that multiple pipeline nodes
(intent_ingest, pddl_parser, reverse_prompt, plan_synthesizer)
can consume without each needing their own configuration.
"""

from __future__ import annotations

import os
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

# Default model on the Kimi Coding endpoint
DEFAULT_KIMI_MODEL = "kimi-for-coding-highspeed"

# Module-level LLM reference, set during graph initialization.
_llm: BaseChatModel | None = None


def set_llm(llm: BaseChatModel) -> None:
    """Configure the shared LLM used by pipeline nodes."""
    global _llm  # noqa: PLW0603
    _llm = llm


def get_llm() -> BaseChatModel:
    """Retrieve the configured LLM or raise if not set."""
    if _llm is None:
        msg = (
            "LLM not configured. "
            "Call set_llm() before running the pipeline."
        )
        raise RuntimeError(msg)
    return _llm


def create_kimi_llm(
    *,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    think_effort: str | None = None,
    thinking_disabled: bool = False,
    extra_body: dict[str, Any] | None = None,
) -> ChatOpenAI:
    """Create a ChatOpenAI instance configured for the Kimi API.

    Args:
        api_key: API key for the Kimi service.
        base_url: Custom base URL (required for Kimi).
        model: Model identifier (defaults to KIMI_MODEL env or 'kimi-for-coding-highspeed').
        temperature: Sampling temperature. Defaults to 0.6 if thinking is disabled, 1.0 otherwise.
        max_tokens: Maximum tokens for completion (including reasoning tokens). Defaults to 8000 for highspeed.
        think_effort: Optional reasoning effort ('low', 'high', 'max') for K3 models.
        thinking_disabled: Whether to disable reasoning/thinking entirely.
        extra_body: Additional raw payload attributes.

    Returns:
        A configured ChatOpenAI instance.
    """
    resolved_model = model or os.getenv("KIMI_MODEL", DEFAULT_KIMI_MODEL)
    resolved_temp = (0.6 if thinking_disabled else 1.0) if temperature is None else temperature
    resolved_max_tokens = (
        max_tokens
        if max_tokens is not None
        else (8000 if resolved_model == DEFAULT_KIMI_MODEL else 2500)
    )

    body_params: dict[str, Any] = dict(extra_body) if extra_body else {}
    if thinking_disabled:
        body_params["thinking"] = {"type": "disabled"}
    elif think_effort:
        body_params["think_effort"] = think_effort

    kwargs: dict[str, Any] = {
        "model": resolved_model,
        "api_key": api_key,
        "temperature": resolved_temp,
        "max_tokens": resolved_max_tokens,
    }
    if base_url:
        kwargs["base_url"] = base_url
    if body_params:
        kwargs["extra_body"] = body_params

    return ChatOpenAI(**kwargs)

