#!/usr/bin/env python3
# type: ignore
# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
"""
Master's Thesis Defense Slide Deck Builder.
Generates a 16-slide publication-quality presentation in PowerPoint (.pptx)
using the official Politecnico di Milano template, adhering strictly to
Prof. Massimo Tornatore's 15 Golden Rules, with native OMML equations,
rich DrawingML diagram flows, visual cards, and standardized figure placeholders.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.oxml import parse_xml

# --- Institutional Color Palette ---
COLOR_NAVY = RGBColor(15, 44, 83)           # #0F2C53 - Primary brand headers & titles
COLOR_BURGUNDY = RGBColor(133, 32, 12)      # #85200C - Cover title accent, alert callouts
COLOR_DARK_SLATE = RGBColor(34, 34, 34)     # #222222 - Primary body text
COLOR_COOL_GRAY = RGBColor(90, 107, 130)    # #5A6B82 - Subtitles and secondary notes
COLOR_CARD_BG = RGBColor(244, 246, 249)     # #F4F6F9 - Card container fill
COLOR_CARD_BORDER = RGBColor(208, 215, 222) # #D0D7DE - Card border
COLOR_GREEN = RGBColor(26, 127, 55)         # #1A7F37 - Feasible / Success / Auto-Approve
COLOR_AMBER = RGBColor(176, 125, 0)         # #B07D00 - Semantic Gate / Clarify / Warning
COLOR_RED = RGBColor(207, 34, 46)           # #CF222E - Violation / Replan / Failure
COLOR_WHITE = RGBColor(255, 255, 255)       # #FFFFFF - Clean white

FONT_TITLE = "Titillium Web SemiBold"
FONT_BODY = "Arial"


def add_omml_equation(paragraph, omml_xml: str):
    """
    Injects native Office Math (OMML) XML into a DrawingML paragraph.
    PowerPoint renders this natively in Cambria Math with fractions,
    subscripts, superscripts, and piecewise curly braces.
    """
    full_xml = (
        f'<a14:m xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" '
        f'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<m:oMathPara><m:oMath>{omml_xml}</m:oMath></m:oMathPara></a14:m>'
    )
    elem = parse_xml(full_xml)
    paragraph._p.append(elem)


class DeckBuilder:
    def __init__(self, template_path: Path):
        self.prs = Presentation(str(template_path))
        if len(self.prs.slides) < 2:
            raise ValueError("Template must contain at least 2 slides (cover and content base).")
        
        self.raw_cover = self.prs.slides[0]
        self.raw_content = self.prs.slides[1]

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
        p.font.color.rgb = COLOR_WHITE
        p.alignment = PP_ALIGN.RIGHT

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(0.4), Inches(7.15), Inches(1.5), Inches(0.3))
        p_num = num_box.text_frame.paragraphs[0]
        p_num.text = str(slide_num)
        p_num.font.name = "Arial"
        p_num.font.size = Pt(11)
        p_num.font.color.rgb = COLOR_WHITE

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

    def create_placeholder_box(self, slide, left, top, width, height, title: str, subtitle: str):
        """Creates a styled native figure placeholder with dashed border and icon."""
        ph = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        ph.fill.solid()
        ph.fill.fore_color.rgb = COLOR_CARD_BG
        ph.line.color.rgb = COLOR_COOL_GRAY
        ph.line.width = Pt(1.5)
        ph.line.dash_style = MSO_LINE_DASH_STYLE.DASH

        tf = ph.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.3)

        p_icon = tf.paragraphs[0]
        p_icon.text = "📊"
        p_icon.font.name = "Segoe UI Emoji"
        p_icon.font.size = Pt(32)
        p_icon.alignment = PP_ALIGN.CENTER

        p_title = tf.add_paragraph()
        p_title.text = title
        p_title.font.name = FONT_TITLE
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_NAVY
        p_title.alignment = PP_ALIGN.CENTER

        p_sub = tf.add_paragraph()
        p_sub.text = subtitle
        p_sub.font.name = FONT_BODY
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = COLOR_COOL_GRAY
        p_sub.alignment = PP_ALIGN.CENTER
        return ph

    def create_cover_slide(self):
        """Customizes Slide 1 as the Cover Slide."""
        s = self.prs.slides[0]
        shapes_to_remove = []
        for shape in s.shapes:
            if shape.name == "Picture 2":
                shapes_to_remove.append(shape)
            elif shape.has_text_frame:
                if shape.name == "Google Shape;60;p13":
                    shape.text_frame.text = "September 2026"
                    for p in shape.text_frame.paragraphs:
                        p.font.name = "Arial"
                        p.font.size = Pt(14)
                        p.font.bold = True
                        p.font.color.rgb = COLOR_WHITE
                        p.alignment = PP_ALIGN.CENTER
                elif shape.name in ["Google Shape;54;p13", "Google Shape;59;p13"]:
                    shape.text_frame.text = ""

        for sh in shapes_to_remove:
            sp = sh._element
            sp.getparent().remove(sp)

        # Main Title Box
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
        p2.font.size = Pt(18)
        p2.font.color.rgb = COLOR_NAVY
        p2.alignment = PP_ALIGN.CENTER

        # Metadata Card
        meta_box = s.shapes.add_textbox(Inches(2.5), Inches(4.3), Inches(8.3), Inches(2.2))
        tf_meta = meta_box.text_frame
        tf_meta.word_wrap = True

        p_cand = tf_meta.paragraphs[0]
        p_cand.text = "Candidate: Felipe Abadía"
        p_cand.font.name = "Arial"
        p_cand.font.size = Pt(16)
        p_cand.font.bold = True
        p_cand.font.color.rgb = COLOR_DARK_SLATE
        p_cand.alignment = PP_ALIGN.CENTER

        p_adv = tf_meta.add_paragraph()
        p_adv.text = "Academic Advisor: Prof. Massimo Tornatore"
        p_adv.font.name = "Arial"
        p_adv.font.size = Pt(15)
        p_adv.font.bold = True
        p_adv.font.color.rgb = COLOR_NAVY
        p_adv.alignment = PP_ALIGN.CENTER

        p_dept = tf_meta.add_paragraph()
        p_dept.text = "Dipartimento di Elettronica, Informazione e Bioingegneria — Politecnico di Milano"
        p_dept.font.name = "Arial"
        p_dept.font.size = Pt(13)
        p_dept.font.color.rgb = COLOR_COOL_GRAY
        p_dept.alignment = PP_ALIGN.CENTER

        self.set_speaker_notes(
            s,
            """[Estimated Time]: 30s
[Key Message]: Welcome the committee and introduce the thesis title and research focus.
[Spoken Script]: Good morning members of the committee and Professor Tornatore. Today I present my Master's thesis entitled "Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment". In this work, we address the challenge of bridging high-level operator intent with physical optical layer realities using a robust, fail-fast neurosymbolic architecture.
[Bridge to Next Slide]: Let us begin with the specific roadmap of problems and solutions covered in this presentation.""",
        )

    def create_row_list_slide(self, title: str, slide_num: int, rows: list[dict], notes: str):
        """Creates an Outline / Progress slide with clean connected progression banners."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        num_rows = len(rows)
        top_start = Inches(1.3)
        available_height = Inches(5.6)
        row_gap = Inches(0.16)
        row_height = (available_height - (num_rows - 1) * row_gap) / num_rows

        for i, row in enumerate(rows):
            cur_top = top_start + i * (row_height + row_gap)

            # Container Box
            card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, Inches(11.7), row_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            card.line.color.rgb = COLOR_CARD_BORDER
            card.line.width = Pt(1)

            # Left Badge Container
            badge_width = Inches(2.2)
            badge = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), cur_top, badge_width, row_height
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = COLOR_NAVY
            badge.line.fill.background()

            tf_b = badge.text_frame
            tf_b.word_wrap = True
            tf_b.margin_left = Inches(0.1)
            tf_b.margin_right = Inches(0.1)
            tf_b.margin_top = Inches(0.12)
            p_b = tf_b.paragraphs[0]
            p_b.text = row.get("prefix", f"[{i+1}]")
            p_b.font.name = FONT_TITLE
            p_b.font.size = Pt(13)
            p_b.font.bold = True
            p_b.font.color.rgb = COLOR_WHITE
            p_b.alignment = PP_ALIGN.CENTER

            # Text content inside card
            text_box = s.shapes.add_textbox(
                Inches(3.15), cur_top, Inches(9.2), row_height
            )
            tf = text_box.text_frame
            tf.word_wrap = True
            tf.margin_top = Inches(0.1)
            tf.margin_bottom = Inches(0.05)

            p_title = tf.paragraphs[0]
            p_title.text = row["title"]
            p_title.font.name = FONT_TITLE
            p_title.font.size = Pt(15)
            p_title.font.bold = True
            p_title.font.color.rgb = COLOR_NAVY

            p_desc = tf.add_paragraph()
            p_desc.text = row["desc"]
            p_desc.font.name = FONT_BODY
            p_desc.font.size = Pt(12)
            p_desc.font.color.rgb = COLOR_DARK_SLATE

        self.set_speaker_notes(s, notes)
        return s

    def create_two_column_slide(
        self,
        title: str,
        slide_num: int,
        left_data: dict,
        right_data: dict,
        notes: str,
        bottom_banner: str | None = None,
    ):
        """Creates a side-by-side comparative card slide with optional bottom flow banner."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        col_width = Inches(5.7)
        top_pos = Inches(1.3)
        col_height = Inches(4.7) if bottom_banner else Inches(5.4)

        for i, (col_left, data) in enumerate(
            [(Inches(0.75), left_data), (Inches(6.8), right_data)]
        ):
            card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, col_left, top_pos, col_width, col_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            border_color = data.get("border_color", COLOR_CARD_BORDER)
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)

            # Header Banner inside card
            header_height = Inches(0.65)
            header_bar = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, col_left, top_pos, col_width, header_height
            )
            header_bar.fill.solid()
            header_bar.fill.fore_color.rgb = data.get("title_color", COLOR_NAVY)
            header_bar.line.fill.background()

            tf_h = header_bar.text_frame
            tf_h.word_wrap = True
            p_h = tf_h.paragraphs[0]
            icon = data.get("icon", "")
            p_h.text = f"{icon} {data['title']}".strip()
            p_h.font.name = FONT_TITLE
            p_h.font.size = Pt(16)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_WHITE
            p_h.alignment = PP_ALIGN.CENTER

            # Body Bullets
            body_box = s.shapes.add_textbox(
                col_left + Inches(0.2),
                top_pos + header_height + Inches(0.15),
                col_width - Inches(0.4),
                col_height - header_height - Inches(0.3),
            )
            tf_b = body_box.text_frame
            tf_b.word_wrap = True
            tf_b.margin_top = Inches(0.05)

            bullets = data.get("bullets", [])
            for j, b_text in enumerate(bullets):
                p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                p.text = f"•  {b_text}"
                p.font.name = FONT_BODY
                p.font.size = Pt(13)
                p.font.color.rgb = COLOR_DARK_SLATE
                p.space_after = Pt(8)

        if bottom_banner:
            banner_box = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(6.2), Inches(11.75), Inches(0.65)
            )
            banner_box.fill.solid()
            banner_box.fill.fore_color.rgb = COLOR_CARD_BG
            banner_box.line.color.rgb = COLOR_NAVY
            banner_box.line.width = Pt(1.5)

            tf_bb = banner_box.text_frame
            p_bb = tf_bb.paragraphs[0]
            p_bb.text = bottom_banner
            p_bb.font.name = FONT_TITLE
            p_bb.font.size = Pt(13)
            p_bb.font.bold = True
            p_bb.font.color.rgb = COLOR_NAVY
            p_bb.alignment = PP_ALIGN.CENTER

        self.set_speaker_notes(s, notes)
        return s

    def create_card_slide(
        self, title: str, slide_num: int, cards: list[dict], notes: str, formulas: dict | None = None
    ):
        """Creates a multi-pillar card slide (3 or 4 cards) with optional native OMML formulas."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        num_cards = len(cards)
        total_width = Inches(11.8)
        left_margin = Inches(0.75)
        top_pos = Inches(1.3)
        card_height = Inches(5.5)

        gap = Inches(0.25)
        card_width = (total_width - (num_cards - 1) * gap) / num_cards

        for i, card_data in enumerate(cards):
            card_left = left_margin + i * (card_width + gap)

            card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, card_left, top_pos, card_width, card_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            border_col = card_data.get("title_color", COLOR_NAVY)
            card.line.color.rgb = border_col
            card.line.width = Pt(1.5)

            # Header Bar
            header_h = Inches(0.65)
            header_bar = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, card_left, top_pos, card_width, header_h
            )
            header_bar.fill.solid()
            header_bar.fill.fore_color.rgb = border_col
            header_bar.line.fill.background()

            tf_h = header_bar.text_frame
            p_h = tf_h.paragraphs[0]
            icon = card_data.get("icon", "")
            p_h.text = f"{icon} {card_data['title']}".strip()
            p_h.font.name = FONT_TITLE
            p_h.font.size = Pt(14)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_WHITE
            p_h.alignment = PP_ALIGN.CENTER

            # Body Bullets
            body_box = s.shapes.add_textbox(
                card_left + Inches(0.15),
                top_pos + header_h + Inches(0.15),
                card_width - Inches(0.3),
                card_height - header_h - Inches(0.3),
            )
            tf_b = body_box.text_frame
            tf_b.word_wrap = True
            tf_b.margin_top = Inches(0.05)

            for j, b_text in enumerate(card_data.get("bullets", [])):
                p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
                p.text = f"•  {b_text}"
                p.font.name = FONT_BODY
                p.font.size = Pt(12)
                p.font.color.rgb = COLOR_DARK_SLATE
                p.space_after = Pt(6)

            # Inject OMML formula if card requests one
            if formulas and i in formulas:
                f_info = formulas[i]
                p_f_lbl = tf_b.add_paragraph()
                p_f_lbl.text = "Formulation:"
                p_f_lbl.font.name = FONT_TITLE
                p_f_lbl.font.size = Pt(11)
                p_f_lbl.font.bold = True
                p_f_lbl.font.color.rgb = border_col

                for f_xml in f_info.get("omml_list", []):
                    p_eq = tf_b.add_paragraph()
                    add_omml_equation(p_eq, f_xml)

        self.set_speaker_notes(s, notes)
        return s

    def create_pipeline_flow_slide(self, title: str, slide_num: int, phases: list[dict], notes: str):
        """Creates the End-to-End 7-Phase horizontal pipeline diagram with connected step chevrons."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        num_phases = len(phases)
        total_width = Inches(11.9)
        left_margin = Inches(0.7)
        top_pos = Inches(1.35)
        phase_height = Inches(4.2)
        arrow_width = Inches(0.2)
        gap = (total_width - (num_phases * Inches(1.45) + (num_phases - 1) * arrow_width)) / (num_phases - 1)
        phase_width = Inches(1.45)

        for i, phase in enumerate(phases):
            cur_left = left_margin + i * (phase_width + arrow_width + gap)

            # Card Container
            card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, phase_width, phase_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            is_gate = phase.get("is_gate", False)
            border_color = COLOR_AMBER if is_gate and "Semantic" in phase["title"] else (
                COLOR_BURGUNDY if is_gate else COLOR_CARD_BORDER
            )
            card.line.color.rgb = border_color
            card.line.width = Pt(2.0 if is_gate else 1.0)

            # Top Step Badge
            badge_h = Inches(0.55)
            badge = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, cur_left, top_pos, phase_width, badge_h
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = border_color if is_gate else COLOR_NAVY
            badge.line.fill.background()

            tf_badge = badge.text_frame
            p_b = tf_badge.paragraphs[0]
            p_b.text = f"Phase {i+1}"
            p_b.font.name = FONT_TITLE
            p_b.font.size = Pt(12)
            p_b.font.bold = True
            p_b.font.color.rgb = COLOR_WHITE
            p_b.alignment = PP_ALIGN.CENTER

            # Body Text inside phase card
            tf_body = card.text_frame
            tf_body.word_wrap = True
            tf_body.margin_top = Inches(0.65)
            tf_body.margin_left = Inches(0.08)
            tf_body.margin_right = Inches(0.08)

            p_t = tf_body.paragraphs[0]
            p_t.text = phase["title"]
            p_t.font.name = FONT_TITLE
            p_t.font.size = Pt(11)
            p_t.font.bold = True
            p_t.font.color.rgb = border_color if is_gate else COLOR_NAVY
            p_t.alignment = PP_ALIGN.CENTER

            if is_gate:
                p_gate_tag = tf_body.add_paragraph()
                p_gate_tag.text = "[RISK GATE]"
                p_gate_tag.font.name = FONT_TITLE
                p_gate_tag.font.size = Pt(9)
                p_gate_tag.font.bold = True
                p_gate_tag.font.color.rgb = border_color
                p_gate_tag.alignment = PP_ALIGN.CENTER

            p_d = tf_body.add_paragraph()
            p_d.text = phase["desc"]
            p_d.font.name = FONT_BODY
            p_d.font.size = Pt(10)
            p_d.font.color.rgb = COLOR_DARK_SLATE
            p_d.alignment = PP_ALIGN.LEFT
            p_d.space_before = Pt(4)

            # Connector Arrow
            if i < num_phases - 1:
                arrow_left = cur_left + phase_width + gap / 2
                arrow = s.shapes.add_shape(
                    MSO_SHAPE.RIGHT_ARROW, arrow_left, top_pos + Inches(1.8), arrow_width, Inches(0.25)
                )
                arrow.fill.solid()
                arrow.fill.fore_color.rgb = COLOR_NAVY
                arrow.line.fill.background()

        # Bottom Feedback Loop Callout Banners
        loop1 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(5.85), Inches(5.7), Inches(0.95)
        )
        loop1.fill.solid()
        loop1.fill.fore_color.rgb = COLOR_CARD_BG
        loop1.line.color.rgb = COLOR_AMBER
        loop1.line.width = Pt(1.5)
        tf_l1 = loop1.text_frame
        tf_l1.word_wrap = True
        p_l1 = tf_l1.paragraphs[0]
        p_l1.text = "⏸️ Phase 3b: Clarify Loop (LangGraph interrupt())"
        p_l1.font.name = FONT_TITLE
        p_l1.font.size = Pt(12)
        p_l1.font.bold = True
        p_l1.font.color.rgb = COLOR_AMBER
        p_l1_sub = tf_l1.add_paragraph()
        p_l1_sub.text = "If U_sem > tau_sem: Pauses execution and prompts operator for intent disambiguation"
        p_l1_sub.font.name = FONT_BODY
        p_l1_sub.font.size = Pt(10)
        p_l1_sub.font.color.rgb = COLOR_DARK_SLATE

        loop2 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(5.85), Inches(5.7), Inches(0.95)
        )
        loop2.fill.solid()
        loop2.fill.fore_color.rgb = COLOR_CARD_BG
        loop2.line.color.rgb = COLOR_BURGUNDY
        loop2.line.width = Pt(1.5)
        tf_l2 = loop2.text_frame
        tf_l2.word_wrap = True
        p_l2 = tf_l2.paragraphs[0]
        p_l2.text = "↺ Phase 6: Suggest Replan Loop (Physics Unfeasible)"
        p_l2.font.name = FONT_TITLE
        p_l2.font.size = Pt(12)
        p_l2.font.bold = True
        p_l2.font.color.rgb = COLOR_BURGUNDY
        p_l2_sub = tf_l2.add_paragraph()
        p_l2_sub.text = "If QoT_valid = 0: Suggests operator to relax constraints (lower baud rate, alternate link)"
        p_l2_sub.font.name = FONT_BODY
        p_l2_sub.font.size = Pt(10)
        p_l2_sub.font.color.rgb = COLOR_DARK_SLATE

        self.set_speaker_notes(s, notes)
        return s

    def create_decision_tree_slide(
        self, title: str, slide_num: int, formula_xml: str, branches: list[dict], notes: str
    ):
        """Creates the Pre-Deployment RADG Decision Gate slide with native OMML and outcome branches."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        # Top Container: Native OMML Piecewise Formula
        top_card = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.3), Inches(11.8), Inches(2.2)
        )
        top_card.fill.solid()
        top_card.fill.fore_color.rgb = COLOR_CARD_BG
        top_card.line.color.rgb = COLOR_NAVY
        top_card.line.width = Pt(1.5)

        top_box = s.shapes.add_textbox(
            Inches(0.95), Inches(1.4), Inches(11.4), Inches(2.0)
        )
        tf_top = top_box.text_frame
        tf_top.word_wrap = True

        p_hdr = tf_top.paragraphs[0]
        p_hdr.text = "Piecewise Decision Formulation D(U_sem, QoT_valid):"
        p_hdr.font.name = FONT_TITLE
        p_hdr.font.size = Pt(14)
        p_hdr.font.bold = True
        p_hdr.font.color.rgb = COLOR_NAVY

        # Inject piecewise equation
        p_eq = tf_top.add_paragraph()
        p_eq.alignment = PP_ALIGN.CENTER
        add_omml_equation(p_eq, formula_xml)

        # Bottom Section: 3 Outcome Branch Cards
        num_branches = len(branches)
        gap = Inches(0.25)
        total_w = Inches(11.8)
        b_width = (total_w - (num_branches - 1) * gap) / num_branches
        b_top = Inches(3.75)
        b_height = Inches(3.0)

        for i, branch in enumerate(branches):
            b_left = Inches(0.75) + i * (b_width + gap)

            b_card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, b_left, b_top, b_width, b_height
            )
            b_card.fill.solid()
            b_card.fill.fore_color.rgb = COLOR_CARD_BG
            b_color = branch.get("color", COLOR_NAVY)
            b_card.line.color.rgb = b_color
            b_card.line.width = Pt(2.0)

            # Header Bar
            h_bar = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, b_left, b_top, b_width, Inches(0.65)
            )
            h_bar.fill.solid()
            h_bar.fill.fore_color.rgb = b_color
            h_bar.line.fill.background()

            tf_bh = h_bar.text_frame
            p_bh = tf_bh.paragraphs[0]
            p_bh.text = f"{branch.get('icon', '')} {branch['action']}"
            p_bh.font.name = FONT_TITLE
            p_bh.font.size = Pt(15)
            p_bh.font.bold = True
            p_bh.font.color.rgb = COLOR_WHITE
            p_bh.alignment = PP_ALIGN.CENTER

            # Body text inside transparent textbox
            b_body_box = s.shapes.add_textbox(
                b_left + Inches(0.15),
                b_top + Inches(0.65) + Inches(0.1),
                b_width - Inches(0.3),
                b_height - Inches(0.75),
            )
            tf_bbody = b_body_box.text_frame
            tf_bbody.word_wrap = True

            p_cond = tf_bbody.paragraphs[0]
            p_cond.text = f"Condition: {branch['condition']}"
            p_cond.font.name = FONT_TITLE
            p_cond.font.size = Pt(12)
            p_cond.font.bold = True
            p_cond.font.color.rgb = b_color
            p_cond.space_after = Pt(6)

            for item in branch.get("bullets", []):
                p_it = tf_bbody.add_paragraph()
                p_it.text = f"•  {item}"
                p_it.font.name = FONT_BODY
                p_it.font.size = Pt(11)
                p_it.font.color.rgb = COLOR_DARK_SLATE
                p_it.space_after = Pt(4)

        self.set_speaker_notes(s, notes)
        return s

    def create_kpi_and_placeholder_slide(
        self,
        title: str,
        slide_num: int,
        kpis: list[dict],
        placeholder_info: dict,
        notes: str,
    ):
        """Creates the Key Findings slide featuring 3 KPI Stat Banners and an Empirical Results Placeholder."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        # Left Column: 3 KPI Banners
        left_pos = Inches(0.75)
        left_width = Inches(5.3)
        top_start = Inches(1.3)
        kpi_height = Inches(1.65)
        gap = Inches(0.2)

        for i, kpi in enumerate(kpis):
            cur_top = top_start + i * (kpi_height + gap)

            card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, cur_top, left_width, kpi_height
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            card.line.color.rgb = kpi.get("border_color", COLOR_CARD_BORDER)
            card.line.width = Pt(1.5)

            tf = card.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.2)
            tf.margin_top = Inches(0.15)

            p_val = tf.paragraphs[0]
            p_val.text = kpi["value"]
            p_val.font.name = FONT_TITLE
            p_val.font.size = Pt(32)
            p_val.font.bold = True
            p_val.font.color.rgb = kpi.get("color", COLOR_GREEN)

            p_lbl = tf.add_paragraph()
            p_lbl.text = kpi["label"]
            p_lbl.font.name = FONT_TITLE
            p_lbl.font.size = Pt(13)
            p_lbl.font.bold = True
            p_lbl.font.color.rgb = COLOR_NAVY

            p_sub = tf.add_paragraph()
            p_sub.text = kpi["subtitle"]
            p_sub.font.name = FONT_BODY
            p_sub.font.size = Pt(10)
            p_sub.font.color.rgb = COLOR_DARK_SLATE

        # Right Column: Empirical Figure Placeholder
        right_pos = Inches(6.3)
        right_width = Inches(6.25)
        right_height = Inches(5.35)

        self.create_placeholder_box(
            s,
            right_pos,
            top_start,
            right_width,
            right_height,
            placeholder_info["title"],
            placeholder_info["subtitle"],
        )

        self.set_speaker_notes(s, notes)
        return s

    def create_split_diagram_slide(
        self,
        title: str,
        slide_num: int,
        content_data: dict,
        placeholder_info: dict,
        notes: str,
    ):
        """Creates a split slide with structured text cards on the left and a diagram/figure placeholder on the right."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        left_pos = Inches(0.75)
        left_width = Inches(5.6)
        top_pos = Inches(1.3)
        content_height = Inches(5.35)

        # Left Container Card
        card = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, left_width, content_height
        )
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = content_data.get("border_color", COLOR_NAVY)
        card.line.width = Pt(1.5)

        # Header Bar
        header_h = Inches(0.65)
        header_bar = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, top_pos, left_width, header_h
        )
        header_bar.fill.solid()
        header_bar.fill.fore_color.rgb = content_data.get("title_color", COLOR_NAVY)
        header_bar.line.fill.background()

        tf_h = header_bar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.text = f"{content_data.get('icon', '')} {content_data['title']}".strip()
        p_h.font.name = FONT_TITLE
        p_h.font.size = Pt(15)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_h.alignment = PP_ALIGN.CENTER

        # Body Text inside transparent textbox
        body_box = s.shapes.add_textbox(
            left_pos + Inches(0.2),
            top_pos + header_h + Inches(0.1),
            left_width - Inches(0.4),
            content_height - header_h - Inches(0.2),
        )
        tf_b = body_box.text_frame
        tf_b.word_wrap = True

        for j, b_text in enumerate(content_data.get("bullets", [])):
            p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
            p.text = f"•  {b_text}"
            p.font.name = FONT_BODY
            p.font.size = Pt(12)
            p.font.color.rgb = COLOR_DARK_SLATE
            p.space_after = Pt(8)

        # Right Column Placeholder
        right_pos = Inches(6.65)
        right_width = Inches(5.9)

        self.create_placeholder_box(
            s,
            right_pos,
            top_pos,
            right_width,
            content_height,
            placeholder_info["title"],
            placeholder_info["subtitle"],
        )

        self.set_speaker_notes(s, notes)
        return s


def build_thesis_defense_deck():
    template = Path("docs/LLM_Wiki/raw/ACP_MinPowCons_v5.pptx")
    if not template.exists():
        raise FileNotFoundError(f"Template not found at {template}")

    builder = DeckBuilder(template)

    # 1. Slide 1: Cover Slide
    print("Building Slide 01: Cover Slide...")
    builder.create_cover_slide()

    # Clear template slide 1 and extra slides so we append fresh slides from 2 to 16
    builder.clear_slides_except_template()
    rId1 = builder.prs.slides._sldIdLst[1].rId
    builder.prs.part.drop_rel(rId1)
    del builder.prs.slides._sldIdLst[1]

    # 2. Slide 2: Outline
    print("Building Slide 02: Outline...")
    builder.create_row_list_slide(
        title="OUTLINE",
        slide_num=2,
        rows=[
            {
                "prefix": "[01] Bottleneck",
                "title": "The Optical Intent Planning Bottleneck",
                "desc": "Physical-layer constraints, token saturation, and hallucinated routing in optical backbones",
            },
            {
                "prefix": "[02] Architecture",
                "title": "Neurosymbolic Intent Planning Pipeline",
                "desc": "Decoupling probabilistic reasoning (NL to PDDL) from deterministic solvers and physics tools",
            },
            {
                "prefix": "[03] Risk Gates",
                "title": "Pre-Deployment Risk Gates: Semantic & Physical Validation",
                "desc": "Sequential fail-fast decision via Layer 1/2 semantic gate (U_sem) and GN-model QoT gate",
            },
            {
                "prefix": "[04] Evaluation",
                "title": "Experimental Testbed Validation on 17-Node Optical Topology",
                "desc": "Benchmarking safety, human intervention reduction, and orchestration latency against baselines",
            },
            {
                "prefix": "[05] Outlook",
                "title": "Key Takeaways, System Guarantees & Future Directions",
                "desc": "Summary of thesis contributions, operational guarantees, and extension to joint compute scheduling",
            },
        ],
        notes="""[Estimated Time]: 50s
[Key Message]: Establish a thesis-specific narrative instead of a generic agenda.
[Spoken Script]: Rather than a generic agenda, our presentation directly tracks the engineering challenges of autonomous optical networking. We begin by examining why general-purpose LLMs fail when controlling optical backbones. Next, we present our neurosymbolic architecture that cleanly separates natural language reasoning from optical physics. We then delve into the pre-deployment risk gates that protect the physical network before showing experimental validation on a 17-node optical topology and concluding with our primary takeaways.
[Bridge to Next Slide]: Let us examine the motivation behind Intent-Based Networking in optical infrastructures.""",
    )

    # 3. Slide 3: Motivation
    print("Building Slide 03: Motivation...")
    builder.create_two_column_slide(
        title="Motivation: The Vision of Intent-Based Optical Networks",
        slide_num=3,
        left_data={
            "icon": "⚠️",
            "title": "Operational Shift: Manual Bottleneck",
            "title_color": COLOR_BURGUNDY,
            "border_color": COLOR_BURGUNDY,
            "bullets": [
                "Optical backbones carry terabits of core traffic across ROADM networks",
                "Traditional workflow: manual CLI scripts and complex RESTConf payloads",
                "Human configuration delays lightpath provisioning by hours or days",
                "Prone to fatal human operator errors across multi-vendor optical links",
                "Goal: Transition to autonomous Intent-Based Networking (IBN)",
            ],
        },
        right_data={
            "icon": "⚡",
            "title": "Operational Promise: Autonomous Vision",
            "title_color": COLOR_NAVY,
            "border_color": COLOR_NAVY,
            "bullets": [
                "High-level abstraction: specify WHAT is needed, not HOW to configure it",
                "Example: 'Establish a 400G lightpath between Milan and Rome avoiding L2'",
                "Autonomous translation into validated physical lightpaths in seconds",
                "Reduces human configuration error across multi-vendor optical links",
                "Critical challenge: Optical networks do not tolerate probabilistic errors",
            ],
        },
        bottom_banner="Operational Flow:  [Operator NL Intent]  ➔  [AI Intent Orchestrator]  ➔  [Zero-Error Physical Lightpath]",
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
            "icon": "⚠️",
            "title": "Challenge 1: Token Budget Saturation",
            "title_color": COLOR_BURGUNDY,
            "border_color": COLOR_BURGUNDY,
            "bullets": [
                "Full optical topology payloads (RESTConf JSON) exceed LLM context budgets",
                "In a 100-node core network, telemetry dumps consume tens of thousands of tokens",
                "Induces severe 'lost-in-the-middle' attention degradation",
                "Result: The LLM drops explicit user constraints such as link exclusion rules",
                "High API token cost and unpredictable prompt execution times",
            ],
        },
        right_data={
            "icon": "🚫",
            "title": "Challenge 2: Hallucinated Physics",
            "title_color": COLOR_BURGUNDY,
            "border_color": COLOR_BURGUNDY,
            "bullets": [
                "LLMs are probabilistic text predictors, not optical physics calculators",
                "Incapable of computing Generalized Signal-to-Noise Ratio (GSNR)",
                "Ignore nonlinear fiber Kerr effects and EDFA noise accumulation",
                "Result: Proposes lightpaths with unfeasible optical Quality of Transmission",
                "Causes severe traffic drop or optical controller rejection upon deployment",
            ],
        },
        bottom_banner="Empirical Risk: Unconstrained LLMs allow up to 34% physically unfeasible routes to reach the optical controller",
        notes="""[Estimated Time]: 60s
[Key Message]: Standard LLMs cannot calculate optical physics and choke on massive topology payloads.
[Spoken Script]: Consider what happens if an operator asks a standard LLM to provision a 400G demand. First, we face Token Budget Saturation: dumping full topology states with hundreds of ROADMs and EDFA amplifier parameters degrades the LLM's attention, causing it to drop explicit constraints like link exclusions. Second, and more dangerously, LLMs suffer from Hallucinated Physics. Because they predict text probabilities rather than calculating nonlinear optical impairments, they will confidently propose routes that drop light below the required GSNR threshold, leading to service disruption.
[Bridge to Next Slide]: This fundamental gap defines our formal problem statement.""",
    )

    # 5. Slide 5: Problem Statement (3 Cards with Native OMML Equations)
    print("Building Slide 05: Problem Statement...")
    builder.create_card_slide(
        title="Problem Statement: Inputs, Constraints & Objectives",
        slide_num=5,
        cards=[
            {
                "icon": "📥",
                "title": "1. Given Inputs",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "Unstructured Natural Language intent from operator",
                    "Physical topology graph G(V, E) via RESTConf",
                    "Link parameters: span lengths, attenuation, dispersion",
                    "EDFA amplifier gains and noise figures",
                    "Transponder specs: baud rates, modulation formats",
                ],
            },
            {
                "icon": "🔒",
                "title": "2. Constraints",
                "title_color": COLOR_BURGUNDY,
                "bullets": [
                    "Semantic alignment: formal model matches intent",
                    "Optical GSNR exceeds transponder threshold",
                    "Receiver power satisfies sensitivity bounds",
                    "Zero spectral overlap and wavelength collision",
                ],
            },
            {
                "icon": "🎯",
                "title": "3. Objectives",
                "title_color": COLOR_GREEN,
                "bullets": [
                    "Zero unfeasible routes reaching network controller",
                    "Fail-fast pre-deployment validation pipeline",
                    "Selective, risk-proportional HITL engagement",
                    "Sub-second deterministic computation time",
                    "Auditable planning report for network engineers",
                ],
            },
        ],
        formulas={
            1: {
                "omml_list": [
                    '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>',
                    '<m:r><m:t>GSNR ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub>',
                    '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx,min</m:t></m:r></m:sub></m:sSub>',
                ]
            }
        },
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
            "icon": "🧠",
            "title": "Probabilistic Reasoning Layer",
            "title_color": COLOR_NAVY,
            "border_color": COLOR_NAVY,
            "bullets": [
                "LLMs Reason, Deterministic Tools Calculate",
                "Prohibit LLMs from performing graph routing or arithmetic",
                "Constrain the LLM strictly to formal linguistic translation",
                "Natural Language is parsed into formal PDDL constraints",
                "Zero hallucination of routing decisions or optical physics",
            ],
        },
        right_data={
            "icon": "📐",
            "title": "Deterministic Execution Layer",
            "title_color": COLOR_GREEN,
            "border_color": COLOR_GREEN,
            "bullets": [
                "Path computation delegated to Yen's KSP graph algorithms",
                "Physical validation delegated to analytical GN-model engine",
                "Subtopology extraction via scoped Mock GraphRAG",
                "Pre-deployment safety gate (RADG) verifies feasibility",
                "Guarantees provable physical safety before configuration push",
            ],
        },
        bottom_banner="Core Contributions: [1] Neurosymbolic Pipeline  |  [2] Scoped GraphRAG  |  [3] Risk-Adaptive Gates  |  [4] LangGraph Orchestrator",
        notes="""[Estimated Time]: 55s
[Key Message]: State the thesis contributions explicitly: decoupling probabilistic reasoning from deterministic calculations.
[Spoken Script]: Our core architectural principle is: 'LLMs reason, deterministic tools calculate'. We forbid the LLM from performing math or path exploration. Instead, the LLM acts solely as a semantic translator, converting natural language into formal Planning Domain Definition Language, or PDDL. This enables our four key contributions: a neurosymbolic pipeline, a scoped Optical GraphRAG mechanism, sequential pre-deployment risk gates, and an auditable LangGraph state machine.
[Bridge to Next Slide]: Let us trace the execution of this pipeline from end to end.""",
    )

    # 7. Slide 7: End-to-End System Architecture (7 Phases Flow Diagram)
    print("Building Slide 07: System Architecture...")
    builder.create_pipeline_flow_slide(
        title="End-to-End System Architecture & Pipeline Flow",
        slide_num=7,
        phases=[
            {"title": "Optical RAG", "desc": "Enrich intent with ITU-T grid & transponders"},
            {"title": "PDDL Parser", "desc": "Translate intent into formal PDDL AST"},
            {"title": "Semantic Gate", "desc": "Evaluate CFG & Reverse Prompting", "is_gate": True},
            {"title": "Symbolic Solver", "desc": "Scoped GraphRAG & Yen's KSP routing"},
            {"title": "QoT Physics", "desc": "Deterministic GN-model GSNR calculation"},
            {"title": "Risk Gate (RADG)", "desc": "Piecewise decision: Approve / Replan", "is_gate": True},
            {"title": "Plan Synthesizer", "desc": "Auditable report & deployment commands"},
        ],
        notes="""[Estimated Time]: 60s
[Key Message]: Walk through the clean 7-phase pipeline, highlighting the sequential fail-fast flow.
[Spoken Script]: Here we see the complete 7-phase execution pipeline. The operator's intent enters Phase 1 where it is enriched with optical standards. In Phase 2, the LLM generates PDDL constraints. Crucially, before running heavy graph solvers or physics tools, Phase 3 evaluates semantic uncertainty. If semantically sound, Phase 4 extracts candidate routes via symbolic graph algorithms. Phase 5 evaluates physical feasibility using a deterministic GN-model. Finally, the Risk-Adaptive Decision Gate verifies physical safety before synthesizing the final auditable report.
[Bridge to Next Slide]: Let us inspect how Phase 4 solves the token saturation problem.""",
    )

    # 8. Slide 8: Scoped GraphRAG (Split with Diagram Placeholder)
    print("Building Slide 08: Scoped GraphRAG...")
    builder.create_split_diagram_slide(
        title="Overcoming Token Saturation: Scoped Optical GraphRAG",
        slide_num=8,
        content_data={
            "icon": "🌐",
            "title": "Deterministic k-hop Subtopology Scoping",
            "title_color": COLOR_NAVY,
            "border_color": COLOR_NAVY,
            "bullets": [
                "Full topology dumps overwhelm LLM context windows",
                "Raw JSON contains excessive telemetry: ROADM ports, EDFAs, fibers",
                "Mock GraphRAG extracts only the k-hop neighborhood between endpoints",
                "Filters out irrelevant core subnets, links, and unused transponders",
                "Quantitative Impact: Over 75% reduction in prompt token payload",
                "Sub-millisecond graph extraction: O(V + E) executed in pure Python",
                "Guarantees sharp LLM attention focus on active optical constraints",
            ],
        },
        placeholder_info={
            "title": "Visual Diagram: Full 17-Node Backbone vs Scoped 2-Hop Subtopology",
            "subtitle": "(Target: 4:3 Network Topology & Subtopology Diagram — Replace in PowerPoint)",
        },
        notes="""[Estimated Time]: 50s
[Key Message]: Scoped GraphRAG extracts only relevant k-hop subtopologies, eliminating attention degradation.
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with hundreds of network nodes and links, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. This reduces the prompt token footprint by over 75 percent, completely eliminating lost-in-the-middle phenomena while keeping the graph search computationally light.
[Bridge to Next Slide]: Now let us examine how we eliminate semantic drift before any physics calculations occur.""",
    )

    # 9. Slide 9: Semantic Drift & Reverse Prompting (OMML Piecewise Math)
    print("Building Slide 09: Semantic Gate...")
    s9 = builder.prs.slides.add_slide(builder.prs.slide_layouts[6])
    builder.add_chrome(s9, "Overcoming Semantic Drift: Reverse Prompting & HITL", 9)

    # Left Column: 2-Layer Uncertainty Card with OMML
    card_l9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.3), Inches(5.7), Inches(4.7)
    )
    card_l9.fill.solid()
    card_l9.fill.fore_color.rgb = COLOR_CARD_BG
    card_l9.line.color.rgb = COLOR_NAVY
    card_l9.line.width = Pt(1.5)

    hdr_l9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.3), Inches(5.7), Inches(0.65)
    )
    hdr_l9.fill.solid()
    hdr_l9.fill.fore_color.rgb = COLOR_NAVY
    hdr_l9.line.fill.background()
    p_hl9 = hdr_l9.text_frame.paragraphs[0]
    p_hl9.text = "🧠 Two-Layer Semantic Uncertainty (U_sem)"
    p_hl9.font.name = FONT_TITLE
    p_hl9.font.size = Pt(15)
    p_hl9.font.bold = True
    p_hl9.font.color.rgb = COLOR_WHITE
    p_hl9.alignment = PP_ALIGN.CENTER

    body_l9 = s9.shapes.add_textbox(
        Inches(0.95), Inches(2.05), Inches(5.3), Inches(3.85)
    )
    tf_bl9 = body_l9.text_frame
    tf_bl9.word_wrap = True

    bullets_s9 = [
        "Layer 1 (Structural): CFG regex AST check instantly catches syntax errors",
        "Layer 2 (Semantic): Reverse Prompting reconstructs NL directly from PDDL",
        "Independent LLM judge measures semantic discrepancy d_sem in [0, 1]",
    ]
    for j, b_text in enumerate(bullets_s9):
        p = tf_bl9.paragraphs[0] if j == 0 else tf_bl9.add_paragraph()
        p.text = f"•  {b_text}"
        p.font.name = FONT_BODY
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK_SLATE
        p.space_after = Pt(6)

    p_omml_lbl = tf_bl9.add_paragraph()
    p_omml_lbl.text = "Uncertainty Formulation:"
    p_omml_lbl.font.name = FONT_TITLE
    p_omml_lbl.font.size = Pt(12)
    p_omml_lbl.font.bold = True
    p_omml_lbl.font.color.rgb = COLOR_NAVY
    p_omml_lbl.space_before = Pt(4)

    p_omml9 = tf_bl9.add_paragraph()
    p_omml9.alignment = PP_ALIGN.CENTER
    u_sem_xml = (
        '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = </m:t></m:r>'
        '<m:d>'
        '<m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/><m:grow m:val="1"/></m:dPr>'
        '<m:e>'
        '<m:eqArr>'
        '<m:e>'
        '<m:r><m:t>1&#160;&#160;&#160;&#160;&#160;&#160;&#160;&#160;if </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = 0</m:t></m:r>'
        '</m:e>'
        '<m:e>'
        '<m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>&#160;&#160;&#160;&#160;if </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = 1</m:t></m:r>'
        '</m:e>'
        '</m:eqArr>'
        '</m:e>'
        '</m:d>'
    )
    add_omml_equation(p_omml9, u_sem_xml)

    # Right Column: HITL Clarification Loop Card
    card_r9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.7), Inches(4.7)
    )
    card_r9.fill.solid()
    card_r9.fill.fore_color.rgb = COLOR_CARD_BG
    card_r9.line.color.rgb = COLOR_AMBER
    card_r9.line.width = Pt(1.5)

    hdr_r9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.7), Inches(0.65)
    )
    hdr_r9.fill.solid()
    hdr_r9.fill.fore_color.rgb = COLOR_AMBER
    hdr_r9.line.fill.background()
    p_hr9 = hdr_r9.text_frame.paragraphs[0]
    p_hr9.text = "⏸️ Fail-Fast HITL Clarification Loop"
    p_hr9.font.name = FONT_TITLE
    p_hr9.font.size = Pt(15)
    p_hr9.font.bold = True
    p_hr9.font.color.rgb = COLOR_WHITE
    p_hr9.alignment = PP_ALIGN.CENTER

    body_r9 = s9.shapes.add_textbox(
        Inches(7.0), Inches(2.05), Inches(5.3), Inches(3.85)
    )
    tf_br9 = body_r9.text_frame
    tf_br9.word_wrap = True

    bullets_r9 = [
        "Evaluated BEFORE invoking graph solvers or physical tools",
        "If U_sem > tau_sem: Pipeline pauses via LangGraph interrupt()",
        "Prompts operator to clarify ambiguous parameters or missing nodes",
        "Eliminates infinite trial-and-error conversational loops",
        "Guarantees that downstream tools receive mathematically verified intent",
        "If operator approves valid syntax: Bypasses parsing straight to solver",
    ]
    for j, b_text in enumerate(bullets_r9):
        p = tf_br9.paragraphs[0] if j == 0 else tf_br9.add_paragraph()
        p.text = f"•  {b_text}"
        p.font.name = FONT_BODY
        p.font.size = Pt(12)
        p.font.color.rgb = COLOR_DARK_SLATE
        p.space_after = Pt(6)

    # Bottom Summary Banner
    bb9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(6.2), Inches(11.75), Inches(0.65)
    )
    bb9.fill.solid()
    bb9.fill.fore_color.rgb = COLOR_CARD_BG
    bb9.line.color.rgb = COLOR_GREEN
    bb9.line.width = Pt(1.5)
    p_bb9 = bb9.text_frame.paragraphs[0]
    p_bb9.text = "Fail-Fast Guarantee: Zero computational waste on physics simulation when intent is ambiguous"
    p_bb9.font.name = FONT_TITLE
    p_bb9.font.size = Pt(13)
    p_bb9.font.bold = True
    p_bb9.font.color.rgb = COLOR_GREEN
    p_bb9.alignment = PP_ALIGN.CENTER

    builder.set_speaker_notes(
        s9,
        """[Estimated Time]: 60s
[Key Message]: The semantic gate prevents unverified assumptions from entering downstream tools.
[Spoken Script]: To eliminate semantic drift, we introduce a dual-layer Semantic Uncertainty Gate, U_sem. First, Layer 1 validates that the PDDL adheres strictly to our domain grammar, instantly catching structural hallucinations. Second, Layer 2 performs Reverse Prompting: an independent LLM reconstructs a plain-language summary directly from the PDDL. A semantic agreement judge compares this reconstruction against the operator's original request. If uncertainty exceeds our threshold tau_sem, the orchestrator pauses immediately via a LangGraph interrupt, asking the operator for clarification before wasting compute on physics.
[Bridge to Next Slide]: Once semantic validity is established, how do we make the final pre-deployment decision?""",
    )

    # 10. Slide 10: RADG Decision Gate (Full Decision Tree with OMML Piecewise Math)
    print("Building Slide 10: RADG Decision Gate...")
    radg_xml = (
        '<m:r><m:t>D(</m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>, </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t>) = </m:t></m:r>'
        '<m:d>'
        '<m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/><m:grow m:val="1"/></m:dPr>'
        '<m:e>'
        '<m:eqArr>'
        '<m:e>'
        '<m:r><m:t>clarify</m:t></m:r>'
        '<m:r><m:t>&#160;&#160;&#160;&#160;if </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> &gt; </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '</m:e>'
        '<m:e>'
        '<m:r><m:t>replan</m:t></m:r>'
        '<m:r><m:t>&#160;&#160;&#160;&#160;if </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> ≤ </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> ∧ </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = 0</m:t></m:r>'
        '</m:e>'
        '<m:e>'
        '<m:r><m:t>approve</m:t></m:r>'
        '<m:r><m:t>&#160;&#160;&#160;&#160;if </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> ≤ </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> ∧ </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = 1</m:t></m:r>'
        '</m:e>'
        '</m:eqArr>'
        '</m:e>'
        '</m:d>'
    )
    builder.create_decision_tree_slide(
        title="Pre-Deployment Risk Gate: The RADG Decision Function",
        slide_num=10,
        formula_xml=radg_xml,
        branches=[
            {
                "icon": "❓",
                "action": "Clarify Intent",
                "color": COLOR_AMBER,
                "condition": "U_sem > tau_sem",
                "bullets": [
                    "Trigger: Semantic uncertainty exceeds threshold",
                    "Action: Pause pipeline via interrupt()",
                    "Prompts operator to provide missing data",
                    "Prevents unverified intent from reaching physics",
                ],
            },
            {
                "icon": "↺",
                "action": "Suggest Replan",
                "color": COLOR_BURGUNDY,
                "condition": "U_sem <= tau_sem & QoT = 0",
                "bullets": [
                    "Trigger: Valid semantics, but physics infeasible",
                    "Action: Physics failed; notifies operator",
                    "Suggests relaxing constraints (e.g. lower baud rate)",
                    "Loops back to PDDL parsing with feedback",
                ],
            },
            {
                "icon": "✓",
                "action": "Auto-Approve",
                "color": COLOR_GREEN,
                "condition": "U_sem <= tau_sem & QoT = 1",
                "bullets": [
                    "Trigger: Clear semantics and feasible GSNR",
                    "Action: Autonomous zero-touch provisioning",
                    "Generates auditable planning report",
                    "Zero unverified configurations reach controller",
                ],
            },
        ],
        notes="""[Estimated Time]: 60s
[Key Message]: The RADG function mathematically maps semantic and physical signals to optimal actions.
[Spoken Script]: The cornerstone of our pre-deployment safety is the Risk-Adaptive Decision Gate, or RADG. We formalize this as a piecewise decision function, D. If semantic uncertainty U_sem exceeds our threshold, the system triggers 'clarify'. If semantics are sound but QoT fails, the system triggers 'replan' to relax physical constraints. Only when both semantic uncertainty is low and QoT is physically valid does the system issue 'approve'. This ensures zero unverified states reach the controller while avoiding operator fatigue through selective engagement.
[Bridge to Next Slide]: Let us examine the physical calculation engine powering QoT validation.""",
    )

    # 11. Slide 11: GN-Model QoT Validation (Native OMML Physical Formulas)
    print("Building Slide 11: QoT Physics Validation...")
    s11 = builder.prs.slides.add_slide(builder.prs.slide_layouts[6])
    builder.add_chrome(s11, "Deterministic Physical Layer: GN-Model QoT Validation", 11)

    # Left Column: Analytical Noise Model Formulas
    card_l11 = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.3), Inches(5.7), Inches(4.7)
    )
    card_l11.fill.solid()
    card_l11.fill.fore_color.rgb = COLOR_CARD_BG
    card_l11.line.color.rgb = COLOR_NAVY
    card_l11.line.width = Pt(1.5)

    hdr_l11 = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.3), Inches(5.7), Inches(0.65)
    )
    hdr_l11.fill.solid()
    hdr_l11.fill.fore_color.rgb = COLOR_NAVY
    hdr_l11.line.fill.background()
    p_hl11 = hdr_l11.text_frame.paragraphs[0]
    p_hl11.text = "🔬 Analytical Gaussian Noise (GN) Engine"
    p_hl11.font.name = FONT_TITLE
    p_hl11.font.size = Pt(15)
    p_hl11.font.bold = True
    p_hl11.font.color.rgb = COLOR_WHITE
    p_hl11.alignment = PP_ALIGN.CENTER

    body_l11 = s11.shapes.add_textbox(
        Inches(0.95), Inches(2.05), Inches(5.3), Inches(3.85)
    )
    tf_bl11 = body_l11.text_frame
    tf_bl11.word_wrap = True

    p_gn1 = tf_bl11.paragraphs[0]
    p_gn1.text = "•  Pure Python implementation: zero LLM arithmetic"
    p_gn1.font.name = FONT_BODY
    p_gn1.font.size = Pt(12)
    p_gn1.font.color.rgb = COLOR_DARK_SLATE

    p_ase_lbl = tf_bl11.add_paragraph()
    p_ase_lbl.text = "Accumulated ASE Noise Power per Span:"
    p_ase_lbl.font.name = FONT_TITLE
    p_ase_lbl.font.size = Pt(11)
    p_ase_lbl.font.bold = True
    p_ase_lbl.font.color.rgb = COLOR_NAVY
    p_ase_lbl.space_before = Pt(4)

    p_ase_eq = tf_bl11.add_paragraph()
    p_ase_eq.alignment = PP_ALIGN.CENTER
    ase_xml = (
        '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>ASE</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = (G - 1) · h · ν · F · </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>B</m:t></m:r></m:e><m:sub><m:r><m:t>ref</m:t></m:r></m:sub></m:sSub>'
    )
    add_omml_equation(p_ase_eq, ase_xml)

    p_nli_lbl = tf_bl11.add_paragraph()
    p_nli_lbl.text = "Nonlinear Interference (NLI) Noise Power:"
    p_nli_lbl.font.name = FONT_TITLE
    p_nli_lbl.font.size = Pt(11)
    p_nli_lbl.font.bold = True
    p_nli_lbl.font.color.rgb = COLOR_NAVY
    p_nli_lbl.space_before = Pt(4)

    p_nli_eq = tf_bl11.add_paragraph()
    p_nli_eq.alignment = PP_ALIGN.CENTER
    nli_xml = (
        '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>NLI</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> ≈ η · </m:t></m:r>'
        '<m:sSup><m:e><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>ch</m:t></m:r></m:sub></m:sSub></m:e><m:sup><m:r><m:t>3</m:t></m:r></m:sup></m:sSup>'
    )
    add_omml_equation(p_nli_eq, nli_xml)

    p_gn2 = tf_bl11.add_paragraph()
    p_gn2.text = "•  Accounts for fiber Kerr nonlinearity, dispersion, and EDFA noise"
    p_gn2.font.name = FONT_BODY
    p_gn2.font.size = Pt(11)
    p_gn2.font.color.rgb = COLOR_DARK_SLATE
    p_gn2.space_before = Pt(6)

    # Right Column: Feasibility Verification Formulas
    card_r11 = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.7), Inches(4.7)
    )
    card_r11.fill.solid()
    card_r11.fill.fore_color.rgb = COLOR_CARD_BG
    card_r11.line.color.rgb = COLOR_GREEN
    card_r11.line.width = Pt(1.5)

    hdr_r11 = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.3), Inches(5.7), Inches(0.65)
    )
    hdr_r11.fill.solid()
    hdr_r11.fill.fore_color.rgb = COLOR_GREEN
    hdr_r11.line.fill.background()
    p_hr11 = hdr_r11.text_frame.paragraphs[0]
    p_hr11.text = "📐 Optical Feasibility & GSNR Criteria"
    p_hr11.font.name = FONT_TITLE
    p_hr11.font.size = Pt(15)
    p_hr11.font.bold = True
    p_hr11.font.color.rgb = COLOR_WHITE
    p_hr11.alignment = PP_ALIGN.CENTER

    body_r11 = s11.shapes.add_textbox(
        Inches(7.0), Inches(2.05), Inches(5.3), Inches(3.85)
    )
    tf_br11 = body_r11.text_frame
    tf_br11.word_wrap = True

    p_gsnr_lbl = tf_br11.paragraphs[0]
    p_gsnr_lbl.text = "Generalized Signal-to-Noise Ratio (GSNR):"
    p_gsnr_lbl.font.name = FONT_TITLE
    p_gsnr_lbl.font.size = Pt(11)
    p_gsnr_lbl.font.bold = True
    p_gsnr_lbl.font.color.rgb = COLOR_GREEN

    p_gsnr_eq = tf_br11.add_paragraph()
    p_gsnr_eq.alignment = PP_ALIGN.CENTER
    gsnr_xml = (
        '<m:r><m:t>GSNR = </m:t></m:r>'
        '<m:f>'
        '<m:num><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>ch</m:t></m:r></m:sub></m:sSub></m:num>'
        '<m:den><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>ASE</m:t></m:r></m:sub></m:sSub><m:r><m:t> + </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>NLI</m:t></m:r></m:sub></m:sSub></m:den>'
        '</m:f>'
        '<m:r><m:t> ≥ </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub>'
    )
    add_omml_equation(p_gsnr_eq, gsnr_xml)

    p_prx_lbl = tf_br11.add_paragraph()
    p_prx_lbl.text = "Receiver Power Sensitivity Budget:"
    p_prx_lbl.font.name = FONT_TITLE
    p_prx_lbl.font.size = Pt(11)
    p_prx_lbl.font.bold = True
    p_prx_lbl.font.color.rgb = COLOR_GREEN
    p_prx_lbl.space_before = Pt(4)

    p_prx_eq = tf_br11.add_paragraph()
    p_prx_eq.alignment = PP_ALIGN.CENTER
    prx_xml = (
        '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> = </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>launch</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> - </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>A</m:t></m:r></m:e><m:sub><m:r><m:t>total</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> + </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>total</m:t></m:r></m:sub></m:sSub>'
        '<m:r><m:t> ≥ </m:t></m:r>'
        '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx,min</m:t></m:r></m:sub></m:sSub>'
    )
    add_omml_equation(p_prx_eq, prx_xml)

    p_qot_pts = tf_br11.add_paragraph()
    p_qot_pts.text = "•  Deterministic feasibility: GSNR >= threshold AND Power >= sensitivity"
    p_qot_pts.font.name = FONT_BODY
    p_qot_pts.font.size = Pt(11)
    p_qot_pts.font.color.rgb = COLOR_DARK_SLATE
    p_qot_pts.space_before = Pt(6)

    # Bottom Performance Banner
    bb11 = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(6.2), Inches(11.75), Inches(0.65)
    )
    bb11.fill.solid()
    bb11.fill.fore_color.rgb = COLOR_CARD_BG
    bb11.line.color.rgb = COLOR_GREEN
    bb11.line.width = Pt(1.5)
    p_bb11 = bb11.text_frame.paragraphs[0]
    p_bb11.text = "⚡ Execution Speed: Under 5 milliseconds per candidate route (100% deterministic reproducibility)"
    p_bb11.font.name = FONT_TITLE
    p_bb11.font.size = Pt(13)
    p_bb11.font.bold = True
    p_bb11.font.color.rgb = COLOR_GREEN
    p_bb11.alignment = PP_ALIGN.CENTER

    builder.set_speaker_notes(
        s11,
        """[Estimated Time]: 55s
[Key Message]: Pure Python GN-model computes real GSNR and receiver power deterministically in milliseconds.
[Spoken Script]: In Phase 5, candidate paths produced by the symbolic solver are validated against the physical layer. We port the analytical Gaussian Noise model into pure Python. The calculator accounts for fiber attenuation, EDFA noise figures, and nonlinear self-phase modulation across each span. A path is strictly feasible only if its computed GSNR satisfies the modulation format threshold and receiver power sensitivity is met. This deterministic evaluation executes in less than 5 milliseconds, completely eliminating physical hallucination.
[Bridge to Next Slide]: Let us see how this entire system is deployed and tested.""",
    )

    # 12. Slide 12: Experimental Setup (Split with Topology Map Placeholder)
    print("Building Slide 12: Experimental Setup...")
    builder.create_split_diagram_slide(
        title="Experimental Setup & Testbed Environment",
        slide_num=12,
        content_data={
            "icon": "🌐",
            "title": "17-Node German Core Network Benchmark",
            "title_color": COLOR_NAVY,
            "border_color": COLOR_NAVY,
            "bullets": [
                "Realistic telecom benchmark: 17 ROADMs and 26 fiber links",
                "Standard Single-Mode Fiber (SMF-28): alpha = 0.2 dB/km",
                "Dispersion parameter D = 16.7 ps/(nm*km), gamma = 1.2 / (W*km)",
                "Amplified spans: dual-stage EDFAs with noise figure F = 5.5 dB",
                "Dynamic link lengths ranging from 45 km to 350 km per span",
                "Orchestrator: LangGraph StateGraph with memory persistence",
                "Telemetry: RESTConf and Mock SDON testbed client adapters",
            ],
        },
        placeholder_info={
            "title": "Network Topology: Nobel-Germany 17-Node 26-Link Core Backbone",
            "subtitle": "(Target: 16:9 Topology Map with ROADM Nodes & Amplified Spans — Replace in PowerPoint)",
        },
        notes="""[Estimated Time]: 50s
[Key Message]: Realistic evaluation using the standard 17-node German optical topology and RESTConf testbed.
[Spoken Script]: We validate our architecture on the 17-node German backbone network, a standard benchmark in optical research consisting of 26 bidirectional fiber spans. All spans model standard SMF-28 fiber with realistic attenuation, dispersion, and EDFA noise figures. The orchestrator is implemented in Python using LangGraph, interfacing with the optical testbed via RESTConf APIs, and benchmarked using state-of-the-art LLMs as semantic translators.
[Bridge to Next Slide]: What scenarios and metrics do we use to evaluate the system?""",
    )

    # 13. Slide 13: Evaluation Framework (3 Cards: Baselines, Scenarios, Metrics)
    print("Building Slide 13: Evaluation Framework...")
    builder.create_card_slide(
        title="Evaluation Framework & Benchmark Scenarios",
        slide_num=13,
        cards=[
            {
                "icon": "⚖️",
                "title": "Architectural Baselines",
                "title_color": COLOR_NAVY,
                "bullets": [
                    "Baseline A (LLM-Only): Direct prompt-to-configuration generation with heuristic retry",
                    "Baseline B (Static Rule-Based): Strict regex parser with always-on human review",
                    "Proposed (Neurosymbolic RADG): Decoupled translation + sequential risk gates",
                    "Evaluates LLM reasoning limits vs deterministic safety",
                ],
            },
            {
                "icon": "🧪",
                "title": "100 Test Demands (4 Classes)",
                "title_color": COLOR_BURGUNDY,
                "bullets": [
                    "Nominal Intents [40]: Unambiguous valid routing requests with feasible physics",
                    "Ambiguous Intents [20]: Under-specified constraints triggering semantic gate (U_sem)",
                    "Infeasible Intents [25]: High modulation over long unamplified reaches (QoT fails)",
                    "Adversarial Prompts [15]: Hallucinated nodes & grammar violations",
                ],
            },
            {
                "icon": "📊",
                "title": "Evaluation Metrics",
                "title_color": COLOR_GREEN,
                "bullets": [
                    "Pre-Deployment Blocking Accuracy: % of invalid routes blocked before deployment",
                    "Human Intervention Rate: % of demands requiring human operator clarification",
                    "End-to-End Latency: Pipeline execution time from NL intent to planning report",
                    "Token Consumption: Prompt overhead across scoped vs full topologies",
                ],
            },
        ],
        notes="""[Estimated Time]: 55s
[Key Message]: Rigorous benchmarking across 100 diverse intent scenarios against LLM-only and rule-based baselines.
[Spoken Script]: Our evaluation framework tests 100 diverse intent requests across four operational categories: nominal intents, ambiguous intents with missing constraints, physically unfeasible demands, and adversarial prompts designed to induce hallucinations. We compare our neurosymbolic architecture against two baselines: an unconstrained LLM-only pipeline, and a rigid rule-based system. We measure three core dimensions: safety against unfeasible deployments, reduction in operator fatigue, and end-to-end execution latency.
[Bridge to Next Slide]: Let us analyze the key findings and trade-offs.""",
    )

    # 14. Slide 14: Key Findings (3 KPI Stat Banners + Empirical Chart Placeholder)
    print("Building Slide 14: Key Findings...")
    builder.create_kpi_and_placeholder_slide(
        title="Key Findings & Pre-Deployment Guarantees",
        slide_num=14,
        kpis=[
            {
                "value": "100%",
                "color": COLOR_GREEN,
                "border_color": COLOR_GREEN,
                "label": "Pre-Deployment Safety Guarantee",
                "subtitle": "Zero unfeasible lightpaths reach controller (vs 34% violation in LLM baseline)",
            },
            {
                "value": "> 70%",
                "color": COLOR_NAVY,
                "border_color": COLOR_NAVY,
                "label": "Reduction in Operator Fatigue",
                "subtitle": "Autonomous approval when U_sem <= tau_sem (operator engaged only on high risk)",
            },
            {
                "value": "< 15 ms",
                "color": COLOR_NAVY,
                "border_color": COLOR_NAVY,
                "label": "Deterministic Physics & Solver Latency",
                "subtitle": "Sub-second orchestration; solver & GN model execute in sub-milliseconds",
            },
        ],
        placeholder_info={
            "title": "Empirical Benchmark: GSNR Distribution & Blocking Rate vs Baselines",
            "subtitle": "(Target: 16:9 Matplotlib / Chapter 4 Benchmark Plot — Replace in PowerPoint)",
        },
        notes="""[Estimated Time]: 60s
[Key Message]: 100% pre-deployment safety, 70% reduction in operator fatigue, and sub-second deterministic compute.
[Spoken Script]: The experimental results validate our core hypothesis. Most importantly, our architecture achieved a 100 percent pre-deployment safety guarantee: zero physically unfeasible or hallucinated configurations ever reached the network controller. In contrast, the unconstrained LLM baseline allowed up to 34 percent invalid routes. Furthermore, by evaluating semantic uncertainty early, we reduced human operator interventions by over 70 percent compared to always-on review. Finally, our deterministic physics engine executed in under 15 milliseconds, proving that safety does not compromise speed.
[Bridge to Next Slide]: Let us summarize the primary conclusions of this thesis.""",
    )

    # 15. Slide 15: Conclusions & Main Takeaways (2x2 Grid)
    print("Building Slide 15: Conclusions...")
    s15 = builder.prs.slides.add_slide(builder.prs.slide_layouts[6])
    builder.add_chrome(s15, "Conclusions & Main Takeaways", 15)

    takeaways = [
        {
            "icon": "🧠",
            "title": "Neurosymbolic Decoupling is Essential",
            "border_color": COLOR_NAVY,
            "bullets": [
                "Probabilistic LLMs must never calculate physical impairments or route lightpaths",
                "Natural language reasoning cleanly bridges to formal PDDL planning",
                "Guarantees formal soundness without constraining operator expressiveness",
            ],
        },
        {
            "icon": "🔒",
            "title": "Sequential Risk Gates Prevent Failure",
            "border_color": COLOR_GREEN,
            "bullets": [
                "Early semantic evaluation (U_sem) eliminates drift before physics computation",
                "Deterministic GN-model verification (QoT_valid) ensures 100% physical feasibility",
                "Zero unverified configurations ever reach the optical controller",
            ],
        },
        {
            "icon": "⚡",
            "title": "Selective HITL Optimizes Efficiency",
            "border_color": COLOR_NAVY,
            "bullets": [
                "Engaging operators proportionally to risk eliminates fatigue while maintaining safety",
                "Over 70% reduction in human intervention compared to always-on review",
                "Sub-second planning latency enables rapid dynamic lightpath turn-up",
            ],
        },
        {
            "icon": "⚙️",
            "title": "Production-Ready Engineering",
            "border_color": COLOR_NAVY,
            "bullets": [
                "Fully implemented LangGraph state machine with memory checkpoints",
                "Benchmarked on realistic 17-node German optical topology and RESTConf testbed",
                "Establishes a reproducible foundation for autonomous optical networking",
            ],
        },
    ]

    grid_w = Inches(5.7)
    grid_h = Inches(2.55)
    positions = [
        (Inches(0.75), Inches(1.35)),
        (Inches(6.8), Inches(1.35)),
        (Inches(0.75), Inches(4.25)),
        (Inches(6.8), Inches(4.25)),
    ]

    for (pos_left, pos_top), item in zip(positions, takeaways):
        card = s15.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, pos_left, pos_top, grid_w, grid_h
        )
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD_BG
        card.line.color.rgb = item["border_color"]
        card.line.width = Pt(1.5)

        # Header Bar
        h_bar = s15.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, pos_left, pos_top, grid_w, Inches(0.55)
        )
        h_bar.fill.solid()
        h_bar.fill.fore_color.rgb = item["border_color"]
        h_bar.line.fill.background()

        tf_h = h_bar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.text = f"{item['icon']} {item['title']}"
        p_h.font.name = FONT_TITLE
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_h.alignment = PP_ALIGN.CENTER

        tf_b = card.text_frame
        tf_b.word_wrap = True
        tf_b.margin_top = Inches(0.65)
        tf_b.margin_left = Inches(0.15)
        tf_b.margin_right = Inches(0.15)

        for j, b_text in enumerate(item["bullets"]):
            p = tf_b.paragraphs[0] if j == 0 else tf_b.add_paragraph()
            p.text = f"•  {b_text}"
            p.font.name = FONT_BODY
            p.font.size = Pt(11)
            p.font.color.rgb = COLOR_DARK_SLATE
            p.space_after = Pt(3)

    builder.set_speaker_notes(
        s15,
        """[Estimated Time]: 55s
[Key Message]: Summarize the four core engineering takeaways of the thesis.
[Spoken Script]: In conclusion, this thesis demonstrates that neurosymbolic decoupling is essential for deploying AI in optical networks. By restricting the LLM to formal PDDL translation and delegating physics and routing to deterministic tools, we eliminate hallucination. Our sequential risk gates ensure that semantic uncertainty is caught early and physical feasibility is guaranteed before deployment. This achieves the dual goal of operational safety and minimal operator fatigue.
[Bridge to Next Slide]: Finally, let us review future research avenues and conclude.""",
    )

    # 16. Slide 16: Future Outlook & Acknowledgments
    print("Building Slide 16: Future Outlook...")
    s16 = builder.prs.slides.add_slide(builder.prs.slide_layouts[6])
    builder.add_chrome(s16, "Future Outlook & Acknowledgments", 16)

    # Left Column: 3 Future Directions Cards
    left_top = Inches(1.35)
    f_h = Inches(1.6)
    f_gap = Inches(0.2)
    left_w = Inches(6.8)

    directions = [
        {
            "icon": "🖥️",
            "title": "Joint Compute and Optical Scheduling",
            "desc": "Extending PDDL domain to co-schedule distributed GPU cluster workloads alongside optical lightpaths",
        },
        {
            "icon": "🌈",
            "title": "Multi-Band & Dynamic Optical Channels",
            "desc": "Expanding analytical GN-models to incorporate C+L multi-band SRS inter-channel Raman crosstalk",
        },
        {
            "icon": "🔄",
            "title": "Autonomous Online Self-Healing",
            "desc": "Ingesting real-time testbed telemetry for closed-loop intent re-planning upon physical fiber degradation",
        },
    ]

    for i, d in enumerate(directions):
        cur_top = left_top + i * (f_h + f_gap)
        c = s16.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), cur_top, left_w, f_h
        )
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD_BG
        c.line.color.rgb = COLOR_NAVY
        c.line.width = Pt(1.5)

        tf = c.text_frame
        tf.word_wrap = True
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.15)

        p_t = tf.paragraphs[0]
        p_t.text = f"{d['icon']}  {d['title']}"
        p_t.font.name = FONT_TITLE
        p_t.font.size = Pt(14)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY

        p_d = tf.add_paragraph()
        p_d.text = d["desc"]
        p_d.font.name = FONT_BODY
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = COLOR_DARK_SLATE
        p_d.space_before = Pt(4)

    # Right Column: Acknowledgment & Thank You Card
    right_card = s16.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.8), Inches(1.35), Inches(4.75), Inches(5.2)
    )
    right_card.fill.solid()
    right_card.fill.fore_color.rgb = COLOR_CARD_BG
    right_card.line.color.rgb = COLOR_BURGUNDY
    right_card.line.width = Pt(2.0)

    tf_rc = right_card.text_frame
    tf_rc.word_wrap = True
    tf_rc.margin_top = Inches(0.4)
    tf_rc.margin_left = Inches(0.25)
    tf_rc.margin_right = Inches(0.25)

    p_ack_hdr = tf_rc.paragraphs[0]
    p_ack_hdr.text = "ACKNOWLEDGMENTS"
    p_ack_hdr.font.name = FONT_TITLE
    p_ack_hdr.font.size = Pt(16)
    p_ack_hdr.font.bold = True
    p_ack_hdr.font.color.rgb = COLOR_BURGUNDY
    p_ack_hdr.alignment = PP_ALIGN.CENTER

    p_ack = tf_rc.add_paragraph()
    p_ack.text = "Sincere gratitude to Academic Advisor Prof. Massimo Tornatore and the SDON Laboratory research group at Politecnico di Milano for their invaluable technical guidance and mentorship."
    p_ack.font.name = FONT_BODY
    p_ack.font.size = Pt(12)
    p_ack.font.color.rgb = COLOR_DARK_SLATE
    p_ack.alignment = PP_ALIGN.CENTER
    p_ack.space_before = Pt(12)

    p_div = tf_rc.add_paragraph()
    p_div.text = "──────────────────────"
    p_div.font.name = "Arial"
    p_div.font.size = Pt(12)
    p_div.font.color.rgb = COLOR_COOL_GRAY
    p_div.alignment = PP_ALIGN.CENTER
    p_div.space_before = Pt(16)

    p_ty = tf_rc.add_paragraph()
    p_ty.text = "Thank You for Your Attention!"
    p_ty.font.name = FONT_TITLE
    p_ty.font.size = Pt(18)
    p_ty.font.bold = True
    p_ty.font.color.rgb = COLOR_NAVY
    p_ty.alignment = PP_ALIGN.CENTER
    p_ty.space_before = Pt(16)

    p_qa = tf_rc.add_paragraph()
    p_qa.text = "Questions & Discussion"
    p_qa.font.name = FONT_BODY
    p_qa.font.size = Pt(14)
    p_qa.font.color.rgb = COLOR_COOL_GRAY
    p_qa.alignment = PP_ALIGN.CENTER
    p_qa.space_before = Pt(4)

    builder.set_speaker_notes(
        s16,
        """[Estimated Time]: 45s
[Key Message]: Thank the committee, outline future research directions (joint compute scheduling), and open Q&A.
[Spoken Script]: Looking forward, our immediate next step is extending this PDDL framework to joint routing and compute scheduling, coordinating optical lightpaths with distributed data center GPU workloads. I want to express my deepest gratitude to Professor Tornatore and my colleagues in the SDON laboratory for their invaluable guidance throughout this research. Thank you very much for your time and attention. I am now open to your questions.""",
    )

    # Save Output Presentation
    output = Path("docs/LLM_Wiki/wiki/presentations/thesis_defense/thesis_defense.pptx")
    output.parent.mkdir(parents=True, exist_ok=True)
    builder.prs.save(str(output))
    print(f"\nPresentation successfully generated at: {output}")
    print(f"Total slides generated: {len(builder.prs.slides)}")


if __name__ == "__main__":
    build_thesis_defense_deck()
