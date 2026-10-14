from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import bpy


SCENE_REQUIRED = {
    "GROUND",
    "START_PLATFORM",
    "FINISH_PLATFORM",
    "ANIMAL_SPAWN",
    "OBSTACLE_SLOT_1",
    "OBSTACLE_SLOT_2",
    "FINISH_ZONE",
    "CAMERA_HERO",
    "CAMERA_CHASE",
    "CAMERA_FINISH",
    "SLIDE_BODY",
    "SLIDE_PATH",
}

OBSTACLE_REQUIRED = {"EVENT_ANCHOR"}

SPECIAL = {
    "obstacle.rotating_hammer": {"ROTATION_ROOT", "HAMMER_BEAM", "HAMMER_POST"},
    "obstacle.spinning_bar": {"ROTATION_ROOT", "SPINNING_BAR"},
    "obstacle.paint_gate": {"TRIGGER_VOLUME", "GATE_L", "GATE_R", "GATE_TOP"},
    "obstacle.ball_pit": {"PIT_BACK"},
    "obstacle.water_pool": {"WATER_SURFACE"},
    "obstacle.cage": {"DOOR_HINGE"},
    "obstacle.bridge": {"PLANK_00"},
    "obstacle.giant_duck": {"DUCK_BODY", "DUCK_HEAD", "DUCK_BEAK"},
    "obstacle.break_wall": {"BRICK_0_0"},
}


def asset_id(path: Path) -> str:
    stem = path.stem
    if stem.startswith("scene_"):
        return "scene." + stem[6:]
    if stem.startswith("obstacle_"):
        return "obstacle." + stem[9:]
    raise ValueError(stem)


def inspect(path: Path):
    with bpy.data.libraries.load(str(path), link=False) as (src, _dst):
        names = set(src.objects)
    aid = asset_id(path)
    required = set(SCENE_REQUIRED if aid.startswith("scene.") else OBSTACLE_REQUIRED)
    required.update(SPECIAL.get(aid, set()))
    missing = sorted(required - names)
    return {
        "asset_id": aid,
        "path": str(path),
        "object_count": len(names),
        "required": sorted(required),
        "missing": missing,
        "passed": not missing,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asset-dir", required=True)
    parser.add_argument("--report", required=True)
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    args = parser.parse_args(argv)
    folder = Path(args.asset_dir).resolve()
    rows = [inspect(path) for path in sorted(folder.glob("*.blend"))]
    payload = {
        "passed": bool(rows) and all(item["passed"] for item in rows),
        "assets": rows,
    }
    Path(args.report).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
