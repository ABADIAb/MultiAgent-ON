#!/usr/bin/env python3
"""
Generate native Draw.io XML (.drawio) for Figure 3.2: Conceptual Framework & 7-Phase Orchestration Pipeline.
Matches fig_3_2_conceptual_framework.py exactly:
- Fully XML-attribute compliant (escapes all HTML tags in value attributes).
- Validated via xml.etree.ElementTree.
- Exact colors, coordinates, and connectors.
"""
import html
from pathlib import Path
import xml.etree.ElementTree as ET

def build_drawio_xml():
    scale = 80
    
    def to_drawio(x, y, w, h):
        dx = round(x * scale)
        dy = round((9.8 - y - h) * scale)
        dw = round(w * scale)
        dh = round(h * scale)
        return dx, dy, dw, dh

    cells = []
    
    def add_box(cid, x, y, w, h, title, detail, fc, ec, font_c="#1A202C", stroke_w=1.4):
        dx, dy, dw, dh = to_drawio(x, y, w, h)
        
        # Build raw HTML label first, then escape it for the XML attribute
        detail_html = detail.replace("\n", "<br>")
        if detail_html:
            raw_html = f"<b>{title}</b><br><font style=\"font-size: 11px;\" color=\"#4A5568\">{detail_html}</font>"
        else:
            raw_html = f"<b>{title}</b>"
            
        attr_val = html.escape(raw_html, quote=True)
        style = (
            f"rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor={fc};strokeColor={ec};"
            f"strokeWidth={stroke_w};fontFamily=Georgia, Times New Roman, serif;fontSize=13;"
            f"fontColor={font_c};align=center;verticalAlign=middle;"
        )
        cells.append(
            f'<mxCell id="{cid}" value="{attr_val}" style="{style}" vertex="1" parent="1">\n'
            f'  <mxGeometry x="{dx}" y="{dy}" width="{dw}" height="{dh}" as="geometry" />\n'
            f'</mxCell>'
        )

    def add_gate(cid, cx, cy, rw, rh, title, detail, fc="#FEFCBF", ec="#B7791F"):
        x = cx - rw
        y = cy - rh
        w = 2 * rw
        h = 2 * rh
        dx, dy, dw, dh = to_drawio(x, y, w, h)
        
        detail_html = detail.replace("\n", "<br>")
        if detail_html:
            raw_html = f"<b>{title}</b><br><font style=\"font-size: 11px;\"><i>{detail_html}</i></font>"
        else:
            raw_html = f"<b>{title}</b>"
            
        attr_val = html.escape(raw_html, quote=True)
        style = (
            f"rhombus;whiteSpace=wrap;html=1;fillColor={fc};strokeColor={ec};"
            f"strokeWidth=1.5;fontFamily=Georgia, Times New Roman, serif;fontSize=12;"
            f"fontColor=#744210;align=center;verticalAlign=middle;"
        )
        cells.append(
            f'<mxCell id="{cid}" value="{attr_val}" style="{style}" vertex="1" parent="1">\n'
            f'  <mxGeometry x="{dx}" y="{dy}" width="{dw}" height="{dh}" as="geometry" />\n'
            f'</mxCell>'
        )

    def add_edge(eid, source, target, label="", color="#2D3748", stroke_w=1.4, dashed=0, curved=0):
        style = (
            f"edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;"
            f"strokeColor={color};strokeWidth={stroke_w};fontFamily=Georgia, Times New Roman, serif;fontSize=11;"
            f"endArrow=block;endFill=1;"
        )
        if dashed:
            style += "dashed=1;"
        if curved:
            style = (
                f"edgeStyle=none;curved=1;html=1;strokeColor={color};strokeWidth={stroke_w};"
                f"fontFamily=Georgia, Times New Roman, serif;fontSize=11;endArrow=block;endFill=1;"
            )
            if dashed:
                style += "dashed=1;"

        attr_val = html.escape(label, quote=True)
        edge_xml = (
            f'<mxCell id="{eid}" value="{attr_val}" style="{style}" edge="1" parent="1" source="{source}" target="{target}">\n'
            f'  <mxGeometry relative="1" as="geometry" />\n'
            f'</mxCell>'
        )
        cells.append(edge_xml)

    # 1. Pipeline Phases
    cw = 4.4
    cx = 3.8
    center_x = cx + cw / 2  # 6.0

    # Phase 1
    add_box("p1", cx, 8.6, cw, 0.75, "Phase 1: Intent Ingestion & Optical RAG",
            "Raw intent <i>I</i><sub>NL</sub> + <i>k</i>-hop subtopology <i>G</i><sub>sub</sub> extraction",
            fc="#EBF8FF", ec="#3182CE")

    # Phase 2
    add_box("p2", cx, 7.45, cw, 0.75, "Phase 2: CFG-Validated PDDL Parsing",
            "LLM Semantic Compiler → <i>S</i><sub>PDDL</sub> + AST Audit (<i>v</i><sub>struct</sub>)",
            fc="#EBF8FF", ec="#3182CE")

    # Phase 3a
    add_box("p3a", cx, 6.3, cw, 0.75, "Phase 3a: Automated Reverse Prompting",
            "Autonomous PDDL → <i>I</i><sub>recon</sub> (0 interrupts, LLM reconstruction)",
            fc="#FAF5FF", ec="#805AD5")

    # Gate 1: Semantic Gate
    add_gate("g1", center_x, 5.25, 2.1, 0.5, "GATE 1: Semantic Gate",
             "<i>U</i><sub>sem</sub> = <i>f</i>(<i>v</i><sub>struct</sub>, <i>d</i><sub>sem</sub>) ≤ <i>τ</i><sub>sem</sub> ?")

    # Phase 3b: HITL Clarify
    add_box("p3b", 0.6, 4.8, 2.4, 0.9, "Phase 3b: HITL Clarify",
            "LangGraph interrupt()\nOperator resolves ambiguity",
            fc="#FEEBC8", ec="#DD6B20", stroke_w=1.6)

    # Phase 4: Symbolic Solver
    add_box("p4", cx, 3.85, cw, 0.75, "Phase 4: Deterministic Symbolic Solver",
            "Pruned topology <i>G̃</i><sub>sub</sub> + Yen's K-Shortest Paths (<i>K</i> = 5)",
            fc="#EDFDFD", ec="#319795")

    # Phase 5: QoT Validation
    add_box("p5", cx, 2.7, cw, 0.75, "Phase 5: Deterministic QoT Validation",
            "Analytical Coherent GN Model: GSNR & <i>P</i><sub>rx</sub> calculation",
            fc="#EDFDFD", ec="#319795")

    # Gate 2: Physical Risk Gate
    add_gate("g2", center_x, 1.6, 2.1, 0.5, "GATE 2: Physical Risk Gate",
             "QoT<sub>valid</sub>(<i>π</i>) = 1 ? (GSNR ≥ GSNR<sub>th</sub>)")

    # Phase 6: Suggest Replan
    add_box("p6", 0.6, 1.15, 2.4, 0.9, "Phase 6: Suggest Replan (RADG)",
            "LangGraph interrupt()\nRelax constraints / modulation",
            fc="#FED7D7", ec="#E53E3E", stroke_w=1.6)

    # Phase 7: Synthesis & Provisioning
    add_box("p7", cx, 0.25, cw, 0.75, "Phase 7: Plan Synthesis & Provisioning",
            "Auditable Planning Report + RESTCONF / NETCONF Dispatch",
            fc="#F0FFF4", ec="#38A169")

    # 2. Right Side Panel: Fail-Fast Properties
    px, py, pw, ph = to_drawio(8.8, 1.5, 3.9, 7.0)
    panel_bg = (
        f'<mxCell id="panel_bg" value="" style="rounded=1;whiteSpace=wrap;html=1;arcSize=4;fillColor=#F7FAFC;strokeColor=#CBD5E0;strokeWidth=1.2;" vertex="1" parent="1">\n'
        f'  <mxGeometry x="{px}" y="{py}" width="{pw}" height="{ph}" as="geometry" />\n'
        f'</mxCell>'
    )
    cells.append(panel_bg)

    # Panel Title
    pty = py + 15
    title_val = html.escape("<b>Fail-Fast Properties</b>", quote=True)
    panel_title = (
        f'<mxCell id="panel_title" value="{title_val}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;fontFamily=Georgia, Times New Roman, serif;fontSize=15;fontColor=#2D3748;" vertex="1" parent="1">\n'
        f'  <mxGeometry x="{px}" y="{pty}" width="{pw}" height="30" as="geometry" />\n'
        f'</mxCell>'
    )
    cells.append(panel_title)

    props = [
        ("Orthogonal Gating:", "Decouples linguistic ambiguity (Gate 1)<br>from physical propagation feasibility (Gate 2)."),
        ("Zero-Overhead Autonomy:", "When <i>U</i><sub>sem</sub> ≤ 0.30 and QoT passes,<br>execution completes with 0 human pauses."),
        ("Deterministic Physics:", "GN model physics calculations never<br>run on hallucinatory paths."),
        ("Protected Control Plane:", "No unverified commands ever reach<br>the SDON controller or ROADM hardware."),
        ("LangGraph Checkpointing:", "Human-in-the-Loop interrupts use<br>atomic state serialization.")
    ]
    curr_y = py + 55
    for idx, (title, desc) in enumerate(props):
        raw_item = f"<b><font color=\"#2B6CB0\">{title}</font></b><br><font color=\"#4A5568\" style=\"font-size:11px;\">{desc}</font>"
        item_val = html.escape(raw_item, quote=True)
        item_style = (
            "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FFFFFF;strokeColor=#E2E8F0;strokeWidth=1;"
            "align=left;verticalAlign=middle;spacingLeft=10;spacingRight=10;"
            "fontFamily=Georgia, Times New Roman, serif;fontSize=12;"
        )
        cells.append(
            f'<mxCell id="prop_{idx}" value="{item_val}" style="{item_style}" vertex="1" parent="1">\n'
            f'  <mxGeometry x="{px + 15}" y="{curr_y}" width="{pw - 30}" height="75" as="geometry" />\n'
            f'</mxCell>'
        )
        curr_y += 88

    # 3. Connectors & Flows
    add_edge("e_p1_p2", "p1", "p2")
    add_edge("e_p2_p3a", "p2", "p3a")
    add_edge("e_p3a_g1", "p3a", "g1")

    # Gate 1 Pass: Down to Phase 4
    add_edge("e_g1_p4", "g1", "p4", label="Yes (Auto-Pass)", color="#276749", stroke_w=1.6)

    # Gate 1 Fail: Left to Phase 3b
    add_edge("e_g1_p3b", "g1", "p3b", label="No (<i>U</i><sub>sem</sub> > <i>τ</i><sub>sem</sub>)", color="#C05621", stroke_w=1.6)

    # Phase 3b loop back to Phase 2 (Curved dashed feedback)
    add_edge("e_p3b_p2", "p3b", "p2", label="Operator Clarification Loop", color="#C05621", stroke_w=1.5, dashed=1, curved=1)

    # Phase 4 to Phase 5
    add_edge("e_p4_p5", "p4", "p5")

    # Phase 5 to Gate 2
    add_edge("e_p5_g2", "p5", "g2")

    # Gate 2 Pass: Down to Phase 7
    add_edge("e_g2_p7", "g2", "p7", label="Yes (Auto-Approve)", color="#276749", stroke_w=1.6)

    # Gate 2 Fail: Left to Phase 6
    add_edge("e_g2_p6", "g2", "p6", label="No (QoT Invalid)", color="#C53030", stroke_w=1.6)

    # Phase 6 loop back to Phase 2 (Curved dashed feedback)
    add_edge("e_p6_p2", "p6", "p2", label="Replan & Constraint Relaxation Loop", color="#C53030", stroke_w=1.5, dashed=1, curved=1)

    xml_content = (
        '<mxfile host="app.diagrams.net" modified="2026-09-06T10:30:00.000Z" agent="5.0" version="22.0.0" type="device">\n'
        '  <diagram id="fig_3_2" name="Figure 3.2: Conceptual Framework">\n'
        '    <mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1100" pageHeight="850" math="1" shadow="0">\n'
        '      <root>\n'
        '        <mxCell id="0" />\n'
        '        <mxCell id="1" parent="0" />\n'
        + "\n".join("        " + c for c in cells) + "\n"
        '      </root>\n'
        '    </mxGraphModel>\n'
        '  </diagram>\n'
        '</mxfile>'
    )
    return xml_content

def main():
    out_dir = Path(__file__).resolve().parent
    xml = build_drawio_xml()
    
    # Rigorous XML validation
    try:
        ET.fromstring(xml)
        print("XML validation passed! No unescaped characters.")
    except ET.ParseError as e:
        print(f"FATAL XML PARSE ERROR: {e}")
        raise
        
    out_file = out_dir / "figure_3_2_conceptual_framework.drawio"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"Generated {out_file}")

if __name__ == "__main__":
    main()
