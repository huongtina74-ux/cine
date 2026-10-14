"""Signature set pieces for Long Slide modules (runs inside Blender).

Modelled on what the niche leaders repeat every round, built procedurally:

- door_reveal: a row of coloured garage doors on the start platform slides up
  while the runners wait behind them;
- ball_smash: giant patchwork balls on the lanes burst into flying pieces the
  moment an animal runs into them;
- clone parade (driven from the worker): rainbow copies of the lead pop in and
  run behind it.

Everything is keyframed (no physics simulation), so renders are deterministic.
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
from mathutils import Vector

import long_slide_events as cues
from long_slide_fx import FX_ROLE, PAINT_BRIGHTNESS, _material, ensure_node_material
from long_slide_fx_plan import PAINT_PALETTE, paint_colors

BALL_RADIUS = 0.78
BALL_CHUNKS = 22
GRAVITY = 9.8
DOOR_HOLD_FRAMES = 22
DOOR_HEIGHT = 2.6


# ---------- door reveal ----------

def _box(name, size, location, material):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.location = location
    obj["factory_role"] = FX_ROLE
    return obj


def _start_edge():
    platform = bpy.data.objects.get("START_PLATFORM")
    if platform is None:
        return -3.2, 3.05, 3.6
    pts = [platform.matrix_world @ Vector(c) for c in platform.bound_box]
    return max(p.y for p in pts), max(p.z for p in pts), max(abs(p.x) for p in pts)


def add_door_reveal(lanes, *, seed):
    """Doors at the front edge of the start platform; they open over DOOR_HOLD_FRAMES."""
    y_edge, z_top, half_width = _start_edge()
    y = y_edge + 0.3  # just past the platform edge, in front of the runners' noses
    colors = paint_colors(len(PAINT_PALETTE), seed)
    frame_mat = _material("FX_DOOR_FRAME", (0.98, 0.98, 0.98), roughness=0.3, coat=0.5)
    post_x = min(half_width, 2.75)
    for side in (-1, 1):
        # Posts reach below the platform top so they stand on the slide, not float above it.
        _box(f"FX_DOOR_POST_{side}", (0.3, 0.4, DOOR_HEIGHT + 1.4), (side * post_x, y, z_top + (DOOR_HEIGHT + 1.4) / 2 - 1.0), frame_mat)
    _box("FX_DOOR_TOP", (2 * post_x + 0.3, 0.45, 0.4), (0.0, y, z_top + DOOR_HEIGHT + 0.4), frame_mat)
    span = 2 * post_x - 0.3
    count = max(3, len(lanes))
    width = span / count
    window = _material("FX_DOOR_WINDOW", (0.75, 0.92, 1.0), roughness=0.05, coat=1.0, emission=0.15)
    rng = random.Random(seed)
    for i in range(count):
        x = -span / 2 + width * (i + 0.5)
        panel = _box(f"FX_DOOR_{i}", (width - 0.06, 0.12, DOOR_HEIGHT), (x, y, z_top + DOOR_HEIGHT / 2),
                     _material(f"FX_DOOR_{i}_{seed}", colors[i % len(colors)], roughness=0.25, coat=0.6))
        smile = _box(f"FX_DOOR_{i}_WINDOW", (width * 0.45, 0.14, 0.32), (0.0, 0.0, DOOR_HEIGHT * 0.22), window)
        smile.parent = panel
        # Shut for the first ~0.4 s so the reveal reads, fully open just before the runners go.
        open_at = DOOR_HOLD_FRAMES - 3 + rng.randint(0, 3)
        panel.keyframe_insert("location", index=2, frame=max(1, open_at - 9))
        panel.location.z += DOOR_HEIGHT + 0.2
        panel.keyframe_insert("location", index=2, frame=open_at)
    cues.record(DOOR_HOLD_FRAMES - 12, "door_open")
    cues.record(DOOR_HOLD_FRAMES, "race_start")
    print(f"FX_DOOR_REVEAL::{count}")
    return DOOR_HOLD_FRAMES


# ---------- ball smash ----------

def _fibonacci_dirs(n):
    golden = math.pi * (3 - math.sqrt(5))
    return [Vector((math.cos(golden * i) * math.sqrt(1 - (1 - 2 * (i + 0.5) / n) ** 2),
                    math.sin(golden * i) * math.sqrt(1 - (1 - 2 * (i + 0.5) / n) ** 2),
                    1 - 2 * (i + 0.5) / n)) for i in range(n)]


def _ball_chunks(name, radius, materials):
    """An icosphere shell split into chunks; returns [(object, centroid_dir)] centred on the origin."""
    source = bmesh.new()
    bmesh.ops.create_icosphere(source, subdivisions=3, radius=radius)
    dirs = _fibonacci_dirs(BALL_CHUNKS)
    groups: dict[int, list] = {}
    for face in source.faces:
        centre = face.calc_center_median().normalized()
        groups.setdefault(max(range(len(dirs)), key=lambda k: dirs[k].dot(centre)), []).append(face)
    chunks = []
    for index, faces in groups.items():
        bm = bmesh.new()
        lookup = {}
        for face in faces:
            verts = []
            for v in face.verts:
                if v.index not in lookup:
                    lookup[v.index] = bm.verts.new(v.co)
                verts.append(lookup[v.index])
            bm.faces.new(verts)
        centroid = sum((v.co for v in bm.verts), Vector()) / max(1, len(bm.verts))
        bmesh.ops.translate(bm, vec=-centroid, verts=bm.verts)
        mesh = bpy.data.meshes.new(f"{name}_{index:02d}")
        bm.to_mesh(mesh)
        bm.free()
        for poly in mesh.polygons:
            poly.use_smooth = True
        obj = bpy.data.objects.new(f"{name}_{index:02d}", mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.data.materials.append(materials[index % len(materials)])
        shell = obj.modifiers.new("FX_SHELL", "SOLIDIFY")
        shell.thickness = radius * 0.08
        obj["factory_role"] = FX_ROLE
        chunks.append((obj, centroid))
    source.free()
    return chunks


def _hit_frame(root, y, end_frame):
    scene = bpy.context.scene
    for frame in range(1, end_frame + 1):
        scene.frame_set(frame)
        if root.matrix_world.translation.y >= y:
            return frame, root.matrix_world.translation.z
    return None, None


def _obstacle_ys():
    return [o.matrix_world.translation.y for o in bpy.context.scene.objects if o.name.startswith("OBSTACLE_SLOT_")]


def _ball_ys(count, rng, avoid):
    """Spread balls down the course, keeping clear of obstacle slots."""
    ys = []
    for i in range(count):
        for _ in range(30):
            y = -1.8 + 6.2 * (i + rng.uniform(0.15, 0.85)) / count
            if all(abs(y - a) > 1.3 for a in avoid) and all(abs(y - b) > 1.0 for b in ys):
                ys.append(y)
                break
    return ys


def add_ball_smash(actors, lanes, *, seed, end_frame, count=3):
    """Giant balls on the lanes; each bursts when the animal on that lane reaches it."""
    rng = random.Random(seed * 13 + 7)
    white = _material("FX_BALL_WHITE", (0.97, 0.97, 0.97), roughness=0.25, coat=0.8)
    placed = 0
    for i, y in enumerate(_ball_ys(count, rng, _obstacle_ys())):
        lane = lanes[i % len(lanes)]
        runner = min(actors, key=lambda a: abs(a["lane_x"] - lane))
        # Height from the runner when it is under the ball; burst when its head meets the near surface.
        _, feet_z = _hit_frame(runner["root"], y, end_frame)
        frame, _ = _hit_frame(runner["root"], y - BALL_RADIUS - 1.1, end_frame)
        if frame is None or feet_z is None:
            continue
        color = PAINT_PALETTE[(seed + i * 3) % len(PAINT_PALETTE)]
        patch = _material(f"FX_BALL_PATCH_{seed}_{i}", color, roughness=0.25, coat=0.8)
        centre = Vector((lane, y, feet_z + BALL_RADIUS + 0.02))
        for obj, offset in _ball_chunks(f"FX_BALL_{i}", BALL_RADIUS, [white, white, patch]):
            start = centre + offset
            obj.location = start
            obj.keyframe_insert("location", frame=1)
            obj.keyframe_insert("location", frame=frame)
            obj.keyframe_insert("rotation_euler", frame=frame)
            obj.keyframe_insert("scale", frame=frame + 10)
            direction = (offset.normalized() + Vector((0.0, 0.8, 0.9))).normalized()
            speed = rng.uniform(3.5, 6.0)
            spin = Vector((rng.uniform(-9, 9), rng.uniform(-9, 9), rng.uniform(-9, 9)))
            for step in range(2, 26, 3):
                t = step / 24.0
                obj.location = start + direction * speed * t + Vector((0, 0, -0.5 * GRAVITY * t * t))
                obj.keyframe_insert("location", frame=frame + step)
                obj.rotation_euler = spin * t
                obj.keyframe_insert("rotation_euler", frame=frame + step)
            obj.scale = (0.0, 0.0, 0.0)
            obj.keyframe_insert("scale", frame=frame + 24)
        cues.record(frame, "smash", lane=round(lane, 2))
        placed += 1
    bpy.context.scene.frame_set(1)
    print(f"FX_BALL_SMASH::{placed}")
    return placed


# ---------- clone parade helpers ----------

def tint_actor(objects, color, owner):
    """Recolour every material of one actor (own copies) with a COLOR blend."""
    copies: dict[str, bpy.types.Material] = {}
    for obj in objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or mat.get("fx_no_paint"):
                continue
            if mat.name not in copies:
                tinted = mat.copy()
                tinted["fx_paint_owner"] = owner
                ensure_node_material(tinted)
                tree = tinted.node_tree
                bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
                base = bsdf.inputs["Base Color"]
                mix = tree.nodes.new("ShaderNodeMix")
                mix.data_type = "RGBA"
                mix.blend_type = "COLOR"
                mix.inputs[0].default_value = 1.0
                if base.is_linked:
                    tree.links.new(base.links[0].from_socket, mix.inputs[6])
                else:
                    mix.inputs[6].default_value = tuple(base.default_value)
                mix.inputs[7].default_value = (color[0], color[1], color[2], 1.0)
                # A COLOR blend keeps the source brightness, so brown animals turn muddy;
                # pull part-way to the pure paint for bright toy colours.
                bright = tree.nodes.new("ShaderNodeMix")
                bright.data_type = "RGBA"
                bright.inputs[0].default_value = PAINT_BRIGHTNESS
                tree.links.new(mix.outputs[2], bright.inputs[6])
                bright.inputs[7].default_value = (color[0], color[1], color[2], 1.0)
                tree.links.new(bright.outputs[2], base)
                copies[mat.name] = tinted
            slot.material = copies[mat.name]


def pop_in(root, frame, *, length=5):
    """Cartoon pop: hidden (scale 0) until `frame`, overshoot, settle."""
    root.scale = (0.0, 0.0, 0.0)
    root.keyframe_insert("scale", frame=1)
    root.keyframe_insert("scale", frame=max(1, frame - 1))
    root.scale = (1.2, 1.2, 1.2)
    root.keyframe_insert("scale", frame=frame + length - 2)
    root.scale = (1.0, 1.0, 1.0)
    root.keyframe_insert("scale", frame=frame + length)
    cues.record(frame, "clone_pop")
