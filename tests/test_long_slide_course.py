"""Continuous long-slide course geometry and art-direction rules (pure Python)."""
from __future__ import annotations

import colorsys
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import long_slide_course_plan as course  # noqa: E402


def test_centreline_is_long_continuous_and_descending():
    samples = course.course_centreline(21, length=180.0)
    assert len(samples) == 181
    steps = [math.dist((a.x, a.y), (b.x, b.y)) for a, b in zip(samples, samples[1:])]
    assert all(abs(d - 1.0) < 1e-6 for d in steps)  # no gaps or jumps: one track
    assert samples[0].z > samples[-1].z + 8
    assert min(s.z for s in samples) >= 1.2
    assert all(s.yaw == 0.0 for s in samples[:12])  # straight launch


def test_curvature_stays_gentle_so_lanes_never_fold():
    samples = course.course_centreline(5, length=240.0)
    for a, b in zip(samples, samples[1:]):
        assert abs(b.yaw - a.yaw) <= 1 / 18.0 + 1e-9
    assert 18.0 > course.TRACK_WIDTH / 2 + course.WALL_WIDTH  # tightest radius beats the half-width


def test_courses_differ_by_seed_and_repeat_for_the_same_seed():
    a = course.course_centreline(1)
    assert a == course.course_centreline(1)
    assert a != course.course_centreline(2)


def test_lanes_tile_the_track_in_a_fixed_rainbow_order():
    offsets = [course.lane_offset(i) for i in range(len(course.LANE_COLORS))]
    assert offsets == sorted(offsets)
    assert offsets[0] == pytest.approx(-course.TRACK_WIDTH / 2 + course.LANE_WIDTH / 2)
    hues = [colorsys.rgb_to_hsv(*c)[0] for c in course.LANE_COLORS]
    hues = [h - 1.0 if h > 0.9 else h for h in hues]  # red sits at both ends of the hue circle
    assert hues == sorted(hues)  # red -> orange -> yellow -> green -> blue -> purple
    assert all(colorsys.rgb_to_hsv(*c)[1] > 0.7 for c in course.LANE_COLORS)
    with pytest.raises(ValueError):
        course.lane_offset(len(course.LANE_COLORS))


def _chroma(color):
    return max(color) - min(color)


def test_world_is_calmer_than_the_track():
    track = min(_chroma(c) for c in course.LANE_COLORS)
    for key in ("hills", "foliage", "pillar", "wall", "sky_horizon"):
        assert _chroma(course.WORLD[key]) < track * 0.7
    for green in course.WORLD["grass"]:
        assert colorsys.rgb_to_hsv(*green)[2] < 0.6  # grass never glows


def test_offsets_are_perpendicular_and_sampling_interpolates():
    samples = course.course_centreline(3)
    sample = samples[60]
    x, y, z = course.offset_point(sample, 2.0)
    forward = (-math.sin(sample.yaw), math.cos(sample.yaw))
    assert (x - sample.x) * forward[0] + (y - sample.y) * forward[1] == pytest.approx(0.0, abs=1e-9)
    assert math.dist((x, y), (sample.x, sample.y)) == pytest.approx(2.0)
    mid = course.sample_at(samples, 60.5)
    assert mid.y == pytest.approx((samples[60].y + samples[61].y) / 2)
    assert course.sample_at(samples, -5).s == 0.0 and course.sample_at(samples, 1e6) == samples[-1]
