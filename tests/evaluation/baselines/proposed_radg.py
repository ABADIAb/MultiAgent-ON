"""Proposed Architecture Wrapper: Neurosymbolic RADG.

Wraps the production V5 LangGraph pipeline (compile_graph) with an automated
evaluation harness capable of handling LangGraph interrupt() checkpoints
programmatically during batch benchmark runs.

Tracks:
  - Selective HITL interruptions (0 on Class I Nominal, targeted on Class II/III)
  - Scoped Optical GraphRAG prompt token savings (>90% reduction)
  - Exact dual-gate fail-fast decision trajectory (U_sem and QoT_valid)
"""

from __future__ import annotations

import time
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.types import Command

from src.core.graph import compile_graph
from src.core.state import ALLOWED_MSGPACK_MODULES
from tests.evaluation.baselines.base import (
    STANDARD_FOLLOW_UP_INTENT,
    BaseBaseline,
    BaselineResult,
    register_baseline,
)


@register_baseline
class ProposedRADGBaseline(BaseBaseline):
    """Proposed Architecture: Neurosymbolic Intent Planning with Risk-Adaptive Decision Gate (RADG)."""

    name = "Proposed (Neurosymbolic RADG)"
    baseline_id = "proposed_radg"

    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        start_time = time.perf_counter()
        intent_id = intent_data.get("id", "unknown")
        intent_text = intent_data.get("intent_text", "")

        checkpointer = InMemorySaver(
            serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
        )
        graph = compile_graph(checkpointer=checkpointer)
        config = {
            "configurable": {
                "thread_id": f"benchmark-{intent_id}-{int(time.time() * 1000)}"
            }
        }

        initial_state: dict[str, Any] = {
            "messages": [HumanMessage(content=intent_text)],
            "topology_snapshot": self.topology_snapshot,
            "active_intent": intent_text,
            "enriched_intent": None,
            "pddl_constraints": None,
            "pddl_valid": None,
            "pddl_parsed_constraints": None,
            "hitl_reconstruction": None,
            "hitl_approved": None,
            "candidate_paths": None,
            "qot_results": None,
            "planning_report": None,
            "error_context": None,
            "usem_score": None,
            "usem_passed": None,
            "radg_decision": None,
            "topology_context": None,
            "subtopology_snapshot": None,
            "refinement_history": None,
            "refinement_count": 0,
        }

        hitl_interrupts = 0
        initial_action: str | None = None
        stream_input: Any = initial_state
        max_turns = 4
        turn = 0
        final_values: dict[str, Any] = {}

        while turn < max_turns:
            turn += 1
            # Execute until completion or interrupt
            for _ in graph.stream(
                stream_input, config=config, stream_mode="updates"
            ):
                pass

            state = graph.get_state(config)
            final_values = state.values

            # Check if graph reached an interrupt
            if state.next:
                hitl_interrupts += 1
                interrupt_val: dict[str, Any] = {}
                if state.tasks:
                    for task in state.tasks:
                        if hasattr(task, "interrupts") and task.interrupts:
                            interrupt_val = task.interrupts[0].value
                            break

                decision_type = interrupt_val.get("decision", "")

                # Record the initial gate action on the first interruption
                if initial_action is None:
                    if (
                        "usem_score" in interrupt_val
                        or decision_type == "clarify"
                        or interrupt_val.get("status") == "clarification_required"
                    ):
                        initial_action = "clarify"
                    elif decision_type == "replan":
                        initial_action = "replan"
                    else:
                        initial_action = "clarify"

                # Automated recovery follow-up response for E2E benchmarking:
                # Provide a clean, nominal intent so execution continues to synthesis
                if "usem_score" in interrupt_val or decision_type == "clarify" or interrupt_val.get("status") == "clarification_required":
                    stream_input = Command(
                        resume={
                            "action": "refine",
                            "feedback": STANDARD_FOLLOW_UP_INTENT,
                        }
                    )
                    continue
                elif decision_type == "replan":
                    stream_input = Command(
                        resume={
                            "action": "replan",
                            "feedback": STANDARD_FOLLOW_UP_INTENT,
                        }
                    )
                    continue
                else:
                    stream_input = Command(
                        resume={
                            "action": "refine",
                            "feedback": STANDARD_FOLLOW_UP_INTENT,
                        }
                    )
                    continue
            else:
                # Execution reached terminal state without interrupts
                if initial_action is None:
                    radg_dec = final_values.get("radg_decision")
                    initial_action = "approve" if radg_dec == "approve" else (radg_dec or "approve")
                break

        # If loop exited while still in interrupt state (exceeded max_turns)
        if initial_action is None:
            initial_action = "clarify"

        pddl_valid = final_values.get("pddl_valid")
        radg_decision = final_values.get("radg_decision")
        qot_results = final_values.get("qot_results") or []
        planning_report = final_values.get("planning_report")

        selected_path: list[str] | None = None
        computed_gsnr: float | None = None
        qot_feasible = False

        feasible_paths = [p for p in qot_results if p.get("feasible")]
        if feasible_paths:
            selected_path = feasible_paths[0].get("path")
            computed_gsnr = feasible_paths[0].get("snr_dB")
            qot_feasible = True
        elif qot_results:
            selected_path = qot_results[0].get("path")
            computed_gsnr = qot_results[0].get("snr_dB")
            qot_feasible = False

        # Cumulative token counting across all messages and state artifacts
        messages = final_values.get("messages", [])
        prompt_tokens = 0
        completion_tokens = 0

        for msg in messages:
            content = getattr(msg, "content", "")
            if isinstance(content, str):
                if getattr(msg, "type", "") == "human" or getattr(msg, "name", "") == "human":
                    prompt_tokens += self.count_tokens(content)
                else:
                    completion_tokens += self.count_tokens(content)

        topo_context = final_values.get("topology_context", "")
        if topo_context:
            prompt_tokens += self.count_tokens(topo_context)

        pddl_str = final_values.get("pddl_constraints", "")
        if pddl_str:
            completion_tokens += self.count_tokens(pddl_str)

        if planning_report:
            completion_tokens += self.count_tokens(planning_report)

        exec_time = time.perf_counter() - start_time
        final_action = "approve" if (not state.next and radg_decision == "approve") else initial_action

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": initial_action,  # type: ignore
            "initial_action": initial_action,  # type: ignore
            "final_action": final_action,  # type: ignore
            "selected_path": selected_path,
            "computed_gsnr_dB": computed_gsnr,
            "qot_feasible": qot_feasible,
            "pddl_valid": pddl_valid,
            "parsed_constraints": final_values.get("pddl_parsed_constraints"),
            "hitl_interrupts": hitl_interrupts,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "execution_time_s": exec_time,
            "planning_report": planning_report,
            "error": final_values.get("error_context"),
            "metadata": {
                "usem_score": final_values.get("usem_score"),
                "usem_passed": final_values.get("usem_passed"),
                "radg_decision": radg_decision,
                "initial_action": initial_action,
                "final_action": final_action,
                "turns": turn,
            },
        }
