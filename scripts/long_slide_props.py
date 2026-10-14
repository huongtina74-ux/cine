"""Real CC0 set dressing for Long Slide renders (runs inside Blender).

Rows come from config/animal_long_slide/kit_props.yaml through the binder,
which has already checked the pack licence and resolved absolute paths. Each
model is imported once into a hidden prototype collection, scaled from its own
bounds to the requested height, and placed as collection instances:

- backdrop: a ring around the course;
- start / finish: beside the platforms, one per side;
- air: pickups floating over the race lanes that spin and pop when an animal
  runs through them.
"""
from __future__ import annotations

import math
import random
import traceback
from pathlib import Path

import bpy
from mathutils import Vector

import long_slide_events as cues

PROP_ROLE = "set_dressing"
PICKUP_ROLE = "pickup"
BACKDROP_RING = (9.5, 22.0)
COURSE_KEEP_OUT_X = 4.2
COURSE_Y = (-9.0, 11.0)
SCENE_GROUND = {"x": 8.0, "y": (-9.5, 12.5), "z": -0.05}
OUTER_GROUND_Z = -0.57
PICKUP_Y = (-2.5, 5.0)
PICKUP_LIFT = 1.25
# The root sits at the body centre; the head reaches a pickup about this far earlier.
PICKUP_HEAD_REACH = 1.1
SPIN_FRAMES = 36


def _proto_collection():
    """Prototypes live outside the scene tree; only their instances render."""
    proto = bpy.data.collections.get("KIT_PROTOTYPES")
    if proto is None:
        proto = bpy.data.collections.new("KIT_PROTOTYPES")
    return proto


def _import(row, proto_root):
    """Import one prop file into its own collection (not linked to the scene)."""
    path = Path(row["path"])
    collection = bpy.data.collections.new(f"KIT_{row['name']}")
    proto_root.children.link(collection)
    before = set(bpy.data.objects)
    if path.suffix.lower() == ".blend":
        with bpy.data.libraries.load(str(path), link=False) as (src, dst):
            dst.objects = list(src.objects)
        objects = [o for o in dst.objects if o is not None]
    else:
        bpy.ops.import_scene.gltf(filepath=str(path))
        objects = [o for o in bpy.data.objects if o not in before]
    objects = [o for o in objects if o.type in {"MESH", "EMPTY"}]
    for obj in objects:
        for parent in list(obj.users_collection):
            parent.objects.unlink(obj)
        collection.objects.link(obj)
        obj["factory_role"] = PROP_ROLE
    bpy.context.view_layer.update()
    points = [o.matrix_world @ Vector(c) for o in objects if o.type == "MESH" for c in o.bound_box]
    if not points:
        return None
    mins = Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    maxs = Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    size = maxs - mins
    return {"collection": collection, "min": mins, "center": (mins + maxs) * 0.5, "height": max(size.z, 1e-3),
            "footprint": max(size.x, size.y, 1e-3)}


def _ground_z(x, y):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    hit, location, _, _, obj, _ = bpy.context.scene.ray_cast(depsgraph, Vector((x, y, 30.0)), Vector((0, 0, -1)), distance=60.0)
    # Only trust real ground: a ray can also land on a tree canopy or a hill.
    if hit and obj is not None and obj.name.startswith(("GROUND", "LOOK_disc")):
        return float(location.z)
    inside = abs(x) <= SCENE_GROUND["x"] and SCENE_GROUND["y"][0] <= y <= SCENE_GROUND["y"][1]
    return SCENE_GROUND["z"] if inside else OUTER_GROUND_Z


def _instance(proto, name, location, height, yaw, role=PROP_ROLE):
    scale = height / proto["height"]
    empty = bpy.data.objects.new(name, None)
    empty.instance_type = "COLLECTION"
    empty.instance_collection = proto["collection"]
    empty.scale = (scale, scale, scale)
    empty.rotation_euler = (0.0, 0.0, yaw)
    # Sit the model's bounds on the ground at the requested point.
    offset = Vector((proto["center"].x, proto["center"].y, proto["min"].z)) * scale
    offset.rotate(empty.rotation_euler)
    empty.location = Vector(location) - offset
    empty["factory_role"] = role
    bpy.context.scene.collection.objects.link(empty)
    return empty


def _backdrop_point(rng, taken):
    for _ in range(60):
        angle = rng.uniform(0, math.tau)
        radius = rng.uniform(*BACKDROP_RING)
        x, y = math.cos(angle) * radius, math.sin(angle) * radius + 1.5
        if abs(x) < COURSE_KEEP_OUT_X and COURSE_Y[0] < y < COURSE_Y[1]:
            continue
        if all((x - tx) ** 2 + (y - ty) ** 2 > tr ** 2 for tx, ty, tr in taken):
            return x, y
    return None


def _platform_side_points(zone):
    if zone == "start":
        return [(-4.4, -5.4), (4.4, -5.4)]
    return [(-4.7, 7.6), (4.7, 7.6)]


def _actor_roots():
    return [o for o in bpy.context.scene.objects
            if o.name.endswith("_ROOT") and not o.name.endswith("SCALE_ROOT") and o.name.startswith("FACTORY_")]


def _crossing(root, y, end_frame):
    scene = bpy.context.scene
    for frame in range(1, end_frame + 1):
        scene.frame_set(frame)
        if root.matrix_world.translation.y >= y:
            return frame
    return None


def _surface_z(x, y):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    hit, location, _, _, obj, _ = bpy.context.scene.ray_cast(depsgraph, Vector((x, y, 20.0)), Vector((0, 0, -1)), distance=40.0)
    if hit and obj is not None and obj.get("factory_role") not in {"animal", "companion", "fx", "obstacle", PROP_ROLE, PICKUP_ROLE}:
        return float(location.z)
    return 1.0


def _pickups(proto, row, rng, end_frame):
    scene = bpy.context.scene
    scene.frame_set(1)
    roots = _actor_roots()
    lanes = sorted({round(r.matrix_world.translation.x, 2) for r in roots}) or [0.0]
    placed = 0
    for i in range(row["count"]):
        lane = lanes[i % len(lanes)]
        y = PICKUP_Y[0] + (PICKUP_Y[1] - PICKUP_Y[0]) * (i + rng.uniform(0.2, 0.8)) / row["count"]
        runner = min(roots, key=lambda r: abs(r.matrix_world.translation.x - lane)) if roots else None
        # Height from the runner itself when it passes: a top-down ray can land on a gate bar.
        passing = _crossing(runner, y, end_frame) if runner is not None else None
        if passing is not None:
            z = runner.matrix_world.translation.z + PICKUP_LIFT
            scene.frame_set(1)
        else:
            z = _surface_z(lane, y) + PICKUP_LIFT
        pickup = _instance(proto, f"KIT_PICKUP_{row['name']}_{i:02d}", (lane, y, z), row["height"], 0.0, PICKUP_ROLE)
        base = pickup.scale.copy()
        pickup.rotation_euler = (0.0, 0.0, 0.0)
        pickup.keyframe_insert("rotation_euler", index=2, frame=1)
        pickup.rotation_euler.z = math.tau
        pickup.keyframe_insert("rotation_euler", index=2, frame=1 + SPIN_FRAMES)
        curve = pickup.animation_data.action.fcurves.find("rotation_euler", index=2)
        for key in curve.keyframe_points:
            key.interpolation = "LINEAR"
        curve.modifiers.new("CYCLES")
        frame = _crossing(runner, y - PICKUP_HEAD_REACH, end_frame) if runner is not None else None
        if frame is not None:
            cues.record(frame + 1, "pickup_pop")
            pickup.scale = base
            pickup.keyframe_insert("scale", frame=max(1, frame - 1))
            pickup.scale = base * 1.45
            pickup.keyframe_insert("scale", frame=frame + 1)
            pickup.scale = base * 0.0
            pickup.keyframe_insert("scale", frame=frame + 4)
        placed += 1
    scene.frame_set(1)
    return placed


def place_kit_props(module, rows, *, end_frame):
    """Dress a themed module with real props. Returns the number of placed instances."""
    if not rows:
        return 0
    rng = random.Random(int(module.get("seed", 0)) * 7349 + 5)
    proto_root = _proto_collection()
    taken: list[tuple[float, float, float]] = []
    placed = 0
    backdrop = 0
    for row in rows:
        try:
            proto = _import(row, proto_root)
        except Exception as exc:  # noqa: BLE001 - a broken prop file must never stop the render
            print(f"KIT_PROP_IMPORT_FAILED::{row['name']}:{type(exc).__name__}:{exc}")
            traceback.print_exc()
            continue
        if proto is None:
            continue
        if row["zone"] == "air":
            placed += _pickups(proto, row, rng, end_frame)
            continue
        if row["zone"] in {"start", "finish"}:
            for index, (x, y) in enumerate(_platform_side_points(row["zone"])[: row["count"]]):
                yaw = math.pi if row["zone"] == "finish" else 0.0
                _instance(proto, f"KIT_{row['zone'].upper()}_{row['name']}_{index}", (x, y, _ground_z(x, y)), row["height"], yaw)
                placed += 1
            continue
        radius = proto["footprint"] * row["height"] / proto["height"] * 0.6 + 0.6
        for index in range(row["count"]):
            point = _backdrop_point(rng, taken)
            if point is None:
                break
            x, y = point
            taken.append((x, y, radius))
            height = row["height"] * rng.uniform(0.85, 1.15)
            _instance(proto, f"KIT_{row['name']}_{index:02d}", (x, y, _ground_z(x, y)), height, rng.uniform(0, math.tau))
            placed += 1
            backdrop += 1
    bpy.context.scene["kit_props_placed"] = placed
    bpy.context.scene["kit_backdrop_placed"] = backdrop
    print(f"KIT_PROPS::{placed}:rows={len(rows)}")
    return placed
