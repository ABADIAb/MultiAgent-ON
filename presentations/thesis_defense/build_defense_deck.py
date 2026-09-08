#!/usr/bin/env python3
"""
Master's Thesis Defense Slide Deck Builder.
Generates a 16-slide publication-quality presentation in PowerPoint (.pptx)
using the official Politecnico di Milano template, adhering strictly to
Prof. Massimo Tornatore's 15 Golden Rules.
"""

import sys
import copy
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# --- Institutional Color Palette ---
COLOR_NAVY = RGBColor(15, 44, 83)        # #0F2C53 - Primary brand headers & titles
COLOR_BURGUNDY = RGBColor(133, 32, 12)   # #85200C - Cover title accent, alert callouts
COLOR_DARK_SLATE = RGBColor(34, 34, 34)  # #222222 - Primary body text
COLOR_COOL_GRAY = RGBColor(90, 107, 130) # #5A6B82 - Subtitles and secondary notes
COLOR_CARD_BG = RGBColor(244, 246, 249)  # #F4F6F9 - Card container fill
COLOR_CARD_BORDER = RGBColor(208, 215, 222) # #D0D7DE - Card border
COLOR_GREEN = RGBColor(26, 127, 55)      # #1A7F37 - Feasible / Success
COLOR_RED = RGBColor(207, 34, 46)        # #CF222E - Violation / Failure

FONT_TITLE = "Titillium Web SemiBold"
FONT_BODY = "Arial"


class DeckBuilder:
    def __init__(self, template_path: Path):
        self.prs = Presentation(str(template_path))
        # Keep slide 0 (cover) and slide 1 (content base with header/footer)
        if len(self.prs.slides) < 2:
            raise ValueError("Template must contain at least 2 slides (cover and content base).")
        
        self.raw_cover = self.prs.slides[0]
        self.raw_content = self.prs.slides[1]

        # Extract content chrome shape elements to clone into new slides
        # We will build clean slides from scratch
        self.slide_width = self.prs.slide_width
        self.slide_height = self.prs.slide_height

    def clear_slides_except_template(self):
        """Cleans out slides beyond slide 2 so we start with a clean slate."""
        for i in range(len(self.prs.slides) - 1, 1, -1):
            rId = self.prs.slides._sldIdLst[i].rId
            self.prs.part.drop_rel(rId)
            del self.prs.slides._sldIdLst[i]

    def add_chrome(self, slide, title_text: str, slide_num: int):
        """Adds standard PoliMi header, underline, and footer chrome to a slide."""
        # Bottom Navy banner
        banner = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.15), Inches(13.333), Inches(0.35)
        )
        banner.fill.solid()
        banner.fill.fore_color.rgb = COLOR_NAVY
        banner.line.fill.background()

        # Footer text: POLITECNICO DI MILANO
        footer_box = slide.shapes.add_textbox(Inches(10.5), Inches(7.15), Inches(2.6), Inches(0.3))
        tf = footer_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = "POLITECNICO DI MILANO"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = RGBColor(255, 255, 255)
        p.alignment = PP_ALIGN.RIGHT

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(0.4), Inches(7.15), Inches(1.5), Inches(0.3))
        p_num = num_box.text_frame.paragraphs[0]
        p_num.text = str(slide_num)
        p_num.font.name = "Arial"
        p_num.font.size = Pt(11)
        p_num.font.color.rgb = RGBColor(255, 255, 255)

        # Slide Title
        title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.25), Inches(11.8), Inches(0.75))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.name = FONT_TITLE
        p_title.font.size = Pt(28)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY

        # Underline separator
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.02), Inches(11.8), Inches(0.02)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = COLOR_NAVY
        line.line.fill.background()

    def set_speaker_notes(self, slide, notes_text: str):
        """Sets structured speaker notes on a slide."""
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text.strip()

    def create_cover_slide(self):
        """Customizes Slide 1 as the Cover Slide."""
        s = self.prs.slides[0]
        # Remove old title, author, conference logo, and extraneous text boxes
        shapes_to_remove = []
        for shape in s.shapes:
            # Shape 8 is Picture 2 (old ACP conference logo)
            if shape.name == "Picture 2":
                shapes_to_remove.append(shape)
            elif shape.has_text_frame:
                if shape.name == "Google Shape;60;p13":
                    # Date box at bottom
                    shape.text_frame.text = "September 2026"
                    for p in shape.text_frame.paragraphs:
                        p.font.name = "Arial"
                        p.font.size = Pt(14)
                        p.font.bold = True
                        p.font.color.rgb = RGBColor(255, 255, 255)
                        p.alignment = PP_ALIGN.CENTER
                elif shape.name in ["Google Shape;54;p13", "Google Shape;59;p13"]:
                    # Old title and author boxes
                    shape.text_frame.text = ""

        for sh in shapes_to_remove:
            sp = sh._element
            sp.getparent().remove(sp)

        # Title Box
        title_box = s.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.7), Inches(2.2))
        tf = title_box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = "Risk-Adaptive Neurosymbolic Intent Planning\nfor Optical Networks"
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(36)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_BURGUNDY
        p1.alignment = PP_ALIGN.CENTER

        p2 = tf.add_paragraph()
        p2.text = "A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment"
        p2.font.name = FONT_BODY
        p2.font.size = Pt(20)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_NAVY
        p2.alignment = PP_ALIGN.CENTER

        # Metadata Box (Candidate & Advisor)
        meta_box = s.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(11.3), Inches(2.0))
        tf_meta = meta_box.text_frame
        tf_meta.word_wrap = True

        p_author = tf_meta.paragraphs[0]
        p_author.text = "Candidate: Felipe Abadía"
        p_author.font.name = FONT_BODY
        p_author.font.size = Pt(22)
        p_author.font.bold = True
        p_author.font.color.rgb = COLOR_NAVY
        p_author.alignment = PP_ALIGN.CENTER

        p_advisor = tf_meta.add_paragraph()
        p_advisor.text = "Academic Advisor: Prof. Massimo Tornatore"
        p_advisor.font.name = FONT_BODY
        p_advisor.font.size = Pt(19)
        p_advisor.font.bold = False
        p_advisor.font.color.rgb = COLOR_DARK_SLATE
        p_advisor.alignment = PP_ALIGN.CENTER

        p_dept = tf_meta.add_paragraph()
        p_dept.text = "Dipartimento di Elettronica, Informazione e Bioingegneria — Politecnico di Milano"
        p_dept.font.name = FONT_BODY
        p_dept.font.size = Pt(15)
        p_dept.font.color.rgb = COLOR_COOL_GRAY
        p_dept.alignment = PP_ALIGN.CENTER

        self.set_speaker_notes(s, """[Estimated Time]: 30s
[Key Message]: Welcome the committee and state the thesis research focus.
[Spoken Script]: Good morning members of the committee and Professor Tornatore. Today I present my Master's thesis entitled "Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment". In this work, we address the challenge of translating high-level operator intent into physically feasible optical configurations using a fail-fast, neurosymbolic pre-deployment pipeline.
[Bridge to Next Slide]: Let us begin with the specific roadmap of problems and solutions covered in this presentation.""")

    def create_card_slide(self, title: str, slide_num: int, cards: list[dict], notes: str):
        """Creates a slide with horizontal or vertical cards."""
        blank_layout = self.prs.slide_masters[0].slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        num_cards = len(cards)
        total_width = 11.8
        spacing = 0.3
        card_width = (total_width - (num_cards - 1) * spacing) / num_cards
        card_top = 1.35
        card_height = 5.5

        for i, card in enumerate(cards):
            left = 0.7 + i * (card_width + spacing)
            # Background shape
            shape = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(card_top), Inches(card_width), Inches(card_height)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = COLOR_CARD_BG
            shape.line.color.rgb = COLOR_CARD_BORDER
            shape.line.width = Pt(1.5)

            # Text frame inside card
            tf = shape.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.25)
            tf.margin_right = Inches(0.25)
            tf.margin_top = Inches(0.3)

            # Header
            p_head = tf.paragraphs[0]
            p_head.text = card.get("title", "")
            p_head.font.name = FONT_BODY
            p_head.font.size = Pt(card.get("title_size", 18))
            p_head.font.bold = True
            p_head.font.color.rgb = card.get("title_color", COLOR_NAVY)
            p_head.space_after = Pt(12)

            if "subtitle" in card:
                p_sub = tf.add_paragraph()
                p_sub.text = card["subtitle"]
                p_sub.font.name = FONT_BODY
                p_sub.font.size = Pt(13)
                p_sub.font.color.rgb = COLOR_COOL_GRAY
                p_sub.space_after = Pt(10)

            for bullet in card.get("bullets", []):
                p_b = tf.add_paragraph()
                p_b.text = "• " + bullet
                p_b.font.name = FONT_BODY
                p_b.font.size = Pt(card.get("bullet_size", 14))
                p_b.font.color.rgb = COLOR_DARK_SLATE
                p_b.space_after = Pt(8)

        self.set_speaker_notes(s, notes)
        return s

    def create_two_column_slide(self, title: str, slide_num: int, left_data: dict, right_data: dict, notes: str):
        """Creates a side-by-side two-column slide."""
        blank_layout = self.prs.slide_masters[0].slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        col_width = 5.7
        col_gap = 0.4
        col_top = 1.35
        col_height = 5.5

        for i, (left_pos, data) in enumerate([(0.7, left_data), (0.7 + col_width + col_gap, right_data)]):
            shape = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left_pos), Inches(col_top), Inches(col_width), Inches(col_height)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = COLOR_CARD_BG
            shape.line.color.rgb = data.get("border_color", COLOR_CARD_BORDER)
            shape.line.width = Pt(1.5)

            tf = shape.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.3)
            tf.margin_right = Inches(0.3)
            tf.margin_top = Inches(0.3)

            p_head = tf.paragraphs[0]
            p_head.text = data.get("title", "")
            p_head.font.name = FONT_BODY
            p_head.font.size = Pt(20)
            p_head.font.bold = True
            p_head.font.color.rgb = data.get("title_color", COLOR_NAVY)
            p_head.space_after = Pt(14)

            for bullet in data.get("bullets", []):
                p_b = tf.add_paragraph()
                p_b.text = "• " + bullet
                p_b.font.name = FONT_BODY
                p_b.font.size = Pt(15)
                p_b.font.color.rgb = COLOR_DARK_SLATE
                p_b.space_after = Pt(10)

        self.set_speaker_notes(s, notes)
        return s

    def create_row_list_slide(self, title: str, slide_num: int, rows: list[dict], notes: str):
        """Creates a slide with horizontal structured banner rows (e.g. for Outline or Pipeline)."""
        blank_layout = self.prs.slide_masters[0].slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        num_rows = len(rows)
        avail_height = 5.60
        row_top_start = 1.30
        gap = 0.16 if num_rows <= 5 else 0.10
        row_height = (avail_height - (num_rows - 1) * gap) / num_rows

        is_compact = num_rows > 5
        title_font_size = Pt(14) if is_compact else Pt(16)
        desc_font_size = Pt(12) if is_compact else Pt(13)
        margin_v = Inches(0.06) if is_compact else Inches(0.12)

        for i, row in enumerate(rows):
            top = row_top_start + i * (row_height + gap)
            shape = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(top), Inches(11.8), Inches(row_height)
            )
            shape.fill.solid()
            shape.fill.fore_color.rgb = row.get("bg_color", COLOR_CARD_BG)
            shape.line.color.rgb = row.get("border_color", COLOR_CARD_BORDER)
            shape.line.width = Pt(1.2)

            tf = shape.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.25)
            tf.margin_right = Inches(0.25)
            tf.margin_top = margin_v
            tf.margin_bottom = margin_v

            p = tf.paragraphs[0]
            # Tag / Number prefix
            run_prefix = p.add_run()
            run_prefix.text = row.get("prefix", "") + " "
            run_prefix.font.name = FONT_BODY
            run_prefix.font.size = title_font_size
            run_prefix.font.bold = True
            run_prefix.font.color.rgb = row.get("prefix_color", COLOR_BURGUNDY)

            # Main text
            run_main = p.add_run()
            run_main.text = row.get("title", "")
            run_main.font.name = FONT_BODY
            run_main.font.size = title_font_size
            run_main.font.bold = True
            run_main.font.color.rgb = COLOR_NAVY

            # Subtitle / description
            if "desc" in row:
                p_desc = tf.add_paragraph()
                p_desc.text = row["desc"]
                p_desc.font.name = FONT_BODY
                p_desc.font.size = desc_font_size
                p_desc.font.color.rgb = COLOR_DARK_SLATE

        self.set_speaker_notes(s, notes)
        return s


def build_thesis_deck(template_path: Path, output_path: Path):
    builder = DeckBuilder(template_path)

    # 1. Slide 1: Cover
    print("Building Slide 01: Cover Slide...")
    builder.create_cover_slide()

    # Clear template slide 1 and extra slides so we append fresh slides from 2 to 16
    builder.clear_slides_except_template()
    # Now remove the old slide 1 as well
    rId1 = builder.prs.slides._sldIdLst[1].rId
    builder.prs.part.drop_rel(rId1)
    del builder.prs.slides._sldIdLst[1]

    # 2. Slide 2: Outline (Bespoke to thesis problems)
    print("Building Slide 02: Outline...")
    builder.create_row_list_slide(
        title="OUTLINE",
        slide_num=2,
        rows=[
            {
                "prefix": "[Problem 1]",
                "title": "The Optical Intent Planning Bottleneck",
                "desc": "Physical-layer constraints, token saturation, and hallucinated routing in optical backbones",
            },
            {
                "prefix": "[Architecture]",
                "title": "Neurosymbolic Intent Planning Pipeline",
                "desc": "Decoupling probabilistic reasoning (NL to PDDL) from deterministic solvers and physics tools",
            },
            {
                "prefix": "[Mechanism]",
                "title": "Pre-Deployment Risk Gates: Semantic & Physical Validation",
                "desc": "Sequential fail-fast decision via Layer 1/2 semantic gate (U_sem) and GN-model QoT gate",
            },
            {
                "prefix": "[Evaluation]",
                "title": "Experimental Testbed Validation on 17-Node Optical Topology",
                "desc": "Benchmarking safety, human intervention reduction, and orchestration latency against baselines",
            },
            {
                "prefix": "[Outlook]",
                "title": "Key Takeaways, System Guarantees & Future Directions",
                "desc": "Summary of thesis contributions, operational guarantees, and extension to joint compute scheduling",
            },
        ],
        notes="""[Estimated Time]: 50s
[Key Message]: Present a thesis-specific narrative rather than a generic table of contents.
[Spoken Script]: Rather than a generic agenda, our presentation directly tracks the engineering challenges of autonomous optical networking. We begin by examining why general-purpose LLMs fail when controlling optical backbones. Next, we present our neurosymbolic architecture that cleanly separates natural language reasoning from optical physics. We then delve into the pre-deployment risk gates that protect the physical network before showing experimental validation on a 17-node optical topology and concluding with our primary takeaways.
[Bridge to Next Slide]: Let us examine the motivation behind Intent-Based Networking in optical infrastructures.""",
    )

    # 3. Slide 3: Motivation
    print("Building Slide 03: Motivation...")
    builder.create_two_column_slide(
        title="Motivation: The Vision of Intent-Based Optical Networks",
        slide_num=3,
        left_data={
            "title": "Operational Paradigm Shift",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Optical backbones carry terabits of core traffic across ROADM networks",
                "Traditional workflow: manual CLI scripts and complex RESTConf payloads",
                "Human configuration delays lightpath provisioning by hours or days",
                "Goal: Transition to autonomous Intent-Based Networking (IBN)",
                "Allow network operators to express high-level operational goals naturally",
            ],
        },
        right_data={
            "title": "The Operational Promise",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "High-level abstraction: specify WHAT is needed, not HOW to configure it",
                "Example: 'Establish a 400G lightpath between Milan and Rome avoiding L2'",
                "Autonomous translation into validated physical lightpaths",
                "Reduces human configuration error across multi-vendor optical links",
                "Critical challenge: Optical networks do not tolerate probabilistic errors",
            ],
        },
        notes="""[Estimated Time]: 55s
[Key Message]: The promise of autonomous IBN is compelling, but optical networks impose strict physical constraints.
[Spoken Script]: Optical networks form the backbone of modern telecommunications, carrying terabits of traffic across core routes. Traditionally, provisioning lightpaths requires expert network operators to manually write vendor-specific RESTConf payloads or CLI scripts. Intent-Based Networking promises to revolutionize this by allowing operators to express high-level operational goals in natural language. While this vision is promising, direct deployment of Large Language Models to optical control planes exposes critical vulnerabilities.
[Bridge to Next Slide]: Let us look at a concrete illustrative failure example to see why.""",
    )

    # 4. Slide 4: Illustrative Failure
    print("Building Slide 04: Illustrative Failure...")
    builder.create_two_column_slide(
        title="Illustrative Failure: Why Standard LLMs Break Optical Backbones",
        slide_num=4,
        left_data={
            "title": "Challenge 1: Token Budget Saturation",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "Full optical topology payloads (RESTConf JSON) exceed LLM context budgets",
                "In a 100-node core network, telemetry dumps consume tens of thousands of tokens",
                "Induces severe 'lost-in-the-middle' attention degradation",
                "Result: The LLM drops explicit user constraints such as link exclusion rules",
                "High API token cost and unpredictable prompt execution times",
            ],
        },
        right_data={
            "title": "Challenge 2: Hallucinated Physics",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "LLMs are probabilistic text predictors, not optical physics calculators",
                "Incapable of computing Generalized Signal-to-Noise Ratio (GSNR)",
                "Ignore nonlinear fiber Kerr effects and EDFA noise accumulation",
                "Result: Proposes lightpaths with unfeasible optical Quality of Transmission",
                "Causes severe traffic drop or optical controller rejection upon deployment",
            ],
        },
        notes="""[Estimated Time]: 60s
[Key Message]: Standard LLMs cannot calculate optical physics and choke on massive topology payloads.
[Spoken Script]: Consider what happens if an operator asks a standard LLM to provision a 400G demand. First, we face Token Budget Saturation: dumping full topology states with hundreds of ROADMs and EDFA amplifier parameters degrades the LLM's attention, causing it to drop explicit constraints like link exclusions. Second, and more dangerously, LLMs suffer from Hallucinated Physics. Because they predict text probabilities rather than calculating nonlinear optical impairments, they will confidently propose routes that drop light below the required GSNR threshold, leading to service disruption.
[Bridge to Next Slide]: This fundamental gap defines our formal problem statement.""",
    )

    # 5. Slide 5: Problem Statement (3 Cards: Inputs, Constraints, Objectives)
    print("Building Slide 05: Problem Statement...")
    builder.create_card_slide(
        title="Problem Statement: Inputs, Constraints & Objectives",
        slide_num=5,
        cards=[
            {
                "title": "1. Given Inputs",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "Unstructured Natural Language intent from operator",
                    "Physical topology graph G(V, E) via RESTConf",
                    "Link fiber parameters: span lengths, attenuation",
                    "EDFA amplifier gains and noise figures",
                    "Transponder specs: baud rates, modulation formats",
                ],
            },
            {
                "title": "2. Constraints",
                "title_color": COLOR_BURGUNDY,
                "bullets": [
                    "Semantic alignment: formal model matches intent",
                    "Uncertainty bounded: U_sem <= tau_sem",
                    "Optical GSNR exceeds modulation threshold",
                    "Receiver power satisfies sensitivity: P_rx >= P_min",
                    "Zero spectral overlap and wavelength collision",
                ],
            },
            {
                "title": "3. Objectives",
                "title_color": COLOR_GREEN,
                "bullets": [
                    "Zero unfeasible routes reaching controller",
                    "Fail-fast pre-deployment validation pipeline",
                    "Selective, risk-proportional HITL engagement",
                    "Sub-second deterministic computation time",
                    "Auditable planning report for network engineers",
                ],
            },
        ],
        notes="""[Estimated Time]: 60s
[Key Message]: Formally state the problem across three distinct pillars: inputs, constraints, and objectives.
[Spoken Script]: To tackle this challenge rigorously, we formalize the problem into three concrete pillars. Our system receives an unstructured operator intent, the physical topology graph G(V, E), and optical layer parameters. It must satisfy two orthogonal constraint classes: semantic consistency to prevent intent drift, and deterministic optical physics, specifically GSNR and receiver power thresholds. Our core objective is simple yet strict: ensure zero physically unfeasible configurations ever reach the network controller, while engaging the operator only when genuine ambiguity exists.
[Bridge to Next Slide]: To achieve this, we introduce our core neurosymbolic architectural philosophy.""",
    )

    # 6. Slide 6: Proposed Solution & Contributions
    print("Building Slide 06: Proposed Solution...")
    builder.create_two_column_slide(
        title="Proposed Solution: Neurosymbolic Decoupling",
        slide_num=6,
        left_data={
            "title": "Core Architectural Principle",
            "title_color": COLOR_NAVY,
            "bullets": [
                "LLMs Reason, Deterministic Tools Calculate",
                "Prohibit LLMs from performing graph routing or arithmetic",
                "Constrain the LLM strictly to formal linguistic translation",
                "Natural Language is parsed into formal PDDL constraints",
                "Path computation delegated to Yen's KSP graph algorithms",
                "Physical validation delegated to analytical GN-model engine",
            ],
        },
        right_data={
            "title": "Four Core Contributions",
            "title_color": COLOR_GREEN,
            "bullets": [
                "1. Neurosymbolic Pipeline: High-accuracy NL-to-PDDL translation",
                "2. Scoped Optical GraphRAG: k-hop neighborhood extraction",
                "3. Pre-Deployment Risk Gates: Joint U_sem and QoT validation",
                "4. Production Orchestration: LangGraph StateGraph engine",
                "Guarantees provable physical safety before configuration push",
            ],
        },
        notes="""[Estimated Time]: 55s
[Key Message]: State the thesis contributions explicitly: decoupling probabilistic reasoning from deterministic calculations.
[Spoken Script]: Our core architectural principle is: 'LLMs reason, deterministic tools calculate'. We forbid the LLM from performing math or path exploration. Instead, the LLM acts solely as a semantic translator, converting natural language into formal Planning Domain Definition Language, or PDDL. This enables our four key contributions: a neurosymbolic pipeline, a scoped Optical GraphRAG mechanism, sequential pre-deployment risk gates, and an auditable LangGraph state machine.
[Bridge to Next Slide]: Let us trace the execution of this pipeline from end to end.""",
    )

    # 7. Slide 7: End-to-End System Architecture (7 Phases)
    print("Building Slide 07: System Architecture...")
    builder.create_row_list_slide(
        title="End-to-End System Architecture & Pipeline Flow",
        slide_num=7,
        rows=[
            {"prefix": "Phase 1", "title": "Intent Ingest & Optical RAG", "desc": "Enrich operator intent with ITU-T optical grid standards and transponder modes"},
            {"prefix": "Phase 2", "title": "PDDL Intent Parsing", "desc": "Translate enriched intent into formal Planning Domain Definition Language constraints"},
            {"prefix": "Phase 3", "title": "Semantic Gate (U_sem)", "desc": "Evaluate CFG regex syntax and Reverse Prompting disagreement to catch hallucinations early"},
            {"prefix": "Phase 4", "title": "Symbolic Solver & GraphRAG", "desc": "Extract scoped k-hop subtopology and generate K-Shortest Paths via NetworkX"},
            {"prefix": "Phase 5", "title": "QoT Physics Validation", "desc": "Compute deterministic GSNR and receiver power P_rx using Python GN-model"},
            {"prefix": "Phase 6", "title": "Risk-Adaptive Decision Gate (RADG)", "desc": "Execute piecewise decision function D(U_sem, QoT_valid) -> Auto-Approve / Replan / Clarify"},
            {"prefix": "Phase 7", "title": "Plan Synthesizer", "desc": "Generate auditable planning report with verification traces and testbed deployment commands"},
        ],
        notes="""[Estimated Time]: 60s
[Key Message]: Walk through the clean 7-phase pipeline, highlighting the sequential fail-fast flow.
[Spoken Script]: Here we see the complete 7-phase execution pipeline. The operator's intent enters Phase 1 where it is enriched with optical standards. In Phase 2, the LLM generates PDDL constraints. Crucially, before running heavy graph solvers or physics tools, Phase 3 evaluates semantic uncertainty. If semantically sound, Phase 4 extracts candidate routes via symbolic graph algorithms. Phase 5 evaluates physical feasibility using a deterministic GN-model. Finally, the Risk-Adaptive Decision Gate verifies physical safety before synthesizing the final auditable report.
[Bridge to Next Slide]: Let us inspect how Phase 4 solves the token saturation problem.""",
    )

    # 8. Slide 8: Scoped GraphRAG
    print("Building Slide 08: Scoped GraphRAG...")
    builder.create_two_column_slide(
        title="Overcoming Token Saturation: Scoped Optical GraphRAG",
        slide_num=8,
        left_data={
            "title": "The Problem: Topology Bloat",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "Full topology dumps overwhelm LLM context windows",
                "Raw JSON contains excessive telemetry: ROADM ports, EDFAs, fibers",
                "Causes severe attention degradation on key operational constraints",
                "Linear increase in inference latency and financial token cost",
                "Fragile prompt structures prone to truncation and context loss",
            ],
        },
        right_data={
            "title": "Deterministic k-hop Subtopology Scoping",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Graph engine extracts only the k-hop neighborhood between endpoints",
                "Filters out irrelevant core subnets, links, and unused transponders",
                "Reduces prompt token payload by over 75%",
                "O(V + E) graph traversal executes in sub-millisecond Python code",
                "Guarantees sharp LLM attention focus on active optical constraints",
            ],
        },
        notes="""[Estimated Time]: 50s
[Key Message]: Scoped GraphRAG extracts only relevant k-hop subtopologies, eliminating attention degradation.
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with hundreds of network nodes and links, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. This reduces the prompt token footprint by over 75 percent, completely eliminating lost-in-the-middle phenomena while keeping the graph search computationally light.
[Bridge to Next Slide]: Now let us examine how we eliminate semantic drift before any physics calculations occur.""",
    )

    # 9. Slide 9: Semantic Drift & Reverse Prompting
    print("Building Slide 09: Semantic Gate...")
    builder.create_two_column_slide(
        title="Overcoming Semantic Drift: Reverse Prompting & HITL",
        slide_num=9,
        left_data={
            "title": "Two-Layer Semantic Uncertainty (U_sem)",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Layer 1 (Structural): Context-Free Grammar (CFG) regex validator",
                "Instantly rejects hallucinated predicates or malformed PDDL syntax",
                "Layer 2 (Semantic): Reverse Prompting reconstructs NL from PDDL",
                "Independent LLM judge measures semantic divergence d_sem in [0, 1]",
                "Formal metric: U_sem = 1 if syntax invalid, else U_sem = d_sem",
            ],
        },
        right_data={
            "title": "Fail-Fast HITL Clarification Loop",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "Evaluated BEFORE invoking graph solvers or physical tools",
                "If U_sem > tau_sem: Pipeline pauses via LangGraph interrupt()",
                "Prompts operator to clarify ambiguous parameters or missing nodes",
                "Eliminates infinite trial-and-error conversational loops",
                "Guarantees that downstream tools receive mathematically verified intent",
            ],
        },
        notes="""[Estimated Time]: 60s
[Key Message]: The semantic gate prevents unverified assumptions from entering downstream tools.
[Spoken Script]: To eliminate semantic drift, we introduce a dual-layer Semantic Uncertainty Gate, U_sem. First, Layer 1 validates that the PDDL adheres strictly to our domain grammar, instantly catching structural hallucinations. Second, Layer 2 performs Reverse Prompting: an independent LLM reconstructs a plain-language summary directly from the PDDL. A semantic agreement judge compares this reconstruction against the operator's original request. If uncertainty exceeds our threshold tau_sem, the orchestrator pauses immediately via a LangGraph interrupt, asking the operator for clarification before wasting compute on physics.
[Bridge to Next Slide]: Once semantic validity is established, how do we make the final pre-deployment decision?""",
    )

    # 10. Slide 10: RADG Decision Gate
    print("Building Slide 10: RADG Decision Gate...")
    builder.create_card_slide(
        title="Pre-Deployment Risk Gate: The RADG Decision Function",
        slide_num=10,
        cards=[
            {
                "title": "1. State Space & Inputs",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "Sequential pre-deployment risk evaluation",
                    "Signal 1: Semantic Uncertainty U_sem in [0, 1]",
                    "Signal 2: Binary QoT feasibility QoT_valid",
                    "Action space A = {approve, clarify, replan}",
                    "Prevents deployment of unverified network plans",
                ],
            },
            {
                "title": "2. Piecewise Formulation",
                "title_color": COLOR_BURGUNDY,
                "bullets": [
                    "D = clarify   IF U_sem > tau_sem",
                    "D = replan   IF U_sem <= tau_sem AND QoT_valid = 0",
                    "D = approve IF U_sem <= tau_sem AND QoT_valid = 1",
                    "Enforces fail-fast sequential decision tree",
                    "Physics never evaluated if semantics fail",
                ],
            },
            {
                "title": "3. Action Guarantees",
                "title_color": COLOR_GREEN,
                "bullets": [
                    "Auto-Approve: Autonomous zero-touch deployment",
                    "Suggest Replan: Prompts operator to relax constraints",
                    "Clarify: Resolves missing intent parameters early",
                    "Zero unverified configurations reach controller",
                    "Drastically cuts human operator fatigue",
                ],
            },
        ],
        notes="""[Estimated Time]: 60s
[Key Message]: The RADG function mathematically maps semantic and physical signals to optimal actions.
[Spoken Script]: The cornerstone of our pre-deployment safety is the Risk-Adaptive Decision Gate, or RADG. We formalize this as a piecewise decision function, D. If semantic uncertainty U_sem exceeds our threshold, the system triggers 'clarify'. If semantics are sound but QoT fails, the system triggers 'replan' to relax physical constraints. Only when both semantic uncertainty is low and QoT is physically valid does the system issue 'approve'. This ensures zero unverified states reach the controller while avoiding operator fatigue through selective engagement.
[Bridge to Next Slide]: Let us examine the physical calculation engine powering QoT validation.""",
    )

    # 11. Slide 11: GN-Model QoT Validation
    print("Building Slide 11: QoT Physics Validation...")
    builder.create_two_column_slide(
        title="Deterministic Physical Layer: GN-Model QoT Validation",
        slide_num=11,
        left_data={
            "title": "Gaussian Noise (GN) Physical Engine",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Pure Python implementation: zero LLM arithmetic involvement",
                "Accumulated Amplified Spontaneous Emission (ASE) noise:",
                "  P_ASE = (G - 1) * h * nu * F * B_ref",
                "Nonlinear Interference (NLI) noise power per span:",
                "  P_NLI ~ eta * P_ch^3",
                "Models fiber dispersion, Kerr nonlinearity, and EDFA noise",
            ],
        },
        right_data={
            "title": "Feasibility & Performance Criteria",
            "title_color": COLOR_GREEN,
            "bullets": [
                "Generalized Signal-to-Noise Ratio (GSNR):",
                "  GSNR = P_ch / (P_ASE + P_NLI) >= GSNR_threshold",
                "Receiver power budget check:",
                "  P_rx = P_launch - A_total + G_total >= P_rx,min",
                "Execution speed: under 5 milliseconds per candidate route",
                "100% deterministic reproducibility across physical spans",
            ],
        },
        notes="""[Estimated Time]: 55s
[Key Message]: Pure Python GN-model computes real GSNR and receiver power deterministically in milliseconds.
[Spoken Script]: In Phase 5, candidate paths produced by the symbolic solver are validated against the physical layer. We port the analytical Gaussian Noise model into pure Python. The calculator accounts for fiber attenuation, EDFA noise figures, and nonlinear self-phase modulation across each span. A path is strictly feasible only if its computed GSNR satisfies the modulation format threshold and receiver power sensitivity is met. This deterministic evaluation executes in less than 5 milliseconds, completely eliminating physical hallucination.
[Bridge to Next Slide]: Let us see how this entire system is deployed and tested.""",
    )

    # 12. Slide 12: Experimental Setup & Testbed
    print("Building Slide 12: Experimental Setup...")
    builder.create_two_column_slide(
        title="Experimental Setup & Testbed Environment",
        slide_num=12,
        left_data={
            "title": "17-Node German Core Network",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Realistic telecom benchmark: 17 ROADMs and 26 fiber links",
                "Standard Single-Mode Fiber (SMF-28): alpha = 0.2 dB/km",
                "Dispersion parameter D = 16.7 ps/(nm*km), gamma = 1.2 / (W*km)",
                "Amplified spans: dual-stage EDFAs with noise figure F = 5.5 dB",
                "Dynamic link lengths ranging from 45 km to 350 km per span",
            ],
        },
        right_data={
            "title": "Software Stack & Orchestration",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "Orchestrator: LangGraph StateGraph with memory persistence",
                "Physics Engine: Deterministic Python GN-model validator",
                "Symbolic Solver: NetworkX Yen's KSP path generation",
                "Testbed Interface: RESTConf and Mock SDON testbed adapters",
                "Evaluated LLMs: Claude 3.5 Sonnet and GPT-4o via API",
            ],
        },
        notes="""[Estimated Time]: 50s
[Key Message]: Realistic evaluation using the standard 17-node German optical topology and RESTConf testbed.
[Spoken Script]: We validate our architecture on the 17-node German backbone network, a standard benchmark in optical research consisting of 26 bidirectional fiber spans. All spans model standard SMF-28 fiber with realistic attenuation, dispersion, and EDFA noise figures. The orchestrator is implemented in Python using LangGraph, interfacing with the optical testbed via RESTConf APIs, and benchmarked using state-of-the-art LLMs as semantic translators.
[Bridge to Next Slide]: What scenarios and metrics do we use to evaluate the system?""",
    )

    # 13. Slide 13: Evaluation Framework & Benchmark Scenarios
    print("Building Slide 13: Evaluation Framework...")
    builder.create_card_slide(
        title="Evaluation Framework & Benchmark Scenarios",
        slide_num=13,
        cards=[
            {
                "title": "Comparative Baselines",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "Baseline A (LLM-Only): Direct prompt-to-JSON generation",
                    "Baseline B (Static Rule-Based): Strict regex + Always-on HITL",
                    "Proposed: Neurosymbolic RADG with sequential gates",
                ],
            },
            {
                "title": "Test Scenarios (100 Demands)",
                "title_color": COLOR_BURGUNDY,
                "bullets": [
                    "Nominal: Unambiguous requests with feasible routes",
                    "Ambiguous: Missing constraints triggering U_sem",
                    "Unfeasible: Long reaches violating GSNR thresholds",
                    "Adversarial: Prompts designed to induce hallucinations",
                ],
            },
            {
                "title": "Evaluation Metrics",
                "title_color": COLOR_GREEN,
                "bullets": [
                    "Pre-deployment safety: Unfeasible route leakage %",
                    "Operator fatigue: Human intervention reduction %",
                    "Orchestration speed: End-to-end planning latency",
                    "Solver efficiency: Graph search time vs topology scale",
                ],
            },
        ],
        notes="""[Estimated Time]: 55s
[Key Message]: Rigorous benchmarking across 100 diverse intent scenarios against LLM-only and rule-based baselines.
[Spoken Script]: Our evaluation framework tests 100 diverse intent requests across four operational categories: nominal intents, ambiguous intents with missing constraints, physically unfeasible demands, and adversarial prompts designed to induce hallucinations. We compare our neurosymbolic architecture against two baselines: an unconstrained LLM-only pipeline, and a rigid rule-based system. We measure three core dimensions: safety against unfeasible deployments, reduction in operator fatigue, and end-to-end execution latency.
[Bridge to Next Slide]: Let us analyze the key findings and trade-offs.""",
    )

    # 14. Slide 14: Key Findings & Pre-Deployment Guarantees
    print("Building Slide 14: Key Findings...")
    builder.create_two_column_slide(
        title="Key Findings & Pre-Deployment Guarantees",
        slide_num=14,
        left_data={
            "title": "Pre-Deployment Safety Guarantee",
            "title_color": COLOR_GREEN,
            "bullets": [
                "Zero physically unfeasible lightpaths reached the controller (100% safety)",
                "LLM-only baseline allowed up to 34% unfeasible routes to deploy",
                "Semantic gate caught 100% of malformed PDDL and syntax drift early",
                "Physical gate intercepted all GSNR and receiver power violations",
                "Eliminates trial-and-error reactive crash loops on live networks",
            ],
        },
        right_data={
            "title": "Operational Efficiency & Latency",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Over 70% reduction in human intervention compared to always-on HITL",
                "Operator engaged only when genuine ambiguity exists (U_sem > tau_sem)",
                "Deterministic solver and QoT evaluation execute in under 15 ms",
                "End-to-end orchestration latency averages under 2.5 s",
                "Proof that provable physical safety does not compromise speed",
            ],
        },
        notes="""[Estimated Time]: 60s
[Key Message]: 100% pre-deployment safety, 70% reduction in operator fatigue, and sub-second deterministic compute.
[Spoken Script]: The experimental results validate our core hypothesis. Most importantly, our architecture achieved a 100 percent pre-deployment safety guarantee: zero physically unfeasible or hallucinated configurations ever reached the network controller. In contrast, the unconstrained LLM baseline allowed up to 34 percent invalid routes. Furthermore, by evaluating semantic uncertainty early, we reduced human operator interventions by over 70 percent compared to always-on review. Finally, our deterministic physics engine executed in under 15 milliseconds, proving that safety does not compromise speed.
[Bridge to Next Slide]: Let us summarize the primary conclusions of this thesis.""",
    )

    # 15. Slide 15: Conclusions & Main Takeaways
    print("Building Slide 15: Conclusions...")
    builder.create_card_slide(
        title="Conclusions & Main Takeaways",
        slide_num=15,
        cards=[
            {
                "title": "1. Decoupling is Essential",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "LLMs must reason, tools must calculate",
                    "Language models excel at PDDL semantic parsing",
                    "Optical physics must remain 100% deterministic",
                ],
            },
            {
                "title": "2. Sequential Risk Gates",
                "title_color": COLOR_BURGUNDY,
                "bullets": [
                    "Early semantic evaluation (U_sem) halts drift early",
                    "Downstream GN-model ensures optical viability",
                    "Guarantees 100% pre-deployment safety",
                ],
            },
            {
                "title": "3. Selective HITL Value",
                "title_color": COLOR_GREEN,
                "bullets": [
                    "Engaging humans proportionally to risk cuts fatigue by 70%",
                    "Preserves operator trust through auditable reports",
                    "Enables scalable autonomous optical operations",
                ],
            },
            {
                "title": "4. Production Ready",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "LangGraph orchestrator tested on 17-node topology",
                    "Sub-second deterministic compute time",
                    "Extensible architecture for next-gen SDN",
                ],
            },
        ],
        notes="""[Estimated Time]: 55s
[Key Message]: Summarize the four core engineering takeaways of the thesis.
[Spoken Script]: In conclusion, this thesis demonstrates that neurosymbolic decoupling is essential for deploying AI in optical networks. By restricting the LLM to formal PDDL translation and delegating physics and routing to deterministic tools, we eliminate hallucination. Our sequential risk gates ensure that semantic uncertainty is caught early and physical feasibility is guaranteed before deployment. This achieves the dual goal of operational safety and minimal operator fatigue.
[Bridge to Next Slide]: Finally, let us review future research avenues and conclude.""",
    )

    # 16. Slide 16: Future Outlook & Acknowledgments
    print("Building Slide 16: Future Outlook...")
    builder.create_two_column_slide(
        title="Future Outlook & Acknowledgments",
        slide_num=16,
        left_data={
            "title": "Future Research Directions",
            "title_color": COLOR_NAVY,
            "bullets": [
                "Joint Optical & Compute Scheduling: Co-scheduling optical paths with GPU jobs",
                "Multi-Band Optical Systems: Expanding GN-model to C+L band non-linearities",
                "Real-Time Telemetry Integration: Online closed-loop self-healing via telemetry",
                "Reinforcement Learning: Fine-tuning PDDL translations from operator feedback",
            ],
        },
        right_data={
            "title": "Acknowledgments & Discussion",
            "title_color": COLOR_BURGUNDY,
            "bullets": [
                "Sincere thanks to Prof. Massimo Tornatore for his guidance and leadership",
                "Gratitude to the SDON Laboratory research group at Politecnico di Milano",
                "Thank you for your attention",
                "Open for questions and technical discussion",
            ],
        },
        notes="""[Estimated Time]: 45s
[Key Message]: Thank the committee, outline future research directions (joint compute scheduling), and open Q&A.
[Spoken Script]: Looking forward, our immediate next step is extending this PDDL framework to joint routing and compute scheduling, coordinating optical lightpaths with distributed data center GPU workloads. I want to express my deepest gratitude to Professor Tornatore and my colleagues in the SDON laboratory for their invaluable guidance throughout this research. Thank you very much for your time and attention. I am now open to your questions.""",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    builder.prs.save(str(output_path))
    print(f"\n✓ Presentation successfully generated: {output_path} ({len(builder.prs.slides)} slides)")


def main():
    template = Path("docs/LLM_Wiki/raw/ACP_MinPowCons_v5.pptx")
    output = Path("presentations/thesis_defense/thesis_defense.pptx")

    if not template.exists():
        print(f"Error: Template not found at {template}", file=sys.stderr)
        sys.exit(1)

    build_thesis_deck(template, output)


if __name__ == "__main__":
    main()
