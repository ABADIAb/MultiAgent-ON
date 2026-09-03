"""Comprehensive End-to-End QA Pipeline Flow Test Suite.

Validates all execution branches, conditional routing loops, Human-in-the-Loop
(HITL) interrupt/resume cycles, and edge cases for Architecture V5:
  1. Happy Path / Auto-Approve (Single-Pass Execution)
  2. Semantic Gate Clarification & Refinement Loop (U_sem > tau_sem)
  3. Physical Risk Gate (RADG) Replan & Constraint Relaxation Loop
  4. Complex Constraints (Avoid-Links & Max-Hops Filtering)
  5. Topology Edge Cases (Missing / Disconnected Endpoints)
  6. Interrupt Resumption Payload Resilience
  7. Checkpointer State Persistence Across Multi-Interruption Trajectories

All tests execute the fully compiled LangGraph StateGraph with InMemorySaver checkpointer.
"""

from __future__ import annotations

import re
from typing import Any
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from src.core.graph import compile_graph
from src.core.llm import set_llm
from src.nodes.intent_ingest import IntentSummary
from src.services.testbed_client import MockTestbedClient


# ---------------------------------------------------------------------------
# Test Fixtures and Helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_topology():
    """Return the standard 17-node Nobel-Germany topology snapshot."""
    return MockTestbedClient().get_topology()


@pytest.fixture
def checkpointer():
    """Return a fresh in-memory checkpointer."""
    return InMemorySaver()


@pytest.fixture(autouse=True)
def _cleanup_llm():
    """Reset LLM singleton after each test."""
    yield
    set_llm(None)  # type: ignore


def _make_initial_state(user_text: str, topology_snapshot) -> dict[str, Any]:
    """Build the standard initial state matching main.py."""
    return {
        "messages": [HumanMessage(content=user_text)],
        "enriched_intent": None,
        "pddl_constraints": None,
        "pddl_valid": None,
        "hitl_reconstruction": None,
        "hitl_approved": None,
        "topology_snapshot": topology_snapshot,
        "candidate_paths": None,
        "qot_results": None,
        "planning_report": None,
        "error_context": None,
        "usem_score": None,
        "usem_passed": None,
        "radg_decision": None,
        "topology_context": None,
    }


def _create_mock_llm(
    *,
    intent_summary: IntentSummary,
    pddl_handler: Any = None,
    reconstruction_handler: Any = None,
    agreement_score: float = 0.05,
) -> MagicMock:
    """Create a context-aware mock LLM that idempotently dispatches responses by node."""
    mock_llm = MagicMock()

    # Structured output for Intent Ingest
    mock_structured = MagicMock()
    mock_structured.invoke.return_value = intent_summary
    mock_llm.with_structured_output.return_value = mock_structured

    def _invoke_dispatcher(messages, *args, **kwargs):
        first_msg = messages[0] if messages else None
        system_prompt = getattr(first_msg, "content", "")
        user_content = messages[1].content if len(messages) > 1 else ""

        if "PDDL Parser module" in system_prompt:
            if callable(pddl_handler):
                return AIMessage(content=str(pddl_handler(user_content)))
            elif isinstance(pddl_handler, list):
                # If refinement feedback is present in user content, use the second PDDL
                if "Operator refinement feedback:" in user_content and len(pddl_handler) > 1:
                    return AIMessage(content=str(pddl_handler[1]))
                return AIMessage(content=str(pddl_handler[0]))
            elif isinstance(pddl_handler, str):
                return AIMessage(content=pddl_handler)
            return AIMessage(content="(define (problem default) (:domain optical-network))")

        elif "Reverse Prompting module" in system_prompt:
            pddl_text = user_content
            if callable(reconstruction_handler):
                return AIMessage(content=str(reconstruction_handler(pddl_text)))
            elif isinstance(reconstruction_handler, str):
                return AIMessage(content=reconstruction_handler)
            # Default dynamic reconstruction from PDDL
            src_m = re.search(r"\(route\s+([^\s)]+)\s+([^\s)]+)\)", pddl_text, re.I)
            snr_m = re.search(r"\(min-gsnr\s+([\d.]+)\)", pddl_text, re.I)
            src = src_m.group(1) if src_m else "source"
            dst = src_m.group(2) if src_m else "target"
            snr = f" with min GSNR {snr_m.group(1)} dB" if snr_m else ""
            return AIMessage(content=f"I understand you want to route from {src} to {dst}{snr}.")

        elif "semantic similarity evaluator" in system_prompt:
            return AIMessage(content=f"{agreement_score:.2f}")

        return AIMessage(content="OK")

    mock_llm.invoke.side_effect = _invoke_dispatcher
    return mock_llm


# ---------------------------------------------------------------------------
# 1. Happy Path / Auto-Approve Execution
# ---------------------------------------------------------------------------


class TestHappyPathExecution:
    """Validate single-pass execution from natural language to approved planning report."""

    def test_happy_path_auto_approve_single_pass(
        self, mock_topology, checkpointer
    ):
        """Operator submits clear feasible intent -> single-pass auto-approval with ZERO interrupts."""
        valid_pddl = (
            "(define (problem route-berlin-frankfurt)\n"
            "  (:domain optical-network)\n"
            "  (:objects Berlin Frankfurt Hannover - node)\n"
            "  (:init (connected Berlin Hannover) (connected Hannover Frankfurt))\n"
            "  (:goal (and (route Berlin Frankfurt) (min-gsnr 12.0)))\n"
            ")"
        )
        reconstruction_text = (
            "I understand you want to establish an optical lightpath from Berlin "
            "to Frankfurt with at least 12.0 dB GSNR."
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route from Berlin to Frankfurt with min GSNR 12 dB",
                source_node="Berlin",
                target_node="Frankfurt",
            ),
            pddl_handler=valid_pddl,
            reconstruction_handler=reconstruction_text,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-happy-path"}}

        initial_state = _make_initial_state(
            "Route from Berlin to Frankfurt with at least 12 dB GSNR", mock_topology
        )

        # 1. Single invocation runs completely from START to plan_synthesizer (0 interrupts)
        final_result = graph.invoke(initial_state, config=config)

        state_after = graph.get_state(config)
        assert state_after.next == ()  # Graph is completely finished

        # 2. Assertions on completed state
        assert final_result["pddl_valid"] is True
        assert final_result["usem_score"] == pytest.approx(0.05)
        assert final_result["usem_passed"] is True
        assert final_result["radg_decision"] == "approve"

        # Symbolic solver outputs
        candidate_paths = final_result["candidate_paths"]
        assert len(candidate_paths) > 0
        for path in candidate_paths:
            assert path["nodes"][0] == "Berlin"
            assert path["nodes"][-1] == "Frankfurt"

        # QoT results
        qot_results = final_result["qot_results"]
        assert len(qot_results) > 0
        feasible_results = [r for r in qot_results if r["feasible"]]
        assert len(feasible_results) > 0
        assert feasible_results[0]["snr_dB"] >= 12.0

        # Plan synthesizer
        planning_report = final_result["planning_report"]
        assert "Planning Report" in planning_report
        assert "RECOMMENDED PATH: Berlin" in planning_report
        assert "Frankfurt" in planning_report
        assert "✓ FEASIBLE" in planning_report


# ---------------------------------------------------------------------------
# 2. Semantic Gate Clarification & Refinement Loops (U_sem > tau_sem)
# ---------------------------------------------------------------------------


class TestSemanticGateLoops:
    """Validate fail-fast clarification and refinement loopback (Phase 3b HITL)."""

    def test_structural_pddl_error_triggers_refinement_loop_and_reparses(
        self, mock_topology, checkpointer
    ):
        """When PDDL has structural syntax failure (U_sem=1.0), pipeline interrupts at hitl_clarify."""
        invalid_pddl = "(define (problem broken (:domain optical-network)"
        corrected_pddl = (
            "(define (problem route-hamburg-munich)\n"
            "  (:domain optical-network)\n"
            "  (:objects Hamburg Munich Hannover Frankfurt - node)\n"
            "  (:init (connected Hamburg Hannover) (connected Hannover Frankfurt) (connected Frankfurt Munich))\n"
            "  (:goal (and (route Hamburg Munich) (min-gsnr 10.0)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route from Hamburg to Munich",
                source_node="Hamburg",
                target_node="Munich",
            ),
            pddl_handler=[invalid_pddl, corrected_pddl],
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-structural-loop"}}

        initial_state = _make_initial_state(
            "Route from Hamburg to Munich", mock_topology
        )

        # 1. First run halts at hitl_clarify interrupt due to U_sem = 1.0 (CFG fail)
        graph.invoke(initial_state, config=config)

        state_pass1 = graph.get_state(config)
        assert state_pass1.next == ("hitl_clarify",)
        assert state_pass1.tasks[0].interrupts[0].value["status"] == "clarification_required"

        # 2. Operator submits refinement feedback
        final_result = graph.invoke(
            Command(resume={"action": "refine", "feedback": "Fix syntax and close parenthesis"}),
            config=config,
        )

        # 3. Pipeline completes successfully after reparsing
        assert final_result["pddl_valid"] is True
        assert final_result["usem_passed"] is True
        assert final_result["radg_decision"] == "approve"
        assert "RECOMMENDED PATH: Hamburg" in final_result["planning_report"]
        assert "Munich" in final_result["planning_report"]

    def test_semantic_divergence_refinement_loop(
        self, mock_topology, checkpointer
    ):
        """When semantic divergence d_sem > tau_sem, pipeline interrupts at hitl_clarify and re-parses."""
        pddl_v1 = (
            "(define (problem route-koln-berlin)\n"
            "  (:domain optical-network)\n"
            "  (:objects Cologne Berlin - node)\n"
            "  (:init (connected Cologne Berlin))\n"
            "  (:goal (and (route Cologne Berlin) (min-gsnr 10.0)))\n"
            ")"
        )
        pddl_v2 = (
            "(define (problem route-koln-berlin-avoid)\n"
            "  (:domain optical-network)\n"
            "  (:objects Cologne Berlin Dortmund Hannover - node)\n"
            "  (:init (connected Cologne Dortmund) (connected Dortmund Hannover) (connected Hannover Berlin))\n"
            "  (:goal (and (route Cologne Berlin) (avoid-link \"Cologne Frankfurt\") (min-gsnr 10.0)))\n"
            ")"
        )

        # First pass scores 0.6 divergence (fails), second pass scores 0.05 (passes)
        call_count = {"count": 0}

        def _mock_dispatcher(messages, *args, **kwargs):
            first_msg = messages[0] if messages else None
            system_prompt = getattr(first_msg, "content", "")
            user_content = messages[1].content if len(messages) > 1 else ""

            if "PDDL Parser module" in system_prompt:
                if "Operator refinement feedback:" in user_content:
                    return AIMessage(content=pddl_v2)
                return AIMessage(content=pddl_v1)
            elif "Reverse Prompting module" in system_prompt:
                return AIMessage(content="I understand you want to route from Cologne to Berlin.")
            elif "semantic similarity evaluator" in system_prompt:
                call_count["count"] += 1
                if call_count["count"] == 1:
                    return AIMessage(content="0.60")  # High divergence
                return AIMessage(content="0.05")  # Low divergence on pass 2
            return AIMessage(content="OK")

        mock_llm = MagicMock()
        mock_structured = MagicMock()
        mock_structured.invoke.return_value = IntentSummary(
            summary="Route from Cologne to Berlin avoiding Frankfurt",
            source_node="Cologne",
            target_node="Berlin",
        )
        mock_llm.with_structured_output.return_value = mock_structured
        mock_llm.invoke.side_effect = _mock_dispatcher
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-semantic-divergence-loop"}}

        initial_state = _make_initial_state(
            "Route from Cologne to Berlin avoiding Frankfurt", mock_topology
        )

        # Pass 1: halts at hitl_clarify because U_sem = 0.60 > 0.3
        graph.invoke(initial_state, config=config)

        state_pass1 = graph.get_state(config)
        assert state_pass1.next == ("hitl_clarify",)

        # Operator provides clarification feedback
        final_result = graph.invoke(
            Command(resume={"action": "refine", "feedback": "Please avoid the Cologne to Frankfurt link"}),
            config=config,
        )

        assert final_result["pddl_valid"] is True
        assert final_result["usem_passed"] is True
        assert final_result["radg_decision"] == "approve"


# ---------------------------------------------------------------------------
# 3. Physical Risk Gate (RADG) Replan & Constraint Relaxation Loop
# ---------------------------------------------------------------------------


class TestRadgReplanLoops:
    """Validate Physical Risk Gate (RADG) failure, replan interrupt, and constraint relaxation."""

    def test_infeasible_gsnr_triggers_radg_replan_and_relaxes(
        self, mock_topology, checkpointer
    ):
        """When intent sets min-gsnr 45.0 dB (physically impossible), RADG triggers replan and loops back."""
        impossible_pddl = (
            "(define (problem route-bremen-leipzig)\n"
            "  (:domain optical-network)\n"
            "  (:objects Bremen Leipzig Hannover - node)\n"
            "  (:init (connected Bremen Hannover) (connected Hannover Leipzig))\n"
            "  (:goal (and (route Bremen Leipzig) (min-gsnr 45.0)))\n"
            ")"
        )
        relaxed_pddl = (
            "(define (problem route-bremen-leipzig-relaxed)\n"
            "  (:domain optical-network)\n"
            "  (:objects Bremen Leipzig Hannover - node)\n"
            "  (:init (connected Bremen Hannover) (connected Hannover Leipzig))\n"
            "  (:goal (and (route Bremen Leipzig) (min-gsnr 12.0)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route from Bremen to Leipzig with 45 dB GSNR",
                source_node="Bremen",
                target_node="Leipzig",
            ),
            pddl_handler=[impossible_pddl, relaxed_pddl],
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-radg-replan-loop"}}

        initial_state = _make_initial_state(
            "Route from Bremen to Leipzig with 45 dB GSNR", mock_topology
        )

        # 1. First execution: passes semantic gate autonomously, then halts at RADG replan interrupt!
        graph.invoke(initial_state, config=config)

        radg_state = graph.get_state(config)
        assert radg_state.next == ("radg",)
        radg_payload = radg_state.tasks[0].interrupts[0].value
        assert radg_payload["decision"] == "replan"
        assert "SUGGEST REPLAN" in radg_payload["reason"]
        assert "lowering the minimum GSNR threshold" in radg_payload["suggestion"]

        # 2. Operator resumes RADG interrupt with relaxed constraint feedback
        final_result = graph.invoke(
            Command(resume={"action": "refine", "feedback": "Relax GSNR threshold to 12 dB"}),
            config=config,
        )

        # 3. Assertions on approved final plan
        assert final_result["radg_decision"] == "approve"
        assert len(final_result["candidate_paths"]) > 0
        assert any(r["feasible"] for r in final_result["qot_results"])
        assert "RECOMMENDED PATH: Bremen" in final_result["planning_report"]
        assert "Leipzig" in final_result["planning_report"]


# ---------------------------------------------------------------------------
# 4. Complex Constraints: Avoid-Links & Max-Hops Filtering
# ---------------------------------------------------------------------------


class TestComplexConstraintFiltering:
    """Validate symbolic solver constraint filtering propagating to final plan."""

    def test_avoid_link_constraint_filters_paths(
        self, mock_topology, checkpointer
    ):
        """Avoid link constraint removes direct edge and selects valid detour in a single pass."""
        pddl_with_avoid = (
            "(define (problem route-hamburg-berlin-detour)\n"
            "  (:domain optical-network)\n"
            "  (:objects Hamburg Berlin Hannover Bremen - node)\n"
            "  (:init (connected Hamburg Bremen) (connected Bremen Hannover) (connected Hannover Berlin))\n"
            "  (:goal (and (route Hamburg Berlin) (avoid-link \"Hamburg Berlin\") (min-gsnr 10.0)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route Hamburg to Berlin avoiding direct link",
                source_node="Hamburg",
                target_node="Berlin",
            ),
            pddl_handler=pddl_with_avoid,
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-avoid-link"}}

        initial_state = _make_initial_state(
            "Route Hamburg to Berlin avoiding direct link", mock_topology
        )

        # Single pass execution (0 interrupts)
        final_result = graph.invoke(initial_state, config=config)

        assert final_result["radg_decision"] == "approve"
        # None of the candidate paths should be the 1-hop direct Hamburg -> Berlin
        for path in final_result["candidate_paths"]:
            nodes = path["nodes"]
            assert nodes[0] == "Hamburg"
            assert nodes[-1] == "Berlin"
            assert nodes != ["Hamburg", "Berlin"]

    def test_max_hops_constraint_filters_longer_paths(
        self, mock_topology, checkpointer
    ):
        """Max-hops constraint excludes paths exceeding the hop limit in a single pass."""
        pddl_max_hops = (
            "(define (problem route-hannover-berlin-maxhops)\n"
            "  (:domain optical-network)\n"
            "  (:objects Hannover Berlin - node)\n"
            "  (:init (connected Hannover Berlin))\n"
            "  (:goal (and (route Hannover Berlin) (max-hops 1) (min-gsnr 10.0)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route Hannover to Berlin in at most 1 hop",
                source_node="Hannover",
                target_node="Berlin",
            ),
            pddl_handler=pddl_max_hops,
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-max-hops"}}

        initial_state = _make_initial_state(
            "Route Hannover to Berlin max 1 hop", mock_topology
        )

        # Single pass execution (0 interrupts)
        final_result = graph.invoke(initial_state, config=config)

        assert final_result["radg_decision"] == "approve"
        for path in final_result["candidate_paths"]:
            assert path["hops"] <= 1


# ---------------------------------------------------------------------------
# 5. Topology Edge Cases & Non-existent Endpoints
# ---------------------------------------------------------------------------


class TestTopologyEdgeCases:
    """Validate defensive behavior when endpoints are disconnected or missing."""

    def test_invalid_nodes_triggers_radg_replan_without_crash(
        self, mock_topology, checkpointer
    ):
        """When requested nodes do not exist, symbolic solver returns 0 paths and RADG suggests replan."""
        pddl_invalid_nodes = (
            "(define (problem route-atlantis-eldorado)\n"
            "  (:domain optical-network)\n"
            "  (:objects Atlantis ElDorado - node)\n"
            "  (:init)\n"
            "  (:goal (and (route Atlantis ElDorado)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route Atlantis to ElDorado",
                source_node="Atlantis",
                target_node="ElDorado",
            ),
            pddl_handler=pddl_invalid_nodes,
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-invalid-nodes"}}

        initial_state = _make_initial_state(
            "Route Atlantis to ElDorado", mock_topology
        )

        # 1. Passes semantic gate autonomously, solver fails to find nodes -> RADG replan interrupt
        graph.invoke(initial_state, config=config)

        radg_state = graph.get_state(config)
        assert radg_state.next == ("radg",)
        payload = radg_state.tasks[0].interrupts[0].value
        assert payload["decision"] == "replan"
        assert payload["qot_results"] == []


# ---------------------------------------------------------------------------
# 6. Interrupt Resumption Payload Resilience
# ---------------------------------------------------------------------------


class TestInterruptResumptionResilience:
    """Validate that interrupt handlers in hitl_clarify and radg handle various resume formats."""

    def test_hitl_clarify_handles_string_resume(
        self, mock_topology, checkpointer
    ):
        """hitl_clarify_node handles string command resume."""
        invalid_pddl = "(define (problem broken (:domain optical-network)"
        corrected_pddl = (
            "(define (problem route-stuttgart-munich)\n"
            "  (:domain optical-network)\n"
            "  (:objects Stuttgart Munich - node)\n"
            "  (:init (connected Stuttgart Munich))\n"
            "  (:goal (and (route Stuttgart Munich) (min-gsnr 10.0)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route Stuttgart to Munich",
                source_node="Stuttgart",
                target_node="Munich",
            ),
            pddl_handler=[invalid_pddl, corrected_pddl],
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-string-resume"}}

        initial_state = _make_initial_state(
            "Route Stuttgart to Munich", mock_topology
        )

        # First run pauses at hitl_clarify interrupt
        graph.invoke(initial_state, config=config)

        # Resume with plain string
        final_result = graph.invoke(Command(resume="Fixed PDDL"), config=config)
        assert final_result["radg_decision"] == "approve"


# ---------------------------------------------------------------------------
# 7. Checkpointer State Persistence Across Multi-Interruption Trajectories
# ---------------------------------------------------------------------------


class TestCheckpointerPersistence:
    """Validate that LangGraph StateGraph checkpointer retains complete state history."""

    def test_state_history_captured_across_interrupts(
        self, mock_topology, checkpointer
    ):
        """Ensure checkpointer tracks state snapshots through interruption cycles."""
        invalid_pddl = "(define (problem broken (:domain optical-network)"
        valid_pddl = (
            "(define (problem route-nuremberg-munich)\n"
            "  (:domain optical-network)\n"
            "  (:objects Nuremberg Munich - node)\n"
            "  (:init (connected Nuremberg Munich))\n"
            "  (:goal (and (route Nuremberg Munich) (min-gsnr 10.0)))\n"
            ")"
        )

        mock_llm = _create_mock_llm(
            intent_summary=IntentSummary(
                summary="Route Nuremberg to Munich",
                source_node="Nuremberg",
                target_node="Munich",
            ),
            pddl_handler=[invalid_pddl, valid_pddl],
            reconstruction_handler=None,
            agreement_score=0.05,
        )
        set_llm(mock_llm)

        graph = compile_graph(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "test-history-persistence"}}

        initial_state = _make_initial_state(
            "Route Nuremberg to Munich", mock_topology
        )

        # Step 1: run to hitl_clarify interrupt
        graph.invoke(initial_state, config=config)

        # Step 2: resume and complete
        graph.invoke(Command(resume={"action": "refine", "feedback": "Fix syntax"}), config=config)

        # Inspect history
        history = list(graph.get_state_history(config))
        assert len(history) >= 2
        # Final state has planning report
        latest_state = history[0]
        assert latest_state.values.get("planning_report") is not None
