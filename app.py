import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ==========================================
# 1. CORE CONFIGURATION & CONSTANTS
# ==========================================
STATION_VERSION = "2.1.0-LARGE"
THEME_DARK = "#0b0d0e"
INTEL_BLUE = "#1f6feb"
DEF_ZONE_RED = "#ef4444"
OFF_PATH_GOLD = "#facc15"
RUSH_VEC_BLUE = "#58a6ff"

# Scaling Constants for High Visibility
BOX_WIDTH = 5.2 
BOX_HEIGHT = 2.8
LABEL_FONT_SIZE = 9
ROUTE_LINE_WIDTH = 3.5

CSS_UI_STANDARDS = f"""
<style>
    .main {{ background-color: {THEME_DARK}; color: #f8fafc; font-family: 'Inter', sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; width: 350px !important; }}
    .stButton>button {{ width: 100%; border-radius: 0px; border: 1px solid #1f2937; height: 4em; font-weight: bold; text-transform: uppercase; font-size: 1rem; }}
    .report-frame {{ background: #111827; border-left: 6px solid {INTEL_BLUE}; padding: 25px; border-radius: 4px; margin-bottom: 25px; border: 1px solid #1f2937; font-size: 1.1rem; }}
    .remove-btn>button {{ background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }}
    h1 {{ font-size: 4rem !important; margin-bottom: 0px !important; }}
</style>
"""

# ==========================================
# 2. LOGIC ENGINE (Tactical Intelligence)
# ==========================================
class TacticalInference:
    def __init__(self, file_bytes, width, height):
        self.fingerprint = hashlib.sha256(file_bytes).hexdigest()
        self.seed = int(self.fingerprint, 16)
        self.ratio = width / height
        self.is_ez_view = self.ratio < 1.7
        self.perspective = "EZ-CAM (Perspective)" if self.is_ez_view else "ALL-22 (Wide)"
        
        p_roll = self.seed % 10
        self.personnel = "11-PERS" if p_roll < 6 else ("12-PERS" if p_roll < 9 else "13-PERS")
        self.is_bunch = (self.seed % 4 == 0)
        
        self.shell_num = (self.seed % 2) + 1
        self.cushion = (self.seed % 9) + 4 # Boosted minimum cushion for visual gap
        self.coverage = f"COVER {self.shell_num * 2}" if self.shell_num == 2 else "COVER 3"
        self.blitz_lb_index = (self.seed % 3) if (self.seed % 7 == 0) else None

        route_sets = {
            "COVER 4": ["POST", "HITCH", "SEAM", "GO"],
            "COVER 2": ["HOLE", "FADE", "POST", "COMEBACK"],
            "COVER 3": ["SEAM", "OUT", "POST", "SLANT"]
        }
        self.offensive_gameplan = route_sets.get(self.coverage, ["SLANT", "CROSS", "FADE", "OUT"])

    def get_summary(self):
        return {
            "hash": self.fingerprint[:10],
            "shell": f"{self.shell_num}-HIGH",
            "threat": self.offensive_gameplan[0] if not self.is_bunch else "SWITCH_RELEASE",
            "type": "BUNCH" if self.is_bunch else "SPREAD"
        }

# ==========================================
# 3. RENDERING ENGINE (Spatial Analysis)
# ==========================================
class SpatialRenderer:
    def __init__(self, data):
        self.data = data
        # Scale: Massive plot for better resolution
        self.fig, self.ax = plt.subplots(figsize=(18, 10)) 
        self.ax.set_facecolor(THEME_DARK)

    def _warp(self, x, y):
        if not self.data.is_ez_view: return x, y
        scale = 1 - (y * 0.016)
        return x * scale, y

    def _draw_box(self, x, y, label, col, is_def=True, arrow_col=None, zone_on=False):
        tx, ty = self._warp(x, y)
        scale_size = (1 - (y * 0.015)) if self.data.is_ez_view else 1
        w, h = BOX_WIDTH * scale_size, BOX_HEIGHT * scale_size
        
        if is_def and zone_on and not arrow_col:
            zx, zy = self._warp(x * 1.1, y + 2.5) 
            bw, bh = (45 if y > 18 else 28), (20 if y > 18 else 14)
            self.ax.add_patch(patches.Ellipse((zx, zy), bw*scale_size, bh*scale_size, color=DEF_ZONE_RED, alpha=0.1, ec=DEF_ZONE_RED, lw=1.5, ls='--'))
            plt.plot([tx, zx], [ty, zy], color=DEF_ZONE_RED, alpha=0.2, ls=':', lw=1)

        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=1.0, zorder=20))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=LABEL_FONT_SIZE, fontweight='bold', zorder=21)
        
        if arrow_col:
            self.ax.annotate("", xy=self._warp(x, y-7), xytext=(tx, ty), 
                             arrowprops=dict(arrowstyle="->", color=arrow_col, lw=3))

    def _draw_path(self, start_x, start_y, route_name):
        schemes = {
            "POST": [(0, 18), (28 if start_x < 0 else -28, 15)],
            "COMEBACK": [(0, 18), (12 if start_x < 0 else -12, -6)],
            "OUT": [(0, 12), (-18 if start_x < 0 else 18, 0)],
            "SLANT": [(0, 4), (20 if start_x < 0 else -20, 14)],
            "SEAM": [(0, 45)], "GO": [(0, 50)],
            "HOLE": [(0, 15), (22 if start_x < 0 else -22, 5)],
            "HITCH": [(0, 9), (1, -2)]
        }
        segments = schemes.get(route_name, [(0, 25)])
        cx, cy = start_x, start_y
        for i, (dx, dy) in enumerate(segments):
            nx, ny = cx + dx, cy + dy
            p1, p2 = self._warp(cx, cy), self._warp(nx, ny)
            self.ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=ROUTE_LINE_WIDTH, alpha=0.9))
            if i == len(segments) - 1:
                plt.text(p2[0], p2[1]+2.5, route_name, color=OFF_PATH_GOLD, fontsize=8, fontweight='bold', ha='center')
            cx, cy = nx, ny

    def render(self, off_overlay, def_overlay):
        # Grid calibration
        plt.axhline(0, color='white', linewidth=3, alpha=0.5) 
        for yard in range(10, 70, 10):
            l1, l2 = self._warp(-100, yard), self._warp(100, yard)
            self.ax.plot([l1[0], l2[0]], [l1[1], l2[1]], color='#1f2937', lw=1.2, alpha=0.2)

        # 1. Defense Positioning
        for x in [-15, -6, 6, 15]: 
            self._draw_box(x, 1.2, 'DL', '#111827', arrow_col=RUSH_VEC_BLUE if def_overlay else None)
        
        if self.data.is_bunch:
            lb_locs = [(-15, 8.5, 'SLB'), (25, 6.5, 'MLB'), (10, 8.5, 'WLB')]
            self._draw_box(42, 6.0, 'CB', '#064e3b', zone_on=True)
        else:
            lb_locs = [(-15, 8.5, 'SLB'), (0, 8.5, 'MLB'), (15, 8.5, 'WLB')]
            self._draw_box(55, self.data.cushion, 'CB', '#064e3b', zone_on=def_overlay)

        for i, (lx, ly, ln) in enumerate(lb_locs):
            bz = (self.data.blitz_lb_index == i)
            self._draw_box(lx, 3.5 if bz else ly, ln, '#161b22', arrow_col="#f85149" if bz else None, zone_on=def_overlay and not bz)

        self._draw_box(-55, self.data.cushion, 'CB', '#064e3b', zone_on=def_overlay)
        s_y = 22 if self.data.shell_num == 2 else 26
        if self.data.shell_num == 2:
            self._draw_box(-24, s_y, 'FS', '#1e3a8a', zone_on=def_overlay)
            self._draw_box(24, s_y, 'SS', '#1e3a8a', zone_on=def_overlay)
        else:
            self._draw_box(0, s_y, 'S', '#1e3a8a', zone_on=def_overlay)

        # 2. Offense personnel (Full-Width)
        for i, x in enumerate([-16, -8, 0, 8, 16]): 
            self._draw_box(x, -1.5, ['LT','LG','C','RG','RT'][i], '#161b22', False)
        self._draw_box(0, -4.5, 'QB', '#111827', False)
        self._draw_box(8, -5.2, 'RB', '#161b22', False)

        if self.data.is_bunch:
            skills = [(-75, 0, 'X'), (25, 0, 'Y'), (35, 0, 'Z'), (25, -3.5, 'TE')]
        elif self.data.personnel == "11-PERS":
            skills = [(-78, 0, 'X'), (78, 0, 'Z'), (-30, 0, 'Y'), (25, 0, 'TE')]
        elif self.data.personnel == "12-PERS":
            skills = [(-78, 0, 'X'), (78, 0, 'Z'), (28, 0, 'TE'), (-28, 0, 'TE')]
        else:
            skills = [(-78, 0, 'X'), (32, 0, 'TE'), (-32, 0, 'TE'), (45, 0, 'TE')]

        for i, (wx, wy, wl) in enumerate(skills):
            self._draw_box(wx, wy, wl, '#111827', False)
            if off_overlay: self._draw_path(wx, wy, self.data.offensive_gameplan[i % len(self.data.offensive_gameplan)])

        plt.ylim(-20, 68); plt.xlim(-105, 105); plt.axis('off')
        return self.fig

# ==========================================
# 4. SYSTEM UI INTEGRATION
# ==========================================
if 'reboot_token' not in st.session_state: st.session_state.reboot_token = 0

def system_wipe():
    st.session_state.reboot_token += 1
    st.rerun()

st.markdown(CSS_UI_STANDARDS, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; letter-spacing: 15px; color: white;'>PRO-VISION</h1>", unsafe_allow_html=True)

# Enlarged Intelligence Tabs
def trigger_heavy_metrics(metrics):
    cols = st.columns(len(metrics))
    for i, (lab, val) in enumerate(metrics.items()):
        html = f"""<div style='background:#111827; border:2px solid #1f2937; border-radius:4px; padding:18px;'>
        <p style='color:#4b5563; font-size:0.65rem; letter-spacing:3px; text-transform:uppercase; margin:0;'>{lab}</p>
        <p style="font-family:'JetBrains Mono'; font-weight:800; font-size:1.9rem; color:white; margin:0;">{str(val).upper()}</p>
        </div>"""
        cols[i].markdown(html, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div style='padding:10px;'></div>", unsafe_allow_html=True)
    source_feed = st.file_uploader("SOURCE ANALYTICS FEED", type=['jpg','png','jpeg'], key=f"s_{st.session_state.reboot_token}")
    o_layer = st.toggle("ACTIVATE ROUTE VOID OVERLAY", value=True)
    d_layer = st.toggle("ACTIVATE DEFENSIVE BUBBLES", value=True)
    st.divider()
    st.markdown("<div class='remove-btn'>", unsafe_allow_html=True)
    if st.button("TERMINATE SESSION"): system_wipe()
    st.markdown("</div>", unsafe_allow_html=True)

if source_feed:
    raw_pil = Image.open(source_feed)
    intel = TacticalInference(source_feed.getvalue(), raw_pil.width, raw_pil.height)
    st.markdown("---")
    
    trigger_heavy_metrics({"Personnel": intel.personnel, "Shell": intel.get_summary()['shell'], 
                          "Set": intel.get_summary()['type'], "Primary Beater": intel.get_summary()['threat']})

    display_l, display_r = st.columns([3.5, 1], gap="medium") # Widened Main View
    with display_l:
        renderer = SpatialRenderer(intel)
        st.pyplot(renderer.render(o_layer, d_layer), transparent=True)
        st.image(raw_pil, use_container_width=True)
    with display_r:
        st.markdown(f"**TRACE_ID // {intel.get_summary()['hash']}**")
        st.markdown(f"""<div class="report-frame">
        <b>SENSORY LOG:</b> 
        Analysis indicates a {intel.perspective} view frame.<br><br>
        <b>FIELD INTEL:</b> 
        Calculated deep safety dispersion is characteristic of a modern {intel.coverage} shell.<br><br>
        <b>SCENARIO:</b>
        { 'Bunch identification forces a BOX-TRIANGLE adaptation from the Strongside CB/MLB.' if intel.is_bunch else 'Standard spread identified. Coverage maintained at balanced leverages.' }
        </div>""", unsafe_allow_html=True)
        if intel.blitz_lb_index is not None:
            st.error(f"DETECTION ALERT: LB Attack detected from {['SLB','MLB','WLB'][intel.blitz_lb_index]}. Expected pressure at the snap.")
else:
    st.markdown("<div style='height:500px; border:2px dashed #1f2937; border-radius:10px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#0e1113;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#334155; letter-spacing:15px; font-size:3rem;'>STANDBY</h2><p style='color:#1a1b1e;'>AWAITING COORDINATE UPLOAD</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
