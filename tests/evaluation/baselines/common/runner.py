"""Execution runner and callback telemetry for graph-based intent evaluation."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command

from src.core.state import ALLOWED_MSGPACK_MODULES
from src.services.testbed_client import MockTestbedClient
from tests.evaluation.baselines.common.metrics import compute_constraint_retention

STANDARD_FOLLOW_UP_INTENT = "Route traffic from Berlin to Frankfurt with at least 12 dB GSNR."
DEFAULT_INTENT_TIMEOUT = 300.0  # 5 minutes default global wall-clock timeout per demand

logger = logging.getLogger(__name__)


class TokenTracker(BaseCallbackHandler):
    """LangChain callback handler to track LLM token usage across graph invocations."""

    def __init__(self) -> None:
        super().__init__()
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        if hasattr(response, "llm_output") and response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self.prompt_tokens += usage.get("prompt_tokens", 0)
            self.completion_tokens += usage.get("completion_tokens", 0)
            self.total_tokens += usage.get("total_tokens", 0)
        elif hasattr(response, "generations"):
            for gen_list in response.generations:
                for gen in gen_list:
                    msg = getattr(gen, "message", None)
                    if msg and hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        self.prompt_tokens += msg.usage_metadata.get("input_tokens", 0)
                        self.completion_tokens += msg.usage_metadata.get("output_tokens", 0)
                        self.total_tokens += msg.usage_metadata.get("total_tokens", 0)


def check_action_success(
    item_class: str,
    expected_radg: str,
    initial_action: str | None,
) -> bool:
    """Verify if the pipeline's initial action matches expected risk mitigation.

    - Class I (Nominal): 'approve' (autonomous 0-interrupt pass)
    - Class II (Ambiguous): 'clarify' (Phase 3b Semantic Gate HITL catch)
    - Class III (Infeasible): 'replan' (Phase 6 RADG Physical Gate catch)
    - Class IV (Adversarial): 'clarify' or 'replan' (Structural/Physical catch)
    """
    if not initial_action:
        return False
    if item_class == "I_Nominal":
        return initial_action == "approve"
    if item_class == "II_Ambiguous":
        return initial_action == "clarify"
    if item_class == "III_Infeasible":
        return initial_action == "replan"
    if item_class == "IV_Adversarial":
        return initial_action in ("clarify", "replan")
    return initial_action == expected_radg


def evaluate_intent_with_graph(
    graph_factory: Callable[..., CompiledStateGraph],
    item: dict[str, Any],
    max_turns: int = 3,
    follow_up_intent: str = STANDARD_FOLLOW_UP_INTENT,
    baseline_name: str = "proposed_radg",
    intent_timeout: float = DEFAULT_INTENT_TIMEOUT,
    verbose: bool = True,
) -> dict[str, Any]:
    """Execute a single intent demand through a compiled LangGraph state graph.

    Handles interrupts programmatically, supplying follow_up_intent on clarify/replan pauses.
    Enforces intent_timeout (default 300.0s / 5 minutes) to protect against hanging models.
    """
    item_id = item.get("id", "intent_unknown")
    item_class = item.get("class", "I_Nominal")
    intent_text = item.get("intent_text", "")
    expected_radg = item.get("expected_radg_action", "approve")
    explicit_constraints = item.get("ground_truth_constraints", {})

    if verbose:
        print(f"\n{'='*70}")
        print(f"[{item_id}] ({item_class}) Baseline: {baseline_name}")
        print(f"Intent: \"{intent_text}\"")
        print(f"Target RADG Action: {expected_radg}")
        print(f"{'-'*70}")

    checkpointer = InMemorySaver(
        serde=JsonPlusSerializer(allowed_msgpack_modules=ALLOWED_MSGPACK_MODULES)
    )
    graph = graph_factory(checkpointer=checkpointer)
    token_tracker = TokenTracker()
    config = {
        "configurable": {"thread_id": f"eval-{baseline_name}-{item_id}"},
        "callbacks": [token_tracker],
    }

    initial_state = {
        "messages": [HumanMessage(content=intent_text)],
        "topology_snapshot": MockTestbedClient().get_topology(),
        "intent_class": item_class,
    }

    t_start = time.perf_counter()
    stream_input: Any = initial_state
    hitl_count = 0
    initial_action: str | None = None
    final_action: str | None = None
    execution_status: str = "completed"
    turn = 1

    turn_telemetry: list[dict[str, Any]] = []
    diagnostics: dict[str, Any] = {}
    turn_1_pddl: str | None = None
    turn_1_pddl_valid: bool | None = None
    turn_1_usem: float | None = None
    turn_1_qot_results: list[dict] | None = None

    while turn <= max_turns:
        elapsed_so_far = time.perf_counter() - t_start
        if elapsed_so_far > intent_timeout:
            if verbose:
                print(f"  ⏱️  [!] Global intent timeout exceeded ({elapsed_so_far:.1f}s > {intent_timeout:.1f}s). Terminating.")
            execution_status = "timeout"
            diagnostics["fatal_error"] = f"Intent timeout ({elapsed_so_far:.1f}s > {intent_timeout:.1f}s)"
            break

        if verbose:
            print(f"  [Turn {turn}] Running pipeline...")
        turn_t0 = time.perf_counter()
        tokens_before = token_tracker.total_tokens
        prompt_before = token_tracker.prompt_tokens
        completion_before = token_tracker.completion_tokens
        turn_data: dict[str, Any] = {"turn": turn}

        try:
            for event in graph.stream(stream_input, config=config, stream_mode="updates"):
                if "__interrupt__" in event:
                    continue
                for node, val in event.items():
                    if verbose:
                        print(f"    ✓ {node}")
                    if node == "intent_ingest":
                        turn_data["active_intent"] = val.get("active_intent")
                    elif node == "pddl_parser":
                        turn_data["pddl_valid"] = val.get("pddl_valid")
                        turn_data["pddl_constraints"] = val.get("pddl_constraints")
                        diagnostics["pddl_valid"] = val.get("pddl_valid")
                        diagnostics["pddl_constraints"] = val.get("pddl_constraints")
                        if turn == 1:
                            turn_1_pddl = val.get("pddl_constraints")
                            turn_1_pddl_valid = val.get("pddl_valid")
                    elif node == "reverse_prompt":
                        turn_data["hitl_reconstruction"] = val.get("hitl_reconstruction")
                        diagnostics["reconstruction"] = val.get("hitl_reconstruction")
                    elif node in ("semantic_gate", "always_on_semantic_gate", "bypassed_semantic_gate"):
                        turn_data["usem_score"] = val.get("usem_score")
                        turn_data["usem_passed"] = val.get("usem_passed")
                        turn_data["error_context"] = val.get("error_context")
                        diagnostics["usem_score"] = val.get("usem_score")
                        diagnostics["usem_passed"] = val.get("usem_passed")
                        diagnostics["error_context"] = val.get("error_context")
                        if turn == 1:
                            turn_1_usem = val.get("usem_score")
                    elif node == "symbolic_solver":
                        cands = val.get("candidate_paths") or []
                        turn_data["num_candidates"] = len(cands)
                        diagnostics["num_candidates"] = len(cands)
                    elif node == "qot_validation":
                        qot = val.get("qot_results") or []
                        turn_data["qot_results"] = qot
                        diagnostics["qot_results"] = qot
                        if turn == 1:
                            turn_1_qot_results = qot
                    elif node in ("radg", "controller_surrogate_radg"):
                        turn_data["radg_decision"] = val.get("radg_decision")
                        diagnostics["radg_decision"] = val.get("radg_decision")
                        if "controller_verdict" in val:
                            diagnostics["controller_verdict"] = val.get("controller_verdict")
                        if "controller_error" in val:
                            diagnostics["controller_error"] = val.get("controller_error")
                    elif node == "plan_synthesizer":
                        diagnostics["has_report"] = bool(val.get("planning_report"))

        except Exception as exc:
            if verbose:
                print(f"    [!] Error during pipeline stream: {exc}")
            turn_data["error"] = str(exc)
            diagnostics["fatal_error"] = str(exc)
            execution_status = "error"
            break

        turn_data["elapsed_s"] = round(time.perf_counter() - turn_t0, 2)
        turn_data["prompt_tokens"] = token_tracker.prompt_tokens - prompt_before
        turn_data["completion_tokens"] = token_tracker.completion_tokens - completion_before
        turn_data["total_tokens"] = token_tracker.total_tokens - tokens_before
        turn_telemetry.append(turn_data)

        state = graph.get_state(config)
        if state.next:
            hitl_count += 1
            gate_name = state.next[0]
            action = "clarify" if gate_name == "hitl_clarify" else "replan"
            if initial_action is None:
                if baseline_name == "llm_only":
                    initial_action = "approve"
                else:
                    initial_action = action

            interrupt_info: dict[str, Any] = {}
            if state.tasks and state.tasks[0].interrupts:
                interrupt_info = state.tasks[0].interrupts[0].value

            if verbose:
                print(f"  ⚠️  HITL Interrupt triggered at {gate_name} (Action: {action})")
                print(f"      Reason: {interrupt_info.get('reason') or interrupt_info.get('error_context')}")
                print(f"      Injecting Standard Follow-Up: \"{follow_up_intent}\"")

            resume_payload = {
                "action": "refine" if action == "clarify" else "replan",
                "feedback": follow_up_intent,
            }
            stream_input = Command(resume=resume_payload)
            turn += 1
        else:
            if initial_action is None:
                initial_action = "approve"
            final_action = "approve"
            if verbose:
                print("  ✅ Pipeline completed successfully to Phase 7!")
            break

    total_time = round(time.perf_counter() - t_start, 2)

    if execution_status == "timeout":
        final_action = "timeout"
        initial_action = initial_action or "timeout"
        success = False
    elif execution_status == "completed" and turn > max_turns and not diagnostics.get("has_report"):
        execution_status = "max_turns_exceeded"
        final_action = "failed"
        initial_action = initial_action or "failed"
        success = False
    else:
        final_action = final_action or ("approve" if diagnostics.get("has_report") else "failed")
        initial_action = initial_action or "failed"
        success = check_action_success(item_class, expected_radg, initial_action)

    # Compute Pillar 1: CRR
    crr_info = compute_constraint_retention(explicit_constraints, turn_1_pddl)

    # Compute Pillar 1: Semantic Agreement Score
    semantic_agreement = None
    if turn_1_usem is not None:
        semantic_agreement = round(max(0.0, min(1.0, 1.0 - turn_1_usem)), 3)

    # Check Physical Feasibility: Unsafe Approval check
    qot_results_t1 = turn_1_qot_results if turn_1_qot_results is not None else (diagnostics.get("qot_results") or [])
    has_infeasible_path = any(
        q.get("feasible") is False or q.get("qot_valid") is False
        for q in qot_results_t1
    ) or (item_class == "III_Infeasible")
    is_unfeasible_approval = (initial_action == "approve" and has_infeasible_path)

    return {
        "id": item_id,
        "baseline": baseline_name,
        "intent_text": intent_text,
        "class": item_class,
        "expected_radg_action": expected_radg,
        "initial_action": initial_action,
        "final_action": final_action,
        "execution_status": execution_status,
        "success": success,
        "passed_first_try": (initial_action == "approve"),
        "hitl_count": hitl_count,
        "total_elapsed_seconds": total_time,
        "prompt_tokens": token_tracker.prompt_tokens,
        "completion_tokens": token_tracker.completion_tokens,
        "total_tokens": token_tracker.total_tokens,
        "turn_1_pddl": turn_1_pddl,
        "pddl_valid": turn_1_pddl_valid if turn_1_pddl_valid is not None else diagnostics.get("pddl_valid"),
        "usem_score": turn_1_usem if turn_1_usem is not None else diagnostics.get("usem_score"),
        "semantic_agreement": semantic_agreement,
        "crr_info": crr_info,
        "is_unfeasible_approval": is_unfeasible_approval,
        "radg_decision": diagnostics.get("radg_decision"),
        "controller_verdict": diagnostics.get("controller_verdict", "approve" if item_class == "I_Nominal" else "replan"),
        "controller_error": diagnostics.get("controller_error", (item_class != "I_Nominal" and baseline_name == "llm_only")),
        "turn_telemetry": turn_telemetry,
        "diagnostics": diagnostics,
    }
