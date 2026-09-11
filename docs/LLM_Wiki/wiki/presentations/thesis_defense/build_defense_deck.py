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
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
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


# --- Comprehensive Office Math (OMML) Dictionary ---
OMML_MAP = {
    # Semantic Gate & Uncertainty
    r"U_{sem}": '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>',
    r"\tau_{sem}": '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>',
    r"U_{sem} \le \tau_{sem}": '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>',
    r"U_{sem} > \tau_{sem}": '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> &gt; </m:t></m:r><m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>',
    r"d_{sem}": '<m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>',
    r"d_{sem} \in [0, 1]": '<m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∈ [0, 1]</m:t></m:r>',
    r"v_{struct}": '<m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub>',
    r"v_{struct} \in \{0, 1\}": '<m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∈ {0, 1}</m:t></m:r>',
    r"v_{struct} = 1": '<m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 1</m:t></m:r>',
    r"v_{struct} = 0": '<m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 0</m:t></m:r>',
    r"U_{sem} = f(v_{struct}, d_{sem})": '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> = f(</m:t></m:r><m:sSub><m:e><m:r><m:t>v</m:t></m:r></m:e><m:sub><m:r><m:t>struct</m:t></m:r></m:sub></m:sSub><m:r><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:t>d</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t>)</m:t></m:r>',
    r"\mathcal{I}_{NL}": '<m:sSub><m:e><m:r><m:t>ℐ</m:t></m:r></m:e><m:sub><m:r><m:t>NL</m:t></m:r></m:sub></m:sSub>',
    r"\mathcal{S}_{PDDL}": '<m:sSub><m:e><m:r><m:t>𝒮</m:t></m:r></m:e><m:sub><m:r><m:t>PDDL</m:t></m:r></m:sub></m:sSub>',
    r"\mathcal{I}_{NL} \to \mathcal{S}_{PDDL}": '<m:sSub><m:e><m:r><m:t>ℐ</m:t></m:r></m:e><m:sub><m:r><m:t>NL</m:t></m:r></m:sub></m:sSub><m:r><m:t> → </m:t></m:r><m:sSub><m:e><m:r><m:t>𝒮</m:t></m:r></m:e><m:sub><m:r><m:t>PDDL</m:t></m:r></m:sub></m:sSub>',
    r"\mathcal{I}_{recon}": '<m:sSub><m:e><m:r><m:t>ℐ</m:t></m:r></m:e><m:sub><m:r><m:t>recon</m:t></m:r></m:sub></m:sSub>',

    # Physical Risk Gate & QoT
    r"\text{QoT}_{valid}": '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub>',
    r"\text{QoT}_{valid} = 1": '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 1</m:t></m:r>',
    r"\text{QoT}_{valid} = 0": '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 0</m:t></m:r>',
    r"U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 0": '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∧ </m:t></m:r><m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 0</m:t></m:r>',
    r"U_{sem} \le \tau_{sem} \land \text{QoT}_{valid} = 1": '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∧ </m:t></m:r><m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t> = 1</m:t></m:r>',
    r"D(U_{sem}, \text{QoT}_{valid})": '<m:r><m:t>D(</m:t></m:r><m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t>)</m:t></m:r>',
    r"D(U_{sem}, \text{QoT})": '<m:r><m:t>D(</m:t></m:r><m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t>, QoT)</m:t></m:r>',

    # Topology & Graph Scoping
    r"G(V, E)": '<m:r><m:t>G(V, E)</m:t></m:r>',
    r"G = (V, E)": '<m:r><m:t>G = (V, E)</m:t></m:r>',
    r"G_{sub}": '<m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>sub</m:t></m:r></m:sub></m:sSub>',
    r"G_{sub} \subseteq G": '<m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>sub</m:t></m:r></m:sub></m:sSub><m:r><m:t> ⊆ G</m:t></m:r>',
    r"G_{sub} = (V_{sub}, E_{sub}) \subseteq G": '<m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>sub</m:t></m:r></m:sub></m:sSub><m:r><m:t> = (</m:t></m:r><m:sSub><m:e><m:r><m:t>V</m:t></m:r></m:e><m:sub><m:r><m:t>sub</m:t></m:r></m:sub></m:sSub><m:r><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:t>E</m:t></m:r></m:e><m:sub><m:r><m:t>sub</m:t></m:r></m:sub></m:sSub><m:r><m:t>) ⊆ G</m:t></m:r>',
    r"|V| = 17, |E| = 26": '<m:r><m:t>|V| = 17, |E| = 26</m:t></m:r>',
    r"k": '<m:r><m:t>k</m:t></m:r>',
    r"k\text{-hop}": '<m:r><m:t>k</m:t></m:r><m:r><m:t>-hop</m:t></m:r>',
    r"K\text{-SP}": '<m:r><m:t>K</m:t></m:r><m:r><m:t>-SP</m:t></m:r>',
    r"\mathcal{O}(|V| + |E|)": '<m:r><m:t>𝒪(|V| + |E|)</m:t></m:r>',
    r"T_{prompt}(G_{sub}) \ll T_{prompt}(G)": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>prompt</m:t></m:r></m:sub></m:sSub><m:r><m:t>(</m:t></m:r><m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>sub</m:t></m:r></m:sub></m:sSub><m:r><m:t>) ≪ </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>prompt</m:t></m:r></m:sub></m:sSub><m:r><m:t>(G)</m:t></m:r>',

    # Optical Physics & QoT Metrics
    r"\text{GSNR}": '<m:r><m:t>GSNR</m:t></m:r>',
    r"\text{GSNR}_{th}": '<m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub>',
    r"\text{GSNR} \ge \text{GSNR}_{th}": '<m:r><m:t>GSNR ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub>',
    r"P_{rx}": '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx</m:t></m:r></m:sub></m:sSub>',
    r"P_{rx,min}": '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx,min</m:t></m:r></m:sub></m:sSub>',
    r"P_{rx} \ge P_{rx,min}": '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx,min</m:t></m:r></m:sub></m:sSub>',
    r"\text{GSNR} \ge \text{GSNR}_{th} \land P_{rx} \ge P_{rx,min}": '<m:r><m:t>GSNR ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∧ </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx,min</m:t></m:r></m:sub></m:sSub>',
    r"P_{ASE}": '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>ASE</m:t></m:r></m:sub></m:sSub>',
    r"P_{NLI}": '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>NLI</m:t></m:r></m:sub></m:sSub>',
    r"P_{ch}": '<m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>ch</m:t></m:r></m:sub></m:sSub>',
    r"\alpha": '<m:r><m:t>α</m:t></m:r>',
    r"\alpha = 0.2\text{ dB/km}": '<m:r><m:t>α = 0.2 dB/km</m:t></m:r>',
    r"D": '<m:r><m:t>D</m:t></m:r>',
    r"D = 16.7\text{ ps/(nm}\cdot\text{km})": '<m:r><m:t>D = 16.7 ps/(nm·km)</m:t></m:r>',
    r"\gamma": '<m:r><m:t>γ</m:t></m:r>',
    r"\gamma = 1.2\text{ W}^{-1}\text{km}^{-1}": '<m:r><m:t>γ = 1.2 </m:t></m:r><m:sSup><m:e><m:r><m:t>W</m:t></m:r></m:e><m:sup><m:r><m:t>-1</m:t></m:r></m:sup></m:sSup><m:sSup><m:e><m:r><m:t>km</m:t></m:r></m:e><m:sup><m:r><m:t>-1</m:t></m:r></m:sup></m:sSup>',
    r"NF": '<m:r><m:t>NF</m:t></m:r>',
    r"NF = 5.5\text{ dB}": '<m:r><m:t>NF = 5.5 dB</m:t></m:r>',
    r"G_m": '<m:sSub><m:e><m:r><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>',
    r"NF_m": '<m:sSub><m:e><m:r><m:t>NF</m:t></m:r></m:e><m:sub><m:r><m:t>m</m:t></m:r></m:sub></m:sSub>',
    r"R_s": '<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>s</m:t></m:r></m:sub></m:sSub>',
    r"L \in [45, 350]\text{ km}": '<m:r><m:t>L ∈ [45, 350] km</m:t></m:r>',

    # Evaluation Metrics
    r"\text{UAR} = 100\%": '<m:r><m:t>UAR = 100%</m:t></m:r>',
    r"\text{UAR} = 0": '<m:r><m:t>UAR = 0</m:t></m:r>',
    r"UAR = 0": '<m:r><m:t>UAR = 0</m:t></m:r>',
    r"UAR = 0 ": '<m:r><m:t>UAR = 0 </m:t></m:r>',
    r"\text{UAR}": '<m:r><m:t>UAR</m:t></m:r>',
    r"\text{HIC}": '<m:r><m:t>HIC</m:t></m:r>',
    r"T_{E2E}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>E2E</m:t></m:r></m:sub></m:sSub>',
    r"T_{prompt}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>prompt</m:t></m:r></m:sub></m:sSub>',
    r"T_{phys} < 15\text{ ms}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>phys</m:t></m:r></m:sub></m:sSub><m:r><m:t> &lt; 15 ms</m:t></m:r>',
    r"T_{phys} < 5\text{ ms}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>phys</m:t></m:r></m:sub></m:sSub><m:r><m:t> &lt; 5 ms</m:t></m:r>',
    r"T_{solver} < 10\text{ ms}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>solver</m:t></m:r></m:sub></m:sSub><m:r><m:t> &lt; 10 ms</m:t></m:r>',
    r"\text{QoT}": '<m:r><m:t>QoT</m:t></m:r>',
    r"G": '<m:r><m:t>G</m:t></m:r>',
    r"V": '<m:r><m:t>V</m:t></m:r>',
    r"E": '<m:r><m:t>E</m:t></m:r>',
    r"K": '<m:r><m:t>K</m:t></m:r>',
    r"T_{phys}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>phys</m:t></m:r></m:sub></m:sSub>',
    r"T_{solver}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>solver</m:t></m:r></m:sub></m:sSub>',

    # Slide 5 Formal Problem Formulation Math
    r"L": '<m:r><m:t>L</m:t></m:r>',
    r"\text{GSNR}_{th} = \text{SNR}_{min} + \text{Margin}": '<m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub><m:r><m:t> = </m:t></m:r><m:sSub><m:e><m:r><m:t>SNR</m:t></m:r></m:e><m:sub><m:r><m:t>min</m:t></m:r></m:sub></m:sSub><m:r><m:t> + Margin</m:t></m:r>',
    r"\pi^* \in \mathcal{K}_{path}": '<m:sSup><m:e><m:r><m:t>π</m:t></m:r></m:e><m:sup><m:r><m:t>*</m:t></m:r></m:sup></m:sSup><m:r><m:t> ∈ </m:t></m:r><m:sSub><m:e><m:r><m:t>𝒦</m:t></m:r></m:e><m:sub><m:r><m:t>path</m:t></m:r></m:sub></m:sSub>',
    r"a \in \{\text{approve}, \text{clarify}, \text{replan}\}": '<m:r><m:t>a ∈ {approve, clarify, replan}</m:t></m:r>',
    r"c^*": '<m:sSup><m:e><m:r><m:t>c</m:t></m:r></m:e><m:sup><m:r><m:t>*</m:t></m:r></m:sup></m:sSup>',
    r"\min \mathcal{J} = \alpha \cdot N_{hitl} + \beta \cdot T_{tokens}": '<m:r><m:t>min 𝒥 = α · </m:t></m:r><m:sSub><m:e><m:r><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:t>hitl</m:t></m:r></m:sub></m:sSub><m:r><m:t> + β · </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>tokens</m:t></m:r></m:sub></m:sSub>',
    r"\min \alpha \cdot N_{hitl} + \beta \cdot T_{tokens}": '<m:r><m:t>min α · </m:t></m:r><m:sSub><m:e><m:r><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:t>hitl</m:t></m:r></m:sub></m:sSub><m:r><m:t> + β · </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>tokens</m:t></m:r></m:sub></m:sSub>',
    r"\min N_{hitl}": '<m:r><m:t>min </m:t></m:r><m:sSub><m:e><m:r><m:t>N</m:t></m:r></m:e><m:sub><m:r><m:t>hitl</m:t></m:r></m:sub></m:sSub>',
    r"\min T_{tokens}": '<m:r><m:t>min </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>tokens</m:t></m:r></m:sub></m:sSub>',
    r"\mathcal{D}(U_{sem}, \text{QoT}_{valid}) = \text{approve}": '<m:r><m:t>𝒟(</m:t></m:r><m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub><m:r><m:t>, </m:t></m:r><m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t>) = approve</m:t></m:r>',
    r"T_{prompt} \le T_{max}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>prompt</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>max</m:t></m:r></m:sub></m:sSub>',
    r"T_{prompt} \le T_{max} \ll T_{full}": '<m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>prompt</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>max</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≪ </m:t></m:r><m:sSub><m:e><m:r><m:t>T</m:t></m:r></m:e><m:sub><m:r><m:t>full</m:t></m:r></m:sub></m:sSub>',
    r"t_{exec} \le t_{max\_budget}": '<m:sSub><m:e><m:r><m:t>t</m:t></m:r></m:e><m:sub><m:r><m:t>exec</m:t></m:r></m:sub></m:sSub><m:r><m:t> ≤ </m:t></m:r><m:sSub><m:e><m:r><m:t>t</m:t></m:r></m:e><m:sub><m:r><m:t>max_budget</m:t></m:r></m:sub></m:sSub>',
    r"K \in [3, 5]": '<m:r><m:t>K ∈ [3, 5]</m:t></m:r>',
    r"\text{GSNR}(\pi^*) \ge \text{GSNR}_{th} \land P_{rx}(\pi^*) \ge P_{rx,min}": '<m:r><m:t>GSNR(</m:t></m:r><m:sSup><m:e><m:r><m:t>π</m:t></m:r></m:e><m:sup><m:r><m:t>*</m:t></m:r></m:sup></m:sSup><m:r><m:t>) ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>GSNR</m:t></m:r></m:e><m:sub><m:r><m:t>th</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∧ </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx</m:t></m:r></m:sub></m:sSub><m:r><m:t>(</m:t></m:r><m:sSup><m:e><m:r><m:t>π</m:t></m:r></m:e><m:sup><m:r><m:t>*</m:t></m:r></m:sup></m:sSup><m:r><m:t>) ≥ </m:t></m:r><m:sSub><m:e><m:r><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:t>rx,min</m:t></m:r></m:sub></m:sSub>',
    r"\text{QoT}_{valid} \in \{0, 1\}": '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub><m:r><m:t> ∈ {0, 1}</m:t></m:r>',
}


def add_math_runs_to_paragraph(paragraph, text: str, font_size=Pt(12), color=COLOR_DARK_SLATE, font_name=FONT_BODY, bold=False):
    """
    Parses a string that may contain LaTeX math tokens delimited by $...$
    and appends normal DrawingML runs (<a:r>) and native Office Math (<a14:m><m:oMath>).
    Configures <a:defRPr> on the paragraph so math formulas match the text size and color.
    """
    sz_val = int(font_size.pt * 100)
    p_pr = paragraph._p.get_or_add_pPr()
    
    if isinstance(color, (tuple, RGBColor)):
        color_hex = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    else:
        color_hex = str(color).replace('#', '')
        
    b_attr = ' b="1"' if bold else ''
    
    existing_def = p_pr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}defRPr')
    if existing_def is not None:
        p_pr.remove(existing_def)
        
    def_xml = (
        f'<a:defRPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" sz="{sz_val}"{b_attr}>'
        f'<a:solidFill><a:srgbClr val="{color_hex}"/></a:solidFill>'
        f'</a:defRPr>'
    )
    p_pr.append(parse_xml(def_xml))

    parts = re.split(r'(\$[^\$]+\$)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('$') and part.endswith('$'):
            latex = part[1:-1].strip()
            xml = OMML_MAP.get(latex, f'<m:r><m:t>{latex}</m:t></m:r>')
            full_xml = (
                f'<a14:m xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" '
                f'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
                f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
                f'<m:oMath>{xml}</m:oMath></a14:m>'
            )
            paragraph._p.append(parse_xml(full_xml))
        else:
            r = paragraph.add_run()
            r.text = part
            r.font.name = font_name
            r.font.size = font_size
            r.font.bold = bold
            r.font.color.rgb = color


def add_bullet_with_math(text_frame, text: str, font_size=Pt(12), color=COLOR_DARK_SLATE, space_after=Pt(6), space_before=Pt(0)):
    """
    Adds a bullet point to a TextFrame, supporting embedded $math$ expressions.
    Reuses the first paragraph if it is currently empty.
    """
    if len(text_frame.paragraphs) == 1 and len(text_frame.paragraphs[0].text) == 0 and len(text_frame.paragraphs[0].runs) == 0:
        p = text_frame.paragraphs[0]
    else:
        p = text_frame.add_paragraph()
    p.space_after = space_after
    p.space_before = space_before
    add_math_runs_to_paragraph(p, text, font_size=font_size, color=color, font_name=FONT_BODY)
    return p


def add_omml_equation(paragraph, omml_xml: str, font_size=Pt(12), color=COLOR_DARK_SLATE):
    """
    Injects native Office Math (OMML) XML into a DrawingML paragraph.
    PowerPoint renders this natively in Cambria Math with fractions,
    subscripts, superscripts, and piecewise curly braces.
    Configures <a:defRPr> so the equation renders with proportional font size and color.
    """
    sz_val = int(font_size.pt * 100)
    p_pr = paragraph._p.get_or_add_pPr()
    
    if isinstance(color, (tuple, RGBColor)):
        color_hex = f"{color[0]:02X}{color[1]:02X}{color[2]:02X}"
    else:
        color_hex = str(color).replace('#', '')
        
    existing_def = p_pr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}defRPr')
    if existing_def is not None:
        p_pr.remove(existing_def)
        
    def_xml = (
        f'<a:defRPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" sz="{sz_val}">'
        f'<a:solidFill><a:srgbClr val="{color_hex}"/></a:solidFill>'
        f'</a:defRPr>'
    )
    p_pr.append(parse_xml(def_xml))

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

    def add_chrome(self, slide, title_text: str, slide_num: int, title_h: float = 0.75):
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
        title_box = slide.shapes.add_textbox(Inches(0.7), Inches(0.25), Inches(11.8), Inches(title_h))
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

    def add_entrance_click_animation(self, slide, shape_id: int):
        """
        Injects PresentationML timing XML so that the target shape appears
        on mouse click or keyboard arrow advancement during the slideshow.
        """
        timing_xml = f'''<p:timing xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:tnLst>
    <p:par>
      <p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot">
        <p:childTnLst>
          <p:seq concurrent="1" nextAc="seek">
            <p:cTn id="2" dur="indefinite" nodeType="mainSeq">
              <p:childTnLst>
                <p:par>
                  <p:cTn id="3" fill="hold">
                    <p:stCondLst>
                      <p:cond delay="indefinite"/>
                    </p:stCondLst>
                    <p:childTnLst>
                      <p:par>
                        <p:cTn id="4" fill="hold">
                          <p:stCondLst>
                            <p:cond delay="0"/>
                          </p:stCondLst>
                          <p:childTnLst>
                            <p:par>
                              <p:cTn id="5" presetID="1" presetClass="entr" presetSubtype="0" fill="hold" nodeType="clickEffect">
                                <p:stCondLst>
                                  <p:cond delay="0"/>
                                </p:stCondLst>
                                <p:childTnLst>
                                  <p:set>
                                    <p:cBhvr>
                                      <p:cTn id="6" dur="1" fill="hold">
                                        <p:stCondLst>
                                          <p:cond delay="0"/>
                                        </p:stCondLst>
                                      </p:cTn>
                                      <p:tgtEl>
                                        <p:spTgt spid="{shape_id}"/>
                                      </p:tgtEl>
                                      <p:attrNameLst>
                                        <p:attrName>style.visibility</p:attrName>
                                      </p:attrNameLst>
                                    </p:cBhvr>
                                    <p:to>
                                      <p:strVal val="visible"/>
                                    </p:to>
                                  </p:set>
                                </p:childTnLst>
                              </p:cTn>
                            </p:par>
                          </p:childTnLst>
                        </p:cTn>
                      </p:par>
                    </p:childTnLst>
                  </p:cTn>
                </p:par>
              </p:childTnLst>
            </p:cTn>
            <p:prevCondLst>
              <p:cond evt="onPrev" delay="0">
                <p:tgtEl>
                  <p:sldTgt/>
                </p:tgtEl>
              </p:cond>
            </p:prevCondLst>
            <p:nextCondLst>
              <p:cond evt="onNext" delay="0">
                <p:tgtEl>
                  <p:sldTgt/>
                </p:tgtEl>
              </p:cond>
            </p:nextCondLst>
          </p:seq>
        </p:childTnLst>
      </p:cTn>
    </p:par>
  </p:tnLst>
</p:timing>'''
        timing_elem = parse_xml(timing_xml)
        ext_lst = slide.element.xpath('./p:extLst')
        if ext_lst:
            ext_lst[0].addprevious(timing_elem)
        else:
            slide.element.append(timing_elem)

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
        p1.text = "LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning\nfor Optical Networks"
        p1.font.name = FONT_TITLE
        p1.font.size = Pt(32)
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
        p_adv.text = "Academic Advisor: Prof. Massimo Tornatore & Prof. Qiaolun Zhang"
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
[Spoken Script]: Good morning members of the committee and Professor Tornatore. Today I present my Master's thesis entitled "LLM-Assisted Risk-Adaptive Neurosymbolic Intent Planning for Optical Networks: A Pre-Deployment Decision Mechanism with Joint Semantic and QoT Assessment". In this work, we address the challenge of bridging high-level operator intent with physical optical layer realities using a robust, fail-fast neurosymbolic architecture.
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
            add_math_runs_to_paragraph(p_title, row["title"], font_size=Pt(15), color=COLOR_NAVY, font_name=FONT_TITLE, bold=True)

            p_desc = tf.add_paragraph()
            add_math_runs_to_paragraph(p_desc, row["desc"], font_size=Pt(12), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

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

            callout = data.get("callout")
            body_h = (col_height - header_height - Inches(1.2)) if callout else (col_height - header_height - Inches(0.3))

            # Body Bullets
            body_box = s.shapes.add_textbox(
                col_left + Inches(0.2),
                top_pos + header_height + Inches(0.12),
                col_width - Inches(0.4),
                body_h,
            )
            tf_b = body_box.text_frame
            tf_b.word_wrap = True
            tf_b.margin_top = Inches(0.05)

            bullets = data.get("bullets", [])
            for j, b_text in enumerate(bullets):
                add_bullet_with_math(tf_b, f"•  {b_text}", font_size=Pt(11.5), color=COLOR_DARK_SLATE, space_after=Pt(4))

            # Bottom Callout Block if provided
            if callout:
                callout_y = top_pos + col_height - Inches(0.95)
                callout_box = s.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE,
                    col_left + Inches(0.2),
                    callout_y,
                    col_width - Inches(0.4),
                    Inches(0.80),
                )
                callout_box.fill.solid()
                callout_box.fill.fore_color.rgb = COLOR_WHITE
                callout_box.line.color.rgb = border_color
                callout_box.line.width = Pt(1.5)

                tf_c = callout_box.text_frame
                tf_c.word_wrap = True
                tf_c.margin_top = Inches(0.08)
                tf_c.margin_left = Inches(0.12)
                tf_c.margin_right = Inches(0.12)
                p_c = tf_c.paragraphs[0]
                add_math_runs_to_paragraph(p_c, callout["text"], font_size=Pt(11), color=border_color, font_name=FONT_TITLE, bold=True)
                p_c.alignment = PP_ALIGN.CENTER

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
            add_math_runs_to_paragraph(p_bb, bottom_banner, font_size=Pt(12), color=COLOR_NAVY, font_name=FONT_TITLE, bold=True)
            p_bb.alignment = PP_ALIGN.CENTER

        self.set_speaker_notes(s, notes)
        return s

    def create_evolution_sdon_ibon_slide(
        self,
        title: str,
        slide_num: int,
        notes: str,
    ):
        """Creates Slide 3: Evolution from Imperative SDON to Declarative IBON (Paradigm Shift)."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        # === LEFT COLUMN: Imperative SDON ===
        card_l = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.95), Inches(1.42), Inches(4.65), Inches(4.41))
        card_l.fill.solid()
        card_l.fill.fore_color.rgb = COLOR_CARD_BG
        card_l.line.color.rgb = COLOR_BURGUNDY
        card_l.line.width = Pt(1.5)

        hdr_l = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.30), Inches(5.05), Inches(0.72))
        hdr_l.fill.solid()
        hdr_l.fill.fore_color.rgb = COLOR_BURGUNDY
        hdr_l.line.fill.background()

        tf_hl = hdr_l.text_frame
        tf_hl.word_wrap = True
        tf_hl.margin_top = Inches(0.08)
        p_hl0 = tf_hl.paragraphs[0]
        p_hl0.text = "⚠️ Current Paradigm: Imperative SDON"
        p_hl0.font.name = FONT_TITLE
        p_hl0.font.size = Pt(13.5)
        p_hl0.font.bold = True
        p_hl0.font.color.rgb = COLOR_WHITE
        p_hl0.alignment = PP_ALIGN.CENTER

        p_hl1 = tf_hl.add_paragraph()
        p_hl1.text = 'Procedural "HOW" Execution • Open-Loop Control'
        p_hl1.font.name = FONT_BODY
        p_hl1.font.size = Pt(10.5)
        p_hl1.font.color.rgb = COLOR_WHITE
        p_hl1.alignment = PP_ALIGN.CENTER

        left_pills = ["Procedural Scripts", "Static Margins", "Open-Loop Control"]
        left_tops = [Inches(2.46), Inches(3.315), Inches(4.17)]
        for p_text, top_pos in zip(left_pills, left_tops):
            pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.17), top_pos, Inches(4.21), Inches(0.62))
            pill.fill.solid()
            pill.fill.fore_color.rgb = COLOR_WHITE
            pill.line.color.rgb = COLOR_BURGUNDY
            pill.line.width = Pt(1.2)
            tf_p = pill.text_frame
            tf_p.word_wrap = True
            tf_p.margin_top = Inches(0.12)
            p_p = tf_p.paragraphs[0]
            p_p.text = p_text
            p_p.font.name = FONT_TITLE
            p_p.font.size = Pt(14)
            p_p.font.bold = True
            p_p.font.color.rgb = COLOR_BURGUNDY
            p_p.alignment = PP_ALIGN.CENTER

        # === CENTRAL CONNECTOR: Right Arrow + Paradigm Shift Badge ===
        arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(5.41), Inches(2.40), Inches(2.51), Inches(2.39))
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = RGBColor(0xDC, 0xE6, 0xF2)
        arrow.line.color.rgb = COLOR_NAVY
        arrow.line.width = Pt(1.0)

        badge = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.81), Inches(3.23), Inches(1.67), Inches(0.69))
        badge.fill.solid()
        badge.fill.fore_color.rgb = COLOR_WHITE
        badge.line.color.rgb = RGBColor(0x5A, 0x6B, 0x82)
        badge.line.width = Pt(1.0)

        tf_b = badge.text_frame
        tf_b.word_wrap = True
        tf_b.margin_top = Inches(0.08)
        p_b0 = tf_b.paragraphs[0]
        p_b0.text = "PARADIGM SHIFT"
        p_b0.font.name = FONT_TITLE
        p_b0.font.size = Pt(9.5)
        p_b0.font.bold = True
        p_b0.font.color.rgb = COLOR_NAVY
        p_b0.alignment = PP_ALIGN.CENTER

        p_b1 = tf_b.add_paragraph()
        p_b1.text = '"HOW" ➔ "WHAT"'
        p_b1.font.name = FONT_TITLE
        p_b1.font.size = Pt(9.5)
        p_b1.font.bold = True
        p_b1.font.color.rgb = COLOR_BURGUNDY
        p_b1.alignment = PP_ALIGN.CENTER

        # === RIGHT COLUMN: Declarative IBON ===
        card_r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.70), Inches(1.42), Inches(4.65), Inches(4.41))
        card_r.fill.solid()
        card_r.fill.fore_color.rgb = COLOR_CARD_BG
        card_r.line.color.rgb = COLOR_NAVY
        card_r.line.width = Pt(1.5)

        hdr_r = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.50), Inches(1.30), Inches(5.05), Inches(0.72))
        hdr_r.fill.solid()
        hdr_r.fill.fore_color.rgb = COLOR_NAVY
        hdr_r.line.fill.background()

        tf_hr = hdr_r.text_frame
        tf_hr.word_wrap = True
        tf_hr.margin_top = Inches(0.08)
        p_hr0 = tf_hr.paragraphs[0]
        p_hr0.text = "⚡ Target Vision: Declarative IBON"
        p_hr0.font.name = FONT_TITLE
        p_hr0.font.size = Pt(13.5)
        p_hr0.font.bold = True
        p_hr0.font.color.rgb = COLOR_WHITE
        p_hr0.alignment = PP_ALIGN.CENTER

        p_hr1 = tf_hr.add_paragraph()
        p_hr1.text = "Autonomous \"WHAT\" Abstraction • Closed-Loop Assurance"
        p_hr1.font.name = FONT_BODY
        p_hr1.font.size = Pt(10.5)
        p_hr1.font.color.rgb = COLOR_WHITE
        p_hr1.alignment = PP_ALIGN.CENTER

        right_pills = ["✓ High-Level Intents", "✓ Dynamic Physics", "✓ Zero-Touch Assurance"]
        right_tops = [Inches(2.46), Inches(3.315), Inches(4.17)]
        for p_text, top_pos in zip(right_pills, right_tops):
            pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.92), top_pos, Inches(4.21), Inches(0.62))
            pill.fill.solid()
            pill.fill.fore_color.rgb = COLOR_WHITE
            pill.line.color.rgb = COLOR_NAVY
            pill.line.width = Pt(1.2)
            tf_p = pill.text_frame
            tf_p.word_wrap = True
            tf_p.margin_top = Inches(0.12)
            p_p = tf_p.paragraphs[0]
            p_p.text = p_text
            p_p.font.name = FONT_TITLE
            p_p.font.size = Pt(14)
            p_p.font.bold = True
            p_p.font.color.rgb = COLOR_NAVY
            p_p.alignment = PP_ALIGN.CENTER

        # === BOTTOM WARNING BANNER ===
        banner_box = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.74), Inches(6.15), Inches(11.75), Inches(0.75)
        )
        banner_box.fill.solid()
        banner_box.fill.fore_color.rgb = COLOR_CARD_BG
        banner_box.line.color.rgb = COLOR_BURGUNDY
        banner_box.line.width = Pt(1.5)

        tf_bb = banner_box.text_frame
        tf_bb.word_wrap = True
        tf_bb.margin_top = Inches(0.18)
        p_bb = tf_bb.paragraphs[0]
        p_bb.text = "⚠️ BUT: Standard LLMs alone cannot simply drive an IBON controller"
        p_bb.font.name = FONT_TITLE
        p_bb.font.size = Pt(14.5)
        p_bb.font.bold = True
        p_bb.font.color.rgb = COLOR_BURGUNDY
        p_bb.alignment = PP_ALIGN.CENTER

        self.set_speaker_notes(s, notes)
        return s

    def create_five_challenges_slide(
        self,
        title: str,
        slide_num: int,
        challenges: list[dict],
        bottom_banner: str,
        notes: str,
    ):
        """Creates Slide 4: 5 horizontal cards mapping the 5 failure modes of Section 3.1.1."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        top_start = Inches(1.30)
        card_w = Inches(11.75)
        card_h = Inches(0.82)
        gap = Inches(0.14)

        for i, item in enumerate(challenges):
            cur_top = top_start + i * (card_h + gap)

            # Container card
            card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), cur_top, card_w, card_h
            )
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            card.line.color.rgb = COLOR_CARD_BORDER
            card.line.width = Pt(1)

            # Left Badge
            badge_w = Inches(3.65)
            badge = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), cur_top, badge_w, card_h
            )
            badge.fill.solid()
            badge.fill.fore_color.rgb = item.get("badge_color", COLOR_BURGUNDY)
            badge.line.fill.background()

            tf_b = badge.text_frame
            tf_b.word_wrap = True
            tf_b.margin_top = Inches(0.12)
            p_b = tf_b.paragraphs[0]
            p_b.text = item["badge_text"]
            p_b.font.name = FONT_TITLE
            p_b.font.size = Pt(14)
            p_b.font.bold = True
            p_b.font.color.rgb = COLOR_WHITE
            p_b.alignment = PP_ALIGN.CENTER

            # Right Description Text
            desc_box = s.shapes.add_textbox(
                Inches(4.55), cur_top, Inches(7.8), Inches(0.394)
            )
            tf_d = desc_box.text_frame
            tf_d.word_wrap = True
            tf_d.margin_top = Inches(0.14)
            p_d = tf_d.paragraphs[0]
            add_math_runs_to_paragraph(p_d, item["desc"], font_size=Pt(12), color=COLOR_DARK_SLATE, font_name=FONT_TITLE)

        # Bottom Empirical Risk Banner
        banner_box = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(6.20), card_w, Inches(0.65)
        )
        banner_box.fill.solid()
        banner_box.fill.fore_color.rgb = COLOR_CARD_BG
        banner_box.line.color.rgb = COLOR_BURGUNDY
        banner_box.line.width = Pt(1.5)

        tf_bb = banner_box.text_frame
        tf_bb.word_wrap = True
        tf_bb.margin_top = Inches(0.12)
        p_bb = tf_bb.paragraphs[0]
        add_math_runs_to_paragraph(p_bb, bottom_banner, font_size=Pt(12), color=COLOR_BURGUNDY, font_name=FONT_TITLE, bold=True)
        p_bb.alignment = PP_ALIGN.CENTER

        self.set_speaker_notes(s, notes)
        return s

    def create_problem_statement_slide(
        self,
        title: str,
        slide_num: int,
        upper_cards: list[dict],
        lower_constraints: dict,
        notes: str,
    ):
        """Creates Slide 5: 2-tier problem statement (Upper: Given, Decide, Objective; Lower: Constraints)."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        # === UPPER TIER: 3 Cards Side-by-Side ===
        top_u = Inches(1.30)
        h_u = Inches(2.65)
        w_u = Inches(3.75)
        gap_u = Inches(0.25)

        for i, card_data in enumerate(upper_cards):
            left_c = Inches(0.75) + i * (w_u + gap_u)

            # Container
            card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_c, top_u, w_u, h_u)
            card.fill.solid()
            card.fill.fore_color.rgb = COLOR_CARD_BG
            border_c = card_data.get("border_color", COLOR_NAVY)
            card.line.color.rgb = border_c
            card.line.width = Pt(1.5)

            # Header
            hdr_h = Inches(0.50)
            hdr = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_c, top_u, w_u, hdr_h)
            hdr.fill.solid()
            hdr.fill.fore_color.rgb = card_data.get("title_color", COLOR_NAVY)
            hdr.line.fill.background()

            p_h = hdr.text_frame.paragraphs[0]
            icon = card_data.get("icon", "")
            p_h.text = f"{icon} {card_data['title']}".strip()
            p_h.font.name = FONT_TITLE
            p_h.font.size = Pt(14)
            p_h.font.bold = True
            p_h.font.color.rgb = COLOR_WHITE
            p_h.alignment = PP_ALIGN.CENTER

            # 4 Rounded Pills inside card
            pill_w = Inches(3.21)
            pill_h = Inches(0.43)
            pill_l = left_c + Inches(0.27)
            pill_tops = [Inches(1.992), Inches(2.580), Inches(3.167), Inches(3.742)]

            bullets = card_data.get("bullets", [])
            for b_idx, b_text in enumerate(bullets[:4]):
                top_p = pill_tops[b_idx]
                pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, pill_l, top_p, pill_w, pill_h)
                pill.fill.solid()
                pill.fill.fore_color.rgb = COLOR_WHITE
                pill.line.color.rgb = COLOR_CARD_BORDER
                pill.line.width = Pt(1.0)

                tf_p = pill.text_frame
                tf_p.word_wrap = True
                tf_p.margin_top = Inches(0.04)
                tf_p.margin_bottom = Inches(0.04)
                tf_p.margin_left = Inches(0.06)
                tf_p.margin_right = Inches(0.06)

                lines = b_text.split("\n")
                p0 = tf_p.paragraphs[0]
                add_math_runs_to_paragraph(p0, lines[0], font_size=Pt(10), color=COLOR_DARK_SLATE, font_name=FONT_TITLE, bold=True)
                p0.alignment = PP_ALIGN.CENTER

                if len(lines) > 1:
                    p1 = tf_p.add_paragraph()
                    add_math_runs_to_paragraph(p1, lines[1], font_size=Pt(9.5), color=COLOR_DARK_SLATE, font_name=FONT_BODY)
                    p1.alignment = PP_ALIGN.CENTER

        # === LOWER TIER: Full-Width Constraints Container with 2 Columns ===
        top_l = Inches(4.734)
        h_l = Inches(2.128)
        w_l = Inches(10.308)
        left_l = Inches(1.471)

        card_lower = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_l, top_l, w_l, h_l)
        card_lower.fill.solid()
        card_lower.fill.fore_color.rgb = COLOR_CARD_BG
        card_lower.line.color.rgb = COLOR_BURGUNDY
        card_lower.line.width = Pt(1.5)

        # Header
        hdr_lh = Inches(0.48)
        hdr_l = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left_l, Inches(4.652), w_l, hdr_lh)
        hdr_l.fill.solid()
        hdr_l.fill.fore_color.rgb = COLOR_BURGUNDY
        hdr_l.line.fill.background()

        p_hl = hdr_l.text_frame.paragraphs[0]
        p_hl.text = lower_constraints.get("title", "🔒 [4] Constraints: Resource Limits vs. Physical & Semantic Boundaries")
        p_hl.font.name = FONT_TITLE
        p_hl.font.size = Pt(13)
        p_hl.font.bold = True
        p_hl.font.color.rgb = COLOR_WHITE
        p_hl.alignment = PP_ALIGN.CENTER

        # Left Sub-Panel: Resource Constraints
        sub_w = Inches(4.806)
        sub_h = Inches(1.134)
        sub_y = Inches(5.232)

        box_rc = s.shapes.add_textbox(Inches(1.577), sub_y, sub_w, sub_h)
        tf_rc = box_rc.text_frame
        tf_rc.word_wrap = True
        tf_rc.margin_top = Inches(0.02)
        p_rc_title = tf_rc.paragraphs[0]
        p_rc_title.text = lower_constraints.get("left_title", "Resource Constraints (System & Solver Limits):")
        p_rc_title.font.name = FONT_TITLE
        p_rc_title.font.size = Pt(11)
        p_rc_title.font.bold = True
        p_rc_title.font.color.rgb = COLOR_NAVY
        p_rc_title.space_after = Pt(2)

        for b_text in lower_constraints.get("left_bullets", []):
            add_bullet_with_math(tf_rc, f"•  {b_text}", font_size=Pt(10), color=COLOR_DARK_SLATE, space_after=Pt(2))

        # Right Sub-Panel: Boundary Constraints
        sub_hr = Inches(1.372)
        box_bc = s.shapes.add_textbox(Inches(6.867), sub_y, sub_w, sub_hr)
        tf_bc = box_bc.text_frame
        tf_bc.word_wrap = True
        tf_bc.margin_top = Inches(0.02)
        p_bc_title = tf_bc.paragraphs[0]
        p_bc_title.text = lower_constraints.get("right_title", "Boundary Constraints (Physical & Semantic Feasibility):")
        p_bc_title.font.name = FONT_TITLE
        p_bc_title.font.size = Pt(11)
        p_bc_title.font.bold = True
        p_bc_title.font.color.rgb = COLOR_BURGUNDY
        p_bc_title.space_after = Pt(2)

        for b_text in lower_constraints.get("right_bullets", []):
            add_bullet_with_math(tf_bc, f"•  {b_text}", font_size=Pt(10), color=COLOR_DARK_SLATE, space_after=Pt(2))

        self.set_speaker_notes(s, notes)
        return s

    def create_proposed_solution_slide(
        self,
        title: str,
        slide_num: int,
        neural_data: dict,
        symbolic_data: dict,
        contributions_header: str,
        contributions: list[dict],
        notes: str,
    ):
        """
        Creates Slide 6: Proposed Solution & Core Contributions.
        Left Column: 2 vertically stacked cards (Neural Subsystem: Semantic Domain on top,
                     Symbolic Subsystem: Optical Domain on bottom).
        Right Column: Core Thesis Contributions header with 3 stacked highlight blocks.
        """
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num, title_h=0.572)

        # === LEFT COLUMN: Two Vertically Stacked Subsystems ===
        left_col_x = Inches(0.75)
        left_col_w = Inches(5.7)

        # 1. Top Card: Neural Subsystem (Semantic Domain)
        top_y = Inches(1.30)
        card_h = Inches(2.72)
        card_l1 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_col_x, top_y, left_col_w, card_h
        )
        card_l1.fill.solid()
        card_l1.fill.fore_color.rgb = COLOR_CARD_BG
        card_l1.line.color.rgb = COLOR_NAVY
        card_l1.line.width = Pt(1.5)

        hdr_l1 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_col_x, top_y, left_col_w, Inches(0.55)
        )
        hdr_l1.fill.solid()
        hdr_l1.fill.fore_color.rgb = COLOR_NAVY
        hdr_l1.line.fill.background()
        p_hl1 = hdr_l1.text_frame.paragraphs[0]
        p_hl1.text = neural_data["title"]
        p_hl1.font.name = FONT_TITLE
        p_hl1.font.size = Pt(14)
        p_hl1.font.bold = True
        p_hl1.font.color.rgb = COLOR_WHITE
        p_hl1.alignment = PP_ALIGN.CENTER

        # 3 White Rounded Pills for Neural Subsystem
        pill_l = Inches(1.593)
        pill_w = Inches(3.967)
        pill_h = Inches(0.43)
        neural_tops = [Inches(2.065), Inches(2.612), Inches(3.210)]
        neural_pills = neural_data.get("pills", [
            "Translation of the intent",
            "Validation of the semantic similarity",
            "Orchestration",
        ])
        for p_idx, p_text in enumerate(neural_pills[:3]):
            p_shape = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, pill_l, neural_tops[p_idx], pill_w, pill_h
            )
            p_shape.fill.solid()
            p_shape.fill.fore_color.rgb = COLOR_WHITE
            p_shape.line.color.rgb = COLOR_CARD_BORDER
            p_shape.line.width = Pt(1.0)
            tf_p = p_shape.text_frame
            tf_p.word_wrap = True
            tf_p.margin_top = Inches(0.06)
            tf_p.margin_bottom = Inches(0.06)
            p_para = tf_p.paragraphs[0]
            p_para.text = p_text
            p_para.font.name = FONT_TITLE
            p_para.font.size = Pt(12)
            p_para.font.bold = True
            p_para.font.color.rgb = COLOR_DARK_SLATE
            p_para.alignment = PP_ALIGN.CENTER

        # 2. Bottom Card: Symbolic Subsystem (Optical Domain)
        bottom_y = Inches(4.18)
        card_l2 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_col_x, bottom_y, left_col_w, card_h
        )
        card_l2.fill.solid()
        card_l2.fill.fore_color.rgb = COLOR_CARD_BG
        card_l2.line.color.rgb = COLOR_GREEN
        card_l2.line.width = Pt(1.5)

        hdr_l2 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_col_x, bottom_y, left_col_w, Inches(0.55)
        )
        hdr_l2.fill.solid()
        hdr_l2.fill.fore_color.rgb = COLOR_GREEN
        hdr_l2.line.fill.background()
        p_hl2 = hdr_l2.text_frame.paragraphs[0]
        p_hl2.text = symbolic_data["title"]
        p_hl2.font.name = FONT_TITLE
        p_hl2.font.size = Pt(14)
        p_hl2.font.bold = True
        p_hl2.font.color.rgb = COLOR_WHITE
        p_hl2.alignment = PP_ALIGN.CENTER

        # 3 White Rounded Pills for Symbolic Subsystem
        symbolic_tops = [Inches(4.977), Inches(5.524), Inches(6.122)]
        symbolic_pills = symbolic_data.get("pills", [
            "Topology extraction",
            "Compute candidate lightpaths",
            "Physical feasibility validation",
        ])
        for p_idx, p_text in enumerate(symbolic_pills[:3]):
            p_shape = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, pill_l, symbolic_tops[p_idx], pill_w, pill_h
            )
            p_shape.fill.solid()
            p_shape.fill.fore_color.rgb = COLOR_WHITE
            p_shape.line.color.rgb = COLOR_CARD_BORDER
            p_shape.line.width = Pt(1.0)
            tf_p = p_shape.text_frame
            tf_p.word_wrap = True
            tf_p.margin_top = Inches(0.06)
            tf_p.margin_bottom = Inches(0.06)
            p_para = tf_p.paragraphs[0]
            p_para.text = p_text
            p_para.font.name = FONT_TITLE
            p_para.font.size = Pt(12)
            p_para.font.bold = True
            p_para.font.color.rgb = COLOR_DARK_SLATE
            p_para.alignment = PP_ALIGN.CENTER

        # === RIGHT COLUMN: Core Thesis Contributions (3 Stacked Blocks) ===
        right_col_x = Inches(6.8)
        right_col_w = Inches(5.75)

        # Header Bar across right column
        hdr_r = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, right_col_x, Inches(1.30), right_col_w, Inches(0.55)
        )
        hdr_r.fill.solid()
        hdr_r.fill.fore_color.rgb = COLOR_NAVY
        hdr_r.line.fill.background()
        p_hr = hdr_r.text_frame.paragraphs[0]
        p_hr.text = contributions_header
        p_hr.font.name = FONT_TITLE
        p_hr.font.size = Pt(13)
        p_hr.font.bold = True
        p_hr.font.color.rgb = COLOR_WHITE
        p_hr.alignment = PP_ALIGN.CENTER

        # 3 Stacked Contribution Blocks
        num_contribs = len(contributions)
        r_top_start = Inches(1.95)
        r_total_h = Inches(4.95)
        r_gap = Inches(0.12)
        block_h = (r_total_h - (num_contribs - 1) * r_gap) / num_contribs

        for i, contrib in enumerate(contributions):
            cur_top = r_top_start + i * (block_h + r_gap)
            c_card = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, right_col_x, cur_top, right_col_w, block_h
            )
            c_card.fill.solid()
            c_card.fill.fore_color.rgb = COLOR_CARD_BG
            b_color = contrib.get("border_color", COLOR_NAVY)
            c_card.line.color.rgb = b_color
            c_card.line.width = Pt(1.5)

            tb_c = s.shapes.add_textbox(
                right_col_x + Inches(0.15), cur_top + Inches(0.08), right_col_w - Inches(0.3), block_h - Inches(0.16)
            )
            tf_c = tb_c.text_frame
            tf_c.word_wrap = True
            tf_c.margin_top = Inches(0.02)
            tf_c.margin_bottom = Inches(0.02)

            p_ctitle = tf_c.paragraphs[0]
            add_math_runs_to_paragraph(p_ctitle, contrib["title"], font_size=Pt(12), color=b_color, font_name=FONT_TITLE, bold=True)
            p_ctitle.space_after = Pt(2)

            for b_text in contrib.get("bullets", []):
                add_bullet_with_math(tf_c, f"•  {b_text}", font_size=Pt(10), color=COLOR_DARK_SLATE, space_after=Pt(2))

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
                add_bullet_with_math(tf_b, f"•  {b_text}", font_size=Pt(12), color=COLOR_DARK_SLATE, space_after=Pt(6))

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
                    add_omml_equation(p_eq, f_xml, font_size=Pt(11), color=border_col)

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

            # Body Text inside transparent textbox over phase card
            tb_body = s.shapes.add_textbox(
                cur_left + Inches(0.04),
                top_pos + badge_h + Inches(0.04),
                phase_width - Inches(0.08),
                phase_height - badge_h - Inches(0.08),
            )
            tf_body = tb_body.text_frame
            tf_body.word_wrap = True
            tf_body.margin_top = Inches(0.06)
            tf_body.margin_left = Inches(0.04)
            tf_body.margin_right = Inches(0.04)

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

            if isinstance(phase["desc"], list):
                for d_idx, desc_item in enumerate(phase["desc"]):
                    p_d = tf_body.add_paragraph()
                    p_d.space_before = Pt(2 if d_idx > 0 else 4)
                    p_d.alignment = PP_ALIGN.LEFT
                    add_math_runs_to_paragraph(p_d, f"•  {desc_item}", font_size=Pt(9.5), color=COLOR_DARK_SLATE, font_name=FONT_BODY)
            else:
                p_d = tf_body.add_paragraph()
                p_d.space_before = Pt(4)
                p_d.alignment = PP_ALIGN.LEFT
                add_math_runs_to_paragraph(p_d, phase["desc"], font_size=Pt(9.5), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

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

        tb_l1 = s.shapes.add_textbox(Inches(0.75), Inches(5.88), Inches(5.6), Inches(0.88))
        tf_l1 = tb_l1.text_frame
        tf_l1.word_wrap = True
        tf_l1.margin_top = Inches(0.04)
        p_l1 = tf_l1.paragraphs[0]
        p_l1.text = "⏸️ Phase 3b: Clarify Loop (LangGraph interrupt())"
        p_l1.font.name = FONT_TITLE
        p_l1.font.size = Pt(12)
        p_l1.font.bold = True
        p_l1.font.color.rgb = COLOR_AMBER
        p_l1_sub = tf_l1.add_paragraph()
        add_math_runs_to_paragraph(p_l1_sub, "If $U_{sem} > \\tau_{sem}$: Pauses execution and prompts operator for intent disambiguation", font_size=Pt(10), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

        loop2 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(5.85), Inches(5.7), Inches(0.95)
        )
        loop2.fill.solid()
        loop2.fill.fore_color.rgb = COLOR_CARD_BG
        loop2.line.color.rgb = COLOR_BURGUNDY
        loop2.line.width = Pt(1.5)

        tb_l2 = s.shapes.add_textbox(Inches(6.85), Inches(5.88), Inches(5.6), Inches(0.88))
        tf_l2 = tb_l2.text_frame
        tf_l2.word_wrap = True
        tf_l2.margin_top = Inches(0.04)
        p_l2 = tf_l2.paragraphs[0]
        p_l2.text = "↺ Phase 6: Suggest Replan Loop (Physics Unfeasible)"
        p_l2.font.name = FONT_TITLE
        p_l2.font.size = Pt(12)
        p_l2.font.bold = True
        p_l2.font.color.rgb = COLOR_BURGUNDY
        p_l2_sub = tf_l2.add_paragraph()
        add_math_runs_to_paragraph(p_l2_sub, "If $\\text{QoT}_{valid} = 0$: Suggests operator to relax constraints (lower baud rate, alternate link)", font_size=Pt(10), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

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
            Inches(0.95), Inches(1.4), Inches(11.4), Inches(1.5)
        )
        tf_top = top_box.text_frame
        tf_top.word_wrap = True

        p_hdr = tf_top.paragraphs[0]
        p_hdr.text = "Piecewise Decision Formulation:"
        p_hdr.font.name = FONT_TITLE
        p_hdr.font.size = Pt(16)
        p_hdr.font.bold = True
        p_hdr.font.color.rgb = COLOR_NAVY

        # Spacing
        tf_top.add_paragraph()

        # Inject piecewise equation
        p_eq = tf_top.add_paragraph()
        p_eq.alignment = PP_ALIGN.CENTER
        add_omml_equation(p_eq, formula_xml, font_size=Pt(13), color=COLOR_NAVY)

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

            # Header Bar with OMML Condition
            h_bar = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, b_left, Inches(3.649), b_width, Inches(0.851)
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

            p_bheq = tf_bh.add_paragraph()
            p_bheq.alignment = PP_ALIGN.CENTER
            add_omml_equation(p_bheq, branch.get("condition_xml", ""), font_size=Pt(12), color=COLOR_WHITE)

            # Body text inside transparent textbox
            b_body_h = Inches(1.38) if i < 2 else Inches(1.01)
            b_body_box = s.shapes.add_textbox(
                b_left + Inches(0.167),
                Inches(4.705),
                b_width - Inches(0.3),
                b_body_h,
            )
            tf_bbody = b_body_box.text_frame
            tf_bbody.word_wrap = True

            for j, item in enumerate(branch.get("bullets", [])):
                if j == 0:
                    p_b = tf_bbody.paragraphs[0]
                    add_math_runs_to_paragraph(p_b, f"•  {item}", font_size=Pt(11), color=COLOR_DARK_SLATE, font_name=FONT_BODY)
                    p_b.space_after = Pt(3)
                else:
                    add_bullet_with_math(tf_bbody, f"•  {item}", font_size=Pt(11), color=COLOR_DARK_SLATE, space_after=Pt(3))

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

            tb = s.shapes.add_textbox(
                left_pos + Inches(0.15), cur_top + Inches(0.08), left_width - Inches(0.3), kpi_height - Inches(0.16)
            )
            tf = tb.text_frame
            tf.word_wrap = True
            tf.margin_left = Inches(0.05)
            tf.margin_top = Inches(0.05)

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
            add_math_runs_to_paragraph(p_sub, kpi["subtitle"], font_size=Pt(10), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

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

    def create_evaluation_framework_slide(
        self,
        title: str,
        slide_num: int,
        baselines_info: dict,
        corpus_info: dict,
        pillars: list[dict],
        notes: str,
    ):
        """Creates the Slide 13 Evaluation Framework featuring Baselines + Corpus on the left and 4 Validation Pillars on the right."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        # Left Column: Setup & Benchmarks (Baselines + Corpus)
        left_pos = Inches(0.75)
        left_width = Inches(4.6)
        top_start = Inches(1.25)

        # 1. Top Card: Architectural Baselines Container
        base_top = top_start
        base_h = Inches(2.65)
        card_base = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, base_top, left_width, base_h
        )
        card_base.fill.solid()
        card_base.fill.fore_color.rgb = COLOR_CARD_BG
        card_base.line.color.rgb = COLOR_NAVY
        card_base.line.width = Pt(1.5)

        tf_cb = card_base.text_frame
        p_vs = tf_cb.paragraphs[0]
        p_vs.text = "vs."
        p_vs.alignment = PP_ALIGN.CENTER
        p_vs.font.name = FONT_BODY
        p_vs.font.size = Pt(13)
        p_vs.font.bold = True
        p_vs.font.color.rgb = COLOR_COOL_GRAY

        # Header Bar for Baselines
        h_base = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, Inches(1.21), left_width, Inches(0.52)
        )
        h_base.fill.solid()
        h_base.fill.fore_color.rgb = COLOR_NAVY
        h_base.line.fill.background()
        tf_hb = h_base.text_frame
        p_hb = tf_hb.paragraphs[0]
        p_hb.text = f"{baselines_info['icon']} {baselines_info['title']}" if baselines_info.get("icon") else baselines_info["title"]
        p_hb.font.name = FONT_TITLE
        p_hb.font.size = Pt(12)
        p_hb.font.bold = True
        p_hb.font.color.rgb = COLOR_WHITE
        p_hb.alignment = PP_ALIGN.CENTER

        # 2. Bottom Card: 100 Test Demands Container
        corpus_top = Inches(4.05)
        corpus_h = Inches(2.85)
        card_corp = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, corpus_top, left_width, corpus_h
        )
        card_corp.fill.solid()
        card_corp.fill.fore_color.rgb = COLOR_CARD_BG
        card_corp.line.color.rgb = COLOR_BURGUNDY
        card_corp.line.width = Pt(1.5)

        h_corp = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, left_pos, corpus_top, left_width, Inches(0.48)
        )
        h_corp.fill.solid()
        h_corp.fill.fore_color.rgb = COLOR_BURGUNDY
        h_corp.line.fill.background()
        tf_hc = h_corp.text_frame
        p_hc = tf_hc.paragraphs[0]
        p_hc.text = f"{corpus_info['icon']} {corpus_info['title']}" if corpus_info.get("icon") else corpus_info["title"]
        p_hc.font.name = FONT_TITLE
        p_hc.font.size = Pt(12)
        p_hc.font.bold = True
        p_hc.font.color.rgb = COLOR_WHITE
        p_hc.alignment = PP_ALIGN.CENTER

        # Table: 100 Test Demands (4 Risk Classes)
        t_shape = s.shapes.add_table(5, 3, Inches(0.978), Inches(4.53), Inches(4.144), Inches(2.215))
        table = t_shape.table
        table.columns[0].width = Inches(1.366)
        table.columns[1].width = Inches(1.648)
        table.columns[2].width = Inches(1.130)

        t_headers = ["Class & Size", "Intent Characteristics", "RADG Action"]
        for j, h in enumerate(t_headers):
            cell = table.cell(0, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = COLOR_NAVY
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.05)
            cell.margin_right = Inches(0.05)
            cell.margin_top = Inches(0.02)
            cell.margin_bottom = Inches(0.02)
            p = cell.text_frame.paragraphs[0]
            p.text = h
            p.alignment = PP_ALIGN.CENTER
            for r in p.runs:
                r.font.name = FONT_TITLE
                r.font.size = Pt(9.5)
                r.font.bold = True
                r.font.color.rgb = COLOR_WHITE

        table_data = corpus_info.get("table_rows", [
            ("Class I: Nominal [40]", "Feasible path, unambiguous", "Auto-Approve", COLOR_GREEN),
            ("Class II: Ambiguous [20]", "Under-specified (U_sem > τ)", "Clarify Intent", COLOR_AMBER),
            ("Class III: Infeasible [25]", "Violates GSNR threshold", "Suggest Replan", COLOR_BURGUNDY),
            ("Class IV: Adversarial [15]", "Hallucinated nodes (v_struct=0)", "Reject Intent", COLOR_BURGUNDY),
        ])

        for row_idx, (c_name, c_char, c_act, act_color) in enumerate(table_data, start=1):
            bg_color = COLOR_WHITE if row_idx % 2 == 1 else COLOR_CARD_BG
            for col_idx in range(3):
                cell = table.cell(row_idx, col_idx)
                cell.fill.solid()
                cell.fill.fore_color.rgb = bg_color
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                cell.margin_left = Inches(0.05)
                cell.margin_right = Inches(0.05)
                cell.margin_top = Inches(0.02)
                cell.margin_bottom = Inches(0.02)
                p = cell.text_frame.paragraphs[0]
                if col_idx == 0:
                    p.text = c_name
                    p.alignment = PP_ALIGN.LEFT
                    for r in p.runs:
                        r.font.name = FONT_BODY
                        r.font.size = Pt(9.0)
                        r.font.bold = True
                        r.font.color.rgb = COLOR_DARK_SLATE
                elif col_idx == 1:
                    p.text = c_char
                    p.alignment = PP_ALIGN.LEFT
                    for r in p.runs:
                        r.font.name = FONT_BODY
                        r.font.size = Pt(8.8)
                        r.font.color.rgb = COLOR_DARK_SLATE
                else:
                    p.text = c_act
                    p.alignment = PP_ALIGN.CENTER
                    for r in p.runs:
                        r.font.name = FONT_BODY
                        r.font.size = Pt(9.0)
                        r.font.bold = True
                        r.font.color.rgb = act_color

        # Right Column: 4 Stacked Pillar Cards (floating directly on slide)
        subcard_left = Inches(5.75)
        subcard_w = Inches(6.65)
        p_card_h = Inches(1.15)
        p_gap = Inches(0.1)
        p_top_start = Inches(1.87)

        for i, pillar in enumerate(pillars):
            cur_p_top = p_top_start + i * (p_card_h + p_gap)
            p_color = pillar.get("color", COLOR_NAVY)

            subcard = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, subcard_left, cur_p_top, subcard_w, p_card_h
            )
            subcard.fill.solid()
            subcard.fill.fore_color.rgb = COLOR_WHITE
            subcard.line.color.rgb = p_color
            subcard.line.width = Pt(1.5)

            tb_pillar = s.shapes.add_textbox(
                subcard_left + Inches(0.12), cur_p_top + Inches(0.04), subcard_w - Inches(0.24), p_card_h - Inches(0.08)
            )
            tf_p = tb_pillar.text_frame
            tf_p.word_wrap = True
            tf_p.margin_top = Inches(0.02)
            tf_p.margin_left = Inches(0.02)

            # Title line
            p_title = tf_p.paragraphs[0]
            p_title.text = f"{pillar['icon']} {pillar['title']}" if pillar.get("icon") else pillar["title"]
            p_title.font.name = FONT_TITLE
            p_title.font.size = Pt(11)
            p_title.font.bold = True
            p_title.font.color.rgb = p_color

            # Focus line
            p_foc = tf_p.add_paragraph()
            p_foc.space_before = Pt(1)
            add_math_runs_to_paragraph(p_foc, f"•  Test Focus: {pillar['focus']}", font_size=Pt(9.2), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

            # Metrics line
            p_met = tf_p.add_paragraph()
            p_met.space_before = Pt(1)
            add_math_runs_to_paragraph(p_met, f"•  Key Metrics: {pillar['metrics']}", font_size=Pt(9.2), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

        # Baseline Sub-Cards inside Top Card
        # 1. Baseline A Pill
        card_b_a = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.1), Inches(1.99), Inches(1.6), Inches(0.625)
        )
        card_b_a.fill.solid()
        card_b_a.fill.fore_color.rgb = COLOR_WHITE
        card_b_a.line.color.rgb = COLOR_CARD_BORDER
        card_b_a.line.width = Pt(1.0)
        tf_ba = card_b_a.text_frame
        tf_ba.margin_left = Inches(0.1)
        tf_ba.margin_right = Inches(0.1)
        tf_ba.margin_top = Inches(0.05)
        tf_ba.margin_bottom = Inches(0.05)
        p_ba1 = tf_ba.paragraphs[0]
        p_ba1.text = "Baseline A"
        p_ba1.alignment = PP_ALIGN.CENTER
        for r in p_ba1.runs:
            r.font.name = FONT_TITLE
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = COLOR_NAVY
        p_ba2 = tf_ba.add_paragraph()
        p_ba2.text = "LLM-Only"
        p_ba2.alignment = PP_ALIGN.CENTER
        for r in p_ba2.runs:
            r.font.name = FONT_BODY
            r.font.size = Pt(10.5)
            r.font.color.rgb = COLOR_DARK_SLATE

        # 2. Baseline B Pill
        card_b_b = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(3.41), Inches(1.99), Inches(1.6), Inches(0.625)
        )
        card_b_b.fill.solid()
        card_b_b.fill.fore_color.rgb = COLOR_WHITE
        card_b_b.line.color.rgb = COLOR_CARD_BORDER
        card_b_b.line.width = Pt(1.0)
        tf_bb = card_b_b.text_frame
        tf_bb.margin_left = Inches(0.1)
        tf_bb.margin_right = Inches(0.1)
        tf_bb.margin_top = Inches(0.05)
        tf_bb.margin_bottom = Inches(0.05)
        p_bb1 = tf_bb.paragraphs[0]
        p_bb1.text = "Baseline B"
        p_bb1.alignment = PP_ALIGN.CENTER
        for r in p_bb1.runs:
            r.font.name = FONT_TITLE
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = COLOR_NAVY
        p_bb2 = tf_bb.add_paragraph()
        p_bb2.text = "Always-HITL"
        p_bb2.alignment = PP_ALIGN.CENTER
        for r in p_bb2.runs:
            r.font.name = FONT_BODY
            r.font.size = Pt(10.5)
            r.font.color.rgb = COLOR_DARK_SLATE

        # 3. Proposed Neurosymbolic RADG Full-Width Pill
        card_prop = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.906), Inches(2.925), Inches(4.324), Inches(0.645)
        )
        card_prop.fill.solid()
        card_prop.fill.fore_color.rgb = COLOR_WHITE
        card_prop.line.color.rgb = COLOR_GREEN
        card_prop.line.width = Pt(1.0)
        tf_cp = card_prop.text_frame
        tf_cp.margin_left = Inches(0.1)
        tf_cp.margin_right = Inches(0.1)
        tf_cp.margin_top = Inches(0.05)
        tf_cp.margin_bottom = Inches(0.05)
        p_cp1 = tf_cp.paragraphs[0]
        p_cp1.text = "Proposed Neurosymbolic RADG"
        p_cp1.alignment = PP_ALIGN.CENTER
        for r in p_cp1.runs:
            r.font.name = FONT_TITLE
            r.font.size = Pt(14)
            r.font.bold = True
            r.font.color.rgb = COLOR_GREEN
        p_cp2 = tf_cp.add_paragraph()
        p_cp2.text = "Decoupled translation + sequential pre-deployment risk gates"
        p_cp2.alignment = PP_ALIGN.CENTER
        for r in p_cp2.runs:
            r.font.name = FONT_BODY
            r.font.size = Pt(10.5)
            r.font.color.rgb = COLOR_DARK_SLATE

        self.set_speaker_notes(s, notes)
        return s

    def create_split_diagram_slide(
        self,
        title: str,
        slide_num: int,
        content_data: dict,
        placeholder_info: dict | None = None,
        notes: str = "",
        formulas: list[str] | None = None,
        animated_image_pair: dict | None = None,
        image_info: dict | None = None,
    ):
        """Creates a split slide with structured text cards on the left and a diagram/figure placeholder or animated image pair on the right."""
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
        icon = content_data.get("icon", "")
        p_h.text = f"{icon} {content_data['title']}".strip()
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
            add_bullet_with_math(tf_b, f"•  {b_text}", font_size=Pt(11), color=COLOR_DARK_SLATE, space_after=Pt(5))

        if formulas:
            p_f_lbl = tf_b.add_paragraph()
            p_f_lbl.text = "Mathematical Scoping Bound:"
            p_f_lbl.font.name = FONT_TITLE
            p_f_lbl.font.size = Pt(11)
            p_f_lbl.font.bold = True
            p_f_lbl.font.color.rgb = content_data.get("title_color", COLOR_NAVY)
            p_f_lbl.space_before = Pt(4)

            for f_xml in formulas:
                p_eq = tf_b.add_paragraph()
                p_eq.alignment = PP_ALIGN.CENTER
                add_omml_equation(p_eq, f_xml, font_size=Pt(12), color=content_data.get("title_color", COLOR_NAVY))

        # Right Column: Animated Image Pair or Placeholder Box
        right_pos = Inches(6.65)
        right_width = Inches(5.9)

        if animated_image_pair:
            # 1. Container Card
            card_r = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, right_pos, top_pos, right_width, content_height
            )
            card_r.fill.solid()
            card_r.fill.fore_color.rgb = COLOR_CARD_BG
            card_r.line.color.rgb = content_data.get("border_color", COLOR_NAVY)
            card_r.line.width = Pt(1.5)

            # 2. Header Bar
            header_rh = Inches(0.55)
            header_r = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, right_pos, top_pos, right_width, header_rh
            )
            header_r.fill.solid()
            header_r.fill.fore_color.rgb = content_data.get("title_color", COLOR_NAVY)
            header_r.line.fill.background()

            tf_rh = header_r.text_frame
            p_rh = tf_rh.paragraphs[0]
            card_title = animated_image_pair.get("title", "🗺️ 17-Node German Core: Scoped Subnetwork")
            p_rh.text = card_title
            p_rh.font.name = FONT_TITLE
            p_rh.font.size = Pt(14)
            p_rh.font.bold = True
            p_rh.font.color.rgb = COLOR_WHITE
            p_rh.alignment = PP_ALIGN.CENTER

            # 3. Bottom Banner / Caption Callout
            caption_text = animated_image_pair.get("caption")
            banner_h = Inches(0.48) if caption_text else Inches(0)
            if caption_text:
                banner_top = top_pos + content_height - banner_h - Inches(0.12)
                banner_left = right_pos + Inches(0.2)
                banner_w = right_width - Inches(0.4)
                banner = s.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE, banner_left, banner_top, banner_w, banner_h
                )
                banner.fill.solid()
                banner.fill.fore_color.rgb = COLOR_WHITE
                banner.line.color.rgb = COLOR_CARD_BORDER
                banner.line.width = Pt(1)

                tf_bn = banner.text_frame
                tf_bn.word_wrap = True
                p_bn = tf_bn.paragraphs[0]
                p_bn.text = caption_text
                p_bn.font.name = FONT_TITLE
                p_bn.font.size = Pt(10.5)
                p_bn.font.bold = True
                p_bn.font.color.rgb = COLOR_NAVY
                p_bn.alignment = PP_ALIGN.CENTER

            # 4. Images: Base (full topology) & Overlay (scoped subnetwork)
            img_w = Inches(5.5)
            img_h = Inches(3.67)
            img_left = right_pos + (right_width - img_w) / 2
            avail_h = content_height - header_rh - banner_h - Inches(0.2)
            img_top = top_pos + header_rh + (avail_h - img_h) / 2

            base_img_path = str(animated_image_pair["base_image"])
            overlay_img_path = str(animated_image_pair["overlay_image"])

            pic_base = s.shapes.add_picture(base_img_path, img_left, img_top, width=img_w, height=img_h)
            pic_base.line.color.rgb = COLOR_CARD_BORDER
            pic_base.line.width = Pt(1)

            pic_overlay = s.shapes.add_picture(overlay_img_path, img_left, img_top, width=img_w, height=img_h)
            pic_overlay.line.color.rgb = COLOR_CARD_BORDER
            pic_overlay.line.width = Pt(1)

            # 5. Entrance Animation on Click/Advance for Overlay Image
            self.add_entrance_click_animation(s, pic_overlay.shape_id)

        elif image_info:
            # 1. Container Card
            card_r = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, right_pos, top_pos, right_width, content_height
            )
            card_r.fill.solid()
            card_r.fill.fore_color.rgb = COLOR_CARD_BG
            card_r.line.color.rgb = content_data.get("border_color", COLOR_NAVY)
            card_r.line.width = Pt(1.5)

            # 2. Header Bar
            header_rh = Inches(0.55)
            header_r = s.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, right_pos, top_pos, right_width, header_rh
            )
            header_r.fill.solid()
            header_r.fill.fore_color.rgb = content_data.get("title_color", COLOR_NAVY)
            header_r.line.fill.background()

            tf_rh = header_r.text_frame
            p_rh = tf_rh.paragraphs[0]
            card_title = image_info.get("title", "🗺️ Network Topology Map")
            p_rh.text = card_title
            p_rh.font.name = FONT_TITLE
            p_rh.font.size = Pt(14)
            p_rh.font.bold = True
            p_rh.font.color.rgb = COLOR_WHITE
            p_rh.alignment = PP_ALIGN.CENTER

            # 3. Bottom Banner / Caption Callout
            caption_text = image_info.get("caption")
            banner_h = Inches(0.48) if caption_text else Inches(0)
            if caption_text:
                banner_top = top_pos + content_height - banner_h - Inches(0.12)
                banner_left = right_pos + Inches(0.2)
                banner_w = right_width - Inches(0.4)
                banner = s.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE, banner_left, banner_top, banner_w, banner_h
                )
                banner.fill.solid()
                banner.fill.fore_color.rgb = COLOR_WHITE
                banner.line.color.rgb = COLOR_CARD_BORDER
                banner.line.width = Pt(1)

                tf_bn = banner.text_frame
                tf_bn.word_wrap = True
                p_bn = tf_bn.paragraphs[0]
                p_bn.text = caption_text
                p_bn.font.name = FONT_TITLE
                p_bn.font.size = Pt(10.5)
                p_bn.font.bold = True
                p_bn.font.color.rgb = COLOR_NAVY
                p_bn.alignment = PP_ALIGN.CENTER

            # 4. Single Picture
            img_w = Inches(5.5)
            img_h = Inches(3.67)
            img_left = right_pos + (right_width - img_w) / 2
            avail_h = content_height - header_rh - banner_h - Inches(0.2)
            img_top = top_pos + header_rh + (avail_h - img_h) / 2

            img_path = str(image_info["image_path"])
            pic = s.shapes.add_picture(img_path, img_left, img_top, width=img_w, height=img_h)
            pic.line.color.rgb = COLOR_CARD_BORDER
            pic.line.width = Pt(1)

        elif placeholder_info:
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

    def create_scoped_graphrag_slide(
        self,
        title: str,
        slide_num: int,
        base_img_path: Path,
        overlay_img_path: Path,
        notes: str = "",
    ):
        """Creates Slide 8: Overcoming Token Saturation with Scoped Optical GraphRAG.
        Features a 3-stage vertical pill flow connected by a down arrow,
        the mathematical scoping bound equations, and the 17-node German backbone network map."""
        blank_layout = self.prs.slide_layouts[6]
        s = self.prs.slides.add_slide(blank_layout)
        self.add_chrome(s, title, slide_num)

        # 1. Large background container card
        card_l = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.833), Inches(1.300), Inches(9.300), Inches(5.350)
        )
        card_l.fill.solid()
        card_l.fill.fore_color.rgb = COLOR_CARD_BG
        card_l.line.color.rgb = COLOR_NAVY
        card_l.line.width = Pt(1.5)

        # 2. Header Bar Badge
        header_bar = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.750), Inches(1.244), Inches(5.600), Inches(0.706)
        )
        header_bar.fill.solid()
        header_bar.fill.fore_color.rgb = COLOR_NAVY
        header_bar.line.fill.background()

        tf_h = header_bar.text_frame
        p_h = tf_h.paragraphs[0]
        p_h.text = "Deterministic Subtopology Scoping"
        p_h.font.name = FONT_TITLE
        p_h.font.size = Pt(15)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_h.alignment = PP_ALIGN.CENTER

        # 3. Down Arrow connecting the pills (placed before pills in z-order so white pills sit on top)
        arrow = s.shapes.add_shape(
            MSO_SHAPE.DOWN_ARROW, Inches(3.311), Inches(2.075), Inches(0.767), Inches(2.258)
        )
        arrow.fill.solid()
        arrow.fill.fore_color.rgb = COLOR_BURGUNDY
        arrow.line.color.rgb = COLOR_CARD_BG

        # 4. Pill 1 (Top)
        pill1 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.103), Inches(2.222), Inches(3.183), Inches(0.623)
        )
        pill1.fill.solid()
        pill1.fill.fore_color.rgb = COLOR_WHITE
        pill1.line.color.rgb = COLOR_CARD_BORDER
        pill1.line.width = Pt(1.0)
        tf_p1 = pill1.text_frame
        tf_p1.word_wrap = True
        tf_p1.margin_top = Inches(0.04)
        tf_p1.margin_bottom = Inches(0.04)
        p1_0 = tf_p1.paragraphs[0]
        p1_0.text = "Raw JSON contains excessive telemetry:"
        p1_0.font.name = FONT_TITLE
        p1_0.font.size = Pt(12)
        p1_0.font.bold = True
        p1_0.font.color.rgb = COLOR_DARK_SLATE
        p1_0.alignment = PP_ALIGN.CENTER
        p1_1 = tf_p1.add_paragraph()
        p1_1.text = "ROADM ports, EDFAs, fibers"
        p1_1.font.name = FONT_TITLE
        p1_1.font.size = Pt(12)
        p1_1.font.bold = True
        p1_1.font.color.rgb = COLOR_DARK_SLATE
        p1_1.alignment = PP_ALIGN.CENTER

        # 5. Pill 2 (Middle)
        pill2 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.069), Inches(3.105), Inches(3.217), Inches(0.623)
        )
        pill2.fill.solid()
        pill2.fill.fore_color.rgb = COLOR_WHITE
        pill2.line.color.rgb = COLOR_CARD_BORDER
        pill2.line.width = Pt(1.0)
        tf_p2 = pill2.text_frame
        tf_p2.word_wrap = True
        tf_p2.margin_top = Inches(0.1)
        tf_p2.margin_bottom = Inches(0.04)
        p2_0 = tf_p2.paragraphs[0]
        p2_0.text = "Full topology dumps overwhelm LLM context windows"
        p2_0.font.name = FONT_TITLE
        p2_0.font.size = Pt(12)
        p2_0.font.bold = True
        p2_0.font.color.rgb = COLOR_DARK_SLATE
        p2_0.alignment = PP_ALIGN.CENTER

        # 6. Pill 3 (Bottom - Green Border)
        pill3 = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.779), Inches(4.333), Inches(3.967), Inches(0.592)
        )
        pill3.fill.solid()
        pill3.fill.fore_color.rgb = COLOR_WHITE
        pill3.line.color.rgb = COLOR_GREEN
        pill3.line.width = Pt(1.0)
        tf_p3 = pill3.text_frame
        tf_p3.word_wrap = True
        tf_p3.margin_top = Inches(0.04)
        tf_p3.margin_bottom = Inches(0.04)
        p3_0 = tf_p3.paragraphs[0]
        p3_0.text = "Mock GraphRAG extracts localized subtopology"
        p3_0.font.name = FONT_TITLE
        p3_0.font.size = Pt(12)
        p3_0.font.bold = True
        p3_0.font.color.rgb = COLOR_GREEN
        p3_0.alignment = PP_ALIGN.CENTER
        p3_1 = tf_p3.add_paragraph()
        p3_1.alignment = PP_ALIGN.CENTER
        add_math_runs_to_paragraph(p3_1, "$G_{sub} \\subseteq G$", font_size=Pt(12), color=COLOR_GREEN, font_name=FONT_TITLE)

        # 7. Mathematical Scoping Bound Textbox
        tb_math = s.shapes.add_textbox(
            Inches(1.094), Inches(5.197), Inches(5.200), Inches(0.706)
        )
        tf_m = tb_math.text_frame
        tf_m.word_wrap = True
        p_mlbl = tf_m.paragraphs[0]
        p_mlbl.text = "Mathematical Scoping Bound:"
        p_mlbl.font.name = FONT_TITLE
        p_mlbl.font.size = Pt(11)
        p_mlbl.font.bold = True
        p_mlbl.font.color.rgb = COLOR_NAVY
        p_mlbl.space_before = Pt(0)
        p_mlbl.space_after = Pt(2)

        p_eq1 = tf_m.add_paragraph()
        p_eq1.alignment = PP_ALIGN.CENTER
        add_omml_equation(p_eq1, OMML_MAP[r"G_{sub} = (V_{sub}, E_{sub}) \subseteq G"], font_size=Pt(12), color=COLOR_NAVY)

        p_eq2 = tf_m.add_paragraph()
        p_eq2.alignment = PP_ALIGN.CENTER
        add_omml_equation(p_eq2, OMML_MAP[r"T_{prompt}(G_{sub}) \ll T_{prompt}(G)"], font_size=Pt(12), color=COLOR_NAVY)

        # 8. Right Column Images
        img_left = Inches(6.850)
        img_top = Inches(2.075)
        img_w = Inches(5.500)
        img_h = Inches(3.670)

        pic_base = s.shapes.add_picture(str(base_img_path), img_left, img_top, width=img_w, height=img_h)
        pic_base.line.color.rgb = COLOR_CARD_BORDER
        pic_base.line.width = Pt(1.0)

        pic_overlay = s.shapes.add_picture(str(overlay_img_path), img_left, img_top, width=img_w, height=img_h)
        pic_overlay.line.color.rgb = COLOR_CARD_BORDER
        pic_overlay.line.width = Pt(1.0)

        # Entrance Animation on Click/Advance for Overlay Image
        self.add_entrance_click_animation(s, pic_overlay.shape_id)

        # Citation textbox below image
        tb_cite = s.shapes.add_textbox(
            img_left, Inches(5.527), img_w, Inches(0.236)
        )
        tf_cite = tb_cite.text_frame
        tf_cite.word_wrap = True
        p_cite = tf_cite.paragraphs[0]
        p_cite.text = "From: https://topolib.readthedocs.io/en/latest/topology_repository.html"
        p_cite.font.name = FONT_BODY
        p_cite.font.size = Pt(8)
        p_cite.font.color.rgb = COLOR_DARK_SLATE

        # Bottom Banner
        banner = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, img_left, Inches(5.960), img_w, Inches(0.480)
        )
        banner.fill.solid()
        banner.fill.fore_color.rgb = COLOR_WHITE
        banner.line.color.rgb = COLOR_CARD_BORDER
        banner.line.width = Pt(1.0)

        tf_bn = banner.text_frame
        tf_bn.word_wrap = True
        p_bn = tf_bn.paragraphs[0]
        p_bn.text = "e.g.  Frankfurt ➔ Munich demand: Northern nodes pruned from LLM prompt"
        p_bn.font.name = FONT_TITLE
        p_bn.font.size = Pt(10.5)
        p_bn.font.bold = True
        p_bn.font.color.rgb = COLOR_NAVY
        p_bn.alignment = PP_ALIGN.CENTER

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
                "prefix": "01 Bottleneck",
                "title": "The Optical Intent Planning Bottleneck",
                "desc": "Physical-layer constraints, token saturation, and hallucinated routing in optical backbones",
            },
            {
                "prefix": "02 Architecture",
                "title": "Neurosymbolic Intent Planning Pipeline",
                "desc": "Decoupling probabilistic reasoning ($\\mathcal{I}_{NL} \\to \\mathcal{S}_{PDDL}$) from deterministic solvers and physics tools",
            },
            {
                "prefix": "03 Risk Gates",
                "title": "Pre-Deployment Risk Gates: Semantic & Physical Validation",
                "desc": "Sequential fail-fast decision via Layer 1/2 semantic gate ($U_{sem}$) and GN-model QoT gate ($\\text{QoT}_{valid}$)",
            },
            {
                "prefix": "04 Evaluation",
                "title": "Experimental Testbed Validation on 17-Node Optical Topology",
                "desc": "Benchmarking safety ($\\text{UAR} = 100\\%$), human intervention reduction, and orchestration latency against baselines",
            },
            {
                "prefix": "05 Outlook",
                "title": "Key Takeaways, System Guarantees & Future Directions",
                "desc": "Summary of thesis contributions, operational guarantees, and extension to joint compute scheduling",
            },
        ],
        notes="""[Estimated Time]: 50s
[Key Message]: Establish a thesis-specific narrative instead of a generic agenda.
[Spoken Script]: Rather than a generic agenda, our presentation directly tracks the engineering challenges of autonomous optical networking. We begin by examining why general-purpose LLMs fail when controlling optical backbones. Next, we present our neurosymbolic architecture that cleanly separates natural language reasoning from optical physics. We then delve into the pre-deployment risk gates that protect the physical network before showing experimental validation on a 17-node optical topology and concluding with our primary takeaways.
[Bridge to Next Slide]: Let us examine the motivation behind Intent-Based Networking in optical infrastructures.""",
    )

    # 3. Slide 3: Motivation (Evolution from Imperative SDON to Declarative IBON)
    print("Building Slide 03: Motivation...")
    builder.create_evolution_sdon_ibon_slide(
        title="Motivation: The Evolution from Imperative SDON to Declarative IBON",
        slide_num=3,
        notes="""[Estimated Time]: 55s
[Key Message]: Moving from Imperative SDON to Declarative IBON is essential to eliminate the human configuration bottleneck, but connecting naive LLMs directly to optical control planes introduces catastrophic physical risks.
[Spoken Script]: Optical transport networks form the multi-terabit backbone of modern telecommunications. Over the past decade, Software-Defined Optical Networking (SDON) successfully centralized the control plane through standardized Southbound interfaces like NETCONF and RESTConf. However, SDON remains fundamentally imperative: human operators must still manually compute explicit lightpaths, calculate wavelength grids, and configure ROADM cross-connects, relying on slow offline tools with conservative 3 to 5 dB margins. Intent-Based Optical Networking (IBON), formalized in IETF RFC 9315, represents a crucial paradigm shift from 'how' to 'what': operators express declarative service intents in natural language, and the system autonomously derives the physical optical configuration under continuous closed-loop assurance. However, connecting generative AI directly to optical backbones creates severe risks, as optical networks do not tolerate probabilistic hallucination.
[Bridge to Next Slide]: To understand why standard LLMs cannot simply drive an IBON controller, let us examine the five architectural failure modes that occur.""",
    )

    # 4. Slide 4: Illustrative Failure Modes (5 Horizontal Failure Cards)
    print("Building Slide 04: Illustrative Failure Modes...")
    builder.create_five_challenges_slide(
        title="Illustrative Failure: Why Standard LLMs Break Optical Backbones",
        slide_num=4,
        challenges=[
            {
                "badge_text": "1. Token Budget Saturation",
                "badge_color": COLOR_BURGUNDY,
                "desc": "Telemetry dumps trigger attention degradation, dropping critical route exclusions",
            },
            {
                "badge_text": "2. Hallucinated Physics",
                "badge_color": COLOR_BURGUNDY,
                "desc": "Probabilistic predictors lack wave propagation engines, violating non-linear GSNR margins",
            },
            {
                "badge_text": "3. Semantic Drift",
                "badge_color": COLOR_BURGUNDY,
                "desc": "Unconstrained multi-turn conversational loops mutate or drop initial boundary constraints",
            },
            {
                "badge_text": "4. Reactive Deployment Latency",
                "badge_color": COLOR_BURGUNDY,
                "desc": "Trial-and-error configuration risks live outages and introduces high control-plane recovery latency",
            },
            {
                "badge_text": "5. Suboptimal HITL Friction",
                "badge_color": COLOR_BURGUNDY,
                "desc": "Binary all-or-nothing review causes operator fatigue or outages; models fail to fail-early",
            },
        ],
        bottom_banner="Empirical Risk: Unconstrained LLMs might allow unfeasible deployments, semantic drift loops, and critical control-plane latency",
        notes="""[Estimated Time]: 65s
[Key Message]: Connecting standard generative LLMs directly to optical control planes exposes five fundamental architectural failure modes.
[Spoken Script]: When we evaluate standard generative LLMs for optical network control, we observe five interconnected failure modes that compromise operational integrity: First, Token Budget Saturation: injecting complete network states exhausts token budgets and triggers attention degradation, causing link exclusions to be dropped. Second, Hallucinated Physical Feasibility: autoregressive token predictors cannot solve wave propagation equations, computing invalid lightpaths that cause transponder loss of lock. Third, Semantic Drift: multi-turn chat loops mutate initial constraints without convergence guarantees. Fourth, Reactive Failure Latency: detecting faults after hardware rejection risks live link disruptions. Fifth, Suboptimal HITL: binary all-or-nothing review causes operator fatigue.
[Bridge to Next Slide]: To overcome these five failure modes, we must formally structure the optical intent problem with hard physical constraints.""",
    )

    # 5. Slide 5: Problem Statement (2-Tier Given, Decide, Objective & Constraints)
    print("Building Slide 05: Problem Statement...")
    builder.create_problem_statement_slide(
        title="Problem Statement: Given, Decide, Objective & Constraints",
        slide_num=5,
        upper_cards=[
            {
                "icon": "",
                "title": "Given (System Inputs)",
                "title_color": COLOR_NAVY,
                "border_color": COLOR_NAVY,
                "bullets": [
                    r"Unstructured operator intent ($\mathcal{I}_{NL}$)",
                    r"Active optical topology graph $G(V, E)$",
                    r"Physical parameters (e.g. span length $L$)",
                    r"Feasibility threshold (e.g. $\text{GSNR}$)",
                ],
            },
            {
                "icon": "",
                "title": "Decide (Variables & Actions)",
                "title_color": COLOR_NAVY,
                "border_color": COLOR_NAVY,
                "bullets": [
                    r"Formal symbolic specification" + "\n" + r"($\mathcal{S}_{PDDL}$ compiled from intent)",
                    r"Optimal physical lightpath route" + "\n" + r"($\pi^* \in \mathcal{K}_{path}$ from candidate paths)",
                    r"Pre-deployment control action" + "\n" + r"($a \in \{\text{approve}, \text{clarify}, \text{replan}\}$)",
                    r"Provisioning routing configuration" + "\n" + r"($c^*$ dispatched to controller)",
                ],
            },
            {
                "icon": "",
                "title": "Objective (Optimization)",
                "title_color": COLOR_GREEN,
                "border_color": COLOR_GREEN,
                "bullets": [
                    r"Minimize human interruptions ($\min N_{hitl}$)",
                    r"Minimize prompt tokens ($\min T_{tokens}$)",
                    r"Minimize operational friction" + "\n" + r"($\min \alpha \cdot N_{hitl} + \beta \cdot T_{tokens}$)",
                    r"Guarantee pre-deployment safety" + "\n" + r"($\mathcal{D}(U_{sem}, \text{QoT}_{valid}) = \text{approve}$)",
                ],
            },
        ],
        lower_constraints={
            "title": "Constraints: Resource Limits vs. Physical & Semantic Boundaries",
            "left_title": "Resource Constraints (System & Solver Limits):",
            "left_bullets": [
                r"Token context limits ($T_{prompt} \le T_{max}$)",
                r"Computational inference latency ($t_{exec} \le t_{max\_budget}$)",
                r"Symbolic solver complexity $K \in [3, 5]$",
            ],
            "right_title": "Boundary Constraints (Physical & Semantic Feasibility):",
            "right_bullets": [
                "Zero semantic drift tolerance bound",
                "Deterministic optical QoT feasibility",
                r"Pre-deployment physical validity state ($\text{QoT}_{valid} \in \{0, 1\}$)",
            ],
        },
        notes="""[Estimated Time]: 60s
[Key Message]: Formally formulate the problem across four structured dimensions: Given inputs, Decision variables, Objective function, and Constraints (Resource vs Boundary).
[Spoken Script]: Following classical telecommunications optimization methodology, we formulate our intent planning problem across four precise dimensions: Given, Decide, Objective, and Constraints. In the upper row, first, Given: the orchestrator ingests the natural language intent, queries the network graph via RESTConf, and loads physical parameters. Second, Decide: the system determines the PDDL specification, selects the optimal lightpath route pi*, resolves the risk decision action in {approve, clarify, replan}, and generates the final configuration c*. Third, Objective: we formulate a multi-objective cost function minimizing human interruptions and prompt tokens under the hard invariant that no lightpath is deployed without approval. In the lower half, Constraints decouple into Resource Constraints on the left and Boundary Constraints on the right.
[Bridge to Next Slide]: To solve this constrained optimization problem, we introduce our neurosymbolic architectural philosophy.""",
    )

    # 6. Slide 6: Proposed Solution & Contributions
    print("Building Slide 06: Proposed Solution...")
    builder.create_proposed_solution_slide(
        title="Proposed Solution: RADG with Neurosymbolic Planning",
        slide_num=6,
        neural_data={
            "title": "Neural Subsystem (Semantic Domain)",
            "pills": [
                "Translation of the intent",
                "Validation of the semantic similarity",
                "Orchestration",
            ],
        },
        symbolic_data={
            "title": "Symbolic Subsystem (Optical Domain)",
            "pills": [
                "Topology extraction",
                "Compute candidate lightpaths",
                "Physical feasibility validation",
            ],
        },
        contributions_header="Core Thesis Contributions",
        contributions=[
            {
                "title": "1. Scoped GraphRAG for IBON in a Neurosymbolic system",
                "border_color": COLOR_NAVY,
                "bullets": [
                    "Strict separation: probabilistic semantic translation vs deterministic physics",
                    "Subtopology scoping reduces prompt tokens, eliminating attention loss",
                ],
            },
            {
                "title": "2. Quantification of Semantic Uncertainty for IBON in a Neurosymbolic system",
                "border_color": COLOR_AMBER,
                "bullets": [
                    r"Layer 1 syntax check ($v_{struct} \in \{0, 1\}$)",
                    r"Layer 2 semantic discrepancy ($d_{sem}$)",
                ],
            },
            {
                "title": "3. Risk-Adaptive Decision Gate (RADG) for HITL optimization",
                "border_color": COLOR_GREEN,
                "bullets": [
                    r"Piecewise decision $D(U_{sem}, \text{QoT}_{valid})$: clarify, replan, or auto-approve",
                    r"Guarantees physical safety ($UAR = 0$) with <5 ms calculation latency",
                ],
            },
        ],
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
            {"title": "Optical RAG", "desc": "Enrich $\\mathcal{I}_{NL}$ with ITU-T grid & transponders"},
            {"title": "PDDL Parser", "desc": "Translate intent into formal PDDL $\\mathcal{S}_{PDDL}$ AST"},
            {"title": "Semantic Gate", "desc": ["Evaluate CFG $v_{struct}$", "Reverse Prompting $d_{sem}$"], "is_gate": True},
            {"title": "Symbolic Solver", "desc": "Scoped GraphRAG & Yen's $K\\text{-SP}$ routing"},
            {"title": "QoT Physics", "desc": "Deterministic GN-model $\\text{GSNR}$ calculation"},
            {"title": "Feasibility Gate", "desc": "Piecewise risk gate $D(U_{sem}, \\text{QoT})$", "is_gate": True},
            {"title": "Plan Synthesizer", "desc": "Auditable report & deployment commands"},
        ],
        notes="""[Estimated Time]: 60s
[Key Message]: Walk through the clean 7-phase pipeline, highlighting the sequential fail-fast flow.
[Spoken Script]: Here we see the complete 7-phase execution pipeline. The operator's intent enters Phase 1 where it is enriched with optical standards. In Phase 2, the LLM generates PDDL constraints. Crucially, before running heavy graph solvers or physics tools, Phase 3 evaluates semantic uncertainty. If semantically sound, Phase 4 extracts candidate routes via symbolic graph algorithms. Phase 5 evaluates physical feasibility using a deterministic GN-model. Finally, the Risk-Adaptive Decision Gate verifies physical safety before synthesizing the final auditable report.
[Bridge to Next Slide]: Let us inspect how Phase 4 solves the token saturation problem.""",
    )

    # 8. Slide 8: Scoped GraphRAG (Split with Animated Scoped Topology)
    print("Building Slide 08: Scoped GraphRAG...")
    deck_dir = Path(__file__).resolve().parent
    assets_dir = deck_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    base_img = assets_dir / "germany_17nodes.png"
    overlay_img = assets_dir / "germany_17nodes_opaco.jpg"

    # Ensure assets exist, converting/copying from raw if needed
    if not base_img.exists():
        raw_webp = Path("docs/LLM_Wiki/raw/germany-17nodes.webp")
        if not raw_webp.exists():
            raw_webp = deck_dir.parents[3] / "raw" / "germany-17nodes.webp"
        from PIL import Image
        im = Image.open(raw_webp)
        im.save(base_img, "PNG")

    if not overlay_img.exists():
        raw_opaco = Path("docs/LLM_Wiki/raw/germany-17nodes-opaco.jpg")
        if not raw_opaco.exists():
            raw_opaco = deck_dir.parents[3] / "raw" / "germany-17nodes-opaco.jpg"
        import shutil
        shutil.copy2(raw_opaco, overlay_img)

    builder.create_scoped_graphrag_slide(
        title="Overcoming Token Saturation: Scoped Optical GraphRAG",
        slide_num=8,
        base_img_path=base_img,
        overlay_img_path=overlay_img,
        notes="""[Estimated Time]: 50s
[Key Message]: Scoped GraphRAG extracts only relevant k-hop subtopologies, eliminating attention degradation.
[Spoken Script]: To solve token budget saturation, we implement Scoped Optical GraphRAG. Instead of flooding the LLM context with the entire 17-node topology, our deterministic graph engine extracts only the k-hop neighborhood bounding the source and destination. For instance, [Click / Advance] if an operator requests a lightpath between Frankfurt and Munich, there is no need to load northern nodes like Hamburg, Bremen, or Berlin into the LLM context. We prune distant nodes and links, reducing the prompt token footprint by over 75 percent, eliminating the lost-in-the-middle phenomenon while keeping the graph search computationally instantaneous.
[Bridge to Next Slide]: Now let us examine how we eliminate semantic drift before any physics calculations occur.""",
    )

    # 9. Slide 9: Semantic Drift & Reverse Prompting (OMML Piecewise Math)
    print("Building Slide 09: Semantic Gate...")
    s9 = builder.prs.slides.add_slide(builder.prs.slide_layouts[6])
    builder.add_chrome(s9, "Overcoming Semantic Drift: Reverse Prompting & HITL", 9)

    # Main Container Card
    card_l9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.867), Inches(1.25), Inches(8.51), Inches(4.7)
    )
    card_l9.fill.solid()
    card_l9.fill.fore_color.rgb = COLOR_CARD_BG
    card_l9.line.color.rgb = COLOR_NAVY
    card_l9.line.width = Pt(1.5)

    # Header Bar
    hdr_l9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.2), Inches(5.7), Inches(0.75)
    )
    hdr_l9.fill.solid()
    hdr_l9.fill.fore_color.rgb = COLOR_NAVY
    hdr_l9.line.fill.background()
    p_hl9 = hdr_l9.text_frame.paragraphs[0]
    add_math_runs_to_paragraph(p_hl9, "Two-Layer Semantic Uncertainty ($U_{sem}$)", font_size=Pt(15), color=COLOR_WHITE, font_name=FONT_TITLE, bold=True)
    p_hl9.alignment = PP_ALIGN.CENTER

    # Lower Text & Formula Box inside Container Card
    body_l9 = s9.shapes.add_textbox(
        Inches(1.06), Inches(3.72), Inches(6.37), Inches(1.238)
    )
    tf_bl9 = body_l9.text_frame
    tf_bl9.word_wrap = True

    p_judge = tf_bl9.paragraphs[0]
    add_math_runs_to_paragraph(p_judge, "Independent LLM judge measures semantic discrepancy $d_{sem} \\in [0, 1]$", font_size=Pt(14), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

    p_omml_lbl = tf_bl9.add_paragraph()
    p_omml_lbl.text = "Uncertainty Formulation:"
    p_omml_lbl.font.name = FONT_BODY
    p_omml_lbl.font.size = Pt(14)
    p_omml_lbl.font.color.rgb = COLOR_DARK_SLATE
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
    add_omml_equation(p_omml9, u_sem_xml, font_size=Pt(12), color=COLOR_NAVY)

    # Right Action Banner 1: Amber Clarification
    banner_amber = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.505), Inches(3.801), Inches(4.247), Inches(0.807)
    )
    banner_amber.fill.solid()
    banner_amber.fill.fore_color.rgb = COLOR_AMBER
    banner_amber.line.fill.background()
    p_ba = banner_amber.text_frame.paragraphs[0]
    p_ba.text = "Fail-Fast HITL Clarification Loop"
    p_ba.font.name = FONT_TITLE
    p_ba.font.size = Pt(16)
    p_ba.font.bold = True
    p_ba.font.color.rgb = COLOR_WHITE
    p_ba.alignment = PP_ALIGN.CENTER

    # Right Action Banner 2: Green Guarantee
    banner_green = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.505), Inches(4.818), Inches(4.247), Inches(0.807)
    )
    banner_green.fill.solid()
    banner_green.fill.fore_color.rgb = COLOR_CARD_BG
    banner_green.line.color.rgb = COLOR_GREEN
    banner_green.line.width = Pt(1.5)
    p_bg = banner_green.text_frame.paragraphs[0]
    p_bg.text = "Fail-Fast Guarantee: Zero computational waste on physics simulation when intent is ambiguous"
    p_bg.font.name = FONT_TITLE
    p_bg.font.size = Pt(14)
    p_bg.font.bold = True
    p_bg.font.color.rgb = COLOR_GREEN
    p_bg.alignment = PP_ALIGN.CENTER

    # Subcard 1: Structural
    sub1_s9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.458), Inches(2.543), Inches(2.133), Inches(0.818)
    )
    sub1_s9.fill.solid()
    sub1_s9.fill.fore_color.rgb = COLOR_WHITE
    sub1_s9.line.color.rgb = COLOR_CARD_BORDER
    sub1_s9.line.width = Pt(1.0)
    tf_sub1 = sub1_s9.text_frame
    p_s1_0 = tf_sub1.paragraphs[0]
    p_s1_0.text = "Structural"
    p_s1_0.font.name = FONT_TITLE
    p_s1_0.font.size = Pt(16)
    p_s1_0.font.color.rgb = COLOR_DARK_SLATE
    p_s1_0.alignment = PP_ALIGN.CENTER

    p_s1_1 = tf_sub1.add_paragraph()
    p_s1_1.alignment = PP_ALIGN.CENTER
    add_math_runs_to_paragraph(p_s1_1, "CFG regex AST checks ($v_{struct} \\in \\{0, 1\\}$)", font_size=Pt(11), color=COLOR_DARK_SLATE, font_name=FONT_BODY)

    # Subcard 2: Semantic
    sub2_s9 = s9.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.042), Inches(2.575), Inches(2.133), Inches(0.818)
    )
    sub2_s9.fill.solid()
    sub2_s9.fill.fore_color.rgb = COLOR_WHITE
    sub2_s9.line.color.rgb = COLOR_CARD_BORDER
    sub2_s9.line.width = Pt(1.0)
    tf_sub2 = sub2_s9.text_frame
    p_s2_0 = tf_sub2.paragraphs[0]
    p_s2_0.text = "Semantic"
    p_s2_0.font.name = FONT_TITLE
    p_s2_0.font.size = Pt(16)
    p_s2_0.font.color.rgb = COLOR_DARK_SLATE
    p_s2_0.alignment = PP_ALIGN.CENTER

    p_s2_1 = tf_sub2.add_paragraph()
    p_s2_1.alignment = PP_ALIGN.CENTER
    p_s2_1.text = "Reverse Prompting reconstructs the intent"
    p_s2_1.font.name = FONT_TITLE
    p_s2_1.font.size = Pt(11)
    p_s2_1.font.bold = True
    p_s2_1.font.color.rgb = COLOR_DARK_SLATE

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
                "condition": "$U_{sem} > \\tau_{sem}$",
                "condition_xml": (
                    '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> &gt; </m:t></m:r>'
                    '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
                ),
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
                "condition": "$U_{sem} \\le \\tau_{sem} \\land \\text{QoT}_{valid} = 0$",
                "condition_xml": (
                    '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> ≤ </m:t></m:r>'
                    '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> ∧ </m:t></m:r>'
                    '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> = 0</m:t></m:r>'
                ),
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
                "condition": "$U_{sem} \\le \\tau_{sem} \\land \\text{QoT}_{valid} = 1$",
                "condition_xml": (
                    '<m:sSub><m:e><m:r><m:t>U</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> ≤ </m:t></m:r>'
                    '<m:sSub><m:e><m:r><m:t>τ</m:t></m:r></m:e><m:sub><m:r><m:t>sem</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> ∧ </m:t></m:r>'
                    '<m:sSub><m:e><m:r><m:t>QoT</m:t></m:r></m:e><m:sub><m:r><m:t>valid</m:t></m:r></m:sub></m:sSub>'
                    '<m:r><m:t> = 1</m:t></m:r>'
                ),
                "bullets": [
                    "Trigger: Clear semantics and feasible $\\text{GSNR}$",
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

    add_bullet_with_math(tf_bl11, "•  Pure Python implementation: zero LLM arithmetic", font_size=Pt(12), color=COLOR_DARK_SLATE, space_after=Pt(4))

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
    add_omml_equation(p_ase_eq, ase_xml, font_size=Pt(13), color=COLOR_NAVY)

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
    add_omml_equation(p_nli_eq, nli_xml, font_size=Pt(13), color=COLOR_NAVY)

    add_bullet_with_math(tf_bl11, "•  Accounts for fiber Kerr nonlinearity, dispersion, and EDFA noise", font_size=Pt(11), color=COLOR_DARK_SLATE, space_before=Pt(6))

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
    add_omml_equation(p_gsnr_eq, gsnr_xml, font_size=Pt(13), color=COLOR_GREEN)

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
    add_omml_equation(p_prx_eq, prx_xml, font_size=Pt(13), color=COLOR_GREEN)

    add_bullet_with_math(tf_br11, "•  Deterministic feasibility: $\\text{GSNR} \\ge \\text{GSNR}_{th} \\land P_{rx} \\ge P_{rx,min}$", font_size=Pt(11), color=COLOR_DARK_SLATE, space_before=Pt(6))

    # Bottom Performance Banner
    bb11 = s11.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(6.2), Inches(11.75), Inches(0.65)
    )
    bb11.fill.solid()
    bb11.fill.fore_color.rgb = COLOR_CARD_BG
    bb11.line.color.rgb = COLOR_GREEN
    bb11.line.width = Pt(1.5)
    tb_bb11 = s11.shapes.add_textbox(Inches(0.75), Inches(6.2), Inches(11.75), Inches(0.65))
    p_bb11 = tb_bb11.text_frame.paragraphs[0]
    add_math_runs_to_paragraph(p_bb11, "⚡ Execution Speed: $T_{phys} < 5\\text{ ms}$ per candidate route (100% deterministic reproducibility)", font_size=Pt(13), color=COLOR_GREEN, font_name=FONT_TITLE, bold=True)
    p_bb11.alignment = PP_ALIGN.CENTER

    builder.set_speaker_notes(
        s11,
        """[Estimated Time]: 55s
[Key Message]: Pure Python GN-model computes real GSNR and receiver power deterministically in milliseconds.
[Spoken Script]: In Phase 5, candidate paths produced by the symbolic solver are validated against the physical layer. We port the analytical Gaussian Noise model into pure Python. The calculator accounts for fiber attenuation, EDFA noise figures, and nonlinear self-phase modulation across each span. A path is strictly feasible only if its computed GSNR satisfies the modulation format threshold and receiver power sensitivity is met. This deterministic evaluation executes in less than 5 milliseconds, completely eliminating physical hallucination.
[Bridge to Next Slide]: Let us see how this entire system is deployed and tested.""",
    )

    # 12. Slide 12: Experimental Setup (Unified Backdrop Container & Topology Map)
    print("Building Slide 12: Experimental Setup...")
    s12 = builder.prs.slides.add_slide(builder.prs.slide_layouts[6])
    builder.add_chrome(s12, "Experimental Setup & Testbed Environment", 12)

    # Main Container Card (expanded width 9.404")
    card_l12 = s12.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.3), Inches(9.404), Inches(5.35)
    )
    card_l12.fill.solid()
    card_l12.fill.fore_color.rgb = COLOR_CARD_BG
    card_l12.line.color.rgb = COLOR_NAVY
    card_l12.line.width = Pt(1.5)

    # Header Bar
    hdr_l12 = s12.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), Inches(1.25), Inches(5.6), Inches(0.7)
    )
    hdr_l12.fill.solid()
    hdr_l12.fill.fore_color.rgb = COLOR_NAVY
    hdr_l12.line.fill.background()
    p_hl12 = hdr_l12.text_frame.paragraphs[0]
    p_hl12.text = "17-Node German Core Network Benchmark"
    p_hl12.font.name = FONT_TITLE
    p_hl12.font.size = Pt(15)
    p_hl12.font.bold = True
    p_hl12.font.color.rgb = COLOR_WHITE
    p_hl12.alignment = PP_ALIGN.CENTER

    # Bullets Textbox
    body_l12 = s12.shapes.add_textbox(
        Inches(1.15), Inches(2.863), Inches(5.517), Inches(1.935)
    )
    tf_bl12 = body_l12.text_frame
    tf_bl12.word_wrap = True

    bullets_s12 = [
        r"Realistic telecom topology: $|V| = 17, |E| = 26$ bidirectional fiber links",
        r"Standard Single-Mode Fiber (SMF-28): $\alpha = 0.2\text{ dB/km}$",
        r"Dispersion parameter $D = 16.7\text{ ps/(nm}\cdot\text{km})$, $\gamma = 1.2\text{ W}^{-1}\text{km}^{-1}$",
        r"Amplified spans: dual-stage EDFAs with noise figure $NF = 5.5\text{ dB}$",
        r"Dynamic span lengths ranging from $L \in [45, 350]\text{ km}$",
        "Orchestrator: LangGraph StateGraph with memory persistence",
        "Telemetry: RESTConf and Mock SDON testbed client adapters",
    ]
    for b_text in bullets_s12:
        add_bullet_with_math(tf_bl12, f"•  {b_text}", font_size=Pt(12), color=COLOR_DARK_SLATE, space_after=Pt(3))

    # Topology Image & Source Citation
    img_path = Path("docs/LLM_Wiki/wiki/presentations/thesis_defense/assets/germany_17nodes.png")
    pic12 = s12.shapes.add_picture(str(img_path), Inches(6.85), Inches(2.075), Inches(5.5), Inches(3.67))
    pic12.line.color.rgb = COLOR_CARD_BORDER
    pic12.line.width = Pt(1.0)

    cite_box = s12.shapes.add_textbox(Inches(6.85), Inches(5.527), Inches(5.5), Inches(0.236))
    p_cite = cite_box.text_frame.paragraphs[0]
    p_cite.text = "From: https://topolib.readthedocs.io/en/latest/topology_repository.html"
    p_cite.font.name = FONT_BODY
    p_cite.font.size = Pt(9)
    p_cite.font.color.rgb = COLOR_COOL_GRAY

    builder.set_speaker_notes(
        s12,
        """[Estimated Time]: 50s
[Key Message]: Realistic evaluation using the standard 17-node German optical topology and RESTConf testbed.
[Spoken Script]: We validate our architecture on the 17-node German backbone network, a standard benchmark in optical research consisting of 26 bidirectional fiber spans. All spans model standard SMF-28 fiber with realistic attenuation, dispersion, and EDFA noise figures. The orchestrator is implemented in Python using LangGraph, interfacing with the optical testbed via RESTConf APIs, and benchmarked using state-of-the-art LLMs as semantic translators.
[Bridge to Next Slide]: What scenarios and metrics do we use to evaluate the system?""",
    )

    # 13. Slide 13: Evaluation Framework (Baselines + Corpus on Left, 4 Validation Pillars on Right)
    print("Building Slide 13: Evaluation Framework...")
    builder.create_evaluation_framework_slide(
        title="Evaluation Framework & Benchmark Scenarios",
        slide_num=13,
        baselines_info={
            "icon": "",
            "title": "Architectural Baselines",
            "bullets": [
                "Baseline A (LLM-Only): Direct prompt-to-configuration generation with reactive retry",
                "Baseline B (Static Rule-Based): Strict regex parser with mandatory Always-HITL review",
                "Proposed (Neurosymbolic RADG): Decoupled translation + sequential pre-deployment risk gates",
                "17-Node German Backbone: 26 bidirectional fiber links, standard SMF-28, dual-stage EDFAs",
            ],
        },
        corpus_info={
            "icon": "",
            "title": "100 Test Demands (4 Risk Classes)",
            "table_rows": [
                ("Class I: Nominal [40]", "Feasible path, unambiguous", "Auto-Approve", COLOR_GREEN),
                ("Class II: Ambiguous [20]", "Under-specified (U_sem > τ)", "Clarify Intent", COLOR_AMBER),
                ("Class III: Infeasible [25]", "Violates GSNR threshold", "Suggest Replan", COLOR_BURGUNDY),
                ("Class IV: Adversarial [15]", "Hallucinated nodes (v_struct=0)", "Reject Intent", COLOR_BURGUNDY),
            ],
            "bullets": [
                "Class I — Nominal [40]: Unambiguous requests with feasible optical paths ➔ Auto-Approve",
                "Class II — Ambiguous [20]: Under-specified constraints triggering $U_{sem} > \\tau_{sem}$ ➔ Clarify",
                "Class III — Infeasible [25]: High modulation over long spans violating GSNR ➔ Suggest Replan",
                "Class IV — Adversarial [15]: Hallucinated nodes & syntax violations ($v_{struct} = 0$) ➔ Reject",
            ],
        },
        pillars=[
            {
                "icon": "",
                "title": "1. Semantic Translation Accuracy (Neural Domain)",
                "color": COLOR_AMBER,
                "focus": "Validates NL ➔ PDDL translation without constraint loss or hallucinations",
                "metrics": "Constraint Retention Rate (CRR = 100%) • CFG AST Pass Rate ($v_{struct} = 1$)",
            },
            {
                "icon": "",
                "title": "2. Physical Feasibility (Optical Layer Integrity)",
                "color": COLOR_GREEN,
                "focus": "Validates optical reach and non-linear impairments before controller push",
                "metrics": "Unsafe Approval Rate (UAR = 0% hard invariant) • QoT Feasibility (100%)",
            },
            {
                "icon": "",
                "title": "3. Orchestration & Resource Efficiency (System Limits)",
                "color": COLOR_NAVY,
                "focus": "Quantifies prompt token savings from GraphRAG and operator fatigue reduction",
                "metrics": "> 75% Token Reduction ($G_{sub} \\subseteq G$) • > 70% HITL Cut • Sub-second compute",
            },
            {
                "icon": "",
                "title": "4. RADG Decision Robustness (Gate Reliability)",
                "color": COLOR_BURGUNDY,
                "focus": "Stress-tests piecewise decision logic ($U_{sem}$, $\\text{QoT}_{valid}$) across boundary conditions",
                "metrics": "Gate Decision Accuracy (> 98%) • Zero False Positives (FPR = 0%)",
            },
        ],
        notes="""[Estimated Time]: 55s
[Key Message]: Rigorous benchmarking across 100 diverse intent scenarios against LLM-only and rule-based baselines across 4 validation pillars.
[Spoken Script]: In Slide 13, we present our comprehensive evaluation framework. On the left, we establish the experimental baseline: we test against an unconstrained LLM-only baseline with trial-and-error retry, and a rigid rule-based system with always-on human review, deployed on the 17-node German optical backbone. We evaluate a benchmark corpus of 100 intent demands spanning four risk classes: nominal, ambiguous, physically infeasible, and adversarial prompts. On the right, rather than just measuring latency, we evaluate our system across four rigorous validation pillars: first, Semantic Translation Accuracy to guarantee zero constraint loss; second, Physical Feasibility to enforce our non-negotiable zero percent Unsafe Approval Rate; third, Orchestration Efficiency, measuring over 75 percent token savings from GraphRAG and 70 percent reduction in operator fatigue; and fourth, RADG Decision Robustness, ensuring over 98 percent gate accuracy and zero false positives across all boundary conditions.
[Bridge to Next Slide]: Let us analyze the key findings and empirical guarantees obtained from these benchmarks.""",
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
                "subtitle": "$\\text{UAR} = 100\\%$: Zero unfeasible lightpaths reach controller (vs 34% in baseline)",
            },
            {
                "value": "> 70%",
                "color": COLOR_NAVY,
                "border_color": COLOR_NAVY,
                "label": "Reduction in Operator Fatigue",
                "subtitle": "Autonomous approval when $U_{sem} \\le \\tau_{sem}$ (operator engaged only on high risk)",
            },
            {
                "value": "< 5 ms",
                "color": COLOR_NAVY,
                "border_color": COLOR_NAVY,
                "label": "Deterministic Physics Latency",
                "subtitle": "GN model executes in $T_{phys} < 5\\text{ ms}$ ($T_{solver} < 10\\text{ ms}$, sub-second total)",
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
                "Natural language reasoning $\\mathcal{I}_{NL} \\to \\mathcal{S}_{PDDL}$ bridges to formal planning",
                "Guarantees formal soundness without constraining operator expressiveness",
            ],
        },
        {
            "icon": "🔒",
            "title": "Sequential Risk Gates Prevent Failure",
            "border_color": COLOR_GREEN,
            "bullets": [
                "Early semantic evaluation ($U_{sem} \\le \\tau_{sem}$) eliminates drift before physics computation",
                "Deterministic GN-model verification ($\\text{QoT}_{valid} = 1$) ensures 100% physical feasibility",
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
                "Benchmarked on realistic $|V| = 17, |E| = 26$ German topology and RESTConf testbed",
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

        tb_b = s15.shapes.add_textbox(
            pos_left + Inches(0.15), pos_top + Inches(0.6), grid_w - Inches(0.3), grid_h - Inches(0.65)
        )
        tf_b = tb_b.text_frame
        tf_b.word_wrap = True
        tf_b.margin_top = Inches(0.05)
        tf_b.margin_left = Inches(0.05)
        tf_b.margin_right = Inches(0.05)
        tf_b.margin_bottom = Inches(0.05)

        for b_text in item["bullets"]:
            add_bullet_with_math(tf_b, f"•  {b_text}", font_size=Pt(11), color=COLOR_DARK_SLATE, space_after=Pt(3))

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
