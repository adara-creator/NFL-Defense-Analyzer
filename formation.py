"""
Classifies offensive player roles (OL/QB/RB/TE/WR) and names the formation,
using ONLY real field-coordinate positions (yards from LOS, yards from
center) produced by calibration.py. No prediction, no ML, no confidence
scores -- this is deterministic geometry, same as a human reading
alignment off a diagram.

COORDINATE CONVENTION (matches calibration.py):
    x: yards from center (negative = left, positive = right)
    y: yards from LOS (negative = behind LOS, i.e. backfield;
       0 = on the line; positive = downfield, shouldn't occur pre-snap
       for offense)

LIMITATIONS (explicit, not hidden):
- This assumes all 11 offensive players were correctly detected and
  correctly separated from defense (garbage in -> garbage out).
- Role thresholds below (LOS_TOLERANCE, TACKLE_BOX_HALF_WIDTH, etc.) are
  reasonable defaults, not universal constants -- unusual formations
  (swinging gate, jumbo, etc.) may misclassify. They're config, so tune
  them, don't hardcode around a single test case.
- QB identification for shotgun/pistol vs under-center is a heuristic
  (closest-to-center backfield player), not guaranteed correct if two
  backfield players are similarly centered (e.g. some pistol/offset sets).
"""

from __future__ import annotations
from dataclasses import dataclass

# ---- Config: tune these, don't treat as fixed truth ----
# NOTE: OL tolerance must stay tighter than a normal under-center QB depth
# (~1 yard), or the QB gets mistaken for a 6th lineman. Found via testing
# with a synthetic under-center formation -- see test output.
OL_LOS_TOLERANCE = 0.5           # OL are essentially AT y=0
TE_LOS_TOLERANCE = 0.75          # TE occasionally sits a touch off the line
WR_LOS_TOLERANCE = 3.0           # WR/slot can be noticeably off the ball
TACKLE_BOX_HALF_WIDTH = 4.0      # OL are within this of center (x)
TE_MAX_HALF_WIDTH = 8.0          # TE = on line, wider than OL, inside this
BACKFIELD_Y_THRESHOLD = -0.75    # more negative than this = clearly backfield


@dataclass
class Player:
    id: str
    x: float  # yards from center
    y: float  # yards from LOS (negative = behind)


def classify_roles(players: list[Player]) -> dict[str, str]:
    """Returns {player_id: role} where role in {OL, QB, RB, TE, WR, UNKNOWN}."""
    roles: dict[str, str] = {}
    remaining = list(players)

    # --- OL: near LOS, within the tackle box width ---
    ol_candidates = [p for p in remaining if abs(p.y) <= OL_LOS_TOLERANCE
                      and abs(p.x) <= TACKLE_BOX_HALF_WIDTH]
    # OL should be exactly 5 in a legal formation; if we found a different
    # count, don't silently pretend -- take the 5 closest to y=0 as OL and
    # flag the rest as UNKNOWN rather than guessing further roles for them.
    ol_candidates.sort(key=lambda p: abs(p.y))
    ol = ol_candidates[:5]
    for p in ol:
        roles[p.id] = "OL"
    if len(ol_candidates) != 5:
        for p in ol_candidates[5:]:
            roles[p.id] = "UNKNOWN"  # ambiguous — near LOS but OL slots full
    remaining = [p for p in remaining if p.id not in roles]

    # --- TE: on line, just outside the tackle box ---
    te = [p for p in remaining if abs(p.y) <= TE_LOS_TOLERANCE
          and TACKLE_BOX_HALF_WIDTH < abs(p.x) <= TE_MAX_HALF_WIDTH]
    for p in te:
        roles[p.id] = "TE"
    remaining = [p for p in remaining if p.id not in roles]

    # --- WR: on or near the line, wide of the TE zone ---
    wr = [p for p in remaining if abs(p.y) <= WR_LOS_TOLERANCE
          and abs(p.x) > TACKLE_BOX_HALF_WIDTH]
    for p in wr:
        roles[p.id] = "WR"
    remaining = [p for p in remaining if p.id not in roles]

    # --- Backfield: whoever is left, clearly behind the LOS ---
    backfield = [p for p in remaining if p.y <= BACKFIELD_Y_THRESHOLD]
    if backfield:
        # QB = backfield player closest to center (x near 0)
        backfield.sort(key=lambda p: abs(p.x))
        qb = backfield[0]
        roles[qb.id] = "QB"
        for p in backfield[1:]:
            roles[p.id] = "RB"
    remaining = [p for p in remaining if p.id not in roles]

    for p in remaining:
        roles[p.id] = "UNKNOWN"

    return roles


def classify_formation(players: list[Player], roles: dict[str, str]) -> dict:
    """
    Returns a dict describing the formation using only counted/measured
    facts -- no coverage/defense terminology, no confidence scores.
    {
        "personnel": "11",              # RB count + TE count, standard notation
        "rb_count": 1, "te_count": 1, "wr_count": 3,
        "backfield_set": "shotgun" | "under_center" | "unknown",
        "receiver_split": {"left": 2, "right": 1},
        "grouping": "trips_right" | "bunch_left" | "2x2" | "empty" | "balanced",
        "notes": [...]  # any ambiguity flags
    }
    """
    by_id = {p.id: p for p in players}
    notes = []

    rb_ids = [pid for pid, r in roles.items() if r == "RB"]
    te_ids = [pid for pid, r in roles.items() if r == "TE"]
    wr_ids = [pid for pid, r in roles.items() if r == "WR"]
    qb_ids = [pid for pid, r in roles.items() if r == "QB"]

    personnel = f"{len(rb_ids)}{len(te_ids)}"

    backfield_set = "unknown"
    if qb_ids:
        qb = by_id[qb_ids[0]]
        # under center: QB essentially at the LOS; shotgun/pistol: clearly back
        if qb.y > -1.5:
            backfield_set = "under_center"
        elif qb.y <= -3.0:
            backfield_set = "shotgun_or_pistol"
        else:
            notes.append("QB depth ambiguous between under-center and shotgun")

    receivers = [by_id[pid] for pid in te_ids + wr_ids]
    left = [p for p in receivers if p.x < 0]
    right = [p for p in receivers if p.x > 0]
    receiver_split = {"left": len(left), "right": len(right)}

    grouping = "balanced"
    if len(rb_ids) == 0 and len(receivers) >= 4:
        grouping = "empty"
    elif len(left) >= 3:
        grouping = "trips_left"
    elif len(right) >= 3:
        grouping = "trips_right"
    elif len(left) == 2 and len(right) == 2:
        grouping = "2x2"

    # bunch detection: 3+ receivers on the same side within a tight radius
    def _is_bunch(side_players):
        if len(side_players) < 3:
            return False
        for i, p1 in enumerate(side_players):
            close = [p2 for p2 in side_players
                     if p2.id != p1.id
                     and ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5 <= 3.0]
            if len(close) >= 2:
                return True
        return False

    if _is_bunch(left):
        grouping = "bunch_left"
    elif _is_bunch(right):
        grouping = "bunch_right"

    return {
        "personnel": personnel,
        "rb_count": len(rb_ids),
        "te_count": len(te_ids),
        "wr_count": len(wr_ids),
        "backfield_set": backfield_set,
        "receiver_split": receiver_split,
        "grouping": grouping,
        "notes": notes,
    }
