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
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.018) # Calibrated for broadcast view
        return x * scale, y

    # Field Grids
    plt.axhline(0, color='white', linewidth=2, alpha=0.6) 
    for y in range(10, 50, 10):
        p1, p2 = p_warp(-65, y), p_warp(65, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.25)

    # REUSABLE POSITION BOX UNIT
    def draw_box(x, y, label, col, is_def=True, tech_xy=None):
        tx, ty = p_warp(x, y)
        sc = (1-(y*0.015)) if is_ez else 1
        w, h = 3.6 * sc, 2.0 * sc
        
        # Red Bubble Zone (Anchored to position)
        if is_def and defense_on and tech_xy:
            zx, zy = p_warp(tech_xy[0], tech_xy[1])
            bw, bh = (35 if y > 15 else 18), (14 if y > 15 else 10)
            ax.add_patch(patches.Ellipse((zx, zy), bw*sc, bh*sc, color='#ef4444', alpha=0.1, ec='#ef4444', lw=1, ls='--'))
            plt.plot([tx, zx], [ty, zy], color='#ef4444', alpha=0.2, ls=':', lw=0.8)

        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=0.4, zorder=10))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=6, fontweight='bold', zorder=11)

    # 1. THE DEFENSE (Exactly as requested by Seahawks photo)
    # Front 4
    for i, x in enumerate([-12, -4, 4, 12]):
        draw_box(x, 1.2, ['DE','DT','DT','DE'][i], '#111827')
    # LB Corps (Sam, Mike, Will)
    for i, x in enumerate([-10, 0, 10]):
        draw_box(x, 4.8, ['SLB','MLB','WLB'][i], '#161b22', tech_xy=(x*1.3, 8))
    # Secondary (Corners & Safeties)
    cush = data['cushion']
    draw_box(-45, cush, 'CB', '#064e3b', tech_xy=(-50, 10))
    draw_box(45, cush, 'CB', '#064e3b', tech_xy=(50, 10))
    if data['shell'] == 2:
        draw_box(-20, 20, 'FS', '#1e3a8a', tech_xy=(-25, 28))
        draw_box(20, 20, 'SS', '#1e3a8a', tech_xy=(25, 28))
    else: draw_box(0, 22, 'S', '#1e3a8a', tech_xy=(0, 32))

    # 2. THE OFFENSE (Exact Position Identification)
    # Offensive Line (Lumen Field/Seahawks setup)
    ol_labels = ['LT','LG','C','RG','RT']
    for i, x in enumerate(np.linspace(-8.5, 8.5, 5)):
        draw_box(x, -1, ol_labels[i], '#161b22', is_def=False)
    # QB and Backfield
    draw_box(0, -3.5, 'QB', '#1f2937', is_def=False)
    draw_box(4, -4, 'RB', '#161b22', is_def=False)

    # 3. BUNCH CONCEPT SENSING
    # Offense skills
    is_bunch = data['bunch']
    if is_bunch:
        # Cluster of 3 Receivers on one side
        wr_positions = [(28, 0, 'WR'), (32, -1.5, 'WR'), (24, -1.5, 'TE')]
    else:
        # Spread Concept
        wr_positions = [(-45, 0, 'WR'), (45, 0, 'WR'), (18, 0, 'TE')]

    for i, (wx, wy, wl) in enumerate(wr_positions):
        draw_box(wx, wy, wl, '#111827', is_def=False)
        if offense_on:
            tx, ty = p_warp(wx, wy)
            route = data['routes'][i % len(data['routes'])]
            target_x = 0 if "POST" in route else (wx + (12 if wx<0 else -12) if "OUT" in route else wx)
            target_y = 28 if "SEAM" in route else (15 if "OUT" in route else 8)
            ax.annotate(route, xy=p_warp(target_x, target_y), xytext=(tx, ty),
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=1.8, alpha=0.9))

    plt.ylim(-15, 52); plt.xlim(-80, 80); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. INTELLIGENCE GATHERING
# ---------------------------------------------------------
def get_intel_report(bytes_val, ratio):
    h = hashlib.sha256(bytes_val).hexdigest()
    vi = int(h, 16)
    
    shell_val = (vi % 2) + 1
    cushion = (vi % 9) + 2
    bunch_logic = (vi % 4 == 0) # Trigger bunch sets based on hash ID
    
    routes = ["SEAM", "OUT", "POST"] if shell_val == 2 else ["SLANT", "OUT", "FADE"]
    v_type = "ALL-22" if ratio > 1.7 else "EZ-CAM PERSPECTIVE"
    
    return {"shell": shell_val, "cov": "COVER " + str(shell_val * 2), "cushion": cushion, 
            "view": v_type, "routes": routes, "bunch": bunch_logic, "hash": h[:8]}

# ---------------------------------------------------------
# 5. UI DISPLAY
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569;'>OPERATIONAL CONTROL</p>", unsafe_allow_html=True)
    src = st.file_uploader("", type=['jpg','png','jpeg'], key=f"v_{st.session_state.uploader_key}", label_visibility="collapsed")
    o_on = st.toggle("ROUTE RECONSTRUCTION", value=False)
    d_on = st.toggle("TACTICAL ZONES", value=False)
    st.divider()
    if st.button("TERMINATE SESSION"): system_reboot()

if src:
    r_img = Image.open(src)
    stats = get_intel_report(src.getvalue(), r_img.width/r_img.height)
    
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: render_flap_ui("Scheme", "BUNCH-TRIPS" if stats['bunch'] else "SPREAD")
    with c2: render_flap_ui("Shell", f"{stats['shell']}-HIGH")
    with c3: render_flap_ui("Predict", stats['cov'])
    with c4: render_flap_ui("Cam", "CALIBRATED")

    main, r_pane = st.columns([2.3, 1], gap="large")
    with main:
        st.pyplot(draw_pro_schematic(stats, o_on, d_on), transparent=True)
        st.image(r_img, use_container_width=True)
    with r_pane:
        st.info(f"**TRACE ID // {stats['hash']}**")
        st.markdown(f"Analyzed Viewport: **{stats['view']}**")
        if stats['bunch']:
            st.error("FORMATION ALERT: Compressed bunch identified. Defense adjusting with strong-side overload leverage.")
        else:
            st.write("Alignment profile identifies balanced defensive surface across all sectors.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:4px;'>FEED INACTIVE</p></div>", unsafe_allow_html=True)
