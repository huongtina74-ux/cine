from __future__ import annotations

import hashlib
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "data" / "assets" / "animal_long_slide" / "internal"
CONFIG = ROOT / "config" / "animal_long_slide" / "assets.yaml"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def asset_id_from_file(path: Path) -> str:
    stem = path.stem
    if stem.startswith("scene_"):
        return "scene." + stem[len("scene_"):]
    if stem.startswith("obstacle_"):
        return "obstacle." + stem[len("obstacle_"):]
    raise ValueError(stem)


def main():
    rows = []
    for blend in sorted(ASSET_DIR.glob("*.blend")):
        asset_id = asset_id_from_file(blend)
        preview = ASSET_DIR / "previews" / (blend.stem + ".png")
        technical = blend.stat().st_size > 1024 and preview.is_file() and preview.stat().st_size > 1024
        rows.append({
            "asset_id": asset_id,
            "kind": "SCENE" if asset_id.startswith("scene.") else "OBSTACLE",
            "source_uri": "internal://animal-long-slide-generator",
            "source_pack_id": "internal.long_slide.bootstrap.v1",
            "license_evidence_uri": "internal://owned-original-procedural-assets",
            "license_state": "APPROVED",
            "commercial_use": True,
            "redistribution_allowed": True,
            "local_path": str(blend.relative_to(ROOT)).replace("\\", "/"),
            "version": "1",
            "blender_min_version": "4.5",
            "dependencies": [],
            "production_ready": False,
            "technical_qc_passed": technical,
            "visual_qc_passed": False,
            "content_sha256": sha256(blend),
            "provenance_notes": [
                "Generated procedurally by scripts/build_long_slide_internal_assets.py.",
                "Preview render exists; semantic visual approval is intentionally pending.",
            ],
            "tags": ["internal_owned", "procedural", "bootstrap", "needs_visual_approval"],
        })

    CONFIG.parent.mkdir(parents=True, exist_ok=True)
    CONFIG.write_text(
        yaml.safe_dump({"assets": rows}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"registered={len(rows)} config={CONFIG}")


if __name__ == "__main__":
    main()
