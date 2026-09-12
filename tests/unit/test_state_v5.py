"""Tests for the V5 Risk-Adaptive Neurosymbolic AgentState schema.

Validates the V5 state fields (PDDL constraints, PDDL parsed constraints, HITL approval,
candidate paths, QoT results, planning report) alongside the
topology models that survive from V3.
"""

from __future__ import annotations

import operator
from typing import get_type_hints, Annotated

import pytest

from src.core.state import (
    AgentState,
    FiberLink,
    NetworkNode,
    TopologySnapshot,
)


class TestAgentStateV5Fields:
    """Verify V5 neurosymbolic state fields exist and have correct types."""

    def test_state_has_enriched_intent(self):
        """State must have enriched_intent field."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": "Route from A to B with min 10 dB SNR",
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
        }
        assert state["enriched_intent"] == "Route from A to B with min 10 dB SNR"

    def test_state_has_pddl_constraints(self):
        """State must have pddl_constraints field for PDDL output."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": "(define (problem optical-route) ...)",
            "pddl_valid": True,
            "pddl_parsed_constraints": {"source": "Milano-A", "destination": "Milano-D"},
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
        }
        assert state["pddl_constraints"] is not None
        assert state["pddl_valid"] is True
        assert state["pddl_parsed_constraints"] == {"source": "Milano-A", "destination": "Milano-D"}

    def test_state_has_hitl_fields(self):
        """State must have HITL reconstruction and approval fields."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "hitl_reconstruction": "I understand you want to route from Milano-A to Milano-D",
            "hitl_approved": True,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
        }
        assert state["hitl_reconstruction"] is not None
        assert state["hitl_approved"] is True

    def test_state_has_candidate_paths(self):
        """State must have candidate_paths for Symbolic Solver output."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": [["node_1", "node_2", "node_3"]],
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
        }
        assert state["candidate_paths"] is not None
        assert len(state["candidate_paths"]) == 1

    def test_state_has_qot_results(self):
        """State must have qot_results for QoT validation output."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": [{"feasible": True, "snr_dB": 15.2}],
            "planning_report": None,
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
        }
        assert state["qot_results"] is not None
        assert state["qot_results"][0]["feasible"] is True

    def test_state_has_planning_report(self):
        """State must have planning_report for final synthesis."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": "Route Milano-A → Milano-D is feasible.",
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
        }
        assert state["planning_report"] is not None
        assert "feasible" in state["planning_report"]

    def test_state_has_v5_semantic_gate_fields(self):
        """State must have usem_score and usem_passed for V5 Semantic Gate."""
        hints = get_type_hints(AgentState)
        assert "usem_score" in hints
        assert "usem_passed" in hints

    def test_state_has_v5_radg_field(self):
        """State must have radg_decision for V5 RADG gate."""
        hints = get_type_hints(AgentState)
        assert "radg_decision" in hints

    def test_state_has_topology_context_field(self):
        """State must have topology_context for Optical RAG subgraph serialization."""
        hints = get_type_hints(AgentState)
        assert "topology_context" in hints

    def test_state_has_active_intent_field(self):
        """State must have active_intent for reconciled operational intent."""
        hints = get_type_hints(AgentState)
        assert "active_intent" in hints

    def test_state_has_intent_reconciliation_fields(self):
        """State must have intent_update_reasoning and intent_update_type fields."""
        hints = get_type_hints(AgentState)
        assert "intent_update_reasoning" in hints
        assert "intent_update_type" in hints

    def test_fiber_link_has_amplifiers_field(self):
        """FiberLink must carry amplifiers list for QoT physics propagation."""
        link = FiberLink(
            link_id="l1",
            source_node="n1",
            target_node="n2",
            length_km=20.0,
        )
        assert hasattr(link, "amplifiers")
        assert isinstance(link.amplifiers, list)

    def test_fiber_link_has_port_loss_field(self):
        """FiberLink must carry port_loss_dB for QoT physics propagation."""
        link = FiberLink(
            link_id="l1",
            source_node="n1",
            target_node="n2",
            length_km=20.0,
        )
        assert link.port_loss_dB == 0.0

    def test_state_no_task_plan_field(self):
        """V5 state must NOT have the V3 task_plan field."""
        hints = get_type_hints(AgentState)
        assert "task_plan" not in hints

    def test_state_no_current_agent_field(self):
        """V5 state must NOT have the V3 current_agent field."""
        hints = get_type_hints(AgentState)
        assert "current_agent" not in hints

    def test_state_still_has_messages_reducer(self):
        """messages field must still use operator.add reducer."""
        hints = get_type_hints(AgentState, include_extras=True)
        msg_hint = hints["messages"]
        assert hasattr(msg_hint, "__metadata__")
        assert operator.add in msg_hint.__metadata__

    def test_state_still_has_topology_snapshot(self):
        """topology_snapshot must survive from V3."""
        hints = get_type_hints(AgentState)
        assert "topology_snapshot" in hints


class TestTopologyModelsUnchanged:
    """Verify V3 topology models are preserved and enriched for V5."""

    def test_network_node_creation(self):
        node = NetworkNode(node_id="n1", name="Milano-A", interfaces=[101, 102])
        assert node.name == "Milano-A"
        assert len(node.interfaces) == 2

    def test_fiber_link_creation_minimal(self):
        """FiberLink can be created with minimal required fields."""
        link = FiberLink(
            link_id="l1",
            source_node="n1",
            target_node="n2",
            length_km=20.0,
        )
        assert link.length_km == 20.0
        assert link.port_loss_dB == 0.0
        assert link.amplifiers == []

    def test_fiber_link_creation_full(self):
        """FiberLink accepts full V5 physics data."""
        link = FiberLink(
            link_id="l1",
            source_node="n1",
            target_node="n2",
            length_km=20.0,
            num_amplifiers=2,
            active_channels=4,
            port_loss_dB=0.5,
            amplifiers=[
                {"position_km": 0.0, "gain_dB": 13.0, "amp_type": "booster", "att_dB": 0.0}
            ],
        )
        assert link.port_loss_dB == 0.5
        assert len(link.amplifiers) == 1

    def test_topology_snapshot_creation(self):
        snap = TopologySnapshot(
            nodes=[NetworkNode(node_id="n1", name="Test", interfaces=[])],
            links=[],
            timestamp="2026-07-09T00:00:00Z",
        )
        assert len(snap.nodes) == 1


class TestUnifiedFiberLinkModel:
    """Verify the unified FiberLink model handles physics aliases and coercion."""

    def test_fiber_link_legacy_src_dst_node_id_aliases(self) -> None:
        """FiberLink accepts legacy src_node_id and dst_node_id."""
        link = FiberLink(
            link_id=1,  # int coerced to str
            src_node_id="n1",
            dst_node_id="n2",
            length_km=50.0,
        )
        assert link.link_id == "1"
        assert link.source_node == "n1"
        assert link.target_node == "n2"
        assert link.src_node_id == "n1"
        assert link.dst_node_id == "n2"

    def test_fiber_link_auto_converts_amplifier_dicts(self) -> None:
        """FiberLink automatically converts list of dicts to Amplifier models."""
        link = FiberLink(
            link_id="link_1",
            source_node="A",
            target_node="B",
            length_km=100.0,
            amplifiers=[
                {"position_km": 0.0, "gain_dB": 15.0, "amp_type": "booster"},
                {"position_km": 100.0, "gain_dB": 20.0, "amp_type": "preamp"},
            ],
        )
        assert len(link.amplifiers) == 2
        assert link.amplifiers[0].amp_type == "booster"
        assert link.amplifiers[0]["amp_type"] == "booster"
        assert link.amplifiers[1].amp_type == "preamp"
        assert link.num_amplifiers == 2

