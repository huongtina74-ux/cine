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
        str(ROOT / "tests" / "test_visual_fidelity_v162.py")
    )
    episode = ns["style_episode"](
        "MINECRAFT",
        "mc_a",
        "minecraft_classroom",
        "minecraft_book",
    ).model_copy(
        update={
            "project_id": "VERIFY_PROP_V172",
            "episode_id": "VERIFY_PROP_V172",
            "width": 320,
            "height": 180,
            "quality_profile": "preview",
        }
    )
    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    project_root = ROOT / "data" / "verification" / "v172_prop"
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
    )
    try:
        report = producer.produce(
            episode,
            project_root=project_root,
            render_preview=True,
        )
    finally:
        producer.close()

    take = report.shots[0].takes[0]
    payload = {
        "passed": report.passed,
        "performance_score": take.performance_score,
        "camera_score": take.camera_score,
        "performance_qc": take.evidence.get("performance_qc"),
        "identity_qc": take.evidence.get("identity_qc"),
        "findings": take.findings,
    }
    out = project_root / "prop_contact_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
