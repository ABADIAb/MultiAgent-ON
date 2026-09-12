"""Unit tests for the Intent Reconciler module (Strict TDD).

Validates prompt-engineered LLM reasoning for operator intent refinement:
1. Classification into FULL_REPLACEMENT vs PARTIAL_UPDATE
2. Detailed constraint delta analysis and unified active_intent synthesis
3. Fallback resilience on LLM errors
4. Subtopology neighborhood re-extraction when endpoints change
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.core.state import AgentState, NetworkNode, FiberLink, TopologySnapshot
from src.nodes.intent_reconciler import (
    IntentUpdateType,
    RefinedIntentAnalysis,
    reconcile_operator_intent,
    reconcile_and_enrich_intent,
)


class TestIntentReconcilerSchemas:
    """Verify enum and Pydantic model schemas."""

    def test_intent_update_type_values(self):
        """Must define full_replacement and partial_update."""
        assert IntentUpdateType.FULL_REPLACEMENT == "full_replacement"
        assert IntentUpdateType.PARTIAL_UPDATE == "partial_update"

    def test_refined_intent_analysis_instantiation(self):
        """Model must validate required fields."""
        analysis = RefinedIntentAnalysis(
            update_type=IntentUpdateType.PARTIAL_UPDATE,
            reasoning="Lowered GSNR threshold from 15 dB to 12 dB due to physical infeasibility.",
            updated_intent="Route traffic from Hamburg to Munich with min GSNR 12 dB avoiding Frankfurt",
            source_node="Hamburg",
            target_node="Munich",
            modified_constraints=["min_gsnr relaxed from 15 dB to 12 dB"],
        )
        assert analysis.update_type == IntentUpdateType.PARTIAL_UPDATE
        assert analysis.source_node == "Hamburg"
        assert analysis.target_node == "Munich"
        assert len(analysis.modified_constraints) == 1


class TestReconcileOperatorIntent:
    """Verify reconcile_operator_intent function with mocked LLM structured output."""

    @patch("src.nodes.intent_reconciler.get_llm")
    def test_partial_update_gsnr_relaxation(self, mock_get_llm):
        """Operator relaxes GSNR constraint after physical failure."""
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = RefinedIntentAnalysis(
            update_type=IntentUpdateType.PARTIAL_UPDATE,
            reasoning="Lowered min GSNR from 15 to 12 dB. Preserved endpoints Hamburg->Munich and avoid Frankfurt.",
            updated_intent="Route traffic from Hamburg to Munich with min GSNR 12 dB avoiding Frankfurt",
            source_node="Hamburg",
            target_node="Munich",
            modified_constraints=["min_gsnr updated from 15 dB to 12 dB"],
        )
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        current_intent = "Route traffic from Hamburg to Munich with min GSNR 15 dB avoiding Frankfurt"
        feedback = "All candidate paths failed physical validation. Lower GSNR threshold to 12 dB."

        result = reconcile_operator_intent(current_intent, feedback)

        assert result.update_type == IntentUpdateType.PARTIAL_UPDATE
        assert "12 dB" in result.updated_intent
        assert result.source_node == "Hamburg"
        assert result.target_node == "Munich"
        assert mock_structured.invoke.called

    @patch("src.nodes.intent_reconciler.get_llm")
    def test_full_replacement_discards_old_constraints(self, mock_get_llm):
        """Operator explicitly cancels previous intent and requests an entirely new path."""
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = RefinedIntentAnalysis(
            update_type=IntentUpdateType.FULL_REPLACEMENT,
            reasoning="Operator canceled previous request. Created new request between Cologne and Leipzig with 10 dB GSNR. Discarded Hamburg, Munich, Frankfurt.",
            updated_intent="Route traffic from Cologne to Leipzig with min GSNR 10 dB",
            source_node="Cologne",
            target_node="Leipzig",
            modified_constraints=["replaced entire request with Cologne -> Leipzig (min GSNR 10 dB)"],
        )
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        current_intent = "Route traffic from Hamburg to Munich with min GSNR 15 dB avoiding Frankfurt"
        feedback = "Cancel that. Establish a lightpath from Cologne to Leipzig with 10 dB GSNR."

        result = reconcile_operator_intent(current_intent, feedback)

        assert result.update_type == IntentUpdateType.FULL_REPLACEMENT
        assert "Cologne" in result.updated_intent
        assert "Leipzig" in result.updated_intent
        assert "Hamburg" not in result.updated_intent
        assert result.source_node == "Cologne"
        assert result.target_node == "Leipzig"

    @patch("src.nodes.intent_reconciler.get_llm")
    def test_partial_update_endpoint_redirection(self, mock_get_llm):
        """Operator updates destination while retaining source and compatible constraints."""
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = RefinedIntentAnalysis(
            update_type=IntentUpdateType.PARTIAL_UPDATE,
            reasoning="Target changed from Munich to Berlin. Source Hamburg and avoidance of Frankfurt retained.",
            updated_intent="Route traffic from Hamburg to Berlin with min GSNR 15 dB avoiding Frankfurt",
            source_node="Hamburg",
            target_node="Berlin",
            modified_constraints=["target changed from Munich to Berlin"],
        )
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        current_intent = "Route traffic from Hamburg to Munich with min GSNR 15 dB avoiding Frankfurt"
        feedback = "Actually, change destination to Berlin instead of Munich"

        result = reconcile_operator_intent(current_intent, feedback)

        assert result.update_type == IntentUpdateType.PARTIAL_UPDATE
        assert result.source_node == "Hamburg"
        assert result.target_node == "Berlin"
        assert "Berlin" in result.updated_intent

    @patch("src.nodes.intent_reconciler.get_llm")
    def test_fallback_on_llm_failure(self, mock_get_llm):
        """Gracefully fallback if LLM structured output invocation raises an exception."""
        mock_structured = MagicMock()
        mock_structured.invoke.side_effect = RuntimeError("API connection timeout")
        mock_llm = MagicMock()
        mock_llm.with_structured_output.return_value = mock_structured
        mock_get_llm.return_value = mock_llm

        current_intent = "Route traffic from Hamburg to Munich"
        feedback = "Relax GSNR to 12 dB"

        result = reconcile_operator_intent(current_intent, feedback)

        assert result.update_type == IntentUpdateType.PARTIAL_UPDATE
        assert "Hamburg" in result.updated_intent
        assert "Relax GSNR to 12 dB" in result.updated_intent
        assert "fallback" in result.reasoning.lower()


class TestReconcileAndEnrichIntent:
    """Verify reconcile_and_enrich_intent helper that refreshes state and subtopology."""

    @patch("src.nodes.intent_reconciler.reconcile_operator_intent")
    def test_reconciles_and_preserves_subtopology_when_endpoints_unchanged(self, mock_reconcile):
        """When endpoints do not change, existing subtopology snapshot is preserved."""
        mock_reconcile.return_value = RefinedIntentAnalysis(
            update_type=IntentUpdateType.PARTIAL_UPDATE,
            reasoning="GSNR relaxed.",
            updated_intent="Route from A to B with min 12 dB SNR",
            source_node="A",
            target_node="B",
            modified_constraints=["GSNR relaxed to 12 dB"],
        )

        state: AgentState = {
            "messages": [],
            "active_intent": "Route from A to B with min 15 dB SNR",
            "enriched_intent": "Route from A to B with min 15 dB SNR\nTopology Context:\nA-B",
            "topology_context": "A-B",
            "error_context": "Lower GSNR to 12 dB",
            "refinement_history": ["Lower GSNR to 12 dB"],
        }

        updates = reconcile_and_enrich_intent(state)

        assert updates["active_intent"] == "Route from A to B with min 12 dB SNR"
        assert updates["intent_update_type"] == "partial_update"
        assert "12 dB" in updates["enriched_intent"]
        assert "Topology Context:" in updates["enriched_intent"]

    @patch("src.nodes.intent_reconciler.reconcile_operator_intent")
    def test_refreshes_subtopology_when_endpoints_change(self, mock_reconcile):
        """When destination changes, mock GraphRAG re-extracts the k-hop neighborhood."""
        mock_reconcile.return_value = RefinedIntentAnalysis(
            update_type=IntentUpdateType.PARTIAL_UPDATE,
            reasoning="Target changed from B to C.",
            updated_intent="Route from A to C",
            source_node="A",
            target_node="C",
            modified_constraints=["target changed to C"],
        )

        topo = TopologySnapshot(
            nodes=[
                NetworkNode(node_id="A", name="A"),
                NetworkNode(node_id="B", name="B"),
                NetworkNode(node_id="C", name="C"),
            ],
            links=[
                FiberLink(link_id="L1", source_node="A", target_node="B", length_km=50.0),
                FiberLink(link_id="L2", source_node="B", target_node="C", length_km=60.0),
            ],
        )

        state: AgentState = {
            "messages": [],
            "active_intent": "Route from A to B",
            "enriched_intent": "Route from A to B",
            "error_context": "Change destination to C",
            "refinement_history": ["Change destination to C"],
            "topology_snapshot": topo,
        }

        updates = reconcile_and_enrich_intent(state)

        assert updates["active_intent"] == "Route from A to C"
        assert updates["subtopology_snapshot"] is not None
        assert "C" in {n.node_id for n in updates["subtopology_snapshot"].nodes}
        assert updates["topology_context"] is not None
        assert "C" in updates["topology_context"]
