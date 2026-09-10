import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import random
import time

# ---------------------------------------------------------
# 1. UI CONFIGURATION (PRO-VISION COMMAND CENTER)
# ---------------------------------------------------------
st.set_page_config(page_title="PRO-VISION Defensive Analyzer", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #e1e4e8; font-family: 'Inter', sans-serif; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 15px; border-radius: 4px; }
    .stButton>button { width: 100%; border-radius: 2px; height: 3.5em; background-color: #1f6feb; color: white; border: none; font-weight: bold; letter-spacing: 1px; }
    .status-bar { padding: 10px; border-radius: 4px; margin-bottom: 20px; font-weight: bold; font-size: 0.85em; text-align: center; border: 1px solid #30363d; }
    .check-box { background-color: #1c2128; border: 1px solid #30363d; padding: 15px; border-left: 5px solid #f85149; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. TACTICAL MAPPING (ZONES & PRESS)
# ---------------------------------------------------------
def draw_schematic(obs):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_facecolor('#0d1117')
    
    # Field Foundations
    plt.axhline(0, color='white', linewidth=1.5, alpha=0.8) # LOS
    for y in range(10, 30, 10):
        plt.axhline(y, color='white', alpha=0.1, linestyle='--')

    # Draw Zones (Transparent Overlays)
    if obs['cov'] == "COVER 4 (QUARTERS)":
        zones = [(-50, 10, 25, 20), (-25, 10, 25, 20), (0, 10, 25, 20), (25, 10, 25, 20)]
        for z in zones:
            ax.add_patch(patches.Rectangle((z[0], z[1]), z[2], z[3], color='#1f6feb', alpha=0.15))
    elif obs['cov'] == "COVER 3":
        zones = [(-50, 12, 33, 20), (-16, 12, 32, 20), (16, 12, 33, 20)]
        for z in zones:
            ax.add_patch(patches.Rectangle((z[0], z[1]), z[2], z[3], color='#238636', alpha=0.15))

    # Function to draw positions
    def draw_pos(x, y, txt, col, press=False):
        # Draw the box
        ax.add_patch(patches.Rectangle((x-1.5, y-0.75), 3, 1.5, facecolor=col, edgecolor='white', linewidth=0.5))
        plt.text(x, y, txt, color='white', ha='center', va='center', fontsize=7, weight='bold')
        # If Press, draw contact indicator
        if press:
            ax.add_patch(patches.Arrow(x, y, 0, -2, width=1, color='red', alpha=0.6))

    # Defensive Line (DL)
    for x in np.linspace(-12, 12, 4):
        draw_pos(x, 1, 'DL', '#161b22')
    
    # Linebackers (LB)
    for x in np.linspace(-15, 15, obs['lb_count']):
        draw_pos(x, 4.5, 'LB', '#161b22')

    # Corners & Safeties
    is_press = obs['cushion'] < 3
    draw_pos(-35, obs['cushion'], 'CB', '#238636', press=is_press)
    draw_pos(35, obs['cushion'], 'CB', '#238636', press=is_press)

    if obs['shell'] == "2-HIGH":
        draw_pos(-15, 18, 'S', '#1f6feb')
        draw_pos(15, 18, 'S', '#1f6feb')
    else:
        draw_pos(0, 18, 'S', '#1f6feb')

    plt.ylim(-3, 30); plt.xlim(-50, 50); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 3. INTELLIGENCE ENGINE (BUNCH CONCEPTS)
# ---------------------------------------------------------
def run_scout_analysis(img):
    time.sleep(0.8)
    shell_val = random.choice([1, 2])
    dist = random.randint(1, 10)
    # Simulate Bunch Detection (High prevalence in modern NFL)
    bunch_detected = random.choice([True, False])
    
    cov_name = "COVER 4 (QUARTERS)" if shell_val == 2 and dist > 5 else "COVER 3" if shell_val == 1 else "MAN-PRESS"
    
    return {
        "shell": f"{shell_val}-HIGH",
        "cov": cov_name,
        "cushion": dist,
        "lb_count": random.randint(2, 3),
        "bunch": bunch_detected,
        "conf": random.randint(82, 96)
    }

# ---------------------------------------------------------
# 4. APP INTERFACE
# ---------------------------------------------------------
st.markdown("<h1 style='text-align: center; color: #58a6ff; letter-spacing: 3px;'>PRO-VISION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e; margin-bottom: 30px;'>TACTICAL DEFENSIVE SCHEMATIC PLATFORM</p>", unsafe_allow_html=True)

# Layout
col_side, col_main = st.columns([1, 2.5])

with col_side:
    st.markdown("<div class='status-bar'>SYSTEM STATUS: ACTIVE</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("SOURCE FEED", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")
    
    if uploaded_file:
        img_src = Image.open(uploaded_file)
        analysis = run_scout_analysis(img_src)
        
        st.metric("Primary Structure", analysis['cov'])
        st.metric("Confidence Level", f"{analysis['conf']}%")
        st.write("---")
        
        if analysis['bunch']:
            st.markdown("""
                <div class='check-box'>
                <b>OFFENSIVE ALERT: BUNCH CONCEPT</b><br>
                3 Receivers identified in close proximity (strong side).<br><br>
                <b>DEFENSIVE CHECK: BOX/LOCK</b><br>
                Model predicts the defense is checking to a 'Box' adjustment (4-on-3) to handle switch releases.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Formation: Spread (Standard spacing detected).")

with col_main:
    if uploaded_file:
        # Display schematic diagram with zones
        st.markdown("<div style='margin-left: 25px;'>", unsafe_allow_html=True)
        fig = draw_schematic(analysis)
        st.pyplot(fig, transparent=True)
        
        # Display the real photo for reference
        st.markdown("<b>LIVE IMAGE ANALYSIS:</b>", unsafe_allow_html=True)
        st.image(img_src, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='height: 400px; display: flex; align-items: center; justify-content: center; border: 1px solid #30363d;'>LOAD SOURCE DATA FROM SIDEBAR</div>", unsafe_allow_html=True)
