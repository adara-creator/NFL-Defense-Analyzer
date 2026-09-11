"""
Field calibration: converts image pixel coordinates into real-world field
coordinates (yards from line of scrimmage, yards from center).

This is pure geometry (a homography), not machine learning. Given 4
correctly-identified point correspondences (pixel location <-> known real
-world field location), the transform is exact math -- the only error
source is how precisely the 4 points were identified in the first place.

COORDINATE CONVENTION (field space, in yards):
    x = horizontal distance from the center of the formation
        (positive = offense's right, negative = offense's left)
    y = distance from the line of scrimmage
        (positive = downfield / defense's side, negative = behind LOS /
         offensive backfield)
    LOS is y = 0 by definition.

REQUIRED CALIBRATION POINTS:
Ask the user to click 4 points on the photo corresponding to these 4
known real-world locations (choose points that are usually visible and
far enough apart for a stable homography):
    1. Left hash mark, on the line of scrimmage      -> field coords (-0.83, 0)*
    2. Right hash mark, on the line of scrimmage      -> field coords (+0.83, 0)*
    3. Left hash mark, 5 yards downfield from LOS     -> field coords (-0.83, 5)
    4. Right hash mark, 5 yards downfield from LOS    -> field coords (+0.83, 5)

    * NFL hashes are 18'6" apart (~6.17 yards), centered on the field,
      so each hash is ~3.08 yards from center -- adjust the constant
      HASH_HALF_WIDTH_YARDS below if you calibrate against a different
      hash spacing (college hashes are much wider).

If hash marks aren't visible in a given photo, any 4 points with known
real-world positions work (yard-line numbers, sideline intersections,
etc.) -- just pass the corresponding field coordinates instead of the
defaults above.
"""

from __future__ import annotations

import numpy as np
import cv2

HASH_HALF_WIDTH_YARDS = 3.08  # NFL: hashes are ~6.17 yards apart, centered


class CalibrationError(Exception):
    """Raised when the 4 calibration points can't produce a stable homography."""
    pass


def default_field_points(downfield_yards: float = 5.0):
    """Default 4 field-coordinate targets matching the docstring's
    hash-mark instructions, in the same order the user should click."""
    h = HASH_HALF_WIDTH_YARDS
    return [
        (-h, 0.0),
        (h, 0.0),
        (-h, downfield_yards),
        (h, downfield_yards),
    ]


def compute_homography(image_points, field_points=None):
    """
    image_points: list of 4 (x_px, y_px) tuples, in click order.
    field_points: list of 4 (x_yards, y_yards) tuples, same order.
                  Defaults to the hash-mark convention above.

    Returns: 3x3 homography matrix mapping image pixels -> field yards.
    Raises CalibrationError if the points are degenerate (collinear /
    too close together for a numerically stable solve).
    """
    if field_points is None:
        field_points = default_field_points()

    if len(image_points) != 4 or len(field_points) != 4:
        raise CalibrationError("Exactly 4 point correspondences are required.")

    src = np.array(image_points, dtype=np.float32)
    dst = np.array(field_points, dtype=np.float32)

    # Degeneracy check: reject near-collinear image points (a stable
    # homography needs 4 points in "general position", not on a line).
    area = 0.5 * abs(
        (src[1][0] - src[0][0]) * (src[2][1] - src[0][1])
        - (src[2][0] - src[0][0]) * (src[1][1] - src[0][1])
    )
    if area < 50:  # pixels^2 -- points too close/collinear to be reliable
        raise CalibrationError(
            "Calibration points are too close together or nearly collinear. "
            "Pick 4 points that are well-spread and not on a single line."
        )

    matrix = cv2.getPerspectiveTransform(src, dst)

    # sanity check: the matrix should not contain nan/inf
    if not np.all(np.isfinite(matrix)):
        raise CalibrationError("Homography solve produced invalid values.")

    return matrix


def pixel_to_field(matrix, pixel_point):
    """Transform a single (x_px, y_px) point into (x_yards, y_yards)."""
    pt = np.array([[pixel_point]], dtype=np.float32)  # shape (1,1,2)
    out = cv2.perspectiveTransform(pt, matrix)
    x_yards, y_yards = out[0][0]
    return float(x_yards), float(y_yards)


def boxes_to_field_positions(matrix, boxes):
    """
    boxes: list of (x, y, w, h) pixel boxes (e.g. from detection.py).
    Returns: list of (x_yards, y_yards) for each box's bottom-center point
             (feet position is a better ground-plane estimate than the
             box center, which is roughly at torso height).
    """
    positions = []
    for (x, y, w, h) in boxes:
        foot_point = (x + w / 2, y + h)  # bottom-center of box
        positions.append(pixel_to_field(matrix, foot_point))
    return positions
