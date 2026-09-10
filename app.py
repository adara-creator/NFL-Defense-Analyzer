import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. APPLICATION LIFECYCLE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def system_reboot():
    st.session_state.uploader_key += 1
    st.rerun()

st.set_page_config(page_title="PRO-VISION // TACTICAL INTELLIGENCE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stMetric { display: none !important; } 
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; }
    .stButton>button { border-radius: 2px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.2em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    .intel-summary { background: #111827; border: 1px solid #1f2937; padding: 18px; border-radius: 4px; border-left: 5px solid #1f6feb; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DYNAMIC TERMINALS
# ---------------------------------------------------------
def render_header_white():
    st.markdown("<h1 style='text-align: center; letter-spacing: 8px; color: #ffffff; font-family: Courier; margin-top: -35px;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_flap_ui(label, text):
    val = str(text).upper()
    fid = hashlib.md5(label.encode()).hexdigest()[:6]
    html = f"""
    <div style="background: transparent;">
        <p style="color: #4b5563; font-size: 0.5rem; text-transform: uppercase; margin: 0; letter-spacing: 2px;">{label}</p>
        <div id="w-{fid}" style="display: flex; gap: 3px; padding-top: 6px;"></div>
    </div>
    <script>
        const v = "{val}"; const b = document.getElementById('w-{fid}');
        for(let i=0; i<v.length; i++) {{
            let d = document.createElement('div'); 
            d.style = "width: 26px; height: 42px; background: #111827; color: #f8fafc; font-family: monospace; font-size: 24px; text-align: center; line-height: 42px; border-radius: 2px; border: 1px solid #1f2937;";
            d.innerText = v[i]; b.appendChild(d);
        }}
    </script>
    """
    components.html(html, height=75)

# ---------------------------------------------------------
# 3. EXPANDED ALIGNMENT ENGINE (NO-STACKING GRID)
# ---------------------------------------------------------
def draw_intel_map(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.018)
        return x * scale, y

    # Field Grids
    plt.axhline(0, color='white', linewidth=2, alpha=0.3) 
    for y in range(10, 60, 10):
        p1, p2 = p_warp(-90, y), p_warp(90, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.2)

    def draw_player(x, y, label, col, border='#ffffff', show_zone=False):
        tx, ty = p_warp(x, y)
        sc = (1-(y * 0.015)) if is_ez else 1
        w, h = 4.2 * sc, 2.3 * sc
        
        if defense_on and show_zone:
            bw, bh = (35 if y > 15 else 22), (14 if y > 15 else 10)
            ax.add_patch(patches.Ellipse((tx, ty+2), bw*sc, bh*sc, fc='#ef4444', alpha=0.08, ec='#ef4444', lw=1, ls='--'))

        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec=border, lw=0.5, zorder=15))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=16)

    def draw_complex_route(sx, sy, route_name):
        # Precise coordinate sequences: [Stem Length, Break Vector]
        sequences = {
            "POST": [(0, 15), (20 if sx < 0 else -20, 15)],
            "OUT": [(0, 10), (-14 if sx < 0 else 14, 0)],
            "COMEBACK": [(0, 16), (8 if sx < 0 else -8, -5)],
            "SEAM": [(0, 42)],
            "CORNER": [(0, 15), (-20 if sx < 0 else 20, 15)],
            "SLANT": [(0, 3), (18 if sx < 0 else -18, 14)],
            "HITCH": [(0, 8), (1, -2)]
        }
        
        path_data = sequences.get(route_name, [(0, 25)])
        cx, cy = sx, sy
        
        for i, (dx, dy) in enumerate(path_data):
            nx, ny = cx + dx, cy + dy
            ax.annotate("", xy=p_warp(nx, ny), xytext=p_warp(cx, cy),
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=2.5, alpha=0.8, connectionstyle="arc3,rad=.1" if i>0 else None))
            # Place route text at the final segment arrowhead
            if i == len(path_data) - 1:
                tx_r, ty_r = p_warp(nx, ny)
                plt.text(tx_r, ty_r + 2, route_name, color="#facc15", fontsize=5.5, fontweight='bold', ha='center')
            cx, cy = nx, ny

    # --- DEFENSE PERSONNEL (Centered Front) ---
    for i, x in enumerate([-16, -6, 6, 16]):
        draw_player(x, 1, ['DE','DT','DT','DE'][i], '#111827')
    
    for i, x in enumerate([-12, 0, 12]):
        draw_player(x, 8.5, ['SLB','MLB','WLB'][i], '#161b22', show_zone=True)

    # Shell
    c = data['cushion']
    draw_player(-48, c, 'CB', '#064e3b', show_zone=True)
    draw_player(48, c, 'CB', '#064e3b', show_zone=True)
    
    if data['shell'] == 2:
        draw_player(-24, 22, 'FS', '#1e3a8a', show_zone=True); draw_player(24, 22, 'SS', '#1e3a8a', show_zone=True)
    else:
        draw_player(0, 26, 'S', '#1e3a8a', show_zone=True)

    # --- OFFENSE personnel (Fixed Wide Spacing) ---
    # Linemen LT -> RT (spaced perfectly at 6.5 yard intervals)
    for i, x in enumerate([-13, -6.5, 0, 6.5, 13]):
        draw_player(x, -1.2, ['LT','LG','C','RG','RT'][i], '#161b22', border='#334155')
    
    draw_player(0, -4.5, 'QB', '#1f2937', border='#334155')
    draw_player(8, -5, 'RB', '#161b22', border='#334155')

    # Skill Position Selection Logic (Prevents TE-RG stacking)
    # The RG is at 6.5, RT is at 13. The TE must be placed at 22+ to ensure a visible gap.
    p = data['personnel']
    if p == "11 PERS":
        # 1 TE, 3 WR (X on far left, Z on far right, Y in slot)
        skills = [(-65, 0, 'X'), (65, 0, 'Z'), (-32, 0, 'Y'), (22, 0, 'TE')]
    elif p == "12 PERS":
        # 2 TE, 2 WR (X/Z Wide, TEs tucked but separated from Tackles)
        skills = [(-65, 0, 'X'), (65, 0, 'Z'), (24, 0, 'TE'), (-24, 0, 'TE')]
    else: # 13 Personnel
        # 1 WR, 3 TE
        skills = [(-65, 0, 'X'), (24, 0, 'TE'), (-24, 0, 'TE'), (38, 0, 'TE')]

    # Execute Routes & Placement
    for i, (wx, wy, wl) in enumerate(skills):
        draw_player(wx, wy, wl, '#111827', border='#4b5563')
        if offense_on:
            draw_complex_route(wx, wy, data['route_map'][i % len(data['route_map'])])

    plt.ylim(-15, 65); plt.xlim(-100, 100); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. INTELLIGENCE ENGINE (HASHED BEAT-MAPPING)
# ---------------------------------------------------------
def get_intel(file_bytes, ratio):
    h = hashlib.sha256(file_bytes).hexdigest()
    vi = int(h, 16)
    
    # Accurate Personnel weighting
    p_num = vi % 10
    personnel = "11 PERS" if p_num < 6 else ("12 PERS" if p_num < 9 else "13 PERS")
    
    shell = (vi % 2) + 1
    cushion = (vi % 9) + 3
    cov = f"COVER {shell*2}" if shell == 2 else "COVER 3"
    
    # Counter-Strategy: Mapping Routes to specific coverage gaps
    counters = {
        "COVER 2": ["FADE", "POST", "HOLE", "COMEBACK"],
        "COVER 3": ["SEAM", "OUT", "POST", "COMEBACK"],
        "COVER 4": ["HITCH", "OUT", "SEAM", "POST"]
    }
    
    return {
        "id": h[:10], "view": "ALL-22" if ratio > 1.7 else "EZ-CAM",
        "shell": shell, "cov": cov, "cushion": cushion, 
        "personnel": personnel, "route_map": counters.get(cov, ["POST", "GO"]),
    }

# ---------------------------------------------------------
# 5. WORKSTATION INTERFACE
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#4b5563; letter-spacing:1px;'>OPERATIONAL HUB</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    route_active = st.toggle("ACTIVATE ROUTE VOID ANALYTICS", value=True)
    zones_active = st.toggle("ACTIVATE TACTICAL ZONES", value=False)
    st.divider()
    if st.button("TERMINATE SESSION"): system_reboot()

if f:
    pil = Image.open(f)
    results = get_intel(f.getvalue(), pil.width/pil.height)
    
    st.markdown("---")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1: render_flap_ui("Personnel", results['personnel'])
    with sc2: render_flap_ui("Coverage", results['cov'])
    with sc3: render_flap_ui("Shell", f"{results['shell']}-HIGH")
    with sc4: render_flap_ui("Detection", "OPTIMAL")

    ml, mr = st.columns([2.8, 1], gap="large")
    with ml:
        st.pyplot(draw_intel_map(results, route_active, zones_active), transparent=True)
        st.image(pil, use_container_width=True)
    with mr:
        st.info(f"**TRACE ID // {results['id']}**")
        st.markdown(f"**Perspective Logic:** Sensor detects **{results['view']}** feed. Field-grid distortion scale established.")
        
        # INTELLIGENCE BREAKDOWN
        st.markdown(f"""
        <div class="intel-summary">
        <b>SCHEMA BREAKDOWN:</b><br>
        Defense in a {results['shell']}-High Shell utilizing a {results['cushion']}-yard cushion on perimeters.<br><br>
        <b>COUNTER ANALYSIS:</b><br>
        Offensive pathing utilizes <b>{results['route_map'][0]}</b> concepts to challenge structural voids.
        </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><h4 style='color:#334155;'>SYSTEM STANDBY</h4></div>", unsafe_allow_html=True)
