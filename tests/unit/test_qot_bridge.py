"""Tests for the QoT Bridge — candidate path dict to models.FiberLink converter.

These tests ensure that physics data flows correctly from the Symbolic Solver
output (topology-level dicts) into the QoT calculator (physics-level Pydantic models).
All tests are offline — no LLM or testbed calls.
"""

from __future__ import annotations

import pytest

from src.core.qot_bridge import candidate_path_to_fiber_links


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

LINK_PHYSICS_AB = {
    "link_id": "link_ab",
    "length_km": 20.0,
    "port_loss_dB": 0.5,
    "amplifiers": [
        {"position_km": 0.0, "gain_dB": 13.0, "amp_type": "booster", "att_dB": 0.0},
        {"position_km": 20.0, "gain_dB": 15.0, "amp_type": "preamp", "att_dB": 0.0},
    ],
}

LINK_PHYSICS_BC = {
    "link_id": "link_bc",
    "length_km": 40.0,
    "port_loss_dB": 0.5,
    "amplifiers": [
        {"position_km": 0.0, "gain_dB": 13.0, "amp_type": "booster", "att_dB": 0.0},
        {"position_km": 20.0, "gain_dB": 15.0, "amp_type": "ila", "att_dB": 0.0},
        {"position_km": 40.0, "gain_dB": 15.0, "amp_type": "preamp", "att_dB": 0.0},
    ],
}

SINGLE_LINK_PATH = {
    "nodes": ["Milano-A", "Milano-B"],
    "links": ["link_ab"],
    "total_length_km": 20.0,
    "hops": 1,
    "link_physics": [LINK_PHYSICS_AB],
}

DOUBLE_LINK_PATH = {
    "nodes": ["Milano-A", "Milano-B", "Milano-C"],
    "links": ["link_ab", "link_bc"],
    "total_length_km": 60.0,
    "hops": 2,
    "link_physics": [LINK_PHYSICS_AB, LINK_PHYSICS_BC],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCandidatePathToFiberLinks:
    """Verify correct conversion from solver path dict to models.FiberLink list."""

    def test_single_link_path_returns_one_fiber_link(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        assert len(links) == 1

    def test_double_link_path_returns_two_fiber_links(self) -> None:
        links = candidate_path_to_fiber_links(DOUBLE_LINK_PATH)
        assert len(links) == 2

    def test_fiber_link_length_is_preserved(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        assert links[0].length_km == pytest.approx(20.0)

    def test_fiber_link_port_loss_is_preserved(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        assert links[0].port_loss_dB == pytest.approx(0.5)

    def test_fiber_link_amplifiers_count_matches_input(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        assert len(links[0].amplifiers) == 2

    def test_fiber_link_second_link_has_three_amplifiers(self) -> None:
        links = candidate_path_to_fiber_links(DOUBLE_LINK_PATH)
        assert len(links[1].amplifiers) == 3

    def test_amplifier_positions_are_preserved(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        positions = [a.position_km for a in links[0].amplifiers]
        assert positions == pytest.approx([0.0, 20.0])

    def test_amplifier_gains_are_preserved(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        gains = [a.gain_dB for a in links[0].amplifiers]
        assert gains == pytest.approx([13.0, 15.0])

    def test_amplifier_types_are_preserved(self) -> None:
        links = candidate_path_to_fiber_links(SINGLE_LINK_PATH)
        types = [a.amp_type for a in links[0].amplifiers]
        assert types == ["booster", "preamp"]

    def test_ila_type_is_preserved_on_second_link(self) -> None:
        links = candidate_path_to_fiber_links(DOUBLE_LINK_PATH)
        types = [a.amp_type for a in links[1].amplifiers]
        assert "ila" in types

    def test_link_ids_are_integer_indexed(self) -> None:
        """Bridge assigns sequential int IDs to satisfy models.FiberLink.link_id: int."""
        links = candidate_path_to_fiber_links(DOUBLE_LINK_PATH)
        assert links[0].link_id == 0
        assert links[1].link_id == 1

    def test_src_dst_node_ids_are_sequential(self) -> None:
        """src_node_id and dst_node_id are index-based within the path."""
        links = candidate_path_to_fiber_links(DOUBLE_LINK_PATH)
        # A→B: src=0, dst=1; B→C: src=1, dst=2
        assert links[0].src_node_id == 0
        assert links[0].dst_node_id == 1
        assert links[1].src_node_id == 1
        assert links[1].dst_node_id == 2


class TestCandidatePathToFiberLinksEdgeCases:
    """Edge cases: missing physics data, empty amplifier lists."""

    def test_empty_amplifiers_list_is_accepted(self) -> None:
        path = {
            "nodes": ["Milano-A", "Milano-B"],
            "links": ["link_ab"],
            "total_length_km": 20.0,
            "hops": 1,
            "link_physics": [
                {"link_id": "link_ab", "length_km": 20.0, "port_loss_dB": 0.0, "amplifiers": []}
            ],
        }
        links = candidate_path_to_fiber_links(path)
        assert len(links) == 1
        assert links[0].amplifiers == []

    def test_missing_port_loss_defaults_to_zero(self) -> None:
        path = {
            "nodes": ["A", "B"],
            "links": ["l"],
            "total_length_km": 10.0,
            "hops": 1,
            "link_physics": [
                {"link_id": "l", "length_km": 10.0, "amplifiers": []}
                # port_loss_dB intentionally missing
            ],
        }
        links = candidate_path_to_fiber_links(path)
        assert links[0].port_loss_dB == pytest.approx(0.0)

    def test_missing_link_physics_raises_value_error(self) -> None:
        path = {
            "nodes": ["A", "B"],
            "links": ["l"],
            "total_length_km": 10.0,
            "hops": 1,
            # link_physics key missing entirely
        }
        with pytest.raises((KeyError, ValueError)):
            candidate_path_to_fiber_links(path)
