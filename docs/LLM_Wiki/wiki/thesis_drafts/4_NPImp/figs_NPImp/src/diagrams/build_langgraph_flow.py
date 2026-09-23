#!/usr/bin/env python3
"""
Generates the native Draw.io XML for Figure 4.1: langgraph_execution_flow.drawio.
Adheres strictly to thesis-coauthor figure guidelines:
- Generous typography (titles: 15-16 pt bold, subtitles: 12.5-13.5 pt, gates: 14 pt bold, edges: 12.5 pt)
- Academic color palette (neural, symbolic, gates, HITL, replan, checkpointer)
- Strict XML escaping and well-formed XML AST validation.
- Zero edge/label collisions with clean non-overlapping orthogonal routing.
"""

import xml.etree.ElementTree as ET
from pathlib import Path


def generate_drawio_xml() -> str:
    xml = [
        '<mxfile host="Electron" agent="5.0">',
        '  <diagram id="fig_langgraph_execution_flow" name="LangGraph State Machine Execution Flow">',
        '    <mxGraphModel dx="1400" dy="1000" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="960" pageHeight="1060" math="1" shadow="0">',
        '      <root>',
        '        <mxCell id="0" />',
        '        <mxCell id="1" parent="0" />',
    ]

    def add_cell(cell_id, parent_id, value, style, x, y, w, h, is_edge=False, source=None, target=None, points=None):
        if is_edge:
            pts_xml = ""
            if points:
                pts_str = "".join([f'<mxPoint x="{px}" y="{py}" />' for px, py in points])
                pts_xml = f'<Array as="points">{pts_str}</Array>'
            xml.append(
                f'        <mxCell id="{cell_id}" parent="{parent_id}" value="{value}" style="{style}" edge="1" source="{source}" target="{target}">'
            )
            xml.append(f'          <mxGeometry relative="1" as="geometry">{pts_xml}</mxGeometry>')
            xml.append('        </mxCell>')
        else:
            xml.append(
                f'        <mxCell id="{cell_id}" parent="{parent_id}" value="{value}" style="{style}" vertex="1">'
            )
            xml.append(f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry" />')
            xml.append('        </mxCell>')

    # 1. State Persistence Container (Checkpointer)
    checkpointer_val = (
        "&lt;b&gt;Thread Checkpointer &amp;amp; State Persistence&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#4A5568&quot;&gt;"
        "• Serializes &lt;code&gt;AgentState&lt;/code&gt; snapshot at interrupts&lt;br&gt;"
        "• Non-blocking thread release via &lt;code&gt;thread_id&lt;/code&gt;&lt;br&gt;"
        "• Deterministic resumption upon human response&lt;/font&gt;"
    )
    checkpointer_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#F7FAFC;strokeColor=#CBD5E0;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#2D3748;align=left;verticalAlign=top;spacingLeft=12;spacingTop=8;"
    )
    add_cell("checkpointer", "1", checkpointer_val, checkpointer_style, 40, 30, 310, 110)

    # 2. Main Execution Pipeline (Center Column: x=460, width=420)
    col_x = 460
    node_w = 420

    # START Node
    start_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#2D3748;strokeColor=#1A202C;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#FFFFFF;align=center;verticalAlign=middle;fontStyle=1;"
    )
    add_cell("node_start", "1", "START", start_style, col_x + 155, 30, 110, 36)

    # Phase 1: Intent Ingestion & Scoping
    p1_val = (
        "&lt;b&gt;Phase 1: Intent Ingestion &amp;amp; Topological Scoping&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;intent_ingest&lt;/code&gt;: Raw &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;NL&lt;/sub&gt; + Mock GraphRAG scoped subtopology &lt;i&gt;G&lt;/i&gt;&lt;sub&gt;sub&lt;/sub&gt;&lt;/font&gt;"
    )
    p1_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EBF8FF;strokeColor=#3182CE;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p1", "1", p1_val, p1_style, col_x, 95, node_w, 64)

    # Phase 2: PDDL Parsing & Reconciliation
    p2_val = (
        "&lt;b&gt;Phase 2: PDDL Parsing &amp;amp; Intent Reconciler&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;pddl_parser&lt;/code&gt;: LLM Translation → &lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt; + CFG AST check (Re-entry target)&lt;/font&gt;"
    )
    p2_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EBF8FF;strokeColor=#3182CE;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p2", "1", p2_val, p2_style, col_x, 185, node_w, 64)

    # Phase 3a: Reverse Prompting
    p3a_val = (
        "&lt;b&gt;Phase 3a: Automated Reverse Prompting&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;reverse_prompt&lt;/code&gt;: Autonomous PDDL → &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;recon&lt;/sub&gt; (zero human interrupts)&lt;/font&gt;"
    )
    p3a_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FAF5FF;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p3a", "1", p3a_val, p3a_style, col_x, 275, node_w, 64)

    # Gate 1: Semantic RADG Router
    gate1_val = (
        "&lt;b&gt;GATE 1: Semantic RADG Conditional Router&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot;&gt;&lt;code&gt;semantic_gate&lt;/code&gt;: &lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; = &lt;i&gt;f&lt;/i&gt;(&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt;, &lt;i&gt;d&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt;) ≤ &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; (0.30)?&lt;/font&gt;"
    )
    gate1_style = (
        "rhombus;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#B7791F;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#744210;align=center;verticalAlign=middle;"
    )
    add_cell("gate_sem", "1", gate1_val, gate1_style, col_x - 10, 365, node_w + 20, 84)

    # Phase 3b: HITL Clarify Interrupt (Left Column)
    p3b_val = (
        "&lt;b&gt;Phase 3b: HITL Clarify Checkpoint&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#7B341E&quot;&gt;"
        "&lt;code&gt;hitl_clarify&lt;/code&gt;: LangGraph &lt;code&gt;interrupt()&lt;/code&gt;&lt;br&gt;"
        "Halts thread; presents &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;recon&lt;/sub&gt; to operator&lt;/font&gt;"
    )
    p3b_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEEBC8;strokeColor=#DD6B20;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p3b", "1", p3b_val, p3b_style, 35, 369, 295, 76)

    # Phase 4: Deterministic Symbolic Solver
    p4_val = (
        "&lt;b&gt;Phase 4: Deterministic Symbolic Solver&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;symbolic_solver&lt;/code&gt;: Yen&#39;s &lt;i&gt;K&lt;/i&gt;-Shortest Paths (&lt;i&gt;K&lt;/i&gt; = 5) on pruned &lt;i&gt;G̃&lt;/i&gt;&lt;sub&gt;sub&lt;/sub&gt;&lt;/font&gt;"
    )
    p4_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EDFDFD;strokeColor=#319795;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p4", "1", p4_val, p4_style, col_x, 520, node_w, 64)

    # Phase 5: Deterministic QoT Validation
    p5_val = (
        "&lt;b&gt;Phase 5: Deterministic QoT Validation&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;qot_validation&lt;/code&gt;: Incoherent GN Model (ASE + NLI GSNR computation)&lt;/font&gt;"
    )
    p5_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EDFDFD;strokeColor=#319795;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p5", "1", p5_val, p5_style, col_x, 610, node_w, 64)

    # Gate 2: Physical RADG Router
    gate2_val = (
        "&lt;b&gt;GATE 2: Physical RADG Conditional Router&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot;&gt;&lt;code&gt;radg&lt;/code&gt;: QoT&lt;sub&gt;valid&lt;/sub&gt;(&lt;i&gt;π&lt;/i&gt;) = 1? (GSNR ≥ GSNR&lt;sub&gt;th&lt;/sub&gt; ∧ &lt;i&gt;P&lt;/i&gt;&lt;sub&gt;rx&lt;/sub&gt; ≥ &lt;i&gt;P&lt;/i&gt;&lt;sub&gt;min&lt;/sub&gt;)&lt;/font&gt;"
    )
    gate2_style = (
        "rhombus;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#B7791F;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#744210;align=center;verticalAlign=middle;"
    )
    add_cell("gate_phys", "1", gate2_val, gate2_style, col_x - 10, 700, node_w + 20, 84)

    # Phase 6: Physical Replan Interrupt (Left Column)
    p6_val = (
        "&lt;b&gt;Phase 6: Physical Replan Checkpoint&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#742A2A&quot;&gt;"
        "&lt;code&gt;radg&lt;/code&gt;: LangGraph &lt;code&gt;interrupt()&lt;/code&gt;&lt;br&gt;"
        "Halts thread; presents QoT failure telemetry to operator&lt;/font&gt;"
    )
    p6_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FED7D7;strokeColor=#E53E3E;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p6", "1", p6_val, p6_style, 40, 704, 310, 76)

    # Phase 7: Plan Synthesis & Provisioning
    p7_val = (
        "&lt;b&gt;Phase 7: Plan Synthesis &amp;amp; Auditable Trace&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;plan_synthesizer&lt;/code&gt;: Auditable Planning Report + NBI Dispatch&lt;/font&gt;"
    )
    p7_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F0FFF4;strokeColor=#38A169;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("node_p7", "1", p7_val, p7_style, col_x, 855, node_w, 64)

    # END Node
    end_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=50;fillColor=#2D3748;strokeColor=#1A202C;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#FFFFFF;align=center;verticalAlign=middle;fontStyle=1;"
    )
    add_cell("node_end", "1", "END", end_style, col_x + 155, 955, 110, 36)

    # 3. Transitions & Edges
    edge_std = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2D3748;strokeWidth=1.5;endArrow=block;endFill=1;"

    # START -> Phase 1
    add_cell("e_start_p1", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_start", target="node_p1")
    # Phase 1 -> Phase 2
    add_cell("e_p1_p2", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_p1", target="node_p2")
    # Phase 2 -> Phase 3a
    add_cell("e_p2_p3a", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_p2", target="node_p3a")
    # Phase 3a -> Gate 1
    add_cell("e_p3a_gate1", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_p3a", target="gate_sem")

    # Gate 1 -> Phase 3b (HITL Clarify)
    e_gate1_p3b_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DD6B20;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#7B341E;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_gate1_p3b", "1", "&lt;b&gt;&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; &gt; &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;(Ambiguity)", e_gate1_p3b_style, 0, 0, 0, 0, is_edge=True, source="gate_sem", target="node_p3b")

    # Gate 1 -> Phase 4 (Autonomous Pass)
    e_gate1_p4_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#38A169;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#22543D;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_gate1_p4", "1", "&lt;b&gt;&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; ≤ &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;(Autonomous Pass)", e_gate1_p4_style, 0, 0, 0, 0, is_edge=True, source="gate_sem", target="node_p4")

    # Phase 3b -> Phase 2 (Refined Feedback Loop)
    # Exits top of Phase 3b at x=280, y=369, goes up to y=225, enters left of Phase 2 at x=460, y=225
    e_p3b_p2_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;strokeColor=#DD6B20;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#7B341E;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;exitX=0.75;exitY=0;exitDx=0;exitDy=0;entryX=0;entryY=0.65;entryDx=0;entryDy=0;"
    )
    add_cell("e_p3b_p2", "1", "&lt;b&gt;Operator Clarification&lt;/b&gt;&lt;br&gt;(Refined Intent)", e_p3b_p2_style, 0, 0, 0, 0, is_edge=True, source="node_p3b", target="node_p2", points=[(272, 227)])

    # Phase 3b -> Phase 4 (Fast-Track Manual Override)
    # Exits bottom of Phase 3b at x=280, y=445, goes down to y=552, enters left of Phase 4 at x=460, y=552
    e_p3b_p4_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;strokeColor=#38A169;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#22543D;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;exitX=0.75;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_p3b_p4", "1", "&lt;b&gt;Fast-Track Override&lt;/b&gt;&lt;br&gt;(Bypass re-parsing, &lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 1)", e_p3b_p4_style, 0, 0, 0, 0, is_edge=True, source="node_p3b", target="node_p4", points=[(272, 552)])

    # Phase 4 -> Phase 5
    add_cell("e_p4_p5", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_p4", target="node_p5")
    # Phase 5 -> Gate 2
    add_cell("e_p5_gate2", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_p5", target="gate_phys")

    # Gate 2 -> Phase 6 (Replan Interrupt)
    e_gate2_p6_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#E53E3E;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#742A2A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_gate2_p6", "1", "&lt;b&gt;QoT&lt;sub&gt;valid&lt;/sub&gt; = 0&lt;/b&gt;&lt;br&gt;(Physics Failed)", e_gate2_p6_style, 0, 0, 0, 0, is_edge=True, source="gate_phys", target="node_p6")

    # Phase 6 -> Phase 2 (Constraint Relaxation Loop)
    # Exits left of Phase 6 at x=40, y=742. Runs up along x=18 to y=197, enters Phase 2 at x=460, y=197.
    # Label is positioned vertically at x=18 without colliding with anything!
    e_p6_p2_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;strokeColor=#E53E3E;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#742A2A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.2;entryDx=0;entryDy=0;"
    )
    add_cell("e_p6_p2", "1", "&lt;b&gt;Constraint Relaxation Loop&lt;/b&gt;&lt;br&gt;(Relax GSNR / adjust topology)", e_p6_p2_style, 0, 0, 0, 0, is_edge=True, source="node_p6", target="node_p2", points=[(18, 742), (18, 198)])

    # Gate 2 -> Phase 7 (Auto-Approve)
    e_gate2_p7_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#38A169;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#22543D;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_gate2_p7", "1", "&lt;b&gt;QoT&lt;sub&gt;valid&lt;/sub&gt; = 1&lt;/b&gt;&lt;br&gt;(Auto-Approve)", e_gate2_p7_style, 0, 0, 0, 0, is_edge=True, source="gate_phys", target="node_p7")

    # Phase 7 -> END
    add_cell("e_p7_end", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="node_p7", target="node_end")

    # 4. Checkpointer Associations:
    # Instead of piercing the boxes, connect neatly from right-side or top of boxes:
    # Connection 1: from Checkpointer bottom (x=120, y=140) to Phase 3b top (x=120, y=369)
    assoc_p3b_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;dashPattern=2 3;"
        "strokeColor=#718096;strokeWidth=1.4;endArrow=none;fontFamily=Georgia, Times New Roman, serif;fontSize=11.5;fontColor=#4A5568;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("assoc_check_p3b", "1", "State Snapshot", assoc_p3b_style, 0, 0, 0, 0, is_edge=True, source="checkpointer", target="node_p3b", points=[(120, 140), (120, 369)])

    # Connection 2: from Phase 3b bottom (x=120, y=445) down to Phase 6 top (x=120, y=704)
    add_cell("assoc_p3b_p6", "1", "State Snapshot", assoc_p3b_style, 0, 0, 0, 0, is_edge=True, source="node_p3b", target="node_p6", points=[(120, 445), (120, 704)])

    xml.extend([
        '      </root>',
        '    </mxGraphModel>',
        '  </diagram>',
        '</mxfile>',
    ])
    return "\n".join(xml)


def main():
    content = generate_drawio_xml()
    try:
        ET.fromstring(content)
        print("✓ XML syntax validation passed.")
    except ET.ParseError as e:
        print(f"✗ XML validation failed: {e}")
        return 1

    out_file = Path(__file__).resolve().parent / "langgraph_execution_flow.drawio"
    out_file.write_text(content, encoding="utf-8")
    print(f"✓ Successfully generated {out_file}")
    return 0


if __name__ == "__main__":
    exit(main())
