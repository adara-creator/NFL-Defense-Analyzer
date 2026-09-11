"""
Real player detection for pre-snap NFL photos.

This replaces the old hash-based fake analysis with an actual detector
that looks at pixels. Two backends are provided:

- HOGPersonDetector: zero heavy dependencies (just opencv), works out of
  the box, but is a general pedestrian detector -- not tuned for tightly
  packed / crouched football players. Good enough to get real boxes on
  screen and validate the rest of the pipeline (team split, field mapping,
  formation logic) before investing in a heavier model.

- YOLOPersonDetector: much better accuracy on occluded/crouched people,
  but needs `ultralytics` + `torch` installed (larger dependency, more
  RAM/disk). Recommended once you're deploying somewhere with more
  headroom than a small dev sandbox (Streamlit Community Cloud is fine).

Both return the same shape of output so the rest of the app doesn't care
which one is active:

    [{"box": (x, y, w, h), "confidence": float}, ...]

Coordinates are in original image pixel space (x, y = top-left corner).
"""

from __future__ import annotations

import numpy as np
from PIL import Image


class HOGPersonDetector:
    """OpenCV's built-in HOG + SVM pedestrian detector. No model download,
    no torch. Reasonable for spread-out players; weak on packed/crouched
    linemen. Use this to validate the pipeline end-to-end cheaply."""

    def __init__(self, hit_threshold: float = 0.0):
        import cv2  # local import so this module is importable even if
                    # opencv isn't installed and you're only using YOLO
        self._cv2 = cv2
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        self.hit_threshold = hit_threshold

    def detect(self, image: Image.Image) -> list[dict]:
        cv2 = self._cv2
        img = np.array(image.convert("RGB"))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        # Downscale very large images for speed; HOG is slow on big frames.
        h, w = img_bgr.shape[:2]
        scale = 1.0
        max_dim = 1280
        if max(h, w) > max_dim:
            scale = max_dim / max(h, w)
            img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)))

        boxes, weights = self.hog.detectMultiScale(
            img_bgr,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05,
            hitThreshold=self.hit_threshold,
        )

        results = []
        for (x, y, bw, bh), weight in zip(boxes, weights):
            # undo the downscale so boxes line up with the original image
            results.append({
                "box": (x / scale, y / scale, bw / scale, bh / scale),
                "confidence": float(weight),
            })
        return results


class YOLOPersonDetector:
    """Ultralytics YOLOv8, filtered to the 'person' class. Needs
    `pip install ultralytics` (pulls in torch). Much better on packed,
    crouched, occluded players than HOG. Swap this in once you have the
    dependency budget for it."""

    def __init__(self, model_name: str = "yolov8n.pt", conf: float = 0.25):
        from ultralytics import YOLO  # deferred import
        self.model = YOLO(model_name)
        self.conf = conf

    def detect(self, image: Image.Image) -> list[dict]:
        results = self.model(image, conf=self.conf, classes=[0], verbose=False)
        out = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                out.append({
                    "box": (x1, y1, x2 - x1, y2 - y1),
                    "confidence": float(box.conf[0]),
                })
        return out


def get_detector(backend: str = "hog"):
    """Factory so app.py can switch backends with one string."""
    if backend == "hog":
        return HOGPersonDetector()
    if backend == "yolo":
        return YOLOPersonDetector()
    raise ValueError(f"Unknown backend: {backend}")
