from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.studio.block_production import BlockAnimationProducer


def main() -> None:
    ns = runpy.run_path(
        str(ROOT / "tests" / "test_block_auto_repair_v173.py")
    )
    episode = ns["_episode"]().model_copy(
        update={
            "project_id": "VERIFY_AUTO_REPAIR_V173",
            "episode_id": "VERIFY_AUTO_REPAIR_V173",
        }
    )

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    project_root = (
        ROOT
        / "data"
        / "verification"
        / "v173_auto_repair"
    )
    output_dir = (
        project_root
        / "renders"
        / "block_animation"
    )

    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
        max_repair_rounds=2,
    )
    compiled = producer.assembler.compile(
        episode,
        output_dir=output_dir,
    )
    compiled.shots[0].render_quality.exposure = -3.0

    original_compile = producer.assembler.compile
    producer.assembler.compile = lambda *args, **kwargs: compiled
    try:
        report = producer.produce(
            episode,
            project_root=project_root,
            render_preview=True,
        )
    finally:
        producer.assembler.compile = original_compile
        producer.close()

    shot = report.shots[0]
    takes = []
    for take in shot.takes:
        takes.append(
            {
                "take_id": take.take_id,
                "repair_round": take.repair_round,
                "technical_pass": take.technical_pass,
                "visual_pass": take.visual_pass,
                "failure_code": (
                    take.failure_code.value
                    if take.failure_code is not None
                    else None
                ),
                "findings": take.findings,
                "repair_plan_next": take.evidence.get(
                    "repair_plan_next"
                ),
                "rendered_frame_qc": take.evidence.get(
                    "rendered_frame_qc"
                ),
                "path": take.path,
            }
        )

    payload = {
        "passed": report.passed,
        "selected_take_id": shot.selected_take_id,
        "selected_path": shot.selected_path,
        "selected_score": shot.selected_score,
        "takes": takes,
        "remaining_repair_directives": [
            item.model_dump(mode="json")
            for item in shot.repair_directives
        ],
    }
    project_root.mkdir(parents=True, exist_ok=True)
    report_path = (
        project_root
        / "auto_repair_verification.json"
    )
    report_path.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
