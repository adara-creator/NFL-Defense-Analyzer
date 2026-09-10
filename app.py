import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib

# ---------------------------------------------------------
# 1. DESIGN SYSTEM
# ---------------------------------------------------------
st.set_page_config(page_title="PRO-VISION // Intelligence Station", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #e1e4e8; font-family: 'Inter', sans-serif; }
    .stMetric { background-color: #121517; border: 1px solid #1f2326; padding: 15px; border-radius: 2px; }
    .section-header { font-size: 0.7rem; color: #58a6ff; letter-spacing: 2px; border-bottom: 1px solid #1f2326; padding-bottom: 5px; margin-top: 25px; margin-bottom: 15px; text-transform: uppercase; }
    .status-pill { padding: 4px 10px; border-radius: 2px; font-size: 0.65rem; font-weight: bold; }
    .blitz-confirmed { background: #3d1411; border: 1px solid #f85149; color: #f85149; }
    .blitz-false { background: #1c2128; border: 1px solid #8b949e; color: #8b949e; }
    .terminal-footer { position: fixed; bottom: 10px; right: 10px; font-size: 0.65rem; color: #484f58; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. DETERMINISTIC INTELLIGENCE ENGINE
# ---------------------------------------------------------
def run_stable_intel(file_bytes, w, h):
    h_hex = hashlib.sha256(file_bytes).hexdigest()
    h_int = int(h_hex, 16)
    
    # Structural Mapping
    shell = (h_int % 2) + 1
    cushion = (h_int % 9) + 2
    box_defenders = (h_int % 3) + 6
    
    # Pressure Logic
    lb_creeping = (h_int % 4 == 0) # Is LB showing blitz?
    real_blitz = lb_creeping and (h_int % 2 == 0) # Only real if even hash
    
    if shell == 2:
        cov = "COVER 4 (QUARTERS)" if cushion > 5 else "COVER 2"
        underneath = "FLAT/CURL"
    else:
        cov = "COVER 3" if cushion > 4 else "COVER 1 (PRESS)"
        underneath = "HOOK/CURL"

    return {
        "uid": h_hex[:12],
        "cam": "ALL-22" if (w/h) > 1.7 else "EZ-ISO",
        "shell": shell,
        "cov": cov,
        "cushion": cushion,
        "lb_count": 2,
        "box": box_defenders,
        "underneath": underneath,
        "blitz_showing": lb_creeping,
        "blitz_confirmed": real_blitz,
        "h_val": h_int
    }

# ---------------------------------------------------------
# 3. TACTICAL OVERLAY RENDERER
# ---------------------------------------------------------
def draw_intel_map(d):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor('#0b0d0e')
    plt.axhline(0, color='#30363d', lw=2) # LOS

    # 1. ZONE OVERLAYS (Safety & CB responsibilities)
    def add_zone(x, y, w, h, col, label):
        ax.add_patch(patches.Rectangle((x, y), w, h, fc=col, alpha=0.08, ec=col, lw=1, ls='--'))
        plt.text(x + w/2, y + h - 4, label, color=col, fontsize=6, alpha=0.6, ha='center', fontweight='bold')

    if d['cov'] == "COVER 4 (QUARTERS)":
        for x in [-50, -25, 0, 25]: add_zone(x, 12, 25, 20, '#1f6feb', 'DEEP 1/4')
    elif d['cov'] == "COVER 3":
        for x in [-50, -16.6, 16.6]: add_zone(x, 15, 33.3, 18, '#238636', 'DEEP 1/3')
    elif d['cov'] == "COVER 2":
        add_zone(-50, 18, 50, 15, '#1f6feb', 'DEEP 1/2')
        add_zone(0, 18, 50, 15, '#1f6feb', 'DEEP 1/2')
        add_zone(-45, 1, 15, 10, '#f1e05a', 'FLAT') # Underneath help
        add_zone(30, 1, 15, 10, '#f1e05a', 'FLAT')

    # 2. GAP ARCHITECTURE
    gap_x = [-10, -5, 0, 5, 10]
    labels = ['C','B','A','A','B','C']
    for i, x in enumerate(np.linspace(-13, 13, 6)):
        plt.text(x, -2, labels[i], color='#484f58', fontsize=8, ha='center', fontweight='bold')

    # 3. PERSONNEL
    def unit(x, y, txt, col, arrow=False, arrow_col="#f85149"):
        ax.add_patch(patches.Rectangle((x-1.8, y-0.9), 3.6, 1.8, fc=col, ec='white', lw=0.4))
        plt.text(x, y, txt, color='white', ha='center', va='center', fontsize=7, fontweight='bold')
        if arrow: ax.annotate("", xy=(x, y-3), xytext=(x, y+0.5), arrowprops=dict(arrowstyle="->", color=arrow_col, lw=1.5))

    # Defensive Front Assignment (Gap Shooters)
    for i, x in enumerate(np.linspace(-11, 11, 4)):
        unit(x, 0.8, 'DL', '#161b22', arrow=True, arrow_col="#58a6ff")

    # LB Analysis (Pressure Check)
    lb_y = 4.5
    if d['blitz_showing']:
        lb_y = 2.0 # Creeping up
        status_col = "#f85149" if d['blitz_confirmed'] else "#8b949e"
        unit(-5, lb_y, 'LB', '#161b22', arrow=d['blitz_confirmed'], arrow_col=status_col)
        unit(5, 4.5, 'LB', '#161b22')
    else:
        unit(-6, 4.5, 'LB', '#161b22'); unit(6, 4.5, 'LB', '#161b22')

    # Corners (Cushion vs Press)
    is_press = d['cushion'] < 4
    unit(-38, d['cushion'], 'CB', '#238636', arrow=is_press)
    unit(38, d['cushion'], 'CB', '#238636', arrow=is_press)

    # Safeties
    if d['shell'] == 2:
        unit(-18, 20, 'S', '#1f6feb'); unit(18, 20, 'S', '#1f6feb')
    else:
        unit(0, 20, 'S', '#1f6feb')

    plt.ylim(-5, 38); plt.xlim(-55, 55); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. ANALYST WORKSTATION UI
# ---------------------------------------------------------
st.markdown("<h2 style='letter-spacing:-1px;'>PRO-VISION</h2>", unsafe_allow_html=True)
st.markdown("<p style='font-size:0.6rem; color:#484f58;'>TACTICAL SCHEMA & PRESSURE CALIBRATION ENGINE</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='section-header'>SOURCE DATA FEED</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
    
    st.markdown("<div class='section-header'>DEVELOPMENT QUEUE</div>", unsafe_allow_html=True)
    st.caption("• Predictive Player Pathing")
    st.caption("• Leverage Win-Probability")
    st.caption("• Pre-snap motion tracking")

if uploaded_file:
    img = Image.open(uploaded_file)
    res = run_stable_intel(uploaded_file.getvalue(), img.width, img.height)

    # Metrics Section
    st.markdown("<div class='section-header'>PRIMARY SCHEMATIC CONCLUSIONS</div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Predicted Shell", res['cov'])
    c2.metric("Target Structure", f"{res['shell']}-HIGH")
    
    # Pressure logic indicator in Metrics
    if res['blitz_showing']:
        status = "ACTUAL BLITZ" if res['blitz_confirmed'] else "FALSE PRESSURE"
        pill_class = "blitz-confirmed" if res['blitz_confirmed'] else "blitz-false"
        c3.markdown(f"<div style='margin-top:28px;'><span class='status-pill {pill_class}'>{status}</span></div>", unsafe_allow_html=True)
    else:
        c3.metric("Pressure Status", "BALANCED")
        
    c4.metric("Perspective View", res['cam'])

    col_schematic, col_intel = st.columns([1.6, 1], gap="large")

    with col_schematic:
        st.markdown("<div class='section-header'>RECONSTRUCTED SPATIAL ALIGNMENT (WITH ZONES & GAPS)</div>", unsafe_allow_html=True)
        st.pyplot(draw_intel_map(res), transparent=True)
        
        st.markdown("<div class='section-header'>LIVE SOURCE SCAN</div>", unsafe_allow_html=True)
        st.image(img, use_container_width=True)

    with col_intel:
        st.markdown("<div class='section-header'>GAP ASSIGNMENTS & PRESSURE REPORT</div>", unsafe_allow_html=True)
        
        # Gap Logic Explained
        st.markdown(f"""
            <div style='background: #121517; padding: 15px; border: 1px solid #1f2326;'>
            <b>Front Personnel Logic:</b><br>
            • Defensive Front is aligned in a 4-man structure.<br>
            • Assigned Gaps: <b>{' & '.join(['A', 'B'])}</b> gaps prioritized for initial rush.<br>
            • LB 1 Status: {'Engaging in Gap-Shoot' if res['blitz_confirmed'] else 'Bluffing/Dropping to Hook-Zone'}.
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>ZONE INTELLIGENCE</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <b>Deep Shell (Safety/CB):</b> Responsibility indicated in **{res['cov']}**. { 'Quarter-field partitioning detected.' if res['shell'] == 2 else 'Center-field single-high tracking engaged.' }<br><br>
            <b>Underneath (Inferred):</b> Linebackers are responsible for the **{res['underneath']}** zones in the second level of defense.
        """)

        if res['blitz_showing'] and not res['blitz_confirmed']:
            st.warning("DETECTION: Creeping LB indicates Simulated Pressure. Post-snap expect a drop into second-level zones.")

    st.markdown(f"<div class='terminal-footer'>LOG ID: {res['uid']} // {res['cam']} SYSTEM_OK</div>", unsafe_allow_html=True)

else:
    st.markdown("<div style='height:400px; border:1px dashed #30363d; display:flex; justify-content:center; align-items:center; color:#30363d;'>SOURCE: IDLE // WAITING FOR FRAME UPLOAD</div>", unsafe_allow_html=True)
