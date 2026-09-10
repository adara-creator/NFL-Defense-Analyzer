import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. APPLICATION PERSISTENCE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def trigger_reset():
    st.session_state.uploader_key += 1
    st.rerun()

# ---------------------------------------------------------
# 2. DESIGN ARCHITECTURE
# ---------------------------------------------------------
st.set_page_config(page_title="PRO-VISION // TACTICAL ANALYZER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stMetric { display: none !important; } 
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; }
    .stButton>button { border-radius: 2px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.5em; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. ELASTIC SPLIT-FLAP TERMINAL (DYNAMIC BOXES)
# ---------------------------------------------------------
def render_header_static():
    st.markdown("<h1 style='text-align: center; letter-spacing: 5px; color: #ffffff; font-family: Courier; margin-top: -20px;'>PRO-VISION</h1>", u
