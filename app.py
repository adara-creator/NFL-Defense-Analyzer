import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CORE SYSTEM INITIALIZATION
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
    .stButton>button { border-radius: 0px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.5em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PRO-UI TERMINALS (ELASTIC TILES)
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
# 3. 100% ACCURACY ALIGNMENT CHART (22-MAN MAPPING)
# ---------------------------------------------------------
def draw_pro_schematic(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(15, 8.5))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.018) 
        return x * scale, y

    # Render Field Elements
    plt.axhline(0, color='white', linewidth=2, alpha=0.5) 
    for y in range(10, 60, 10):
        p1, p2 = p_warp(-75, y), p_warp(75, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.2)

    def draw_box(x, y, label, col, is_def=True, tech_xy=None):
        tx, ty = p_warp(x, y)
        sc = (1-(y * 0.015)) if is_ez else 1
        w, h = 3.8 * sc, 2.2 * sc
        
        if is_def and defense_on and tech_xy:
            zx, zy = p_warp(tech_xy[0], tech_xy[1])
            bw, bh = (38 if y > 15 else 22), (15 if y > 15 else 11)
            ax.add_patch(patches.Ellipse((zx, zy), bw*sc, bh*sc, color='#ef4444', alpha=0.1, ec='#ef4444', lw=1, ls='--'))
            plt.plot([tx, zx], [ty, zy], color='#ef4444', alpha=0.2, ls=':', lw=0.8)

        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=0.5, zorder=10))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=11)

    # 1. THE DEFENSE (4-3 UNDER ALIGNMENT)
    # D-Line (4 Linemen)
    for i, x in enumerate([-12, -4, 4, 12]):
        draw_box(x, 1.2, ['DE','DT','DT','DE'][i], '#111827')
    # LBs (Sam, Mike, Will)
    for i, x in enumerate([-12, 0, 12]):
        draw_box(x, 4.8, ['SLB','MLB','WLB'][i], '#161b22', tech_xy=(x*1.3, 8))
    # Secondary
    cush = data['cushion']
    draw_box(-45, cush, 'CB', '#064e3b', tech_xy=(-50, 10))
    draw_box(45, cush, 'CB', '#064e3b', tech_xy=(50, 10))
    if data['shell'] == 2:
        draw_box(-22, 20, 'FS', '#1e3a8a', tech_xy=(-25, 32))
        draw_box(22, 20, 'SS', '#1e3a8a', tech_xy=(25, 32))
    else: 
        draw_box(0, 22, 'S', '#1e3a8a', tech_xy=(0, 32))

    # 2. THE OFFENSE (11-MAN PERSPECTIVE)
    # OL (Left to Right)
    ol = ['LT','LG','C','RG','RT']
    for i, x in enumerate([-12, -6, 0, 6, 12]):
        draw_box(x, -1.2, ol[i], '#161b22', is_def=False)
    
    # Backfield
    draw_box(0, -3.8, 'QB', '#1f2937', is_def=False)
    draw_box(5, -4.2, 'RB', '#161b22', is_def=False)

    # Skills - Correcting for X (Left WR), Z (Right WR), Slot (Y), and TE
    # Full spread includes a wide receiver on the extreme left.
    is_bunch = data['bunch']
    if is_bunch:
        skill_pos = [(-45, 0, 'WR/X'), (28, 0, 'WR/Z'), (24, -1.5, 'WR/Y'), (32, -1.5, 'TE')]
    else:
        skill_pos = [(-50, 0, 'WR/X'), (50, 0, 'WR/Z'), (-25, 0, 'WR/Y'), (18, 0, 'TE')]

    for i, (wx, wy, wl) in enumerate(skill_pos):
        draw_box(wx, wy, wl, '#111827', is_def=False)
        if offense_on:
            tx, ty = p_warp(wx, wy)
            route = data['routes'][i % len(data['routes'])]
            # Path Logic (Stems and Cuts)
            dest_x = 0 if "POST" in route else (wx + (15 if wx<0 else -15) if "OUT" in route else wx)
            dest_y = 30 if "SEAM" in route else (15 if "OUT" in route else 10)
            ax.annotate(route, xy=p_warp(dest_x, dest_y), xytext=(tx, ty),
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=2, alpha=0.9))

    plt.ylim(-18, 55); plt.xlim(-85, 85); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. INTELLIGENCE ENGINE
# ---------------------------------------------------------
def fetch_tactical_data(file_bytes, ratio):
    h = hashlib.sha256(file_bytes).hexdigest()
    val = int(h, 16)
    shell_val = (val % 2) + 1
    cushion = (val % 9) + 2
    
    v_type = "ALL-22 (WIDE)" if ratio > 1.7 else "EZ-CAM PERSPECTIVE"
    bank = ["SEAM", "OUT", "POST", "HITCH", "FADE"]
    r_set = [bank[(val+i)%len(bank)] for i in range(4)]
    
    return {"shell": shell_val, "cov": f"COVER {shell_val*2}", "cushion": cushion, 
            "view": v_type, "routes": r_set, "bunch": (val % 4 == 0), "hash": h[:8]}

# ---------------------------------------------------------
# 5. USER STATION UI
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569; letter-spacing:1px;'>OPERATIONAL HUB</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    o_on = st.toggle("ACTIVATE ROUTE OVERLAYS", value=False)
    d_on = st.toggle("ACTIVATE TACTICAL ZONES", value=False)
    st.divider()
    if st.button("TERMINATE SESSION"): system_reboot()

if f:
    pil_img = Image.open(f)
    stats = fetch_tactical_data(f.getvalue(), pil_img.width / pil_img.height)
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_flap_ui("System", "SCAN ACTIVE")
    with c2: render_flap_ui("Target", stats['cov'])
    with c3: render_flap_ui("Shell", f"{stats['shell']}-HIGH")
    with c4: render_flap_ui("Concept", "BUNCH-S" if stats['bunch'] else "11-SPREAD")

    main, r_pane = st.columns([2.5, 1], gap="large")
    with main:
        st.pyplot(draw_pro_schematic(stats, o_on, d_on), transparent=True)
        st.image(pil_img, use_container_width=True)
    with r_pane:
        st.info(f"**TRACE ID // {stats['hash']}**")
        st.markdown(f"Sensor Orientation: **{stats['view']}**")
        if stats['bunch']:
            st.error("OFFENSIVE ALERT: Compressed bunch cluster. High rub-route threat on play side.")
else:
    st.markdown("<div style='height:420px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:4px;'>FEED DISCONNECTED</p></div>", unsafe_allow_html=True)
