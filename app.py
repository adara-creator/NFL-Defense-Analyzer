import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageStat
import hashlib
import streamlit.components.v1 as components

# ==========================================
# 1. DESIGN STANDARDS (PRO-STATION)
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
        letter-spacing: 15px !important; margin-top: -35px !important; text-align: center; margin-bottom: 0px !important;
    }}
    .author-sig {{
        font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #58a6ff; 
        text-align: center; letter-spacing: 4px; margin-top: -10px; margin-bottom: 30px; text-transform: uppercase;
    }}
</style>
"""

# ==========================================
# 2. INTELLIGENCE ENGINE (DETETERMINISTIC LOGIC)
# ==========================================
class TacticalIntelligence:
    def __init__(self, uploaded_file):
        self.img = Image.open(uploaded_file)
        self.hash = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
        self.seed = int(self.hash, 16)
        
        # Validation
        stats = ImageStat.Stat(self.img)
        self.is_valid = not (stats.stddev[0] < 30 and stats.mean[0] > 200)
        
        # State Decisions
        self.is_ez = (self.img.width / self.img.height) < 1.7
        p_roll = self.seed % 10
        self.personnel = "11-P (Standard)" if p_roll < 6 else ("12-P (Heavy)" if p_roll < 9 else "13-P (Jumbo)")
        self.bunch = (self.seed % 4 == 0)
        
        # Defensive Logic
        self.shell = (self.seed % 2) + 1
        self.cush = (self.seed % 8) + 4
        self.cov = f"COVER {self.shell*2}" if self.shell == 2 else "COVER 3"
        
        # Specific Coverage rules for bunches
        self.bunch_check = "STUMP / BOX" if self.shell == 2 else "LOCK / MABEL"

# ==========================================
# 3. COORDINATE RENDERING (FULL-FIX VERSION)
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

    def _draw_player(self, x, y, label, col, zone_on=False, anchor_side=1):
        tx, ty = self._warp(x, y)
        sc = (1-(y*0.015)) if self.intel.is_ez else 1
        w, h = 6.2 * sc, 3.6 * sc
        
        # Tethered Bubble zones (Red Circles)
        if zone_on and label not in ['QB','RB','LT','LG','C','RG','RT']:
            # Adjust zone position slightly to overlap the cluster in bunch
            zx, zy = self._warp(x + (3*anchor_side), y + 3)
            self.ax.plot([tx, zx], [ty, zy], color=DEF_ZONE_RED, alpha=0.3, lw=1.5, zorder=5)
            self.ax.add_patch(patches.Ellipse((zx, zy), 40*sc, 20*sc, color=DEF_ZONE_RED, alpha=0.08, ec=DEF_ZONE_RED, lw=2, ls='--'))

        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=1.2, zorder=50))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=12, fontweight='bold', family='monospace', zorder=51)

    def render(self, off_overlay, def_overlay):
        plt.axhline(0, color='white', lw=4, alpha=0.4)
        
        # --- 1. OFFENSIVE MAPPING (DETERMINISTIC) ---
        for i, x in enumerate([-20, -10, 0, 10, 20]): self._draw_player(x, -2.5, ['LT','LG','C','RG','RT'][i], '#161b22')
        self._draw_player(0, -7.5, 'QB', '#111827'); self._draw_player(10, -8.5, 'RB', '#161b22')
        
        # Skill Alignment
        bx = self.intel.bunch
        if bx:
            # Shift Z and Y into a Cluster with the TE on the Right
            skill_set = [(-90,0,'X'), (40,0,'Z'), (28,0,'Y'), (15,0,'TE')]
        else:
            skill_set = [(-95,0,'X'), (95,0,'Z'), (-45,0,'Y'), (18,0,'TE')]
        
        for x, y, lbl in skill_set: self._draw_player(x, y, lbl, '#111827')

        # --- 2. DEFENSIVE MAPPING (MATCH-TETHERED) ---
        for x in [-18, -6, 6, 18]: self._draw_player(x, 1.2, 'DL', '#111827')
        
        # Linebackers
        lb_set = [(-18, 9, 'SLB'), (0, 9, 'MLB'), (18, 9, 'WLB')]
        if bx: lb_set[1] = (22, 6, 'MLB') # Shift MLB toward Bunch
        for i, (lx, ly, ln) in enumerate(lb_set): self._draw_player(lx, ly, ln, '#161b22', zone_on=def_overlay)

        # RCB THE FIX:RCB coordinates tied to Z Receiver's current position (leverage match)
        rcb_x = 95 if not bx else 48 # Corner shifts from 95 (wide) to 48 (following bunch)
        lcb_x = -95 
        
        self._draw_player(lcb_x, self.intel.cush, 'CB', '#064e3b', zone_on=def_overlay, anchor_side=-1)
        self._draw_player(rcb_x, self.intel.cush, 'CB', '#064e3b', zone_on=def_overlay, anchor_side=1)

        # Safety Shell
        s_y = 25
        if self.intel.shell == 2:
            self._draw_player(-28, s_y, 'FS', '#1e3a8a', zone_on=def_overlay)
            self._draw_player(28, s_y, 'SS', '#1e3a8a', zone_on=def_overlay)
        else: self._draw_player(0, s_y, 'S', '#1e3a8a', zone_on=def_overlay)

        # 3. ROUTE EXPLOIT RECONSTRUCTION
        if off_overlay:
            bank = {"COVER 2": "HOLE", "COVER 3": "SEAM", "COVER 4": "POST", "COVER 1": "SLANT"}
            r_name = bank.get(self.intel.cov, "GO")
            for sx, sy, _ in skill_set:
                target_x = 0 if "POST" in r_name else (sx + (15 if sx < 0 else -15) if "OUT" in r_name else sx)
                self.ax.annotate("", xy=self._warp(target_x, 35), xytext=self._warp(sx, sy), 
                                 arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=4, alpha=0.8))

        plt.ylim(-30, 85); plt.xlim(-130, 130); plt.axis('off')
        return self.fig

# ==========================================
# 4. APP DEPLOYMENT (DARA WORKSTATION)
# ==========================================
st.set_page_config(page_title="PRO-VISION // SIGNATURE", layout="wide")
st.markdown(CSS_CONFIG, unsafe_allow_html=True)

if 'rst' not in st.session_state: st.session_state.rst = 0
st.markdown("<h1>PRO-VISION</h1><p class='author-sig'>By:Akshay Dara</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<p style='font-size:0.7rem;'>SYSTEM SENSOR</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.rst}", label_visibility="collapsed")
    o_on = st.toggle("ROUTE SCANNER", value=True)
    d_on = st.toggle("ZONE TETHERS", value=True)
    if st.button("TERMINATE SESSION"): st.session_state.rst += 1; st.rerun()

if f:
    intel = TacticalIntelligence(f)
    if not intel.is_valid: st.error("SCAN FAILED: Diagram Detected.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("PERSONNEL", intel.personnel.split()[0])
        m2.metric("CONCEPTS", "BUNCH-S" if intel.bunch else "SPREAD-A")
        m3.metric("DEFENSE", intel.cov)
        m4.metric("SYSTEM", "STABLE")

        col1, col2 = st.columns([7, 1], gap="medium")
        with col1:
            st.pyplot(SpatialRenderer(intel).render(o_on, d_on), transparent=True)
            st.image(intel.img, use_container_width=True)
        with col2:
            st.markdown("<p style='font-size:0.5rem; letter-spacing:2px; text-align:center;'>LOG_STRM</p>", unsafe_allow_html=True)
            with st.popover("[ SENSORY ]"):
                st.write(f"PERSP: {intel.persp}")
                st.write(f"HASH: {intel.hash[:8]}")
            with st.popover("[ TACTICAL ]"):
                st.markdown(f"**MODE:** {intel.bunch_check}")
                st.info("Match logic initiated over compressed receivers.")
            st.markdown(f"<div style='margin-top:250px; color:#1a1b1e; font-size:0.6rem;'>S_UID_{intel.hash[:6]}</div>", unsafe_allow_html=True)
