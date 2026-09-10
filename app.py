import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CORE ENGINE & RESET
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
    .stButton>button { border-radius: 2px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.2em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PRO-UI TERMINALS
# ---------------------------------------------------------
def render_header_white():
    st.markdown("<h1 style='text-align: center; letter-spacing: 7px; color: #ffffff; font-family: Courier; margin-top: -35px;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_flap_ui(label, text):
    val = str(text).upper()
    fid = hashlib.md5(label.encode()).hexdigest()[:6]
    html = f"""
    <div style="background: transparent;">
        <p style="color: #4b5563; font-size: 0.55rem; text-transform: uppercase; margin: 0; letter-spacing: 2px;">{label}</p>
        <div id="w-{fid}" style="display: flex; gap: 3px; padding-top: 6px;"></div>
    </div>
    <script>
        const v = "{val}"; const b = document.getElementById('w-{fid}');
        for(let i=0; i<v.length; i++) {{
            let d = document.createElement('div'); 
            d.style = "width: 28px; height: 44px; background: #111827; color: #f8fafc; font-family: monospace; font-size: 26px; text-align: center; line-height: 44px; border-radius: 2px; border: 1px solid #1f2937;";
            d.innerText = v[i]; b.appendChild(d);
        }}
    </script>
    """
    components.html(html, height=80)

# ---------------------------------------------------------
# 3. ADVANCED PLAYBOOK ENGINE (FULL ROUTES)
# ---------------------------------------------------------
def draw_tactical_schematic(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.016)
        return x * scale, y

    # Field Layout
    for y in range(0, 50, 10):
        p1, p2 = p_warp(-65, y), p_warp(65, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.3)

    # 1. PERSONNEL RENDER
    def draw_unit(x, y, txt, col, border='#ffffff', tech_xy=None):
        tx, ty = p_warp(x, y)
        sc = (1-(y*0.015)) if is_ez else 1
        w, h = 3.6 * sc, 1.8 * sc
        
        # Red Bubble Zone (The Requested 4-3 Overlay)
        if defense_on and tech_xy:
            zx, zy = p_warp(tech_xy[0], tech_xy[1])
            bw, bh = (40 if y > 15 else 22), (16 if y > 15 else 12)
            ax.add_patch(patches.Ellipse((zx, zy), bw * sc, bh * sc, color='#ef4444', alpha=0.15, ec='#ef4444', lw=1, ls='--'))
            plt.plot([tx, zx], [ty, zy], color='#ef4444', alpha=0.3, ls=':', lw=1)

        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec=border, lw=0.6, zorder=10))
        plt.text(tx, ty, txt, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=11)

    # 2. DEFENSE personnel
    for x in np.linspace(-12, 12, 4): draw_unit(x, 1, 'DL', '#161b22')
    for i, x in enumerate(np.linspace(-10, 10, 3)): draw_unit(x, 4.5, ['S', 'M', 'W'][i], '#161b22', tech_xy=(x*1.5, 8))
    
    c = data['cushion']
    draw_unit(-42, c, 'CB', '#064e3b', tech_xy=(-45, 12))
    draw_unit(42, c, 'CB', '#064e3b', tech_xy=(45, 12))
    
    if data['shell'] == 2:
        draw_unit(-20, 20, 'FS', '#1e3a8a', tech_xy=(-25, 30))
        draw_unit(20, 20, 'SS', '#1e3a8a', tech_xy=(25, 30))
    else: draw_unit(0, 22, 'S', '#1e3a8a', tech_xy=(0, 32))

    # 3. FULL ROUTE RECONSTRUCTION (The Logic)
    def draw_full_route(start_x, start_y, route_name):
        # Coordinates based on football theory: (vertical stem, break width, break depth)
        schemes = {
            "POST": [(0, 12), (15 if start_x < 0 else -15, 15)],
            "CORNER": [(0, 12), (-12 if start_x < 0 else 12, 12)],
            "OUT": [(0, 8), (-10 if start_x < 0 else 10, 0)],
            "SLANT": [(0, 3), (12 if start_x < 0 else -12, 12)],
            "COMEBACK": [(0, 14), (6 if start_x < 0 else -6, -4)],
            "HITCH": [(0, 6), (2 if start_x < 0 else -2, -2)],
            "SEAM": [(0, 35)]
        }
        
        path_segments = schemes.get(route_name, [(0, 20)])
        current_x, current_y = start_x, start_y
        
        for seg_x, seg_y in path_segments:
            next_x = current_x + seg_x
            next_y = current_y + seg_y
            
            p1 = p_warp(current_x, current_y)
            p2 = p_warp(next_x, next_y)
            
            # Draw Route Stem/Branch
            ax.annotate("", xy=p2, xytext=p1, 
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=2, alpha=0.9))
            
            # Place Route Label at the break or end
            plt.text(p2[0], p2[1]+1, route_name, color="#facc15", fontsize=5, ha='center', fontweight='bold')
            current_x, current_y = next_x, next_y

    # 4. OFFENSE personnel
    for x in np.linspace(-9, 9, 5): draw_unit(x, -1, 'OL', '#111827', '#374151')
    draw_unit(0, -4, 'QB', '#1f2937'); draw_unit(4, -4, 'RB', '#111827')
    
    wr_spots = [(-45, 0, data['r_set'][0]), (45, 0, data['r_set'][1]), (22, 0, data['r_set'][2])]
    for wx, wy, wr_route in wr_spots:
        draw_unit(wx, wy, "WR" if abs(wx)>30 else "TE", '#111827', '#374151')
        if offense_on:
            draw_full_route(wx, wy, wr_route)

    plt.ylim(-15, 55); plt.xlim(-75, 75); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. DETERMINISTIC INTEL
# ---------------------------------------------------------
def fetch_intel(bytes_data, ratio):
    h = hashlib.sha256(bytes_data).hexdigest()
    val = int(h, 16)
    shell = (val % 2) + 1
    
    # Random but Image-Consistent Route Tree for Variety
    bank = ["POST", "OUT", "SLANT", "CORNER", "HITCH", "COMEBACK", "SEAM"]
    r_set = [bank[(val+i)%len(bank)] for i in range(3)]
    
    view = "ALL-22 (WIDE)" if ratio > 1.7 else "EZ-CAM (PERSPECTIVE)"
    return {"shell": shell, "cov": "COVER " + str(shell * 2), "cushion": (val % 8) + 2, 
            "view": view, "r_set": r_set, "hash": h[:8]}

# ---------------------------------------------------------
# 5. UI INTERFACE
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569; letter-spacing:1px;'>OPERATIONAL HUB</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    off_on = st.toggle("ACTIVATE ROUTE RECONSTRUCTION", value=False)
    def_on = st.toggle("ACTIVATE DEFENSIVE BUBBLES", value=False)
    if st.button("TERMINATE SESSION"): system_reboot()

if f:
    results = fetch_intel(f.getvalue(), Image.open(f).width / Image.open(f).height)
    st.markdown("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_flap_ui("Target", results['cov'])
    with c2: render_flap_ui("Shell", f"{results['shell']}-HIGH")
    with c3: render_flap_ui("Concept", results['r_set'][0])
    with c4: render_flap_ui("Persp.", "CALIBRATED")

    l, r = st.columns([2.2, 1], gap="large")
    with l:
        st.pyplot(draw_tactical_schematic(results, off_on, def_on), transparent=True)
        st.image(Image.open(f), use_container_width=True)
    with r:
        st.info(f"**TRACE ID // {results['id']}**")
        st.markdown(f"**Field Strategy:** Attack plan emphasizes **{results['r_set'][0]}** logic to challenge depth-to-width ratios.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:3px;'>FEED STANDBY</p></div>", unsafe_allow_html=True)
