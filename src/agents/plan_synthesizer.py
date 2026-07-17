"""Plan Synthesizer node for the Neurosymbolic Intent Pipeline.

Sprint 3 will implement:
- Full Planning Report generation with PDDL trace
- Reverse Prompting conversation history
- Testbed provisioning command generation

Current: Pass-through placeholder that generates a summary report.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from src.core.state import AgentState


def plan_synthesizer_node(state: AgentState) -> dict:
    """Synthesize the final Planning Report.

    Placeholder: generates a simple text summary of the pipeline results.
    Sprint 3 will produce a full auditable Planning Report.

    Returns:
        Partial state update with planning_report.
    """
    qot_results = state.get("qot_results") or []
    feasible_paths = [r for r in qot_results if r.get("feasible")]

    if not feasible_paths:
        report = "No feasible paths found. The operator's intent cannot be satisfied."
    else:
        path_summaries = []
        for i, result in enumerate(feasible_paths, 1):
            path = " → ".join(result.get("path", ["unknown"]))
            snr = result.get("snr_dB", 0)
            power = result.get("power_dBm", 0)
            path_summaries.append(
                f"  Path {i}: {path} (SNR: {snr:.1f} dB, Power: {power:.1f} dBm)"
            )

        report = (
            f"Planning Report (Placeholder)\n"
            f"{'=' * 40}\n"
            f"Intent: {state.get('enriched_intent', 'N/A')}\n"
            f"PDDL: {state.get('pddl_constraints', 'N/A')}\n"
            f"HITL Approved: {state.get('hitl_approved', False)}\n"
            f"Feasible Paths ({len(feasible_paths)}):\n"
            + "\n".join(path_summaries)
        )

    return {
        "planning_report": report,
        "messages": [
            AIMessage(
                content=report,
                name="plan_synthesizer",
            )
        ],
    }
