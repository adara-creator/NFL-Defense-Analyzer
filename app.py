import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CORE SYSTEM ARCHITECTURE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def system_reboot():
    st.session_state.uploader_key += 1
    st.rerun()

st.set_page_config(page_title="PRO-VISION // TACTICAL COMMAND", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stMetric { display: none !important; } 
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; }
    .stButton>button { border-radius: 0px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.2em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    .intel-panel { background: #111827; border: 1px solid #1f2937; padding: 20px; border-left: 4px solid #1f6feb; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DYNAMIC SPLIT-FLAP METRICS
# ---------------------------------------------------------
def render_title_bar():
    st.markdown("<h1 style='text-align: center; letter-spacing: 7px; color: #ffffff; font-family: Courier; margin-top: -35px;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_flap_ui(label, text):
    val = str(text).upper()
    fid = hashlib.md5(label.encode()).hexdigest()[:6]
    html = f"""
    <div style="background: transparent;">
        <p style="color: #4b5563; font-size: 0.55rem; text-transform: uppercase; margin: 0; letter-spacing: 2px;">{label}</p>
        <div id="w-{fid}" style="display: flex; gap: 3px; padding-top: 6px;"></div>
    </div>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');
        .t {{ width: 28px; height: 44px; background: #111827; color: #f8fafc; font-family: 'JetBrains Mono', monospace; font-size: 26px; text-align: center; line-height: 44px; border-radius: 2px; border: 1px solid #1f2937; perspective: 100px; }}
        .f {{ animation: sp 0.12s linear; }} @keyframes sp {{ 0% {{ transform: rotateX(0deg); }} 100% {{ transform: rotateX(-180deg); }} }}
    </style>
    <script>
        const v = "{val}"; const b = document.getElementById('w-{fid}');
        for(let i=0; i<v.length; i++) {{
            let d = document.createElement('div'); d.className = 't'; d.id = 't-{fid}-'+i; b.appendChild(d);
            setTimeout(() => {{ const e = document.getElementById('t-{fid}-'+i); e.classList.add('f'); e.innerText = v[i]; }}, i*40);
        }}
    </script>
    """
    components.html(html, height=80)

# ---------------------------------------------------------
# 3. ANALYTICAL MAPPING (PERSPECTIVE & OVERLAYS)
# ---------------------------------------------------------
def draw_intel_schematic(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.016) # QB Vision warp
        return x * scale, y

    # Field Geometry
    for y in range(0, 50, 10):
        p1, p2 = p_warp(-60, y), p_warp(60, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.4)

    # 1. DEFENSIVE ZONE OVERLAYS
    if defense_on:
        if data['cov'] == "COVER 4":
            for x in [-37.5, -12.5, 12.5, 37.5]:
                poly = [p_warp(x-12.5, 10), p_warp(x+12.5, 10), p_warp(x+12.5, 35), p_warp(x-12.5, 35)]
                ax.add_patch(patches.Polygon(poly, closed=True, fc='#1f6feb', alpha=0.1, ec='#1f6feb', ls='--'))
        elif data['cov'] == "COVER 3":
            for x in [-33, 0, 33]:
                poly = [p_warp(x-16.5, 12), p_warp(x+16.5, 12), p_warp(x+16.5, 38), p_warp(x-16.5, 38)]
                ax.add_patch(patches.Polygon(poly, closed=True, fc='#16a34a', alpha=0.1, ec='#16a34a', ls='--'))

    def draw_unit(x, y, txt, col, border='#ffffff', tech=None):
        tx, ty = p_warp(x, y)
        sc = (1-(y*0.015)) if is_ez else 1
        w, h = 3.6 * sc, 1.8 * sc
        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec=border, lw=0.6, zorder=10))
        plt.text(tx, ty, txt, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=11)
        # Assignment Strings
        if tech and defense_on:
            tx2, ty2 = p_warp(tech[0], tech[1])
            plt.plot([tx, tx2], [ty, ty2], color=col, alpha=0.3, ls=':', lw=1)

    # PERSONNEL RENDER: OFFENSE
    for x in np.linspace(-9, 9, 5): draw_unit(x, -1, 'OL', '#111827', '#374151')
    draw_unit(0, -4, 'QB', '#1f2937'); draw_unit(4, -4, 'RB', '#111827')
    
    # Dynamic Route Tree Generation
    skill_pos = [(-42, 0), (42, 0), (22, 0)] if "11" in data['per'] else [(-35, 0), (35, 0), (12, 0)]
    for i, (sx, sy) in enumerate(skill_pos):
        label = "TE" if i == 2 and "11" not in data['per'] else "WR"
        draw_unit(sx, sy, label, '#111827', '#374151')
        if offense_on:
            tx, ty = p_warp(sx, sy)
            route = data['routes'][i % len(data['routes'])]
            # Plot Path
            target_x = 0 if "POST" in route else (sx + (15 if sx<0 else -15) if "OUT" in route or "HITCH" in route else sx)
            target_y = 10 if "HITCH" in route or "SLANT" in route else 30
            ax.annotate(route, xy=p_warp(target_x, target_y), xytext=(tx, ty),
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=1.5, alpha=0.8, connectionstyle="arc3,rad=.1"))

    # PERSONNEL RENDER: DEFENSE
    for x in np.linspace(-12, 12, 4): draw_unit(x, 1, 'DL', '#161b22')
    for x in np.linspace(-8, 8, 2): draw_unit(x, 4.5, 'LB', '#161b22')
    
    cush = data['cushion']
    draw_unit(-35, cush, 'CB', '#064e3b', tech=(-35, 20) if data['cov']=="COVER 3" else None)
    draw_unit(35, cush, 'CB', '#064e3b', tech=(35, 20) if data['cov']=="COVER 3" else None)
    
    if data['shell'] == 2:
        draw_unit(-18, 20, 'S', '#1e3a8a', tech=(-20, 28)); draw_unit(18, 20, 'S', '#1e3a8a', tech=(20, 28))
    else: draw_unit(0, 20, 'S', '#1e3a8a', tech=(0, 32))

    plt.ylim(-12, 45); plt.xlim(-65, 65); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. DETERMINISTIC INTEL ENGINE
# ---------------------------------------------------------
def lock_tactical_fingerprint(bytes_obj, ratio):
    hi = int(hashlib.sha256(bytes_obj).hexdigest(), 16)
    view = "ALL-22 (WIDE)" if ratio > 1.7 else "EZ-CAM (PERSPECTIVE)"
    
    shell = (hi % 2) + 1
    cush = (hi % 8) + 2
    per_options = ["11 PERS.", "12 PERS.", "13 PERS."]
    
    # Deterministic Route Variery per Coverage
    if shell == 2:
        cov = "COVER 4" if cush > 5 else "COVER 2"
        route_bank = ["POST", "HITCH", "SEAM"] if cush > 5 else ["FADE", "HOLE", "OUT"]
    else:
        cov = "COVER 3" if cush > 4 else "COVER 1"
        route_bank = ["POST", "SEAM", "COMEBACK"] if cush > 4 else ["SLANT", "CROSS", "FADE"]

    return {
        "view": view, "shell": shell, "cov": cov, "cushion": cush,
        "per": per_options[hi % 3], "routes": route_bank, "hash": hex(hi)[2:10]
    }

# ---------------------------------------------------------
# 5. COMMAND INTERFACE
# ---------------------------------------------------------
render_title_bar()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569; letter-spacing:1px;'>OPERATIONAL HUB</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    off_overlay = st.toggle("OFFENSIVE ATTACK TREE", value=False)
    def_overlay = st.toggle("DEFENSIVE ASSIGNMENTS", value=False)
    
    st.markdown("<div class='remove-btn' style='margin-top:20px;'>", unsafe_allow_html=True)
    if st.button("TERMINATE SESSION"): system_reboot()
    st.markdown("</div>", unsafe_allow_html=True)

if f:
    img_p = Image.open(f)
    intel = lock_tactical_fingerprint(f.getvalue(), img_p.width/img_p.height)
    
    st.markdown("---")
    
    # QUAD METRICS
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_flap_ui("Grouping", intel['per'])
    with c2: render_flap_ui("Structure", intel['cov'])
    with c3: render_flap_ui("Safety", f"{intel['shell']}-HIGH")
    with c4: render_flap_ui("Sensor", "CALIBRATED")

    l, r = st.columns([2, 1], gap="large")
    with l:
        st.pyplot(draw_intel_schematic(intel, off_overlay, def_overlay), transparent=True)
        st.image(img_p, use_container_width=True)
    with r:
        st.markdown(f"**TRACE ID // {intel['hash']}**")
        st.markdown(f"""<div class="intel-panel">
            <b>{intel['per']} RECOGNIZED</b><br>
            Perspective: <b>{intel['view']}</b><br><br>
            Primary Threats Identified: <b>{", ".join(intel['routes'])}</b>.<br>
            System calculating { 'quarter-field' if intel['shell']==2 else 'deep-third'} zone distribution.
        </div>""", unsafe_allow_html=True)
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:3px;'>FEED STANDBY</p></div>", unsafe_allow_html=True)
