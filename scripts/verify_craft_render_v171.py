from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import BlenderAnimationJob
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.studio.block_adapter import (
    BlockProductionStyle,
    CompanyToBlockAdapter,
)
from cinefactory.turbo.blender import PersistentBlenderWorker


ROOT = Path(__file__).resolve().parents[1]
BLENDER = (
    ROOT
    / ".tools"
    / "blender-4.5.14-windows-x64"
    / "blender.exe"
)


def main() -> None:
    test_ns = runpy.run_path(
        str(ROOT / "tests" / "test_render_intent_binding_v171.py")
    )
    shot, performance, graph, lighting = (
        test_ns["_professional_block_inputs"]()
    )
    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="VERIFY_V171",
        episode_id="VERIFY_V171",
        title="Craft render verification",
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
    output_dir = ROOT / "data" / "verification" / "v171"
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=output_dir,
    )
    output = output_dir / "intent_preview.mp4"
    job = BlenderAnimationJob(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot=compiled.shots[0],
        output_path=str(output),
        render_preview=True,
    )
    worker = PersistentBlenderWorker(
        ROOT,
        blender_executable=str(BLENDER),
        startup_timeout=120,
        job_timeout=600,
    )
    try:
        result = BlockAnimationRuntime(ROOT).render_and_qc(
            worker,
            job,
        )
    finally:
        worker.close()
    report = {
        "path": result["path"],
        "geometry_qc": result["geometry_qc"],
        "gaze_debug": result["gaze_debug"],
        "lighting_debug": result["lighting_debug"],
        "creative_intent_bound": result["creative_intent_bound"],
        "performance_directive_count": (
            result["performance_directive_count"]
        ),
        "visual_qc": result["visual_qc"],
    }
    report_path = output_dir / "verification_report.json"
    report_path.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
