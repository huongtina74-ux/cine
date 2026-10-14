"""Look development for Long Slide renders (runs inside Blender).

Turns the bare internal slide scene into a bright, toy-like world modelled on
what leading channels in the niche show on screen: a gradient sky with clouds,
water and distant hills, biome-specific trees, patterned glossy floors, striped
rails, colourful set dressing, soft sunlight, bloom and a saturation lift.
Everything is procedural (no downloaded assets), deterministic per module seed,
and driven by the episode environment theme from the VariationDirector.
"""
from __future__ import annotations

import colorsys
import math
import random

import bpy
from mathutils import Vector

from long_slide_fx import ensure_node_material

# Course footprint (the internal scenes keep the run inside |x|<6 and -10<y<13).
COURSE_HALF_WIDTH = 9.0
COURSE_Y = (-10.0, 13.0)

# Themed jobs frame like the niche leaders: lower, closer, faces visible (+y is
# the running direction, so positive y offsets look at the animal's face).
TOY_LENS_MM = 38.0
TOY_TARGET_AREA = 0.12
TOY_CAMERA_CANDIDATES = {
    "hero_start": [Vector((3.4, 3.4, 1.8)), Vector((-3.4, 3.4, 1.8)), Vector((4.4, 1.6, 2.2)),
                   Vector((-4.4, 1.6, 2.2)), Vector((3.0, 3.0, 3.6))],
    "chase": [Vector((3.6, -3.4, 2.3)), Vector((-3.6, -3.4, 2.3)), Vector((0.0, -4.6, 2.6)),
              Vector((4.2, -2.0, 3.6))],
    "obstacle_side": [Vector((4.6, 0.6, 2.0)), Vector((-4.6, 0.6, 2.0)), Vector((4.0, -1.6, 2.8)),
                      Vector((-4.0, -1.6, 2.8)), Vector((5.0, 0.0, 4.2))],
    "finish_reaction": [Vector((2.8, 3.8, 1.7)), Vector((-2.8, 3.8, 1.7)), Vector((0.0, 4.6, 2.0)),
                        Vector((3.6, 2.4, 3.4))],
    "wide_establish": [Vector((7.5, -7.5, 4.5)), Vector((-7.5, -7.5, 4.5)), Vector((0.0, -10.0, 5.0))],
    "top_down": [Vector((0.6, -1.0, 7.0)), Vector((-0.6, -1.0, 7.0)), Vector((0.0, -2.0, 6.5))],
    "low_front": [Vector((2.2, 3.8, 0.9)), Vector((-2.2, 3.8, 0.9)), Vector((0.0, 4.4, 1.1)),
                  Vector((3.4, 2.0, 1.3))],
}


def is_themed(module) -> bool:
    return bool(((module.get("metadata") or {}).get("environment") or {}).get("theme_id"))

BIOMES = {
    "sunny_park": {
        "ground": ((0.20, 0.62, 0.12), (0.34, 0.76, 0.18)), "hills": (0.16, 0.48, 0.14),
        "sky": ((0.78, 0.92, 1.0), (0.16, 0.46, 0.95)), "water": (0.05, 0.45, 0.85),
        "trees": "palm", "canopy": [(0.15, 0.6, 0.15)], "clouds": (1.0, 1.0, 1.0),
        "checker": ((1.0, 0.82, 0.08), (0.12, 0.52, 1.0)), "rails": ((1.0, 0.12, 0.12), (1.0, 1.0, 1.0)),
        "props": [(1.0, 0.15, 0.2), (1.0, 0.8, 0.1), (0.2, 0.6, 1.0), (0.3, 0.85, 0.3), (0.9, 0.3, 0.9)],
    },
    "snow_peak": {
        "ground": ((0.88, 0.92, 0.97), (0.78, 0.86, 0.95)), "hills": (0.9, 0.94, 1.0),
        "sky": ((0.85, 0.93, 1.0), (0.35, 0.6, 0.95)), "water": (0.55, 0.78, 0.95),
        "trees": "pine", "canopy": [(0.08, 0.35, 0.18)], "clouds": (1.0, 1.0, 1.0),
        "checker": ((0.15, 0.55, 1.0), (1.0, 1.0, 1.0)), "rails": ((0.9, 0.15, 0.25), (1.0, 1.0, 1.0)),
        "props": [(0.2, 0.5, 1.0), (1.0, 1.0, 1.0), (0.9, 0.2, 0.3), (0.5, 0.85, 1.0)],
    },
    "candy_hills": {
        "ground": ((0.95, 0.45, 0.68), (0.92, 0.6, 0.8)), "hills": (0.82, 0.55, 0.92),
        "sky": ((0.98, 0.72, 0.88), (0.52, 0.4, 0.95)), "water": (0.98, 0.85, 0.95),
        "trees": "lollipop", "canopy": [(1.0, 0.3, 0.5), (0.4, 0.8, 1.0), (1.0, 0.85, 0.2)],
        "clouds": (1.0, 0.95, 1.0),
        "checker": ((1.0, 0.35, 0.62), (1.0, 0.95, 0.55)), "rails": ((0.55, 0.3, 1.0), (1.0, 1.0, 1.0)),
        "props": [(1.0, 0.35, 0.65), (0.6, 0.4, 1.0), (0.4, 0.85, 1.0), (1.0, 0.9, 0.3)],
    },
    "jungle_river": {
        "ground": ((0.12, 0.46, 0.10), (0.22, 0.56, 0.12)), "hills": (0.08, 0.32, 0.1),
        "sky": ((0.8, 0.95, 0.9), (0.2, 0.55, 0.8)), "water": (0.05, 0.55, 0.5),
        "trees": "round", "canopy": [(0.1, 0.45, 0.1), (0.18, 0.55, 0.12)], "clouds": (1.0, 1.0, 1.0),
        "checker": ((1.0, 0.6, 0.08), (0.2, 0.78, 0.3)), "rails": ((0.95, 0.35, 0.05), (1.0, 0.95, 0.7)),
        "props": [(1.0, 0.55, 0.1), (0.95, 0.2, 0.3), (1.0, 0.9, 0.2), (0.3, 0.8, 1.0)],
    },
    "desert_canyon": {
        "ground": ((0.93, 0.74, 0.44), (0.87, 0.66, 0.36)), "hills": (0.78, 0.42, 0.22),
        "sky": ((1.0, 0.9, 0.75), (0.3, 0.58, 0.95)), "water": None,
        "trees": "cactus", "canopy": [(0.25, 0.6, 0.25)], "clouds": (1.0, 0.98, 0.95),
        "checker": ((0.95, 0.3, 0.12), (0.18, 0.72, 0.85)), "rails": ((0.15, 0.6, 0.85), (1.0, 0.95, 0.85)),
        "props": [(0.95, 0.35, 0.15), (0.2, 0.7, 0.85), (1.0, 0.8, 0.25), (0.6, 0.3, 0.8)],
    },
    "night_glow": {
        "ground": ((0.04, 0.16, 0.10), (0.06, 0.22, 0.14)), "hills": (0.04, 0.06, 0.14),
        "sky": ((0.12, 0.12, 0.32), (0.01, 0.01, 0.07)), "water": (0.02, 0.05, 0.2),
        "trees": "round", "canopy": [(0.03, 0.2, 0.12)], "clouds": None,
        "checker": ((0.05, 0.95, 0.9), (0.85, 0.15, 1.0)), "rails": ((1.0, 0.85, 0.1), (0.1, 0.1, 0.2)),
        "props": [(0.05, 1.0, 0.9), (1.0, 0.2, 0.8), (1.0, 0.85, 0.1), (0.4, 0.5, 1.0)],
        "glow": 2.5,
    },
    "rainy_day": {
        "ground": ((0.16, 0.38, 0.14), (0.22, 0.44, 0.16)), "hills": (0.22, 0.32, 0.24),
        "sky": ((0.72, 0.76, 0.8), (0.38, 0.44, 0.54)), "water": (0.2, 0.35, 0.5),
        "trees": "round", "canopy": [(0.12, 0.4, 0.14)], "clouds": (0.7, 0.72, 0.78),
        "checker": ((1.0, 0.8, 0.1), (0.25, 0.35, 0.9)), "rails": ((1.0, 0.5, 0.05), (1.0, 1.0, 1.0)),
        "props": [(1.0, 0.8, 0.1), (0.25, 0.45, 1.0), (1.0, 0.3, 0.3), (0.3, 0.85, 0.5)],
        "wet": True,
    },
    "autumn_forest": {
        "ground": ((0.5, 0.42, 0.12), (0.62, 0.36, 0.1)), "hills": (0.55, 0.3, 0.12),
        "sky": ((1.0, 0.88, 0.72), (0.38, 0.55, 0.85)), "water": None,
        "trees": "round", "canopy": [(0.95, 0.45, 0.08), (0.85, 0.2, 0.08), (0.98, 0.75, 0.12)],
        "clouds": (1.0, 0.96, 0.9),
        "checker": ((1.0, 0.55, 0.1), (0.55, 0.18, 0.08)), "rails": ((0.85, 0.15, 0.1), (1.0, 0.9, 0.6)),
        "props": [(1.0, 0.55, 0.1), (0.85, 0.2, 0.1), (1.0, 0.85, 0.2), (0.45, 0.25, 0.1)],
    },
}


def _set(obj, attr, value):
    """Set a Blender property if this Blender version has it."""
    try:
        setattr(obj, attr, value)
    except (AttributeError, TypeError, ValueError):
        pass


def _rgba(rgb, alpha=1.0):
    return (float(rgb[0]), float(rgb[1]), float(rgb[2]), alpha)


# ---------- materials ----------

def _principled(name, color, roughness=0.45, coat=0.0, emission=0.0, transmission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = _rgba(color)
    bsdf.inputs["Roughness"].default_value = roughness
    for key, value in (("Coat Weight", coat), ("Transmission Weight", transmission)):
        if key in bsdf.inputs:
            bsdf.inputs[key].default_value = value
    if emission > 0 and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = _rgba(color)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def _pattern_material(name, colors, kind, scale, roughness=0.3, emission=0.0):
    """Checker floors or banded rails driven by object coordinates."""
    mat = _principled(name, colors[0], roughness=roughness, coat=0.4, emission=emission)
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    coords = nt.nodes.new("ShaderNodeTexCoord")
    if kind == "checker":
        tex = nt.nodes.new("ShaderNodeTexChecker")
        tex.inputs["Color1"].default_value = _rgba(colors[0])
        tex.inputs["Color2"].default_value = _rgba(colors[1])
        tex.inputs["Scale"].default_value = scale
        nt.links.new(coords.outputs["Object"], tex.inputs["Vector"])
        color_out = tex.outputs["Color"]
    else:
        tex = nt.nodes.new("ShaderNodeTexWave")
        tex.wave_type = "BANDS"
        tex.bands_direction = "Y"
        tex.inputs["Scale"].default_value = scale
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.interpolation = "CONSTANT"
        ramp.color_ramp.elements[0].color = _rgba(colors[0])
        ramp.color_ramp.elements[1].position = 0.5
        ramp.color_ramp.elements[1].color = _rgba(colors[1])
        nt.links.new(coords.outputs["Object"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Fac"], ramp.inputs["Fac"])
        color_out = ramp.outputs["Color"]
    nt.links.new(color_out, bsdf.inputs["Base Color"])
    if emission > 0 and "Emission Color" in bsdf.inputs:
        nt.links.new(color_out, bsdf.inputs["Emission Color"])
    return mat


def _ground_material(name, colors, wet=False):
    mat = _principled(name, colors[0], roughness=0.25 if wet else 0.85)
    nt = mat.node_tree
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.35
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = _rgba(colors[0])
    ramp.color_ramp.elements[1].color = _rgba(colors[1])
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes.get("Principled BSDF").inputs["Base Color"])
    return mat


def _vivid(color, saturation_boost=1.35, value_floor=0.55):
    h, s, v = colorsys.rgb_to_hsv(*color[:3])
    return colorsys.hsv_to_rgb(h, min(1.0, s * saturation_boost), max(v, value_floor))


def _restyle_obstacles(biome):
    """Give obstacle props a glossy, saturated toy finish; grey parts take a theme colour."""
    done: dict[str, bpy.types.Material] = {}
    accents = list(biome["props"])
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.get("factory_role") != "obstacle":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                continue
            if mat.name not in done:
                base = mat.diffuse_color[:3]
                if mat.use_nodes and mat.node_tree.nodes.get("Principled BSDF"):
                    base = mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value[:3]
                if colorsys.rgb_to_hsv(*base)[1] < 0.12:
                    base = accents[len(done) % len(accents)]
                done[mat.name] = _principled(f"LOOK_{mat.name}", _vivid(base), roughness=0.22, coat=0.7)
            slot.link = "OBJECT"
            slot.material = done[mat.name]


def _soften_animals():
    """Round off low-poly animals into a soft vinyl-toy look (smooth shading + one subdivision)."""
    done: set[str] = set()
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.get("factory_role") not in {"animal", "companion"}:
            continue
        for poly in obj.data.polygons:
            poly.use_smooth = True
        if not any(m.type == "SUBSURF" for m in obj.modifiers):
            mod = obj.modifiers.new("LOOK_SOFTEN", "SUBSURF")
            mod.levels = 1
            mod.render_levels = 1
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or mat.name in done:
                continue
            ensure_node_material(mat)
            bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
            if bsdf is not None:
                bsdf.inputs["Roughness"].default_value = 0.42
                if "Coat Weight" in bsdf.inputs:
                    bsdf.inputs["Coat Weight"].default_value = 0.25
            done.add(mat.name)


def _restyle_course(biome):
    glow = biome.get("glow", 0.0) * 0.4
    floor = _pattern_material("LOOK_FLOOR", biome["checker"], "checker", 0.85, emission=glow)
    rails = _pattern_material("LOOK_RAILS", biome["rails"], "bands", 1.6, roughness=0.25, emission=glow)
    ground = _ground_material("LOOK_GROUND", biome["ground"], wet=biome.get("wet", False))
    swaps = {"MAT_SLIDE": floor, "MAT_RAIL": rails, "MAT_GROUND": ground}
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.get("factory_role") in {"animal", "companion", "obstacle", "fx"}:
            continue
        for slot in obj.material_slots:
            if slot.material is not None and slot.material.name in swaps:
                slot.material = swaps[slot.material.name]
    return ground


# ---------- world ----------

def _sky(scene, biome):
    world = scene.world or bpy.data.worlds.new("LOOK_WORLD")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    coords = nt.nodes.new("ShaderNodeTexCoord")
    split = nt.nodes.new("ShaderNodeSeparateXYZ")
    remap = nt.nodes.new("ShaderNodeMapRange")
    remap.inputs["From Min"].default_value = -0.05
    remap.inputs["From Max"].default_value = 0.65
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = _rgba(biome["sky"][0])
    ramp.color_ramp.elements[1].color = _rgba(biome["sky"][1])
    background = nt.nodes.new("ShaderNodeBackground")
    background.inputs["Strength"].default_value = 1.0
    output = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(coords.outputs["Generated"], split.inputs["Vector"])
    nt.links.new(split.outputs["Z"], remap.inputs["Value"])
    nt.links.new(remap.outputs["Result"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], background.inputs["Color"])
    nt.links.new(background.outputs["Background"], output.inputs["Surface"])


# ---------- set dressing ----------

class _Builder:
    def __init__(self, seed: int):
        self.rng = random.Random(seed)
        self.collection = bpy.data.collections.new("LOOKDEV_SET")
        bpy.context.scene.collection.children.link(self.collection)
        self._protos: dict[str, bpy.types.Mesh] = {}
        self._mats: dict[tuple, bpy.types.Material] = {}

    def material(self, color, **kw):
        key = (tuple(round(c, 3) for c in color), tuple(sorted(kw.items())))
        if key not in self._mats:
            self._mats[key] = _principled(f"LOOK_MAT_{len(self._mats):03d}", color, **kw)
        return self._mats[key]

    def proto(self, kind):
        if kind not in self._protos:
            ops = {
                "sphere": lambda: bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1.0),
                "cone": lambda: bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=1.0, depth=2.0),
                "cylinder": lambda: bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.0, depth=2.0),
                "plane": lambda: bpy.ops.mesh.primitive_plane_add(size=2.0),
                "disc": lambda: bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=1.0, depth=0.1),
            }
            ops[kind]()
            obj = bpy.context.object
            if kind in {"sphere", "cone", "cylinder"}:
                bpy.ops.object.shade_smooth()
            mesh = obj.data
            mesh.materials.append(self.material((1, 1, 1)))
            bpy.data.objects.remove(obj, do_unlink=True)
            self._protos[kind] = mesh
        return self._protos[kind]

    def add(self, kind, location, scale, color=None, material=None, rotation=(0, 0, 0), **mat_kw):
        obj = bpy.data.objects.new(f"LOOK_{kind}", self.proto(kind))
        self.collection.objects.link(obj)
        obj.location = Vector(location)
        obj.scale = Vector(scale)
        obj.rotation_euler = rotation
        obj["factory_role"] = "set_dressing"
        slot = obj.material_slots[0]
        slot.link = "OBJECT"
        slot.material = material or self.material(color, **mat_kw)
        return obj

    def ring_point(self, r_min, r_max, keep_out_course=True):
        for _ in range(40):
            angle = self.rng.uniform(0, math.tau)
            radius = self.rng.uniform(r_min, r_max)
            x, y = math.cos(angle) * radius, math.sin(angle) * radius + 1.5
            if not keep_out_course or abs(x) > COURSE_HALF_WIDTH or not (COURSE_Y[0] < y < COURSE_Y[1]):
                return x, y
        return COURSE_HALF_WIDTH + 2.0, 0.0


def _tree(b, kind, x, y, biome):
    canopy = b.rng.choice(biome["canopy"])
    trunk = (0.45, 0.28, 0.14)
    h = b.rng.uniform(0.8, 1.3)
    if kind == "palm":
        b.add("cylinder", (x, y, 2.4 * h), (0.22, 0.22, 2.4 * h), trunk, roughness=0.8)
        for i in range(6):
            a = i * math.tau / 6 + b.rng.uniform(-0.2, 0.2)
            b.add("sphere", (x + math.cos(a) * 1.3, y + math.sin(a) * 1.3, 4.8 * h), (1.6, 0.45, 0.12),
                  canopy, rotation=(0, 0.35, a), roughness=0.6)
    elif kind == "pine":
        b.add("cylinder", (x, y, 0.8), (0.25, 0.25, 0.8), trunk, roughness=0.8)
        for i, (r, z) in enumerate(((1.8, 2.2), (1.4, 3.4), (0.9, 4.5))):
            b.add("cone", (x, y, z * h), (r, r, 0.9), canopy if i < 2 else (0.95, 0.97, 1.0), roughness=0.7)
    elif kind == "lollipop":
        b.add("cylinder", (x, y, 1.6 * h), (0.09, 0.09, 1.6 * h), (1, 1, 1), roughness=0.3)
        b.add("sphere", (x, y, 3.4 * h), (1.1, 0.35, 1.1), canopy, rotation=(math.pi / 2, 0, b.rng.uniform(0, 3)),
              roughness=0.15, coat=0.8)
    elif kind == "cactus":
        b.add("cylinder", (x, y, 1.5 * h), (0.38, 0.38, 1.5 * h), canopy, roughness=0.7)
        b.add("sphere", (x, y, 3.0 * h), (0.38, 0.38, 0.38), canopy, roughness=0.7)
        side = b.rng.choice((-1, 1))
        b.add("cylinder", (x + side * 0.6, y, 1.8 * h), (0.22, 0.22, 0.6), canopy, roughness=0.7)
    else:
        b.add("cylinder", (x, y, 1.1 * h), (0.3, 0.3, 1.1 * h), trunk, roughness=0.8)
        b.add("sphere", (x, y, 3.1 * h), (1.6, 1.6, 1.4), canopy, roughness=0.65)
        b.add("sphere", (x + 0.7, y + 0.3, 3.6 * h), (1.0, 1.0, 0.9), canopy, roughness=0.65)


def _backdrop(b, biome, ground_mat, *, real_props=False):
    b.add("disc", (0, 1.5, -0.62), (42, 42, 1), material=ground_mat)
    if biome["water"] is not None:
        b.add("plane", (0, 0, -0.7), (420, 420, 1), biome["water"], roughness=0.05, coat=1.0)
    for i in range(9):
        angle = i * math.tau / 9 + b.rng.uniform(-0.2, 0.2)
        r = b.rng.uniform(85, 120)
        size = b.rng.uniform(18, 34)
        b.add("sphere", (math.cos(angle) * r, math.sin(angle) * r, -3), (size, size, b.rng.uniform(7, 15)),
              biome["hills"], roughness=0.9)
    count = 16 if biome["trees"] in {"palm", "pine", "round"} else 20
    if real_props:
        count = 8  # far filler only; the kit props carry the near backdrop
    for _ in range(count):
        x, y = b.ring_point(12, 34)
        _tree(b, biome["trees"], x, y, biome)


def _sky_objects(b, biome):
    if biome.get("clouds") is not None:
        for _ in range(9):
            angle = b.rng.uniform(0, math.tau)
            r = b.rng.uniform(45, 110)
            cx, cy, cz = math.cos(angle) * r, math.sin(angle) * r, b.rng.uniform(22, 40)
            for k in range(b.rng.randint(3, 5)):
                s = b.rng.uniform(3.5, 6.5)
                b.add("sphere", (cx + k * 3.2, cy + b.rng.uniform(-1.5, 1.5), cz + b.rng.uniform(-0.8, 0.8)),
                      (s, s * 0.8, s * 0.6), biome["clouds"], roughness=1.0)
    if biome.get("glow"):
        for _ in range(60):
            angle = b.rng.uniform(0, math.tau)
            r = b.rng.uniform(80, 160)
            b.add("sphere", (math.cos(angle) * r, math.sin(angle) * r, b.rng.uniform(25, 90)), (0.35, 0.35, 0.35),
                  (1.0, 0.95, 0.8), emission=6.0)


def _decor(b, biome):
    glow = biome.get("glow", 0.0)
    palette = biome["props"]
    for side in (-1, 1):
        for y in (-3.0, 2.5, 8.0):
            color = b.rng.choice(palette)
            b.add("sphere", (side * b.rng.uniform(10.0, 11.5), y, -0.3), (1.3, 1.3, 1.6), color,
                  roughness=0.08, coat=1.0, transmission=0.35, emission=glow)
        for _ in range(4):
            x, y = side * b.rng.uniform(9.5, 15), b.rng.uniform(-8, 14)
            r = b.rng.uniform(0.35, 0.7)
            b.add("sphere", (x, y, r - 0.55), (r, r, r), b.rng.choice(palette), roughness=0.2, coat=0.8, emission=glow)
    for x in (-4.6, 4.6):
        for y in (-7.4, 9.6):
            for k in range(5):
                b.add("sphere", (x, y, 0.6 + k * 0.75), (0.38, 0.38, 0.46), palette[(k + int(x > 0)) % len(palette)],
                      roughness=0.15, coat=0.9, emission=glow)


# ---------- render ----------

def _render_settings(scene, camera, target):
    eevee = scene.eevee
    for attr, value in (("taa_render_samples", 64), ("use_raytracing", True), ("use_shadows", True),
                        ("shadow_ray_count", 2), ("shadow_step_count", 8), ("use_gtao", True),
                        ("gtao_distance", 1.2), ("use_motion_blur", True)):
        _set(eevee, attr, value)
    _set(scene.render, "use_motion_blur", True)
    # Kids' toy-box channels use saturated primaries; AgX compresses saturation,
    # so themed renders use Standard with a gentle contrast look.
    _set(scene.view_settings, "view_transform", "Standard")
    for look in ("Medium High Contrast", "None"):
        try:
            scene.view_settings.look = look
            break
        except TypeError:
            continue
    scene.view_settings.exposure = -0.35  # Standard clips early; keep saturated mid-tones
    sun = bpy.data.objects.get("LONG_SLIDE_SUN")
    if sun is not None:
        _set(sun.data, "angle", math.radians(3.0))
    if camera is not None and target is not None:
        camera.data.dof.use_dof = True
        camera.data.dof.focus_object = target
        camera.data.dof.aperture_fstop = 5.6


def _compositor(scene, glow):
    scene.use_nodes = True
    tree = scene.node_tree
    if tree is None:
        return
    tree.nodes.clear()
    layers = tree.nodes.new("CompositorNodeRLayers")
    glare = tree.nodes.new("CompositorNodeGlare")
    for attr, value in (("glare_type", "BLOOM"), ("quality", "HIGH"), ("threshold", 0.9), ("mix", -0.75 + 0.2 * bool(glow))):
        _set(glare, attr, value)
    for name, value in (("Threshold", 0.9), ("Strength", 0.35 + 0.3 * bool(glow))):
        if name in glare.inputs:
            glare.inputs[name].default_value = value
    huesat = tree.nodes.new("CompositorNodeHueSat")
    if "Saturation" in huesat.inputs:
        huesat.inputs["Saturation"].default_value = 1.12
    composite = tree.nodes.new("CompositorNodeComposite")
    tree.links.new(layers.outputs["Image"], glare.inputs["Image"])
    tree.links.new(glare.outputs["Image"], huesat.inputs["Image"])
    tree.links.new(huesat.outputs["Image"], composite.inputs["Image"])


def apply_lookdev(scene, module, camera=None, target=None):
    """Dress the scene for a themed module. Unthemed jobs are left unchanged."""
    env = (module.get("metadata") or {}).get("environment") or {}
    theme = env.get("theme_id")
    if not theme:
        return None
    biome = BIOMES.get(theme, BIOMES["sunny_park"])
    builder = _Builder(int(module.get("seed", 0)))
    ground = _restyle_course(biome)
    _restyle_obstacles(biome)
    _soften_animals()
    _sky(scene, biome)
    _backdrop(builder, biome, ground, real_props=bool(bpy.context.scene.get("kit_backdrop_placed")))
    _sky_objects(builder, biome)
    _decor(builder, biome)
    _render_settings(scene, camera, target)
    _compositor(scene, biome.get("glow", 0.0))
    scene["long_slide_lookdev"] = theme
    return theme
