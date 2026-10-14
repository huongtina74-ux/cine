from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


def inspect_blend(path: Path) -> dict:
    with bpy.data.libraries.load(str(path), link=False) as (src, _dst):
        objects = list(src.objects)
        armatures = list(src.armatures)
        actions = list(src.actions)
        materials = list(src.materials)
    return {
        "path": str(path),
        "format": "BLEND",
        "objects": objects,
        "armatures": armatures,
        "actions": actions,
        "materials": materials,
        "armature_count": len(armatures),
        "action_count": len(actions),
        "object_count": len(objects),
        "has_rig": bool(armatures),
        "has_animation": bool(actions),
    }


def reset_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for collection in (
        bpy.data.actions,
        bpy.data.armatures,
        bpy.data.meshes,
        bpy.data.materials,
        bpy.data.images,
    ):
        # imported datablocks can stay until process exit; scene reset is enough
        pass


def inspect_glb(path: Path) -> dict:
    reset_scene()
    before_actions = set(bpy.data.actions.keys())
    bpy.ops.import_scene.gltf(filepath=str(path))
    imported_objects = list(bpy.context.scene.objects)
    armatures = [o for o in imported_objects if o.type == "ARMATURE"]
    meshes = [o for o in imported_objects if o.type == "MESH"]
    new_actions = [
        name for name in bpy.data.actions.keys()
        if name not in before_actions
    ]
    bone_counts = {
        arm.name: len(arm.data.bones)
        for arm in armatures
    }
    return {
        "path": str(path),
        "format": "GLB",
        "objects": [o.name for o in imported_objects],
        "armatures": [o.name for o in armatures],
        "meshes": [o.name for o in meshes],
        "actions": sorted(new_actions),
        "bone_counts": bone_counts,
        "armature_count": len(armatures),
        "action_count": len(new_actions),
        "object_count": len(imported_objects),
        "has_rig": bool(armatures),
        "has_animation": bool(new_actions),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--report", required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    paths = [
        root / "opengameart_elephant_lowpoly.blend",
        root / "opengameart_gorilla_male_extracted" / "gorilla_male.blend",
        root / "opengameart_tiger_extracted" / "tiger.blend",
        root / "kenney_prototype_kit_extracted" / "Models" / "GLB format" / "animal-bison.glb",
        root / "kenney_prototype_kit_extracted" / "Models" / "GLB format" / "animal-dog.glb",
        root / "kenney_prototype_kit_extracted" / "Models" / "GLB format" / "animal-horse.glb",
    ]

    rows = []
    for path in paths:
        try:
            row = inspect_blend(path) if path.suffix.lower() == ".blend" else inspect_glb(path)
            row["exists"] = path.is_file()
            row["error"] = None
        except Exception as exc:
            row = {
                "path": str(path),
                "exists": path.is_file(),
                "error": f"{type(exc).__name__}:{exc}",
                "has_rig": False,
                "has_animation": False,
            }
        rows.append(row)

    payload = {"assets": rows}
    Path(args.report).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
