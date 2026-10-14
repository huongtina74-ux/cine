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
from cinefactory.block_animation.contracts import BlenderAnimationJob
from cinefactory.block_animation.execution import BlockExecutionPlanner
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.block_animation.visual_qc import BlockVisualQC
from cinefactory.turbo.blender import PersistentBlenderWorker
from scripts.beauty_benchmark_001 import build_episode


validation_root = ROOT / "data" / "validation" / "v1.6.1"
phase_root = validation_root / "beauty_benchmark_001_after"
assembler = EpisodeAssembler.from_root(ROOT)
compiled = assembler.compile(build_episode(), output_dir=phase_root)
assembler.write_compiled(compiled, phase_root / "compiled_episode.json")
shot = compiled.shots[7]
output_path = phase_root / "shots" / f"{shot.order:04d}_{shot.shot_id}.mp4"
plan = BlockExecutionPlanner.plan(BlenderAnimationJob(
    project_id=compiled.project_id,
    episode_id=compiled.episode_id,
    shot=shot,
    output_path=str(output_path),
))
(phase_root / "execution_plans" / f"{shot.order:04d}_{shot.shot_id}.json").write_text(
    json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
)

worker = PersistentBlenderWorker(
    ROOT,
    blender_executable=os.environ.get("CINEFACTORY_BLENDER_EXECUTABLE", "blender"),
    startup_timeout=180,
    job_timeout=7200,
)
runtime = BlockAnimationRuntime(ROOT)
started = time.monotonic()
worker.start()
try:
    result = runtime.render_and_qc(worker, BlenderAnimationJob(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot=shot,
        output_path=str(output_path),
    ))
finally:
    worker.close()
result["retake_duration_seconds"] = time.monotonic() - started

master_path = validation_root / "beauty_benchmark_001_after.mp4"
assembled = runtime.assemble_episode({
    "episode_id": compiled.episode_id,
    "output_path": str(master_path),
    "shots": [
        {
            "shot_id": item.shot_id,
            "order": item.order,
            "path": str(phase_root / "shots" / f"{item.order:04d}_{item.shot_id}.mp4"),
        }
        for item in compiled.shots
    ],
})
master_qc = BlockVisualQC().review(master_path)
metrics_path = phase_root / "benchmark_metrics.json"
report = json.loads(metrics_path.read_text(encoding="utf-8"))
report["shots"][7]["result"] = result
report["shots"][7]["render_duration_seconds"] = result["retake_duration_seconds"]
report["shots"][7]["seconds_per_frame"] = result["retake_duration_seconds"] / max(1, shot.frame_end)
report["assembled"] = assembled
report["master_visual_qc"] = {
    "passed": master_qc.passed,
    "findings": master_qc.findings,
    "black_seconds": master_qc.black_seconds,
    "freeze_seconds": master_qc.freeze_seconds,
}
metrics_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
(phase_root / "qc_report.json").write_text(json.dumps(report["master_visual_qc"], ensure_ascii=False, indent=2), encoding="utf-8")
shutil.copy2(assembled["event_manifest"], phase_root / "events_manifest.json")
final_dir = validation_root / "beauty_benchmark_001"
final_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(master_path, final_dir / "master.mp4")
shutil.copy2(phase_root / "compiled_episode.json", final_dir / "compiled_episode.json")
shutil.copytree(phase_root / "execution_plans", final_dir / "execution_plans", dirs_exist_ok=True)
shutil.copytree(phase_root / "shots", final_dir / "shots", dirs_exist_ok=True)
shutil.copy2(phase_root / "events_manifest.json", final_dir / "events_manifest.json")
shutil.copy2(phase_root / "benchmark_metrics.json", final_dir / "benchmark_metrics.json")
shutil.copy2(phase_root / "qc_report.json", final_dir / "qc_report.json")
print(json.dumps({"retaken_shot": shot.shot_id, "result": result, "assembled": assembled, "master_visual_qc": report["master_visual_qc"]}, indent=2))
