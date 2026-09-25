"""Test verifying the full LLM-Only 3-turn graph loop."""

import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from tests.evaluation.baselines.llm_only.graph import compile_llm_only_graph


def test_llm_only_graph_turn_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock LLM calls so it runs deterministically
    call_count = {"pddl": 0, "reconcile": 0}

    monkeypatch.setattr(
        "tests.evaluation.baselines.llm_only.graph.intent_ingest_node",
        lambda state: {"enriched_intent": "Route traffic from Berlin to Frankfurt", "messages": []},
    )

    monkeypatch.setattr(
        "tests.evaluation.baselines.llm_only.graph.semantic_gate_node",
        lambda state: {"usem_score": 0.1, "usem_passed": True, "error_context": None, "messages": []},
    )

    def mock_pddl_node(state):
        call_count["pddl"] += 1
        ref_count = state.get("refinement_count") or 0
        if ref_count >= 2:
            pddl = "(problem opt (:domain optical-network) (:objects Berlin Frankfurt - node) (:init (connected Berlin Frankfurt)) (:goal (and (route Berlin Frankfurt) (min-gsnr 12))))"
        else:
            pddl = "(problem opt (:domain optical-network) (:objects Berlin Frankfurt - node) (:init (connected Berlin Frankfurt)) (:goal (and (route Berlin Frankfurt) (min-gsnr 35))))"
        return {
            "pddl_constraints": pddl,
            "pddl_valid": True,
            "active_intent": "Route traffic",
            "messages": [AIMessage(content="Generated PDDL", name="pddl_parser")],
        }

    monkeypatch.setattr("tests.evaluation.baselines.llm_only.graph.pddl_parser_node", mock_pddl_node)

    # Mock reverse prompt
    monkeypatch.setattr(
        "tests.evaluation.baselines.llm_only.graph.reverse_prompt_node",
        lambda state: {"hitl_reconstruction": "Reconstructed intent", "messages": []},
    )

    # Mock symbolic solver
    monkeypatch.setattr(
        "tests.evaluation.baselines.llm_only.graph.symbolic_solver_node",
        lambda state: {"candidate_paths": [{"nodes": ["Berlin", "Frankfurt"], "length_km": 500}], "messages": []},
    )

    # Mock QoT validation: fails on Turn 1 & 2, succeeds on Turn 3
    def mock_qot_node(state):
        ref_count = state.get("refinement_count") or 0
        feasible = (ref_count >= 2)
        snr = 16.5 if feasible else 8.0
        return {
            "qot_results": [{"path": ["Berlin", "Frankfurt"], "feasible": feasible, "snr_dB": snr, "power_dBm": -12.0}],
            "messages": [],
        }

    monkeypatch.setattr("tests.evaluation.baselines.llm_only.graph.qot_validation_node", mock_qot_node)

    checkpointer = InMemorySaver()
    graph = compile_llm_only_graph(checkpointer=checkpointer)
    config = {"configurable": {"thread_id": "test-llm-only-trace"}, "recursion_limit": 50}

    initial_state = {
        "messages": [HumanMessage(content="Route traffic with 35 dB GSNR")],
        "intent_class": "III_Infeasible",
    }

    # Pass 1 & Pass 2 happen in the first stream call!
    events_1 = list(graph.stream(initial_state, config=config, stream_mode="updates"))
    state_after_stream_1 = graph.get_state(config)

    # Should pause at radg interrupt (Turn 2 failed blind retry)
    assert state_after_stream_1.next == ("radg",)
    assert call_count["pddl"] == 2  # Visited pddl_parser twice! (Turn 1 initial + Turn 2 blind retry)

    # Inspect messages: Turn 1 injected raw RESTConf error
    all_msgs = state_after_stream_1.values.get("messages", [])
    controller_msgs = [m for m in all_msgs if getattr(m, "name", "") == "controller"]
    assert len(controller_msgs) >= 1
    assert "RFC 8040 RESTCONF" in controller_msgs[0].content

    # Now simulate human incident response in Turn 3
    resume_payload = {
        "action": "replan",
        "feedback": "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR.",
    }
    events_2 = list(graph.stream(Command(resume=resume_payload), config=config, stream_mode="updates"))
    state_after_stream_2 = graph.get_state(config)

    # Turn 3 completes to END!
    assert state_after_stream_2.next == ()
    assert call_count["pddl"] == 3  # Visited pddl_parser for Turn 3!
    assert state_after_stream_2.values.get("radg_decision") == "approve"
    assert state_after_stream_2.values.get("controller_error") is False
    print("ALL ASSERTIONS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
