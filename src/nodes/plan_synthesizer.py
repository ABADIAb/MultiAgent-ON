"""Plan Synthesizer node for the V5 Neurosymbolic Intent Pipeline.

Exp 3.0: Generates the full auditable Planning Report including:
  - Intent & Alignment Specification (Initial intent, HITL refinements, and active operational intent)
  - Pre-deployment safety gate verification (U_sem score and RADG physical feasibility)
  - Selected lightpath topology (Horizontal ASCII graph with link distances and EDFA counts)
  - Candidate lightpath QoT feasibility matrix (real GN-model physics)
  - Deployment recommendation and provisioning readiness

This node is reached only when RADG decision is "approve", meaning
at least one candidate lightpath passed all physical-layer checks.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from src.core.state import AgentState


def _extract_clean_base_intent(state: AgentState) -> str:
    """Extract a clean operator intent string without prefixes or topology dumps."""
    messages = state.get("messages") or []
    for msg in messages:
        if isinstance(msg, HumanMessage) and msg.content:
            content = str(msg.content).strip()
            if content:
                return content
        elif isinstance(msg, dict) and msg.get("role") == "user" and msg.get("content"):
            content = str(msg["content"]).strip()
            if content:
                return content

    raw = state.get("enriched_intent") or ""
    if raw:
        # Strip subtopology context text completely
        clean = raw.split("\nTopology Context:")[0].strip()
        clean = clean.split("Topology Context:")[0].strip()
        # Remove redundant leading "Intent: " or "Intent :"
        if clean.lower().startswith("intent:"):
            clean = clean[len("intent:") :].strip()
        elif clean.lower().startswith("intent :"):
            clean = clean[len("intent :") :].strip()
        if clean:
            return clean

    return "N/A"


def _format_horizontal_path(
    nodes: list[str],
    link_physics: list[dict[str, Any]] | None = None,
) -> tuple[str, str]:
    """Render horizontal ASCII/Unicode lightpath graph with distances and EDFA counts.

    Returns:
        tuple of (graph_ascii, summary_metrics)
    """
    if not nodes:
        return "No path available", "0 Spans • 0.0 km • 0 EDFAs"

    if len(nodes) == 1:
        return f"[ {nodes[0]} ]", "0 Spans (Local) • 0.0 km • 0 EDFAs"

    segments = []
    total_dist = 0.0
    total_edfas = 0

    has_physics = bool(link_physics and len(link_physics) == len(nodes) - 1)

    for i in range(len(nodes) - 1):
        u = nodes[i]
        if has_physics and link_physics:
            phy = link_physics[i]
            dist = float(phy.get("length_km", 0.0))
            amps = len(phy.get("amplifiers") or [])
            total_dist += dist
            total_edfas += amps
            amp_str = f"{amps} EDFA" if amps == 1 else f"{amps} EDFAs"
            edge_label = f"────( {dist:.1f} km | {amp_str} )────►"
        else:
            edge_label = "────►"
        segments.append(f"[ {u} ] {edge_label}")

    segments.append(f"[ {nodes[-1]} ]")
    graph_ascii = " ".join(segments)

    hops = len(nodes) - 1
    if has_physics:
        metrics = (
            f"{hops} Spans ({'Hop' if hops == 1 else 'Hops'}) • "
            f"{total_dist:.1f} km Total Fiber • "
            f"{total_edfas} Inline EDFAs (C-Band Coherent 96-ch)"
        )
    else:
        metrics = f"{hops} Spans ({'Hop' if hops == 1 else 'Hops'})"

    return graph_ascii, metrics


def _find_candidate_physics(
    candidate_paths: list[dict[str, Any]] | None,
    route_nodes: list[str],
) -> list[dict[str, Any]] | None:
    """Locate candidate path dict matching the selected route nodes."""
    if not candidate_paths:
        return None
    for cand in candidate_paths:
        if cand.get("nodes") == route_nodes:
            return cand.get("link_physics")
    if len(candidate_paths) == 1 and candidate_paths[0].get("link_physics"):
        return candidate_paths[0].get("link_physics")
    return None


def plan_synthesizer_node(state: AgentState) -> dict:
    """Synthesize the final auditable Planning Report.

    Produces an executive-grade, pre-deployment decision record:
    1. Intent & Alignment Trace (Original intent, HITL feedback, Active intent)
    2. Pre-Deployment Safety Verification (Semantic Gate U_sem + Physical RADG)
    3. Selected Optical Lightpath Topology (Horizontal ASCII path + Spans/EDFAs)
    4. Evaluated Candidate Routes & QoT Physics (Feasibility matrix)
    5. Provisioning Recommendation & Testbed Action

    Args:
        state: Full AgentState after RADG approval.

    Returns:
        Partial state update with planning_report and message.
    """
    qot_results = state.get("qot_results") or []
    feasible_paths = [r for r in qot_results if r.get("feasible")]
    all_paths = qot_results

    base_intent = _extract_clean_base_intent(state)
    refinement_history = state.get("refinement_history") or []
    refinement_count = state.get("refinement_count") or len(refinement_history)

    # 1. Refinement & Intent status
    if refinement_history:
        refinement_status = f"Refined via Operator HITL ({refinement_count} iteration{'s' if refinement_count != 1 else ''})"
        refinements_list = "\n".join(f"  - Turn {idx}: \"{fb}\"" for idx, fb in enumerate(refinement_history, 1))
        active_intent = f"{base_intent} (Updated with operator refinements: {'; '.join(refinement_history)})"
        refinement_block = (
            f"- **Refinement Status:** {refinement_status}\n"
            f"- **Applied HITL Refinements:**\n{refinements_list}\n"
            f"- **Active Operational Intent:** {active_intent}"
        )
    else:
        refinement_status = "Autonomous Pass (0 Interrupts)"
        active_intent = base_intent
        refinement_block = (
            f"- **Refinement Status:** {refinement_status}\n"
            f"- **Active Operational Intent:** {active_intent}"
        )

    if not feasible_paths:
        report = (
            "# 📋 Optical Network Planning Report\n"
            "**MultiAgent-ON Neurosymbolic Orchestrator (V5)** • *SDON Pre-Deployment Decision Record*\n\n"
            "---\n\n"
            "### 1. Intent & Alignment Specification\n"
            f"- **Initial Intent:** {base_intent}\n"
            f"{refinement_block}\n\n"
            "### Status: No feasible paths found.\n"
            "The operator's intent cannot be satisfied with the current physical constraints.\n"
            "Recommendation: Relax the GSNR threshold or adjust the route request."
        )
    else:
        # Best path selection: highest GSNR among feasible candidates
        best_path = max(feasible_paths, key=lambda r: r.get("snr_dB", 0.0))
        best_route_nodes = best_path.get("path", ["unknown"])
        best_route = " → ".join(best_route_nodes)

        # 2. Safety Gates evaluation line
        usem = state.get("usem_score")
        usem_passed = state.get("usem_passed")
        radg_decision = (state.get("radg_decision") or "N/A").upper()

        usem_metric = f"U_sem={usem:.3f}" if usem is not None else "U_sem=N/A"
        usem_status = "PASS" if usem_passed else ("FAIL" if usem is not None else "N/A")
        usem_action = "Semantic alignment confirmed (Auto-Pass)" if usem_passed else "Operator disambiguation"

        radg_status = "PASS" if radg_decision == "APPROVE" else "REPLAN"
        radg_action = "Auto-Approved (Coherent physics verified)" if radg_decision == "APPROVE" else "Constraint replan required"

        # 3. Horizontal Lightpath Graph
        candidate_paths = state.get("candidate_paths") or []
        link_physics = _find_candidate_physics(candidate_paths, best_route_nodes)
        graph_ascii, path_metrics = _format_horizontal_path(best_route_nodes, link_physics)

        # Hop-by-hop span breakdown
        span_breakdown_lines = []
        if link_physics and len(link_physics) == len(best_route_nodes) - 1:
            for i in range(len(best_route_nodes) - 1):
                u = best_route_nodes[i]
                v = best_route_nodes[i + 1]
                phy = link_physics[i]
                dist = float(phy.get("length_km", 0.0))
                amps = len(phy.get("amplifiers") or [])
                amp_lbl = f"{amps} EDFA" if amps == 1 else f"{amps} EDFAs"
                span_breakdown_lines.append(f"  - Hop {i + 1}: `{u} ➔ {v}` ({dist:.1f} km, {amp_lbl})")
        span_breakdown_str = (
            "\n- **Optical Link Spans:**\n" + "\n".join(span_breakdown_lines)
            if span_breakdown_lines
            else ""
        )

        # 4. QoT candidate table
        table_rows = []
        for idx, result in enumerate(all_paths, 1):
            route_str = " → ".join(result.get("path", ["unknown"]))
            snr = result.get("snr_dB", 0.0)
            pwr = result.get("power_dBm", 0.0)
            thresh = result.get("snr_threshold_dB", 0.0)
            margin = snr - thresh
            feasible = result.get("feasible", False)
            verdict = "✓ FEASIBLE" if feasible else "✗ INFEASIBLE"
            err = result.get("error")
            err_suffix = f" *(Error: {err})*" if err else ""

            table_rows.append(
                f"| {idx} | `{route_str}` | {snr:.2f} dB | {thresh:.1f} dB | {margin:+.2f} dB | {pwr:.2f} dBm | **{verdict}**{err_suffix} |"
            )

        qot_table_str = (
            "| # | Candidate Route | GSNR | Thresh | Margin | P_rx | Status |\n"
            "| :-: | :--- | -: | -: | -: | -: | :-: |\n"
            + "\n".join(table_rows)
        )

        # 5. Full Markdown Report Assembly
        report = (
            "# 📋 Optical Network Planning Report\n"
            "**MultiAgent-ON Neurosymbolic Orchestrator (V5)** • *SDON Pre-Deployment Decision Record*\n\n"
            "---\n\n"
            "### 1. Intent & Alignment Specification\n"
            f"- **Initial Intent:** {base_intent}\n"
            f"{refinement_block}\n\n"
            "### 2. Pre-Deployment Safety Verification\n"
            "| Gate | Evaluated Signal | Constraint | Status | Action |\n"
            "| :--- | :--- | :--- | :---: | :--- |\n"
            f"| **Semantic Gate (Phase 3)** | {usem_metric} | $\\tau_{{sem}} \\le 0.300$ | `{usem_status}` | {usem_action} |\n"
            f"| **Physical Risk Gate (Phase 6)** | RADG = {radg_decision} | Feasible Paths $\\ge 1$ | `{radg_status}` | {radg_action} |\n\n"
            "### 3. Selected Optical Lightpath Topology\n"
            "```text\n"
            f"{graph_ascii}\n"
            "```\n"
            f"- **Cumulative Metrics:** {path_metrics}"
            f"{span_breakdown_str}\n\n"
            "### 4. Evaluated Candidate Routes (Physical-Layer Feasibility)\n"
            f"{qot_table_str}\n\n"
            "### 5. Deployment Recommendation & Testbed Status\n"
            f"- **RECOMMENDED PATH: {best_route}**\n"
            f"- **Physical Layer Parameters:** Computed GSNR = {best_path.get('snr_dB', 0.0):.2f} dB | $P_{{rx}}$ = {best_path.get('power_dBm', 0.0):.2f} dBm\n"
            "- **Safety Guarantee:** Coherent GN-model verified. Zero physical violations allowed to reach network controller.\n"
            "- **Provisioning Action:** `READY_FOR_PROVISIONING` via SDON Testbed Adapter (100G DP-QPSK C-Band).\n"
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

