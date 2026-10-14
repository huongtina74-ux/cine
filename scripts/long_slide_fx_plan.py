"""Pure planning helpers for Long Slide character FX (no bpy, unit-testable).

The Blender side (long_slide_fx.py) turns these numbers into geometry and
keyframes: cartoon eyes that blink, race lanes and paces for companion
animals, and paint-gate colours.
"""
from __future__ import annotations

import random

MAX_COMPANIONS = 2

# Lead runs the centre lane so every camera rig keeps it framed; companions
# take the side lanes. The internal slide body spans |x| < 2.7.
LANE_OFFSETS = (0.0, -1.55, 1.55)
COMPANION_TARGET_LENGTH = 2.3

# Saturated toy paints, kept away from the course checker colours so a painted
# animal reads clearly against the floor.
PAINT_PALETTE = (
    (0.98, 0.20, 0.55),  # bubblegum pink
    (0.15, 0.55, 1.00),  # sky blue
    (0.20, 0.85, 0.30),  # lime green
    (0.60, 0.25, 0.95),  # grape purple
    (1.00, 0.55, 0.05),  # tangerine
    (1.00, 0.88, 0.10),  # lemon yellow
    (0.05, 0.85, 0.85),  # aqua
    (0.95, 0.10, 0.10),  # cherry red
)

BLINK_MIN_SECONDS = 2.0
BLINK_MAX_SECONDS = 3.8
BLINK_CLOSE_FRAMES = 2
BLINK_HOLD_FRAMES = 1
BLINK_OPEN_FRAMES = 2
BLINK_CLOSED_SCALE = 0.08


def lane_offsets(actor_count: int) -> list[float]:
    if not 1 <= actor_count <= len(LANE_OFFSETS):
        raise ValueError(f"actor_count must be 1..{len(LANE_OFFSETS)}, got {actor_count}")
    return list(LANE_OFFSETS[:actor_count])


def race_paces(outcome: str, companion_count: int, seed: int) -> list[float]:
    """Time multipliers for companions (1.0 = same pace as the lead).

    SUCCESS keeps the lead in front, COMIC_FAIL lets a friend win, and the
    other outcomes mix so the finish order is not always the same.
    """
    if not 0 <= companion_count <= MAX_COMPANIONS:
        raise ValueError(f"companion_count must be 0..{MAX_COMPANIONS}, got {companion_count}")
    rng = random.Random(seed * 7919 + 17)
    if outcome == "SUCCESS":
        return [round(rng.uniform(1.05, 1.16), 3) for _ in range(companion_count)]
    if outcome == "COMIC_FAIL":
        return [round(rng.uniform(0.86, 0.94), 3) for _ in range(companion_count)]
    paces = [round(rng.uniform(0.94, 1.10), 3) for _ in range(companion_count)]
    if len(paces) == 2 and (paces[0] - 1.0) * (paces[1] - 1.0) > 0:
        paces[1] = round(2.0 - paces[1], 3)  # one ahead, one behind
    return paces


def blink_starts(end_frame: int, fps: int, seed: int) -> list[int]:
    """Frames where a blink starts; irregular spacing reads as alive."""
    if end_frame < 2 or fps <= 0:
        return []
    rng = random.Random(seed * 104729 + 3)
    span = BLINK_CLOSE_FRAMES + BLINK_HOLD_FRAMES + BLINK_OPEN_FRAMES
    starts: list[int] = []
    frame = 1 + round(rng.uniform(0.6, 1.6) * fps)
    while frame + span <= end_frame:
        starts.append(frame)
        frame += max(span + 1, round(rng.uniform(BLINK_MIN_SECONDS, BLINK_MAX_SECONDS) * fps))
    return starts


def blink_keys(start: int) -> list[tuple[int, float]]:
    """(frame, eyelid scale) keys for one blink starting at `start`."""
    closed = start + BLINK_CLOSE_FRAMES
    return [
        (start, 1.0),
        (closed, BLINK_CLOSED_SCALE),
        (closed + BLINK_HOLD_FRAMES, BLINK_CLOSED_SCALE),
        (closed + BLINK_HOLD_FRAMES + BLINK_OPEN_FRAMES, 1.0),
    ]


def paint_colors(lane_count: int, seed: int) -> list[tuple[float, float, float]]:
    """One distinct paint per lane, rotated by seed so gates differ per module."""
    if not 1 <= lane_count <= len(PAINT_PALETTE):
        raise ValueError(f"lane_count must be 1..{len(PAINT_PALETTE)}, got {lane_count}")
    order = list(range(len(PAINT_PALETTE)))
    random.Random(seed * 31337 + 11).shuffle(order)
    return [PAINT_PALETTE[i] for i in order[:lane_count]]


def lane_for_x(x: float, lanes: list[float]) -> int:
    return min(range(len(lanes)), key=lambda i: abs(lanes[i] - x))


def curtain_strips(x_min: float, x_max: float, strip_width: float = 0.26, gap: float = 0.05) -> list[float]:
    """Centre x of each hanging paint strip across a gate opening."""
    if x_max - x_min < strip_width:
        return [(x_min + x_max) / 2.0]
    count = int((x_max - x_min + gap) // (strip_width + gap))
    used = count * strip_width + (count - 1) * gap
    left = x_min + (x_max - x_min - used) / 2.0 + strip_width / 2.0
    return [round(left + i * (strip_width + gap), 4) for i in range(count)]
