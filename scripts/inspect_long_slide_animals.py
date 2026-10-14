from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--folders", nargs="+", required=True)
    parser.add_argument("--output", required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return parser.parse_args(argv)


def world_bounds(meshes):
    points = []
    for obj in meshes:
        try:
            for corner in obj.bound_box:
                points.append(obj.matrix_world @ Vector(corner))
        except Exception:
            pass
    if not points:
        return None
    mins = [min(getattr(p, axis) for p in points) for axis in ("x", "y", "z")]
    maxs = [max(getattr(p, axis) for p in points) for axis in ("x", "y", "z")]
    return {
        "min": [round(v, 6) for v in mins],
        "max": [round(v, 6) for v in maxs],
        "size": [round(maxs[i] - mins[i], 6) for i in range(3)],
    }


def inspect(path: Path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    armatures = [o for o in bpy.data.objects if o.type == "ARMATURE"]
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    actions = []
    for action in bpy.data.actions:
        slots = []
        try:
            slots = [slot.name for slot in action.slots]
        except Exception:
            pass
        actions.append({
            "name": action.name,
            "frame_range": [round(float(action.frame_range[0]), 3), round(float(action.frame_range[1]), 3)],
            "slots": slots,
        })
    rigs = []
    for arm in armatures:
        bones = [b.name for b in arm.data.bones]
        rigs.append({
            "object": arm.name,
            "data": arm.data.name,
            "bone_count": len(bones),
            "bones": bones,
            "scale": [round(float(x), 6) for x in arm.scale],
            "rotation_mode": arm.rotation_mode,
        })
    return {
        "path": str(path.resolve()),
        "name": path.stem,
        "object_count": len(bpy.data.objects),
        "mesh_count": len(meshes),
        "armature_count": len(armatures),
        "action_count": len(actions),
        "actions": actions,
        "rigs": rigs,
        "bounds": world_bounds(meshes),
        "materials": sorted({slot.material.name for o in meshes for slot in o.material_slots if slot.material}),
        "scenes": [s.name for s in bpy.data.scenes],
        "fps": bpy.context.scene.render.fps if bpy.context.scene else None,
    }


def main():
    ns = args()
    files = []
    for folder in ns.folders:
        files.extend(sorted(Path(folder).rglob("*.blend")))
    rows = []
    for path in files:
        try:
            row = inspect(path)
            row["status"] = "OK"
        except Exception as exc:
            row = {"path": str(path), "name": path.stem, "status": "ERROR", "error": f"{type(exc).__name__}:{exc}"}
        print("INSPECT", row["name"], row.get("action_count"), row.get("armature_count"), flush=True)
        rows.append(row)
    out = Path(ns.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"assets": rows}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
