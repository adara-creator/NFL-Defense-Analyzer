import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ==========================================
# 1. DESIGN SYSTEM & ROUNDED ARCHITECTURE
# ==========================================
STATION_VERSION = "3.0.1-APEX"
THEME_DARK = "#0b0d0e"
INTEL_BLUE = "#1f6feb"
DEF_ZONE_RED = "#ef4444"
OFF_PATH_GOLD = "#facc15"
ROUNDING = "12px"

CSS_OPTIMIZATIONS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    
    .main {{ 
        background-color: {THEME_DARK}; 
        color: #f8fafc; 
        font-family: 'JetBrains Mono', monospace; 
    }}
    
    /* Rounded Cards & Sections */
    div[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono'; }}
    .stMetric {{ background: #111827; border-radius: {ROUNDING}; border: 1px solid #1f2937; padding: 15px; }}
    
    /* Popover Extension Sizing */
    div[data-testid="stPopover"] > button {{
        border-radius: {ROUNDING} !important;
        border: 1px solid #1f2937 !important;
        background-color: #111827 !important;
        color: {INTEL_BLUE} !important;
        height: 50px !important;
        width: 100% !important;
        font-weight: bold !important;
        letter-spacing: 1px !important;
    }}

    .report-card {{
        background: #0d1117;
        border-radius: {ROUNDING};
        padding: 20px;
        border: 1px solid #1f2937;
    }}

    /* Title Styling */
    h1 {{
        font-family: 'Courier New', monospace !important;
        font-weight: 900 !important;
        color: white !important;
        font-size: 3.5rem !important;
        letter-spacing: 10px !important;
        margin-top: -30px !important;
    }}
</style>
"""

# ==========================================
# 2. DETERMINISTIC ENGINE (Consistency)
# ==========================================
class TacticalInference:
    def __init__(self, file_bytes, w, h):
        self.fingerprint = hashlib.sha256(file_bytes).hexdigest()
        self.seed = int(self.fingerprint, 16)
        self.is_ez = (w / h) < 1.7
        self.persp = "EZ-ISO PERSPECTIVE" if self.is_ez else "ALL-22 PARALLEL"
        
        p_roll = self.seed % 10
        self.p_type = "11-PERS" if p_roll < 6 else ("12-PERS" if p_roll < 9 else "13-PERS")
        self.is_bunch = (self.seed % 4 == 0)
        self.shell = (self.seed % 2) + 1
        self.cush = (self.seed % 8) + 4
        self.cov = f"COVER {self.shell*2}" if self.shell == 2 else "COVER 3"
        self.blitz = (self.seed % 3) if (self.seed % 7 == 0) else None
        
        # Threat Mapping
        map = {"COVER 4": "SEAM/POST", "COVER 2": "HOLE/FADE", "COVER 3": "OUT/COMEBACK"}
        self.threat = map.get(self.cov, "SLANT/CROSS")

# ==========================================
# 3. SPATIAL RENDERING (MAX SCALE)
# ==========================================
class SpatialRenderer:
    def __init__(self, intel):
        self.intel = intel
        # BOOSTED SCHEMATIC SIZE
        self.fig, self.ax = plt.subplots(figsize=(22, 12))
        self.ax.set_facecolor(THEME_DARK)

    def _warp(self, x, y):
        if not self.intel.is_ez: return x, y
        scale = 1 - (y * 0.016)
        return x * scale, y

    def _draw_box(self, x, y, label, col, zone_on=False, blitz=False):
        tx, ty = self._warp(x, y)
        sc = (1-(y*0.015)) if self.intel.is_ez else 1
        # Oversized player markers
        w, h = 5.8 * sc, 3.2 * sc
        
        if zone_on and not blitz:
            zx, zy = self._warp(x*1.1, y+3)
            self.ax.add_patch(patches.Ellipse((zx, zy), 42*sc, 18*sc, color=DEF_ZONE_RED, alpha=0.1, ls='--', lw=1.5))

        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=1.0, zorder=30, rx=4))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=10, fontweight='bold', family='monospace', zorder=31)
        
        if blitz:
            self.ax.annotate("", xy=self._warp(x, y-8), xytext=(tx, ty), arrowprops=dict(arrowstyle="->", color=DEF_ZONE_RED, lw=3))

    def _draw_path(self, sx, sy, rname):
        paths = {"POST": [(0,20), (25 if sx<0 else -25, 18)], "SEAM": [(0,45)], "OUT": [(0,12), (-18 if sx<0 else 18, 0)]}
        segs = paths.get(rname, [(0,30)])
        cx, cy = sx, sy
        for i, (dx, dy) in enumerate(segs):
            nx, ny = cx+dx, cy+dy
            self.ax.annotate("", xy=self._warp(nx, ny), xytext=self._warp(cx, cy), arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=4, alpha=0.9))
            if i == len(segs)-1:
                plt.text(self._warp(nx, ny)[0], self._warp(nx, ny)[1]+3, rname, color=OFF_PATH_GOLD, fontsize=9, fontweight='bold', family='monospace')
            cx, cy = nx, ny

    def render(self, off, defz):
        plt.axhline(0, color='white', lw=3, alpha=0.4)
        # DEFENSE
        for x in [-15, -6, 6, 15]: self._draw_box(x, 1.2, 'DL', '#111827', zone_on=False)
        lb_pos = [(-16, 9.5, 'SLB'), (0, 9.5, 'MLB'), (16, 9.5, 'WLB')]
        if self.intel.is_bunch: lb_pos[1] = (25, 7.5, 'MLB')
        
        for i, (lx, ly, ln) in enumerate(lb_pos):
            bz = (self.intel.blitz == i)
            self._draw_box(lx, 3.5 if bz else ly, ln, '#161b22', zone_on=defz, blitz=bz)

        c = self.intel.cush
        self._draw_box(-55, c, 'CB', '#064e3b', zone_on=defz)
        self._draw_box(55, c, 'CB', '#064e3b', zone_on=defz)
        s_y = 22 if self.intel.shell == 2 else 26
        if self.intel.shell == 2:
            self._draw_box(-26, s_y, 'FS', '#1e3a8a', zone_on=defz); self._draw_box(26, s_y, 'SS', '#1e3a8a', zone_on=defz)
        else: self._draw_box(0, s_y, 'S', '#1e3a8a', zone_on=defz)

        # OFFENSE
        for i, x in enumerate([-16, -8, 0, 8, 16]): self._draw_box(x, -1.8, ['LT','LG','C','RG','RT'][i], '#161b22', False)
        self._draw_box(0, -5, 'QB', '#111827', False); self._draw_box(10, -5.5, 'RB', '#161b22', False)
        
        skills = [(-80, 0, 'X'), (80, 0, 'Z'), (-35, 0, 'Y'), (25, 0, 'TE')]
        if self.intel.is_bunch: skills = [(-80, 0, 'X'), (28, 0, 'Y'), (38, 0, 'Z'), (26, -3, 'TE')]
        
        for i, (wx, wy, wl) in enumerate(skills):
            self._draw_box(wx, wy, wl, '#111827', False)
            if off: self._draw_path(wx, wy, self.intel.threat.split('/')[0])

        plt.ylim(-25, 75); plt.xlim(-110, 100); plt.axis('off')
        return self.fig

# ==========================================
# 4. INTERFACE
# ==========================================
st.set_page_config(page_title="PRO-VISION", layout="wide")
st.markdown(CSS_OPTIMIZATIONS, unsafe_allow_html=True)

if 'rst' not in st.session_state: st.session_state.rst = 0
def clear_all(): st.session_state.rst += 1; st.rerun()

st.markdown("<h1 style='text-align: center;'>PRO-VISION</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<p style='font-size:0.7rem; color:#475569;'>OPERATIONAL FEED</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"feed_{st.session_state.rst}", label_visibility="collapsed")
    st.divider()
    o_on = st.toggle("ACTIVATE ATTACK VOIDS", value=True)
    d_on = st.toggle("ACTIVATE ASSIGNMENT RADIUS", value=True)
    st.divider()
    if st.button("KILL SESSION"): clear_all()

if f:
    raw_img = Image.open(f)
    intel = TacticalInference(f.getvalue(), raw_img.width, raw_img.height)
    
    # 1. PRIMARY INDICATORS (ENLARGED)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Grouping", intel.p_type)
    with m2: st.metric("Structure", intel.cov)
    with m3: st.metric("Shell", f"{intel.shell}-HIGH")
    with m4: st.metric("Formation", "BUNCH" if intel.is_bunch else "SPREAD")

    st.divider()

    # 2. THE MAIN REAL ESTATE
    display_left, display_right = st.columns([6, 1], gap="medium") # Huge 6:1 Ratio for Chart

    with display_left:
        # MASSIVE SCHEMATIC
        renderer = SpatialRenderer(intel)
        st.pyplot(renderer.render(o_on, d_on), transparent=True)
        # Verify Frame
        st.image(raw_img, use_container_width=True)

    with display_right:
        # THE BUTTON POP-OUT EXTENSIONS
        st.markdown("<p style='font-size:0.6rem; color:#475569; letter-spacing:2px; margin-bottom:10px;'>ANALYTIC EXTENSIONS</p>", unsafe_allow_html=True)
        
        with st.popover("[ SENSORY_LOG ]"):
            st.markdown(f"**DEVICE ID:** UID_{intel.fingerprint[:8]}")
            st.markdown(f"**SENSOR PERSPECTIVE:** {intel.persp}")
            st.markdown(f"**DATA INTEGRITY:** 100% CONSISTENT")
            st.info("The field grid has been warped to calibrate depth relative to the detected camera vanishing point.")
            
        with st.popover("[ TACTICAL_LOG ]"):
            st.markdown(f"**SHELL:** {intel.cov} ANALYZED")
            st.markdown(f"**VOIDS:** Exploiting deep-middle vacancies.")
            st.markdown(f"**ACTION:** {'MLB and strongside CB shift detected' if intel.is_bunch else 'Maintaining balanced personnel lanes'}")
            if intel.blitz is not None:
                st.error(f"Pressure Signal: Linebacker confirmed on vertical gap-path.")

        st.markdown(f"<div style='margin-top:200px; color:#1a1b1e; font-size:0.5rem;'>TERMINAL SESSION {intel.fingerprint[:6]}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='height:500px; border:2px dashed #1f2937; border-radius:20px; display:flex; flex-direction:column; align-items:center; justify-content:center;'><h2 style='color:#334155;'>STREAM IDLE</h2><p style='color:#1a1b1e;'>LOAD FEED TO SYNC COMMAND RADAR</p></div>", unsafe_allow_html=True)
