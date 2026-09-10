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

st.set_page_config(page_title="PRO-VISION // COMMAND STATION", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stMetric { display: none !important; } 
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; }
    .stButton>button { border-radius: 2px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.5em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PRO-UI TERMINALS (DETERMINISTIC FLAPS)
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
# 3. POSITION-SPECIFIC ALIGNMENT CHART
# ---------------------------------------------------------
def draw_pro_schematic(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(15, 8.5))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.018) 
        return x * scale, y

    plt.axhline(0, color='white', linewidth=2, alpha=0.5) 
    for y in range(10, 60, 10):
        p1, p2 = p_warp(-75, y), p_warp(75, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.2)

    def draw_box(x, y, label, col, is_def=True, tech_xy=None):
        tx, ty = p_warp(x, y)
        sc = (1-(y * 0.015)) if is_ez else 1
        w, h = 4.2 * sc, 2.4 * sc # Enlarged for visibility
        
        if is_def and defense_on and tech_xy:
            zx, zy = p_warp(tech_xy[0], tech_xy[1])
            bw, bh = (38 if y > 15 else 22), (15 if y > 15 else 11)
            ax.add_patch(patches.Ellipse((zx, zy), bw*sc, bh*sc, color='#ef4444', alpha=0.12, ec='#ef4444', lw=1, ls='--'))
            plt.plot([tx, zx], [ty, zy], color='#ef4444', alpha=0.2, ls=':', lw=0.8)

        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=0.6, zorder=10))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=7, fontweight='bold', zorder=11)

    def draw_path(sx, sy, route_name):
        paths = {
            "POST": [(0, 12), (20 if sx < 0 else -20, 15)],
            "OUT": [(0, 10), (-12 if sx < 0 else 12, 0)],
            "SLANT": [(0, 3), (15 if sx < 0 else -15, 12)],
            "COMEBACK": [(0, 15), (6 if sx < 0 else -6, -4)],
            "HITCH": [(0, 7), (2 if sx < 0 else -2, -2)],
            "GO": [(0, 35)]
        }
        segments = paths.get(route_name, [(0, 25)])
        cx, cy = sx, sy
        for dx, dy in segments:
            nx, ny = cx + dx, cy + dy
            p1, p2 = p_warp(cx, cy), p_warp(nx, ny)
            ax.annotate("", xy=p2, xytext=p1, arrowprops=dict(arrowstyle="->", color="#facc15", lw=2.5, alpha=0.9))
            plt.text(p2[0], p2[1]+1, route_name, color="#facc15", fontsize=6, fontweight='bold')
            cx, cy = nx, ny

    # 1. DEFENSE
    for i, x in enumerate([-12, -4, 4, 12]): draw_box(x, 1.2, ['DE','DT','DT','DE'][i], '#111827')
    for i, x in enumerate([-12, 0, 12]): draw_box(x, 4.8, ['SLB','MLB','WLB'][i], '#161b22', tech_xy=(x*1.3, 8))
    
    c = data['cushion']
    draw_box(-45, c, 'CB', '#064e3b', tech_xy=(-50, 10))
    draw_box(45, c, 'CB', '#064e3b', tech_xy=(50, 10))
    if data['shell'] == 2:
        draw_box(-22, 20, 'FS', '#1e3a8a', tech_xy=(-25, 32)); draw_box(22, 20, 'SS', '#1e3a8a', tech_xy=(25, 32))
    else: draw_box(0, 22, 'S', '#1e3a8a', tech_xy=(0, 32))

    # 2. OFFENSE personnel SETS
    for i, x in enumerate([-12, -6, 0, 6, 12]): draw_box(x, -1.2, ['LT','LG','C','RG','RT'][i], '#161b22', is_def=False)
    draw_box(0, -3.8, 'QB', '#1f2937', is_def=False)
    draw_box(5, -4.2, 'RB', '#161b22', is_def=False)

    p_type = data['personnel']
    if p_type == "11 PERS.":
        # 3 WR (X, Y, Z) + 1 TE
        skills = [(-52, 0, 'X'), (52, 0, 'Z'), (-25, 0, 'Y'), (18, 0, 'TE')]
    elif p_type == "12 PERS.":
        # 2 WR (X, Z) + 2 TE
        skills = [(-52, 0, 'X'), (52, 0, 'Z'), (15, 0, 'TE'), (-15, 0, 'TE')]
    else: # 13 Personnel
        # 1 WR (X) + 3 TE
        skills = [(-52, 0, 'X'), (15, 0, 'TE'), (-12, 0, 'TE'), (24, 0, 'TE')]

    for i, (wx, wy, wl) in enumerate(skills):
        draw_box(wx, wy, wl, '#111827', is_def=False)
        if offense_on:
            draw_path(wx, wy, data['routes'][i % len(data['routes'])])

    plt.ylim(-18, 55); plt.xlim(-85, 85); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. DETERMINISTIC INTEL
# ---------------------------------------------------------
def fetch_tactical_data(file_bytes, ratio):
    h = hashlib.sha256(file_bytes).hexdigest()
    val = int(h, 16)
    v_type = "ALL-22" if ratio > 1.7 else "EZ-CAM"
    p_opt = ["11 PERS.", "12 PERS.", "13 PERS."]
    routes = ["POST", "OUT", "GO", "HITCH", "SLANT", "COMEBACK"]
    
    return {
        "shell": (val % 2) + 1, "cov": f"COVER {(val % 2 + 1)*2}", "cushion": (val % 8) + 2,
        "personnel": p_opt[val % 3], "view": v_type, 
        "routes": [routes[(val+i)%len(routes)] for i in range(4)], "hash": h[:8]
    }

# ---------------------------------------------------------
# 5. USER STATION
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569;'>OPERATIONAL CONTROL</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    o_on = st.toggle("ACTIVATE ROUTE OVERLAYS", value=True) # Defaulting to True as requested
    d_on = st.toggle("ACTIVATE DEFENSE ZONES", value=False)
    if st.button("RESET ENGINE"): system_reboot()

if f:
    pil_img = Image.open(f)
    stats = fetch_tactical_data(f.getvalue(), pil_img.width / pil_img.height)
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_flap_ui("Personnel", stats['personnel'])
    with c2: render_flap_ui("Predict", stats['cov'])
    with c3: render_flap_ui("Shell", f"{stats['shell']}-HIGH")
    with c4: render_flap_ui("Cam", stats['view'])

    main, r_pane = st.columns([2.8, 1], gap="large")
    with main:
        st.pyplot(draw_pro_schematic(stats, o_on, d_on), transparent=True)
        st.image(pil_img, use_container_width=True)
    with r_pane:
        st.info(f"**TRACE ID // {stats['hash']}**")
        st.markdown(f"**Deployment Analytics:** {stats['personnel']} identified. Analyzing skill position leverage.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:4px;'>FEED DISCONNECTED</p></div>", unsafe_allow_html=True)
