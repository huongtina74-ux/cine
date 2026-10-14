"""One continuous long slide per episode: centreline, lanes and art-direction rules (no bpy).

Art direction, from the niche leader's videos: a natural world (blue sky, green
grass) fills most of the frame, and saturation is spent on the track only -
rainbow lanes in a fixed order that never changes, white separators and walls -
plus a few large hero props. Nothing else competes with the track.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

# Fixed lane order, every episode (the channel's visual signature).
LANE_COLORS = (
    (0.86, 0.10, 0.12),  # red
    (0.96, 0.46, 0.06),  # orange
    (0.98, 0.80, 0.08),  # yellow
    (0.16, 0.68, 0.26),  # green
    (0.10, 0.44, 0.90),  # blue
    (0.52, 0.22, 0.84),  # purple
)
LANE_WIDTH = 1.15
SEPARATOR_WIDTH = 0.07
WALL_WIDTH = 0.28
WALL_HEIGHT = 0.42
TRACK_WIDTH = len(LANE_COLORS) * LANE_WIDTH
# The natural world stays calm so the track reads first.
WORLD = {
    "sky_top": (0.16, 0.44, 0.92),
    "sky_horizon": (0.74, 0.88, 1.00),
    "grass": ((0.09, 0.30, 0.06), (0.20, 0.47, 0.10)),  # two greens, large-scale variation
    "hills": (0.11, 0.28, 0.16),  # darker and slightly blue: reads as distance
    "foliage": (0.17, 0.46, 0.12),  # every tree canopy is pulled to one natural green
    "wall": (0.96, 0.96, 0.97),
    "separator": (1.0, 1.0, 1.0),
    "pillar": (0.88, 0.88, 0.90),
}
# Lanes stay matte enough that the sky does not wash their colour out.
LANE_ROUGHNESS = 0.45
LANE_COAT = 0.0
LANE_SPECULAR = 0.25  # grazing sky reflections were turning the lanes pastel
VIEW_EXPOSURE = -0.1


@dataclass(frozen=True)
class CourseSample:
    s: float  # distance along the centreline (m)
    x: float
    y: float
    z: float
    yaw: float  # heading, radians; 0 = +Y


def course_centreline(seed: int, length: float = 180.0, step: float = 1.0,
                      start_height: float = 16.0, slope: float = 0.075) -> list[CourseSample]:
    """A gently winding, steadily descending centreline with a few soft bumps.

    Curvature stays below about 1/18 m so lanes never fold, and the track never
    drops under 1.2 m above the ground.
    """
    rng = random.Random(seed * 9973 + 1)
    waves = [(rng.uniform(0.010, 0.022), rng.uniform(0, math.tau), rng.uniform(0.18, 0.32)) for _ in range(2)]
    bumps = [(rng.uniform(0.25, 0.85) * length, rng.uniform(4.0, 7.0), rng.uniform(0.5, 0.9)) for _ in range(2)]
    samples = []
    x = y = 0.0
    yaw = 0.0
    count = int(length / step) + 1
    for i in range(count):
        s = i * step
        z = start_height - slope * s
        for centre, width, height in bumps:
            z += height * math.exp(-((s - centre) / width) ** 2)
        z = max(1.2, z)
        samples.append(CourseSample(s, x, y, z, yaw))
        curvature = sum(a * math.sin(f * s * 0.1 * math.tau / 2 + p) for a, p, f in waves)
        curvature = max(-1 / 18.0, min(1 / 18.0, curvature)) if s > 12 else 0.0  # straight launch
        yaw += curvature * step
        x += -math.sin(yaw) * step
        y += math.cos(yaw) * step
    return samples


def lane_offset(lane: int) -> float:
    """Signed distance of a lane centre from the centreline (lane 0 is the far left)."""
    if not 0 <= lane < len(LANE_COLORS):
        raise ValueError(f"lane must be 0..{len(LANE_COLORS) - 1}")
    return -TRACK_WIDTH / 2 + LANE_WIDTH * (lane + 0.5)


def sample_at(samples: list[CourseSample], s: float) -> CourseSample:
    """Linear interpolation along the centreline (clamped to its ends)."""
    if s <= samples[0].s:
        return samples[0]
    if s >= samples[-1].s:
        return samples[-1]
    step = samples[1].s - samples[0].s
    i = int(s / step)
    a, b = samples[i], samples[min(i + 1, len(samples) - 1)]
    t = (s - a.s) / step
    return CourseSample(s, a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t,
                        a.yaw + (b.yaw - a.yaw) * t)


def offset_point(sample: CourseSample, lateral: float) -> tuple[float, float, float]:
    """World point `lateral` metres to the right of the centreline at `sample`."""
    right = (math.cos(sample.yaw), math.sin(sample.yaw))
    return sample.x + right[0] * lateral, sample.y + right[1] * lateral, sample.z
