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

# Default model and endpoint on OpenRouter
DEFAULT_OPENROUTER_MODEL = "inclusionai/ling-3.0-flash-vl:free"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Default model and endpoint on Ollama
DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434/v1"
SUPPORTED_OLLAMA_MODELS: tuple[str, ...] = (
    "qwen2.5:3b",
    "qwen3:4b",
    "phi4-mini:latest",
    "qwen3.5:4b",
    "gemma4:e4b",
)

# Default request timeout in seconds across LLM providers
DEFAULT_LLM_TIMEOUT: float = 120.0


def resolve_llm_timeout(timeout: float | None = None) -> float:
    """Resolve request timeout in seconds from explicit param, LLM_TIMEOUT env, or default."""
    if timeout is not None:
        return float(timeout)
    if env_val := os.getenv("LLM_TIMEOUT"):
        try:
            return float(env_val)
        except ValueError:
            pass
    return DEFAULT_LLM_TIMEOUT


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


class OpenRouterChatOpenAI(ChatOpenAI):
    """ChatOpenAI specialization for OpenRouter models.

    Ensures structured outputs default to 'function_calling' because many OpenRouter
    providers (including Novita hosting ling-3.0-flash-vl) do not support the
    native OpenAI 'json_schema' response format.
    """

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Any:
        if "method" not in kwargs:
            kwargs["method"] = "function_calling"
        return super().with_structured_output(schema, **kwargs)


class OllamaChatOpenAI(ChatOpenAI):
    """ChatOpenAI specialization for local Ollama models.

    Uses schema prompt formatting and robust JSON parsing for local models
    where strict tool_choice is not natively supported by Ollama's OpenAI endpoint.
    """

    def with_structured_output(self, schema: Any, **kwargs: Any) -> Any:
        from pydantic import BaseModel

        if isinstance(schema, type) and issubclass(schema, BaseModel):
            from langchain_core.messages import SystemMessage
            from langchain_core.output_parsers import PydanticOutputParser
            from langchain_core.runnables import RunnableLambda

            parser = PydanticOutputParser(pydantic_object=schema)
            instructions = parser.get_format_instructions()

            def _inject_instructions(messages: Any) -> Any:
                strong_directive = (
                    "CRITICAL WARNING: You must output the ACTUAL JSON DATA that conforms to the schema. "
                    "DO NOT output the JSON schema definition itself! Return a valid JSON object."
                )
                full_instructions = f"{instructions}\n\n{strong_directive}"

                if isinstance(messages, list):
                    updated = list(messages)
                    for idx, msg in enumerate(updated):
                        if getattr(msg, "type", None) == "system":
                            updated[idx] = SystemMessage(
                                content=f"{msg.content}\n\n{full_instructions}"
                            )
                            return updated
                    return [SystemMessage(content=full_instructions), *updated]
                elif isinstance(messages, str):
                    return f"{messages}\n\n{full_instructions}"
                return messages

            def _parse_pydantic(ai_message: Any) -> Any:
                import re

                raw_text = getattr(ai_message, "content", str(ai_message))
                # Strip internal reasoning blocks <think>...</think> from reasoning models
                raw_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
                # Extract outermost JSON object to ignore any preambles or code fences
                json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                if json_match:
                    clean = json_match.group(0).strip()
                else:
                    lines = [
                        line for line in raw_text.splitlines()
                        if not line.strip().startswith("```")
                    ]
                    clean = "\n".join(lines).strip()
                return parser.parse(clean)

            bound_llm = self.bind(response_format={"type": "json_object"})
            return RunnableLambda(_inject_instructions) | bound_llm | RunnableLambda(_parse_pydantic)

        return super().with_structured_output(schema, **kwargs)


def create_kimi_llm(
    *,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
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
        timeout: Request timeout in seconds. Defaults to LLM_TIMEOUT env or 120.0s.
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
    resolved_timeout = resolve_llm_timeout(timeout)

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
        "timeout": resolved_timeout,
    }
    if base_url:
        kwargs["base_url"] = base_url
    if body_params:
        kwargs["extra_body"] = body_params

    return ChatOpenAI(**kwargs)



def create_openrouter_llm(
    *,
    api_key: str,
    base_url: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
    http_referer: str | None = None,
    title: str | None = None,
    extra_body: dict[str, Any] | None = None,
    **_ignored_kwargs: Any,
) -> OpenRouterChatOpenAI:
    """Create an OpenRouterChatOpenAI instance configured for OpenRouter.

    Args:
        api_key: API key for OpenRouter.
        base_url: Custom base URL (defaults to OPENROUTER_BASE_URL or 'https://openrouter.ai/api/v1').
        model: Model identifier (defaults to OPENROUTER_MODEL, OP_LING_MODEL, or ling-3.0-flash-vl:free).
        temperature: Sampling temperature. Defaults to 0.2 for deterministic planning.
        max_tokens: Maximum tokens for completion. Defaults to 2000.
        timeout: Request timeout in seconds. Defaults to LLM_TIMEOUT env or 120.0s.
        http_referer: Optional site URL for ranking on openrouter.ai.
        title: Optional site/app name for ranking on openrouter.ai.
        extra_body: Additional raw payload attributes.
        **_ignored_kwargs: Safely absorbs provider-specific kwargs (e.g. think_effort, thinking_disabled).

    Returns:
        A configured OpenRouterChatOpenAI instance with function_calling fallback.
    """
    resolved_base_url = base_url or os.getenv("OPENROUTER_BASE_URL", DEFAULT_OPENROUTER_BASE_URL)
    resolved_model = (
        model
        or os.getenv("OPENROUTER_MODEL")
        or os.getenv("OP_LING_MODEL")
        or DEFAULT_OPENROUTER_MODEL
    )
    resolved_temp = 0.2 if temperature is None else temperature
    resolved_max_tokens = 2000 if max_tokens is None else max_tokens
    resolved_timeout = resolve_llm_timeout(timeout)

    referer = (
        http_referer
        or os.getenv("OPENROUTER_HTTP_REFERER", "https://github.com/ABADIAb/MultiAgent-ON")
    )
    app_title = title or os.getenv("OPENROUTER_TITLE", "MultiAgentON")

    default_headers: dict[str, str] = {
        "HTTP-Referer": referer,
        "X-Title": app_title,
    }

    kwargs: dict[str, Any] = {
        "model": resolved_model,
        "api_key": api_key,
        "base_url": resolved_base_url,
        "temperature": resolved_temp,
        "max_tokens": resolved_max_tokens,
        "default_headers": default_headers,
        "timeout": resolved_timeout,
    }
    if extra_body:
        kwargs["extra_body"] = extra_body

    return OpenRouterChatOpenAI(**kwargs)



def resolve_ollama_base_url(base_url: str | None = None) -> str:
    """Resolve the base URL for the Ollama API, handling WSL2 host resolution if needed."""
    if base_url:
        return base_url.rstrip("/")
    if env_url := os.getenv("OLLAMA_BASE_URL"):
        return env_url.rstrip("/")

    # Check if localhost:11434 is directly reachable
    default_url = "http://localhost:11434/v1"
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=0.3):
            return default_url
    except Exception:
        pass

    # If in WSL2, attempt gateway host IP
    try:
        import subprocess
        route_out = subprocess.check_output(["ip", "route"], text=True, timeout=0.5)
        for line in route_out.splitlines():
            if "default via" in line:
                host_ip = line.split()[2]
                return f"http://{host_ip}:11434/v1"
    except Exception:
        pass

    return default_url


def create_ollama_llm(
    *,
    base_url: str | None = None,
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
    extra_body: dict[str, Any] | None = None,
    **_ignored_kwargs: Any,
) -> OllamaChatOpenAI:
    """Create an OllamaChatOpenAI instance configured for local Ollama models.

    Args:
        base_url: Base URL for Ollama OpenAI endpoint (auto-resolves WSL host if omitted).
        model: Model identifier (defaults to OLLAMA_MODEL or 'qwen2.5:3b').
        temperature: Sampling temperature. Defaults to 0.2.
        max_tokens: Maximum tokens for completion. Defaults to 2000.
        timeout: Request timeout in seconds. Defaults to LLM_TIMEOUT env or 120.0s.
        extra_body: Additional raw payload attributes.
        **_ignored_kwargs: Safely absorbs provider-specific kwargs.

    Returns:
        A configured OllamaChatOpenAI instance with function_calling structured output.
    """
    resolved_base_url = resolve_ollama_base_url(base_url)
    resolved_model = model or os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL)
    resolved_temp = 0.2 if temperature is None else temperature
    resolved_timeout = resolve_llm_timeout(timeout)
    # Thinking models (qwen3, qwen3.5, gemma4) need a larger token ceiling so internal reasoning doesn't truncate output
    is_thinking_model = (
        "qwen3" in resolved_model
        or "3.5" in resolved_model
        or "gemma4" in resolved_model
    ) and "qwen2" not in resolved_model
    default_tokens = 3000 if is_thinking_model else 2000
    resolved_max_tokens = default_tokens if max_tokens is None else max_tokens

    kwargs: dict[str, Any] = {
        "model": resolved_model,
        "api_key": "ollama",
        "base_url": resolved_base_url,
        "temperature": resolved_temp,
        "max_tokens": resolved_max_tokens,
        "timeout": resolved_timeout,
    }
    if extra_body:
        kwargs["extra_body"] = extra_body

    return OllamaChatOpenAI(**kwargs)



def create_configured_llm(
    provider: str | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Create an LLM instance based on provider selection ('ollama', 'openrouter', or 'kimi').

    If provider is not explicitly passed, resolves from LLM_PROVIDER env var.
    Defaults to 'ollama' if LLM_PROVIDER is 'ollama', 'openrouter' if OPENROUTER_API_KEY is present,
    otherwise falls back to 'kimi'.
    """
    active_provider = (provider or os.getenv("LLM_PROVIDER", "")).lower().strip()
    if not active_provider:
        if os.getenv("LLM_PROVIDER") == "ollama":
            active_provider = "ollama"
        elif os.getenv("OPENROUTER_API_KEY"):
            active_provider = "openrouter"
        else:
            active_provider = "kimi"

    if active_provider == "ollama":
        return create_ollama_llm(**kwargs)
    elif active_provider == "openrouter":
        api_key = kwargs.pop("api_key", None) or os.getenv("OPENROUTER_API_KEY", "")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not set in environment or arguments.")
        return create_openrouter_llm(api_key=api_key, **kwargs)
    elif active_provider == "kimi":
        api_key = kwargs.pop("api_key", None) or os.getenv("KIMI_API_KEY", "")
        if not api_key:
            raise ValueError("KIMI_API_KEY is not set in environment or arguments.")
        base_url = kwargs.pop("base_url", None) or os.getenv("KIMI_BASE_URL", "")
        return create_kimi_llm(api_key=api_key, base_url=base_url or None, **kwargs)
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{active_provider}'. Supported options: 'ollama', 'openrouter', 'kimi'."
        )



