from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import BlenderAnimationJob, EpisodeSpec
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.turbo.blender import PersistentBlenderWorker
from cinefactory.turbo.metrics import gpu_snapshot

BLENDER_EXECUTABLE = os.environ.get("CINEFACTORY_BLENDER_EXECUTABLE", "blender")
if not Path(BLENDER_EXECUTABLE).exists() and not shutil.which(BLENDER_EXECUTABLE):
    raise SystemExit("Blender not found on PATH or CINEFACTORY_BLENDER_EXECUTABLE")

episode = EpisodeSpec.model_validate_json((ROOT / "examples/block_animation/original_episode.json").read_text())
outdir = ROOT / "data" / "benchmarks" / "block-v1.6"
compiled = EpisodeAssembler.from_root(ROOT).compile(episode, output_dir=outdir)
worker = PersistentBlenderWorker(ROOT, blender_executable=BLENDER_EXECUTABLE)
runtime = BlockAnimationRuntime(ROOT)
rows = []
startup_started = time.monotonic()
startup = worker.start()
startup_seconds = time.monotonic() - startup_started
pid = startup["pid"]
try:
    for shot in compiled.shots:
        p = outdir / "shots" / f"{shot.order:04d}_{shot.shot_id}.mp4"
        t = time.monotonic()
        gpu_before = gpu_snapshot()
        result = runtime.render_and_qc(worker, BlenderAnimationJob(
            project_id=compiled.project_id,
            episode_id=compiled.episode_id,
            shot=shot,
            output_path=str(p),
        ))
        elapsed = time.monotonic()-t
        rows.append({
            "shot_id": shot.shot_id,
            "frames": shot.frame_end,
            "resolution": {"width": shot.width, "height": shot.height},
            "render_duration_seconds": elapsed,
            "seconds_per_frame": elapsed/max(1, shot.frame_end),
            "pid": worker.pid,
            "quality_profile": shot.render_quality.profile_id,
            "gpu_before": gpu_before,
            "result": result,
            "gpu_after": gpu_snapshot(),
        })
finally:
    worker.close()
report = {
    "version": "1.6.1-validation",
    "benchmark": "original_v1.6_block_animation",
    "blender_executable": str(Path(BLENDER_EXECUTABLE).resolve()) if Path(BLENDER_EXECUTABLE).exists() else BLENDER_EXECUTABLE,
    "persistent_pid": pid,
    "worker_startup_seconds": startup_seconds,
    "shots": rows,
}
report_path = ROOT / "data" / "validation" / "v1.6.1" / "rtx3060_raw_benchmark.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
