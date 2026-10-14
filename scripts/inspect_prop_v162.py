"""Render one prop-presentation shot for a fast visual attachment check."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler  # noqa: E402
from cinefactory.block_animation.contracts import BlenderAnimationJob  # noqa: E402
from cinefactory.block_animation.execution import BlockExecutionPlanner  # noqa: E402
from cinefactory.block_animation.runtime import BlockAnimationRuntime  # noqa: E402
from cinefactory.turbo.blender import PersistentBlenderWorker  # noqa: E402
from beauty_fidelity_v162 import build_episode, resolve_blender, style_definition  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", choices=["MINECRAFT", "ROBLOX"], default="MINECRAFT")
    parser.add_argument("--order", type=int, default=6)
    args = parser.parse_args()
    folder = "minecraft" if args.style == "MINECRAFT" else "roblox"
    out_root = ROOT / "data" / "validation" / "v1.6.2" / folder
    assembler = EpisodeAssembler.from_root(ROOT)
    compiled = assembler.compile(build_episode(args.style), output_dir=out_root)
    shot = compiled.shots[args.order]
    output = out_root / "inspection" / f"prop_test_{args.style.lower()}_{shot.shot_id}.mp4"
    output.parent.mkdir(parents=True, exist_ok=True)
    job = BlenderAnimationJob(project_id=compiled.project_id, episode_id=compiled.episode_id, shot=shot, output_path=str(output))
    worker = PersistentBlenderWorker(ROOT, blender_executable=resolve_blender(), startup_timeout=180, job_timeout=7200)
    try:
        worker.start()
        BlockAnimationRuntime(ROOT).render_and_qc(worker, job)
    finally:
        worker.close()
    print(output)
    print(worker.last_result or {})


if __name__ == "__main__":
    main()
