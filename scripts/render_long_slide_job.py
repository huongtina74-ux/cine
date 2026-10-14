from __future__ import annotations

import argparse
import json
import math
import re
import sys
import traceback
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from long_slide_lookdev import (  # noqa: E402
    TOY_CAMERA_CANDIDATES,
    TOY_LENS_MM,
    TOY_TARGET_AREA,
    apply_lookdev,
    is_themed,
)
import long_slide_events as cues  # noqa: E402
from long_slide_fx import add_cartoon_eyes, apply_paint_gates  # noqa: E402
from long_slide_gimmicks import (  # noqa: E402
    DOOR_HOLD_FRAMES,
    add_ball_smash,
    add_door_reveal,
    pop_in,
    tint_actor,
)
from long_slide_props import place_kit_props  # noqa: E402
from long_slide_fx_plan import (  # noqa: E402
    COMPANION_TARGET_LENGTH,
    MAX_COMPANIONS,
    PAINT_PALETTE,
    lane_offsets,
    race_paces,
)

# Roles a grounding or camera ray may pass through (characters and FX, not set).
ACTOR_ROLES = {"animal", "companion"}
CAMERA_PASS_ROLES = {"animal", "fx", "pickup"}
RACE_FRAMING = 1.3
# The parade flies in a V behind the lead: every clone has its own lane (bodies
# are ~0.8 wide, the slide is |x| < 2.6) and the one that shares the lead's lane
# trails by more than a body length (~0.056 m per frame on the course).
CLONE_FORMATION = ((-0.95, 14), (0.95, 14), (-1.85, 28), (1.85, 28), (0.0, 50))
FINISH_OVERSHOOT_MAX = 1.8


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--still", type=int, action="append", default=[],
                        help="render only these frames as PNG stills (lookdev review)")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def visible_bbox(objects):
    points = []
    for obj in objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))
    if not points:
        return Vector((-1, -1, 0)), Vector((1, 1, 2))
    mins = Vector((
        min(p.x for p in points),
        min(p.y for p in points),
        min(p.z for p in points),
    ))
    maxs = Vector((
        max(p.x for p in points),
        max(p.y for p in points),
        max(p.z for p in points),
    ))
    return mins, maxs


def append_library(path: Path, *, prefix: str, include_actions: bool = False):
    before_objects = set(bpy.data.objects)
    before_actions = set(bpy.data.actions)
    with bpy.data.libraries.load(str(path), link=False) as (data_from, data_to):
        data_to.objects = [
            name for name in data_from.objects
            if not name.startswith("PREVIEW_")
        ]
        if include_actions:
            data_to.actions = list(data_from.actions)

    collection = bpy.data.collections.new(prefix)
    bpy.context.scene.collection.children.link(collection)
    loaded_objects = []
    for obj in data_to.objects:
        if obj is None:
            continue
        for parent_collection in list(obj.users_collection):
            parent_collection.objects.unlink(obj)
        collection.objects.link(obj)
        loaded_objects.append(obj)

    loaded_actions = []
    if include_actions:
        loaded_actions = [
            action for action in bpy.data.actions
            if action not in before_actions
        ]
    return collection, loaded_objects, loaded_actions


def normalize_animal(objects, spawn: Vector, target_length=2.6, *, prefix="FACTORY_ANIMAL", role="animal"):
    # Keep model normalization separate from motion. Camera and path rigs must
    # never inherit the source model's scale.
    motion_root = bpy.data.objects.new(f"{prefix}_ROOT", None)
    scale_root = bpy.data.objects.new(f"{prefix}_SCALE_ROOT", None)
    bpy.context.scene.collection.objects.link(motion_root)
    bpy.context.scene.collection.objects.link(scale_root)
    scale_root.parent = motion_root

    for obj in objects:
        obj["factory_role"] = role
    top_level = [obj for obj in objects if obj.parent is None or obj.parent not in objects]
    for obj in top_level:
        obj.parent = scale_root

    bpy.context.view_layer.update()
    mins, maxs = visible_bbox(objects)
    size = maxs - mins
    longest = max(size.x, size.y, size.z, 0.001)
    scale = target_length / longest
    scale_root.scale = (scale, scale, scale)
    bpy.context.view_layer.update()

    mins, maxs = visible_bbox(objects)
    center = (mins + maxs) * 0.5
    scale_root.location += Vector((-center.x, -center.y, -mins.z))
    motion_root.location = spawn
    bpy.context.view_layer.update()
    return motion_root, scale_root


def normalize_forward_axis(objects, scale_root, *, record=True):
    """Rotate imported animals so their semantic forward points to factory +Y."""
    if scale_root is None:
        return "UNKNOWN"

    armatures = [obj for obj in objects if obj.type == "ARMATURE"]
    if not armatures:
        return _forward_from_bounds(objects, scale_root, record=record)
    bones = armatures[0].data.bones

    head = None
    for bone in bones:
        name = bone.name.lower()
        if name == "head":
            head = bone
            break
    if head is None:
        for bone in bones:
            if "head" in bone.name.lower() and "react" not in bone.name.lower():
                head = bone
                break
    if head is None:
        return _forward_from_bounds(objects, scale_root, record=record)

    p = (head.head_local + head.tail_local) * 0.5
    if abs(p.y) >= abs(p.x):
        if p.y < 0:
            yaw = math.pi
            source = "-Y"
        else:
            yaw = 0.0
            source = "+Y"
    else:
        if p.x > 0:
            yaw = math.pi / 2.0
            source = "+X"
        else:
            yaw = -math.pi / 2.0
            source = "-X"

    scale_root.rotation_euler.z = yaw
    bpy.context.view_layer.update()
    if record:
        bpy.context.scene["animal_source_forward_axis"] = source
        bpy.context.scene["animal_forward_normalized_to"] = "+Y"
    print(f"ANIMAL_FORWARD_NORMALIZED::{scale_root.name}:{source}->+Y")
    return source


def _forward_from_bounds(objects, scale_root, *, record=True):
    """Rigs without a head bone (e.g. Bone..Bone.004): the head is the higher end of the long axis."""
    points = [obj.matrix_world @ v.co for obj in objects if obj.type == "MESH" for v in obj.data.vertices]
    if len(points) < 8:
        return "UNKNOWN"
    spans = {axis: max(p[axis] for p in points) - min(p[axis] for p in points) for axis in (0, 1)}
    axis = max(spans, key=spans.get)
    lo = min(p[axis] for p in points)
    hi = max(p[axis] for p in points)
    reach = 0.25 * (hi - lo)
    top_low = max((p.z for p in points if p[axis] <= lo + reach), default=0.0)
    top_high = max((p.z for p in points if p[axis] >= hi - reach), default=0.0)
    positive = top_high >= top_low
    source, yaw = {
        (1, True): ("+Y", 0.0), (1, False): ("-Y", math.pi),
        (0, True): ("+X", math.pi / 2.0), (0, False): ("-X", -math.pi / 2.0),
    }[(axis, positive)]
    scale_root.rotation_euler.z = yaw
    bpy.context.view_layer.update()
    if record:
        bpy.context.scene["animal_source_forward_axis"] = source + "(bounds)"
        bpy.context.scene["animal_forward_normalized_to"] = "+Y"
    print(f"ANIMAL_FORWARD_NORMALIZED::{scale_root.name}:{source}(bounds)->+Y")
    return source


def base_action_name(name: str) -> str:
    """Blender renames clashing appends to Run.001; match on the source name."""
    return re.sub(r"\.\d{3}$", "", name)


# Locomotion first: a module's animation sequence starts with "idle", but the
# animal travels the whole course, so an idle pose would slide without legs moving.
LOCOMOTION_RANK = {"run": 0, "walk": 1, "idle": 2}


def select_source_action(motions, actions):
    by_name = {}
    for action in actions:
        by_name.setdefault(base_action_name(action.name), action)
    ranked = sorted(
        (m for m in motions if m.get("semantic_action") in LOCOMOTION_RANK and m.get("source_action")),
        key=lambda m: LOCOMOTION_RANK[m["semantic_action"]],
    )
    preference = [m["source_action"] for m in ranked]
    preference.extend(["Run", "Gallop", "Walk", "Idle"])
    for name in preference:
        if name in by_name:
            return by_name[name]
    return next(iter(actions), None)


def bind_action(objects, action):
    if action is None:
        return None
    armatures = [obj for obj in objects if obj.type == "ARMATURE"]
    if not armatures:
        return None
    armature = armatures[0]
    if armature.animation_data is None:
        armature.animation_data_create()
    armature.animation_data.action = action
    if base_action_name(action.name).lower() in {"run", "gallop", "walk", "walkslow", "idle"}:
        for curve in action.fcurves:
            if not any(mod.type == "CYCLES" for mod in curve.modifiers):
                curve.modifiers.new("CYCLES")
    return armature


def platform_top(name: str, fallback: float) -> float:
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        return fallback
    return max((obj.matrix_world @ Vector(corner)).z for corner in obj.bound_box)


def surface_height(x: float, y: float, fallback: float) -> float:
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    origin = Vector((x, y, 20.0))
    direction = Vector((0.0, 0.0, -1.0))
    hit, location, _, _, obj, _ = bpy.context.scene.ray_cast(
        depsgraph,
        origin,
        direction,
        distance=40.0,
    )
    if hit and obj is not None and obj.get("factory_role") not in ACTOR_ROLES | {"fx"}:
        return float(location.z)
    return fallback


def animate_root(root, module, fps, *, lane_x=0.0, pace=1.0, start_hold=0, delay=0):
    """Key the run down the course.

    lane_x shifts the line sideways; pace > 1 is slower; start_hold keeps the
    runner on the start line for that many frames (doors opening); delay shifts
    the whole run later at the same speed (a parade following the lead).
    """
    duration = float(module["duration_seconds"])
    end_frame = max(2, round(duration * fps))
    run_start = 1 + int(start_hold)
    span = end_frame - run_start

    def at(fraction):
        return int(delay) + run_start + round(span * fraction * pace)
    start_marker = bpy.data.objects.get("ANIMAL_SPAWN")
    finish_marker = bpy.data.objects.get("FINISH_ZONE")

    start = Vector(start_marker.location if start_marker else (0, -4.5, 1.0))
    finish = Vector(finish_marker.location if finish_marker else (0, 7.0, 0.8))
    start.x += lane_x
    finish.x += lane_x
    start.z = platform_top("START_PLATFORM", start.z) + 0.05
    finish.z = platform_top("FINISH_PLATFORM", finish.z) + 0.05

    # normalize_animal already established the offset needed to keep the
    # source model centered and grounded. Animate deltas from that calibrated pose.
    calibrated = root.location.copy()
    root.location = calibrated
    root.keyframe_insert("location", frame=1)
    if run_start + int(delay) > 1:
        root.keyframe_insert("location", frame=run_start + int(delay))

    mid1 = start.lerp(finish, 0.30)
    mid1.z = surface_height(mid1.x, mid1.y, mid1.z) + 0.05
    root.location = calibrated + (mid1 - start)
    root.keyframe_insert("location", frame=max(2, at(0.30)))

    mid2 = start.lerp(finish, 0.67)
    mid2.z = surface_height(mid2.x, mid2.y, mid2.z) + 0.05
    root.location = calibrated + (mid2 - start)
    root.keyframe_insert("location", frame=max(3, at(0.67)))

    root.location = calibrated + (finish - start)
    root.keyframe_insert("location", frame=max(4, at(1.0)))
    if pace < 1.0:
        # A friend who arrives first keeps running across the finish platform
        # instead of jogging on the spot until the cut.
        travel = Vector((finish.x - start.x, finish.y - start.y, 0.0))
        overshoot = min(FINISH_OVERSHOOT_MAX, travel.length * (1.0 / pace - 1.0))
        if travel.length > 1e-6 and at(1.0) < end_frame:
            root.location = calibrated + (finish - start) + travel.normalized() * overshoot
            root.keyframe_insert("location", frame=end_frame)

    # Small controlled reaction near the end; no unbounded rigid-body simulation.
    reaction_frame = max(3, at(0.82))
    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert("rotation_euler", frame=max(2, reaction_frame - 2))
    root.rotation_euler.z = math.radians(8)
    root.keyframe_insert("rotation_euler", frame=reaction_frame)
    root.rotation_euler.z = 0
    root.keyframe_insert("rotation_euler", frame=min(end_frame, reaction_frame + 3))

    if root.animation_data and root.animation_data.action:
        for fc in root.animation_data.action.fcurves:
            interpolation = "LINEAR" if fc.data_path == "location" else "BEZIER"
            for kp in fc.keyframe_points:
                kp.interpolation = interpolation
    return end_frame


def place_obstacle(row, index):
    path = Path(row["path"])
    _, objects, _ = append_library(
        path,
        prefix=f"OBSTACLE_{index:02d}_{row['asset_id'].replace('.', '_')}",
    )
    root = bpy.data.objects.new(f"OBSTACLE_ROOT_{index:02d}", None)
    bpy.context.scene.collection.objects.link(root)
    for obj in objects:
        obj["factory_role"] = "obstacle"
    top = [obj for obj in objects if obj.parent is None or obj.parent not in objects]
    for obj in top:
        obj.parent = root

    marker = bpy.data.objects.get(str(row.get("slot", "")).upper())
    if marker is None:
        marker = bpy.data.objects.get(f"OBSTACLE_SLOT_{index}")
    if marker is not None:
        root.location = marker.location

    for obj in objects:
        if obj.get("rotation_speed_deg_s") is not None:
            speed = float(obj["rotation_speed_deg_s"])
            obj.rotation_euler.z = 0
            obj.keyframe_insert("rotation_euler", frame=1)
            obj.rotation_euler.z = math.radians(speed * 6.0)
            obj.keyframe_insert("rotation_euler", frame=145)
            if obj.animation_data and obj.animation_data.action:
                for fc in obj.animation_data.action.fcurves:
                    for kp in fc.keyframe_points:
                        kp.interpolation = "LINEAR"
    return root


CAMERA_CANDIDATES = {
    "hero_start": [
        Vector((6.0, -6.5, 4.2)),
        Vector((-6.0, -6.5, 4.2)),
        Vector((0.0, -8.0, 4.8)),
    ],
    "chase": [
        Vector((5.0, -6.0, 4.0)),
        Vector((-5.0, -6.0, 4.0)),
        Vector((0.0, -8.0, 4.6)),
    ],
    "obstacle_side": [
        Vector((7.0, -0.5, 4.8)),
        Vector((-7.0, -0.5, 4.8)),
        Vector((6.0, -3.0, 5.6)),
        Vector((-6.0, -3.0, 5.6)),
    ],
    # Finish shots intentionally move in front of the animal. A chase camera
    # behind the animal can occupy the same world-space as an obstacle already
    # passed by the actor.
    "finish_reaction": [
        Vector((4.5, 4.0, 3.8)),
        Vector((-4.5, 4.0, 3.8)),
        Vector((0.0, 5.5, 4.2)),
    ],
    # Variation patterns used by VariationDirector camera styles. They are
    # local offsets on the same chase rig, so they inherit the line-of-sight
    # and framing scoring above.
    "wide_establish": [
        Vector((9.0, -9.0, 6.5)),
        Vector((-9.0, -9.0, 6.5)),
        Vector((0.0, -12.0, 7.5)),
    ],
    "top_down": [
        Vector((0.6, -1.2, 9.0)),
        Vector((-0.6, -1.2, 9.0)),
        Vector((0.0, -2.5, 8.5)),
    ],
    "low_front": [
        Vector((2.8, 4.8, 1.4)),
        Vector((-2.8, 4.8, 1.4)),
        Vector((0.0, 5.8, 1.7)),
    ],
}


def camera_line_clear(cam, target_world):
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    origin = cam.matrix_world.translation.copy()
    direction = target_world - origin
    distance = direction.length
    if distance <= 1e-6:
        return False
    hit, _, _, _, obj, _ = bpy.context.scene.ray_cast(
        depsgraph,
        origin,
        direction.normalized(),
        distance=distance * 1.02,
    )
    if not hit:
        return True
    return bool(obj and obj.get("factory_role") in CAMERA_PASS_ROLES)


CLUTTER_GRID = (0.15, 0.5, 0.85)
CLUTTER_NEAR = 0.6


def foreground_clutter(cam, target_world):
    """Share of screen rays that hit set geometry well in front of the animal.

    A clear line to the animal is not enough: a platform edge can fill half the
    frame while the animal is still technically visible below it.
    """
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    origin = cam.matrix_world.translation.copy()
    near = (target_world - origin).length * CLUTTER_NEAR
    tl, tr, br, bl = _frame_corners(cam, scene)
    rotation = cam.matrix_world.to_3x3()
    hits = 0
    total = 0
    for u in CLUTTER_GRID:
        for v in CLUTTER_GRID:
            local = (tl.lerp(tr, u)).lerp(bl.lerp(br, u), v)
            direction = (rotation @ local).normalized()
            hit, _, _, _, obj, _ = scene.ray_cast(depsgraph, origin, direction, distance=near)
            total += 1
            if hit and obj is not None and obj.get("factory_role") not in CAMERA_PASS_ROLES | {"companion"}:
                hits += 1
    return hits / total


def _frame_corners(cam, scene):
    # view_frame order: top-right, bottom-right, bottom-left, top-left.
    tr, br, bl, tl = (Vector(c) for c in cam.data.view_frame(scene=scene))
    return tl, tr, br, bl


def animal_screen_metrics(cam, animal_objects):
    coords = []
    scene = bpy.context.scene
    for obj in animal_objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            world = obj.matrix_world @ Vector(corner)
            ndc = world_to_camera_view(scene, cam, world)
            if ndc.z > 0:
                coords.append((float(ndc.x), float(ndc.y)))
    if not coords:
        return 0.0, 0.0

    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    clipped_w = max(0.0, min(1.0, xmax) - max(0.0, xmin))
    clipped_h = max(0.0, min(1.0, ymax) - max(0.0, ymin))
    area = clipped_w * clipped_h
    inside = sum(
        1
        for x, y in coords
        if 0.02 <= x <= 0.98 and 0.02 <= y <= 0.98
    ) / len(coords)
    return area, inside


def setup_camera(animal_root, animal_objects, module, fps, width, height, *, framing=1.0):
    """framing > 1 pulls every candidate back (races keep the friends in shot)."""
    for name in ("PREVIEW_CAMERA", "LONG_SLIDE_CAMERA", "CAMERA_TARGET"):
        old = bpy.data.objects.get(name)
        if old is not None:
            bpy.data.objects.remove(old, do_unlink=True)

    target = bpy.data.objects.new("CAMERA_TARGET", None)
    bpy.context.scene.collection.objects.link(target)
    target.parent = animal_root
    target.location = (0.0, 0.0, 0.8)

    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "LONG_SLIDE_CAMERA"
    cam.parent = animal_root
    themed = is_themed(module)
    camera_map = TOY_CAMERA_CANDIDATES if themed else CAMERA_CANDIDATES
    cam.data.lens = TOY_LENS_MM if themed else 55
    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"
    bpy.context.scene.camera = cam

    beats = module.get("camera_beats", [])
    if not beats:
        beats = [{
            "pattern_id": "chase",
            "start_seconds": 0.0,
            "end_seconds": float(module.get("duration_seconds", 1.0)),
        }]

    repairs = []
    decisions = []
    for beat_index, beat in enumerate(beats):
        pattern = str(beat.get("pattern_id", "chase"))
        candidates = [offset * framing for offset in camera_map.get(pattern, camera_map["chase"])]
        start_frame = max(
            1,
            round(float(beat.get("start_seconds", 0.0)) * fps) + 1,
        )
        end_frame = max(
            start_frame + 1,
            round(float(beat.get("end_seconds", beat.get("start_seconds", 0.0))) * fps),
        )
        # Five samples catch moving obstacles (a rotating hammer) that three can miss.
        sample_frames = sorted({
            round(start_frame + (end_frame - start_frame) * t)
            for t in (0.0, 0.25, 0.5, 0.75, 1.0)
        })

        scored = []
        for index, offset in enumerate(candidates):
            sample_scores = []
            min_inside = 1.0
            min_area = 1.0
            clear_hits = 0
            max_clutter = 0.0
            for sample_frame in sample_frames:
                bpy.context.scene.frame_set(sample_frame)
                cam.location = offset
                bpy.context.view_layer.update()
                target_world = target.matrix_world.translation.copy()
                clear = camera_line_clear(cam, target_world)
                area, inside = animal_screen_metrics(cam, animal_objects)
                max_clutter = max(max_clutter, foreground_clutter(cam, target_world))
                clear_hits += int(clear)
                min_inside = min(min_inside, inside)
                min_area = min(min_area, area)

                target_area = (TOY_TARGET_AREA if themed else 0.07) / (framing * framing)
                area_score = max(
                    0.0,
                    1.0 - abs(area - target_area) / target_area,
                )
                sample_scores.append(
                    area_score * 3.0
                    + inside * 5.0
                    + (4.0 if clear else -3.0)
                )

            score = min(sample_scores) if sample_scores else -999.0
            if min_inside < 0.75:
                score -= 8.0
            if min_area < 0.018:
                score -= 6.0
            if clear_hits == 0:
                score -= 12.0
            score -= max_clutter * 9.0
            scored.append((score, index, offset, min_area, min_inside, clear_hits, max_clutter))

        scored.sort(key=lambda row: row[0], reverse=True)
        _, chosen_index, chosen, min_area, min_inside, clear_hits, clutter = scored[0]
        decisions.append(
            f"{pattern}:candidate_{chosen_index + 1}:"
            f"area={min_area:.3f}:inside={min_inside:.2f}:clear={clear_hits}/{len(sample_frames)}"
            f":clutter={clutter:.2f}"
        )
        if chosen_index:
            repairs.append(f"{pattern}:candidate_{chosen_index + 1}")

        # Camera is parented to the unit-scale motion root. Keyframed local
        # offsets behave like true chase rigs and are independent of animal scale.
        cam.location = chosen
        cam.keyframe_insert("location", frame=start_frame)
        cam.location = chosen
        cam.keyframe_insert("location", frame=end_frame)

        # Force a clean shot cut at the next beat instead of drifting through a
        # large interpolated camera move.
        if beat_index + 1 < len(beats):
            next_frame = min(end_frame + 1, round(float(module.get("duration_seconds", 1.0)) * fps))
            cam.location = chosen
            cam.keyframe_insert("location", frame=next_frame)

    if decisions:
        bpy.context.scene["camera_decisions"] = "|".join(decisions)
        print("CAMERA_DECISIONS::" + "|".join(decisions))
    if repairs:
        bpy.context.scene["camera_auto_repairs"] = "|".join(repairs)
        print("CAMERA_AUTO_REPAIR::" + "|".join(repairs))

    if cam.animation_data and cam.animation_data.action:
        for curve in cam.animation_data.action.fcurves:
            for kp in curve.keyframe_points:
                kp.interpolation = "CONSTANT"

    scene = bpy.context.scene
    scene.render.resolution_x = int(width)
    scene.render.resolution_y = int(height)
    scene.render.resolution_percentage = 100


DEFAULT_ENVIRONMENT = {
    "world_color": (0.12, 0.12, 0.12),
    "sun_color": (1.0, 1.0, 1.0),
    "sun_energy": 2.2,
    "sun_elevation_deg": 62.0,
    "sun_azimuth_deg": 25.0,
}


def apply_environment(scene, module):
    """Episode environment theme from the VariationDirector (sky colour and sun)."""
    themed = (module.get("metadata") or {}).get("environment") or {}
    env = dict(DEFAULT_ENVIRONMENT)
    env.update(themed)
    if scene.world is None:
        scene.world = bpy.data.worlds.new("LONG_SLIDE_WORLD")
    sky = tuple(float(c) for c in env["world_color"])
    scene.world.color = sky
    if themed:
        # Scene libraries use a node-based world, which ignores world.color in EEVEE.
        scene.world.use_nodes = True
        nodes = scene.world.node_tree.nodes
        background = next((n for n in nodes if n.type == "BACKGROUND"), None)
        if background is None:
            background = nodes.new("ShaderNodeBackground")
            output = next((n for n in nodes if n.type == "OUTPUT_WORLD"), None) or nodes.new("ShaderNodeOutputWorld")
            scene.world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])
        background.inputs["Color"].default_value = (*sky, 1.0)
        background.inputs["Strength"].default_value = 1.0
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 8))
    sun = bpy.context.object
    sun.name = "LONG_SLIDE_SUN"
    sun.data.energy = float(env["sun_energy"])
    sun.data.color = tuple(float(c) for c in env["sun_color"])
    if themed:
        tilt = math.radians(90.0 - float(env["sun_elevation_deg"]))
        sun.rotation_euler = (tilt, 0.0, math.radians(float(env["sun_azimuth_deg"])))
    else:
        # Unthemed jobs keep the original v1.6 lighting exactly.
        sun.rotation_euler = (math.radians(28), math.radians(-20), math.radians(25))
    scene["long_slide_environment"] = str(env.get("theme_id", "default"))
    return sun


def configure_render(payload, end_frame):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    apply_environment(scene, payload["module"])
    scene.render.fps = int(payload["fps"])
    scene.frame_start = 1
    scene.frame_end = end_frame
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.filepath = str(Path(payload["output_path"]))
    scene.render.film_transparent = False

    if payload.get("render_preview"):
        scene.render.resolution_percentage = min(scene.render.resolution_percentage, 100)


def optional_set_piece(name, build, *args, **kwargs):
    """Set pieces are decoration: a failure is logged and the module still renders."""
    try:
        return build(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001
        print(f"GIMMICK_FAILED::{name}:{type(exc).__name__}:{exc}")
        traceback.print_exc()
        return None


def spawn_actor(row, motions, *, prefix, role, lane_x=0.0, target_length=2.6, record=True):
    """Append one animal, normalize it onto its lane and bind its locomotion."""
    _, objects, actions = append_library(Path(row["path"]), prefix=prefix, include_actions=True)
    spawn_marker = bpy.data.objects.get("ANIMAL_SPAWN")
    spawn = Vector(spawn_marker.location if spawn_marker else (0, -4.5, 1.0))
    spawn.x += lane_x
    spawn.z = platform_top("START_PLATFORM", spawn.z) + 0.05
    root, scale_root = normalize_animal(objects, spawn, target_length, prefix=prefix, role=role)
    normalize_forward_axis(objects, scale_root, record=record)
    action = select_source_action(motions, actions)
    bind_action(objects, action)
    return {"name": prefix, "objects": objects, "root": root, "scale_root": scale_root,
            "lane_x": lane_x, "action": action}


def build_clone_parade(payload, module, fps, seed, hold):
    """Rainbow copies of the lead in a V formation behind it (popped in after their eyes are added)."""
    lead_color = PAINT_PALETTE[seed % len(PAINT_PALETTE)]
    colors = [c for c in PAINT_PALETTE if c != lead_color]
    clones = []
    for index, (offset, delay) in enumerate(CLONE_FORMATION):
        clone = spawn_actor(payload["animal"], payload.get("motions", []), prefix=f"FACTORY_CLONE_{index + 1}",
                            role="companion", lane_x=offset, target_length=COMPANION_TARGET_LENGTH, record=False)
        animate_root(clone["root"], module, fps, lane_x=offset, start_hold=hold, delay=delay)
        tint_actor(clone["objects"], colors[index % len(colors)], clone["name"])
        clone["pop_frame"] = 1 + hold + delay
        clones.append(clone)
    print(f"LONG_SLIDE_CLONE_PARADE::{len(clones)}")
    return clones


def main():
    args = parse_args()
    job_path = Path(args.job).resolve()
    payload = json.loads(job_path.read_text(encoding="utf-8"))
    module = payload["module"]
    fps = int(payload["fps"])
    seed = int(module.get("seed", 0))
    for finding in payload.get("kit_prop_findings", []):
        print("KIT_PROP_FINDING::" + str(finding))

    bpy.ops.wm.open_mainfile(filepath=payload["scene"]["path"])
    cues.reset()
    gimmicks = set((module.get("metadata") or {}).get("gimmicks") or [])
    hold = DOOR_HOLD_FRAMES if "door_reveal" in gimmicks else 0

    companions = payload.get("companions", [])[:MAX_COMPANIONS]
    if "clone_parade" in gimmicks:
        companions = []  # the parade needs the lanes behind the lead
    lanes = lane_offsets(1 + len(companions))
    lead = spawn_actor(payload["animal"], payload.get("motions", []), prefix="FACTORY_ANIMAL", role="animal")
    animal_root, animal_objects, action = lead["root"], lead["objects"], lead["action"]

    # Solve every motion path against clean scene geometry before obstacles
    # are appended, so the grounding ray cannot snap to a moving obstacle.
    end_frame = animate_root(animal_root, module, fps, start_hold=hold)
    actors = [lead]
    paces = race_paces(str(module.get("outcome", "SUCCESS")), len(companions), seed)
    for index, (row, pace) in enumerate(zip(companions, paces), start=1):
        actor = spawn_actor(row, row.get("motions", []), prefix=f"FACTORY_COMPANION_{index}",
                            role="companion", lane_x=lanes[index],
                            target_length=COMPANION_TARGET_LENGTH, record=False)
        animate_root(actor["root"], module, fps, lane_x=lanes[index], pace=pace, start_hold=hold)
        actors.append(actor)
    if companions:
        bpy.context.scene["long_slide_companions"] = ",".join(r["asset_id"] for r in companions)
        print("LONG_SLIDE_RACE::" + ",".join(f"{r['asset_id']}@pace={p}" for r, p in zip(companions, paces)))

    clones = []
    if "clone_parade" in gimmicks:
        clones = optional_set_piece("clone_parade", build_clone_parade, payload, module, fps, seed, hold) or []

    for index, actor in enumerate(actors + clones):
        add_cartoon_eyes(actor["name"], actor["objects"], actor["scale_root"],
                         seed=seed + index * 7, fps=fps, end_frame=end_frame)
    for clone in clones:  # after the eyes: they are measured on the full-size body
        optional_set_piece("clone_pop", pop_in, clone["root"], clone["pop_frame"])
    if "door_reveal" in gimmicks:
        optional_set_piece("door_reveal", add_door_reveal, lanes, seed=seed)
    else:
        cues.record(1, "race_start")

    for index, row in enumerate(payload.get("obstacles", []), start=1):
        place_obstacle(row, index)
    apply_paint_gates(actors, lanes, seed=seed, end_frame=end_frame)
    if "ball_smash" in gimmicks:
        optional_set_piece("ball_smash", add_ball_smash, actors, lanes, seed=seed, end_frame=end_frame)
    # Real props go in before the camera solve so occlusion scoring sees them.
    if is_themed(module):
        place_kit_props(module, payload.get("kit_props", []), end_frame=end_frame)
    bpy.context.scene.frame_set(1)
    setup_camera(
        animal_root,
        animal_objects,
        module,
        fps,
        payload["width"],
        payload["height"],
        framing=RACE_FRAMING if companions else 1.0,
    )
    configure_render(payload, end_frame)
    apply_lookdev(
        bpy.context.scene,
        module,
        camera=bpy.data.objects.get("LONG_SLIDE_CAMERA"),
        target=bpy.data.objects.get("CAMERA_TARGET"),
    )

    bpy.context.scene["long_slide_project_id"] = payload["project_id"]
    bpy.context.scene["long_slide_episode_id"] = payload["episode_id"]
    bpy.context.scene["long_slide_module_id"] = payload["module"]["module_id"]
    bpy.context.scene["long_slide_animal"] = payload["module"]["animal_id"]
    bpy.context.scene["long_slide_source_action"] = action.name if action else ""

    if args.no_render:
        debug_path = job_path.with_suffix(".assembled.blend")
        bpy.ops.wm.save_as_mainfile(filepath=str(debug_path))
        print("LONG_SLIDE_ASSEMBLED_OK::" + str(debug_path))
        return

    if args.still:
        scene = bpy.context.scene
        scene.render.image_settings.file_format = "PNG"
        base = Path(payload["output_path"]).with_suffix("")
        for frame in args.still:
            scene.frame_set(frame)
            scene.render.filepath = f"{base}_f{frame:04d}.png"
            bpy.ops.render.render(write_still=True)
            print("LONG_SLIDE_STILL_OK::" + scene.render.filepath)
        return

    bpy.ops.render.render(animation=True)
    sidecar = cues.dump(payload["output_path"], fps=fps, frames=end_frame)
    print("LONG_SLIDE_EVENTS::" + str(sidecar))
    print("LONG_SLIDE_RENDER_OK::" + payload["output_path"])


if __name__ == "__main__":
    main()
