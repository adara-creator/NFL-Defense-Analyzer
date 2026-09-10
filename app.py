import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import random
import time

# --- APP CONFIG & THEME ---
st.set_page_config(page_title="NFL Defensive Analyzer", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; color: #ffffff; }
    .stTabs [data-baseweb='tab-list'] { gap: 24px; }
    .stTabs [data-baseweb='tab'] { height: 50px; background-color: #1a1c23; border-radius: 5px; padding: 0 20px; color: white; }
    .stMetric { background-color: #1a1c23; border: 1px solid #3e4451; padding: 15px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- DATA STRUCTURES & MOCK LOGIC ---
if 'processed' not in st.session_state:
    st.session_state.processed = False
if 'results' not in st.session_state:
    st.session_state.results = None

def run_analysis(image):
    time.sleep(1.2)
    safeties_detected = random.choice([0, 1, 2])
    cb_dist = random.randint(1, 10)
    box_count = random.randint(5, 8)
    
    shell = f"{safeties_detected}-HIGH"
    if safeties_detected == 2:
        family, specific = "2-High", "Cover 4" if cb_dist > 5 else "Cover 2"
        man_zone, confidence = "ZONE" if cb_dist > 5 else "MAN", 0.84
    elif safeties_detected == 1:
        family, specific = "1-High", "Cover 3" if cb_dist > 4 else "Cover 1"
        man_zone, confidence = "ZONE" if cb_dist > 4 else "MAN", 0.76
    else:
        family, specific, man_zone, confidence = "0-High", "Cover 0", "MAN", 0.92

    return {
        "observed": {"safety_count": safeties_detected, "shell": shell, "cb_dist": cb_dist, "box_count": box_count},
        "inferred": {"family": family, "coverage": specific, "man_zone": man_zone, "confidence": confidence, "logic": "Visual alignment suggests depth-based coverage."}
    }

st.title("🏈 NFL Defensive Coverage Analyzer")

with st.sidebar:
    st.header("INPUT CENTER")
    uploaded_file = st.file_uploader("Upload Play Frame", type=['jpg', 'jpeg', 'png'])
    if st.button("ANALYZE DEFENSE", type="primary"):
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.session_state.results = run_analysis(image)
            st.session_state.processed = True

if st.session_state.processed:
    res = st.session_state.results
    obs, inf = res['observed'], res['inferred']
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("SAFETY SHELL", obs['shell'])
    m2.metric("MAN/ZONE", inf['man_zone'])
    m3.metric("LIKELY COVERAGE", inf['coverage'])
    m4.metric("CONFIDENCE", f"{int(inf['confidence']*100)}%")

    tab1, tab2 = st.tabs(["📊 Intelligence Report", "📍 Alignment Map"])
    with tab1:
        colA, colB = st.columns([1.2, 1])
        with colA:
            # FIX: Ensure use_container_width is used here to prevent the crash
            st.image(Image.open(uploaded_file), caption="Uploaded Play View", use_container_width=True)
        with colB:
            st.markdown(f"### Results: {inf['coverage']}")
            st.write(f"**Logic:** {inf['logic']}")
            st.write(f"**Technique:** {inf['family']}")
    with tab2:
        fig, ax = plt.subplots(figsize=(10, 4.5))
        ax.set_facecolor('#1b4332')
        plt.axhline(0, color='white', linewidth=3)
        plt.scatter(np.linspace(-10, 10, obs['box_count']), [1.5]*obs['box_count'], color='red', s=200)
        plt.ylim(-2, 22); plt.xlim(-45, 45); plt.axis('off')
        st.pyplot(fig)
else:
    st.info("👋 Upload a screenshot to begin the analysis.")
