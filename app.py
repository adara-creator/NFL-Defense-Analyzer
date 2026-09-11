import streamlit as st
import numpy as np
from PIL import Image, ImageDraw
from streamlit_image_coordinates import streamlit_image_coordinates

from detection import get_detector
from team_split import split_teams
from calibration import compute_homography, default_field_points, boxes_to_field_positions, CalibrationError
from formation import Player, classify_roles, classify_formation

THEME_DARK = "#0b0d0e"
ROLE_COLORS = {
    "OL": "#6b7280", "QB": "#facc15", "RB": "#f97316",
    "TE": "#22c55e", "WR": "#38bdf8", "UNKNOWN": "#ef4444",
    "DEF": "#a855f7",
}

st.set_page_config(page_title="PRO-VISION // COMMAND STATION", layout="wide")
st.markdown(f"<style>.main {{ background-color: {THEME_DARK}; color: #f8fafc; }}</style>",
            unsafe_allow_html=True)

st.title("PRO-VISION")
st.caption("Real player detection → field calibration → offensive formation")

if "calib_points" not in st.session_state:
    st.session_state.calib_points = []
if "uploaded_key" not in st.session_state:
    st.session_state.uploaded_key = None

with st.sidebar:
    backend = st.selectbox("Detection backend", ["hog", "yolo"],
                            help="hog = no extra deps. yolo = needs `pip install ultralytics`.")
    f = st.file_uploader("Upload pre-snap photo", type=["jpg", "jpeg", "png"])
    if st.button("Reset calibration points"):
        st.session_state.calib_points = []

if not f:
    st.info("Upload a pre-snap photo to begin.")
    st.stop()

# Reset calibration if a new file is uploaded
if st.session_state.uploaded_key != f.name:
    st.session_state.calib_points = []
    st.session_state.uploaded_key = f.name

image = Image.open(f).convert("RGB")

# ============================================================
# STEP 1: Calibration — 4 clicks required before anything else
# ============================================================
st.subheader("Step 1: Calibrate the field")
st.write(
    "Click 4 points on the photo, in this exact order: "
    "**(1) left hash at the line of scrimmage, (2) right hash at the line "
    "of scrimmage, (3) left hash 5 yards downfield, (4) right hash 5 yards "
    "downfield.** If hashes aren't visible, use any 4 points whose real "
    "yard positions you know, and adjust `field_points` in code accordingly."
)

n_clicked = len(st.session_state.calib_points)
st.write(f"Points clicked: {n_clicked}/4")

if n_clicked < 4:
    coords = streamlit_image_coordinates(image, key="calib_click")
    if coords is not None:
        pt = (coords["x"], coords["y"])
        if pt not in st.session_state.calib_points:
            st.session_state.calib_points.append(pt)
            st.rerun()
else:
    # show the image with the 4 chosen points marked, for confirmation
    preview = image.copy()
    draw = ImageDraw.Draw(preview)
    for i, (x, y) in enumerate(st.session_state.calib_points):
        draw.ellipse([x - 6, y - 6, x + 6, y + 6], outline="#facc15", width=3)
        draw.text((x + 8, y - 8), str(i + 1), fill="#facc15")
    st.image(preview, use_container_width=True,
              caption="Calibration points (reset in sidebar if these look wrong)")

if n_clicked < 4:
    st.stop()  # do not proceed with detection/formation until calibrated

# ============================================================
# STEP 2: Homography
# ============================================================
try:
    H = compute_homography(st.session_state.calib_points, default_field_points())
except CalibrationError as e:
    st.error(f"Calibration failed: {e}")
    st.button("Reset and try again", on_click=lambda: st.session_state.update(calib_points=[]))
    st.stop()

# ============================================================
# STEP 3: Detection
# ============================================================
st.subheader("Step 2: Detected players")
with st.spinner("Detecting players..."):
    try:
        detector = get_detector(backend)
        detections = detector.detect(image)
    except ImportError as e:
        st.error(f"Backend '{backend}' isn't installed: {e}")
        st.stop()

boxes = [d["box"] for d in detections]

if len(boxes) < 10:
    st.warning(
        f"Only {len(boxes)} players detected (expected ~22 total on the "
        f"field). Formation results below will likely be incomplete or "
        f"wrong — this is a detection problem, not a formation-logic "
        f"problem. Try the YOLO backend if using HOG."
    )

if len(boxes) == 0:
    st.stop()

# ============================================================
# STEP 4: Team split (offense vs defense) using color + field depth
# ============================================================
labels, team_colors = split_teams(image, boxes)
field_positions = boxes_to_field_positions(H, boxes)

# Decide which color-cluster is offense: offense is behind the LOS (y<0)
# on average. This uses the calibration, not just color, to disambiguate.
avg_y_by_label = {}
for lbl in set(labels):
    ys = [fp[1] for fp, l in zip(field_positions, labels) if l == lbl]
    avg_y_by_label[lbl] = sum(ys) / len(ys) if ys else 0
offense_label = min(avg_y_by_label, key=avg_y_by_label.get)  # most negative y

# ============================================================
# STEP 5: Role classification + formation (offense only)
# ============================================================
offense_players = []
for i, ((x, y, w, h), (fx, fy), lbl) in enumerate(zip(boxes, field_positions, labels)):
    if lbl == offense_label:
        offense_players.append(Player(id=f"O{i}", x=fx, y=fy))

roles = classify_roles(offense_players) if offense_players else {}
formation = classify_formation(offense_players, roles) if offense_players else None

# ============================================================
# DISPLAY
# ============================================================
draw_img = image.copy()
draw = ImageDraw.Draw(draw_img)
for i, ((x, y, w, h), lbl) in enumerate(zip(boxes, labels)):
    pid = f"O{i}"
    if lbl == offense_label and pid in roles:
        role = roles[pid]
        color = ROLE_COLORS.get(role, "#ffffff")
        text = role
    else:
        color = ROLE_COLORS["DEF"]
        text = "DEF"
    draw.rectangle([x, y, x + w, y + h], outline=color, width=3)
    draw.text((x, y - 12), text, fill=color)

st.image(draw_img, use_container_width=True,
          caption="Detected players — colored by role (offense) or purple (defense)")

if formation:
    st.subheader("Step 3: Offensive formation")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Personnel", formation["personnel"])
    c2.metric("Backfield", formation["backfield_set"])
    c3.metric("Grouping", formation["grouping"])
    c4.metric("Split L/R", f"{formation['receiver_split']['left']}/{formation['receiver_split']['right']}")

    unknown_count = list(roles.values()).count("UNKNOWN")
    if unknown_count > 0:
        st.warning(f"{unknown_count} offensive player(s) could not be confidently role-classified (shown as UNKNOWN).")
    if formation["notes"]:
        for note in formation["notes"]:
            st.caption(f"⚠️ {note}")

    with st.expander("Raw measured data (for debugging/verification)"):
        st.write("Field positions (yards from center, yards from LOS):")
        st.json({p.id: {"x": round(p.x, 2), "y": round(p.y, 2), "role": roles.get(p.id)} for p in offense_players})
else:
    st.info("No offensive players identified — check team split / calibration.")
