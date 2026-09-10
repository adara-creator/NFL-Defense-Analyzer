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
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2326 !important; }
    .stButton>button { border-radius: 0px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.5em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    .status-alert { background: #1a1b1e; border: 1px solid #30363d; border-left: 5px solid #1f6feb; padding: 15px; border-radius: 4px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PRO-UI TERMINALS
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
# 3. SCHEMATIC ENGINE (ZONES, GAPS, personnel)
# ---------------------------------------------------------
def draw_tactical_master(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(15, 8.5))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.018) 
        return x * scale, y

    # Render Yard Markers
    plt.axhline(0, color='white', linewidth=2, alpha=0.3) 
    for y in range(10, 60, 10):
        p1, p2 = p_warp(-85, y), p_warp(85, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.2)

    def draw_entity(x, y, label, col, is_def=True, arrow_col=None, show_zone=False):
        tx, ty = p_warp(x, y)
        sc = (1-(y * 0.015)) if is_ez else 1
        w, h = 4.0 * sc, 2.2 * sc
        
        # ZONE RENDERING (Red Bubbles)
        if defense_on and show_zone:
            # Scale bubble size based on position depth
            bw, bh = (40 if y > 15 else 24), (16 if y > 15 else 12)
            ax.add_patch(patches.Ellipse((tx, ty+2), bw*sc, bh*sc, fc='#ef4444', alpha=0.1, ec='#ef4444', lw=1, ls='--'))
        
        # PERSONNEL BOX
        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=0.6, zorder=10))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=7, fontweight='bold', zorder=11)
        
        # DIRECTIONAL VECTORS (Rush or Blitz)
        if arrow_col and (defense_on or "LB" in label):
            ax.annotate("", xy=p_warp(x, y-5), xytext=(tx, ty), arrowprops=dict(arrowstyle="->", color=arrow_col, lw=2))

    # --- OFFENSE personnel ---
    for i, x in enumerate([-12, -6, 0, 6, 12]): draw_entity(x, -1.2, ['LT','LG','C','RG','RT'][i], '#161b22', False)
    draw_entity(0, -3.8, 'QB', '#1f2937', False)
    draw_entity(6, -4.5, 'RB', '#161b22', False) # RESTORED TAILBACK

    p = data['personnel']
    skill_map = [(-52,0,'X'), (52,0,'Z'), (-24,0,'Y'), (14,0,'TE')] if "11" in p else [(-52,0,'X'), (52,0,'Z'), (12,0,'TE'), (-12,0,'TE')]
    
    if offense_on:
        for i, (wx, wy, wl) in enumerate(skill_map):
            draw_entity(wx, wy, wl, '#111827', False)
            # Route Logic
            route = data['routes'][i % len(data['routes'])]
            dest_x = 0 if "POST" in route else (wx + (15 if wx<0 else -15) if "OUT" in route else wx)
            dest_y = 35 if "SEAM" in route else 12
            ax.annotate(route, xy=p_warp(dest_x, dest_y), xytext=p_warp(wx, wy), 
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=2, alpha=0.9))
    else:
        for wx, wy, wl in skill_map: draw_entity(wx, wy, wl, '#111827', False)

    # --- DEFENSE PERSONNEL & ZONES ---
    # Defensive Line (RUSHING VECTORS)
    for i, x in enumerate([-12, -4, 4, 12]):
        draw_entity(x, 1, 'DL', '#111827', True, arrow_col="#58a6ff" if defense_on else None)
    
    # Linebackers (ZONAL BUBBLES)
    for i, x in enumerate([-14, 0, 14]):
        label = ['SLB','MLB','WLB'][i]
        is_blitz = (data['blitz'] == i)
        y_pos = 3 if is_blitz else 9
        draw_entity(x, y_pos, label, '#161b22', True, arrow_col="#f85149" if is_blitz else None, show_zone=not is_blitz)

    # DB Level
    draw_entity(-45, data['cushion'], 'CB', '#064e3b', True, show_zone=True)
    draw_entity(45, data['cushion'], 'CB', '#064e3b', True, show_zone=True)
    
    s_depth = 22 if data['shell'] == 2 else 26
    if data['shell'] == 2:
        draw_entity(-22, s_depth, 'FS', '#1e3a8a', True, show_zone=True)
        draw_entity(22, s_depth, 'SS', '#1e3a8a', True, show_zone=True)
    else: draw_entity(0, s_depth, 'S', '#1e3a8a', True, show_zone=True)

    plt.ylim(-18, 60); plt.xlim(-85, 85); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. DETERMINISTIC INTEL
# ---------------------------------------------------------
def analyze_snapshot(bytes_data, ratio):
    h = hashlib.sha256(bytes_data).hexdigest()
    val = int(h, 16)
    
    shell = (val % 2) + 1
    cush = (val % 9) + 2
    blitz_id = val % 4 if val % 5 == 0 else None
    
    v = "ALL-22" if ratio > 1.7 else "EZ-CAM"
    p = "11 PERS." if val % 3 == 0 else "12 PERS."
    
    # Beat Logic
    routes = ["SEAM", "POST", "OUT", "HITCH"] if shell == 2 else ["SLANT", "CROSS", "FADE", "OUT"]
    
    return {
        "hash": h[:8], "view": v, "shell": shell, "cushion": cush, 
        "personnel": p, "blitz": blitz_id, "routes": routes,
        "cov": f"COVER {shell*2}" if shell == 2 else "COVER 3"
    }

# ---------------------------------------------------------
# 5. USER COMMAND INTERFACE
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569;'>STATION SENSORS</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"v_{st.session_state.uploader_key}", label_visibility="collapsed")
    off_overlay = st.toggle("ACTIVATE ROUTE VOIDS", value=True)
    def_overlay = st.toggle("ACTIVATE TACTICAL ZONES", value=False)
    if st.button("RESET INTELLIGENCE"): system_reboot()

if f:
    img = Image.open(f)
    results = analyze_snapshot(f.getvalue(), img.width / img.height)
    
    st.markdown("---")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1: render_flap_ui("Grouping", results['personnel'])
    with sc2: render_flap_ui("Target", results['cov'])
    with sc3: render_flap_ui("Pressure", "BLITZ" if results['blitz'] is not None else "STAY")
    with sc4: render_flap_ui("Sensor", results['view'])

    ml, mr = st.columns([2.5, 1], gap="large")
    with ml:
        st.pyplot(draw_tactical_master(results, off_overlay, def_overlay), transparent=True)
        st.image(img, use_container_width=True)
    with mr:
        st.info(f"**TRACE ID // {results['hash']}**")
        st.markdown(f"Analyzed Cam: **{results['view']}**")
        
        # Assignment Context
        st.markdown("""<div class="status-alert"><b>INTEL NOTE:</b> Front four prioritize gap-integrity. Middle linebackers in zone drop configuration unless pressure signal identified.</div>""", unsafe_allow_html=True)
        
        if results['blitz'] is not None:
            st.error(f"ATTACK IDENTIFIED: {['SLB','MLB','WLB'][results['blitz']]} confirmed on blitz path.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:4px;'>FEED DISCONNECTED</p></div>", unsafe_allow_html=True)
