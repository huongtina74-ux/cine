from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.animal_long_slide import AssetKind, LongSlideAssetRegistry


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--force", action="store_true")
    p.add_argument("--asset-id", action="append", default=[])
    return p.parse_args()


def main():
    ns = parse_args()
    registry = LongSlideAssetRegistry.load(ROOT)
    blender = (
        ROOT / ".tools" / "blender-4.5.14-windows-x64" / "blender.exe"
    )
    if not blender.is_file():
        raise SystemExit(f"Blender missing: {blender}")
    script = ROOT / "scripts" / "render_long_slide_asset_preview.py"
    out_dir = ROOT / "renders" / "animal_long_slide" / "qualification_previews"
    out_dir.mkdir(parents=True, exist_ok=True)

    wanted = set(ns.asset_id)
    failures = []
    rendered = 0
    skipped = 0

    for asset in registry.values():
        if asset.kind is not AssetKind.ANIMAL:
            continue
        if wanted and asset.asset_id not in wanted:
            continue
        if not registry.preview_qualified(asset):
            skipped += 1
            print(f"SKIP::{asset.asset_id}::NOT_PREVIEW_QUALIFIED")
            continue
        src = registry.resolve_local_path(ROOT, asset)
        if src is None or not src.is_file():
            skipped += 1
            print(f"SKIP::{asset.asset_id}::MISSING_SOURCE")
            continue
        dst = out_dir / f"{asset.asset_id.replace('.', '_')}.png"
        if dst.is_file() and dst.stat().st_size > 1024 and not ns.force:
            skipped += 1
            print(f"SKIP::{asset.asset_id}::PREVIEW_EXISTS")
            continue

        command = [
            str(blender),
            "--background",
            "--factory-startup",
            "--python",
            str(script),
            "--",
            "--input",
            str(src),
            "--output",
            str(dst),
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0 or not dst.is_file():
            failures.append(asset.asset_id)
            print(
                f"FAIL::{asset.asset_id}::"
                + (result.stderr[-500:] or result.stdout[-500:])
            )
            continue
        rendered += 1
        print(f"RENDERED::{asset.asset_id}::{dst}")

    print(
        f"PREVIEW_FARM_SUMMARY::rendered={rendered}::"
        f"skipped={skipped}::failed={len(failures)}"
    )
    if failures:
        print("FAILED_ASSETS::" + ",".join(failures))


if __name__ == "__main__":
    main()
