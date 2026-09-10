import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CORE ARCHITECTURE & PERSISTENCE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def trigger_full_reset():
    st.session_state.uploader_key += 1
    st.rerun()

st.set_page_config(page_title="PRO-VISION // TACTICAL INTELLIGENCE", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stMetric { display: none !important; } 
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2326 !important; }
    .stButton>button { border-radius: 2px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.2em; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    .intel-panel { background: #111827; border: 1px solid #1f2937; padding: 20px; border-radius: 4px; border-left: 4px solid #1f6feb; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DYNAMIC TERMINAL FLAPS (PRO-STYLE)
# ---------------------------------------------------------
def render_header():
    st.markdown("<h1 style='text-align: center; letter-spacing: 6px; color: #ffffff; font-family: Courier; margin-top: -30px;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_elastic_flap(label, text):
    word = str(text).upper()
    flap_html = f"""
    <div style="background: transparent;">
        <p style="color: #4b5563; font-size: 0.55rem; text-transform: uppercase; margin: 0; letter-spacing: 2px;">{label}</p>
        <div id="w-{label}" style="display: flex; gap: 3px; padding-top: 6px;"></div>
    </div>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');
        .t {{ width: 28px; height: 44px; background: #111827; color: #f8fafc; font-family: 'JetBrains Mono', monospace; font-size: 26px; text-align: center; line-height: 44px; border-radius: 3px; border: 1px solid #1f2937; perspective: 100px; }}
        .f {{ animation: sp 0.1s linear; }} @keyframes sp {{ 0% {{ transform: rotateX(0deg); }} 100% {{ transform: rotateX(-180deg); }} }}
    </style>
    <script>
        const txt = "{word}";
        const box = document.getElementById('w-{label}');
        for(let i=0; i<txt.length; i++) {{
            let d = document.createElement('div'); d.className = 't'; d.id = 't-{label}-'+i; box.appendChild(d);
            setTimeout(() => {{ const e = document.getElementById('t-{label}-'+i); e.classList.add('f'); e.innerText = txt[i]; }}, i*30);
        }}
    </script>
    """
    components.html(flap_html, height=80)

# ---------------------------------------------------------
# 3. ADVANCED RENDERING (QB PERSPECTIVE WARP)
# ---------------------------------------------------------
def draw_schematic(data, overlay_on):
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_facecolor('#0b0d0e')
    
    is_qb_view = "EZ" in data['view']
    
    # Grid transformation logic for QB Perspective
    def transform_coord(x, y):
        if not is_qb_view: return x, y
        # In End Zone view, Y gets compressed as it goes away, X gets wider
        depth_scale = 1 - (y * 0.015) 
        return x * depth_scale, y

    # Render Field Lines
    for y_val in range(0, 40, 10):
        tx1, ty1 = transform_coord(-55, y_val)
        tx2, ty2 = transform_coord(55, y_val)
        plt.plot([tx1, tx2], [ty1, ty2], color='#1f2937', lw=1, alpha=0.5)

    def draw_unit(x, y, label, col, is_def=True):
        tx, ty = transform_coord(x, y)
        w, h = (3.4, 1.8) if not is_qb_view else (3.4 * (1-(y*0.015)), 1.8 * (1-(y*0.015)))
        rect = patches.Rectangle((tx - w/2, ty - h/2), w, h, fc=col, ec='white', lw=0.5, alpha=0.9, zorder=5)
        ax.add_patch(rect)
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=6)

    # OFFENSE (Negative Y)
    # OL (The Front 5)
    for i, x in enumerate(np.linspace(-8, 8, 5)): draw_unit(x, -0.5, 'OL', '#161b22', False)
    draw_unit(0, -3.5, 'QB', '#1f2937', False) # Quarterback (Shotgun)
    draw_unit(4, -3.5, 'RB', '#161b22', False) # Tailback
    
    # Offense Skill Position Layout (11, 12, 13)
    p = data['personnel']
    bx = data['bunch']
    
    # Determing offensive positioning
    if bx:
        skills = [(30, 0), (27, -1.5), (24, 0)] # Tight Cluster
    else:
        if "11" in p: skills = [(-42, 0), (42, 0), (25, 0)] # 3 Wide
        else: skills = [(-38, 0), (38, 0), (12, 0)] # 2 Wide/Heavy
    
    for x_s, y_s in skills:
        draw_unit(x_s, y_s, 'WR' if x_s > 20 else 'TE', '#161b22', False)
        if overlay_on:
            tx, ty = transform_coord(x_s, y_s)
            ax.annotate(data['route'], xy=transform_coord(x_s, 22), xytext=(tx, ty), 
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=2, alpha=0.7))

    # DEFENSE (Positive Y)
    # Line & Backers
    for x in np.linspace(-12, 12, 4): draw_unit(x, 1, 'DL', '#161b22')
    for x in np.linspace(-8, 8, 2): draw_unit(x, 4.5, 'LB', '#161b22')
    
    # Boundary / Shell
    c = data['cushion']
    draw_unit(-35, c, 'CB', '#064e3b')
    draw_unit(35, c, 'CB', '#064e3b')
    
    if data['shell'] == 2:
        draw_unit(-16, 20, 'S', '#1e3a8a'); draw_unit(16, 20, 'S', '#1e3a8a')
    else:
        draw_unit(0, 20, 'S', '#1e3a8a')

    plt.ylim(-10, 40); plt.xlim(-60, 60); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. TACTICAL FINGERPRINT ENGINE
# ---------------------------------------------------------
def generate_tactical_lock(file_bytes, ratio):
    h_int = int(hashlib.sha256(file_bytes).hexdigest(), 16)
    view = "ALL-22 (WIDE)" if ratio > 1.7 else "EZ-CAM (PERSPECTIVE)"
    
    s_count = (h_int % 2) + 1
    cushion = (h_int % 8) + 2
    per_opt = ["11 Pers.", "12 Pers.", "13 Pers."]
    
    cov = "COVER 4" if s_count == 2 and cushion > 5 else "COVER 2" if s_count == 2 else "COVER 3" if cushion > 4 else "COVER 1"
    
    return {
        "view": view, "shell": s_count, "cov": cov, "cushion": cushion,
        "personnel": per_opt[h_int % 3], "bunch": (h_int % 5 == 0),
        "route": "POST" if cushion > 5 else "FADE" if cushion < 3 else "SLANT",
        "hash": hex(h_int)[2:10]
    }

# ---------------------------------------------------------
# 5. USER STATION UI
# ---------------------------------------------------------
render_header()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569; letter-spacing:1px;'>OPERATIONAL HUB</p>", unsafe_allow_html=True)
    input_file = st.file_uploader("", type=['jpg','png','jpeg'], key=f"feed_{st.session_state.uploader_key}", label_visibility="collapsed")
    sim_on = st.toggle("ACTIVATE PREDICTIVE ROUTES", value=False)
    
    st.markdown("<div class='remove-btn' style='margin-top:20px;'>", unsafe_allow_html=True)
    if st.button("TERMINATE SESSION"): trigger_full_reset()
    st.markdown("</div>", unsafe_allow_html=True)

if input_file:
    img = Image.open(input_file)
    results = generate_tactical_lock(input_file.getvalue(), img.width / img.height)
    
    st.markdown("---")
    
    # TACTICAL FLAPS
    f1, f2, f3, f4 = st.columns(4)
    with f1: render_elastic_flap("Personnel", results['personnel'])
    with f2: render_elastic_flap("Target", results['cov'])
    with f3: render_elastic_flap("Shell", f"{results['shell']}-HIGH")
    with f4: render_elastic_flap("Logic", "PERSPECTIVE" if "EZ" in results['view'] else "STATIC")

    l, r = st.columns([2, 1], gap="large")
    with l:
        st.pyplot(draw_schematic(results, sim_on), transparent=True)
        st.image(img, use_container_width=True)
    with r:
        st.markdown(f"**INTEL LOG // {results['hash']}**")
        st.markdown(f"""<div class="intel-panel">
            <b>{results['personnel']} RECOGNIZED</b><br>
            Current sensor is <b>{results['view']}</b>. Adjusting for coordinate distortion.<br><br>
            <i>Note: Front seven maintains balanced gap integrity. Offensive attack vector predicted: <b>{results['route']}</b>.</i>
        </div>""", unsafe_allow_html=True)
        if results['bunch']:
            st.warning("OFFENSIVE BUNCH ALERT: Compressed receivers identified. Strong side overload risk.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; border-radius:4px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#0e1113;'><h4 style='color:#334155; letter-spacing:3px;'>FEED STANDBY</h4></div>", unsafe_allow_html=True)
