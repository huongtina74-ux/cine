from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.studio.block_adapter import (
    BlockProductionStyle,
    CompanyToBlockAdapter,
)
from cinefactory.studio.block_production import BlockAnimationProducer


def main() -> None:
    ns = runpy.run_path(
        str(ROOT / "tests" / "test_render_intent_binding_v171.py")
    )
    shot, performance, graph, lighting = ns["_professional_block_inputs"]()
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="VERIFY_DAILIES_V171",
        episode_id="VERIFY_DAILIES_V171",
        title="Dailies evidence verification",
        shots=[shot],
        style=BlockProductionStyle.MINECRAFT,
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        creative_intent_graph=graph,
        performance_direction=performance,
        lighting_color_intent=lighting,
    )
    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    project_root = ROOT / "data" / "verification" / "v171_dailies"
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
        "selected_score": report.shots[0].selected_score,
        "technical_pass": take.technical_pass,
        "visual_pass": take.visual_pass,
        "identity_score": take.identity_score,
        "continuity_score": take.continuity_score,
        "performance_score": take.performance_score,
        "camera_score": take.camera_score,
        "aggregate_score": take.aggregate_score,
        "score_semantics": take.score_semantics,
        "evidence": take.evidence,
        "findings": take.findings,
    }
    out = project_root / "dailies_evidence.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
