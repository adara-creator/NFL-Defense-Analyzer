import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageStat
import hashlib
import streamlit.components.v1 as components

# ==========================================
# 1. VISUAL DESIGN STANDARDS
# ==========================================
THEME_DARK = "#0b0d0e"
INTEL_BLUE = "#1f6feb"
DEF_ZONE_RED = "#ef4444"
OFF_PATH_GOLD = "#facc15"
ROUNDING = "14px"

CSS_CONFIG = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    .main {{ background-color: {THEME_DARK}; color: #f8fafc; font-family: 'JetBrains Mono', monospace; }}
    .stMetric {{ background: #111827; border-radius: {ROUNDING}; border: 1px solid #1f2937; padding: 18px; }}
    div[data-testid="stPopover"] > button {{
        border-radius: {ROUNDING} !important; border: 1px solid #1f2937 !important;
        background-color: #111827 !important; color: {INTEL_BLUE} !important;
        height: 55px !important; width: 100% !important; font-weight: 800 !important;
    }}
    h1 {{
        font-family: 'Courier New', monospace !important; font-weight: 900 !important;
        color: white !important; font-size: 4rem !important;
        letter-spacing: 15px !important; text-align: center; margin-bottom: 0px !important; margin-top: -30px !important;
    }}
    .author-sig {{
        font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #58a6ff; 
        text-align: center; letter-spacing: 4px; margin-top: -10px; margin-bottom: 30px; text-transform: uppercase;
    }}
</style>
"""

# ==========================================
# 2. INTELLIGENCE ENGINE (TACHTICAL MAPPING)
# ==========================================
class TacticalIntelligence:
    def __init__(self, uploaded_file):
        self.img = Image.open(uploaded_file)
        self.hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        self.seed = int(self.hash, 16)
        
        # Validates if image is likely football film via color variance
        stats = ImageStat.Stat(self.img)
        self.is_valid = not (stats.stddev[0] < 20 and stats.mean[0] > 210)
        self.is_ez = (self.img.width / self.img.height) < 1.7
        self.persp = "EZ-ISO (Foreview)" if self.is_ez else "ALL-22 (Wide)"
        
        # Deterministic Tactics
        shell_roll = self.seed % 3 # 0, 1, or 2 high
        self.shell = shell_roll
        self.cush = (self.seed % 8) + 4
        
        # Coverage Decision Logic
        if self.shell == 0: self.cov = "COVER 0 (BLITZ)"
        elif self.shell == 1: self.cov = "COVER 1" if self.cush < 5 else "COVER 3"
        else: self.cov = "COVER 4" if self.cush > 6 else "COVER 2"
        
        p_roll = self.seed % 10
        self.personnel = "11-P" if p_roll < 6 else ("12-P" if p_roll < 9 else "13-P")
        self.bunch = (self.seed % 5 == 0)

        # OFFENSIVE PLAYBOOK ENGINE: Linked to Defense Output
        # Each concept consists of a 4-man integrated route plan
        concepts = {
            "COVER 0 (BLITZ)": ["SLANT", "CROSS", "SLANT", "FLAT"],
            "COVER 1": ["FADE", "POST-COR", "POST", "CROSS"],
            "COVER 2": ["HOLE-FADE", "POST", "POST", "HOLE-OUT"],
            "COVER 3": ["SEAM", "COMEBACK", "CURL", "SEAM"],
            "COVER 4": ["HITCH", "OUT", "HITCH", "S-POST"]
        }
        self.play_concept = concepts.get(self.cov, ["GO", "GO", "GO", "GO"])

# ==========================================
# 3. SPATIAL RENDERER (BEAT-MAP SCHEMATIC)
# ==========================================
class SpatialRenderer:
    def __init__(self, intel):
        self.intel = intel
        self.fig, self.ax = plt.subplots(figsize=(26, 12)) 
        self.ax.set_facecolor(THEME_DARK)

    def _warp(self, x, y):
        if not self.intel.is_ez: return x, y
        scale = 1 - (y * 0.016)
        return x * scale, y

    def _draw_player(self, x, y, label, col, zone_on=False, side=1):
        tx, ty = self._warp(x, y)
        sc = (1-(y*0.015)) if self.intel.is_ez else 1
        w, h = 6.4 * sc, 3.6 * sc
        
        if zone_on and label not in ['QB','RB','LT','LG','C','RG','RT']:
            zx, zy = self._warp(x + (3*side), y + 4)
            self.ax.plot([tx, zx], [ty, zy], color=DEF_ZONE_RED, alpha=0.3, lw=1.5, zorder=5)
            self.ax.add_patch(patches.Ellipse((zx, zy), 42*sc, 22*sc, color=DEF_ZONE_RED, alpha=0.08, ec=DEF_ZONE_RED, lw=1.5, ls='--'))

        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=1.2, zorder=50))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=11, fontweight='800', family='monospace', zorder=51)

    def _render_route(self, sx, sy, name):
        # Precise vector segments for different route concepts
        schemes = {
            "SEAM": [(0, 45)], "FADE": [(8 if sx<0 else -8, 35)], "SLANT": [(0,3),(18 if sx<0 else -18,12)],
            "POST": [(0,15),(25 if sx<0 else -25,18)], "OUT": [(0,10),(-12 if sx<0 else 12,0)],
            "CURL": [(0,14),(0,-3)], "HITCH": [(0,7),(0,-2)], "COMEBACK": [(0,15),(6 if sx<0 else -6,-4)],
            "HOLE-FADE": [(4 if sx<0 else -4, 18), (8 if sx<0 else -8, 20)],
            "POST-COR": [(0,14),(10 if sx<0 else -10, 8), (-12 if sx<0 else 12, 10)]
        }
        segs = schemes.get(name, [(0,30)])
        cx, cy = sx, sy
        for i, (dx, dy) in enumerate(segs):
            nx, ny = cx + dx, cy + dy
            p1, p2 = self._warp(cx, cy), self._warp(nx, ny)
            self.ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=4, alpha=0.9))
            if i == len(segs)-1:
                plt.text(p2[0], p2[1]+2.5, name, color=OFF_PATH_GOLD, fontsize=9, fontweight='800', family='monospace', ha='center')
            cx, cy = nx, ny

    def build_field(self, show_off, show_def):
        plt.axhline(0, color='white', lw=4, alpha=0.3)
        # 1. DEFENSE POSITIONING
        for x in [-18, -6, 6, 18]: self._draw_player(x, 1.2, 'DL', '#111827')
        lb_set = [(-18, 10, 'SLB'), (0, 10, 'MLB'), (18, 10, 'WLB')]
        if self.intel.bunch: lb_set[1] = (25, 7, 'MLB') # Nickel/Star move over bunch
        for lx, ly, ln in lb_set: self._draw_player(lx, ly, ln, '#161b22', show_def)
        
        rcb_x = 45 if self.intel.bunch else 95
        self._draw_player(-95, self.intel.cush, 'CB', '#064e3b', show_def, -1)
        self._draw_player(rcb_x, self.intel.cush, 'CB', '#064e3b', show_def, 1)

        if self.intel.shell == 2:
            self._draw_player(-28, 24, 'FS', '#1e3a8a', show_def); self._draw_player(28, 24, 'SS', '#1e3a8a', show_def)
        elif self.intel.shell == 1:
            self._draw_player(0, 26, 'S', '#1e3a8a', show_def)

        # 2. OFFENSE personnel SETS
        for i, x in enumerate([-20, -10, 0, 10, 20]): self._draw_player(x, -2.5, ['LT','LG','C','RG','RT'][i], '#161b22')
        self._draw_player(0, -7.5, 'QB', '#111827'); self._draw_player(12, -8.5, 'RB', '#161b22')

        p_str = self.intel.personnel
        if "11" in p_str: skill_spots = [(-90,0,'X'), (90,0,'Z'), (-40,0,'Y'), (32,0,'TE')]
        elif "12" in p_str: skill_spots = [(-90,0,'X'), (90,0,'Z'), (-30,0,'TE'), (32,0,'TE')]
        else: skill_spots = [(-90,0,'X'), (-32,0,'TE'), (18,0,'TE'), (45,0,'TE')]

        if self.intel.bunch: skill_spots = [(-90,0,'X'), (38,0,'Z'), (28,0,'Y'), (18,0,'TE')]

        for i, (sx, sy, sl) in enumerate(skill_spots):
            self._draw_player(sx, sy, sl, '#111827')
            if show_off: self._render_route(sx, sy, self.intel.play_concept[i])

        plt.ylim(-30, 85); plt.xlim(-130, 130); plt.axis('off')
        return self.fig

# ==========================================
# 4. DASHBOARD DEPLOYMENT
# ==========================================
st.set_page_config(page_title="PRO-VISION // COMMAND", layout="wide")
st.markdown(CSS_CONFIG, unsafe_allow_html=True)
if 'r' not in st.session_state: st.session_state.r = 0

st.markdown("<h1>PRO-VISION</h1><p class='author-sig'>By:Akshay Dara</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<p style='font-size:0.7rem;'>SECURE HUB</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.r}", label_visibility="collapsed")
    o_tog = st.toggle("ACTIVATE ATTACK VOIDS", value=True)
    d_tog = st.toggle("ACTIVATE ASSIGNMENT BUBBLES", value=True)
    if st.button("KILL TERMINAL"): st.session_state.r += 1; st.rerun()

if f:
    intel = TacticalIntelligence(f)
    if not intel.is_valid: st.error("ANALYSIS REJECTED: Not Football Formation")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("PERSONNEL", intel.personnel.split()[0])
        m2.metric("DEFENSE", intel.cov)
        m3.metric("STRUCTURE", "BUNCH-R" if intel.bunch else "SPREAD-A")
        m4.metric("SYSTEM", "STABLE")

        main, logs = st.columns([7, 1], gap="medium")
        with main:
            st.pyplot(SpatialRenderer(intel).build_field(o_tog, d_tog), transparent=True)
            st.image(intel.img, use_container_width=True)
        with logs:
            st.markdown("<p style='font-size:0.5rem; text-align:center;'>RECON_S</p>", unsafe_allow_html=True)
            with st.popover("[ SENSORY ]"):
                st.write(f"CAM: {intel.persp}")
                st.write(f"SEED: {intel.hash[:6]}")
            with st.popover("[ TACTICAL ]"):
                st.markdown(f"**VOIDS:** Vertical Seams") if "3" in intel.cov else st.markdown(f"**VOIDS:** Perimeter Hole")
                st.write(f"OFF_BEATER: {intel.play_concept[0]}")
            st.markdown(f"<div style='margin-top:280px; color:#1a1b1e; font-size:0.5rem;'>ID_{intel.hash[:8]}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='height:480px; border:2px dashed #1f2937; border-radius:20px; display:flex; justify-content:center; align-items:center; flex-direction:column; background:#0e1113;'><h2 style='color:#334155; letter-spacing:10px;'>AWAITING SENSOR LINK</h2></div>", unsafe_allow_html=True)
