from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.animal_long_slide import (
    LongSlideAssetQualifier,
    LongSlideAssetRegistry,
    MotionCompatibilityGraph,
)
from cinefactory.qc.visual_command import CommandVisualQC


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--asset-id", action="append", default=[])
    p.add_argument("--visual-qc-command")
    p.add_argument("--min-visual-score", type=float, default=0.78)
    p.add_argument("--output-dir", default="data/animal_long_slide/qualification")
    return p.parse_args()


def preview_for(asset_id: str) -> Path | None:
    token = asset_id.replace(".", "_")
    candidates = [
        ROOT / "data" / "assets" / "animal_long_slide" / "internal" / "previews" / f"{token}.png",
        ROOT / "renders" / "animal_long_slide" / "qualification_previews" / f"{token}.png",
        ROOT / "renders" / "animal_long_slide" / "asset_previews_v2" / f"{asset_id.split('.',1)[-1]}.png",
        ROOT / "renders" / "animal_long_slide" / "asset_previews" / f"{asset_id.split('.',1)[-1]}.png",
    ]
    return next((p for p in candidates if p.is_file()), None)


def main():
    ns = parse_args()
    registry = LongSlideAssetRegistry.load(ROOT)
    motions = MotionCompatibilityGraph.load(ROOT)
    reviewer = (
        CommandVisualQC(ns.visual_qc_command)
        if ns.visual_qc_command
        else None
    )
    qualifier = LongSlideAssetQualifier(
        registry,
        motions=motions,
        reviewer=reviewer,
        min_visual_score=ns.min_visual_score,
    )
    ids = ns.asset_id or [asset.asset_id for asset in registry.values()]
    out_dir = (ROOT / ns.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "qualified": 0,
        "awaiting_visual_review": 0,
        "blocked": 0,
        "reports": [],
    }
    for asset_id in ids:
        report = qualifier.qualify(
            asset_id,
            preview_path=preview_for(asset_id),
        )
        path = out_dir / f"{asset_id.replace('.', '_')}.json"
        path.write_text(report.model_dump_json(indent=2), encoding="utf-8")
        summary["reports"].append(str(path))
        key = report.state.value.lower()
        if key == "awaiting_visual_review":
            summary["awaiting_visual_review"] += 1
        elif key == "qualified":
            summary["qualified"] += 1
        else:
            summary["blocked"] += 1
        print(
            f"{asset_id}::{report.state.value}::"
            + ",".join(report.blockers)
        )

    summary_path = out_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    print("QUALIFICATION_SUMMARY::" + json.dumps({
        k: v for k, v in summary.items() if k != "reports"
    }))


if __name__ == "__main__":
    main()
