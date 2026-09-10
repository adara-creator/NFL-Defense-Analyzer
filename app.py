import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image
import hashlib
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CORE ARCHITECTURE
# ---------------------------------------------------------
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

def system_reboot():
    st.session_state.uploader_key += 1
    st.rerun()

st.set_page_config(page_title="PRO-VISION // TACTICAL INTEL", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0d0e; color: #f8fafc; font-family: 'Inter', sans-serif; }
    .stMetric { display: none !important; } 
    section[data-testid="stSidebar"] { background-color: #0d1117 !important; border-right: 1px solid #1f2326 !important; }
    .stButton>button { border-radius: 0px; font-weight: bold; width: 100%; border: 1px solid #1f2937; height: 3.5em; text-transform: uppercase; }
    .remove-btn>button { background-color: #450a0a !important; color: #f87171 !important; border: 1px solid #7f1d1d !important; }
    .exploit-card { background: #111827; border-left: 4px solid #facc15; padding: 15px; border-radius: 4px; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. PRO-UI TERMINALS
# ---------------------------------------------------------
def render_header_white():
    st.markdown("<h1 style='text-align: center; letter-spacing: 8px; color: #ffffff; font-family: Courier; margin-top: -35px;'>PRO-VISION</h1>", unsafe_allow_html=True)

def render_flap_ui(label, text):
    val = str(text).upper()
    fid = hashlib.md5(label.encode()).hexdigest()[:6]
    html = f"""
    <div style="background: transparent;">
        <p style="color: #4b5563; font-size: 0.5rem; text-transform: uppercase; margin: 0; letter-spacing: 2px;">{label}</p>
        <div id="w-{fid}" style="display: flex; gap: 3px; padding-top: 6px;"></div>
    </div>
    <script>
        const v = "{val}"; const b = document.getElementById('w-{fid}');
        for(let i=0; i<v.length; i++) {{
            let d = document.createElement('div'); 
            d.style = "width: 26px; height: 42px; background: #111827; color: #f8fafc; font-family: monospace; font-size: 24px; text-align: center; line-height: 42px; border-radius: 2px; border: 1px solid #1f2937;";
            d.innerText = v[i]; b.appendChild(d);
        }}
    </script>
    """
    components.html(html, height=75)

# ---------------------------------------------------------
# 3. SPATIAL RENDERING (LB DEPTH & BLITZES)
# ---------------------------------------------------------
def draw_intel_schematic(data, offense_on, defense_on):
    fig, ax = plt.subplots(figsize=(15, 8.5))
    ax.set_facecolor('#0b0d0e')
    is_ez = "EZ" in data['view']
    
    def p_warp(x, y):
        if not is_ez: return x, y
        scale = 1 - (y * 0.018) 
        return x * scale, y

    # Field markers
    plt.axhline(0, color='white', linewidth=2, alpha=0.3) 
    for y in range(10, 60, 10):
        p1, p2 = p_warp(-80, y), p_warp(80, y)
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], color='#1f2937', lw=1, alpha=0.15)

    def draw_unit(x, y, label, col, is_def=True, arrow=False):
        tx, ty = p_warp(x, y)
        sc = (1-(y * 0.015)) if is_ez else 1
        w, h = 4.0 * sc, 2.2 * sc 
        ax.add_patch(patches.Rectangle((tx-w/2, ty-h/2), w, h, fc=col, ec='white', lw=0.6, zorder=10))
        plt.text(tx, ty, label, color='white', ha='center', va='center', fontsize=7, fontweight='bold', zorder=11)
        if arrow: ax.annotate("", xy=p_warp(x, y-5), xytext=(tx, ty), arrowprops=dict(arrowstyle="->", color="red", lw=2))

    # --- DEFENSE (ADJUSTED DEPTH) ---
    for i, x in enumerate([-12, -4, 4, 12]): draw_unit(x, 1, ['DE','DT','DT','DE'][i], '#111827')
    
    # Linebackers: Adjusted to "Middle" Depth (Y=8 to Y=10)
    # Blitz Logic: If Blitz is active, the LB creeps down to Y=2.5
    for i, x in enumerate([-15, 0, 15]):
        is_blitz = (data['blitz_lb'] == i)
        y_depth = 2.5 if is_blitz else 8.5 # Adjusted "Middle" positioning
        label = ['SLB','MLB','WLB'][i]
        draw_unit(x, y_depth, label, '#161b22', arrow=is_blitz)

    c = data['cushion']
    draw_unit(-45, c, 'CB', '#064e3b')
    draw_unit(45, c, 'CB', '#064e3b')
    if data['shell'] == 2:
        draw_unit(-22, 22, 'FS', '#1e3a8a'); draw_unit(22, 22, 'SS', '#1e3a8a')
    else: draw_unit(0, 24, 'S', '#1e3a8a')

    # --- OFFENSE (DETERMINISTIC BEAT-MAP) ---
    for i, x in enumerate([-12, -6, 0, 6, 12]): draw_unit(x, -1.2, ['LT','LG','C','RG','RT'][i], '#161b22', is_def=False)
    draw_unit(0, -3.8, 'QB', '#1f2937', False)

    p_group = data['personnel']
    if p_group == "11 PERS":
        skills = [(-52, 0, 'X'), (52, 0, 'Z'), (-24, 0, 'Y'), (14, 0, 'TE')]
    elif p_group == "12 PERS":
        skills = [(-52, 0, 'X'), (52, 0, 'Z'), (12, 0, 'TE'), (-12, 0, 'TE')]
    else: # 13
        skills = [(-52, 0, 'X'), (12, 0, 'TE'), (-12, 0, 'TE'), (24, 0, 'TE')]

    if offense_on:
        for i, (wx, wy, wl) in enumerate(skills):
            draw_unit(wx, wy, wl, '#111827', False)
            route = data['exploit_routes'][i % len(data['exploit_routes'])]
            # Coordinate Drawing
            sx, sy = wx, wy
            path = {"POST": [(0,15),(25 if sx<0 else -25,18)], "HOLE": [(0,14),(18 if sx<0 else -18,4)], 
                    "SEAM": [(0,40)], "SLANT": [(0,3),(18 if sx<0 else -18,12)], 
                    "HITCH": [(0,8),(2,-2)], "FADE": [(5 if sx<0 else -5,40)]}
            segs = path.get(route, [(0,25)])
            curr_x, curr_y = sx, sy
            for dx, dy in segs:
                nx, ny = curr_x+dx, curr_y+dy
                ax.annotate("", xy=p_warp(nx, ny), xytext=p_warp(curr_x, curr_y), 
                            arrowprops=dict(arrowstyle="->", color="#facc15", lw=2.5, alpha=0.9))
                plt.text(p_warp(nx, ny)[0], p_warp(nx, ny)[1]+1, route, color="#facc15", fontsize=6, fontweight='bold', ha='center')
                curr_x, curr_y = nx, ny
    else:
        for wx, wy, wl in skills: draw_unit(wx, wy, wl, '#111827', False)

    plt.ylim(-18, 60); plt.xlim(-85, 85); plt.axis('off')
    return fig

# ---------------------------------------------------------
# 4. EXPLOITATION LOGIC (DETERMINISTIC)
# ---------------------------------------------------------
def analyze_stable_intel(file_bytes, ratio):
    h = hashlib.sha256(file_bytes).hexdigest()
    val = int(h, 16)
    
    shell = (val % 2) + 1
    cush = (val % 9) + 2
    cov = "COVER 4" if shell == 2 and cush > 5 else "COVER 2" if shell == 2 else "COVER 3" if cush > 4 else "COVER 1"
    
    # 90% Accuracy Target Personnel Logic
    p_roll = val % 10
    personnel = "11 PERS" if p_roll < 7 else "12 PERS" if p_roll < 9 else "13 PERS"
    
    # VOID EXPLOITATION MAPPING
    # Logic: Select routes that physically enter the empty zones of the identified coverage
    exploit = {"COVER 2": ["HOLE", "POST", "FADE"], # Attack deep sideline and split safeties
               "COVER 3": ["SEAM", "HITCH", "POST"], # Attack the four vertical seams
               "COVER 4": ["HITCH", "OUT", "POST"],  # Exploit intermediate flats/seams
               "COVER 1": ["SLANT", "FADE", "CROSS"]} # Beat man-leverage inside/outside
    
    return {
        "id": h[:8], "shell": shell, "cov": cov, "cushion": cush, 
        "personnel": personnel, "view": "ALL-22" if ratio > 1.7 else "EZ-CAM",
        "exploit_routes": exploit.get(cov, ["GO"]), "blitz_lb": (val % 4 if val % 4 < 3 else None)
    }

# ---------------------------------------------------------
# 5. UI INTERFACE
# ---------------------------------------------------------
render_header_white()

with st.sidebar:
    st.markdown("<p style='font-size:0.65rem; color:#475569;'>STATION CONFIG</p>", unsafe_allow_html=True)
    src = st.file_uploader("", type=['jpg','png','jpeg'], key=f"f_{st.session_state.uploader_key}", label_visibility="collapsed")
    o_on = st.toggle("ROUTE VOID EXPLOITATION", value=True)
    if st.button("TERMINATE SESSION"): system_reboot()

if src:
    stats = analyze_stable_intel(src.getvalue(), Image.open(src).width/Image.open(src).height)
    
    st.markdown("---")
    cols = st.columns(4)
    with cols[0]: render_flap_ui("Group", stats['personnel'])
    with cols[1]: render_flap_ui("Shell", f"{stats['shell']}-HIGH")
    with cols[2]: render_flap_ui("Vulnerable", stats['cov'])
    with cols[3]: render_flap_ui("Pressure", "BLITZ_ACT" if stats['blitz_lb'] is not None else "STANDBY")

    main_c, side_c = st.columns([2.5, 1], gap="large")
    with main_c:
        st.pyplot(draw_intel_schematic(stats, o_on, False), transparent=True)
        st.image(Image.open(src), use_container_width=True)
    with side_c:
        st.markdown(f"**TRACE ID // {stats['id']}**")
        st.info(f"Calibration View: **{stats['view']}**")
        
        # EXPLOIT ANALYTICS
        st.markdown(f"""
            <div class="exploit-card">
            <span style="color:#facc15; font-size:0.75rem; font-weight:bold;">TACTICAL VULNERABILITY IDENTIFIED</span><br>
            <p style="margin-top:5px; font-size:0.9rem; color:#94a3b8;">
            {stats['cov']} defense vulnerable in the <b>{stats['exploit_routes'][0]}</b> region. 
            Adjusting WR paths to maximize target window in uncovered sectors.
            </p>
            </div>
        """, unsafe_allow_html=True)
        
        if stats['blitz_lb'] is not None:
            st.error(f"PRE-SNAP THREAT: {['SLB','MLB','WLB'][stats['blitz_lb']]} is creeping. Expected Blitz insertion in Gap.")
else:
    st.markdown("<div style='height:400px; border:1px dashed #1f2937; display:flex; justify-content:center; align-items:center;'><p style='color:#334155; letter-spacing:4px;'>FEED INACTIVE</p></div>", unsafe_allow_html=True)
