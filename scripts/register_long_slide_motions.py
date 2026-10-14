from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "config" / "animal_long_slide" / "motions.yaml"


def motion(
    motion_id, animal, action, family, path, *,
    source_action=None, frame_start=None, frame_end=None, fps=None,
    speed=1.0, loopable=False, preview_ready=True, tags=None,
):
    return {
        "motion_id": motion_id,
        "semantic_action": action,
        "skeleton_family": family,
        "local_path": path,
        "source_action": source_action,
        "frame_start": frame_start,
        "frame_end": frame_end,
        "source_fps": fps,
        "speed_multiplier": speed,
        "animal_id": animal,
        "method": "SOURCE_ACTION",
        "loopable": loopable,
        "root_motion": False,
        "foot_contact_validated": False,
        "preview_ready": bool(preview_ready),
        "production_ready": False,
        "compatible_animals": [],
        "tags": list(tags or []) + ["inspection_verified", "needs_motion_qc"],
    }


def main():
    rows = []
    farm = "data/assets/animal_long_slide/quarantine/quaternius/farm/Blends"
    for animal, filename, family in [
        ("cow", "Cow.blend", "quadruped.hoofed"),
        ("horse", "Horse.blend", "quadruped.hoofed"),
        ("llama", "Llama.blend", "quadruped.hoofed"),
        ("pig", "Pig.blend", "quadruped.heavy"),
        ("pug", "Pug.blend", "quadruped.canine"),
        ("sheep", "Sheep.blend", "quadruped.hoofed"),
        ("zebra", "Zebra.blend", "quadruped.hoofed"),
    ]:
        path = f"{farm}/{filename}"
        rows.append(motion(
            f"motion.{animal}.idle.farm.v1", animal, "idle", family, path,
            source_action="Idle", loopable=True, tags=["quaternius", "cc0"],
        ))
        rows.append(motion(
            f"motion.{animal}.run.farm.v1", animal, "run", family, path,
            source_action="Run", loopable=True, tags=["quaternius", "cc0"],
        ))

    ultimate = "data/assets/animal_long_slide/quarantine/quaternius/ultimate/Blends"
    for animal, filename, family in [
        ("alpaca", "Alpaca.blend", "quadruped.hoofed"),
        ("bull", "Bull.blend", "quadruped.hoofed"),
        ("deer", "Deer.blend", "quadruped.hoofed"),
        ("donkey", "Donkey.blend", "quadruped.hoofed"),
        ("fox", "Fox.blend", "quadruped.canine"),
        ("white_horse", "Horse_White.blend", "quadruped.hoofed"),
        ("husky", "Husky.blend", "quadruped.canine"),
        ("shiba_inu", "ShibaInu.blend", "quadruped.canine"),
        ("stag", "Stag.blend", "quadruped.hoofed"),
        ("wolf", "Wolf.blend", "quadruped.canine"),
    ]:
        path = f"{ultimate}/{filename}"
        rows.append(motion(
            f"motion.{animal}.idle.ultimate.v1", animal, "idle", family, path,
            source_action="Idle", loopable=True, tags=["quaternius", "cc0"],
        ))
        rows.append(motion(
            f"motion.{animal}.run.ultimate.v1", animal, "run", family, path,
            source_action="Gallop", loopable=True, tags=["quaternius", "cc0"],
        ))

    # Elephant is useful immediately for idle/reaction work, but deliberately
    # receives no run binding: execution must fail closed until locomotion exists.
    rows.append(motion(
        "motion.elephant.idle.oga.v1",
        "elephant", "idle", "quadruped.elephant",
        "data/assets/animal_long_slide/quarantine/opengameart/elephant-lowpoly.blend",
        source_action="Idle", loopable=True, tags=["opengameart", "cc0"],
    ))

    # Canonical duck is the full-body OpenGameArt rig. Waddle is a valid
    # locomotion source for this stylized vertical and can be speed-adjusted.
    rows.append(motion(
        "motion.duck.run.oga.v1",
        "duck", "run", "avian.duck",
        "data/assets/animal_long_slide/quarantine/opengameart/duck6.blend",
        source_action="Waddle", speed=1.35, loopable=True,
        tags=["opengameart", "cc0", "waddle_as_run"],
    ))

    # Gobkit dinosaur and Kenney buffalo are retained as researched motion
    # candidates, but are not preview-executable until the Blender binder has
    # qualified baked-range / hierarchy animation playback for those formats.
    rows.append(motion(
        "motion.dinosaur.run.gobkit.v1",
        "dinosaur", "run", "dinosaur.generic",
        "data/assets/animal_long_slide/quarantine/gobkit/Trex.glb",
        frame_start=90, frame_end=119, fps=24, speed=1.55, loopable=True,
        preview_ready=False,
        tags=["gobkit", "cc0", "baked_track", "binder_qualification_pending"],
    ))
    rows.append(motion(
        "motion.buffalo.run.kenney.v1",
        "buffalo", "run", "quadruped.heavy",
        "data/assets/animal_long_slide/quarantine/kenney_prototype_kit_extracted/Models/GLB format/animal-bison.glb",
        source_action="run", loopable=True, preview_ready=False,
        tags=["kenney", "cc0", "hierarchy_animation", "binder_qualification_pending"],
    ))

    OUT.write_text(
        yaml.safe_dump({"motions": rows}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"registered_motions={len(rows)} output={OUT}")


if __name__ == "__main__":
    main()
