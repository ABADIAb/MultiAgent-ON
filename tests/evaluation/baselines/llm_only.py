"""Baseline A: Monolithic LLM (LLM-Only).

Architecture: Direct Prompting.
Unconstrained single-call LLM execution without LangGraph, PDDL, symbolic solvers,
or deterministic GN-model physics tools. The entire topology and intent are injected
into a single prompt, asking the LLM to output routing, GSNR estimate, and approval.

Used to evaluate:
  - Hallucinated physics & topological path errors
  - Context window token consumption without Mock GraphRAG
  - Unsafe Approval Rate (UAR)
"""

from __future__ import annotations

import json
import re
import time
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from src.core.llm import get_llm
from tests.evaluation.baselines.base import (
    BaseBaseline,
    BaselineResult,
    register_baseline,
)


class LLMOnlyOutput(BaseModel):
    """Structured response expected from the monolithic LLM."""

    source_node: str = Field(default="", description="Extracted source node")
    destination_node: str = Field(default="", description="Extracted destination node")
    route: list[str] = Field(
        default_factory=list, description="Computed optical route node names"
    )
    estimated_gsnr_dB: float = Field(default=0.0, description="Estimated GSNR in dB")
    action: str = Field(
        default="approve",
        description="Decision: 'approve', 'clarify', or 'replan'",
    )
    reasoning: str = Field(default="", description="Explanation of planning decision")


@register_baseline
class LLMOnlyBaseline(BaseBaseline):
    """Baseline A: Monolithic LLM (Direct NL -> JSON Route without tools)."""

    name = "Baseline A (Monolithic LLM)"
    baseline_id = "llm_only"

    def _build_topology_description(self) -> str:
        """Serialize the entire 17-node Nobel-Germany topology into textual prompt format."""
        nodes = [n.name for n in self.topology_snapshot.nodes]
        links = []
        for link_obj in self.topology_snapshot.links:
            links.append(
                f"{link_obj.source_node} <-> {link_obj.target_node} (length: {link_obj.length_km:.1f} km, amplifiers: {len(link_obj.amplifiers)})"
            )
        return (
            f"Nodes ({len(nodes)}): {', '.join(nodes)}\n\nFiber Links ({len(links)}):\n"
            + "\n".join(links)
        )

    def run(self, intent_data: dict[str, Any], **kwargs: Any) -> BaselineResult:
        start_time = time.perf_counter()
        intent_text = intent_data.get("intent_text", "")
        intent_id = intent_data.get("id", "unknown")
        gt_constraints = intent_data.get("ground_truth_constraints", {})
        min_gsnr = float(gt_constraints.get("min_gsnr", 15.0))

        full_topo_str = self._build_topology_description()

        system_prompt = (
            "You are an autonomous optical network controller. You are provided with the full network "
            "topology below. Your task is to analyze the operator's natural language intent, select an "
            "optical route from source to destination, estimate physical GSNR using optical physics principles, "
            "and output your planning decision as JSON with keys: "
            "'source_node', 'destination_node', 'route' (list of strings), 'estimated_gsnr_dB' (float), "
            "'action' ('approve', 'clarify', or 'replan'), and 'reasoning'."
        )

        user_prompt = (
            f"NETWORK TOPOLOGY:\n{full_topo_str}\n\n"
            f'OPERATOR INTENT:\n"{intent_text}"\n\n'
            "Respond ONLY with valid JSON conforming to the requested schema."
        )

        prompt_tokens = self.count_tokens(system_prompt) + self.count_tokens(
            user_prompt
        )
        completion_tokens = 0
        error_msg: str | None = None
        selected_path: list[str] | None = None
        action = "approve"

        llm = get_llm()
        if llm is None:
            return {
                "intent_id": intent_id,
                "baseline_id": self.baseline_id,
                "action": "replan",
                "selected_path": None,
                "computed_gsnr_dB": None,
                "qot_feasible": False,
                "pddl_valid": False,
                "parsed_constraints": None,
                "hitl_interrupts": 0,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": 0,
                "total_tokens": prompt_tokens,
                "execution_time_s": time.perf_counter() - start_time,
                "planning_report": None,
                "error": "LLM singleton is not configured.",
                "metadata": {},
            }

        try:
            # Try structured output first if supported
            structured_llm = llm.with_structured_output(LLMOnlyOutput)
            result: LLMOnlyOutput = structured_llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            selected_path = result.route
            action = result.action.lower() if result.action else "approve"
            completion_tokens = self.count_tokens(json.dumps(result.model_dump()))
        except Exception:
            # Fallback to standard invoke and regex JSON extraction
            raw_response = llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            raw_text = getattr(raw_response, "content", "")
            completion_tokens = self.count_tokens(raw_text)
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                    selected_path = data.get("route") or []
                    action = str(data.get("action", "approve")).lower()
                except Exception as ex:
                    error_msg = f"JSON parse error: {ex}"
                    action = "replan"
            else:
                error_msg = "No JSON object found in response"
                action = "replan"

        # Normalize action to strictly ternary
        if action not in ("approve", "clarify", "replan"):
            action = "approve"

        # Evaluate actual physical QoT of whatever path the LLM proposed
        actual_gsnr: float | None = None
        qot_feasible = False
        if selected_path and len(selected_path) >= 2:
            try:
                actual_gsnr, qot_feasible = self.verify_optical_path(
                    selected_path, min_gsnr
                )
            except Exception as ex:
                qot_feasible = False
                error_msg = f"Path verification failed (e.g. disconnected hops): {ex}"

        exec_time = time.perf_counter() - start_time

        return {
            "intent_id": intent_id,
            "baseline_id": self.baseline_id,
            "action": action,  # type: ignore
            "selected_path": selected_path,
            "computed_gsnr_dB": actual_gsnr,
            "qot_feasible": qot_feasible,
            "pddl_valid": None,  # No PDDL used in Baseline A
            "parsed_constraints": None,
            "hitl_interrupts": 0,  # Unconstrained autonomous
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "execution_time_s": exec_time,
            "planning_report": f"LLM-Only Route: {selected_path} | Action: {action}",
            "error": error_msg,
            "metadata": {"min_gsnr_threshold": min_gsnr},
        }
