import streamlit as st
import numpy as np
from PIL import Image, ImageDraw

from detection import get_detector
from team_split import split_teams

# ==========================================
# UI THEME (kept from original)
# ==========================================
THEME_DARK = "#0b0d0e"
TEAM_A_COLOR = "#ef4444"
TEAM_B_COLOR = "#1f6feb"

st.set_page_config(page_title="PRO-VISION // COMMAND STATION", layout="wide")
st.markdown(f"""
<style>
    .main {{ background-color: {THEME_DARK}; color: #f8fafc; }}
</style>
""", unsafe_allow_html=True)

st.title("PRO-VISION")
st.caption("Real player detection on uploaded pre-snap photos")

with st.sidebar:
    backend = st.selectbox(
        "Detection backend",
        ["hog", "yolo"],
        help="hog = no extra deps, weaker on packed players. "
             "yolo = needs `pip install ultralytics`, much better on occlusion."
    )
    conf_note = st.caption(
        "HOG has no confidence threshold slider yet (fixed hitThreshold=0). "
        "YOLO backend supports `conf` in code."
    )
    f = st.file_uploader("Upload pre-snap photo", type=["jpg", "jpeg", "png"])

if f:
    image = Image.open(f).convert("RGB")

    with st.spinner("Detecting players..."):
        try:
            detector = get_detector(backend)
            detections = detector.detect(image)
        except ImportError as e:
            st.error(f"Backend '{backend}' isn't installed: {e}")
            st.stop()

    boxes = [d["box"] for d in detections]

    if len(boxes) == 0:
        st.warning(
            "No players detected. This can mean: the detector missed them "
            "(likely if players are tightly packed/crouched — try the YOLO "
            "backend), or the photo isn't a clear pre-snap shot."
        )
    else:
        labels, team_colors = split_teams(image, boxes)

        draw_img = image.copy()
        draw = ImageDraw.Draw(draw_img)
        for (x, y, w, h), label in zip(boxes, labels):
            color = TEAM_A_COLOR if label == 0 else TEAM_B_COLOR
            draw.rectangle([x, y, x + w, y + h], outline=color, width=3)

        n_team_a = labels.count(0)
        n_team_b = labels.count(1)

        m1, m2, m3 = st.columns(3)
        m1.metric("Players detected", len(boxes))
        m2.metric("Team A (red box)", n_team_a)
        m3.metric("Team B (blue box)", n_team_b)

        if len(boxes) < 14:
            st.info(
                f"Only {len(boxes)} players detected out of an expected 22 "
                "on the field pre-snap. Some players were likely missed "
                "(common with the HOG backend on packed formations)."
            )

        st.image(draw_img, use_container_width=True,
                  caption="Detected players (red/blue = team split by jersey color clustering)")

        st.caption(
            "Team split is a color-clustering heuristic, not verified team "
            "identity — it can mislabel players if both teams wear similar "
            "colors, or if shadows/lighting vary a lot across the frame."
        )
else:
    st.info("Upload a pre-snap photo to run detection.")
