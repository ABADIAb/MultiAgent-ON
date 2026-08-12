"""Plan Synthesizer node for the V5 Neurosymbolic Intent Pipeline.

Exp 3.0: Generates the full auditable Planning Report including:
  - Semantic Gate trace (U_sem score, structural/semantic validation)
  - PDDL constraint map
  - QoT results per candidate path (real GN-model physics)
  - RADG decision outcome
  - Recommended path selection

This node is reached only when RADG decision is "approve", meaning
at least one candidate path passed all physical-layer checks.
"""

from __future__ import annotations

from langchain_core.messages import AIMessage

from src.core.state import AgentState


def plan_synthesizer_node(state: AgentState) -> dict:
    """Synthesize the final auditable Planning Report.

    Produces a complete trace of the V5 pipeline execution:
    Semantic Gate → PDDL → Solver → QoT → RADG → Recommendation.

    Args:
        state: Full AgentState after the RADG has approved.

    Returns:
        Partial state update with planning_report.
    """
    qot_results = state.get("qot_results") or []
    feasible_paths = [r for r in qot_results if r.get("feasible")]
    all_paths = qot_results

    if not feasible_paths:
        report = (
            "Planning Report\n"
            "===============\n"
            "Status: No feasible paths found.\n"
            "The operator's intent cannot be satisfied with the current constraints.\n"
            "Recommendation: Relax the GSNR threshold or adjust the route request."
        )
    else:
        # Select the best path: highest GSNR among feasible ones
        best_path = max(feasible_paths, key=lambda r: r.get("snr_dB", 0.0))
        best_route = " → ".join(best_path.get("path", ["unknown"]))

        # --- Semantic Gate section ---
        usem = state.get("usem_score")
        usem_passed = state.get("usem_passed")
        usem_line = (
            f"U_sem={usem:.3f} ({'PASS' if usem_passed else 'FAIL'})"
            if usem is not None
            else "U_sem=N/A"
        )

        # --- QoT results table ---
        path_lines = []
        for i, result in enumerate(all_paths, 1):
            path = " → ".join(result.get("path", ["unknown"]))
            snr = result.get("snr_dB", 0.0)
            pwr = result.get("power_dBm", 0.0)
            thresh = result.get("snr_threshold_dB", 0.0)
            verdict = "✓ FEASIBLE" if result.get("feasible") else "✗ INFEASIBLE"
            err = result.get("error")
            err_note = f" [Error: {err}]" if err else ""
            path_lines.append(
                f"  [{i}] {verdict}  {path}\n"
                f"       SNR={snr:.2f} dB (thresh≥{thresh:.1f}), P_rx={pwr:.2f} dBm{err_note}"
            )

        report = (
            "Planning Report\n"
            "===============\n"
            f"Intent      : {state.get('enriched_intent', 'N/A')}\n"
            f"Semantic Gate: {usem_line}\n"
            f"RADG Decision: {(state.get('radg_decision') or 'N/A').upper()}\n"
            "\n"
            "Candidate Path QoT Results:\n"
            + "\n".join(path_lines)
            + "\n\n"
            f"RECOMMENDED PATH: {best_route}\n"
            f"  → SNR: {best_path.get('snr_dB', 0.0):.2f} dB  |  "
            f"P_rx: {best_path.get('power_dBm', 0.0):.2f} dBm\n"
            f"  → Feasible at 100G (GN-model validated, mocked topology)\n"
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
