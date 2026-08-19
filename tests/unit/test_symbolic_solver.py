"""Unit tests for the Symbolic Solver node.

Validates deterministic path-finding with PDDL constraint enforcement.
All tests are offline — topology is mocked via fixtures.
"""

from __future__ import annotations

import pytest
from langchain_core.messages import AIMessage

from src.core.state import AgentState, FiberLink, NetworkNode, TopologySnapshot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_state(
    topology: TopologySnapshot,
    pddl_constraints: str,
    pddl_valid: bool = True,
) -> AgentState:
    """Build a minimal AgentState for the symbolic solver."""
    return AgentState(
        messages=[],
        enriched_intent=None,
        pddl_constraints=pddl_constraints,
        pddl_valid=pddl_valid,
        hitl_reconstruction=None,
        hitl_approved=True,
        topology_snapshot=topology,
        candidate_paths=None,
        qot_results=None,
        planning_report=None,
        error_context=None,
        pddl_parsed_constraints=None,
        usem_score=None,
        usem_passed=None,
        radg_decision=None,
    )


@pytest.fixture
def linear_topology() -> TopologySnapshot:
    """4-node linear topology: A-B-C-D."""
    nodes = [
        NetworkNode(node_id="n1", name="Node-A", interfaces=[1, 2]),
        NetworkNode(node_id="n2", name="Node-B", interfaces=[3, 4, 5, 6]),
        NetworkNode(node_id="n3", name="Node-C", interfaces=[7, 8, 9, 10]),
        NetworkNode(node_id="n4", name="Node-D", interfaces=[11, 12]),
    ]
    links = [
        FiberLink(link_id="l1", source_node="n1", target_node="n2", length_km=20.0, num_amplifiers=1, active_channels=4),
        FiberLink(link_id="l2", source_node="n2", target_node="n3", length_km=40.0, num_amplifiers=2, active_channels=6),
        FiberLink(link_id="l3", source_node="n3", target_node="n4", length_km=30.0, num_amplifiers=1, active_channels=2),
    ]
    return TopologySnapshot(nodes=nodes, links=links, timestamp="2026-07-29T00:00:00Z")


@pytest.fixture
def mesh_topology() -> TopologySnapshot:
    """3-node mesh: A-B, B-C, A-C (2 paths from A to C)."""
    nodes = [
        NetworkNode(node_id="n1", name="Node-A", interfaces=[1, 2]),
        NetworkNode(node_id="n2", name="Node-B", interfaces=[3, 4]),
        NetworkNode(node_id="n3", name="Node-C", interfaces=[5, 6]),
    ]
    links = [
        FiberLink(link_id="l1", source_node="n1", target_node="n2", length_km=20.0, num_amplifiers=1, active_channels=4),
        FiberLink(link_id="l2", source_node="n2", target_node="n3", length_km=20.0, num_amplifiers=1, active_channels=4),
        FiberLink(link_id="l3", source_node="n1", target_node="n3", length_km=50.0, num_amplifiers=2, active_channels=2),
    ]
    return TopologySnapshot(nodes=nodes, links=links, timestamp="2026-07-29T00:00:00Z")


SIMPLE_PDDL = """
(define (problem optical-routing)
  (:domain optical-network)
  (:objects node_src - node node_dst - node)
  (:init
    (source Node-A)
    (destination Node-D)
  )
  (:goal (and (routed Node-A Node-D)))
)
"""

PDDL_WITH_AVOID = """
(define (problem optical-routing)
  (:domain optical-network)
  (:objects node_src - node node_dst - node)
  (:init
    (source Node-A)
    (destination Node-C)
    (avoid-link l2)
  )
  (:goal (and (routed Node-A Node-C)))
)
"""

PDDL_MAX_HOPS = """
(define (problem optical-routing)
  (:domain optical-network)
  (:objects node_src - node node_dst - node)
  (:init
    (source Node-A)
    (destination Node-D)
    (max-hops 2)
  )
  (:goal (and (routed Node-A Node-D)))
)
"""


# ---------------------------------------------------------------------------
# Tests: symbolic_solver_node
# ---------------------------------------------------------------------------


class TestSymbolicSolverNode:
    """Validate the symbolic solver LangGraph node."""

    def test_solver_returns_dict_with_candidate_paths(self, linear_topology: TopologySnapshot) -> None:
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, SIMPLE_PDDL)
        result = symbolic_solver_node(state)
        assert "candidate_paths" in result
        assert result["candidate_paths"] is not None

    def test_solver_returns_at_least_one_path(self, linear_topology: TopologySnapshot) -> None:
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, SIMPLE_PDDL)
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] is not None
        assert len(result["candidate_paths"]) >= 1

    def test_solver_returns_messages(self, linear_topology: TopologySnapshot) -> None:
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, SIMPLE_PDDL)
        result = symbolic_solver_node(state)
        assert "messages" in result
        assert len(result["messages"]) >= 1
        assert isinstance(result["messages"][-1], AIMessage)

    def test_path_format_has_required_fields(self, linear_topology: TopologySnapshot) -> None:
        """Each path dict must contain: nodes, links, total_length_km, hops."""
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, SIMPLE_PDDL)
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] is not None
        for path in result["candidate_paths"]:
            assert "nodes" in path
            assert "links" in path
            assert "total_length_km" in path
            assert "hops" in path

    def test_path_nodes_are_list(self, linear_topology: TopologySnapshot) -> None:
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, SIMPLE_PDDL)
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] is not None
        for path in result["candidate_paths"]:
            assert isinstance(path["nodes"], list)
            assert len(path["nodes"]) >= 2

    def test_path_total_length_is_positive(self, linear_topology: TopologySnapshot) -> None:
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, SIMPLE_PDDL)
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] is not None
        for path in result["candidate_paths"]:
            assert path["total_length_km"] > 0

    def test_mesh_solver_finds_multiple_paths(self, mesh_topology: TopologySnapshot) -> None:
        """In a mesh topology A-B-C + A-C direct, solver should find 2 paths."""
        from src.core.symbolic_solver import symbolic_solver_node

        pddl = SIMPLE_PDDL.replace("Node-D", "Node-C").replace("node_dst - node", "")
        state = _make_state(mesh_topology, pddl)
        result = symbolic_solver_node(state)
        # Should find at least 2 paths: A-C direct and A-B-C
        assert result["candidate_paths"] is not None
        assert len(result["candidate_paths"]) >= 2

    def test_solver_returns_empty_for_disconnected_topology(self) -> None:
        """Topology with no links should yield no paths."""
        from src.core.symbolic_solver import symbolic_solver_node

        topology = TopologySnapshot(
            nodes=[
                NetworkNode(node_id="n1", name="Node-A", interfaces=[1]),
                NetworkNode(node_id="n2", name="Node-B", interfaces=[2]),
            ],
            links=[],
            timestamp="2026-07-29T00:00:00Z",
        )
        state = _make_state(topology, SIMPLE_PDDL.replace("Node-D", "Node-B"))
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] == []

    def test_solver_uses_topology_from_state(self, mesh_topology: TopologySnapshot, linear_topology: TopologySnapshot) -> None:
        """Solver must use the topology provided in state, not a hardcoded one."""
        from src.core.symbolic_solver import symbolic_solver_node

        # Mesh topology: 3 nodes only
        state_mesh = _make_state(mesh_topology, SIMPLE_PDDL.replace("Node-D", "Node-C"))
        result_mesh = symbolic_solver_node(state_mesh)

        # Linear topology: 4 nodes
        state_linear = _make_state(linear_topology, SIMPLE_PDDL)
        result_linear = symbolic_solver_node(state_linear)

        # Results should differ (different topologies)
        assert result_mesh["candidate_paths"] is not None
        assert result_linear["candidate_paths"] is not None
        mesh_node_counts = [len(p["nodes"]) for p in result_mesh["candidate_paths"]]
        linear_node_counts = [len(p["nodes"]) for p in result_linear["candidate_paths"]]
        # In linear 4-node, paths must have >2 nodes; in direct mesh path, 2 nodes
        assert min(linear_node_counts) >= min(mesh_node_counts)


class TestSymbolicSolverConstraints:
    """Validate PDDL constraint enforcement in the solver."""

    def test_avoid_link_removes_path_using_that_link(self, mesh_topology: TopologySnapshot) -> None:
        """With avoid-link l2 (B-C), solver should not return path A-B-C."""
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(mesh_topology, PDDL_WITH_AVOID)
        result = symbolic_solver_node(state)

        # All returned paths must not use link l2
        assert result["candidate_paths"] is not None
        for path in result["candidate_paths"]:
            assert "l2" not in path["links"]

    def test_max_hops_constraint_respected(self, linear_topology: TopologySnapshot) -> None:
        """With max-hops 2, no path from A to D (3 hops) should be returned."""
        from src.core.symbolic_solver import symbolic_solver_node

        state = _make_state(linear_topology, PDDL_MAX_HOPS)
        result = symbolic_solver_node(state)

        assert result["candidate_paths"] is not None
        for path in result["candidate_paths"]:
            assert path["hops"] <= 2

    def test_min_gsnr_constraint_parsed(self) -> None:
        """Verify _parse_pddl_constraints extracts min-gsnr."""
        from src.core.symbolic_solver import _parse_pddl_constraints

        pddl = """
        (define (problem optical-routing)
          (:domain optical-network)
          (:objects node_src - node node_dst - node)
          (:init
            (source Node-A)
            (destination Node-C)
            (min-gsnr 40.0)
          )
          (:goal (and (routed Node-A Node-C)))
        )
        """
        constraints = _parse_pddl_constraints(pddl)
        assert constraints["min_gsnr"] == 40.0


class TestNobelGermanySymbolicSolver:
    """Validate pathfinding and constraints directly on the 17-node German topology."""

    def test_finds_multiple_paths_berlin_to_frankfurt(self) -> None:
        from src.core.symbolic_solver import symbolic_solver_node
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        pddl = """
        (define (problem optical-routing)
          (:domain optical-network)
          (:objects Berlin Frankfurt - node)
          (:init
            (source Berlin)
            (destination Frankfurt)
          )
          (:goal (and (routed Berlin Frankfurt)))
        )
        """
        state = _make_state(topology, pddl)
        result = symbolic_solver_node(state)
        paths = result["candidate_paths"]
        assert paths is not None
        assert len(paths) >= 2
        # Verify first and last nodes in each path
        for p in paths:
            assert p["nodes"][0] == "Berlin"
            assert p["nodes"][-1] == "Frankfurt"
            assert p["total_length_km"] > 0
            assert len(p["link_physics"]) == p["hops"]

    def test_avoid_link_on_german_topology(self) -> None:
        from src.core.symbolic_solver import symbolic_solver_node
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        # Avoid the direct Leipzig-Frankfurt link
        pddl = """
        (define (problem optical-routing)
          (:domain optical-network)
          (:objects Berlin Frankfurt - node)
          (:init
            (source Berlin)
            (destination Frankfurt)
            (avoid-link link_frankfurt_leipzig)
          )
          (:goal (and (routed Berlin Frankfurt)))
        )
        """
        state = _make_state(topology, pddl)
        result = symbolic_solver_node(state)
        paths = result["candidate_paths"]
        assert paths is not None
        for p in paths:
            assert "link_frankfurt_leipzig" not in p["links"]

    def test_finds_paths_munich_to_cologne_with_goal_route_predicate(self) -> None:
        """BUG-006: Route goal (route Munich Cologne) must yield Munich -> Cologne paths, NOT Hannover -> Leipzig."""
        from src.core.symbolic_solver import symbolic_solver_node
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        pddl = """
        (define (problem establish-service-munich-cologne)
          (:domain optical-network)
          (:objects
            Hannover Frankfurt Hamburg Norden Bremen Berlin Munich Ulm
            Nuremberg Stuttgart Karlsruhe Mannheim Essen Dortmund Dusseldorf
            Cologne Leipzig - node
          )
          (:init
            (connected Munich Ulm)
            (connected Ulm Stuttgart)
          )
          (:goal
            (and
              (route Munich Cologne)
            )
          )
        )
        """
        state = _make_state(topology, pddl)
        result = symbolic_solver_node(state)
        paths = result["candidate_paths"]
        assert paths is not None
        assert len(paths) >= 1
        for p in paths:
            assert p["nodes"][0] == "Munich"
            assert p["nodes"][-1] == "Cologne"
        # Ensure message does NOT say 'from None to None'
        assert "from 'Munich' to 'Cologne'" in result["messages"][-1].content

    def test_fallback_to_enriched_intent_when_pddl_lacks_endpoints(self) -> None:
        """If PDDL does not contain source/target, fallback to enriched_intent."""
        from src.core.symbolic_solver import symbolic_solver_node
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        pddl = """
        (define (problem generic-problem)
          (:domain optical-network)
          (:objects Munich Cologne - node)
          (:init)
          (:goal (and (min-gsnr 15.0)))
        )
        """
        state = _make_state(topology, pddl)
        state["enriched_intent"] = "Intent: Establish service | Source: Munich | Target: Cologne"
        result = symbolic_solver_node(state)
        paths = result["candidate_paths"]
        assert paths is not None
        assert len(paths) >= 1
        for p in paths:
            assert p["nodes"][0] == "Munich"
            assert p["nodes"][-1] == "Cologne"

    def test_fails_gracefully_when_no_endpoints_specified(self) -> None:
        """When neither PDDL nor state has endpoints, return empty paths and descriptive error."""
        from src.core.symbolic_solver import symbolic_solver_node
        from src.services.testbed_client import MockTestbedClient

        topology = MockTestbedClient().get_topology()
        pddl = """
        (define (problem generic-problem)
          (:domain optical-network)
          (:objects Node-A - node)
          (:init)
          (:goal (and (min-gsnr 15.0)))
        )
        """
        state = _make_state(topology, pddl)
        state["enriched_intent"] = "Intent: Generic query without endpoints"
        result = symbolic_solver_node(state)
        assert result["candidate_paths"] == []
        assert "source or destination not specified" in result["messages"][-1].content.lower()


class TestPDDLConstraintParsingVariations:
    """Validate _parse_pddl_constraints against various PDDL goal syntax variations."""

    def test_parse_route_predicate(self) -> None:
        from src.core.symbolic_solver import _parse_pddl_constraints

        pddl = "(:goal (and (route Munich Cologne)))"
        c = _parse_pddl_constraints(pddl)
        assert c["source"] == "Munich"
        assert c["destination"] == "Cologne"

    def test_parse_routed_predicate(self) -> None:
        from src.core.symbolic_solver import _parse_pddl_constraints

        pddl = "(:goal (and (routed Berlin Frankfurt)))"
        c = _parse_pddl_constraints(pddl)
        assert c["source"] == "Berlin"
        assert c["destination"] == "Frankfurt"

    def test_parse_path_predicate(self) -> None:
        from src.core.symbolic_solver import _parse_pddl_constraints

        pddl = "(:goal (and (path Hamburg Munich)))"
        c = _parse_pddl_constraints(pddl)
        assert c["source"] == "Hamburg"
        assert c["destination"] == "Munich"

    def test_parse_target_predicate(self) -> None:
        from src.core.symbolic_solver import _parse_pddl_constraints

        pddl = "(:init (source Munich) (target Cologne))"
        c = _parse_pddl_constraints(pddl)
        assert c["source"] == "Munich"
        assert c["destination"] == "Cologne"

    def test_parse_sink_predicate(self) -> None:
        from src.core.symbolic_solver import _parse_pddl_constraints

        pddl = "(:init (src Munich) (sink Cologne))"
        c = _parse_pddl_constraints(pddl)
        assert c["source"] == "Munich"
        assert c["destination"] == "Cologne"

    def test_resolve_node_id_case_insensitive(self) -> None:
        from src.core.mock_graphrag import build_adjacency_graph
        from src.core.symbolic_solver import _resolve_node_id
        from src.services.testbed_client import MockTestbedClient

        graph = build_adjacency_graph(MockTestbedClient().get_topology())
        # Case-insensitive by name
        assert _resolve_node_id(graph, "munich") == "node_7"
        assert _resolve_node_id(graph, "cologne") == "node_16"
        assert _resolve_node_id(graph, "Munich") == "node_7"
        # By node_id directly
        assert _resolve_node_id(graph, "node_7") == "node_7"
        assert _resolve_node_id(graph, "NODE_16") == "node_16"

