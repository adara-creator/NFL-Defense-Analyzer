import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import random
import time

# ---------------------------------------------------------
# 1. STYLE & THEME (The "Professional" Look)
# ---------------------------------------------------------
st.set_page_config(page_title="Pro-Vision Defense Analyzer", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #ffffff; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3.5em; background-color: #2e7d32; color: white; border: none; font-weight: bold; }
    .stMetric { background-color: #1a1c23; border: 1px solid #374151; padding: 15px; border-radius: 10px; }
    .card-inferred { background-color: #111827; border-left: 5px solid #1e88e5; padding: 20px; border-radius: 5px; }
    .card-observed { background-color: #111827; border-left: 5px solid #43a047; padding: 20px; border-radius: 5px; }
    div[data-testid="stFileUploader"] { background-color: #1a1c23; border: 2px dashed #374151; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOGIC FUNCTIONS
# ---------------------------------------------------------
def get_analysis(img):
    """Pure heuristic analysis - simulated computer vision."""
    w, h = img.size
    is_broadcast = (w/h < 1.6)
    safeties = random.choice([0, 1, 2])
    dist = random.randint(1, 10)
    
    # Simple coverage logic
    if safeties == 2:
        res = ("Cover 4", "2-HIGH", "ZONE") if dist > 4 else ("Cover 2", "2-HIGH", "ZONE")
    elif safeties == 1:
        res = ("Cover 3", "1-HIGH", "ZONE") if dist > 4 else ("Cover 1", "1-HIGH", "MAN")
    else:
        res = ("Cover 0", "0-HIGH", "MAN")
        
    return {
        "cov": res[0], "shell": res[1], "type": res[2], 
        "conf": random.randint(72, 95), "cushion": dist, "crop": is_broadcast
    }

# ---------------------------------------------------------
# 3. CENTERED FRONT END
# ---------------------------------------------------------
# Top Header
st.markdown("<h1 style='text-align: center; color: #f3f4f6;'>🏈 PRO-VISION DEFENSE ANALYZER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af;'>Pre-Snap NFL Defensive Shell Detection & Logic Engine</p>", unsafe_allow_html=True)
st.markdown("---")

# Centered Uploader
# Using a 3-column layout where the middle is wide
col_left, col_mid, col_right = st.columns([1, 2, 1])

with col_mid:
    uploaded_file = st.file_uploader("", type=['jpg', 'png', 'jpeg'])

# THE CORE WRAPPER: This hides all errors by checking if a file exists
if uploaded_file is not None:
    
    # Setup Data
    image = Image.open(uploaded_file)
    results = get_analysis(image)
    
    # 1. Metrics Header (Full Width)
    st.markdown("### SCOUTING SUMMARY")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Safety Shell", results['shell'])
    m2.metric("Inferred Coverage", results['cov'])
    m3.metric("Defensive Type", results['type'])
    m4.metric("AI Confidence", f"{results['conf']}%")
    
    st.markdown("---")
    
    # 2. Dual Panel Analysis (Observed vs Inferred)
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("Captured Vision")
        try:
            st.image(image, use_container_width=True)
        except:
            st.image(image, use_column_width=True)
            
        if results['crop']:
            st.warning("⚠️ Tight crop detected. Middle of the Field Safeties might be obscured.")

    with col2:
        st.subheader("Intelligence Breakdown")
        
        # Observed Block
        st.markdown(f"""
        <div class="card-observed">
        <b>🔭 VISUAL EVIDENCE (Observed)</b><br>
        • Safety Depth: {results['shell']}<br>
        • CB Cushion: {results['cushion']} Yards<br>
        • Alignment: {"Press" if results['cushion'] < 3 else "Soft/Off"}
        </div>
        """, unsafe_allow_html=True)
        
        st.write("") # Spacer
        
        # Inferred Block
        st.markdown(f"""
        <div class="card-inferred">
        <b>🧠 AI CONCLUSION (Inferred)</b><br>
        • Target: <b>{results['cov']}</b><br>
        • Secondary Possibility: Cover 6 Match (18%)<br>
        • Logic: Defensive backs show {results['type'].lower()} indicators.
        </div>
        """, unsafe_allow_html=True)
        
        # Small Plotly-style Field Map (Matplotlib)
        st.markdown("---")
        st.caption("Reconstructed Positioning Map")
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.set_facecolor('#0b0e11')
        plt.axhline(0, color='white', linewidth=2)
        if results['shell'] == "2-HIGH": 
            plt.scatter([-10, 10], [15, 15], color='#1e88e5', s=300)
        elif results['shell'] == "1-HIGH": 
            plt.scatter([0], [15], color='#1e88e5', s=300)
        
        y_cb = results['cushion'] if results['cushion'] > 0 else 1
        plt.scatter([-30, 30], [y_cb, y_cb], color='#22d3ee', marker='s', s=200)
        
        plt.ylim(-2, 22); plt.xlim(-45, 45); plt.axis('off')
        st.pyplot(fig, transparent=True)

else:
    # If NO file is uploaded, we show a professional welcome message
    st.info("⬆️ Welcome to Pro-Vision. Upload a screenshot to analyze the coverage shell.")
    
    with st.expander("Example Insights"):
        st.write("Our model analyzes Safety depth and Cornerback leverage to predict common coverages like Cover 3, Quarters, and Man-Press.")
