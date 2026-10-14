"""Character FX for Long Slide renders (runs inside Blender).

- cartoon eyes: big glossy eyes with pupils and a catch-light, parented to the
  head bone so they follow the animation, with irregular blinks;
- paint gates: hanging paint strips in the gate opening, a world-position wipe
  that recolours every animal as it passes, and a droplet splash.

Planning numbers come from long_slide_fx_plan (pure Python, unit-tested).
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
from mathutils import Matrix, Vector

import long_slide_events as cues
from long_slide_fx_plan import (
    blink_keys,
    blink_starts,
    curtain_strips,
    lane_for_x,
    paint_colors,
)

FX_ROLE = "fx"
EYE_HEAD_WEIGHT = 0.5
MIN_HEAD_VERTS = 8
EYE_RADIUS_OF_WIDTH = 0.19
EYE_DEPTH_FRACTION = 0.56
PAINT_BRIGHTNESS = 0.45


def _rgba(rgb, alpha=1.0):
    return (float(rgb[0]), float(rgb[1]), float(rgb[2]), alpha)


def _material(name, color, roughness=0.2, coat=0.0, emission=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = _rgba(color)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
    if emission:
        bsdf.inputs["Emission Color"].default_value = _rgba(color)
        bsdf.inputs["Emission Strength"].default_value = emission
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        if hasattr(mat, "surface_render_method"):
            mat.surface_render_method = "BLENDED"
    mat.diffuse_color = _rgba(color, alpha)
    return mat


def ensure_node_material(mat):
    """Older packs ship viewport-only materials; give them a Principled BSDF with the same look."""
    if mat.use_nodes and any(n.type == "BSDF_PRINCIPLED" for n in mat.node_tree.nodes):
        return mat
    color = tuple(mat.diffuse_color)
    roughness = float(getattr(mat, "roughness", 0.5))
    metallic = float(getattr(mat, "metallic", 0.0))
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        output = next((n for n in tree.nodes if n.type == "OUTPUT_MATERIAL"), None) or tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])
    bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def _sphere(name, radius, material, parent=None, location=(0, 0, 0), scale=(1, 1, 1)):
    mesh = bpy.data.meshes.get(f"FX_SPHERE_{radius:.4f}")
    if mesh is None:
        mesh = bpy.data.meshes.new(f"FX_SPHERE_{radius:.4f}")
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=14, radius=radius)
        bm.to_mesh(mesh)
        bm.free()
        for poly in mesh.polygons:
            poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    if not obj.data.materials:
        obj.data.materials.append(material)
    obj.material_slots[0].link = "OBJECT"
    obj.material_slots[0].material = material
    obj["factory_role"] = FX_ROLE
    obj.parent = parent
    obj.location = location
    obj.scale = scale
    return obj


# ---------- cartoon eyes ----------

def _head_bone(armature):
    if armature is None:
        return None
    bones = armature.data.bones
    exact = next((b for b in bones if b.name.lower() == "head"), None)
    if exact is not None:
        return exact
    return next((b for b in bones if "head" in b.name.lower() and "react" not in b.name.lower()), None)


def _deformed_points(meshes, group_name=None):
    """World-space vertex positions after the armature pose (optionally one vertex group)."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        group = obj.vertex_groups.get(group_name) if group_name else None
        if group_name and group is None:
            continue
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        try:
            if group is not None and len(mesh.vertices) != len(obj.data.vertices):
                continue
            world = evaluated.matrix_world
            for index, vertex in enumerate(mesh.vertices):
                if group is not None:
                    weight = next((g.weight for g in obj.data.vertices[index].groups if g.group == group.index), 0.0)
                    if weight < EYE_HEAD_WEIGHT:
                        continue
                points.append(world @ vertex.co)
        finally:
            evaluated.to_mesh_clear()
    return points


def _eye_placement(points):
    """Cartoon eyes on top of the forehead of a +Y-facing head, behind the snout."""
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]
    width = max(xs) - min(xs)
    height = max(zs) - min(zs)
    depth = max(ys) - min(ys)
    cx = (max(xs) + min(xs)) / 2.0
    radius = max(0.035, min(EYE_RADIUS_OF_WIDTH * width, 0.30 * height))
    y_eye = min(ys) + EYE_DEPTH_FRACTION * depth
    eyes = []
    for side in (-1.0, 1.0):
        x_eye = cx + side * 0.26 * width
        near = [p.z for p in points if abs(p.x - x_eye) < 0.2 * width and abs(p.y - y_eye) < 0.16 * depth]
        z_top = max(near) if near else min(zs) + 0.8 * height
        eyes.append((side, Vector((x_eye, y_eye, z_top - 0.3 * radius))))
    return eyes, radius


def _parent_keep_world(obj, armature, bone_name, fallback_parent):
    world = obj.matrix_world.copy()
    if armature is not None and bone_name:
        obj.parent = armature
        obj.parent_type = "BONE"
        obj.parent_bone = bone_name
    else:
        obj.parent = fallback_parent
    bpy.context.view_layer.update()
    obj.matrix_world = world


def _blink(roots, *, seed, fps, end_frame):
    base_scales = [root.scale.copy() for root in roots]
    for start in blink_starts(end_frame, fps, seed):
        for frame, lid in blink_keys(start):
            for root, base in zip(roots, base_scales):
                root.scale = (base.x, base.y, base.z * lid)
                root.keyframe_insert("scale", frame=frame)
    for root, base in zip(roots, base_scales):
        root.scale = base


def add_cartoon_eyes(name, objects, scale_root, *, seed, fps, end_frame):
    """Give one animal big blinking eyes. Returns the eye roots (may be empty)."""
    scene = bpy.context.scene
    built_in = [o for o in objects if o.get("factory_eye_root")]
    if built_in:
        # The channel's own toy animals ship their eyes; only add the blinks.
        _blink(built_in, seed=seed, fps=fps, end_frame=end_frame)
        print(f"FX_EYES::{name}:built-in:{len(built_in)}")
        return built_in
    scene.frame_set(1)
    bpy.context.view_layer.update()
    meshes = [o for o in objects if o.type == "MESH"]
    armature = next((o for o in objects if o.type == "ARMATURE"), None)
    bone = _head_bone(armature)
    points = _deformed_points(meshes, bone.name if bone else None) if bone else []
    if len(points) < MIN_HEAD_VERTS:
        # No usable head group: the head is the highest part of the front of the
        # body (forward is +Y after normalize_forward_axis).
        body = _deformed_points(meshes)
        if not body:
            return []
        y_front = max(p.y for p in body)
        length = y_front - min(p.y for p in body)
        front = [p for p in body if p.y >= y_front - 0.32 * length]
        if front:
            z_low, z_high = min(p.z for p in front), max(p.z for p in front)
            points = [p for p in front if p.z >= z_high - 0.45 * (z_high - z_low)]
        else:
            points = []
        bone = None
        if len(points) < MIN_HEAD_VERTS:
            print(f"FX_EYES_SKIPPED::{name}:no head region")
            return []
    eyes, radius = _eye_placement(points)

    sclera = _material("FX_EYE_WHITE", (0.96, 0.96, 0.96), roughness=0.12, coat=1.0)
    pupil = _material("FX_EYE_PUPIL", (0.015, 0.015, 0.02), roughness=0.08, coat=1.0)
    shine = _material("FX_EYE_SHINE", (1.0, 1.0, 1.0), roughness=0.1, emission=3.0)
    roots = []
    for side, centre in eyes:
        root = bpy.data.objects.new(f"{name}_EYE_{'L' if side < 0 else 'R'}", None)
        scene.collection.objects.link(root)
        root["factory_role"] = FX_ROLE
        root.matrix_world = Matrix.Translation(centre) @ Matrix.Rotation(math.radians(-12.0 * side), 4, "Z")
        _sphere(f"{root.name}_WHITE", radius, sclera, parent=root)
        _sphere(f"{root.name}_PUPIL", radius * 0.56, pupil, parent=root,
                location=(-side * radius * 0.08, radius * 0.80, -radius * 0.04), scale=(1.0, 0.42, 1.0))
        _sphere(f"{root.name}_SHINE", radius * 0.17, shine, parent=root,
                location=(radius * 0.18, radius * 1.02, radius * 0.24))
        bpy.context.view_layer.update()
        _parent_keep_world(root, armature, bone.name if bone else None, scale_root)
        roots.append(root)

    _blink(roots, seed=seed, fps=fps, end_frame=end_frame)
    scene["fx_eyes"] = int(scene.get("fx_eyes", 0)) + len(roots)
    print(f"FX_EYES::{name}:radius={radius:.3f}:head={'bone' if bone else 'body'}")
    return roots


# ---------- paint gates ----------

def _world_bbox(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    return (Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))),
            Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts))))


def find_paint_gates():
    """Trigger volumes tagged event=paint_transform, front to back along +Y."""
    bpy.context.view_layer.update()
    gates = []
    for obj in bpy.context.scene.objects:
        if obj.type == "MESH" and obj.get("event") == "paint_transform":
            mins, maxs = _world_bbox(obj)
            gates.append({"object": obj, "y": (mins.y + maxs.y) / 2.0, "x": (mins.x, maxs.x),
                          "z_top": maxs.z})
            obj.hide_render = True
            obj.hide_viewport = True
    return sorted(gates, key=lambda g: g["y"])


def _surface_z(x, y, fallback):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    hit, location, _, _, obj, _ = bpy.context.scene.ray_cast(depsgraph, Vector((x, y, 20.0)), Vector((0, 0, -1)), distance=40.0)
    if hit and obj is not None and obj.get("factory_role") not in {"animal", "companion", FX_ROLE}:
        return float(location.z)
    return fallback


def _surface_below(x, y, z_start, fallback):
    """First non-actor surface under (x, y) starting below the gate bar."""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    hit, location, _, _, obj, _ = bpy.context.scene.ray_cast(depsgraph, Vector((x, y, z_start)), Vector((0, 0, -1)), distance=30.0)
    if hit and obj is not None and obj.get("factory_role") not in {"animal", "companion", FX_ROLE}:
        return float(location.z)
    return fallback


def _gate_top(gate):
    """Underside of the gate's top bar if one sits above the trigger, else the trigger top."""
    y = gate["y"]
    best = None
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or "TOP" not in obj.name.upper():
            continue
        mins, maxs = _world_bbox(obj)
        if mins.y - 0.2 <= y <= maxs.y + 0.2 and mins.z >= gate["z_top"] - 0.5:
            best = mins.z if best is None else min(best, mins.z)
    return best if best is not None else gate["z_top"]


def _build_curtain(index, gate, lanes, colors):
    top = _gate_top(gate)
    x_min, x_max = gate["x"]
    created = []
    mesh = bpy.data.meshes.new(f"FX_GATE_{index}_STRIP")
    mesh.from_pydata([(-0.13, 0, -1), (0.13, 0, -1), (0.13, 0, 0), (-0.13, 0, 0)], [], [(0, 1, 2, 3)])
    for strip, x in enumerate(curtain_strips(x_min + 0.05, x_max - 0.05)):
        lane = lane_for_x(x, lanes)
        mat = _material(f"FX_PAINT_STRIP_{lane}_{index}", colors[lane], roughness=0.15, coat=0.6,
                        emission=0.25, alpha=0.82)
        obj = bpy.data.objects.new(f"FX_GATE_{index}_STRIP_{strip:02d}", mesh)
        bpy.context.scene.collection.objects.link(obj)
        if not obj.data.materials:
            obj.data.materials.append(mat)
        obj.material_slots[0].link = "OBJECT"
        obj.material_slots[0].material = mat
        floor = _surface_below(x, gate["y"], top - 0.05, top - 2.5) + 0.03
        obj.location = (x, gate["y"], top)
        obj.scale = (1.0, 1.0, max(0.2, top - floor))
        obj["factory_role"] = FX_ROLE
        created.append(obj)
    return created


def _paint_material(mat, gate_y, color, suffix):
    """Insert a world-Y wipe in front of Base Color: behind the gate keeps the original, past it is painted."""
    ensure_node_material(mat)
    tree = mat.node_tree
    bsdf = next((n for n in tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    base_input = bsdf.inputs["Base Color"]
    source = base_input.links[0].from_socket if base_input.is_linked else None
    original = tuple(base_input.default_value)

    geometry = tree.nodes.new("ShaderNodeNewGeometry")
    split = tree.nodes.new("ShaderNodeSeparateXYZ")
    wipe = tree.nodes.new("ShaderNodeMapRange")
    mix = tree.nodes.new("ShaderNodeMix")
    mix.name = f"FX_PAINT_MIX_{suffix}"
    mix.data_type = "RGBA"
    mix.blend_type = "COLOR"
    mix.clamp_result = True
    wipe.clamp = True
    wipe.inputs["From Min"].default_value = gate_y - 0.08
    wipe.inputs["From Max"].default_value = gate_y + 0.08
    wipe.inputs["To Min"].default_value = 0.0
    wipe.inputs["To Max"].default_value = 1.0
    tree.links.new(geometry.outputs["Position"], split.inputs["Vector"])
    tree.links.new(split.outputs["Y"], wipe.inputs["Value"])
    tree.links.new(wipe.outputs["Result"], mix.inputs["Factor"])
    a_socket = mix.inputs[6]  # RGBA "A"
    b_socket = mix.inputs[7]  # RGBA "B"
    if source is not None:
        tree.links.new(source, a_socket)
    else:
        a_socket.default_value = original
    b_socket.default_value = _rgba(color)
    # Lift dark animals towards the pure paint (behind the wipe the factor is 0, so the original stays).
    bright = tree.nodes.new("ShaderNodeMix")
    bright.data_type = "RGBA"
    bright.clamp_result = True
    lift = tree.nodes.new("ShaderNodeMath")
    lift.operation = "MULTIPLY"
    lift.inputs[1].default_value = PAINT_BRIGHTNESS
    tree.links.new(wipe.outputs["Result"], lift.inputs[0])
    tree.links.new(lift.outputs[0], bright.inputs[0])
    tree.links.new(mix.outputs[2], bright.inputs[6])
    bright.inputs[7].default_value = _rgba(color)
    tree.links.new(bright.outputs[2], base_input)


def _crossing_frame(root, gate_y, end_frame):
    scene = bpy.context.scene
    for frame in range(1, end_frame + 1):
        scene.frame_set(frame)
        if root.matrix_world.translation.y >= gate_y:
            return frame
    return None


def _splash(name, origin, color, frame, seed, count=12):
    cues.record(frame, "paint_splash")
    rng = random.Random(seed)
    mat = _material(f"FX_PAINT_DROP_{name}", color, roughness=0.12, coat=0.8, emission=0.3)
    for i in range(count):
        drop = _sphere(f"FX_DROP_{name}_{i:02d}", 0.075, mat, location=origin, scale=(0, 0, 0))
        angle = rng.uniform(0, 2 * math.pi)
        spread = rng.uniform(0.6, 1.4)
        end = origin + Vector((math.cos(angle) * spread, rng.uniform(-0.3, 0.5), abs(math.sin(angle)) * spread + 0.3))
        size = rng.uniform(0.7, 1.4)
        drop.keyframe_insert("scale", frame=max(1, frame - 1))
        drop.keyframe_insert("location", frame=max(1, frame - 1))
        drop.scale = (size, size, size)
        drop.keyframe_insert("scale", frame=frame + 2)
        drop.location = end
        drop.keyframe_insert("location", frame=frame + 9)
        drop.scale = (0, 0, 0)
        drop.keyframe_insert("scale", frame=frame + 12)


def apply_paint_gates(actors, lanes, *, seed, end_frame):
    """actors: [{"name", "objects", "root", "lane_x"}]. Recolours each actor past every gate."""
    gates = find_paint_gates()
    if not gates:
        return 0
    for index, gate in enumerate(gates):
        colors = paint_colors(len(lanes), seed + index * 101)
        _build_curtain(index, gate, lanes, colors)
        for actor in actors:
            lane = lane_for_x(actor["lane_x"], lanes)
            color = colors[lane]
            copies: dict[str, bpy.types.Material] = {}
            painted: set[str] = set()
            for obj in actor["objects"]:
                if obj.type != "MESH":
                    continue
                for slot in obj.material_slots:
                    mat = slot.material
                    if mat is None or mat.get("fx_no_paint"):
                        continue
                    if mat.get("fx_paint_owner") != actor["name"]:
                        # Own copy per actor so one animal's paint never leaks onto another.
                        if mat.name not in copies:
                            copies[mat.name] = mat.copy()
                            copies[mat.name]["fx_paint_owner"] = actor["name"]
                        mat = copies[mat.name]
                        slot.material = mat
                    if mat.name not in painted:
                        _paint_material(mat, gate["y"], color, f"{index}")
                        painted.add(mat.name)
            frame = _crossing_frame(actor["root"], gate["y"], end_frame)
            if frame is not None:
                # Splash at the animal's body (its root is at the feet), not on top of the gate bar.
                feet = actor["root"].matrix_world.translation
                origin = Vector((actor["lane_x"], gate["y"], feet.z + 0.9))
                _splash(f"{index}_{actor['name']}", origin, color, frame, seed + index * 13 + lane)
                bpy.context.scene.frame_set(1)
    bpy.context.scene["fx_paint_gates"] = len(gates)
    print(f"FX_PAINT_GATES::{len(gates)}:actors={len(actors)}")
    return len(gates)
