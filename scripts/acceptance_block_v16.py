from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import BlenderAnimationJob, EpisodeSpec
from cinefactory.block_animation.execution import BlockExecutionPlanner
from cinefactory.block_animation.runtime import BlockAnimationRuntime
from cinefactory.block_animation.visual_qc import BlockVisualQC
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.turbo.blender import PersistentBlenderWorker
from cinefactory.turbo.contracts import ResourceClass, WorkerSpec
from cinefactory.turbo.metrics import gpu_snapshot
from cinefactory.turbo.store import TurboStore

OUT = ROOT / "data" / "acceptance" / "v1.6"
OUT.mkdir(parents=True, exist_ok=True)
RESULTS = []


def rec(name, status, **kw):
    RESULTS.append({"name": name, "status": status, **kw})


for name in ("prefill.db", "prefill.db-wal", "prefill.db-shm"):
    (OUT / name).unlink(missing_ok=True)
for p in OUT.glob("protocol_*.mp4"):
    p.unlink(missing_ok=True)

# Compile + execution coverage.
episode = EpisodeSpec.model_validate_json((ROOT / "examples/block_animation/original_episode.json").read_text())
assembler = EpisodeAssembler.from_root(ROOT)
compiled = assembler.compile(episode, output_dir=OUT / "rendered")
assembler.write_compiled(compiled, OUT / "EP_DEMO_001.compiled.json")
plan0 = BlockExecutionPlanner.plan(BlenderAnimationJob(
    project_id=compiled.project_id,
    episode_id=compiled.episode_id,
    shot=compiled.shots[0],
    output_path=str(OUT / "plan_probe.mp4"),
))
rec(
    "episode_compile_execution_plan",
    "PASS",
    shots=len(compiled.shots),
    quality_profile=plan0["render_quality"]["profile_id"],
    scene_mode=plan0["scene_mode"],
    props=len(plan0["props"]),
    events=len(plan0["events"]),
    camera_motion=(plan0["camera"] or {}).get("motion"),
)

# Queue prefill.
store = TurboStore(OUT / "prefill.db")
assembler.enqueue(compiled, store, output_dir=OUT / "rendered")
worker_spec = WorkerSpec(worker_id="g", resources={ResourceClass.GPU}, capabilities={"blender.animation.render"})
ready = store.ready_work_count(worker_spec)
rec("gpu_queue_prefill", "PASS" if ready == len(compiled.shots) else "FAIL", ready_depth=ready, expected=len(compiled.shots))

# Persistent protocol: no Blender required.
mock = PersistentBlenderWorker(
    OUT,
    command=[sys.executable, str(ROOT / "scripts/mock_blender_persistent_worker.py")],
    startup_timeout=5,
    job_timeout=5,
)
pid = mock.start()["pid"]
for i, shot in enumerate(compiled.shots):
    mock.execute_animation(BlenderAnimationJob(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot=shot,
        output_path=str(OUT / f"protocol_{i}.mp4"),
    ))
rec("persistent_worker_same_pid", "PASS" if mock.ping()["pid"] == pid else "FAIL", pid=pid, jobs=len(compiled.shots))
mock.close()

# Local visual QC on moving diagnostic material.
ff = FFmpegToolchain()
moving = OUT / "visual_qc_moving.mp4"
subprocess.run([
    ff.ffmpeg, "-y", "-loglevel", "error", "-f", "lavfi", "-i",
    "testsrc2=size=640x360:rate=24:duration=1.5",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(moving)
], check=True)
vqc = BlockVisualQC(ff).review(moving)
rec("zero_api_visual_qc", "PASS" if vqc.passed else "FAIL", findings=vqc.findings, black_seconds=vqc.black_seconds, freeze_seconds=vqc.freeze_seconds)

# Episode assembly diagnostic (not beauty evidence).
shots = []
for shot in compiled.shots:
    p = OUT / "diagnostic_shots" / f"{shot.order:04d}_{shot.shot_id}.mp4"
    ff.make_slate(f"CineFactory v1.6 diagnostic - {shot.shot_id}", p, duration=shot.duration_seconds, size=f"{shot.width}x{shot.height}", fps=shot.fps)
    shots.append({"shot_id": shot.shot_id, "order": shot.order, "path": str(p)})
assembled = BlockAnimationRuntime(ROOT).assemble_episode({
    "episode_id": compiled.episode_id,
    "output_path": str(OUT / "cinefactory-v1.6-diagnostic.mp4"),
    "shots": shots,
})
rec("ffmpeg_episode_assembly", "PASS", **assembled, note="diagnostic slate video; not Blender beauty-quality evidence")

blender = shutil.which("blender")
if blender:
    rec("real_blender_render", "READY", blender=blender, note="Run scripts/benchmark_block_rtx3060_v16.py for target render benchmark")
else:
    rec("real_blender_render", "SKIP", reason="Blender not installed in build environment")

report = {
    "version": "1.6.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "policy": "ZERO_METERED_API / ZERO_API_QUALITY intent",
    "ffmpeg": shutil.which("ffmpeg"),
    "blender": blender,
    "gpu": gpu_snapshot(),
    "results": RESULTS,
}
report["passed"] = all(x["status"] in {"PASS", "SKIP", "READY"} for x in RESULTS)
path = OUT / "cinefactory-os-v1.6-acceptance-report.json"
path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
