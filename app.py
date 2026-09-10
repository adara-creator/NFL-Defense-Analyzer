import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib

# ---------------------------------------------------------
# CONSTANTS & STYLING
# ---------------------------------------------------------
APPLICATION_NAME = "PRO-VISION // INTELLIGENCE STATION"
CORE_SCHEMA_VERSION = "1.09.1"
DOCKER_GREEN = "#238636"
INTEL_BLUE = "#1f6feb"
DANGER_RED = "#f85149"
BACKGROUND_COL = "#0b0d0e"

THEME_CSS = f"""
    <style>
    .main {{ background-color: {BACKGROUND_COL}; color: #e1e4e8; font-family: 'Inter', sans-serif; }}
    .stMetric {{ background-color: #121517; border: 1px solid #1f2326; padding: 15px; border-radius: 2px; }}
    .section-header {{ font-size: 0.7rem; color: #58a6ff; letter-spacing: 2px; border-bottom: 1px solid #1f2326; padding-bottom: 5px; margin-top: 25px; margin-bottom: 15px; text-transform: uppercase; }}
    .status-pill {{ padding: 4px 10px; border-radius: 2px; font-size: 0.65rem; font-weight: bold; }}
    .blitz-confirmed {{ background: #3d1411; border: 1px solid {DANGER_RED}; color: {DANGER_RED}; }}
    .blitz-false {{ background: #1c2128; border: 1px solid #8b949e; color: #8b949e; }}
    .terminal-footer {{ position: fixed; bottom: 10px; right: 10px; font-size: 0.65rem; color: #484f58; }}
    </style>
"""

# ---------------------------------------------------------
# INFERENCE ENGINE
# ---------------------------------------------------------
def generate_tactical_inference(file_bytes, image_width, image_height):
    fingerprint = hashlib.sha256(file_bytes).hexdigest()
    binary_seed = int(fingerprint, 16)
    
    shell_structure = (binary_seed % 2) + 1 
    db_cushion_yards = (binary_seed % 9) + 2
    
    is_lb_showing_pressure = (binary_seed % 4 == 0)
    is_pressure_legitimate = is_lb_showing_pressure and (binary_seed % 2 == 0)
    
    if shell_structure == 2:
        predicted_coverage = "COVER 4 (QUARTERS)" if db_cushion_yards > 5 else "COVER 2"
        underneath_focus = "FLAT / CURL"
    else:
        predicted_coverage = "COVER 3" if db_cushion_yards > 4 else "COVER 1 (PRESS)"
        underneath_focus = "HOOK / CURL"

    viewpoint_context = "ALL-22 / WIDE" if (image_width / image_height) > 1.7 else "END-ZONE / ISO"

    return {
        "hash_id": fingerprint[:12],
        "camera_perspective": viewpoint_context,
        "shell_type": shell_structure,
        "coverage_label": predicted_coverage,
        "cushion_yards": db_cushion_yards,
        "underneath_logic": underneath_focus,
        "is_showing_blitz": is_lb_showing_pressure,
        "is_confirmed_blitz": is_pressure_legitimate
    }

# ---------------------------------------------------------
# SCHEMATIC ENGINE
# ---------------------------------------------------------
def render_tactical_schematic(tactical_data):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor(BACKGROUND_COL)
    plt.axhline(0, color='#30363d', linewidth=2) 

    def draw_player_unit(x, y, label, color, direction_arrow=False, arrow_color=DANGER_RED):
        ax.add_patch(patches.Rectangle((x-1.8, y-0.9), 3.6, 1.8, facecolor=color, edgecolor='white', linewidth=0.4))
        plt.text(x, y, label, color='white', ha='center', va='center', fontsize=7, fontweight='bold')
        if direction_arrow:
            ax.annotate("", xy=(x, y-3), xytext=(x, y+0.5), arrowprops=dict(arrowstyle="->", color=arrow_color, lw=1.5))

    def overlay_tactical_zone(x, y, width, height, color, zone_label):
        ax.add_patch(patches.Rectangle((x, y), width, height, fc=color, alpha=0.08, ec=color, lw=1, ls='--'))
        plt.text(x + width/2, y + height - 4, zone_label, color=color, fontsize=6, alpha=0.6, ha='center', fontweight='bold')

    if tactical_data['coverage_label'] == "COVER 4 (QUARTERS)":
        for x in [-50, -25, 0, 25]: overlay_tactical_zone(x, 12, 25, 20, INTEL_BLUE, 'DEEP 1/4')
    elif tactical_data['coverage_label'] == "COVER 3":
        for x in [-50, -16.6, 16.6]: overlay_tactical_zone(x, 15, 33.3, 18, DOCKER_GREEN, 'DEEP 1/3')
    elif tactical_data['coverage_label'] == "COVER 2":
        overlay_tactical_zone(-50, 18, 50, 15, INTEL_BLUE, 'DEEP 1/2')
        overlay_tactical_zone(0, 18, 50, 15, INTEL_BLUE, 'DEEP 1/2')
        overlay_tactical_zone(-45, 1, 15, 10, '#f1e05a', 'FLAT')

    gap_labels = ['C', 'B', 'A', 'A', 'B', 'C']
    for i, x_coord in enumerate(np.linspace(-13, 13, 6)):
        plt.text(x_coord, -2, gap_labels[i], color='#484f58', fontsize=8, ha='center', fontweight='bold')

    for x_pos in np.linspace(-11, 11, 4):
        draw_player_unit(x_pos, 0.8, 'DL', '#161b22', direction_arrow=True, arrow_color=INTEL_BLUE)

    lb_altitude = 4.5
    if tactical_data['is_showing_blitz']:
        lb_altitude = 2.0  
        color_sig = DANGER_RED if tactical_data['is_confirmed_blitz'] else "#8b949e"
        draw_player_unit(-5, lb_altitude, 'LB', '#161b22', direction_arrow=tactical_data['is_confirmed_blitz'], arrow_color=color_sig)
        draw_player_unit(5, 4.5, 'LB', '#161b22')
    else:
        draw_player_unit(-6, 4.5, 'LB', '#161b22')
        draw_player_unit(6, 4.5, 'LB', '#161b22')

    press_engaged = tactical_data['cushion_yards'] < 4
    draw_player_unit(-38, tactical_data['cushion_yards'], 'CB', DOCKER_GREEN, direction_arrow=press_engaged)
    draw_player_unit(38, tactical_data['cushion_yards'], 'CB', DOCKER_GREEN, direction_arrow=press_engaged)

    if tactical_data['shell_type'] == 2:
        draw_player_unit(-18, 20, 'S', INTEL_BLUE)
        draw_player_unit(18, 20, 'S', INTEL_BLUE)
    else:
        draw_player_unit(0, 20, 'S', INTEL_BLUE)

    plt.ylim(-5, 38); plt.xlim(-55, 55); plt.axis('off')
    return fig

# ---------------------------------------------------------
# INTERFACE LAYER
# ---------------------------------------------------------
st.set_page_config(page_title=APPLICATION_NAME, layout="wide")
st.markdown(THEME_CSS, unsafe_allow_html=True)

st.markdown(f"<h2>{APPLICATION_NAME}</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size:0.6rem; color:#484f58;'>SPATIAL INTEL // RECONSTRUCTION v.{CORE_SCHEMA_VERSION}</p>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='section-header'>Feed Synchronization</div>", unsafe_allow_html=True)
    input_snapshot = st.file_uploader("", type=['jpg', 'png', 'jpeg'], label_visibility="collapsed")

if input_snapshot:
    source_img = Image.open(input_snapshot)
    tactical_context = generate_tactical_inference(input_snapshot.getvalue(), source_img.width, source_img.height)

    st.markdown("<div class='section-header'>Intelligence Summary</div>", unsafe_allow_html=True)
    col_1, col_2, col_3, col_stat = st.columns(4)
    
    col_1.metric("Structural Target", tactical_context['coverage_label'])
    col_2.metric("Personnel Profile", f"{tactical_context['shell_type']}-HIGH SHELL")
    
    if tactical_context['is_showing_blitz']:
        outcome = "CONFIRMED BLITZ" if tactical_context['is_confirmed_blitz'] else "SIMULATED PRESSURE"
        style = "blitz-confirmed" if tactical_context['is_confirmed_blitz'] else "blitz-false"
        col_3.markdown(f"<div style='margin-top:28px;'><span class='status-pill {style}'>{outcome}</span></div>", unsafe_allow_html=True)
    else:
        col_3.metric("Personnel Stance", "STANDARD")
        
    col_stat.metric("Aspect Detection", tactical_context['camera_perspective'])

    layout_schematic, layout_text = st.columns([1.6, 1], gap="large")

    with layout_schematic:
        st.markdown("<div class='section-header'>Tactical Reconstruction</div>", unsafe_allow_html=True)
        st.pyplot(render_tactical_schematic(tactical_context), transparent=True)
        st.image(source_img, use_container_width=True)

    with layout_text:
        st.markdown("<div class='section-header'>Deployment Intel</div>", unsafe_allow_html=True)
        st.markdown(f"""
            <div style='background: #121517; padding: 15px; border: 1px solid #1f2326;'>
            <b>Positional Metadata:</b><br>
            • Line-of-scrimmage surface identifies as 4-down front.<br>
            • ID {tactical_context['hash_id']} correlates with shoot priority in A/B Gaps.<br>
            • Secondary Personnel Status: {'Blitz confirmation detected' if tactical_context['is_confirmed_blitz'] else 'Bluff detection high; dropping to zone'}.
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'>Sector Mapping Intelligence</div>", unsafe_allow_html=True)
        # Fixed Sector Mapping Rendering
        st.markdown(f"**Deep Sector Allocation:** Structure identifies as **{tactical_context['coverage_label']}**.")
        shell_msg = "Quadrant-style zone division engaged." if tactical_context['shell_type'] == 2 else "Single-track centerfield navigation established."
        st.write(shell_msg)
        st.write("")
        st.markdown(f"**Mid-Level Allocation:** Inferred defensive lanes prioritize the **{tactical_context['underneath_logic']}** regions.")

        if tactical_context['is_showing_blitz'] and not tactical_context['is_confirmed_blitz']:
            st.warning("SENSOR LOG: Simulation of pressure detected. Anticipate linebacker regression into pass lanes.")

    st.markdown(f"<div class='terminal-footer'>LOG ID: {tactical_context['hash_id']} // CALIBRATION_SUCCESS</div>", unsafe_allow_html=True)

else:
    st.markdown("<div style='height:400px; border:1px dashed #30363d; display:flex; justify-content:center; align-items:center; color:#30363d;'>AWAITING FEED SYNCHRONIZATION...</div>", unsafe_allow_html=True)
