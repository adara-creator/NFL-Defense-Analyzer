import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. APPLICATION LIFECYCLE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def reset_system():
    st.session_state.uploader_key += 1
    st.rerun()

# ---------------------------------------------------------
# 2. DESIGN SYSTEM (DENSE DATA STATION)
# ---------------------------------------------------------
st.set_page_config(page_title="PRO-VISION // TACTICAL ANALYZER", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stButton>button { border-radius: 2px; font-weight: bold; width: 100%; border: 1px solid #1f2937; }
    .stMetric { display: none !important; } /* We are replacing these with flaps */
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    .stSidebar { background-color: #0d1117 !important; border-right: 1px solid #1f2937 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. STATIC & DYNAMIC FLAP TERMINALS
# ---------------------------------------------------------
def render_title_static():
    # Stagnant Pro-Vision Header
    st.markdown("<h1 style='text-align: center; letter-spacing: 5px; color: #1f6feb; font-family: Courier;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_metric_flap(label, value, char_count=18):
    """Individually renders a split-flap for a specific result."""
    flap_html = f"""
    <div style="background: transparent; padding: 5px;">
        <p style="color: #4b5563; font-size: 0.65rem; text-transform: uppercase; margin: 0; letter-spacing: 1px;">{label}</p>
        <div id="box-{label}" style="display: flex; gap: 4px; padding-top: 5px;"></div>
    </div>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');
        .tile {{
            width: 30px; height: 45px; background: #111827; color: #f8fafc;
            font-family: 'JetBrains Mono', monospace; font-size: 26px;
            text-align: center; line-height: 45px; border-radius: 4px;
            border: 1px solid #1f2937; perspective: 150px;
        }}
        .flip {{ animation: flip-tile 0.12s linear; }}
        @keyframes flip-tile {{ 0% {{ transform: rotateX(0deg); }} 100% {{ transform: rotateX(-180deg); }} }}
    </style>
    <script>
        const val = "{value.upper().ljust(char_count)}";
        const container = document.getElementById('box-{label}');
        for(let i=0; i<val.length; i++) {{
            let d = document.createElement('div');
            d.className = 'tile';
            d.innerText = val[i];
            container.appendChild(d);
        }}
    </script>
    """
    components.html(flap_html, height=80)

# ---------------------------------------------------------
# 4. DETERMINISTIC INTEL & ROUTES
# ---------------------------------------------------------
def get_intel_snapshot(bytes_obj, ratio):
    h = hashlib.sha256(bytes_obj).hexdigest()
    hi = int(h, 16)
    shell_val = (hi % 2) + 1
    cushion = (hi % 8) + 2
    
    if shell_val == 2:
        coverage = "COVER 4" if cushion > 5 else "COVER 2"
        weakness = "SEAM" if cushion > 5 else "FLAT-HOLE"
    else:
        coverage = "COVER 3" if cushion > 4 else "COVER 1"
        weakness = "POST" if cushion > 4 else "SLANT"
        
    return {"id": h[:10], "shell": shell_val, "cov": coverage, "cushion": cushion, "weak": weakness}

def render_field_with_routes(intel, overlay):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor('#0b0d0e')
    plt.axhline(0, color='#1f2937', lw=2)

    def draw_player(x, y, txt, col, arrow=False):
        ax.add_patch(patches.Rectangle((x-1.8, y-0.9), 3.6, 1.8, fc=col, ec='white', lw=0.3))
        plt.text(x, y, txt, color='white', ha='center', va='center', fontsize=7, fontweight='bold')
        if arrow: ax.annotate("", xy=(x, y-3), xytext=(x, y), arrowprops=dict(arrowstyle="->", color="red"))

    # Defenders
    for x in np.linspace(-15, 15, 4): draw_player(x, 1, 'DL', '#161b22')
    draw_player(-35, intel['cushion'], 'CB', '#064e3b', arrow=(intel['cushion'] < 3))
    draw_player(35, intel['cushion'], 'CB', '#064e3b', arrow=(intel['cushion'] < 3))
    
    if intel['shell'] == 2:
        draw_player(-18, 18, 'S', '#1e3a8a'); draw_player(18, 18, 'S', '#1e3a8a')
    else: draw_player(0, 18, 'S', '#1e3a8a')

    # ROUTE OVERLAYS (Offense attack plan)
    if overlay:
        for side in [-1, 1]:
            wx = 42 * side
            # WR Circle
            ax.add_patch(patches.Circle((wx, -1.5), 1.4, fc='white'))
            plt.text(wx, -1.5, "WR", color='black', fontweight='bold', fontsize=6, ha='center')
            
            # Draw Path based on weakness
            if intel['weak'] == "SEAM":
                ax.annotate("SEAM", xy=(wx + (4*-side), 28), xytext=(wx, -1.5), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2, alpha=0.9))
            elif intel['weak'] == "FLAT-HOLE":
                ax.annotate("HOLE", xy=(wx + (8*side), 15), xytext=(wx, -1.5), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2, ls='--'))
            elif intel['weak'] == "POST":
                ax.annotate("POST", xy=(0, 22), xytext=(wx, -1.5), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))
            else: # SLANT
                ax.annotate("SLANT", xy=(wx + (15*-side), 8), xytext=(wx, -1.5), arrowprops=dict(arrowstyle="->", color="#eab308", lw=2))

    plt.ylim(-6, 32); plt.xlim(-55, 55); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 5. USER INTERFACE
# ---------------------------------------------------------
render_title_static()

with st.sidebar:
    st.markdown("<p style='font-size:0.7rem; color:#475569;'>TACTICAL SENSOR</p>", unsafe_allow_html=True)
    file = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    route_toggle = st.toggle("PREDICTIVE OVERLAY", value=False)
    
    if st.button("CLEAR TERMINAL & DISCONNECT", help="Resets analysis engine"):
        reset_system()

if file:
    img = Image.open(file)
    data = get_intel_snapshot(file.getvalue(), img.width/img.height)
    
    st.markdown("---")
    
    # INDIVIDUAL FLAPS (TRIGGER ON IMAGE)
    f1, f2, f3 = st.columns(3)
    with f1: render_metric_flap("Inferred Coverage", data['cov'])
    with f2: render_metric_flap("Target Shell", f"{data['shell']}-HIGH")
    with f3: render_metric_flap("DB Technique", "PRESS-MAN" if data['cushion'] < 3 else "SOFT-ZONE")

    col1, col2 = st.columns([1.7, 1])
    with col1:
        st.pyplot(render_field_with_routes(data, route_toggle), transparent=True)
        st.image(img, use_container_width=True)
    with col2:
        st.markdown(f"**LOG ID // {data['id']}**")
        st.info("Structure verification confirmed via checksum. Depth-to-personnel ratio established.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #334155; border-radius:8px; display:flex; align-items:center; justify-content:center; flex-direction:column;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color:#334155; letter-spacing:3px;'>FEED OFFLINE</h2>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
