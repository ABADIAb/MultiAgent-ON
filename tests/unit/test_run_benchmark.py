"""Unit tests for Sprint 4 benchmark runner model selection and CLI parser.

Strict TDD Mode: Authored before modifying tests/evaluation/scripts/run_benchmark.py.
Covers:
  1. CLI argument parser (--provider, --model, --temperature, --non-interactive, --mock).
  2. Dynamic Ollama tag fetching with network fallback.
  3. Interactive model selection flows (mock choice, ollama choice, custom model input).
  4. Live LLM instantiation with designated provider and model parameters.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from tests.evaluation.scripts.run_benchmark import (
    build_parser,
    fetch_available_ollama_models,
    interactive_model_selection,
    setup_benchmark_llm,
)


# ---------------------------------------------------------------------------
# 1. CLI Parser Tests
# ---------------------------------------------------------------------------


def test_build_parser_default_arguments() -> None:
    """Verify default parser values and presence of new model selection flags."""
    parser = build_parser()
    args = parser.parse_args([])

    assert args.corpus == "tests/evaluation/test_corpus_compact.json"
    assert args.mock is False
    assert args.provider is None
    assert args.model is None
    assert args.temperature is None
    assert args.non_interactive is False


def test_build_parser_custom_model_flags() -> None:
    """Verify explicit provider and model arguments."""
    parser = build_parser()
    args = parser.parse_args([
        "--provider",
        "ollama",
        "--model",
        "qwen2.5:3b",
        "--temperature",
        "0.1",
        "--non-interactive",
    ])

    assert args.provider == "ollama"
    assert args.model == "qwen2.5:3b"
    assert args.temperature == 0.1
    assert args.non_interactive is True


# ---------------------------------------------------------------------------
# 2. Ollama Dynamic Tag Discovery
# ---------------------------------------------------------------------------


def test_fetch_available_ollama_models_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify successfully parsing Ollama /api/tags JSON."""
    fake_response = MagicMock()
    fake_data = {
        "models": [
            {"name": "qwen2.5:3b"},
            {"name": "llama3.2:1b"},
        ]
    }
    fake_response.read.return_value = json.dumps(fake_data).encode("utf-8")
    fake_response.__enter__.return_value = fake_response

    monkeypatch.setattr(
        "urllib.request.urlopen", lambda url, timeout: fake_response
    )

    models = fetch_available_ollama_models()
    assert models == ["qwen2.5:3b", "llama3.2:1b"]


def test_fetch_available_ollama_models_fallback_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify returning empty list when Ollama endpoint is unreachable."""
    def _raise_error(*args: Any, **kwargs: Any) -> Any:
        raise ConnectionRefusedError("Connection refused")

    monkeypatch.setattr("urllib.request.urlopen", _raise_error)
    models = fetch_available_ollama_models()
    assert models == []


# ---------------------------------------------------------------------------
# 3. Interactive Selection Tests
# ---------------------------------------------------------------------------


def test_interactive_model_selection_mock_choice() -> None:
    """Verify choosing Offline Mock skips live provider and sets use_mock=True."""
    mock_select = MagicMock()
    mock_select.ask.return_value = "mock"

    with patch("questionary.select", return_value=mock_select):
        result = interactive_model_selection()

    assert result["use_mock"] is True
    assert result["provider"] is None
    assert result["model"] is None


def test_interactive_model_selection_ollama_choice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify selecting Local Ollama selects installed model."""
    monkeypatch.setattr(
        "tests.evaluation.scripts.run_benchmark.fetch_available_ollama_models",
        lambda: ["qwen2.5:3b"],
    )

    call_count = 0

    def _mock_select(prompt: str, choices: list[Any], **kwargs: Any) -> Any:
        nonlocal call_count
        call_count += 1
        sub_mock = MagicMock()
        if call_count == 1:
            # First question: Provider selection
            sub_mock.ask.return_value = "ollama"
        else:
            # Second question: Model selection
            sub_mock.ask.return_value = "qwen2.5:3b"
        return sub_mock

    with patch("questionary.select", side_effect=_mock_select):
        result = interactive_model_selection()

    assert result["use_mock"] is False
    assert result["provider"] == "ollama"
    assert result["model"] == "qwen2.5:3b"
    assert result["temperature"] == 0.2


# ---------------------------------------------------------------------------
# 4. Live LLM Setup Helper
# ---------------------------------------------------------------------------


def test_setup_benchmark_llm_delegates_to_factory(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify setup_benchmark_llm passes provider and model to create_configured_llm."""
    mock_llm = MagicMock()
    mock_llm.model_name = "qwen2.5:3b"
    mock_create = MagicMock(return_value=mock_llm)
    mock_set = MagicMock()

    monkeypatch.setattr(
        "tests.evaluation.scripts.run_benchmark.create_configured_llm", mock_create
    )
    monkeypatch.setattr(
        "tests.evaluation.scripts.run_benchmark.set_llm", mock_set
    )

    provider, model, use_mock = setup_benchmark_llm(
        provider="ollama",
        model="qwen2.5:3b",
        temperature=0.2,
        use_mock=False,
    )

    assert use_mock is False
    assert provider == "ollama"
    assert model == "qwen2.5:3b"
    mock_create.assert_called_once_with(
        provider="ollama",
        model="qwen2.5:3b",
        temperature=0.2,
    )
    mock_set.assert_called_once_with(mock_llm)
