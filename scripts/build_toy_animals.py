"""Build the channel's own toy-style animals as rigged, animated .blend files.

    blender --background --factory-startup --python scripts/build_toy_animals.py -- OUT_DIR [species ...]

Each animal is assembled from smooth rounded parts (subdivided, smooth shaded,
glossy vinyl material, soft black outline), with built-in big eyes. Parts are
rigidly parented to an armature (toy articulation, no weight painting), and a
"Run" trot plus an "Idle" breath action are keyframed on the bones. The
result plugs into the existing worker: it finds the "Head" bone, the "Run"
action and the eye roots (tagged factory_eye_root) for blinking.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from toy_animal_specs import BODY_BOB, LEG_PHASE, LEG_SWING_DEG, RUN_FRAMES, SPECS, spec  # noqa: E402

OUTLINE = 0.012
EYE_WHITE = (0.98, 0.98, 0.98)
PUPIL = (0.02, 0.02, 0.03)


# ---------- materials ----------

def _principled(name, color, roughness=0.42, coat=0.12):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
    mat.diffuse_color = (*color, 1.0)
    return mat


def _pattern(name, base, ink, kind):
    """Spots (voronoi) or stripes (wave) in object space, ink on base."""
    mat = _principled(name, base)
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    coords = tree.nodes.new("ShaderNodeTexCoord")
    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].color = (*ink, 1.0)
    ramp.color_ramp.elements[1].color = (*base, 1.0)
    if kind == "spots":
        tex = tree.nodes.new("ShaderNodeTexVoronoi")
        tex.inputs["Scale"].default_value = 2.6
        tree.links.new(coords.outputs["Object"], tex.inputs["Vector"])
        ramp.color_ramp.elements[1].position = 0.42
        tree.links.new(tex.outputs["Distance"], ramp.inputs["Fac"])
    else:
        tex = tree.nodes.new("ShaderNodeTexWave")
        tex.bands_direction = "Y"
        tex.inputs["Scale"].default_value = 3.2
        tex.inputs["Distortion"].default_value = 6.0
        tex.inputs["Detail"].default_value = 1.5
        tree.links.new(coords.outputs["Object"], tex.inputs["Vector"])
        ramp.color_ramp.elements[1].position = 0.32
        tree.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return mat


def _outline_material():
    mat = bpy.data.materials.get("TOY_OUTLINE")
    if mat is None:
        mat = _principled("TOY_OUTLINE", (0.03, 0.03, 0.04), roughness=1.0, coat=0.0)
        mat.use_backface_culling = True
        mat["fx_no_paint"] = True  # paint gates and tints must leave the outline black
    return mat


# ---------- parts ----------

def _finish(obj, mat, *, outline=True, subdiv=2):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.select_set(False)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    obj.data.materials.append(mat)
    sub = obj.modifiers.new("TOY_SMOOTH", "SUBSURF")
    sub.levels = 1
    sub.render_levels = subdiv
    if outline:
        obj.data.materials.append(_outline_material())
        hull = obj.modifiers.new("TOY_OUTLINE", "SOLIDIFY")
        hull.thickness = OUTLINE
        hull.offset = 1.0
        hull.use_flip_normals = True
        hull.material_offset = 1
    obj["factory_role"] = "animal_part"
    return obj


def _ellipsoid(name, center, radii, mat, *, rotation=(0, 0, 0), outline=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.0, location=center, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = radii
    return _finish(obj, mat, outline=outline)


def _cone(name, center, radius, depth, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=radius, radius2=radius * 0.15, depth=depth,
                                    location=center, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    return _finish(obj, mat, subdiv=1)


def _tube(name, points, radius, mat):
    """A tapered smooth tube along points (trunk, tail)."""
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = radius
    curve.bevel_resolution = 6
    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(points) - 1)
    for i, (point, r) in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = point
        bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = r
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.object
    obj.select_set(False)
    return _finish(obj, mat, subdiv=1)


# ---------- assembly ----------

def build(species: str):
    s = spec(species)
    bx, by, bz = s.body
    hip = s.leg_length
    body_z = hip + bz * 0.75
    head_y = by * 0.92
    head_z = body_z + bz * 0.9 + s.head_radius * 0.35
    hr = s.head_radius

    skin = _pattern(f"{species}_skin", s.skin, s.pattern_color, s.pattern) if s.pattern != "none" else _principled(f"{species}_skin", s.skin)
    belly = _principled(f"{species}_belly", s.belly)
    snout_mat = _principled(f"{species}_snout", s.snout_color, roughness=0.3)
    dark = _principled(f"{species}_dark", (0.08, 0.06, 0.07), roughness=0.4)
    horn = _principled(f"{species}_horn", (0.98, 0.93, 0.80), roughness=0.3)
    parts: dict[str, list] = {"Body": [], "Head": [], "Leg_FL": [], "Leg_FR": [], "Leg_BL": [], "Leg_BR": [],
                              "Tail": [], "Ear_L": [], "Ear_R": [], "Trunk": []}

    parts["Body"].append(_ellipsoid(f"{species}_body", (0, 0, body_z), (bx, by, bz), skin))
    parts["Body"].append(_ellipsoid(f"{species}_bellypatch", (0, by * 0.05, body_z - bz * 0.35), (bx * 0.8, by * 0.75, bz * 0.62), belly, outline=False))
    parts["Head"].append(_ellipsoid(f"{species}_head", (0, head_y, head_z), (hr, hr * 0.95, hr * 0.92), skin))
    if any(s.snout):
        sx, sy, sz = s.snout
        parts["Head"].append(_ellipsoid(f"{species}_snout", (0, head_y + hr * 0.82, head_z - hr * 0.32), (sx, sy, sz), snout_mat))
        for side in (-1, 1):
            parts["Head"].append(_ellipsoid(f"{species}_nostril_{side}", (side * sx * 0.38, head_y + hr * 0.82 + sy * 0.92, head_z - hr * 0.26),
                                            (sx * 0.12, sy * 0.08, sz * 0.18), dark, outline=False))
    # Eyes: big, on the face front, slightly apart; roots tagged for blinking.
    eye_r = hr * 0.27
    eye_roots = []
    for side in (-1, 1):
        root = bpy.data.objects.new(f"{species}_eye_{'L' if side < 0 else 'R'}", None)
        bpy.context.scene.collection.objects.link(root)
        root.location = (side * hr * 0.40, head_y + hr * 0.70, head_z + hr * 0.18)
        root.rotation_euler = (0, 0, math.radians(-14 * side))
        root["factory_eye_root"] = True
        white = _ellipsoid(f"{species}_eyewhite_{side}", (0, 0, 0), (eye_r, eye_r * 0.8, eye_r * 1.1), _principled("TOY_EYE", EYE_WHITE, roughness=0.12, coat=1.0))
        pupil = _ellipsoid(f"{species}_pupil_{side}", (0, 0, 0), (eye_r * 0.55, eye_r * 0.3, eye_r * 0.66), _principled("TOY_PUPIL", PUPIL, roughness=0.1, coat=1.0), outline=False)
        shine = _ellipsoid(f"{species}_shine_{side}", (0, 0, 0), (eye_r * 0.17, eye_r * 0.1, eye_r * 0.2), _principled("TOY_SHINE", (1, 1, 1), roughness=0.05), outline=False)
        for obj, offset in ((white, (0, 0, 0)), (pupil, (-side * eye_r * 0.08, eye_r * 0.62, -eye_r * 0.05)),
                            (shine, (eye_r * 0.16, eye_r * 0.86, eye_r * 0.32))):
            obj.parent = root
            obj.location = offset
        eye_roots.append(root)
        parts["Head"].append(root)

    ear = s.ear_size
    for side, bone in ((-1, "Ear_L"), (1, "Ear_R")):
        base = Vector((side * hr * 0.62, head_y - hr * 0.05, head_z + hr * 0.62))
        if s.ears == "round":
            parts[bone].append(_ellipsoid(f"{species}_ear_{side}", base, (ear, ear * 0.4, ear), skin, rotation=(0, side * 0.35, 0)))
        elif s.ears == "pointy":
            parts[bone].append(_cone(f"{species}_ear_{side}", base + Vector((0, 0, ear * 0.5)), ear * 0.75, ear * 1.6, skin, rotation=(0, side * 0.45, 0)))
        elif s.ears == "floppy":
            parts[bone].append(_ellipsoid(f"{species}_ear_{side}", Vector((side * hr * 1.05, head_y - hr * 0.1, head_z + hr * 0.25)),
                                          (ear * 1.2, ear * 0.35, ear * 0.6), skin, rotation=(0, side * -0.35, 0)))
        elif s.ears == "big_disc":
            parts[bone].append(_ellipsoid(f"{species}_ear_{side}", Vector((side * hr * 1.0, head_y - hr * 0.3, head_z + hr * 0.05)),
                                          (ear * 0.18, ear * 0.85, ear * 1.0), skin, rotation=(0, 0, side * -0.5)))

    leg_x, leg_y = bx * 0.55, by * 0.55
    for name, (sx, sy) in {"Leg_FL": (-1, 1), "Leg_FR": (1, 1), "Leg_BL": (-1, -1), "Leg_BR": (1, -1)}.items():
        x, y = sx * leg_x, sy * leg_y
        parts[name].append(_ellipsoid(f"{species}_{name.lower()}", (x, y, hip * 0.5 + s.leg_radius * 0.4),
                                      (s.leg_radius, s.leg_radius, hip * 0.55 + s.leg_radius * 0.4), skin))
        parts[name].append(_ellipsoid(f"{species}_{name.lower()}_hoof", (x, y + s.leg_radius * 0.15, s.leg_radius * 0.55),
                                      (s.leg_radius * 1.1, s.leg_radius * 1.25, s.leg_radius * 0.6), dark))

    tail_root = Vector((0, -by * 0.95, body_z + bz * 0.3))
    if s.tail in {"thin", "tuft"}:
        parts["Tail"].append(_tube(f"{species}_tail", [(tail_root, 1.0), (tail_root + Vector((0, -0.18, 0.12)), 0.8),
                                                       (tail_root + Vector((0, -0.3, 0.05)), 0.5)], 0.03, skin))
        if s.tail == "tuft":
            parts["Tail"].append(_ellipsoid(f"{species}_tuft", tail_root + Vector((0, -0.33, 0.03)), (0.05, 0.06, 0.07), dark))
    elif s.tail == "curl":
        parts["Tail"].append(_tube(f"{species}_tail", [(tail_root, 1.0), (tail_root + Vector((0.06, -0.1, 0.08)), 0.8),
                                                       (tail_root + Vector((-0.02, -0.14, 0.14)), 0.6)], 0.025, skin))
    elif s.tail == "stub":
        parts["Tail"].append(_ellipsoid(f"{species}_tail", tail_root + Vector((0, -0.02, 0)), (0.05, 0.05, 0.05), skin))

    if "horns" in s.features:
        for side in (-1, 1):
            parts["Head"].append(_cone(f"{species}_horn_{side}", (side * hr * 0.42, head_y - hr * 0.1, head_z + hr * 0.95),
                                       hr * 0.12, hr * 0.32, horn, rotation=(0, side * 0.5, 0)))
    if "trunk" in s.features:
        tip = Vector((0, head_y + hr * 1.55, head_z - hr * 0.9))
        parts["Trunk"].append(_tube(f"{species}_trunk", [(Vector((0, head_y + hr * 0.75, head_z - hr * 0.15)), 1.0),
                                                         (Vector((0, head_y + hr * 1.25, head_z - hr * 0.55)), 0.75),
                                                         (tip, 0.55), (tip + Vector((0, 0.08, 0.1)), 0.5)], hr * 0.2, skin))
    if "tusks" in s.features:
        for side in (-1, 1):
            parts["Head"].append(_cone(f"{species}_tusk_{side}", (side * hr * 0.32, head_y + hr * 0.8, head_z - hr * 0.55),
                                       hr * 0.07, hr * 0.32, horn, rotation=(math.radians(-110), 0, 0)))
    if "mane" in s.features:
        mane = _principled(f"{species}_mane", (0.78, 0.36, 0.10), roughness=0.55, coat=0.1)
        for k in range(14):
            a = k / 14 * math.tau
            parts["Head"].append(_ellipsoid(f"{species}_mane_{k}", (math.cos(a) * hr * 1.0, head_y - hr * 0.15, head_z + math.sin(a) * hr * 1.0),
                                            (hr * 0.34, hr * 0.3, hr * 0.34), mane))
    if "mane_strip" in s.features:
        parts["Head"].append(_ellipsoid(f"{species}_mane", (0, head_y - hr * 0.6, head_z + hr * 0.55), (hr * 0.12, hr * 0.7, hr * 0.25), dark))

    arm = _armature(species, s, body_z, head_y, head_z, hip, leg_x, leg_y, tail_root)
    _bind(arm, parts)
    _animate(arm, s)
    return arm


def _armature(species, s, body_z, head_y, head_z, hip, leg_x, leg_y, tail_root):
    data = bpy.data.armatures.new(f"{species}_rig")
    arm = bpy.data.objects.new(f"{species}_Armature", data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    eb = data.edit_bones

    def bone(name, head, tail, parent=None):
        b = eb.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        b.roll = 0.0
        if parent:
            b.parent = eb[parent]
        return b

    bone("Root", (0, 0, 0), (0, 0.25, 0))
    bone("Body", (0, -0.1, body_z), (0, 0.25, body_z), "Root")
    bone("Head", (0, head_y - s.head_radius * 0.4, head_z - s.head_radius * 0.5), (0, head_y, head_z + s.head_radius * 0.6), "Body")
    for name, (sx, sy) in {"Leg_FL": (-1, 1), "Leg_FR": (1, 1), "Leg_BL": (-1, -1), "Leg_BR": (1, -1)}.items():
        bone(name, (sx * leg_x, sy * leg_y, hip + 0.04), (sx * leg_x, sy * leg_y, 0.02), "Body")
    bone("Tail", tuple(tail_root), tuple(tail_root + Vector((0, -0.25, 0.1))), "Body")
    for name, side in (("Ear_L", -1), ("Ear_R", 1)):
        bone(name, (side * s.head_radius * 0.55, head_y, head_z + s.head_radius * 0.5),
             (side * s.head_radius * 0.75, head_y, head_z + s.head_radius * 0.85), "Head")
    bone("Trunk", (0, head_y + s.head_radius * 0.7, head_z - s.head_radius * 0.15),
         (0, head_y + s.head_radius * 1.5, head_z - s.head_radius * 0.8), "Head")
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in arm.pose.bones:
        b.rotation_mode = "XYZ"
    return arm


def _bind(arm, parts):
    bpy.context.view_layer.update()
    for bone_name, objects in parts.items():
        for obj in objects:
            world = obj.matrix_world.copy()
            obj.parent = arm
            obj.parent_type = "BONE"
            obj.parent_bone = bone_name
            bpy.context.view_layer.update()
            obj.matrix_world = world


def _key(arm, frame, values):
    for name, attr, index, value in values:
        pb = arm.pose.bones.get(name)
        if pb is None:
            continue
        getattr(pb, attr)[index] = value
        pb.keyframe_insert(attr, index=index, frame=frame)


def _animate(arm, s):
    arm.animation_data_create()
    run = bpy.data.actions.new("Run")
    run.use_fake_user = True
    arm.animation_data.action = run
    swing = math.radians(LEG_SWING_DEG)
    for f in range(0, RUN_FRAMES + 1, 2):
        p = f / RUN_FRAMES
        values = [(leg, "rotation_euler", 0, math.sin(math.tau * (p + phase)) * swing) for leg, phase in LEG_PHASE.items()]
        values += [
            ("Body", "location", 2, (0.5 + 0.5 * math.cos(2 * math.tau * p)) * BODY_BOB),
            ("Body", "rotation_euler", 0, math.sin(2 * math.tau * p) * math.radians(2.5)),
            ("Head", "rotation_euler", 0, math.sin(2 * math.tau * p + 0.8) * math.radians(5)),
            ("Tail", "rotation_euler", 2, math.sin(math.tau * p) * math.radians(25)),
            ("Ear_L", "rotation_euler", 1, math.sin(2 * math.tau * p + 1.2) * math.radians(12)),
            ("Ear_R", "rotation_euler", 1, -math.sin(2 * math.tau * p + 1.2) * math.radians(12)),
            ("Trunk", "rotation_euler", 0, math.sin(math.tau * p) * math.radians(14)),
        ]
        _key(arm, f + 1, values)
    for curve in run.fcurves:
        curve.modifiers.new("CYCLES")
    idle = bpy.data.actions.new("Idle")
    idle.use_fake_user = True
    arm.animation_data.action = idle
    for f in (1, 25, 49):
        breath = 0.0 if f != 25 else 1.0
        _key(arm, f, [("Body", "location", 2, breath * 0.015), ("Head", "rotation_euler", 0, breath * math.radians(3)),
                      ("Tail", "rotation_euler", 2, (breath - 0.5) * math.radians(20))])
    for curve in idle.fcurves:
        curve.modifiers.new("CYCLES")
    arm.animation_data.action = run


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    for species in argv[1:] or list(SPECS):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        build(species)
        path = out / f"toy_{species}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
        print(f"TOY_ANIMAL_OK::{species}:{path}")


if __name__ == "__main__":
    main()
