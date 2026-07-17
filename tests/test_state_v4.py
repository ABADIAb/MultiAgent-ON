"""Tests for the V4 Neurosymbolic AgentState schema.

Validates the V4 state fields (PDDL constraints, HITL approval,
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


class TestAgentStateV4Fields:
    """Verify V4 neurosymbolic state fields exist and have correct types."""

    def test_state_has_enriched_intent(self):
        """State must have enriched_intent field."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": "Route from A to B with min 10 dB SNR",
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
        assert state["enriched_intent"] == "Route from A to B with min 10 dB SNR"

    def test_state_has_pddl_constraints(self):
        """State must have pddl_constraints field for PDDL output."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": "(define (problem optical-route) ...)",
            "pddl_valid": True,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
        }
        assert state["pddl_constraints"] is not None
        assert state["pddl_valid"] is True

    def test_state_has_hitl_fields(self):
        """State must have HITL reconstruction and approval fields."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "hitl_reconstruction": "I understand you want to route from Milano-A to Milano-D",
            "hitl_approved": True,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
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
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": [["node_1", "node_2", "node_3"]],
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
        }
        assert len(state["candidate_paths"]) == 1

    def test_state_has_qot_results(self):
        """State must have qot_results for QoT validation output."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": [{"feasible": True, "snr_dB": 15.2}],
            "planning_report": None,
            "error_context": None,
        }
        assert state["qot_results"][0]["feasible"] is True

    def test_state_has_planning_report(self):
        """State must have planning_report for final synthesis."""
        state: AgentState = {
            "messages": [],
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "topology_snapshot": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": "Route Milano-A → Milano-D is feasible.",
            "error_context": None,
        }
        assert "feasible" in state["planning_report"]

    def test_state_no_task_plan_field(self):
        """V4 state must NOT have the V3 task_plan field."""
        hints = get_type_hints(AgentState)
        assert "task_plan" not in hints

    def test_state_no_current_agent_field(self):
        """V4 state must NOT have the V3 current_agent field."""
        hints = get_type_hints(AgentState)
        assert "current_agent" not in hints

    def test_state_still_has_messages_reducer(self):
        """messages field must still use operator.add reducer."""
        hints = get_type_hints(AgentState, include_extras=True)
        msg_hint = hints["messages"]
        # Check it's Annotated with operator.add
        assert hasattr(msg_hint, "__metadata__")
        assert operator.add in msg_hint.__metadata__

    def test_state_still_has_topology_snapshot(self):
        """topology_snapshot must survive from V3."""
        hints = get_type_hints(AgentState)
        assert "topology_snapshot" in hints


class TestTopologyModelsUnchanged:
    """Verify V3 topology models are preserved."""

    def test_network_node_creation(self):
        node = NetworkNode(node_id="n1", name="Milano-A", interfaces=[101, 102])
        assert node.name == "Milano-A"
        assert len(node.interfaces) == 2

    def test_fiber_link_creation(self):
        link = FiberLink(
            link_id="l1",
            source_node="n1",
            target_node="n2",
            length_km=20.0,
            num_amplifiers=1,
            active_channels=4,
        )
        assert link.length_km == 20.0

    def test_topology_snapshot_creation(self):
        snap = TopologySnapshot(
            nodes=[NetworkNode(node_id="n1", name="Test", interfaces=[])],
            links=[],
            timestamp="2026-07-09T00:00:00Z",
        )
        assert len(snap.nodes) == 1
