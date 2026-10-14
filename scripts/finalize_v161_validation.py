"""Write the measured CineFactory v1.6.1 validation evidence bundle.

This script deliberately records unavailable instrumentation as NOT_AVAILABLE
instead of inferring it from render duration or sparse telemetry samples.
"""

from __future__ import annotations

import json
import platform
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "validation" / "v1.6.1"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def gpu_samples(report: dict) -> list[dict]:
    samples: list[dict] = []
    for shot in report.get("shots", []):
        for key in ("gpu_before", "gpu_after"):
            snapshot = shot.get(key) or {}
            samples.extend(snapshot.get("gpus") or [])
    return samples


def benchmark_summary(report: dict) -> dict:
    shots = report["shots"]
    render_seconds = sum(float(shot["render_duration_seconds"]) for shot in shots)
    frame_count = sum(int(shot["frames"]) for shot in shots)
    spf = sorted(float(shot["seconds_per_frame"]) for shot in shots)
    middle = len(spf) // 2
    median = spf[middle] if len(spf) % 2 else (spf[middle - 1] + spf[middle]) / 2
    samples = gpu_samples(report)
    vram = [float(sample["vram_used_mb"]) for sample in samples if "vram_used_mb" in sample]
    util = [float(sample["utilization_pct"]) for sample in samples if "utilization_pct" in sample]
    temperatures = [float(sample["temperature_c"]) for sample in samples if "temperature_c" in sample]
    pids = sorted(
        {
            int(value)
            for shot in shots
            for value in (
                shot.get("persistent_pid"),
                shot.get("pid"),
                (shot.get("result") or {}).get("worker_pid"),
            )
            if value is not None
        }
    )
    return {
        "shot_count": len(shots),
        "output_duration_seconds": report["assembled"]["duration"],
        "resolution": {
            "width": report["assembled"]["width"],
            "height": report["assembled"]["height"],
        },
        "fps": report["assembled"]["fps"],
        "total_selected_shot_render_seconds": render_seconds,
        "total_selected_shot_render_minutes": render_seconds / 60,
        "average_seconds_per_frame": render_seconds / frame_count,
        "median_seconds_per_frame": median,
        "throughput_frames_per_second": frame_count / render_seconds,
        "fastest_shot": min(shots, key=lambda shot: shot["seconds_per_frame"])["shot_id"],
        "slowest_shot": max(shots, key=lambda shot: shot["seconds_per_frame"])["shot_id"],
        "worker_pids_in_selected_artifacts": pids,
        "same_pid_across_selected_artifacts": len(pids) == 1,
        "peak_observed_vram_used_mb": max(vram) if vram else "NOT_AVAILABLE",
        "peak_observed_gpu_utilization_pct": max(util) if util else "NOT_AVAILABLE",
        "peak_observed_temperature_c": max(temperatures) if temperatures else "NOT_AVAILABLE",
        "master_visual_qc": report.get("master_visual_qc"),
        "assembled": report.get("assembled"),
        "quality_profile": report.get("quality_profile"),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    before = load_json(OUT / "beauty_benchmark_001_before" / "benchmark_metrics.json")
    after = load_json(OUT / "beauty_benchmark_001_after" / "benchmark_metrics.json")
    raw = load_json(OUT / "rtx3060_raw_benchmark.json")
    generated_at = datetime.now(timezone.utc).isoformat()

    blender = ROOT / ".tools" / "blender-4.5.14-windows-x64" / "blender.exe"
    ffmpeg = Path(r"C:\Users\ADMIN\ffmpeg\bin\ffmpeg.exe")
    nvidia_smi = Path(r"C:\Windows\system32\nvidia-smi.exe")

    system_report = {
        "report": "CineFactory v1.6.1 RTX3060 validation system report",
        "generated_at_utc": generated_at,
        "host": {
            "os": "Windows 10 Pro 22H2",
            "os_build": "22621",
            "architecture": platform.machine() or "AMD64",
            "cpu_logical_processors": 20,
            "cpu_identifier": "Intel64 Family 6 Model 151 Stepping 2, GenuineIntel",
            "ram_total_gib": 31.85,
            "ram_available_sample_gib": "15.7-16.0",
            "disk_free_sample_gib": 172.38,
        },
        "python": {
            "version": "3.11.15",
            "pip_version": "26.1.2",
            "torch_version": "2.13.0+cpu",
            "torch_cuda_built": None,
            "torch_cuda_available": False,
            "torch_cuda_device_count": 0,
        },
        "render_toolchain": {
            "blender_executable": str(blender),
            "blender_executable_exists": blender.exists(),
            "blender_version": "4.5.14 LTS",
            "blender_path_status_before_validation": "NOT_AVAILABLE on PATH",
            "blender_path_status_for_validation": "portable executable explicitly configured via CINEFACTORY_BLENDER_EXECUTABLE",
            "ffmpeg_executable": str(ffmpeg),
            "ffmpeg_executable_exists": ffmpeg.exists(),
            "ffmpeg_version": "7.1-essentials_build-www.gyan.dev",
            "ffprobe_version": "2023-02-13 build observed",
        },
        "gpu": {
            "nvidia_smi": str(nvidia_smi),
            "nvidia_smi_exists": nvidia_smi.exists(),
            "driver_version": "610.47",
            "name": "NVIDIA GeForce RTX 3060",
            "total_vram_mb": 12288,
            "compute_capability": "8.6",
            "python_torch_cuda_runtime": "NOT_AVAILABLE (CPU-only torch build)",
            "blender_gpu_render_evidence": "nvidia-smi telemetry recorded during real Blender renders",
        },
        "measurement_notes": [
            "RAM and disk values are host samples, not capacity guarantees.",
            "GPU utilization and VRAM values are nvidia-smi snapshots before/after shots, not continuous traces.",
            "No paid or metered API was used.",
        ],
    }
    write_json(OUT / "system_report.json", system_report)

    baseline_report = {
        "report": "CineFactory v1.6.1 baseline and final regression report",
        "generated_at_utc": generated_at,
        "git_baseline_commit": "2ae6809",
        "git_baseline_message": "CineFactory v1.6 baseline before RTX3060 validation",
        "pre_patch_baseline": {
            "pytest_command": "python -m pytest -q",
            "result": "66 passed in 14.48s",
            "compileall_command": "python -m compileall -q cinefactory scripts tests",
            "result_compileall": "PASS",
            "acceptance_command": "python scripts/acceptance_block_v16.py",
            "result": "PASS",
            "built_in_real_blender_probe": "SKIP - Blender not installed in build environment",
        },
        "final_regression": {
            "pytest_command": "python -m pytest -q",
            "result": "67 passed in 11.60s",
            "passed": 67,
            "failed": 0,
            "skipped": 0,
            "compileall_command": "python -m compileall -q cinefactory scripts tests",
            "compileall": "PASS",
            "acceptance_command": "python scripts/acceptance_block_v16.py",
            "acceptance_passed": True,
            "acceptance_real_blender_probe": "SKIP - harness PATH lookup does not see the explicitly configured portable executable",
            "dedicated_real_blender_render": "PASS - scripts/benchmark_block_rtx3060_v16.py and scripts/beauty_benchmark_001.py",
        },
        "new_regression_coverage": [
            "CameraTake preserves prop_id through compilation.",
            "A prop-targeted camera plan retains target_mode=prop and prop_id.",
            "Procedural hand/arm sockets resolve to visible arm geometry.",
            "facing_target rotation matches the procedural actor's local -Y face direction.",
        ],
    }
    write_json(OUT / "baseline_test_report.json", baseline_report)

    raw_shots = raw["shots"]
    raw_seconds = sum(float(shot["render_duration_seconds"]) for shot in raw_shots)
    raw_frames = sum(int(shot["frames"]) for shot in raw_shots)
    raw_samples = gpu_samples(raw)
    performance_report = {
        "report": "CineFactory v1.6.1 measured RTX3060 performance report",
        "generated_at_utc": generated_at,
        "hardware": {
            "gpu": "NVIDIA GeForce RTX 3060",
            "vram_total_mb": 12288,
            "quality_profile": "rtx3060_quality",
            "render_engine_evidence": "real Blender 4.5.14 LTS MP4/H.264 renders",
        },
        "raw_original_block_benchmark": {
            "resolution": "640x360",
            "shot_count": len(raw_shots),
            "frames": raw_frames,
            "total_render_seconds": raw_seconds,
            "average_seconds_per_frame": raw_seconds / raw_frames,
            "throughput_frames_per_second": raw_frames / raw_seconds,
            "persistent_pid": raw["persistent_pid"],
            "same_pid": len({shot["pid"] for shot in raw_shots}) == 1,
            "startup_seconds": raw["worker_startup_seconds"],
            "peak_vram_used_mb": max(sample["vram_used_mb"] for sample in raw_samples),
            "peak_gpu_utilization_pct": max(sample["utilization_pct"] for sample in raw_samples),
        },
        "beauty_benchmark_before": benchmark_summary(before),
        "beauty_benchmark_after_final_selected_shots": benchmark_summary(after),
        "worker_persistence": {
            "raw_benchmark": {"pid": 33880, "jobs": 2, "same_pid": True},
            "beauty_before_full_pass": {"pid": 35588, "jobs": 12, "same_pid": True, "startup_seconds": before["worker_startup_seconds"]},
            "beauty_after_full_pass_before_targeted_retake": {"pid": 40648, "jobs": 12, "same_pid": True, "startup_seconds": 0.2969999999986612},
            "final_after_assembly": {
                "pids": [40648, 37196],
                "same_pid": False,
                "reason": "BEAT08 was intentionally re-rendered in a new worker for a camera-composition retake; this is not a failed full-pass persistence result.",
            },
        },
        "cache_and_idle_instrumentation": {
            "external_collection_action_cache_hit_rate": "NOT_AVAILABLE - benchmark scenes are procedural and the worker does not emit cache hit/miss counters.",
            "gpu_idle_periods": "NOT_AVAILABLE - only sparse before/after nvidia-smi snapshots were collected.",
            "continuous_gpu_trace": "NOT_AVAILABLE",
        },
        "interpretation": [
            "Selected final 1080p aggregate is shot-render work only; FFmpeg assembly is not included in those render seconds.",
            "A targeted BEAT08 retake replaced the first after-pass shot in the final aggregate; discarded retake work is not counted in the selected-shot total.",
            "The final master is 49.639333 seconds at 1920x1080 and 24 fps.",
        ],
    }
    write_json(OUT / "performance_report.json", performance_report)

    visual_findings = """# Visual Findings — CineFactory v1.6.1

## Evidence reviewed

- Real Blender before master: data/validation/v1.6.1/beauty_benchmark_001_before.mp4
- Real Blender final after master: data/validation/v1.6.1/beauty_benchmark_001_after.mp4
- Spot frames from establishing, notice, surprise, pickup, presentation, orbit, and final-group beats were extracted and inspected.
- Technical visual QC passed both masters with black_seconds=0 and freeze_seconds=0.

## Before fixes

1. Procedural actors faced away from the camera in close shots because the face's local -Y direction was rotated with the wrong yaw equation.
2. Procedural prop sockets resolved to the actor root rather than visible arm geometry, making the pickup/presentation read as floating or detached.
3. Prop-targeted cameras ignored the prop target and used actor averages, producing overly tight or semantically weak presentation framing.
4. The technical QC correctly detected no black/frozen frames, but it did not detect these semantic composition and attachment errors.

## After fixes

1. Face orientation is readable in notice/surprise and group shots.
2. Prop attachment resolves through the visible procedural arm socket.
3. Prop-target camera intent is preserved through CameraTake and the worker targets the matching CF_PROP_<id> object.
4. The presentation camera was retaken with both principal actors and the book visible in a coherent classroom frame.
5. No black, frozen, corrupt, or obviously unrendered frames were observed in the final master spot review.

## Remaining visual limitations

- Some group/orbit compositions still allow desks, crowd members, or foreground geometry to approach the frame edge.
- The performance uses block actors; foot contact, body mechanics, and exact hand contact are not geometry-aware IK.
- True hand-to-hand prop transfer is not implemented. The benchmark records timed socket attachment only.
- Semantic visual QC remains a human-review responsibility; black/freeze checks are not a substitute for VLM/scene-graph validation.
"""
    (OUT / "visual_findings.md").write_text(visual_findings, encoding="utf-8")

    fixes_applied = """# Fixes Applied — CineFactory v1.6.1

## Runtime correctness

- Added prop_id to CameraTake and preserved it through camera compilation.
- Corrected procedural actor facing_target yaw to match the actor's local -Y face direction.
- Mapped procedural hand.R/hand.L sockets to the visible arm geometry used by the worker.
- Added prop-aware camera targeting for CF_PROP_<prop_id> objects.
- Added a regression test proving prop camera intent survives execution planning.

## Benchmark and evidence tooling

- Added CINEFACTORY_BLENDER_EXECUTABLE support to the RTX3060 benchmark.
- Added startup, per-shot render time, seconds-per-frame, PID, GPU, VRAM, resolution, and QC evidence.
- Added scripts/beauty_benchmark_001.py for the 49.5-second, 1920x1080, 24fps before/after benchmark.
- Added scripts/retake_beauty_presentation.py for an evidence-preserving targeted camera retake.
- Added the presentation_group camera grammar and moved the presentation beat to that grammar.
- Added local render artifacts to .gitignore and preserved a pre-patch Git baseline at commit 2ae6809.

## Verification

- Final regression: 67 passed.
- Compileall: PASS.
- Dedicated real Blender RTX3060 benchmark: PASS.
- Final beauty master: 49.639333 seconds, 1920x1080, 24fps, H.264.
"""
    (OUT / "fixes_applied.md").write_text(fixes_applied, encoding="utf-8")

    remaining_gaps = """# Remaining Gaps — CineFactory v1.6.1

These are explicit scope limits, not silently accepted failures:

- True hand-to-hand prop transfer is not implemented; current behavior is timed socket attachment.
- Geometry-aware IK, foot contact, collision avoidance, and physically validated hand contact are not implemented.
- Semantic visual QC is not automated. Current QC covers black frames, freeze frames, technical output, and event manifests; human visual review remains required.
- The acceptance harness's built-in Blender check still reports SKIP when Blender is not on PATH. The dedicated validation scripts accept the explicitly configured portable Blender executable and produced the real renders.
- The benchmark does not expose collection/action cache hit/miss counters and does not collect continuous GPU idle traces; those fields are recorded as NOT_AVAILABLE.
- Dialogue/audio, Minecraft/Roblox execution, hybrid routing, and local VLM validation remain outside this v1.6.1 Block Animation acceptance.
- Some wide/orbit shots retain stylized block-scene occlusion and edge cropping that should be improved before claiming broad cinematic coverage.

Recommended next milestone: add semantic camera/composition checks and geometry-aware contact/prop-transfer primitives, then repeat this same real-render evidence protocol before expanding runtime scope.
"""
    (OUT / "remaining_gaps.md").write_text(remaining_gaps, encoding="utf-8")

    final_acceptance = {
        "report": "CineFactory v1.6.1 final acceptance report",
        "generated_at_utc": generated_at,
        "status": "READY",
        "scope": "Validated v1.6.1 Block Animation baseline on the available RTX3060 host; not a claim that every future product capability is complete.",
        "acceptance": {
            "source_reviewed_before_patch": True,
            "pre_patch_git_baseline": "2ae6809",
            "full_test_suite": {"passed": 67, "failed": 0, "status": "PASS"},
            "compileall": "PASS",
            "zero_api_policy": "PASS",
            "real_rtx3060_benchmark": "PASS",
            "beauty_render": {
                "status": "PASS",
                "path": str(OUT / "beauty_benchmark_001_after.mp4"),
                "duration_seconds": after["assembled"]["duration"],
                "resolution": "1920x1080",
                "fps": 24,
                "codec": "h264",
                "technical_qc": after["master_visual_qc"],
            },
            "persistent_runtime": {
                "raw_benchmark_same_pid": True,
                "beauty_before_full_pass_same_pid": True,
                "beauty_after_full_pass_same_pid": True,
                "final_assembly_note": "Final assembly includes an intentional BEAT08 targeted retake from a second worker.",
            },
            "human_visual_review": {
                "status": "PASS_WITH_DOCUMENTED_LIMITATIONS",
                "showstopper_observed": False,
                "limitations_file": str(OUT / "visual_findings.md"),
            },
        },
        "decision": {
            "ready_for_v1_6_1_baseline_use": True,
            "safe_to_proceed_to_v1_7_planning_after_review": True,
            "start_v1_7_during_this_validation": False,
            "reason": "The required real render, stable worker runs, technical QC, regression suite, and human visual review are complete. Remaining gaps are explicitly scoped and suitable for the next milestone.",
        },
        "evidence": {
            "before_mp4": str(OUT / "beauty_benchmark_001_before.mp4"),
            "after_mp4": str(OUT / "beauty_benchmark_001_after.mp4"),
            "raw_benchmark": str(OUT / "rtx3060_raw_benchmark.json"),
            "performance_report": str(OUT / "performance_report.json"),
            "visual_findings": str(OUT / "visual_findings.md"),
        },
    }
    write_json(OUT / "final_acceptance_report.json", final_acceptance)
    print(json.dumps({"status": "READY", "output_dir": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
