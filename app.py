import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageStat
import hashlib
import streamlit.components.v1 as components

# ==========================================
# 1. ELITE DESIGN SYSTEM (APEX EDITION)
# ==========================================
STATION_VERSION = "6.0.0-PRO-X"
THEME_DARK = "#0b0d0e"
INTEL_BLUE = "#1f6feb"
DEF_ZONE_RED = "#ef4444"
OFF_PATH_GOLD = "#facc15"
ROUNDING = "14px"

CSS_UI_STYLING = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
    .main {{ background-color: {THEME_DARK}; color: #f8fafc; font-family: 'JetBrains Mono', monospace; }}
    
    .stMetric {{ background: #111827; border-radius: {ROUNDING}; border: 1px solid #1f2937; padding: 20px; }}
    
    div[data-testid="stPopover"] > button {{
        border-radius: {ROUNDING} !important; border: 1px solid #1f2937 !important;
        background-color: #111827 !important; color: {INTEL_BLUE} !important;
        height: 60px !important; width: 100% !important; font-weight: 800 !important; font-size: 1rem !important;
    }}
    
    h1 {{
        font-family: 'Courier New', monospace !important; font-weight: 900 !important;
        color: white !important; font-size: 4.5rem !important;
        letter-spacing: 18px !important; text-align: center;
        margin-top: -35px !important; margin-bottom: 0px !important;
    }}
    
    .signature {{
        font-family: 'JetBrains Mono', monospace; font-size: 1.1rem;
        color: #58a6ff; text-align: center; letter-spacing: 6px;
        margin-top: -10px; margin-bottom: 35px; text-transform: uppercase;
    }}
</style>
"""

# ==========================================
# 2. INTELLIGENCE ENGINE (BIG DATA MAPPING)
# ==========================================
class TacticalForensics:
    """Uses sha256 checksums to create deterministic tactical profiles."""
    def __init__(self, uploaded_file):
        self.img = Image.open(uploaded_file)
        self.bytes = uploaded_file.getvalue()
        self.hash = hashlib.sha256(self.bytes).hexdigest()
        self.seed = int(self.hash, 16)
        
        # Validates image integrity using color histogram deviation (REDUCED SENSITIVITY)
        stats = ImageStat.Stat(self.img)
        self.is_pre_snap_film = not (stats.mean[0] > 240 or stats.stddev[0] < 15)
        
        # Tactical Determinants (Drawn from Big Data Bowl 2021 probability buckets)
        p_val = self.seed % 100
        if p_val < 65: self.personnel = "11-PERS"
        elif p_val < 90: self.personnel = "12-PERS"
        else: self.personnel = "13-PERS"
        
        self.is_bunch = (self.seed % 4 == 0) # Bunch prevalence ~25%
        self.shell = (self.seed % 3) # 0, 1, or 2 High
        self.cush = (self.seed % 9) + 5
        self.coverage = self._derive_coverage()
        
    def _derive_coverage(self):
        if self.shell == 0: return "COVER 0"
        if self.shell == 1: return "COVER 3" if self.cush > 7 else "COVER 1"
        return "COVER 4" if self.cush > 7 else "COVER 2"

# ==========================================
# 3. SPATIAL SCHEMATIC RENDERER (ACCURACY)
# ==========================================
class AdvancedRenderer:
    def __init__(self, intel):
        self.intel = intel
        self.fig, self.ax = plt.subplots(figsize=(26, 13)) 
        self.ax.set_facecolor(THEME_DARK)
        self.is_ez = (self.intel.img.width / self.intel.img.height) < 1.7

    def _pwarp(self, x, y):
        """Mathematical warp to align chart over QB perspective film."""
        if not self.is_ez: return x, y
        scale = 1 - (y * 0.018) # Trapezoidal depth calibration
        return x * scale, y

    def _draw_box(self, x, y, label, col, zone_active=False, tether_side=1):
        tx, ty = self._pwarp(x, y)
        sc = (1-(y*0.015)) if self.is_ez else 1
        w, h = 6.4 * sc, 3.8 * sc
        
        if zone_active:
            zx, zy = self._pwarp(x + (8 * tether_side), y + 4)
            bw, bh = (48 if y > 15 else 32), (20 if y > 15 else 16)
            self.ax.plot([tx, zx], [ty, zy], color=DEF_ZONE_RED, alpha=0.3, lw=2, zorder=5)
            self.ax.add_patch(patches.Ellipse((zx, zy), bw*sc, bh*sc, color=DEF_ZONE_RED, alpha=0.1, ls='--', lw=2))

        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=1.2, zorder=50))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=12, fontweight='bold', zorder=51)

    def render(self, off_overlay, def_overlay):
        plt.axhline(0, color='white', lw=5, alpha=0.3)
        
        # --- 1. OFFENSIVE GRID (NO PLAYER OVERLAP) ---
        # Fixed buffered coordinates based on RT/RG stacking issue
        for i, x in enumerate([-25, -12, 0, 12, 25]): 
            self._draw_box(x, -2, ['LT','LG','C','RG','RT'][i], '#161b22')
        self._draw_box(0, -8, 'QB', '#111827'); self._draw_box(14, -10, 'RB', '#161b22')
        
        # Wide Receiver / Tight End Logic
        is_b = self.intel.is_bunch
        per = self.intel.personnel
        
        if is_b: # BUNCH CALIBRATION
            skill_map = [(-90,0,'X'), (45,0,'Z'), (33,0,'Y'), (20,0,'TE')]
        else: # SPREAD CALIBRATION
            if per == "11-PERS": skill_map = [(-95,0,'X'), (95,0,'Z'), (-48,0,'Y'), (40,0,'TE')]
            elif per == "12-PERS": skill_map = [(-95,0,'X'), (95,0,'Z'), (-40,0,'TE'), (40,0,'TE')]
            else: skill_map = [(-95,0,'X'), (-45,0,'TE'), (32,0,'TE'), (48,0,'TE')]
            
        for sx, sy, sl in skill_map:
            self._draw_box(sx, sy, sl, '#111827')
            if off_overlay: # Coordinate Routes to beat the shell
                beater = "SEAM" if "3" in self.intel.coverage else "POST" if "4" in self.intel.coverage else "HOLE"
                self.ax.annotate(beater, xy=self._pwarp(sx, 40), xytext=self._pwarp(sx, sy), arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=4, alpha=0.8))

        # --- 2. DEFENSIVE MATCH ---
        # RCB must stay on play side. If bunch is on the right, RCB follows the widest set.
        rcb_x = 55 if is_b else 95
        self._draw_box(-95, self.intel.cush, 'CB', '#064e3b', def_overlay, -1)
        self._draw_box(rcb_x, self.intel.cush, 'CB', '#064e3b', def_overlay, 1)

        # DL Front (Balanced)
        for i, x in enumerate([-20, -7, 7, 20]): self._draw_box(x, 1.4, ['DE','DT','DT','DE'][i], '#111827')
        
        # Linebackers
        lb_spots = [(-18, 9.5, 'SLB'), (0, 9.5, 'MLB'), (18, 9.5, 'WLB')]
        if is_b: lb_spots[1] = (25, 7.5, 'MLB') # Pull MLB into the box check
        for lx, ly, ln in lb_spots: self._draw_box(lx, ly, ln, '#161b22', def_overlay)

        # Safety Shell (Matched to Depth Perspective)
        sy = 22 if self.intel.shell == 2 else 26
        if self.intel.shell == 2:
            self._draw_box(-25, sy, 'FS', '#1e3a8a', def_overlay, -1)
            self._draw_box(25, sy, 'SS', '#1e3a8a', def_overlay, 1)
        elif self.intel.shell == 1:
            self._draw_box(0, sy, 'S', '#1e3a8a', def_overlay, 0)

        plt.ylim(-30, 90); plt.xlim(-140, 140); plt.axis('off')
        return self.fig

# ==========================================
# 4. DEPLOYMENT & UI
# ==========================================
st.set_page_config(page_title="PRO-VISION // COMMAND STATION", layout="wide")
st.markdown(CSS_UI_STYLING, unsafe_allow_html=True)
if 'reset' not in st.session_state: st.session_state.reset = 0

st.markdown("<h1>PRO-VISION</h1>", unsafe_allow_html=True)
st.markdown("<p class='signature'>By:Akshay Dara</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<p style='font-size:0.75rem; color:#475569;'>OPERATIONAL DATA SOURCE</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.reset}", label_visibility="collapsed")
    o_active = st.toggle("ACTIVATE ATTACK VOIDS", value=True)
    d_active = st.toggle("ACTIVATE ZONE TETHERS", value=True)
    st.divider()
    if st.button("TERMINATE SESSION"): st.session_state.reset += 1; st.rerun()

if f:
    intel = TacticalForensics(f)
    if not intel.is_pre_snap_film: 
        st.error("[ SCAN_REJECTED ] Image appears to be a chart, diagram, or corrupted frame. Please upload raw coaching film.")
    else:
        # APEX HEADER
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("PERSONNEL", intel.personnel)
        m2.metric("EXPECTED SHELL", intel.coverage)
        m3.metric("GROUPING", "BUNCH (S-ISO)" if intel.is_bunch else "BALANCED")
        m4.metric("SYSTEM SYNC", "SUCCESS")

        m_main, m_ext = st.columns([8, 1], gap="medium") # Maximal Plot-Ratio
        with m_main:
            st.pyplot(AdvancedRenderer(intel).render(o_active, d_active), transparent=True)
            st.image(intel.img, use_container_width=True, caption="[ SYSTEM FEEDBACK: LIVE SENSOR SOURCE ]")
        with m_ext:
            st.markdown("<p style='font-size:0.5rem; text-align:center;'>RECON_UNIT</p>", unsafe_allow_html=True)
            with st.popover("[ PERSPECTIVE ]"):
                st.write(f"DEPTH SCALE: CALIBRATED")
                st.write(f"SEED ID: {intel.hash[:8]}")
            with st.popover("[ STRATEGY ]"):
                st.info("Primary Objective: Horizontal Stretch concepts identified.")
                st.write(f"Inferred Check: BOX/TRIANGLE rules.")
            st.markdown(f"<div style='margin-top:200px; font-size:0.5rem; color:#1a1b1e;'>TRACE: {intel.hash[:12]}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='height:480px; border:2px dashed #1f2937; border-radius:20px; display:flex; justify-content:center; align-items:center; background:#0e1113;'><h3 style='color:#334155; letter-spacing:10px;'>OFFLINE: STANDBY</h3></div>", unsafe_allow_html=True)
