"""Build one continuous long slide and its natural world in Blender.

Geometry comes from long_slide_course_plan (pure Python): a winding,
descending centreline. Cross-section profiles are swept along it to make the
six rainbow lanes, white separators, side walls and an underside slab; pillars
hold it up; the world around it is deliberately calm (grass, soft hills, a few
real trees, blue sky with clouds) so the track carries the colour.
"""
from __future__ import annotations

import math
import random

import bmesh
import bpy
from mathutils import Vector

import colorsys

from long_slide_course_plan import (
    LANE_COAT,
    LANE_COLORS,
    LANE_ROUGHNESS,
    LANE_SPECULAR,
    LANE_WIDTH,
    SEPARATOR_WIDTH,
    TRACK_WIDTH,
    WALL_HEIGHT,
    WALL_WIDTH,
    WORLD,
    offset_point,
)

COURSE_ROLE = "course"


def _rgba(c, a=1.0):
    return (c[0], c[1], c[2], a)


def _material(name, color, roughness=0.35, coat=0.0, emission=0.0, specular=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = _rgba(color)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = coat
    if specular is not None and "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = specular
    if emission:
        bsdf.inputs["Emission Color"].default_value = _rgba(color)
        bsdf.inputs["Emission Strength"].default_value = emission
    mat.diffuse_color = _rgba(color)
    return mat


def _sweep(name, samples, profile, material, *, role=COURSE_ROLE):
    """Extrude a 2D profile [(lateral, dz), ...] along the centreline into one mesh."""
    bm = bmesh.new()
    rows = []
    for sample in samples:
        row = []
        for lateral, dz in profile:
            x, y, z = offset_point(sample, lateral)
            row.append(bm.verts.new((x, y, z + dz)))
        rows.append(row)
    for a, b in zip(rows, rows[1:]):
        for j in range(len(profile) - 1):
            bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
    bm.normal_update()
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    for poly in mesh.polygons:
        poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj["factory_role"] = role
    return obj


def _pbr_material(name, maps, *, scale, tint=None, macro=None, normal_strength=0.6):
    """Image-texture PBR material in object space (no UVs needed), with optional macro variation."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    coords = tree.nodes.new("ShaderNodeTexCoord")
    mapping = tree.nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (scale, scale, scale)
    tree.links.new(coords.outputs["Object"], mapping.inputs["Vector"])

    def image(key, colorspace):
        node = tree.nodes.new("ShaderNodeTexImage")
        node.image = bpy.data.images.load(maps[key], check_existing=True)
        node.image.colorspace_settings.name = colorspace
        node.projection = "BOX"
        node.projection_blend = 0.2
        tree.links.new(mapping.outputs["Vector"], node.inputs["Vector"])
        return node

    colour = image("diff", "sRGB").outputs["Color"]
    if macro is not None:
        # Large-scale light/dark patches break up visible tiling from the air.
        noise = tree.nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = macro
        ramp = tree.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (0.72, 0.72, 0.72, 1.0)
        ramp.color_ramp.elements[1].color = (1.08, 1.08, 1.08, 1.0)
        tree.links.new(coords.outputs["Object"], noise.inputs["Vector"])
        tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
        vary = tree.nodes.new("ShaderNodeMix")
        vary.data_type = "RGBA"
        vary.blend_type = "MULTIPLY"
        vary.inputs[0].default_value = 1.0
        tree.links.new(colour, vary.inputs[6])
        tree.links.new(ramp.outputs["Color"], vary.inputs[7])
        colour = vary.outputs[2]
    if tint is not None:
        tinted = tree.nodes.new("ShaderNodeMix")
        tinted.data_type = "RGBA"
        tinted.blend_type = "MULTIPLY"
        tinted.inputs[0].default_value = 1.0
        tree.links.new(colour, tinted.inputs[6])
        tinted.inputs[7].default_value = _rgba(tint)
        colour = tinted.outputs[2]
    tree.links.new(colour, bsdf.inputs["Base Color"])
    rough = tree.nodes.new("ShaderNodeMath")
    rough.operation = "MULTIPLY_ADD"
    rough.inputs[1].default_value = 0.6
    rough.inputs[2].default_value = 0.35
    tree.links.new(image("rough", "Non-Color").outputs["Color"], rough.inputs[0])
    tree.links.new(rough.outputs[0], bsdf.inputs["Roughness"])
    normal = tree.nodes.new("ShaderNodeNormalMap")
    normal.inputs["Strength"].default_value = normal_strength
    tree.links.new(image("nor", "Non-Color").outputs["Color"], normal.inputs["Color"])
    tree.links.new(normal.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def _hdri_world(world, path, *, strength=1.0, rotation=0.0):
    nt = world.node_tree
    nt.nodes.clear()
    coords = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (0.0, 0.0, rotation)
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(path, check_existing=True)
    background = nt.nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = strength
    output = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(coords.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], background.inputs["Color"])
    nt.links.new(background.outputs["Background"], output.inputs["Surface"])


def build_track(samples, textures=None):
    half = TRACK_WIDTH / 2
    for lane, color in enumerate(LANE_COLORS):
        left = -half + lane * LANE_WIDTH
        _sweep(f"COURSE_LANE_{lane}", samples, [(left, 0.0), (left + LANE_WIDTH, 0.0)],
               _material(f"COURSE_LANE_{lane}", color, roughness=LANE_ROUGHNESS, coat=LANE_COAT,
                         specular=LANE_SPECULAR))
    white = _material("COURSE_SEPARATOR", WORLD["separator"], roughness=0.3)
    for k in range(1, len(LANE_COLORS)):
        c = -half + k * LANE_WIDTH
        _sweep(f"COURSE_SEP_{k}", samples, [(c - SEPARATOR_WIDTH / 2, 0.012), (c + SEPARATOR_WIDTH / 2, 0.012)], white)
    wall = _material("COURSE_WALL", WORLD["wall"], roughness=0.25, coat=0.4)
    for side in (-1, 1):
        inner, outer = side * half, side * (half + WALL_WIDTH)
        profile = [(inner, -0.02), (inner, WALL_HEIGHT), (outer, WALL_HEIGHT), (outer, -0.42)]
        if side < 0:
            profile = profile[::-1]
        _sweep(f"COURSE_WALL_{'L' if side < 0 else 'R'}", samples, profile, wall)
    base = _material("COURSE_BASE", (0.82, 0.83, 0.86), roughness=0.5)
    edge = half + WALL_WIDTH
    _sweep("COURSE_BASE", samples, [(edge, -0.42), (-edge, -0.42)], base)
    if textures and "concrete" in textures:
        pillar = _pbr_material("COURSE_PILLAR", textures["concrete"], scale=0.6, tint=(1.05, 1.05, 1.08))
    else:
        pillar = _material("COURSE_PILLAR", WORLD["pillar"], roughness=0.45)
    for sample in samples[6::12]:
        for lateral in (-half + 0.6, half - 0.6):
            x, y, z = offset_point(sample, lateral)
            height = z - 0.42
            if height < 0.5:
                continue
            bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.28, depth=height, location=(x, y, height / 2))
            obj = bpy.context.object
            obj.name = "COURSE_PILLAR"
            obj.data.materials.append(pillar)
            obj["factory_role"] = COURSE_ROLE


def _grass_material():
    mat = bpy.data.materials.new("COURSE_GRASS")
    mat.use_nodes = True
    tree = mat.node_tree
    bsdf = next(n for n in tree.nodes if n.type == "BSDF_PRINCIPLED")
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.015
    noise.inputs["Detail"].default_value = 3.0
    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = _rgba(WORLD["grass"][0])
    ramp.color_ramp.elements[1].color = _rgba(WORLD["grass"][1])
    tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85
    return mat


def build_world(scene, samples, *, seed, tree_rows=(), textures=None):
    """Ground, sky, hills, clouds and real trees kept clear of the track.

    With `textures` (CC0 Poly Haven files) the sky is a real HDRI that also
    lights the scene, and the ground uses a photographic grass texture.
    """
    textures = textures or {}
    bpy.ops.mesh.primitive_plane_add(size=1600, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "GROUND"
    if "grass" in textures:
        ground.data.materials.append(_pbr_material("COURSE_GRASS", textures["grass"], scale=0.28,
                                                   tint=(0.82, 0.9, 0.72), macro=0.012))
    else:
        ground.data.materials.append(_grass_material())

    world = scene.world or bpy.data.worlds.new("COURSE_WORLD")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    coords = nt.nodes.new("ShaderNodeTexCoord")
    split = nt.nodes.new("ShaderNodeSeparateXYZ")
    remap = nt.nodes.new("ShaderNodeMapRange")
    remap.inputs["From Min"].default_value = 0.0
    remap.inputs["From Max"].default_value = 0.6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = _rgba(WORLD["sky_horizon"])
    ramp.color_ramp.elements[1].color = _rgba(WORLD["sky_top"])
    background = nt.nodes.new("ShaderNodeBackground")
    output = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(coords.outputs["Generated"], split.inputs["Vector"])
    nt.links.new(split.outputs["Z"], remap.inputs["Value"])
    nt.links.new(remap.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], background.inputs["Color"])
    nt.links.new(background.outputs["Background"], output.inputs["Surface"])
    if "hdri" in textures:
        # Sky only: keep it dim enough that it does not wash out the lanes.
        _hdri_world(world, textures["hdri"], strength=0.55, rotation=math.radians(150))

    bpy.ops.object.light_add(type="SUN", location=(0, 0, 50))
    sun = bpy.context.object
    sun.name = "LONG_SLIDE_SUN"
    sun.data.energy = 2.4 if "hdri" in textures else 2.7
    sun.data.color = (1.0, 0.97, 0.92)
    sun.data.angle = math.radians(3.0)
    sun.rotation_euler = (math.radians(38), 0.0, math.radians(35))

    rng = random.Random(seed * 31 + 3)
    cx = sum(s.x for s in samples) / len(samples)
    cy = sum(s.y for s in samples) / len(samples)
    hills = _material("COURSE_HILLS", WORLD["hills"], roughness=0.9)
    for i in range(14):
        angle = i * math.tau / 14 + rng.uniform(-0.15, 0.15)
        radius = rng.uniform(170, 240)
        size = rng.uniform(40, 75)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1.0,
                                             location=(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, -4))
        hill = bpy.context.object
        hill.scale = (size, size, rng.uniform(12, 24))
        hill.data.materials.append(hills)
        bpy.ops.object.shade_smooth()
    cloud = _material("COURSE_CLOUD", (1.0, 1.0, 1.0), roughness=0.9, emission=0.6)
    for i in range(0 if "hdri" in textures else 16):  # the HDRI brings real clouds
        angle = rng.uniform(0, math.tau)
        radius = rng.uniform(90, 200)
        base = Vector((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius, rng.uniform(38, 60)))
        for k in range(4):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=10, radius=1.0,
                                                 location=base + Vector((k * 5 - 7, rng.uniform(-2, 2), rng.uniform(-1, 1.5))))
            puff = bpy.context.object
            r = rng.uniform(4, 7)
            puff.scale = (r * 1.3, r, r * 0.7)
            puff.data.materials.append(cloud)
            bpy.ops.object.shade_smooth()
    if tree_rows:
        _plant_trees(samples, tree_rows, rng)


def _unify_foliage(protos):
    """Pull every green canopy material to one natural green; trunks keep their colour."""
    done = set()
    for proto in protos:
        for obj in proto["collection"].all_objects:
            for slot in getattr(obj, "material_slots", []):
                mat = slot.material
                if mat is None or mat.name in done or not mat.use_nodes:
                    continue
                bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
                if bsdf is None or bsdf.inputs["Base Color"].is_linked:
                    continue
                r, g, b, _ = bsdf.inputs["Base Color"].default_value
                hue, sat, _ = colorsys.rgb_to_hsv(r, g, b)
                if 0.2 <= hue <= 0.55 and sat > 0.2:  # green to teal
                    bsdf.inputs["Base Color"].default_value = (*WORLD["foliage"], 1.0)
                    bsdf.inputs["Roughness"].default_value = 0.8
                done.add(mat.name)


def _plant_trees(samples, rows, rng):
    from long_slide_props import _import, _instance, _proto_collection

    protos = [p for p in (_import(row, _proto_collection()) for row in rows) if p is not None]
    if not protos:
        return
    _unify_foliage(protos)
    clear = TRACK_WIDTH / 2 + WALL_WIDTH + 3.5
    for sample in samples[::5]:
        for side in (-1, 1):
            if rng.random() < 0.35:
                continue
            lateral = side * rng.uniform(clear, clear + 16)
            x, y, _ = offset_point(sample, lateral)
            if min((x - s.x) ** 2 + (y - s.y) ** 2 for s in samples[::3]) < clear ** 2:
                continue  # too close to another part of a winding track
            proto = rng.choice(protos)
            _instance(proto, "COURSE_TREE", (x, y, 0.0), rng.uniform(4.0, 7.0), rng.uniform(0, math.tau))
