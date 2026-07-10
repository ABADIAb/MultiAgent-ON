"""Tests for the Intent Ingest node (Exp 1.0).

Validates that the node extracts the operator's NL intent from messages,
calls the LLM for structured output, and populates enriched_intent in state.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel


class TestIntentIngestNode:
    """Test the intent_ingest_node function."""

    def _make_state(self, user_msg: str = "Route from Milano-A to Milano-D") -> dict:
        """Create a minimal V4 AgentState dict."""
        return {
            "messages": [HumanMessage(content=user_msg)],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
        }

    def test_returns_enriched_intent(self):
        """Node must return a dict with enriched_intent populated."""
        from src.agents.intent_ingest import IntentSummary, intent_ingest_node
        from src.core import llm as llm_module

        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Route optical path from Milano-A to Milano-D",
            source_node="Milano-A",
            target_node="Milano-D",
        )

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured

        llm_module.set_llm(mock_llm)
        try:
            result = intent_ingest_node(self._make_state())
            assert result["enriched_intent"] is not None
            assert "Milano-A" in result["enriched_intent"]
            assert "Milano-D" in result["enriched_intent"]
        finally:
            llm_module._llm = None

    def test_returns_messages_with_ai_response(self):
        """Node must append an AIMessage summarizing the parsed intent."""
        from src.agents.intent_ingest import IntentSummary, intent_ingest_node
        from src.core import llm as llm_module

        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Topology query",
            source_node=None,
            target_node=None,
        )

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured

        llm_module.set_llm(mock_llm)
        try:
            result = intent_ingest_node(self._make_state())
            assert "messages" in result
            assert len(result["messages"]) == 1
            assert isinstance(result["messages"][0], AIMessage)
        finally:
            llm_module._llm = None

    def test_handles_no_user_messages(self):
        """Node must handle state with no human messages gracefully."""
        from src.agents.intent_ingest import intent_ingest_node
        from src.core import llm as llm_module

        mock_llm = MagicMock()
        llm_module.set_llm(mock_llm)
        try:
            state = self._make_state()
            state["messages"] = []
            result = intent_ingest_node(state)
            assert result["enriched_intent"] is None
            assert result["error_context"] is not None
        finally:
            llm_module._llm = None

    def test_llm_called_with_structured_output(self):
        """Node must use with_structured_output for structured parsing."""
        from src.agents.intent_ingest import IntentSummary, intent_ingest_node
        from src.core import llm as llm_module

        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Test",
            source_node=None,
            target_node=None,
        )

        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured

        llm_module.set_llm(mock_llm)
        try:
            intent_ingest_node(self._make_state())
            mock_llm.with_structured_output.assert_called_once_with(IntentSummary)
        finally:
            llm_module._llm = None


class TestIntentSummaryModel:
    """Test the IntentSummary Pydantic model."""

    def test_minimal_creation(self):
        from src.agents.intent_ingest import IntentSummary

        summary = IntentSummary(summary="Route from A to B")
        assert summary.summary == "Route from A to B"
        assert summary.source_node is None
        assert summary.target_node is None

    def test_full_creation(self):
        from src.agents.intent_ingest import IntentSummary

        summary = IntentSummary(
            summary="Route from Milano-A to Milano-D with 100G",
            source_node="Milano-A",
            target_node="Milano-D",
        )
        assert summary.source_node == "Milano-A"
        assert summary.target_node == "Milano-D"

    def test_serialization_roundtrip(self):
        from src.agents.intent_ingest import IntentSummary

        original = IntentSummary(
            summary="Test intent",
            source_node="A",
            target_node="B",
        )
        data = original.model_dump()
        restored = IntentSummary.model_validate(data)
        assert restored == original
