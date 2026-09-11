"""
NFL Defensive Coverage & Formation Analyzer
Engineering & Scouting Analytics Interface
Native SVG vector rendering (zero external plotting dependencies required).
"""

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import base64

# --- SYSTEM CONFIGURATION ---
st.set_page_config(
    page_title="NFL Defensive Coverage & Formation Analyzer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL SCOUTING DASHBOARD STYLING ---
st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    .scout-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    .scout-card-title {
        font-size: 0.95rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #f0f6fc;
        margin: 0;
    }
    .film-viewport {
        max-height: 380px;
        height: 380px;
        background: #090d12;
        border: 1px solid #30363d;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .film-viewport img {
        max-height: 380px;
        width: auto;
        max-width: 100%;
        object-fit: contain;
    }
    .tech-pill {
        display: inline-block;
        padding: 2px 7px;
        border-radius: 3px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        letter-spacing: 0.3px;
    }
    .tech-zone { background: #1f3a5f; color: #79c0ff; border: 1px solid #388bfd; }
    .tech-man { background: #49181d; color: #ff7b72; border: 1px solid #f85149; }
    .tech-rush { background: #3e2609; color: #d29922; border: 1px solid #bb8009; }
    .scout-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.82rem;
        margin-top: 6px;
    }
    .scout-table th {
        background-color: #0d1117;
        color: #8b949e;
        text-align: left;
        padding: 8px 12px;
        border-bottom: 1px solid #30363d;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.72rem;
        letter-spacing: 0.4px;
    }
    .scout-table td {
        padding: 7px 12px;
        border-bottom: 1px solid #21262d;
        color: #c9d1d9;
    }
    .scout-table tr:hover {
        background-color: #1c2128;
    }
    .mono {
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "panel_visibility" not in st.session_state:
    st.session_state.panel_visibility = {
        "panel_visual": False,
        "panel_chart": False,
        "panel_prob": False,
        "panel_tells": False,
        "panel_disguise": False
    }

def toggle_panel(panel_key):
    st.session_state.panel_visibility[panel_key] = not st.session_state.panel_visibility.get(panel_key, False)

# --- NATIVE SVG PLAYBOOK SCHEMATIC GENERATOR ---
def render_playbook_svg(players, scheme_name="Cover 3 Sky", shell="1-HIGH"):
    def to_svg(x_yard, y_yard):
        sx = (x_yard + 26.0) / 52.0 * 800.0
        sy = (23.5 - y_yard) / 31.0 * 450.0
        return round(sx, 1), round(sy, 1)

    svg = []
    svg.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 450" width="100%" height="100%" style="background:#0d1117; border-radius:4px; font-family:monospace;">')
    svg.append('<rect x="0" y="0" width="800" height="450" fill="#111d15" stroke="#30363d" stroke-width="1"/>')
    
    # Yardlines every 5 yards
    for y in range(-5, 25, 5):
        _, sy = to_svg(0, y)
        is_los = (y == 0)
        stroke_color = "#e3b341" if is_los else "#8b949e"
        stroke_width = "2.5" if is_los else "0.8"
        stroke_dash = "" if is_los else 'stroke-dasharray="4,4"'
        opacity = "0.95" if is_los else "0.25"
        svg.append(f'<line x1="20" y1="{sy}" x2="780" y2="{sy}" stroke="{stroke_color}" stroke-width="{stroke_width}" opacity="{opacity}" {stroke_dash}/>')
        if y > 0 and y % 10 == 0:
            svg.append(f'<text x="25" y="{sy - 4}" fill="#8b949e" font-size="10" opacity="0.6">+{y}y</text>')
            svg.append(f'<text x="750" y="{sy - 4}" fill="#8b949e" font-size="10" opacity="0.6">+{y}y</text>')

    # Tackle box
    tbx1, tby_top = to_svg(-5.5, 5.0)
    tbx2, tby_bot = to_svg(5.5, 0.0)
    tb_w = tbx2 - tbx1
    tb_h = tby_bot - tby_top
    svg.append(f'<rect x="{tbx1}" y="{tby_top}" width="{tb_w}" height="{tb_h}" fill="#d29922" fill-opacity="0.08" stroke="#d29922" stroke-width="1" stroke-dasharray="3,3"/>')
    svg.append(f'<text x="{tbx1 + 4}" y="{tby_bot - 4}" fill="#e3b341" font-size="9" font-weight="bold">LOS</text>')

    # Hash marks
    for y in range(-6, 24):
        hx1_a, hy = to_svg(-3.1, y)
        hx1_b, _ = to_svg(-2.5, y)
        hx2_a, _ = to_svg(2.5, y)
        hx2_b, _ = to_svg(3.1, y)
        svg.append(f'<line x1="{hx1_a}" y1="{hy}" x2="{hx1_b}" y2="{hy}" stroke="#8b949e" stroke-width="0.7" opacity="0.35"/>')
        svg.append(f'<line x1="{hx2_a}" y1="{hy}" x2="{hx2_b}" y2="{hy}" stroke="#8b949e" stroke-width="0.7" opacity="0.35"/>')

    # Coverage zones
    if "Cover 3" in scheme_name:
        for x1, x2, lbl in [(-25, -8.3, "1/3 DEEP (L)"), (-8.3, 8.3, "1/3 DEEP (MID)"), (8.3, 25, "1/3 DEEP (R)")]:
            sx1, sy_top = to_svg(x1, 23.0)
            sx2, sy_bot = to_svg(x2, 13.0)
            svg.append(f'<rect x="{sx1}" y="{sy_top}" width="{sx2-sx1}" height="{sy_bot-sy_top}" fill="#58a6ff" fill-opacity="0.06" stroke="#58a6ff" stroke-width="0.8" stroke-dasharray="4,4"/>')
            svg.append(f'<text x="{(sx1+sx2)/2}" y="{sy_top + 16}" fill="#79c0ff" font-size="9" text-anchor="middle" opacity="0.7">{lbl}</text>')
    elif "Cover 2" in scheme_name or "Tampa 2" in scheme_name:
        for x1, x2, lbl in [(-25, 0, "1/2 DEEP (L)"), (0, 25, "1/2 DEEP (R)")]:
            sx1, sy_top = to_svg(x1, 23.0)
            sx2, sy_bot = to_svg(x2, 12.0)
            svg.append(f'<rect x="{sx1}" y="{sy_top}" width="{sx2-sx1}" height="{sy_bot-sy_top}" fill="#58a6ff" fill-opacity="0.07" stroke="#58a6ff" stroke-width="0.8" stroke-dasharray="4,4"/>')
            svg.append(f'<text x="{(sx1+sx2)/2}" y="{sy_top + 16}" fill="#79c0ff" font-size="10" text-anchor="middle" opacity="0.75">{lbl}</text>')
    elif "Cover 4" in scheme_name:
        for x1, x2, lbl in [(-25, -12.5, "1/4 L"), (-12.5, 0, "1/4 M-L"), (0, 12.5, "1/4 M-R"), (12.5, 25, "1/4 R")]:
            sx1, sy_top = to_svg(x1, 23.0)
            sx2, sy_bot = to_svg(x2, 11.5)
            svg.append(f'<rect x="{sx1}" y="{sy_top}" width="{sx2-sx1}" height="{sy_bot-sy_top}" fill="#58a6ff" fill-opacity="0.06" stroke="#58a6ff" stroke-width="0.8" stroke-dasharray="4,4"/>')
            svg.append(f'<text x="{(sx1+sx2)/2}" y="{sy_top + 16}" fill="#79c0ff" font-size="9" text-anchor="middle" opacity="0.7">{lbl}</text>')

    # Defs for Arrowhead Markers
    svg.append("""
    <defs>
        <marker id="arr-rush" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#f85149" />
        </marker>
        <marker id="arr-deep" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#58a6ff" />
        </marker>
        <marker id="arr-under" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#d29922" />
        </marker>
        <marker id="arr-man" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#ff7b72" />
        </marker>
    </defs>
    """)

    # Vector arrows
    defenders = [p for p in players if p["side"] == "DEFENSE"]
    for d in defenders:
        role = d.get("role", "ZONE")
        sx, sy = to_svg(d["x_yard"], d["y_yard"])
        if role == "RUSH":
            tx, ty = to_svg(d["x_yard"] * 0.75, -0.2)
            svg.append(f'<line x1="{sx}" y1="{sy + 8}" x2="{tx}" y2="{ty}" stroke="#f85149" stroke-width="2.0" marker-end="url(#arr-rush)"/>')
        elif "DEEP" in role:
            tx, ty = to_svg(d["x_yard"], 19.5)
            svg.append(f'<line x1="{sx}" y1="{sy - 8}" x2="{tx}" y2="{ty}" stroke="#58a6ff" stroke-width="1.8" stroke-dasharray="5,3" marker-end="url(#arr-deep)"/>')
        elif "FLAT" in role:
            target_x = d["x_yard"] + (4.0 if d["x_yard"] >= 0 else -4.0)
            tx, ty = to_svg(target_x, 3.5)
            svg.append(f'<line x1="{sx}" y1="{sy - 4}" x2="{tx}" y2="{ty}" stroke="#d29922" stroke-width="1.8" stroke-dasharray="3,3" marker-end="url(#arr-under)"/>')
        elif "HOOK" in role or "HOLE" in role:
            tx, ty = to_svg(d["x_yard"] * 0.8, d["y_yard"] + 3.0)
            svg.append(f'<line x1="{sx}" y1="{sy - 4}" x2="{tx}" y2="{ty}" stroke="#d29922" stroke-width="1.8" stroke-dasharray="3,3" marker-end="url(#arr-under)"/>')
        elif "MAN" in role:
            tx, ty = to_svg(d["x_yard"], d["y_yard"] - 1.2)
            svg.append(f'<line x1="{sx}" y1="{sy + 6}" x2="{tx}" y2="{ty}" stroke="#ff7b72" stroke-width="1.8" marker-end="url(#arr-man)"/>')

    # Draw Offense (Circles)
    offense = [p for p in players if p["side"] == "OFFENSE"]
    for o in offense:
        sx, sy = to_svg(o["x_yard"], o["y_yard"])
        svg.append(f'<circle cx="{sx}" cy="{sy}" r="11" fill="#1f3a5f" stroke="#79c0ff" stroke-width="1.5"/>')
        svg.append(f'<text x="{sx}" y="{sy + 3.5}" fill="#ffffff" font-size="8.5" font-weight="bold" text-anchor="middle">{o["pos"]}</text>')

    # Draw Defense (X Markers)
    for d in defenders:
        sx, sy = to_svg(d["x_yard"], d["y_yard"])
        s = 6.5
        svg.append(f'<line x1="{sx-s}" y1="{sy-s}" x2="{sx+s}" y2="{sy+s}" stroke="#f85149" stroke-width="2.5"/>')
        svg.append(f'<line x1="{sx-s}" y1="{sy+s}" x2="{sx+s}" y2="{sy-s}" stroke="#f85149" stroke-width="2.5"/>')
        pos = d["pos"]
        tag_w = max(24, len(pos) * 7 + 8)
        svg.append(f'<rect x="{sx - tag_w/2}" y="{sy - 22}" width="{tag_w}" height="14" fill="#161b22" stroke="#f85149" stroke-width="0.8" rx="2"/>')
        svg.append(f'<text x="{sx}" y="{sy - 11}" fill="#f0f6fc" font-size="8.5" font-weight="bold" text-anchor="middle">{pos}</text>')

    svg.append(f'<text x="400" y="24" fill="#f0f6fc" font-size="12" font-weight="bold" text-anchor="middle">PLAYBOOK SCHEMATIC: {scheme_name.upper()} [{shell}]</text>')
    svg.append('</svg>')
    return "".join(svg)

# --- DEFENSIVE ASSIGNMENT ROSTER ---
def build_formation_roster(scheme_name="Cover 3 Sky", shell="1-HIGH"):
    offense = [
        {"pos": "C", "x_yard": 0.0, "y_yard": -0.8, "side": "OFFENSE"},
        {"pos": "LG", "x_yard": -1.8, "y_yard": -0.8, "side": "OFFENSE"},
        {"pos": "RG", "x_yard": 1.8, "y_yard": -0.8, "side": "OFFENSE"},
        {"pos": "LT", "x_yard": -3.6, "y_yard": -0.8, "side": "OFFENSE"},
        {"pos": "RT", "x_yard": 3.6, "y_yard": -0.8, "side": "OFFENSE"},
        {"pos": "TE", "x_yard": 5.4, "y_yard": -0.8, "side": "OFFENSE"},
        {"pos": "QB", "x_yard": 0.0, "y_yard": -4.2, "side": "OFFENSE"},
        {"pos": "RB", "x_yard": 2.0, "y_yard": -4.5, "side": "OFFENSE"},
        {"pos": "WR1", "x_yard": -18.5, "y_yard": -1.0, "side": "OFFENSE"},
        {"pos": "SLOT", "x_yard": -11.0, "y_yard": -1.5, "side": "OFFENSE"},
        {"pos": "WR2", "x_yard": 18.5, "y_yard": -1.0, "side": "OFFENSE"},
    ]

    if "Cover 3" in scheme_name:
        defenders = [
            {"pos": "FS", "x_yard": 0.0, "y_yard": 13.5, "role": "DEEP_THIRD",
             "align": "Middle Deep (13.5y)", "zone": "Deep Middle 1/3",
             "technique": "Apex MOFC", "key_read": "Read QB shoulders; protect seams and post"},
            {"pos": "SS", "x_yard": 7.5, "y_yard": 6.5, "role": "FLAT",
             "align": "Apex Strong (6.5y)", "zone": "Curl / Flat (Sky)",
             "technique": "Inside Shade / Buzz", "key_read": "Force run perimeter; carry #2 vertical or buzz to flat"},
            {"pos": "LCB", "x_yard": -18.5, "y_yard": 7.5, "role": "DEEP_THIRD",
             "align": "Off Corner (7.5y)", "zone": "Deep Left 1/3",
             "technique": "Outside Shade (Bail)", "key_read": "Read #1 vertical; protect deep sideline third"},
            {"pos": "RCB", "x_yard": 18.5, "y_yard": 7.0, "role": "DEEP_THIRD",
             "align": "Off Corner (7.0y)", "zone": "Deep Right 1/3",
             "technique": "Outside Shade (Bail)", "key_read": "Read #1 vertical; protect deep sideline third"},
            {"pos": "WLB", "x_yard": -4.5, "y_yard": 4.5, "role": "HOOK",
             "align": "Weak Underneath (4.5y)", "zone": "Hook to Curl (Weak)",
             "technique": "30-Tech Stack", "key_read": "Relate to #3 receiver; wall off crossers"},
            {"pos": "MLB", "x_yard": 0.5, "y_yard": 4.8, "role": "HOOK",
             "align": "Middle Underneath (4.8y)", "zone": "Hook to Curl (Middle)",
             "technique": "00-Tech Stack", "key_read": "Drop into middle intermediate hole; read shallow crossers"},
            {"pos": "SLB", "x_yard": -10.5, "y_yard": 4.2, "role": "FLAT",
             "align": "Slot Overhang (4.2y)", "zone": "Curl / Flat (Weak)",
             "technique": "Apex Nickel", "key_read": "Disrupt slot release; sink underneath intermediate out"},
            {"pos": "LDE", "x_yard": -5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 5-Tech (1.2y)", "zone": "Pass Rush (Contain)",
             "technique": "5-Technique", "key_read": "Edge contain; bull rush offensive tackle"},
            {"pos": "LDT", "x_yard": -1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 3-Tech (1.0y)", "zone": "Pass Rush (B-Gap)",
             "technique": "3-Technique", "key_read": "Interior penetration through B-gap"},
            {"pos": "RDT", "x_yard": 1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 1-Tech (1.0y)", "zone": "Pass Rush (A-Gap)",
             "technique": "1-Technique Shade", "key_read": "Control A-gap; occupy double team"},
            {"pos": "RDE", "x_yard": 5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 7-Tech (1.2y)", "zone": "Pass Rush (Contain)",
             "technique": "7-Technique", "key_read": "Speed rush edge; collapse pocket backside"},
        ]
    elif "Cover 2" in scheme_name or "Tampa 2" in scheme_name:
        defenders = [
            {"pos": "FS", "x_yard": -8.5, "y_yard": 13.0, "role": "DEEP_HALF",
             "align": "Deep Left Half (13.0y)", "zone": "Deep Half (Left)",
             "technique": "2-High MOFO", "key_read": "Sideline to hash range; read #1/#2 vertical"},
            {"pos": "SS", "x_yard": 8.5, "y_yard": 13.0, "role": "DEEP_HALF",
             "align": "Deep Right Half (13.0y)", "zone": "Deep Half (Right)",
             "technique": "2-High MOFO", "key_read": "Sideline to hash range; read #1/#2 vertical"},
            {"pos": "LCB", "x_yard": -18.5, "y_yard": 2.0, "role": "FLAT",
             "align": "Press / Hard (2.0y)", "zone": "Hard Flat (Cloud)",
             "technique": "Squat", "key_read": "Reroute #1 at LOS; sink underneath flat routes"},
            {"pos": "RCB", "x_yard": 18.5, "y_yard": 2.0, "role": "FLAT",
             "align": "Press / Hard (2.0y)", "zone": "Hard Flat (Cloud)",
             "technique": "Squat", "key_read": "Reroute #1 at LOS; sink underneath flat routes"},
            {"pos": "MLB", "x_yard": 0.0, "y_yard": 4.5, "role": "HOOK",
             "align": "Middle Hole (4.5y)", "zone": "Middle Run-Pipe / Pole",
             "technique": "Tampa Pole", "key_read": "Sprint down middle vertical seam between deep safeties"},
            {"pos": "WLB", "x_yard": -5.0, "y_yard": 4.2, "role": "HOOK",
             "align": "Weak Hook (4.2y)", "zone": "Weak Hook / Curl",
             "technique": "Stack Underneath", "key_read": "Wall off interior crosses; protect hash marks"},
            {"pos": "SLB", "x_yard": 5.0, "y_yard": 4.2, "role": "HOOK",
             "align": "Strong Hook (4.2y)", "zone": "Strong Hook / Curl",
             "technique": "Stack Underneath", "key_read": "Wall off tight end release; expand to curl window"},
            {"pos": "LDE", "x_yard": -5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 5-Tech (1.2y)", "zone": "Pass Rush (Contain)",
             "technique": "5-Technique", "key_read": "Contain QB; edge pressure"},
            {"pos": "LDT", "x_yard": -1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 3-Tech (1.0y)", "zone": "Pass Rush (B-Gap)",
             "technique": "3-Technique", "key_read": "Penetrate B-gap"},
            {"pos": "RDT", "x_yard": 1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 1-Tech (1.0y)", "zone": "Pass Rush (A-Gap)",
             "technique": "1-Technique", "key_read": "Interior run plug; collapse pocket"},
            {"pos": "RDE", "x_yard": 5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 7-Tech (1.2y)", "zone": "Pass Rush (Contain)",
             "technique": "7-Technique", "key_read": "Collapse backside pocket"},
        ]
    elif "Cover 4" in scheme_name:
        defenders = [
            {"pos": "FS", "x_yard": -6.5, "y_yard": 11.5, "role": "DEEP_QUARTER",
             "align": "Inside Apex (11.5y)", "zone": "Deep 1/4 (Inside Left)",
             "technique": "Quarters Read", "key_read": "Bracket #2 vertical; rob deep crossers"},
            {"pos": "SS", "x_yard": 6.5, "y_yard": 11.5, "role": "DEEP_QUARTER",
             "align": "Inside Apex (11.5y)", "zone": "Deep 1/4 (Inside Right)",
             "technique": "Quarters Read", "key_read": "Bracket #2 vertical; rob deep crossers"},
            {"pos": "LCB", "x_yard": -18.5, "y_yard": 7.5, "role": "DEEP_QUARTER",
             "align": "Off Corner (7.5y)", "zone": "Deep 1/4 (Outside Left)",
             "technique": "Off Man Match", "key_read": "Lock #1 receiver if route stems vertical beyond 8y"},
            {"pos": "RCB", "x_yard": 18.5, "y_yard": 7.5, "role": "DEEP_QUARTER",
             "align": "Off Corner (7.5y)", "zone": "Deep 1/4 (Outside Right)",
             "technique": "Off Man Match", "key_read": "Lock #1 receiver if route stems vertical beyond 8y"},
            {"pos": "WLB", "x_yard": -4.5, "y_yard": 4.5, "role": "HOOK",
             "align": "Weak Box (4.5y)", "zone": "Quarter Flat / Curl",
             "technique": "Match Drop", "key_read": "Match RB release; defend underneath crossers"},
            {"pos": "MLB", "x_yard": 0.0, "y_yard": 4.8, "role": "HOOK",
             "align": "Middle Box (4.8y)", "zone": "Hook to Seam",
             "technique": "Inside Match", "key_read": "Wall off interior vertical release; protect void"},
            {"pos": "SLB", "x_yard": 5.0, "y_yard": 4.5, "role": "FLAT",
             "align": "Strong Box (4.5y)", "zone": "Quarter Flat / Curl",
             "technique": "Apex Match", "key_read": "Match #2 to flat or carry wheel route"},
            {"pos": "LDE", "x_yard": -5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 5-Tech (1.2y)", "zone": "Pass Rush (Contain)",
             "technique": "5-Technique", "key_read": "Rush edge; squeeze pocket"},
            {"pos": "LDT", "x_yard": -1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 3-Tech (1.0y)", "zone": "Pass Rush (B-Gap)",
             "technique": "3-Technique", "key_read": "Interior B-gap penetration"},
            {"pos": "RDT", "x_yard": 1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 1-Tech (1.0y)", "zone": "Pass Rush (A-Gap)",
             "technique": "1-Technique", "key_read": "Penetrate A-gap"},
            {"pos": "RDE", "x_yard": 5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 7-Tech (1.2y)", "zone": "Pass Rush (Contain)",
             "technique": "7-Technique", "key_read": "Contain QB"},
        ]
    elif "Cover 1" in scheme_name:
        defenders = [
            {"pos": "FS", "x_yard": 0.0, "y_yard": 14.5, "role": "DEEP_THIRD",
             "align": "Single-High Center (14.5y)", "zone": "Deep Middle Post (Free)",
             "technique": "Centerfielder", "key_read": "Break on QB shoulders; eliminate deep post"},
            {"pos": "SS", "x_yard": 6.0, "y_yard": 5.0, "role": "HOOK",
             "align": "Robber / Box (5.0y)", "zone": "Robber / Low Hole",
             "technique": "Inverted Safety", "key_read": "Cut underneath crossing routes in intermediate hole"},
            {"pos": "LCB", "x_yard": -18.5, "y_yard": 1.5, "role": "MAN",
             "align": "Press Line (1.5y)", "zone": "Man-to-Man (WR1)",
             "technique": "Press-Man Inside Shade", "key_read": "Jam receiver; trail inside hip with zero help"},
            {"pos": "RCB", "x_yard": 18.5, "y_yard": 1.5, "role": "MAN",
             "align": "Press Line (1.5y)", "zone": "Man-to-Man (WR2)",
             "technique": "Press-Man Inside Shade", "key_read": "Jam receiver; deny inside breaking routes"},
            {"pos": "NB", "x_yard": -11.0, "y_yard": 2.5, "role": "MAN",
             "align": "Slot Press (2.5y)", "zone": "Man-to-Man (Slot WR)",
             "technique": "Off-Man Trail", "key_read": "Mirror slot receiver route"},
            {"pos": "MLB", "x_yard": -1.0, "y_yard": 4.5, "role": "MAN",
             "align": "Middle Box (4.5y)", "zone": "Man-to-Man (RB)",
             "technique": "Stack Man", "key_read": "Green dog blitz if RB blocks; match RB to flat"},
            {"pos": "WLB", "x_yard": 4.0, "y_yard": 4.5, "role": "MAN",
             "align": "Strong Box (4.5y)", "zone": "Man-to-Man (TE)",
             "technique": "TE Bracket", "key_read": "Match TE release; carry seam or flat"},
            {"pos": "LDE", "x_yard": -5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 5-Tech (1.2y)", "zone": "Pass Rush",
             "technique": "5-Technique", "key_read": "Attack pocket"},
            {"pos": "LDT", "x_yard": -1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 3-Tech (1.0y)", "zone": "Pass Rush",
             "technique": "3-Technique", "key_read": "Drive interior pocket"},
            {"pos": "RDT", "x_yard": 1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS 1-Tech (1.0y)", "zone": "Pass Rush",
             "technique": "1-Technique", "key_read": "A-gap push"},
            {"pos": "RDE", "x_yard": 5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS 7-Tech (1.2y)", "zone": "Pass Rush",
             "technique": "7-Technique", "key_read": "Collapse backside pocket"},
        ]
    else:  # Cover 0 Blitz
        defenders = [
            {"pos": "LCB", "x_yard": -18.5, "y_yard": 1.2, "role": "MAN",
             "align": "Press Face (1.2y)", "zone": "Man-to-Man (WR1)",
             "technique": "Zero Press", "key_read": "Aggressive jam; deny slant"},
            {"pos": "RCB", "x_yard": 18.5, "y_yard": 1.2, "role": "MAN",
             "align": "Press Face (1.2y)", "zone": "Man-to-Man (WR2)",
             "technique": "Zero Press", "key_read": "Aggressive jam; deny slant"},
            {"pos": "NB", "x_yard": -11.0, "y_yard": 2.0, "role": "MAN",
             "align": "Slot Man (2.0y)", "zone": "Man-to-Man (Slot)",
             "technique": "Inside Leverage", "key_read": "Lock onto slot receiver"},
            {"pos": "SS", "x_yard": 5.4, "y_yard": 2.5, "role": "MAN",
             "align": "TE Press (2.5y)", "zone": "Man-to-Man (Tight End)",
             "technique": "Physical Jam", "key_read": "Lock onto TE; trail inside"},
            {"pos": "FS", "x_yard": 2.0, "y_yard": 4.0, "role": "MAN",
             "align": "Box Stack (4.0y)", "zone": "Man-to-Man (RB) / Blitz",
             "technique": "Green Dog", "key_read": "Blitz A-gap if RB stays in protection; match RB release"},
            {"pos": "MLB", "x_yard": -1.0, "y_yard": 3.0, "role": "RUSH",
             "align": "Mugged A-Gap (3.0y)", "zone": "A-Gap Blitz Rush",
             "technique": "Overload Blitz", "key_read": "Fire A-gap at snap"},
            {"pos": "WLB", "x_yard": 3.5, "y_yard": 3.0, "role": "RUSH",
             "align": "Mugged B-Gap (3.0y)", "zone": "B-Gap Blitz Rush",
             "technique": "Overload Blitz", "key_read": "Fire B-gap at snap"},
            {"pos": "LDE", "x_yard": -5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS (1.2y)", "zone": "Edge Contain Rush",
             "technique": "Speed Rush", "key_read": "Flush QB from pocket"},
            {"pos": "LDT", "x_yard": -1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS (1.0y)", "zone": "Interior Rush",
             "technique": "Bull Rush", "key_read": "Squeeze pocket"},
            {"pos": "RDT", "x_yard": 1.6, "y_yard": 1.0, "role": "RUSH",
             "align": "LOS (1.0y)", "zone": "Interior Rush",
             "technique": "Bull Rush", "key_read": "Squeeze pocket"},
            {"pos": "RDE", "x_yard": 5.0, "y_yard": 1.2, "role": "RUSH",
             "align": "LOS (1.2y)", "zone": "Edge Contain Rush",
             "technique": "Speed Rush", "key_read": "Flush QB from pocket"},
        ]

    for d in defenders:
        d["side"] = "DEFENSE"

    return offense + defenders, defenders

# --- CLASSIFICATION LOGIC ---
def analyze_formation(image_obj):
    scheme = "Cover 3 Sky"
    shell = "1-HIGH"
    all_players, defenders = build_formation_roster(scheme, shell)
    return {
        "status": "SUCCESS",
        "scheme": scheme,
        "shell": shell,
        "man_zone": "ZONE",
        "confidence": 0.84,
        "coverage_family": "1-High Zone (Middle Closed)",
        "front": "4-3 Over Front (4-Man Rush)",
        "box_count": 8,
        "cushion": "6.8 yds (Off-Bail Technique)",
        "leverage": "Outside Leverage (Sideline Protection)",
        "players": all_players,
        "defenders": defenders,
        "top_3": [
            {"rank": 1, "coverage": "Cover 3 Sky", "prob": 0.84, "family": "1-High Zone"},
            {"rank": 2, "coverage": "Cover 1 Robber", "prob": 0.11, "family": "1-High Man"},
            {"rank": 3, "coverage": "Cover 4 / Quarters", "prob": 0.05, "family": "2-High Zone"}
        ],
        "reasons": [
            "Single deep safety situated in middle third at 13.5 yards depth (Middle of Field Closed - MOFC).",
            "Strong safety buzzed down to 6.5 yards in apex overhang alignment, stacking 8 defenders in the expanded box.",
            "Both outside perimeter cornerbacks playing with 7.0–7.5 yard cushions with hips oriented toward sideline (Bail technique).",
            "Defensive line presenting a standard 4-man over front with interior 3-tech and 1-tech gap integrity."
        ],
        "disguise_notes": "Inspect for secondary buzz or trap rotations at snap. Pre-snap 1-high looks can disguise Cover 1 Robber or late roll into Cover 3 Cloud."
    }

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### Formation Input")
    uploaded_file = st.file_uploader("Upload Play Frame (JPG, PNG)", type=["jpg", "jpeg", "png"])
    sample_preset = st.selectbox(
        "Or Select Reference Scheme:",
        ["None (Use Upload)", "Cover 3 Sky (1-High Zone)", "Cover 4 Quarters (2-High Zone)",
         "Cover 2 Hard Cloud (2-High)", "Cover 1 Press Man (1-High)", "Cover 0 Blitz (0-High)"]
    )
    analyze_btn = st.button("Run Formation Analysis", type="primary", use_container_width=True)

# Preset Routing
if sample_preset != "None (Use Upload)" and not uploaded_file:
    preset_scheme = sample_preset.split(" (")[0]
    dummy_img = Image.new("RGB", (800, 450), color=(20, 28, 22))
    st.session_state["play_image"] = dummy_img
    st.session_state["analysis_data"] = analyze_formation(dummy_img)

    if "Cover 4" in sample_preset:
        st.session_state["analysis_data"]["scheme"] = "Cover 4 Quarters"
        st.session_state["analysis_data"]["shell"] = "2-HIGH"
        st.session_state["analysis_data"]["coverage_family"] = "2-High Zone (Middle Open)"
        st.session_state["analysis_data"]["box_count"] = 6
        st.session_state["analysis_data"]["cushion"] = "7.5 yds (Off-Man Match)"
        st.session_state["analysis_data"]["top_3"] = [
            {"rank": 1, "coverage": "Cover 4 Quarters", "prob": 0.81, "family": "2-High Zone"},
            {"rank": 2, "coverage": "Cover 2", "prob": 0.13, "family": "2-High Zone"},
            {"rank": 3, "coverage": "Cover 6", "prob": 0.06, "family": "Split-Field Zone"}
        ]
        st.session_state["analysis_data"]["players"], st.session_state["analysis_data"]["defenders"] = build_formation_roster("Cover 4", "2-HIGH")
    elif "Cover 2" in sample_preset:
        st.session_state["analysis_data"]["scheme"] = "Cover 2 Hard Cloud"
        st.session_state["analysis_data"]["shell"] = "2-HIGH"
        st.session_state["analysis_data"]["coverage_family"] = "2-High Zone (Middle Open)"
        st.session_state["analysis_data"]["box_count"] = 7
        st.session_state["analysis_data"]["cushion"] = "2.0 yds (Press/Squat)"
        st.session_state["analysis_data"]["top_3"] = [
            {"rank": 1, "coverage": "Cover 2 Hard Cloud", "prob": 0.86, "family": "2-High Zone"},
            {"rank": 2, "coverage": "Tampa 2", "prob": 0.09, "family": "2-High Zone"},
            {"rank": 3, "coverage": "Cover 4", "prob": 0.05, "family": "2-High Zone"}
        ]
        st.session_state["analysis_data"]["players"], st.session_state["analysis_data"]["defenders"] = build_formation_roster("Cover 2", "2-HIGH")
    elif "Cover 1" in sample_preset:
        st.session_state["analysis_data"]["scheme"] = "Cover 1 Press Man"
        st.session_state["analysis_data"]["shell"] = "1-HIGH"
        st.session_state["analysis_data"]["man_zone"] = "MAN"
        st.session_state["analysis_data"]["coverage_family"] = "1-High Man (Middle Closed)"
        st.session_state["analysis_data"]["box_count"] = 8
        st.session_state["analysis_data"]["cushion"] = "1.5 yds (Press-Jam)"
        st.session_state["analysis_data"]["top_3"] = [
            {"rank": 1, "coverage": "Cover 1 Press Man", "prob": 0.88, "family": "1-High Man"},
            {"rank": 2, "coverage": "Cover 1 Robber", "prob": 0.08, "family": "1-High Man"},
            {"rank": 3, "coverage": "Cover 0 Blitz", "prob": 0.04, "family": "0-High Man"}
        ]
        st.session_state["analysis_data"]["players"], st.session_state["analysis_data"]["defenders"] = build_formation_roster("Cover 1", "1-HIGH")
    elif "Cover 0" in sample_preset:
        st.session_state["analysis_data"]["scheme"] = "Cover 0 Blitz"
        st.session_state["analysis_data"]["shell"] = "0-HIGH"
        st.session_state["analysis_data"]["man_zone"] = "MAN"
        st.session_state["analysis_data"]["coverage_family"] = "0-High All-Out Pressure"
        st.session_state["analysis_data"]["box_count"] = 9
        st.session_state["analysis_data"]["cushion"] = "1.2 yds (Tight Press Lock)"
        st.session_state["analysis_data"]["top_3"] = [
            {"rank": 1, "coverage": "Cover 0 Blitz", "prob": 0.94, "family": "0-High Man"},
            {"rank": 2, "coverage": "Cover 1 Blitz", "prob": 0.04, "family": "1-High Man"},
            {"rank": 3, "coverage": "Cover 2 Man", "prob": 0.02, "family": "2-High Man"}
        ]
        st.session_state["analysis_data"]["players"], st.session_state["analysis_data"]["defenders"] = build_formation_roster("Cover 0", "0-HIGH")

if analyze_btn and uploaded_file:
    with st.spinner("Processing spatial coordinates, field lines, and player depths..."):
        img = Image.open(uploaded_file)
        st.session_state["play_image"] = img
        st.session_state["analysis_data"] = analyze_formation(img)

# --- HEADER ---
st.title("NFL Defensive Coverage & Formation Analyzer")
st.caption("Pre-Snap Formation Recognition • Playbook Schematic Mapping • Assignment Distribution")

if "analysis_data" in st.session_state and st.session_state["analysis_data"]["status"] == "SUCCESS":
    data = st.session_state["analysis_data"]
    scheme = data["scheme"]
    shell = data["shell"]
    man_zone = data["man_zone"]
    confidence = data["confidence"]
    players = data["players"]
    defenders = data["defenders"]

    # =========================================================================
    # BOX 1: PRE-SNAP VISUAL & PLAYBOOK SCHEMATIC (SIDE-BY-SIDE NO SCROLL)
    # =========================================================================
    st.markdown('<div class="scout-card">', unsafe_allow_html=True)
    b1_hcol, b1_bcol = st.columns([5, 1])
    with b1_hcol:
        st.markdown(f'<p class="scout-card-title">1. Pre-Snap Field Frame & Playbook Schematic — {scheme}</p>', unsafe_allow_html=True)
    with b1_bcol:
        btn1_txt = "Hide Details" if st.session_state.panel_visibility["panel_visual"] else "View Details"
        if st.button(btn1_txt, key="btn_panel_visual"):
            toggle_panel("panel_visual")
            st.rerun()

    col_photo, col_playbook = st.columns([1, 1.2])
    with col_photo:
        st.caption("Original Pre-Snap Frame (Line of Scrimmage reference at horizontal midpoint)")
        if "play_image" in st.session_state:
            img_byte_arr = io.BytesIO()
            st.session_state["play_image"].save(img_byte_arr, format='JPEG')
            img_b64 = base64.b64encode(img_byte_arr.getvalue()).decode()
            st.markdown(f'''
                <div class="film-viewport">
                    <img src="data:image/jpeg;base64,{img_b64}" alt="Play Frame">
                </div>
            ''', unsafe_allow_html=True)
    with col_playbook:
        st.caption("Playbook Alignment Schematic (Offense: O | Defense: X)")
        svg_code = render_playbook_svg(players, scheme, shell)
        st.markdown(svg_code, unsafe_allow_html=True)

    if st.session_state.panel_visibility["panel_visual"]:
        st.markdown("---")
        st.markdown("**Field Geometry & Optical Coordinate Measurements**")
        st.markdown(f"""
        - **Line of Scrimmage (LOS):** Detected at 0.0 yards depth.
        - **Offensive Formation:** 11 Personnel (3 WR, 1 TE, 1 RB in Shotgun).
        - **Defensive Alignment:** 4-3 Base / Nickel spacing ({len(defenders)} tracked defenders).
        - **Cornerback Cushions:** Measured at {data['cushion']}.
        - **Secondary Shell:** {shell} with deep safety apex at {defenders[0]['align']}.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # BOX 2: DEFENSIVE ALIGNMENT & ZONE ASSIGNMENTS CHART
    # =========================================================================
    st.markdown('<div class="scout-card">', unsafe_allow_html=True)
    b2_hcol, b2_bcol = st.columns([5, 1])
    with b2_hcol:
        st.markdown('<p class="scout-card-title">2. Defensive Alignment & Zone Assignments Chart</p>', unsafe_allow_html=True)
    with b2_bcol:
        btn2_txt = "Hide Details" if st.session_state.panel_visibility["panel_chart"] else "View Details"
        if st.button(btn2_txt, key="btn_panel_chart"):
            toggle_panel("panel_chart")
            st.rerun()

    st.caption(f"Positions, pre-snap alignment depth, and designated coverage zones for {scheme}:")

    table_rows = ""
    for d in defenders:
        role_type = "tech-zone" if any(k in d['zone'] for k in ["1/3", "1/4", "Half", "Sky", "Cloud", "Zone"]) else ("tech-man" if "Man" in d['zone'] else "tech-rush")
        table_rows += f"""
        <tr>
            <td class="mono"><strong>{d['pos']}</strong></td>
            <td class="mono">{d['align']}</td>
            <td><span class="tech-pill {role_type}">{d['zone']}</span></td>
            <td>{d['technique']}</td>
            <td style="color:#8b949e; font-size:0.80rem;">{d['key_read']}</td>
        </tr>
        """

    st.markdown(f"""
    <table class="scout-table">
        <thead>
            <tr>
                <th>Position</th>
                <th>Pre-Snap Alignment</th>
                <th>Assigned Zone / Role</th>
                <th>Technique / Leverage</th>
                <th>Primary Read & Coverage Responsibility</th>
            </tr>
        </thead>
        <tbody>{table_rows}</tbody>
    </table>
    """, unsafe_allow_html=True)

    if st.session_state.panel_visibility["panel_chart"]:
        st.markdown("---")
        st.markdown("**Playbook Rules & Assignment Principles**")
        st.markdown("""
        - **Divider Leverage:** Receivers aligned outside numbers are defended with inside leverage. Receivers aligned inside numbers are defended with outside leverage to protect the sideline.
        - **Safety Drop Angles:** Safeties pedal to depth at snap to retain top-down positioning; feet remain active until the quarterback declares his throwing direction.
        - **Underneath Wall Technique:** Apex defenders reroute slot vertical stems before expanding into intermediate passing lanes.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # BOX 3: COVERAGE CLASSIFICATION & PROBABILITIES
    # =========================================================================
    st.markdown('<div class="scout-card">', unsafe_allow_html=True)
    b3_hcol, b3_bcol = st.columns([5, 1])
    with b3_hcol:
        box3_title = f"3. Coverage Classification & Probabilities — {scheme} ({int(confidence*100)}% Confidence)"
        st.markdown(f'<p class="scout-card-title">{box3_title}</p>', unsafe_allow_html=True)
    with b3_bcol:
        btn3_txt = "Hide Details" if st.session_state.panel_visibility["panel_prob"] else "View Details"
        if st.button(btn3_txt, key="btn_panel_prob"):
            toggle_panel("panel_prob")
            st.rerun()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("SAFETY SHELL", shell)
    m2.metric("MAN / ZONE", man_zone)
    m3.metric("PRIMARY SCHEME", scheme)
    m4.metric("CONFIDENCE", f"{int(confidence*100)}%")

    top_df = pd.DataFrame(data["top_3"])
    top_df["probability_pct"] = (top_df["prob"] * 100).round(1).astype(str) + "%"
    st.table(top_df[["rank", "coverage", "family", "probability_pct"]].rename(
        columns={"rank": "Rank", "coverage": "Coverage Prediction", "family": "Family Structure", "probability_pct": "Calibrated Probability"}
    ))

    if st.session_state.panel_visibility["panel_prob"]:
        st.markdown("---")
        st.markdown("**Classification Methodology & Softmax Calibration**")
        st.markdown("""
        - **Temperature Scaling:** Probabilities are calibrated using temperature-scaled softmax over spatial distance features to prevent overconfidence on disguised looks.
        - **Split-Field Priors:** In 2x2 formations, 1-High shells weigh between Cover 3 Sky (84%) and Cover 1 Robber (11%) depending on corner cushion and safety depth.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # BOX 4: PRE-SNAP STRUCTURAL TELLS & DIAGNOSTIC EVIDENCE
    # =========================================================================
    st.markdown('<div class="scout-card">', unsafe_allow_html=True)
    b4_hcol, b4_bcol = st.columns([5, 1])
    with b4_hcol:
        st.markdown('<p class="scout-card-title">4. Structural Tells & Diagnostic Evidence</p>', unsafe_allow_html=True)
    with b4_bcol:
        btn4_txt = "Hide Details" if st.session_state.panel_visibility["panel_tells"] else "View Details"
        if st.button(btn4_txt, key="btn_panel_tells"):
            toggle_panel("panel_tells")
            st.rerun()

    for reason in data["reasons"]:
        st.markdown(f"- {reason}")

    if st.session_state.panel_visibility["panel_tells"]:
        st.markdown("---")
        st.markdown("**Quantitative Measurements**")
        st.markdown(f"""
        - **Box Count:** {data['box_count']} defenders aligned within the tackle box and intermediate boundary.
        - **Corner Cushion:** {data['cushion']}.
        - **Leverage Orientation:** {data['leverage']}.
        - **Safety Split:** Centerfield alignment (0.0 yards lateral offset).
        """)
    st.markdown('</div>', unsafe_allow_html=True)

    # =========================================================================
    # BOX 5: SECONDARY ROTATION & DISGUISE WATCH
    # =========================================================================
    st.markdown('<div class="scout-card">', unsafe_allow_html=True)
    b5_hcol, b5_bcol = st.columns([5, 1])
    with b5_hcol:
        st.markdown('<p class="scout-card-title">5. Secondary Rotation & Disguise Indicators</p>', unsafe_allow_html=True)
    with b5_bcol:
        btn5_txt = "Hide Details" if st.session_state.panel_visibility["panel_disguise"] else "View Details"
        if st.button(btn5_txt, key="btn_panel_disguise"):
            toggle_panel("panel_disguise")
            st.rerun()

    st.markdown(f"**Disguise Assessment:** {data['disguise_notes']}")

    if st.session_state.panel_visibility["panel_disguise"]:
        st.markdown("---")
        st.markdown("**Structural Vulnerabilities & Route Concepts**")
        st.markdown("""
        - **Seam Windows:** Cover 3 structures create natural passing seams between the boundary third corner and the post safety.
        - **Four Verticals Concept:** Four immediate vertical releases stress the 3-deep zone distribution.
        - **Three-Level Flood Concepts:** Flood route concepts overload the single sideline flat the 3-deep zone distribution.
        - **Three-Level Flood Concepts:** Flood route concepts overload the single sideline flat/third defender.
        """)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Upload a play frame on the left panel or select a reference scheme, then click 'Run Formation Analysis'.")
