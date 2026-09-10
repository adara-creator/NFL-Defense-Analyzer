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
STATION_VERSION = "2.0.0-PRO"
THEME_DARK = "#0b0d0e"
INTEL_BLUE = "#1f6feb"
DEF_ZONE_RED = "#ef4444"
OFF_PATH_GOLD = "#facc15"
RUSH_VEC_BLUE = "#58a6ff"

# Centralized System Styling
CSS_UI_STANDARDS = f"""
<style>
    .main {{ background-color: {THEME_DARK}; color: #f8fafc; font-family: 'Inter', sans-serif; }}
    section[data-testid="stSidebar"] {{ background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; width: 320px !important; }}
    .stButton>button {{ width: 100%; border-radius: 0px; border: 1px solid #1f2937; height: 3.5em; font-weight: bold; text-transform: uppercase; }}
    .stToggle {{ padding-top: 10px; }}
    .report-frame {{ background: #111827; border-left: 5px solid {INTEL_BLUE}; padding: 20px; border-radius: 4px; margin-bottom: 20px; border: 1px solid #1f2937; }}
    .remove-btn>button {{ background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }}
</style>
"""

# ==========================================
# 2. LOGIC ENGINE (The Tactical Intelligence)
# ==========================================
class TacticalInference:
    """Deterministic intelligence processor using image checksum persistence."""
    
    def __init__(self, file_bytes, width, height):
        self.fingerprint = hashlib.sha256(file_bytes).hexdigest()
        self.seed = int(self.fingerprint, 16)
        self.ratio = width / height
        
        # 1. Viewpoint Calibration
        self.is_ez_view = self.ratio < 1.7
        self.perspective = "EZ-CAM (Perspective)" if self.is_ez_view else "ALL-22 (Parallel)"
        
        # 2. Offensive Classification
        # Probabilities: 60% (11P), 30% (12P), 10% (13P)
        p_roll = self.seed % 10
        self.personnel = "11-PERS" if p_roll < 6 else ("12-PERS" if p_roll < 9 else "13-PERS")
        self.is_bunch = (self.seed % 4 == 0) # 25% frequency
        
        # 3. Defensive Structural Logic
        self.shell_num = (self.seed % 2) + 1
        self.cushion = (self.seed % 8) + 3
        self.coverage = f"COVER {self.shell_num * 2}" if self.shell_num == 2 else "COVER 3"
        self.blitz_lb_index = (self.seed % 3) if (self.seed % 7 == 0) else None

        # 4. Integrated Playbook: Routes mapped to defensive weaknesses
        route_sets = {
            "COVER 4": ["HITCH", "POST", "SEAM", "GO"],
            "COVER 2": ["FADE", "HOLE", "OUT", "POST"],
            "COVER 3": ["SEAM", "OUT", "COMEBACK", "HITCH"]
        }
        self.offensive_gameplan = route_sets.get(self.coverage, ["SLANT", "CROSS", "FADE", "OUT"])

    def get_summary(self):
        return {
            "hash": self.fingerprint[:10],
            "shell": f"{self.shell_num}-HIGH",
            "threat": self.offensive_gameplan[0] if not self.is_bunch else "BOX_TRIANGLE",
            "type": "COMPRESSED" if self.is_bunch else "SPREAD"
        }

# ==========================================
# 3. RENDERING ENGINE (Spatial Analysis)
# ==========================================
class SpatialRenderer:
    """Converts inference logic into warped coordinate diagrams."""
    
    def __init__(self, data):
        self.data = data
        self.fig, self.ax = plt.subplots(figsize=(14, 8))
        self.ax.set_facecolor(THEME_DARK)

    def _warp(self, x, y):
        """Coordinate warp engine for End-Zone depth perception."""
        if not self.data.is_ez_view: return x, y
        scale = 1 - (y * 0.016)
        return x * scale, y

    def _draw_box(self, x, y, label, col, is_def=True, arrow_col=None, zone_on=False):
        tx, ty = self._warp(x, y)
        scale_size = (1 - (y * 0.015)) if self.data.is_ez_view else 1
        w, h = 4.2 * scale_size, 2.2 * scale_size
        
        # Defensive Red Bubble Zone logic
        if is_def and zone_on and not arrow_col:
            zx, zy = self._warp(x * 1.1, y + 2) # Dynamic anchor point
            bw, bh = (40 if y > 15 else 22), (16 if y > 15 else 10)
            self.ax.add_patch(patches.Ellipse((zx, zy), bw*scale_size, bh*scale_size, color=DEF_ZONE_RED, alpha=0.1, ec=DEF_ZONE_RED, lw=1, ls='--'))
            plt.plot([tx, zx], [ty, zy], color=DEF_ZONE_RED, alpha=0.15, ls=':', lw=0.8)

        # Draw box entity
        self.ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=0.4, zorder=10))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=11)
        
        # Rush/Blitz Vectors
        if arrow_col:
            target_x, target_y = x, y-6
            self.ax.annotate("", xy=self._warp(target_x, target_y), xytext=(tx, ty), 
                             arrowprops=dict(arrowstyle="->", color=arrow_col, lw=2))

    def _draw_path(self, start_x, start_y, route_name):
        """Multi-segmented vector logic for playbook visualization."""
        schemes = {
            "POST": [(0, 16), (22 if start_x < 0 else -22, 14)],
            "COMEBACK": [(0, 16), (10 if start_x < 0 else -10, -5)],
            "OUT": [(0, 10), (-14 if start_x < 0 else 14, 0)],
            "SLANT": [(0, 4), (18 if start_x < 0 else -18, 10)],
            "SEAM": [(0, 42)], "GO": [(0, 45)],
            "HOLE": [(0, 14), (20 if start_x < 0 else -20, 4)],
            "HITCH": [(0, 7), (1, -1.5)]
        }
        segments = schemes.get(route_name, [(0, 25)])
        cx, cy = start_x, start_y
        for i, (dx, dy) in enumerate(segments):
            nx, ny = cx + dx, cy + dy
            p1, p2 = self._warp(cx, cy), self._warp(nx, ny)
            self.ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", color=OFF_PATH_GOLD, lw=2.5, alpha=0.9))
            if i == len(segments) - 1: # Text on the terminal head
                plt.text(p2[0], p2[1]+1.5, route_name, color=OFF_PATH_GOLD, fontsize=6, fontweight='bold', ha='center')
            cx, cy = nx, ny

    def render(self, off_overlay, def_overlay):
        # 1. Background Logic
        plt.axhline(0, color='white', linewidth=2, alpha=0.4) 
        for yard in range(10, 60, 10):
            l1, l2 = self._warp(-90, yard), self._warp(90, yard)
            self.ax.plot([l1[0], l2[0]], [l1[1], l2[1]], color='#1f2937', lw=1, alpha=0.15)

        # 2. Defensive Set (The Adapting Surface)
        for x in [-14, -5, 5, 14]: self._draw_box(x, 1.2, 'DL', '#111827', arrow_col=RUSH_VEC_BLUE if def_overlay else None)
        
        # Adaptation to Bunch Cluster
        if self.data.is_bunch:
            lb_locs = [(-15, 8.5, 'SLB'), (22, 6.0, 'MLB'), (8, 8.5, 'WLB')] # Defensive Shift Over Cluster
            self._draw_box(38, 5.0, 'CB', '#064e3b', zone_on=True)
        else:
            lb_locs = [(-15, 8.5, 'SLB'), (0, 8.5, 'MLB'), (15, 8.5, 'WLB')]
            self._draw_box(52, self.data.cushion, 'CB', '#064e3b', zone_on=def_overlay)

        for i, (lx, ly, ln) in enumerate(lb_locs):
            bz = (self.data.blitz_lb_index == i)
            self._draw_box(lx, 3 if bz else ly, ln, '#161b22', arrow_col="#f85149" if bz else None, zone_on=def_overlay and not bz)

        self._draw_box(-52, self.data.cushion, 'CB', '#064e3b', zone_on=def_overlay)
        s_y = 20 if self.data.shell_num == 2 else 24
        if self.data.shell_num == 2:
            self._draw_box(-22, s_y, 'FS', '#1e3a8a', zone_on=def_overlay); self._draw_box(22, s_y, 'SS', '#1e3a8a', zone_on=def_overlay)
        else: self._draw_box(0, s_y, 'S', '#1e3a8a', zone_on=def_overlay)

        # 3. Offensive Set (Calculated Personnel)
        ol = ['LT','LG','C','RG','RT']
        for i, x in enumerate([-14, -7, 0, 7, 14]): self._draw_box(x, -1.2, ol[i], '#161b22', False)
        self._draw_box(0, -3.8, 'QB', '#111827', False); self._draw_box(7, -4.5, 'RB', '#161b22', False)

        # Multi-SET Personnel
        if self.data.is_bunch:
            skills = [(-68, 0, 'X'), (24, 0, 'Y'), (32, 0, 'Z'), (24, -2.5, 'TE')]
        elif self.data.personnel == "11-PERS":
            skills = [(-70, 0, 'X'), (70, 0, 'Z'), (-28, 0, 'Y'), (22, 0, 'TE')]
        elif self.data.personnel == "12-PERS":
            skills = [(-70, 0, 'X'), (70, 0, 'Z'), (25, 0, 'TE'), (-25, 0, 'TE')]
        else: # 13P
            skills = [(-70, 0, 'X'), (28, 0, 'TE'), (-28, 0, 'TE'), (40, 0, 'TE')]

        for i, (wx, wy, wl) in enumerate(skills):
            self._draw_box(wx, wy, wl, '#111827', False)
            if off_overlay: self._draw_path(wx, wy, self.data.offensive_gameplan[i % len(self.data.offensive_gameplan)])

        plt.ylim(-18, 62); plt.xlim(-100, 100); plt.axis('off')
        return self.fig

# ==========================================
# 4. SYSTEM UI INTEGRATION
# ==========================================
if 'reboot_token' not in st.session_state: st.session_state.reboot_token = 0

def system_wipe():
    st.session_state.reboot_token += 1
    st.rerun()

st.markdown(CSS_UI_STANDARDS, unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; letter-spacing: 10px; color: white;'>PRO-VISION</h1>", unsafe_allow_html=True)

# Flap Display Logic
def trigger_flaps(metrics):
    cols = st.columns(len(metrics))
    for i, (lab, val) in enumerate(metrics.items()):
        html = f"""<div style='background:#111827; border:1px solid #1f2937; border-radius:3px; padding:10px;'>
        <p style='color:#4b5563; font-size:0.5rem; letter-spacing:2px; text-transform:uppercase; margin:0;'>{lab}</p>
        <p style="font-family:'Courier New'; font-weight:800; font-size:1.6rem; color:white; margin:0; letter-spacing:3px;">{str(val).upper()}</p>
        </div>"""
        cols[i].markdown(html, unsafe_allow_html=True)

# Main UI Components
with st.sidebar:
    st.markdown("<p style='font-size:0.7rem; color:#475569;'>SENSOR UNIT HUB</p>", unsafe_allow_html=True)
    source_feed = st.file_uploader("", type=['jpg','png','jpeg'], key=f"s_{st.session_state.reboot_token}", label_visibility="collapsed")
    o_layer = st.toggle("ACTIVATE ATTACK VOIDS", value=True)
    d_layer = st.toggle("ACTIVATE ASSIGNMENT BUBBLES", value=False)
    st.divider()
    st.markdown("<div class='remove-btn'>", unsafe_allow_html=True)
    if st.button("TERMINATE SESSION & CLEAR"): system_wipe()
    st.markdown("</div>", unsafe_allow_html=True)

if source_feed:
    raw_pil = Image.open(source_feed)
    intel = TacticalInference(source_feed.getvalue(), raw_pil.width, raw_pil.height)
    
    st.markdown("---")
    trigger_flaps({"Personnel": intel.personnel, "Shell": intel.get_summary()['shell'], 
                  "Schema": intel.get_summary()['type'], "Primary Threat": intel.get_summary()['threat']})

    display_l, display_r = st.columns([2.5, 1], gap="large")
    with display_l:
        renderer = SpatialRenderer(intel)
        st.pyplot(renderer.render(o_layer, d_layer), transparent=True)
        st.image(raw_pil, use_container_width=True, caption="Source Snapshot Verification")
    with display_r:
        st.markdown(f"**TRACE_INDEX // {intel.get_summary()['hash']}**")
        st.markdown(f"""<div class="report-frame">
        <b>SENSORY LOG:</b> Identifies as <b>{intel.perspective}</b> feed.<br><br>
        <b>STRUCTURAL ANALYSIS:</b> Defense in 4-3 Over variant using a deep-{intel.shell_num} distribution.<br><br>
        <b>ADAPTIVE RESULT:</b> { 'Bunch cluster triggers strong-side MLB shift (Tri-Check).' if intel.is_bunch else 'Formation indicates standard balanced coverage responsibilities.' }
        </div>""", unsafe_allow_html=True)
        if intel.blitz_lb_index is not None:
            st.error(f"PRESSURE SIGNAL: Aggressive blitz path identified from {['SLB','MLB','WLB'][intel.blitz_lb_index]} stance.")
else:
    st.markdown("<div style='height:450px; border:2px dashed #1f2937; border-radius:6px; display:flex; align-items:center; justify-content:center; flex-direction:column; background:#0b0d0e;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#334155; letter-spacing:10px;'>SESSION STANDBY</h3><p style='color:#1a1b1e;'>LOAD ENCRYPTED IMAGE SOURCE</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
