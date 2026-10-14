from __future__ import annotations

import hashlib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "animal_long_slide" / "external_assets.yaml"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def row(
    asset_id: str,
    path: Path,
    *,
    source_uri: str,
    pack_id: str,
    license_uri: str,
    rig_profile: str | None,
    clips: list[str],
    technical: bool = True,
    tags: list[str] | None = None,
    notes: list[str] | None = None,
):
    exists = path.is_file()
    return {
        "asset_id": asset_id,
        "kind": "ANIMAL",
        "source_uri": source_uri,
        "source_pack_id": pack_id,
        "license_evidence_uri": license_uri,
        "license_state": "APPROVED",
        "commercial_use": True,
        "redistribution_allowed": True,
        "local_path": rel(path) if exists else rel(path),
        "version": "1",
        "rig_profile": rig_profile,
        "clip_ids": clips,
        "dependencies": [],
        "production_ready": False,
        "technical_qc_passed": bool(exists and technical),
        "visual_qc_passed": False,
        "content_sha256": sha256(path) if exists else None,
        "provenance_notes": list(notes or []) + [
            "Binary is held in quarantine until visual/motion qualification completes."
        ],
        "tags": list(tags or []) + [
            "external_candidate",
            "needs_visual_approval",
        ],
    }


def main():
    q = ROOT / "data" / "assets" / "animal_long_slide" / "quarantine"
    ultimate = q / "quaternius" / "ultimate" / "Blends"
    farm = q / "quaternius" / "farm" / "Blends"
    oga = q / "opengameart"
    gob = q / "gobkit"
    kenney = q / "kenney_prototype_kit_extracted" / "Models" / "GLB format"

    rows = []

    farm_animals = {
        "cow": "Cow.blend",
        "horse": "Horse.blend",
        "llama": "Llama.blend",
        "pig": "Pig.blend",
        "pug": "Pug.blend",
        "sheep": "Sheep.blend",
        "zebra": "Zebra.blend",
    }
    for animal, filename in farm_animals.items():
        rows.append(row(
            f"animal.{animal}",
            farm / filename,
            source_uri="https://quaternius.com/packs/farmanimal.html",
            pack_id="quaternius.farm_animals",
            license_uri="https://quaternius.com/packs/farmanimal.html",
            rig_profile="quaternius.farm.quadruped",
            clips=["Death", "Idle", "Jump", "Run", "Walk", "WalkSlow"],
            tags=["cc0", "rigged", "animated", "low_poly"],
            notes=["Blender inspection found one armature and six Actions."],
        ))

    ultimate_animals = {
        "alpaca": ("Alpaca.blend", "quaternius.ultimate.hoofed"),
        "bull": ("Bull.blend", "quaternius.ultimate.hoofed"),
        "deer": ("Deer.blend", "quaternius.ultimate.hoofed"),
        "donkey": ("Donkey.blend", "quaternius.ultimate.hoofed"),
        "fox": ("Fox.blend", "quaternius.ultimate.canine"),
        "white_horse": ("Horse_White.blend", "quaternius.ultimate.hoofed"),
        "husky": ("Husky.blend", "quaternius.ultimate.canine"),
        "shiba_inu": ("ShibaInu.blend", "quaternius.ultimate.canine"),
        "stag": ("Stag.blend", "quaternius.ultimate.hoofed"),
        "wolf": ("Wolf.blend", "quaternius.ultimate.canine"),
    }
    for animal, (filename, rig_profile) in ultimate_animals.items():
        path = ultimate / filename
        canine = "canine" in rig_profile
        clips = (
            ["Attack", "Death", "Eating", "Gallop", "Gallop_Jump", "Idle",
             "Idle_2", "Idle_2_HeadLow", "Idle_HitReact_Left",
             "Idle_HitReact_Right", "Jump_ToIdle", "Walk"]
            if canine else
            ["Attack_Headbutt", "Attack_Kick", "Death", "Eating", "Gallop",
             "Gallop_Jump", "Idle", "Idle_2", "Idle_Headlow",
             "Idle_HitReact_Left", "Idle_HitReact_Right", "Jump_toIdle", "Walk"]
        )
        rows.append(row(
            f"animal.{animal}",
            path,
            source_uri="https://quaternius.com/packs/ultimateanimatedanimals.html",
            pack_id="quaternius.ultimate_animated_animals",
            license_uri=rel(q / "quaternius" / "ultimate" / "License.txt"),
            rig_profile=rig_profile,
            clips=clips,
            tags=["cc0", "rigged", "animated", "low_poly"],
            notes=["Blender inspection found one armature and 12-13 Actions."],
        ))

    rows.extend([
        row(
            "animal.elephant",
            oga / "elephant-lowpoly.blend",
            source_uri="https://opengameart.org/content/low-poly-elephant-model",
            pack_id="opengameart.elephant_lowpoly",
            license_uri="https://opengameart.org/content/low-poly-elephant-model",
            rig_profile="opengameart.elephant.v1",
            clips=["Angry", "Eating", "GettingUp", "Idle", "Sitting"],
            tags=["cc0", "rigged", "partial_motion", "needs_locomotion"],
            notes=["Inspection: 32 bones, five Actions; no walk/run Action."],
        ),
        row(
            "animal.tiger",
            oga / "tiger" / "tiger.blend",
            source_uri="https://opengameart.org/content/tiger",
            pack_id="opengameart.tiger",
            license_uri="https://opengameart.org/content/tiger",
            rig_profile="opengameart.tiger.v1",
            clips=[],
            tags=["cc0", "rigged", "needs_motion", "needs_material_normalization"],
            notes=["Inspection: 35 bones, zero Actions."],
        ),
        row(
            "animal.lion",
            oga / "lion_bestiary.blend",
            source_uri="https://opengameart.org/content/animal-bestiary",
            pack_id="opengameart.animal_bestiary",
            license_uri="https://opengameart.org/content/animal-bestiary",
            rig_profile="opengameart.bestiary.lion",
            clips=[],
            tags=["cc0", "rigged", "needs_motion", "full_body"],
            notes=["Extracted locally from CC0 Animal Bestiary; Armature-Lion has 26 bones and no assigned Action."],
        ),
        row(
            "animal.gorilla",
            oga / "gorilla" / "gorilla_male.blend",
            source_uri="https://opengameart.org/content/gorilla-male",
            pack_id="opengameart.gorilla_male",
            license_uri="https://opengameart.org/content/gorilla-male",
            rig_profile=None,
            clips=[],
            technical=False,
            tags=["cc0", "needs_rig", "needs_motion"],
            notes=["Inspection found no armature and no Actions."],
        ),
        row(
            "animal.hippo",
            oga / "hippo" / "hippo.blend",
            source_uri="https://opengameart.org/content/hippo",
            pack_id="opengameart.hippo",
            license_uri="https://opengameart.org/content/hippo",
            rig_profile="opengameart.hippo.v1",
            clips=[],
            tags=["cc0", "rigged", "needs_motion", "full_body"],
            notes=["Inspection: 34 bones, zero Actions; selected over Gobkit for full-body visual suitability."],
        ),
        row(
            "animal.duck",
            oga / "duck6.blend",
            source_uri="https://opengameart.org/content/rigged-duck",
            pack_id="opengameart.rigged_duck",
            license_uri="https://opengameart.org/content/rigged-duck",
            rig_profile="opengameart.duck.v1",
            clips=["Waddle", "Peck"],
            tags=["cc0", "rigged", "animated", "low_poly", "full_body"],
            notes=["Inspection: 5 bones with Waddle and Peck Actions; selected as canonical duck."],
        ),
        row(
            "animal.dinosaur",
            gob / "Trex.glb",
            source_uri="https://gobkit.com/freebies/dino/Trex.glb",
            pack_id="gobkit.dino_pack",
            license_uri="https://gobkit.com/api/free",
            rig_profile="gobkit.dino.trex",
            clips=["idle", "attack", "dead", "walk"],
            tags=["cc0", "rigged", "animated", "low_poly", "baked_track"],
            notes=["Gobkit manifest: 24fps; idle/attack/dead/walk baked into one track."],
        ),
        row(
            "animal.buffalo",
            kenney / "animal-bison.glb",
            source_uri="https://kenney.nl/assets/prototype-kit",
            pack_id="kenney.prototype_kit",
            license_uri=rel(q / "kenney_prototype_kit_extracted" / "License.txt"),
            rig_profile="kenney.hierarchy_quadruped",
            clips=["down", "run", "up", "walk"],
            tags=["cc0", "animated_hierarchy", "buffalo_proxy", "low_poly"],
            notes=["Blender import inspection found run/walk/up/down hierarchy animation Actions."],
        ),
    ])

    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(
        yaml.safe_dump({"assets": rows}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"registered_external={len(rows)}")
    for item in rows:
        print(
            item["asset_id"],
            "technical=" + str(item["technical_qc_passed"]),
            item["local_path"],
        )


if __name__ == "__main__":
    main()
