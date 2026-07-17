"""Shared LLM configuration for the Neurosymbolic Intent Pipeline.

Provides a module-level LLM instance that multiple pipeline nodes
(intent_ingest, pddl_parser, reverse_prompt, plan_synthesizer)
can consume without each needing their own configuration.
"""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

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
    #model: str = "kimi-k2-0711-preview",
    model: str = "moonshot-v1-8k",
) -> ChatOpenAI:
    """Create a ChatOpenAI instance configured for the Kimi API.

    Args:
        api_key: API key for the Kimi service.
        base_url: Custom base URL (required for Kimi).
        model: Model identifier to use.

    Returns:
        A configured ChatOpenAI instance.
    """
    kwargs: dict = {
        "model": model,
        "api_key": api_key,
        "temperature": 1,
        "max_tokens": 1500,
    }
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)
