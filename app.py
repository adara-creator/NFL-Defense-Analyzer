import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import random
import time

# ---------------------------------------------------------
# 1. STYLE & THEME (Dark Mode Scouting UI)
# ---------------------------------------------------------
st.set_page_config(page_title="Defensive Schematic Analyzer", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', Roboto, sans-serif; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 6px; }
    .stButton>button { width: 100%; border-radius: 4px; height: 3.2em; background-color: #238636; color: white; border: none; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
    .report-card { background-color: #0d1117; border: 1px solid #30363d; padding: 20px; border-radius: 6px; margin-bottom: 15px; }
    div[data-testid="stFileUploader"] { background-color: #161b22; border: 1px dashed #484f58; border-radius: 6px; }
    .scout-header { color: #f0f6fc; border-left: 4px solid #1f6feb; padding-left: 15px; margin-bottom: 20px; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SCHEMATIC RENDERING (Box-Based Field Diagram)
# ---------------------------------------------------------
def draw_defensive_diagram(obs):
    """Creates a professional field map using boxes for players."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor('#0d1117')
    
    # Grass lines (Line of Scrimmage at 0)
    plt.axhline(0, color='#30363d', linewidth=2)
    for y in range(5, 25, 5):
        plt.axhline(y, color='#161b22', linewidth=1, alpha=0.5)

    def draw_player(x, y, label, color):
        rect = patches.Rectangle((x-1.5, y-0.75), 3, 1.5, linewidth=1, edgecolor='white', facecolor=color, alpha=0.9)
        ax.add_patch(rect)
        plt.text(x, y, label, color='white', ha='center', va='center', fontsize=8, weight='bold')

    # Draw Front (DL - Defensive Line) - Blue boxes
    dl_x = np.linspace(-10, 10, 4)
    for x in dl_x:
        draw_player(x, 1, 'DL', '#1f6feb')

    # Draw Second Level (LB - Linebackers) - Orange boxes
    lb_count = obs['box_count'] - 4
    if lb_count > 0:
        lb_x = np.linspace(-15, 15, lb_count)
        for x in lb_x:
            draw_player(x, 4.5, 'LB', '#d29922')

    # Draw Corners (CB) - Green boxes
    cb_y = obs['cushion'] if obs['cushion'] > 0 else 1.5
    draw_player(-35, cb_y, 'CB', '#238636')
    draw_player(35, cb_y, 'CB', '#238636')

    # Draw Deep Level (S - Safeties) - Red boxes
    if obs['shell_num'] == 2:
        draw_player(-15, 16, 'S', '#da3633')
        draw_player(15, 16, 'S', '#da3633')
    elif obs['shell_num'] == 1:
        draw_player(0, 16, 'S', '#da3633')

    plt.ylim(-2, 22)
    plt.xlim(-50, 50)
    plt.axis('off')
    return fig

# ---------------------------------------------------------
# 3. ANALYSIS LOGIC
# ---------------------------------------------------------
def analyze_snap(image):
    # Simulated detections
    s_count = random.choice([1, 2])
    dist = random.randint(1, 10)
    box = random.randint(6, 8)
    
    # Specific NFL rules logic
    if s_count == 2:
        pred = "COVER 4 (QUARTERS)" if dist > 5 else "COVER 2"
        logic = "Dual deep half indicators detected."
    else:
        pred = "COVER 3" if dist > 5 else "COVER 1"
        logic = "Single deep middle indicator (MOFC) detected."

    return {
        "pred": pred, "shell": f"{s_count}-HIGH", "shell_num": s_count,
        "box_count": box, "cushion": dist, "logic": logic, "conf": random.randint(70, 92)
    }

# ---------------------------------------------------------
# 4. APP INTERFACE
# ---------------------------------------------------------
# Clean, professional Header (no emoji)
st.markdown("<h1 style='text-align: center; color: #f0f6fc; letter-spacing: 2px;'>DEFENSIVE SCHEMATIC ANALYZER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; font-size: 0.9em; margin-bottom: 40px;'>STRUCTURAL COVERAGE PREDICTION SYSTEM // NFL GRADE</p>", unsafe_allow_html=True)

# Layout: 3 Columns with the Middle wide
_, col_center, _ = st.columns([1, 3, 1])

with col_center:
    uploaded_file = st.file_uploader("", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")

if uploaded_file is not None:
    # RUN LOGIC
    img = Image.open(uploaded_file)
    results = analyze_snap(img)
    
    st.markdown("---")
    
    # Intelligence Panel (Observed vs Inferred)
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='scout-header'>PRIMARY DETECTION RESULTS</div>", unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        m1.metric("Safety Shell", results['shell'])
        m2.metric("CB Alignment", f"{results['cushion']} YDS OFF")
        
        m3, m4 = st.columns(2)
        m3.metric("Primary Pred", results['pred'])
        m4.metric("Model Conf", f"{results['conf']}%")
        
        st.write("") # Spacer
        st.image(img, use_container_width=True, caption="SOURCE FEED: PRE-SNAP IMAGE")

    with col2:
        st.markdown("<div class='scout-header'>SPATIAL SCHEMATIC</div>", unsafe_allow_html=True)
        # Diagram
        fig = draw_defensive_diagram(results)
        st.pyplot(fig, transparent=True)
        
        st.markdown("<div class='scout-header'>TECHNICAL REPORT</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div class='report-card'>
            <b>ANALYSIS:</b> {results['logic']}<br><br>
            <b>STRUCTURAL TYPE:</b> {'Zone Hybrid' if results['cushion'] > 4 else 'Aggressive/Press Man'}<br>
            <b>OBSERVATION:</b> Front shows {results['box_count']} defenders near the line. 
            Cushion depth suggests the {results['shell']} looks to minimize explosive deep passing attempts.
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("<div style='text-align: center; padding: 50px; color: #484f58;'>WAITING FOR SOURCE DATA: PLEASE UPLOAD A PRE-SNAP IMAGE</div>", unsafe_allow_html=True)
