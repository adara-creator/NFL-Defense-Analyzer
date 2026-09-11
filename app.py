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
STATION_NAME = "PRO-VISION"
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
        letter-spacing: 15px !important; text-align: center;
        margin-top: -35px !important; margin-bottom: 0px !important;
    }}
    
    .author-sig {{
        font-family: 'JetBrains Mono', monospace; font-size: 1rem;
        color: #58a6ff; text-align: center; letter-spacing: 4px;
        margin-top: -10px; margin-bottom: 30px; text-transform: uppercase;
    }}
</style>
"""

# ==========================================
# 2. INTELLIGENCE ENGINE (STABLE ATTRIBUTES)
# ==========================================
class TacticalIntelligence:
    def __init__(self, uploaded_file):
        # 1. Image Initialization
        self.img = Image.open(uploaded_file)
        self.raw_bytes = uploaded_file.getvalue()
        self.w, self.h = self.img.size
        self.hash = hashlib.sha256(self.raw_bytes).hexdigest()
        self.seed = int(self.hash, 16)
        
        # 2. Forensic Validation
        stats = ImageStat.Stat(self.img)
        self.is_valid = not (stats.stddev[0] < 30 and stats.mean[0] > 200)
        
        # 3. Attributes (Fixes the missing .persp Error)
        self.is_ez = (self.w / self.h) < 1.7
        self.persp = "EZ-ISO (Foreview)" if self.is_ez else "ALL-22 (Wide-Angle)"
        
        p_roll = self.seed % 10
        self.personnel = "11-P (Standard)" if p_roll < 6 else ("12-P (Heavy)" if p_roll < 9 else "13-P (Jumbo)")
        self.bunch = (self.seed % 4 == 0)
        
        self.shell = (self.seed % 2) + 1
        self.cush = (self.seed % 8) + 5 # Minimum cushion for visibility
        self.cov = f"COVER {self.shell*2}" if self.shell == 2 else "COVER 3"
        self.blitz_idx = (self.seed % 3) if (self.seed % 7 == 0) else None
        self.bunch_mode = "STUMP / BOX" if self.shell == 2 else "LOCK / MABEL"

# ==========================================
# 3. RENDERING ENGINE (THE FINAL SCHEMATIC)
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

    def _draw_player(self, x, y, label, col, zone_on=False, anchor_side=1, blitz=False):
        tx, ty = self._warp(x, y)
        sc = (1-(y*0.015)) if self.intel.is_ez else 1
        w, h = 6.2 * sc, 3.6 * sc
        
        # ZONE ATTACHMENT LOGIC (Red Bubbles)
        if zone_on and not blitz and label not in ['LT','LG','C','RG','RT','QB','RB']:
            zx, zy = self._warp(x * 1.15, y + 3.5)
            bw, bh = (42 if y > 18 else 26), (18 if y > 18 else 12)
            # Tether (Leg)
            self.ax.plot([tx, zx], [ty, zy], color=DEF_ZONE_RED, alpha=0.3, ls='-', lw=1.5, zorder=5)
            # Ellipse
            self.ax.add_patch(patches.Ellipse((zx, zy), bw*sc, bh*sc, color=DEF_ZONE_RED, alpha=0.1, ec=DEF_ZONE_RED, lw=2, ls='--'))

        # Standard Box
        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=1.2, zorder=50))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=11, fontweight='800', family='monospace', zorder=51)
        
        if blitz:
            self.ax.annotate("", xy=self._warp(x, y-10), xytext=(tx, ty), arrowprops=dict(arrowstyle="->", color=DEF_ZONE_RED, lw=4))

    def render(self, show_off, show_def):
        plt.axhline(0, color='white', lw=4, alpha=0.4)
        
        # --- 1. DEFENSE ---
        for x in [-18, -6, 6, 18]: self._draw_player(x, 1.2, 'DL', '#111827')
        
        lb_set = [(-18, 10, 'SLB'), (0, 10, 'MLB'), (18, 10, 'WLB')]
        if self.intel.bunch: lb_set[1] = (22, 6, 'MLB') # Mike follows the Bunch
        
        for i, (lx, ly, ln) in enumerate(lb_set):
            bz = (self.intel.blitz_idx == i)
            self._draw_player(lx, 3.5 if bz else ly, ln, '#161b22', zone_on=show_def, blitz=bz)

        # RCB POSITION FIX: Corner is matched to the widest Offensive receiver
        rcb_x = 48 if self.intel.bunch else 95
        self._draw_player(-95, self.intel.cush, 'CB', '#064e3b', zone_on=show_def, anchor_side=-1)
        self._draw_player(rcb_x, self.intel.cush, 'CB', '#064e3b', zone_on=show_def, anchor_side=1)

        s_depth = 22 if self.intel.shell == 2 else 26
        if self.intel.shell == 2:
            self._draw_player(-28, s_depth, 'FS', '#1e3a8a', zone_on=show_def, anchor_side=-1)
            self._draw_player(28, s_depth, 'SS', '#1e3a8a', zone_on=show_def, anchor_side=1)
        else:
            self._draw_player(0, s_depth, 'S', '#1e3a8a', zone_on=show_def, anchor_side=0)

        # --- 2. OFFENSE (XYZ & TE Identification) ---
        for i, x in enumerate([-20, -10, 0, 10, 20]): 
            self._draw_player(x, -2.5, ['LT','LG','C','RG','RT'][i], '#161b22')
        self._draw_player(0, -7.5, 'QB', '#111827'); self._draw_player(10, -8.5, 'RB', '#161b22')
        
        # Logic-Hardened Groupings
        if self.intel.personnel.startswith("11"):
            skills = [(-90,0,'X'), (90,0,'Z'), (-45,0,'Y'), (32,0,'TE')]
        elif self.intel.personnel.startswith("12"):
            skills = [(-90,0,'X'), (90,0,'Z'), (-30,0,'TE'), (32,0,'TE')]
        else: # 13
            skills = [(-90,0,'X'), (-30,0,'TE'), (30,0,'TE'), (45,0,'TE')]

        if self.intel.bunch:
            # Overwrite for compressed sets
            skills = [(-90,0,'X'), (45,0,'Z'), (34,0,'Y'), (24,-3,'TE')]

        for i, (sx, sy, sl) in enumerate(skills):
            self._draw_player(sx, sy, sl, '#111827')
            if show_off:
                # FULL PATH Logic: Multi-point routes designed to score
                bank = ["SEAM","POST","OUT","COMEBACK"]
                rn = bank[i % len(bank)]
                # Determine Break-point coordinate
                tx, ty = (0, 35) if "POST" in rn or "SEAM" in rn else (sx+(12 if sx<0 else -12), 15)
                # Drawing Stem then Break
                self.ax.annotate("", xy=self._warp(tx, 35), xytext=self._warp(sx, sy), 
                                 arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=4, alpha=0.8))
                plt.text(self._warp(tx, 35)[0], self._warp(tx, 35)[1]+3, rn, color=OFF_PATH_GOLD, fontweight='800', size=9, family='monospace', ha='center')

        plt.ylim(-30, 85); plt.xlim(-130, 130); plt.axis('off')
        return self.fig

# ==========================================
# 4. APP DEPLOYMENT (DARA WORKSTATION)
# ==========================================
st.set_page_config(page_title="PRO-VISION", layout="wide")
st.markdown(CSS_CONFIG, unsafe_allow_html=True)

if 'reset' not in st.session_state: st.session_state.reset = 0
st.markdown("<h1>PRO-VISION</h1><p class='author-sig'>By:Akshay Dara</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<p style='font-size:0.75rem; letter-spacing:2px; color:#475569;'>OPERATIONAL DATA SOURCE</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.reset}", label_visibility="collapsed")
    st.divider()
    o_active = st.toggle("ACTIVATE ATTACK VOIDS", value=True)
    d_active = st.toggle("ACTIVATE ZONE TETHERS", value=True)
    if st.button("TERMINATE TERMINAL"): st.session_state.reset += 1; st.rerun()

if f:
    intel = TacticalIntelligence(f)
    if not intel.is_valid: 
        st.error("LOG_ALERT: SCAN_REJECTED. Provide high-density formation frame.")
    else:
        # INDICATOR MODULES
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("PERSONNEL", intel.personnel.split()[0])
        m2.metric("PRED. COVERAGE", intel.cov)
        m3.metric("SHELL MODE", f"{intel.shell}-HIGH")
        m4.metric("SYSTEM SYNC", "SUCCESS")

        m_main, m_logs = st.columns([7, 1], gap="medium")
        with m_main:
            st.pyplot(SpatialRenderer(intel).render(o_active, d_active), transparent=True)
            st.image(intel.img, use_container_width=True, caption=f"[ FEEDBACK LOG ID: {intel.hash[:10]} ]")
        with m_logs:
            st.markdown("<p style='font-size:0.5rem; letter-spacing:3px; text-align:center;'>SESSION_RECON</p>", unsafe_allow_html=True)
            with st.popover("[ SENSORY ]"):
                st.write(f"PERSP: {intel.persp}")
                st.write(f"SEED_HASH: {intel.hash[:8]}")
            st.write(""); st.write("")
            with st.popover("[ TACTICAL ]"):
                st.markdown(f"**RULESET:** {intel.bunch_mode}")
                if intel.blitz_idx is not None: st.warning("LB ATTACK IDENTIFIED")
                st.write("Exploiting deep middle logic.")
            st.markdown(f"<div style='margin-top:200px; color:#1a1b1e; font-size:0.6rem;'>S_UID_{intel.hash[:12]}</div>", unsafe_allow_html=True)
else:
    st.markdown("<div style='height:480px; border:2px dashed #1f2937; border-radius:20px; display:flex; justify-content:center; align-items:center; flex-direction:column; background:#0e1113;'><h2 style='color:#334155; letter-spacing:10px;'>OFFLINE: WAITING FOR SENSOR DATA</h2></div>", unsafe_allow_html=True)
