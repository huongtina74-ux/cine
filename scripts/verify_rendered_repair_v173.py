from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.rendered_frame_qc import (
    RenderedAppearanceEvaluator,
    RenderedFrameAnalyzer,
    RenderedFrameQCResult,
)
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.production.failure_router import FailureRouter


def main() -> None:
    base = (
        ROOT
        / "data"
        / "verification"
        / "v172_continuity"
        / "renders"
        / "block_animation"
        / "shots"
    )
    first_video = base / "0000_S02_SH01.mp4"
    second_video = base / "0001_S02_SH02.mp4"
    first_qc_path = first_video.with_suffix(
        first_video.suffix + ".frame_qc.json"
    )
    second_geom_path = second_video.with_suffix(
        second_video.suffix + ".geometry_qc.json"
    )

    first_qc = RenderedFrameQCResult.model_validate_json(
        first_qc_path.read_text(encoding="utf-8")
    )
    second_geom = json.loads(
        second_geom_path.read_text(encoding="utf-8")
    )
    render_state = second_geom.get("render_state") or {}

    out_dir = ROOT / "data" / "verification" / "v173_rendered_repair"
    out_dir.mkdir(parents=True, exist_ok=True)
    drifted = out_dir / "shot2_lookdev_drift.mp4"

    media = FFmpegToolchain()
    media._run([
        media.ffmpeg,
        "-y",
        "-i",
        str(second_video),
        "-vf",
        "eq=brightness=0.35:saturation=2.0:contrast=1.10",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "17",
        "-pix_fmt",
        "yuv420p",
        str(drifted),
    ], timeout=300)

    analyzer = RenderedFrameAnalyzer(media)
    drift_qc = analyzer.analyze(
        drifted,
        render_state=render_state,
    )
    evaluator = RenderedAppearanceEvaluator()

    actor_comparisons = []
    findings = list(drift_qc.findings)
    findings.extend(
        f"RENDERED_FRAME_WARNING:{item}"
        for item in drift_qc.warnings
    )
    for actor_id, current in drift_qc.actors.items():
        reference = first_qc.actors.get(actor_id)
        if reference is None:
            continue
        comparison = evaluator.compare_actor(
            reference,
            current,
        )
        actor_comparisons.append(comparison)
        findings.extend(comparison.findings)

    cut = evaluator.compare_cut(
        first_qc.tail,
        drift_qc.head,
        same_scene=True,
        same_lighting_intent=True,
    )
    findings.extend(cut.findings)

    directives = FailureRouter().classify_all(
        "S02_SH02",
        findings,
    )

    payload = {
        "drifted_video": str(drifted),
        "frame_qc_passed": drift_qc.passed,
        "frame_findings": drift_qc.findings,
        "frame_warnings": drift_qc.warnings,
        "actor_comparisons": [
            item.model_dump(mode="json")
            for item in actor_comparisons
        ],
        "cut_appearance": cut.model_dump(mode="json"),
        "all_findings": findings,
        "repair_directives": [
            item.model_dump(mode="json")
            for item in directives
        ],
    }
    report = out_dir / "rendered_repair_verification.json"
    report.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
