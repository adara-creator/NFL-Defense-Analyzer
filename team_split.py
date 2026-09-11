"""
Splits detected players into two teams by jersey color.

Approach: for each detected box, sample the upper-torso region (roughly
where a jersey is, avoiding grass below and helmet/sky above), find its
dominant color while masking out field-green pixels, then k-means cluster
all players' dominant colors into 2 groups.

This is a real, testable heuristic -- but it is NOT robust to:
- both teams wearing similar/dark colors
- heavy shadow variation across the frame
- refs (in stripes) getting caught in a detection box

Treat it as a first pass. A more robust version would use a jersey-region
crop trained specifically for this (e.g. a small classifier), but color
clustering is a reasonable, cheap starting point that actually looks at
the pixels instead of guessing.
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from sklearn.cluster import KMeans


def _dominant_color(crop: np.ndarray) -> np.ndarray:
    """Dominant color of a crop, excluding likely-field-green pixels."""
    pixels = crop.reshape(-1, 3).astype(np.float32)

    # crude field-green mask: green channel clearly dominant
    r, g, b = pixels[:, 0], pixels[:, 1], pixels[:, 2]
    is_green_field = (g > r + 15) & (g > b + 15)
    kept = pixels[~is_green_field]

    if len(kept) < 10:
        kept = pixels  # fallback if almost everything got masked

    km = KMeans(n_clusters=1, n_init=3, random_state=0).fit(kept)
    return km.cluster_centers_[0]


def split_teams(image: Image.Image, boxes: list[tuple[float, float, float, float]]):
    """
    boxes: list of (x, y, w, h) in image pixel coords.
    Returns: list of team labels (0 or 1), same order as boxes.
             Also returns the two representative team colors.
    """
    img = np.array(image.convert("RGB"))
    colors = []

    for (x, y, w, h) in boxes:
        x, y, w, h = int(x), int(y), int(w), int(h)
        # torso region: middle third vertically, avoiding helmet/legs
        y0 = y + int(h * 0.30)
        y1 = y + int(h * 0.65)
        x0, x1 = x, x + w
        crop = img[max(y0, 0):max(y1, 1), max(x0, 0):max(x1, 1)]
        if crop.size == 0:
            colors.append(np.array([128.0, 128.0, 128.0]))
            continue
        colors.append(_dominant_color(crop))

    colors = np.array(colors)

    if len(colors) < 2:
        # can't cluster fewer than 2 points into 2 groups
        return [0] * len(colors), (colors[0] if len(colors) else None, None)

    km = KMeans(n_clusters=2, n_init=5, random_state=0).fit(colors)
    labels = km.labels_.tolist()
    team_colors = km.cluster_centers_
    return labels, team_colors
