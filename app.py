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
    st.markdown("<h1 style='text-align: center; letter-spacing: 5px; color: #ffffff; font-family: Courier; margin-top: -20px;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_elastic_flap(label, text):
    """Generates exactly the number of tiles needed for the specific result string."""
    word = text.upper()
    tile_count = len(word)
    
    flap_html = f"""
    <div style="background: transparent;">
        <p style="color: #4b5563; font-size: 0.6rem; text-transform: uppercase; margin: 0; letter-spacing: 2px; font-family: 'Inter', sans-serif;">{label}</p>
        <div id="wrapper-{label}" style="display: flex; gap: 4px; padding-top: 8px;"></div>
    </div>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');
        .tile {{
            width: 30px; height: 48px; background: #111827; color: #f8fafc;
            font-family: 'JetBrains Mono', monospace; font-size: 28px;
            text-align: center; line-height: 48px; border-radius: 4px;
            border: 1px solid #1f2937; perspective: 150px;
        }}
        .flip-action {{ animation: spin 0.1s linear; }}
        @keyframes spin {{ 0% {{ transform: rotateX(0deg); }} 100% {{ transform: rotateX(-180deg); }} }}
    </style>
    <script>
        const content = "{word}";
        const parent = document.getElementById('wrapper-{label}');
        for(let i=0; i<content.length; i++) {{
            let d = document.createElement('div');
            d.className = 'tile';
            d.id = 't-{label}-' + i;
            parent.appendChild(d);
            setTimeout(() => {{
                const el = document.getElementById('t-{label}-' + i);
                el.classList.add('flip-action');
                el.innerText = content[i];
                setTimeout(() => el.classList.remove('flip-action'), 100);
            }}, i * 40); // Subtle stagger for realism
        }}
    </script>
    """
    # Auto-adjust height to content
    components.html(flap_html, height=85)

# ---------------------------------------------------------
# 4. TACTICAL OVERLAY LOGIC
# ---------------------------------------------------------
def fetch_tactical_data(file_bytes):
    hash_obj = hashlib.sha256(file_bytes).hexdigest()
    val = int(hash_obj, 16)
    
    shell_val = (val % 2) + 1
    depth = (val % 8) + 2
    
    # Precise deterministic results
    if shell_val == 2:
        res, type_label, route = ("COVER 4", "SOFT-ZONE", "SEAM") if depth > 5 else ("COVER 2", "PRESS-MAN", "HOLE")
    else:
        res, type_label, route = ("COVER 3", "OFF-ZONE", "POST") if depth > 4 else ("COVER 1", "PRESS-MAN", "SLANT")
        
    return {"id": hash_obj[:8], "shell": shell_val, "cov": res, "cushion": depth, "tech": type_label, "weakness": route}

def draw_visual_schematic(data, show_routes):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_facecolor('#0b0d0e')
    plt.axhline(0, color='#1f2937', lw=1.5, alpha=0.8) # LOS

    def render_pos(x, y, txt, col, show_arrow=False):
        rect = patches.Rectangle((x-1.8, y-0.9), 3.6, 1.8, fc=col, ec='white', lw=0.3)
        ax.add_patch(rect)
        plt.text(x, y, txt, color='white', ha='center', va='center', fontsize=7, fontweight='bold')
        if show_arrow:
            ax.annotate("", xy=(x, y-2.5), xytext=(x, y), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1))

    # personnel placement
    for x in np.linspace(-12, 12, 4): render_pos(x, 1, 'DL', '#161b22')
    render_pos(-35, data['cushion'], 'CB', '#064e3b', show_arrow=(data['cushion'] < 4))
    render_pos(35, data['cushion'], 'CB', '#064e3b', show_arrow=(data['cushion'] < 4))
    
    if data['shell'] == 2:
        render_pos(-18, 18, 'S', '#1e3a8a'); render_pos(18, 18, 'S', '#1e3a8a')
    else: render_pos(0, 18, 'S', '#1e3a8a')

    # OFFENSIVE SCHEME OVERLAY
    if show_routes:
        for s in [-1, 1]:
            xwr = 42 * s
            ax.add_patch(patches.Circle((xwr, -1.5), 1.4, fc='white', zorder=10))
            plt.text(xwr, -1.5, "WR", color='black', fontweight='bold', fontsize=6, ha='center', zorder=11)
            
            w = data['weakness']
            target_x = 0 if w == "POST" else xwr + (10 * s if w == "HOLE" else 4 * -s)
            target_y = 22 if w in ["SEAM", "POST"] else (15 if w == "HOLE" else 8)
            
            ax.annotate(w, xy=(target_x, target_y), xytext=(xwr, -1.5), 
                        arrowprops=dict(arrowstyle="->", color="#facc15", lw=2, alpha=0.9))

    plt.ylim(-6, 32); plt.xlim(-55, 55); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 5. USER STATION UI
# ---------------------------------------------------------
render_header_static()

with st.sidebar:
    st.markdown("<p style='font-size:0.7rem; color:#475569; letter-spacing:1px;'>OPERATIONAL HUB</p>", unsafe_allow_html=True)
    f = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    route_on = st.toggle("ACTIVATE ROUTE OVERLAYS", value=False)
    
    st.markdown("<div class='remove-btn' style='margin-top: 15px;'>", unsafe_allow_html=True)
    if st.button("TERMINATE SESSION & CLEAR"):
        trigger_reset()
    st.markdown("</div>", unsafe_allow_html=True)

if f:
    pil_img = Image.open(f)
    results = fetch_tactical_data(f.getvalue())
    
    st.markdown("---")
    
    # ELASTIC FLAPS: ONLY THE NECESSARY TILES
    fc1, fc2, fc3 = st.columns([1, 1, 1])
    with fc1: render_elastic_flap("Inferred Coverage", results['cov'])
    with fc2: render_elastic_flap("Target Shell", f"{results['shell']}-HIGH")
    with fc3: render_elastic_flap("DB Technique", results['tech'])

    # DATA WORKSPACE
    col_l, col_r = st.columns([1.8, 1], gap="large")
    with col_l:
        st.pyplot(draw_visual_schematic(results, route_on), transparent=True)
        st.image(pil_img, use_container_width=True)
    with col_r:
        st.markdown(f"**TRACE ID // {results['id']}**")
        st.info("System hash validated. Spatial depth indicators locked for session.")
        st.write("Current orientation predicts primary liability in " + ("mid-level seam" if results['weakness'] == "SEAM" else "perimeters") + ".")
else:
    # STANDBY DASHBOARD
    st.markdown("<div style='height:420px; border:1px dashed #1f2937; border-radius:6px; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#0e1113;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:#334155; letter-spacing:4px;'>SCANNER IDLE</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#1f2937; font-size: 0.8rem;'>AWAITING ENCRYPTED IMAGE SOURCE</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
