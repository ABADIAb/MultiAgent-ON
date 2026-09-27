#!/usr/bin/env python3
"""
Generates the native Draw.io XML for Figure 4.2: semantic_engine.drawio.
Adheres strictly to thesis-coauthor figure guidelines:
- Generous typography (titles: 15-16 pt bold, subtitles: 12.5-13.5 pt, gates: 14 pt bold, edges: 12.5 pt)
- Academic color palette (neural, symbolic, gates, HITL, checkpointer)
- Strict XML escaping and well-formed XML AST validation.
- Clean closed-loop visual layout: Forward translation (Left->Right) in Layer 1,
  Reverse reconstruction (Right->Left) in Layer 2, zero crossed lines.
"""

import xml.etree.ElementTree as ET
from pathlib import Path


def generate_semantic_engine_xml() -> str:
    xml = [
        '<mxfile host="Electron" agent="5.0">',
        '  <diagram id="fig_semantic_engine" name="Two-Layer Semantic Engine Architecture">',
        '    <mxGraphModel dx="1400" dy="1200" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1040" pageHeight="1140" math="1" shadow="0">',
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

    # -------------------------------------------------------------------------
    # STAGE 0: Ingestion & Intent Reconciliation (y=30 to y=180)
    # -------------------------------------------------------------------------
    box_intent_val = (
        "&lt;b&gt;Raw Operator Intent &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;NL&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#4A5568&quot;&gt;"
        "Verbatim prompt string: ingress/egress nodes, bandwidth, avoidance rules&lt;/font&gt;"
    )
    box_intent_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EBF8FF;strokeColor=#3182CE;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("box_intent", "1", box_intent_val, box_intent_style, 75, 30, 425, 60)

    box_graphrag_val = (
        "&lt;b&gt;Mock GraphRAG Scoped Topology &lt;i&gt;G&lt;/i&gt;&lt;sub&gt;sub&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#285E61&quot;&gt;"
        "&lt;i&gt;k&lt;/i&gt;-hop switching neighborhood (&lt;i&gt;k&lt;/i&gt; = 2) bounding context tokens&lt;/font&gt;"
    )
    box_graphrag_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EDFDFD;strokeColor=#319795;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("box_graphrag", "1", box_graphrag_val, box_graphrag_style, 540, 30, 425, 60)

    box_reconciler_val = (
        "&lt;b&gt;Multi-Turn Intent Reconciler (&lt;code&gt;intent_reconciler&lt;/code&gt;)&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#4A5568&quot;&gt;"
        "• &lt;b&gt;Full Replacement:&lt;/b&gt; Discards stale state on new request; rescopes &lt;i&gt;G&lt;/i&gt;&lt;sub&gt;sub&lt;/sub&gt; on endpoint shift&lt;br&gt;"
        "• &lt;b&gt;Partial Update:&lt;/b&gt; Preserves active constraints; applies relaxed parameters without ghost leakage&lt;/font&gt;"
    )
    box_reconciler_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F7FAFC;strokeColor=#CBD5E0;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#2D3748;align=left;verticalAlign=middle;spacingLeft=16;"
    )
    add_cell("box_reconciler", "1", box_reconciler_val, box_reconciler_style, 75, 110, 890, 66)

    # -------------------------------------------------------------------------
    # LAYER 1: Structural CFG AST Verification (y=195 to y=395) - Left to Right
    # -------------------------------------------------------------------------
    layer1_group_val = (
        "&lt;b&gt;LAYER 1: Context-Free Grammar (CFG) AST Structural Verification&lt;/b&gt; "
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#2B6CB0&quot;&gt;"
        "— Deterministic AST parsing &amp;amp; syntax invariant enforcement (&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; ∈ {0, 1})&lt;/font&gt;"
    )
    layer1_group_style = (
        "swimlane;whiteSpace=wrap;html=1;arcSize=6;fillColor=#F7FAFC;strokeColor=#3182CE;strokeWidth=1.6;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13.5;fontColor=#2B6CB0;collapsible=0;startSize=30;align=left;spacingLeft=14;"
    )
    add_cell("layer1_group", "1", layer1_group_val, layer1_group_style, 75, 195, 890, 200)

    # PDDL Translation LLM
    pddl_llm_val = (
        "&lt;b&gt;PDDL Translation LLM&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#4A5568&quot;&gt;"
        "&lt;code&gt;pddl_parser&lt;/code&gt;: Translates &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;NL&lt;/sub&gt; + &lt;i&gt;G&lt;/i&gt;&lt;sub&gt;sub&lt;/sub&gt;&lt;br&gt;"
        "into formal PDDL string &lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt;&lt;/font&gt;"
    )
    pddl_llm_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#EBF8FF;strokeColor=#3182CE;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13.5;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("pddl_llm", "layer1_group", pddl_llm_val, pddl_llm_style, 25, 42, 240, 76)

    # Deterministic AST Parser
    ast_parser_val = (
        "&lt;b&gt;Deterministic AST CFG Validator&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#2D3748&quot;&gt;"
        "• Tokenizer: invariant depth ≥ 0, terminates at zero&lt;br&gt;"
        "• Recursive builder: extracts &lt;code&gt;:domain&lt;/code&gt;, &lt;code&gt;:init&lt;/code&gt;, &lt;code&gt;:goal&lt;/code&gt;&lt;br&gt;"
        "• Arity audit: &lt;code&gt;avoid-node&lt;/code&gt;, &lt;code&gt;min-gsnr&lt;/code&gt;, &lt;code&gt;max-hops&lt;/code&gt;&lt;/font&gt;"
    )
    ast_parser_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFFFFF;strokeColor=#3182CE;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13;fontColor=#1A202C;align=left;verticalAlign=middle;spacingLeft=10;"
    )
    add_cell("ast_parser", "layer1_group", ast_parser_val, ast_parser_style, 305, 42, 330, 76)

    # Structural AST Gate Verdict
    ast_gate_val = (
        "&lt;b&gt;AST Structural Verdict&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot;&gt;"
        "&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; ∈ {0, 1}&lt;br&gt;"
        "Valid S-expression?&lt;/font&gt;"
    )
    ast_gate_style = (
        "rhombus;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#B7791F;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#744210;align=center;verticalAlign=middle;"
    )
    add_cell("ast_gate", "layer1_group", ast_gate_val, ast_gate_style, 665, 34, 205, 92)

    # Error note block in Layer 1 (restricted width to leave right area open!)
    ast_err_val = (
        "&lt;b&gt;Syntax / Grammar Failure (&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 0):&lt;/b&gt; "
        "Forces &lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; = 1.0; halts Layer 2 and diverts directly to Semantic RADG interrupt."
    )
    ast_err_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FFF5F5;strokeColor=#E53E3E;strokeWidth=1.2;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#742A2A;align=center;verticalAlign=middle;"
    )
    add_cell("ast_err_box", "layer1_group", ast_err_val, ast_err_style, 25, 138, 610, 42)

    # -------------------------------------------------------------------------
    # LAYER 2: Automated Reverse Prompting & Semantic Agreement (y=420 to y=620) - Right to Left
    # -------------------------------------------------------------------------
    layer2_group_val = (
        "&lt;b&gt;LAYER 2: Automated Reverse Prompting &amp;amp; Semantic Agreement Scoring&lt;/b&gt; "
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#553C9A&quot;&gt;"
        "— Closed-loop linguistic reconstruction &amp;amp; agreement judge (zero human interrupts)&lt;/font&gt;"
    )
    layer2_group_style = (
        "swimlane;whiteSpace=wrap;html=1;arcSize=6;fillColor=#FAF5FF;strokeColor=#805AD5;strokeWidth=1.6;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13.5;fontColor=#553C9A;collapsible=0;startSize=30;align=left;spacingLeft=14;"
    )
    add_cell("layer2_group", "1", layer2_group_val, layer2_group_style, 75, 420, 890, 200)

    # Topological Predicate Filter (Right)
    pddl_filter_val = (
        "&lt;b&gt;Goal Predicate Filter&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#553C9A&quot;&gt;"
        "Strips verbose network facts,&lt;br&gt;isolating operational goal rules&lt;/font&gt;"
    )
    pddl_filter_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFFFFF;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("pddl_filter", "layer2_group", pddl_filter_val, pddl_filter_style, 645, 42, 225, 76)

    # Autonomous Reconstruction LLM (Center)
    rev_llm_val = (
        "&lt;b&gt;Autonomous Reconstruction LLM&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#553C9A&quot;&gt;"
        "&lt;code&gt;reverse_prompt&lt;/code&gt;: Translates &lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt;&lt;sup&gt;goal&lt;/sup&gt; → &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;recon&lt;/sub&gt;&lt;br&gt;"
        "&lt;b&gt;zero human interrupts&lt;/b&gt;&lt;/font&gt;"
    )
    rev_llm_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FAF5FF;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("rev_llm", "layer2_group", rev_llm_val, rev_llm_style, 335, 42, 275, 76)

    # Independent LLM Agreement Judge (Left)
    judge_val = (
        "&lt;b&gt;Independent LLM Agreement Judge&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#553C9A&quot;&gt;"
        "Evaluates (&lt;i&gt;I&lt;/i&gt;&lt;sub&gt;NL&lt;/sub&gt;, &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;recon&lt;/sub&gt;) semantic alignment&lt;br&gt;"
        "Outputs divergence: &lt;b&gt;&lt;i&gt;d&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; ∈ [0, 1]&lt;/b&gt;&lt;/font&gt;"
    )
    judge_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FFFFFF;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("judge_llm", "layer2_group", judge_val, judge_style, 25, 42, 275, 76)

    # Layer 2 note block
    layer2_note_val = (
        "&lt;b&gt;Closed-Loop Validation Contract:&lt;/b&gt; "
        "Verifies that semantic intent was preserved during PDDL compilation without human interruption."
    )
    layer2_note_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=6;fillColor=#F7FAFC;strokeColor=#CBD5E0;strokeWidth=1.2;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#4A5568;align=center;verticalAlign=middle;"
    )
    add_cell("layer2_note", "layer2_group", layer2_note_val, layer2_note_style, 25, 138, 845, 42)

    # -------------------------------------------------------------------------
    # STAGE 3: Semantic RADG Decision Multiplexer (y=645 to y=1050)
    # -------------------------------------------------------------------------
    gate_sem_val = (
        "&lt;b&gt;SEMANTIC RADG DECISION GATE&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 13px;&quot;&gt;"
        "&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; = (1.0 if &lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 0 else &lt;i&gt;d&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt;) ≤ &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; (0.30)?&lt;/font&gt;"
    )
    gate_sem_style = (
        "rhombus;whiteSpace=wrap;html=1;fillColor=#FEFCBF;strokeColor=#B7791F;strokeWidth=1.6;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#744210;align=center;verticalAlign=middle;"
    )
    add_cell("gate_radg", "1", gate_sem_val, gate_sem_style, 250, 650, 540, 92)

    # Branch A: Autonomous Pass (Phase 4 Forward) - Right
    branch_pass_val = (
        "&lt;b&gt;Branch A: Autonomous Pass (Phase 4 Forward)&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#22543D&quot;&gt;"
        "&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; ≤ &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; &amp;amp; &lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 1&lt;br&gt;"
        "Dispatches verified &lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt; directly to Symbolic Solver&lt;br&gt;"
        "&lt;b&gt;zero human interruptions on unambiguous intents&lt;/b&gt;&lt;/font&gt;"
    )
    branch_pass_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F0FFF4;strokeColor=#38A169;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("branch_pass", "1", branch_pass_val, branch_pass_style, 535, 790, 430, 84)

    # Branch B: HITL Clarify Interrupt - Left
    branch_clarify_val = (
        "&lt;b&gt;Branch B: Fail-Fast HITL Clarify (Phase 3b)&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12.5px;&quot; color=&quot;#7B341E&quot;&gt;"
        "&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; &gt; &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; or syntax failure (&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 0)&lt;br&gt;"
        "LangGraph &lt;code&gt;interrupt()&lt;/code&gt; halts thread, serializes state,&lt;br&gt;"
        "and presents &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;recon&lt;/sub&gt; + error diagnostics to operator&lt;/font&gt;"
    )
    branch_clarify_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#FEEBC8;strokeColor=#DD6B20;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=14;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("branch_clarify", "1", branch_clarify_val, branch_clarify_style, 75, 790, 430, 84)

    # Fast-Track Manual Override Node
    override_box_val = (
        "&lt;b&gt;Operator Fast-Track Manual Override (Bypass)&lt;/b&gt;&lt;br&gt;"
        "&lt;font style=&quot;font-size: 12px;&quot; color=&quot;#22543D&quot;&gt;"
        "If &lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 1 and operator confirms intent despite &lt;i&gt;d&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; warning,&lt;br&gt;"
        "execution bypasses re-parsing and advances directly to Symbolic Solver (Phase 4)&lt;/font&gt;"
    )
    override_box_style = (
        "rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F0FFF4;strokeColor=#38A169;strokeWidth=1.4;dashed=1;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=13;fontColor=#1A202C;align=center;verticalAlign=middle;"
    )
    add_cell("override_box", "1", override_box_val, override_box_style, 260, 905, 520, 64)

    # -------------------------------------------------------------------------
    # EDGES & TRANSITIONS
    # -------------------------------------------------------------------------
    edge_std = "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2D3748;strokeWidth=1.5;endArrow=block;endFill=1;"

    # Intent & GraphRAG -> Reconciler
    add_cell("e_intent_rec", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="box_intent", target="box_reconciler")
    add_cell("e_rag_rec", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="box_graphrag", target="box_reconciler")

    # Reconciler -> PDDL LLM in Layer 1
    # Exits reconciler on left (x=75), runs down at x=55, enters left of PDDL LLM (x=100, y=275)
    e_rec_pddl_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#2D3748;strokeWidth=1.5;endArrow=block;endFill=1;"
        "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_rec_pddl", "1", "", e_rec_pddl_style, 0, 0, 0, 0, is_edge=True, source="box_reconciler", target="pddl_llm", points=[(55, 143), (55, 275)])

    # Inside Layer 1: PDDL LLM -> AST Parser
    e_pddl_ast_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#3182CE;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#2B6CB0;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_pddl_ast", "layer1_group", "&lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt;", e_pddl_ast_style, 0, 0, 0, 0, is_edge=True, source="pddl_llm", target="ast_parser")

    # Inside Layer 1: AST Parser -> AST Gate
    add_cell("e_ast_gate", "layer1_group", "", edge_std, 0, 0, 0, 0, is_edge=True, source="ast_parser", target="ast_gate")

    # Inside Layer 1: AST Gate Failure (v_struct = 0) -> Error Box
    # Exits left of ast_gate bottom, turns left into ast_err_box right side
    e_gate_err_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#E53E3E;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#742A2A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=0;exitY=1;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_gate_err", "layer1_group", "&lt;b&gt;&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 0&lt;/b&gt;", e_gate_err_style, 0, 0, 0, 0, is_edge=True, source="ast_gate", target="ast_err_box", points=[(715, 126), (715, 159)])

    # From Layer 1 AST Gate to Layer 2 Predicate Filter: PERFECT STRAIGHT VERTICAL DROP
    # AST gate bottom is at x=768, y=126 in Layer 1 (y=321 absolute).
    # Drops straight down through open air at x=830 directly into pddl_filter top (x=830, y=462 absolute)!
    e_ast_pass_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#38A169;strokeWidth=1.6;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#22543D;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=0.8;exitY=0.8;exitDx=0;exitDy=0;exitPerimeter=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;"
    )
    add_cell("e_ast_pass", "1", "&lt;b&gt;&lt;i&gt;v&lt;/i&gt;&lt;sub&gt;struct&lt;/sub&gt; = 1 (Pass)&lt;/b&gt;", e_ast_pass_style, 0, 0, 0, 0, is_edge=True, source="ast_gate", target="pddl_filter", points=[(832, 310), (832, 462)])

    # Inside Layer 2: Filter -> Reconstruction LLM (Right to Left)
    e_filter_rev_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#553C9A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_filter_rev", "layer2_group", "&lt;i&gt;S&lt;/i&gt;&lt;sub&gt;PDDL&lt;/sub&gt;&lt;sup&gt;goal&lt;/sup&gt;", e_filter_rev_style, 0, 0, 0, 0, is_edge=True, source="pddl_filter", target="rev_llm")

    # Inside Layer 2: Reconstruction LLM -> Agreement Judge (Right to Left)
    e_rev_judge_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#553C9A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_rev_judge", "layer2_group", "&lt;i&gt;I&lt;/i&gt;&lt;sub&gt;recon&lt;/sub&gt;", e_rev_judge_style, 0, 0, 0, 0, is_edge=True, source="rev_llm", target="judge_llm")

    # Verbatim Intent I_NL input to Judge (Track at x=38, completely open!)
    e_intent_judge_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;strokeColor=#3182CE;strokeWidth=1.4;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#2B6CB0;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_intent_judge", "1", "Verbatim &lt;i&gt;I&lt;/i&gt;&lt;sub&gt;NL&lt;/sub&gt;", e_intent_judge_style, 0, 0, 0, 0, is_edge=True, source="box_intent", target="judge_llm", points=[(38, 60), (38, 500)])

    # Layer 2 Judge -> Semantic RADG Gate (d_sem score from left into gate)
    e_judge_gate_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#805AD5;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#553C9A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_judge_gate", "1", "&lt;b&gt;&lt;i&gt;d&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; score&lt;/b&gt;", e_judge_gate_style, 0, 0, 0, 0, is_edge=True, source="judge_llm", target="gate_radg", points=[(238, 696)])

    # Error Box (Layer 1 v_struct = 0) -> Semantic RADG Gate (forces U_sem = 1.0 from right into gate)
    e_err_gate_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#E53E3E;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#742A2A;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=1;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_err_gate", "1", "&lt;b&gt;Forces &lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; = 1.0&lt;/b&gt;", e_err_gate_style, 0, 0, 0, 0, is_edge=True, source="ast_err_box", target="gate_radg", points=[(990, 354), (990, 696)])

    # Gate -> Branch A (Autonomous Pass)
    e_gate_pass_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#38A169;strokeWidth=1.6;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#22543D;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_gate_pass", "1", "&lt;b&gt;&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; ≤ &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;(Autonomous Pass)", e_gate_pass_style, 0, 0, 0, 0, is_edge=True, source="gate_radg", target="branch_pass")

    # Gate -> Branch B (HITL Clarify Interrupt)
    e_gate_clarify_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;strokeColor=#DD6B20;strokeWidth=1.6;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#7B341E;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
    )
    add_cell("e_gate_clarify", "1", "&lt;b&gt;&lt;i&gt;U&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt; &gt; &lt;i&gt;τ&lt;/i&gt;&lt;sub&gt;sem&lt;/sub&gt;&lt;/b&gt;&lt;br&gt;(Ambiguity Interrupt)", e_gate_clarify_style, 0, 0, 0, 0, is_edge=True, source="gate_radg", target="branch_clarify")

    # Branch B (Clarify) -> Loopback to Reconciler along Track at x=15 (completely clear!)
    e_clarify_rec_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;strokeColor=#DD6B20;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12.5;fontColor=#7B341E;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=0;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;"
    )
    add_cell("e_clarify_rec", "1", "&lt;b&gt;Operator Feedback Loop&lt;/b&gt;&lt;br&gt;(Clarification to Reconciler)", e_clarify_rec_style, 0, 0, 0, 0, is_edge=True, source="branch_clarify", target="box_reconciler", points=[(15, 832), (15, 143)])

    # Branch B (Clarify) -> Override Box
    add_cell("e_clarify_override", "1", "", edge_std, 0, 0, 0, 0, is_edge=True, source="branch_clarify", target="override_box")

    # Override Box -> Branch Pass (Forward Bypass)
    e_override_pass_style = (
        "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=1;dashed=1;strokeColor=#38A169;strokeWidth=1.5;"
        "fontFamily=Georgia, Times New Roman, serif;fontSize=12;fontColor=#22543D;endArrow=block;endFill=1;labelBackgroundColor=#FFFFFF;"
        "exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0.5;entryY=1;entryDx=0;entryDy=0;"
    )
    add_cell("e_override_pass", "1", "&lt;b&gt;Bypass re-parsing&lt;/b&gt;", e_override_pass_style, 0, 0, 0, 0, is_edge=True, source="override_box", target="branch_pass", points=[(800, 937), (800, 890), (750, 890)])

    xml.extend([
        '      </root>',
        '    </mxGraphModel>',
        '  </diagram>',
        '</mxfile>',
    ])
    return "\n".join(xml)


def main():
    content = generate_semantic_engine_xml()
    try:
        ET.fromstring(content)
        print("✓ XML syntax validation passed.")
    except ET.ParseError as e:
        print(f"✗ XML validation failed: {e}")
        return 1

    out_file = Path(__file__).resolve().parent / "semantic_engine.drawio"
    out_file.write_text(content, encoding="utf-8")
    print(f"✓ Successfully generated {out_file}")
    return 0


if __name__ == "__main__":
    exit(main())
