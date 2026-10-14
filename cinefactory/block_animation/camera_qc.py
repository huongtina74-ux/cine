"""Deterministic, Blender-free camera framing and horizon checks."""

from __future__ import annotations

import math


def _location(actor) -> tuple[float, float, float]:
    transform = actor.transform if hasattr(actor, "transform") else actor
    return (float(transform.location.x), float(transform.location.y), float(transform.location.z))


def estimate_camera_framing(take, scene, actors) -> dict:
    targets = [actor for actor in actors if actor.actor_id in set(take.targets)]
    if not targets:
        return {"passed": False, "findings": ["CAMERA_TARGETS_MISSING"], "metrics": {}}
    points = [_location(actor) for actor in targets]
    center = tuple(sum(point[i] for point in points) / len(points) for i in range(3))
    center = (center[0], center[1], center[2] + 1.45)
    anchor = scene.camera_anchors.get(take.anchor)
    camera = (0.0, -7.0, 2.4) if anchor is None else _location(anchor)
    distance = max(0.1, math.dist(camera, center))
    width = max(1.0, max(point[0] for point in points) - min(point[0] for point in points) + 1.1)
    height = 2.8
    occupancy_x = min(1.0, (width * float(take.lens_mm)) / max(1.0, distance * 48.0))
    occupancy_y = min(1.0, (height * float(take.lens_mm)) / max(1.0, distance * 44.0))
    occupancy = max(occupancy_x, occupancy_y)
    head_positions = [(point[0], point[1], point[2] + 2.8) for point in points]
    headroom = min(1.0, max(0.0, (camera[2] + 3.0 - max(head[2] for head in head_positions)) / 6.0))
    roll = float(getattr(take, "camera_roll", 0.0) or 0.0)
    findings: list[str] = []
    if abs(roll) > 0.001 and take.purpose not in {"dutch_tension", "explicit_dutch"}:
        findings.append("CAMERA_ROLL_NOT_EXPLICIT")
    if occupancy < float(take.min_subject_occupancy):
        findings.append("SUBJECT_UNDERSIZED")
    if occupancy > float(take.max_subject_occupancy):
        findings.append("SUBJECT_OVERSIZED")
    if headroom < float(take.vertical_safe_margin):
        findings.append("HEADROOM_RISK")
    # The benchmark anchors remain in front of the classroom subjects. This is
    # an approximate static-scene gate; true raycasts stay a Blender-side TODO.
    if camera[1] > max(point[1] for point in points) + 0.5:
        findings.append("CAMERA_BEHIND_SUBJECTS")
    return {
        "passed": not findings,
        "findings": findings,
        "metrics": {
            "camera_location": camera,
            "target_center": center,
            "distance": distance,
            "subject_width_estimate": width,
            "head_positions": head_positions,
            "headroom_estimate": headroom,
            "subject_occupancy_estimate": occupancy,
            "camera_roll_degrees": roll,
            "occlusion_check": "APPROXIMATE_STATIC_ANCHOR_CHECK",
        },
    }


def validate_compiled_camera_plan(compiled_episode) -> dict:
    rows = []
    for shot in compiled_episode.shots:
        take = shot.camera_takes[0] if shot.camera_takes else None
        if take is None:
            rows.append({"shot_id": shot.shot_id, "passed": False, "findings": ["CAMERA_MISSING"]})
            continue
        result = estimate_camera_framing(take, shot.scene, shot.actors)
        rows.append({"shot_id": shot.shot_id, "take_id": take.take_id, **result})
    return {
        "passed": all(row["passed"] for row in rows),
        "checks": rows,
        "human_review_required": True,
        "raycast_occlusion_status": "NOT_AVAILABLE_IN_PURE_PYTHON_GATE",
    }
