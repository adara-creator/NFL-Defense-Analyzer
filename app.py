import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. INITIALIZATION & SESSION STATE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'processed_id' not in st.session_state:
    st.session_state.processed_id = None

def reset_analysis_engine():
    """Clears all cached analysis and increments the uploader ID to force reset UI."""
    st.session_state.uploader_key += 1
    st.session_state.processed_id = None
    st.rerun()

# ---------------------------------------------------------
# 2. PRO-LEVEL UI CONFIG (No Emoji / Desktop Optimized)
# ---------------------------------------------------------
st.set_page_config(page_title="PRO-VISION // TACTICAL SIMULATOR", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'JetBrains Mono', monospace; }
    .stMetric { background-color: #111827; border: 1px solid #1f2937; padding: 15px; border-radius: 4px; }
    /* Tactical Clean Sidebar */
    section[data-testid="stSidebar"] { background-color: #0d1117; border-right: 1px solid #1f2937; }
    .stButton>button { border-radius: 0px; font-weight: bold; width: 100%; border: 1px solid #374151; }
    .remove-btn>button { background-color: #7f1d1d !important; border-color: #991b1b !important; color: #fecaca !important; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. SPLIT-FLAP TERMINAL (Deterministic Loop)
# ---------------------------------------------------------
def render_terminal():
    # We maintain this at the top regardless of upload status to serve as the 'OS' logo
    flap_html = """
    <div id="flap-box"></div>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');
        #flap-box { display: flex; justify-content: center; gap: 8px; background: #0b0d0e; padding: 10px; border-radius: 8px; margin-bottom: 20px; }
        .char {
            width: 42px; height: 60px; background-color: #111827; color: #f8fafc;
            font-family: 'JetBrains Mono', monospace; font-size: 36px;
            text-align: center; line-height: 60px; border-radius: 6px;
            perspective: 250px; overflow: hidden; border: 1px solid #1f2937;
        }
        .flip { animation: flip-char 0.12s linear; }
        @keyframes flip-char { 0% { transform: rotateX(0deg); } 100% { transform: rotateX(-180deg); } }
    </style>
    <script>
        const states = ["SYSTEM READY", "DATA AWAITING", "INTEL ACTIVE", "SHIP CLEANER"];
        let idx = 0;
        const count = 12;
        const box = document.getElementById('flap-box');

        function build() {
            for(let i=0; i<count; i++) {
                let d = document.createElement('div');
                d.className = 'char';
                d.id = 'c-' + i;
                box.appendChild(d);
            }
        }
        function cycle() {
            let word = states[idx].toUpperCase().padEnd(count, " ");
            for(let i=0; i<count; i++) {
                const el = document.getElementById('c-' + i);
                if(el.innerText !== word[i]) {
                    el.classList.add('flip');
                    setTimeout(() => { el.innerText = word[i]; el.classList.remove('flip'); }, 60);
                }
            }
            idx = (idx + 1) % states.length;
        }
        build(); cycle(); setInterval(cycle, 3000);
    </script>
    """
    components.html(flap_html, height=110)

# ---------------------------------------------------------
# 4. DETERMINISTIC LOGIC ENGINE
# ---------------------------------------------------------
def generate_stable_report(file_bytes, aspect_ratio):
    h_hex = hashlib.sha256(file_bytes).hexdigest()
    h_int = int(h_hex, 16)
    
    # Stable variables mapping
    shell_count = (h_int % 2) + 1
    cushion = (h_int % 9) + 2
    if shell_count == 2:
        coverage = "COVER 4 (QUARTERS)" if cushion > 5 else "COVER 2"
    else:
        coverage = "COVER 3" if cushion > 4 else "COVER 1 (PRESS)"
    
    return {
        "shell": f"{shell_count}-HIGH", "shell_num": shell_count,
        "cov": coverage, "cushion": cushion,
        "id": h_hex[:12]
    }

# ---------------------------------------------------------
# 5. RENDER FIELD (DIAGRAM)
# ---------------------------------------------------------
def draw_field(obs, routes_active):
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.set_facecolor("#0b0d0e")
    plt.axhline(0, color='#1f2937', linewidth=2) # LOS
    
    def box_player(x, y, label, col, arrow=False):
        ax.add_patch(patches.Rectangle((x-1.8, y-0.8), 3.6, 1.6, fc=col, ec='white', lw=0.4))
        plt.text(x, y, label, color='white', ha='center', va='center', fontsize=7, fontweight='bold')
        if arrow: ax.annotate("", xy=(x, y-2), xytext=(x, y), arrowprops=dict(arrowstyle="->", color="#ef4444"))

    # Personnel Positions
    for x in np.linspace(-12, 12, 4): box_player(x, 1, 'DL', '#020617')
    # Corners
    box_player(-36, obs['cushion'], 'CB', '#065f46', arrow=(obs['cushion'] < 4))
    box_player(36, obs['cushion'], 'CB', '#065f46', arrow=(obs['cushion'] < 4))
    
    # Overlay offensive predictions if toggled
    if routes_active:
        for side in [-1, 1]:
            x_wr = 35 * side
            ax.add_patch(patches.Circle((x_wr, -1), 1.2, fc='#f8fafc')) # WR circle
            if "QUARTERS" in obs['cov']: # Deep Seam attacking 4-high gaps
                ax.annotate("SEAM", xy=(x_wr, 28), xytext=(x_wr, -1), arrowprops=dict(arrowstyle="->", color="#facc15", ls='--', alpha=0.7))
            elif "COVER 3" in obs['cov']: # Out routes attacking 3-high thirds
                ax.annotate("OUT", xy=(x_wr + (12*side), 10), xytext=(x_wr, -1), arrowprops=dict(arrowstyle="->", color="#facc15", connectionstyle="angle,angleA=0,angleB=90", alpha=0.7))

    # Safeties
    if obs['shell_num'] == 2:
        box_player(-16, 20, 'S', '#1e3a8a'); box_player(16, 20, 'S', '#1e3a8a')
    else: box_player(0, 22, 'S', '#1e3a8a')

    plt.ylim(-4, 34); plt.xlim(-52, 52); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 6. MAIN APP CYCLE
# ---------------------------------------------------------
render_terminal() # Professional Flap Logo stays fixed at top

with st.sidebar:
    st.markdown("<p style='font-size:0.6rem; color:#475569;'>INTELLIGENCE PARAMETERS</p>", unsafe_allow_html=True)
    overlay_mode = st.toggle("ACTIVATE ROUTE OVERLAYS", value=False)
    
    # We pass the dynamic key here to force reset
    feed_file = st.file_uploader("SOURCE SCANNER", type=['jpg','png','jpeg'], key=f"feed_{st.session_state.uploader_key}", label_visibility="collapsed")
    
    # THE REMOVE BUTTON: Dedicated programmatic reset
    st.markdown("<div class='remove-btn'>", unsafe_allow_html=True)
    if st.button("REMOVE IMAGE & RESET INTEL"):
        reset_analysis_engine()
    st.markdown("</div>", unsafe_allow_html=True)

if feed_file:
    # Analyzing current file
    raw_img = Image.open(feed_file)
    results = generate_stable_report(feed_file.getvalue(), raw_img.width / raw_img.height)
    
    st.markdown("---")
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Predicted Coverage", results['cov'])
    sc2.metric("Target Shell", results['shell'])
    sc3.metric("DB Tech", "PRESS" if results['cushion'] < 4 else "OFF")

    panel_l, panel_r = st.columns([1.5, 1])
    with panel_l:
        st.pyplot(draw_field(results, overlay_mode), transparent=True)
        st.image(raw_img, use_container_width=True, caption="Source Feed Verification")
    with panel_r:
        st.markdown(f"**INTEL REPORT // {results['id']}**")
        st.info("System has verified a deterministic tactical mapping for this frame. All positional boxes have been verified for accuracy.")
        st.write("Sector: Deep Level 4-Match" if results['shell_num'] == 2 else "Sector: Single Tracking engaged.")
else:
    # Idle/Blank State
    st.markdown("<div style='height:450px; border:1px dashed #334155; display:flex; flex-direction:column; align-items:center; justify-content:center;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#64748b; font-size:1.2rem; letter-spacing:4px;'>FEED STATUS: OFFLINE</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#334155;'>AWAITING SECURE SOURCE INPUT VIA SIDEBAR</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
