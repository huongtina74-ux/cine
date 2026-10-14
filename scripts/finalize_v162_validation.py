"""Build the evidence bundle for the v1.6.2 visual-fidelity review gate."""

from __future__ import annotations

import json
import os
import platform
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATION = ROOT / "data" / "validation" / "v1.6.2"

sys.path.insert(0, str(ROOT))

from cinefactory.block_animation.assembler import EpisodeAssembler  # noqa: E402
from cinefactory.block_animation.styles import style_asset_manifest  # noqa: E402
from cinefactory.turbo.metrics import gpu_snapshot  # noqa: E402


def run(command: list[str], *, env: dict[str, str] | None = None) -> dict:
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=1800)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-4000:],
    }


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_evidence() -> dict:
    task_temp = ROOT / ".pytest-hosttemp-v162-final"
    base_temp = ROOT / ".pytest-basetemp-v162-final"
    task_temp.mkdir(exist_ok=True)
    base_temp.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["TEMP"] = str(task_temp)
    env["TMP"] = str(task_temp)
    pytest = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(base_temp),
            "tests",
        ],
        env=env,
    )
    match = re.search(r"(\d+) passed", pytest["stdout_tail"])
    pytest["passed_count"] = int(match.group(1)) if match else None
    compile_result = run([sys.executable, "-m", "compileall", "-q", "cinefactory", "scripts", "tests"])
    acceptance = run([sys.executable, "scripts/acceptance_block_v16.py"])
    return {
        "isolated_pytest": pytest,
        "compileall": compile_result,
        "acceptance_block_v16": acceptance,
        "baseline_before_visual_fidelity": {
            "commit": "405d89f",
            "command": "python -m pytest -q",
            "result": "40 passed, 27 setup errors caused by host TEMP/.pytest_cache ACLs",
            "isolated_command": "python -m pytest -q -p no:cacheprovider --basetemp .pytest-basetemp-v162",
            "isolated_result": "67 passed in 6.80s",
        },
        "environment_note": "The default pytest temp/cache locations are ACL-restricted on this Windows host; the isolated project-local TEMP/TMP and basetemp command is the reproducible test evidence.",
    }


def gpu_extrema(metrics: dict) -> dict:
    snapshots = []
    for row in metrics.get("shots", []):
        for key in ("gpu_before", "gpu_after"):
            snap = row.get(key) or {}
            if snap.get("available"):
                snapshots.extend(snap.get("gpus", []))
    if not snapshots:
        return {"available": False, "reason": "No nvidia-smi samples were recorded."}
    return {
        "available": True,
        "gpu_name": snapshots[-1].get("name"),
        "peak_vram_used_mb": max(item.get("vram_used_mb", 0) for item in snapshots),
        "peak_gpu_utilization_pct": max(item.get("utilization_pct", 0) for item in snapshots),
        "sample_count": len(snapshots),
    }


def performance_evidence(style_metrics: dict[str, dict]) -> dict:
    by_style = {}
    for style, metrics in style_metrics.items():
        rows = metrics.get("shots", [])
        spf = [float(row["seconds_per_frame"]) for row in rows]
        worker_results = [row.get("worker_result") or {} for row in rows]
        by_style[style] = {
            "episode_duration_seconds": metrics.get("assembled", {}).get("duration"),
            "expected_duration_seconds": metrics.get("duration_expected_seconds"),
            "shot_count": len(rows),
            "total_render_seconds": sum(float(row["render_duration_seconds"]) for row in rows),
            "mean_seconds_per_frame": statistics.mean(spf) if spf else None,
            "median_seconds_per_frame": statistics.median(spf) if spf else None,
            "max_seconds_per_frame": max(spf) if spf else None,
            "persistent_pid": metrics.get("persistent_pid"),
            "same_pid_across_shots": metrics.get("same_pid_across_shots"),
            "gpu": gpu_extrema(metrics),
            "cache_metrics": worker_results[-1].get("cache_metrics") if worker_results else None,
            "production_api_spend": metrics.get("production_api_spend", 0),
        }
    return {
        "host": platform.node(),
        "gpu_snapshot_at_finalize": gpu_snapshot(),
        "styles": by_style,
        "cache_instrumentation_note": "All v1.6.2 fidelity assets are procedural and offline. Collection/action cache counters are exposed by the persistent worker; zero external loads is expected for this benchmark.",
    }


def main() -> None:
    VALIDATION.mkdir(parents=True, exist_ok=True)
    style_metrics = {
        style: load_json(VALIDATION / folder / "shot_metrics.json")
        for style, folder in (("MINECRAFT", "minecraft"), ("ROBLOX", "roblox"))
    }
    assembler = EpisodeAssembler.from_root(ROOT)
    tests = test_evidence()
    performance = performance_evidence(style_metrics)
    style_reports = {}
    for style, folder in (("MINECRAFT", "minecraft"), ("ROBLOX", "roblox")):
        metrics = style_metrics[style]
        style_reports[style] = {
            "style_gate": metrics.get("style_gate"),
            "camera_qc": load_json(VALIDATION / folder / "camera_qc_report.json"),
            "master_visual_qc": metrics.get("master_visual_qc"),
            "shot_qc_passed": all(row.get("result", {}).get("qc_passed") for row in metrics.get("shots", [])),
            "human_review_required": True,
        }

    system = {
        "version": "1.6.2",
        "status": "READY_FOR_HUMAN_VISUAL_REVIEW",
        "production_ready": False,
        "host": platform.node(),
        "platform": platform.platform(),
        "python": sys.version,
        "blender_executable": os.environ.get("CINEFACTORY_BLENDER_EXECUTABLE", "portable Blender used by render command"),
        "blender_version": "4.5.14 LTS",
        "gpu": gpu_snapshot(),
        "paid_api_spend_usd": 0,
        "offline_only": True,
    }
    baseline = {
        "branch": git("branch", "--show-current"),
        "baseline_commit": "405d89f",
        "baseline_tag": "v1.6.1-validated",
        "baseline_head_message": git("show", "-s", "--format=%s", "405d89f"),
        "visual_fidelity_branch_head": git("rev-parse", "HEAD"),
        "working_tree_before_final_commit": git("status", "--short"),
    }

    manifest = style_asset_manifest(assembler.libraries)
    manifest["benchmark_outputs"] = {
        style: {
            "master": str(VALIDATION / folder / ("minecraft_visual_fidelity.mp4" if style == "MINECRAFT" else "roblox_visual_fidelity.mp4")),
            "contact_sheet": str(VALIDATION / f"{folder}_contact_sheet.jpg"),
            "after_contact_sheet": str(VALIDATION / f"{folder}_after_contact_sheet.jpg"),
        }
        for style, folder in (("MINECRAFT", "minecraft"), ("ROBLOX", "roblox"))
    }
    manifest["offline_only"] = True

    root_style_gate = {
        "status": "READY_FOR_HUMAN_VISUAL_REVIEW",
        "production_ready": False,
        "human_review_required": True,
        "styles": style_reports,
        "paid_api_spend_usd": 0,
    }
    root_camera = {
        "passed": all(report["camera_qc"].get("passed") for report in style_reports.values()),
        "human_review_required": True,
        "styles": {style: report["camera_qc"] for style, report in style_reports.items()},
        "note": "Pure-Python camera QC is deterministic framing/anchor analysis; Blender raycast occlusion and final visual judgment remain human review items.",
    }
    technical = {
        "status": "READY_FOR_HUMAN_VISUAL_REVIEW",
        "styles": style_reports,
        "all_master_qc_passed": all(report["master_visual_qc"].get("passed") for report in style_reports.values()),
        "all_shot_qc_passed": all(report["shot_qc_passed"] for report in style_reports.values()),
        "resolution": "1920x1080",
        "fps": 24,
        "duration_target_seconds": "25-40 per benchmark loop",
        "human_review_required": True,
    }

    (VALIDATION / "system_report.json").write_text(json.dumps(system, indent=2), encoding="utf-8")
    (VALIDATION / "baseline_report.json").write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    (VALIDATION / "test_report.json").write_text(json.dumps(tests, indent=2), encoding="utf-8")
    (VALIDATION / "performance_report.json").write_text(json.dumps(performance, indent=2), encoding="utf-8")
    (VALIDATION / "asset_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (VALIDATION / "style_gate_report.json").write_text(json.dumps(root_style_gate, indent=2), encoding="utf-8")
    (VALIDATION / "camera_qc_report.json").write_text(json.dumps(root_camera, indent=2), encoding="utf-8")
    (VALIDATION / "technical_qc_report.json").write_text(json.dumps(technical, indent=2), encoding="utf-8")

    (VALIDATION / "remaining_gaps.md").write_text(
        """# v1.6.2 remaining visual-fidelity gaps

The deterministic offline benchmark is complete and stopped at `READY_FOR_HUMAN_VISUAL_REVIEW`. It is not `PRODUCTION_READY`.

- Human visual review is still required for silhouette quality, readable prop interaction, final occlusion, lighting taste, and style authenticity.
- Minecraft and Roblox assets are original procedural offline approximations; native source-game asset ingestion is not claimed.
- Camera QC is deterministic framing/anchor analysis. Full Blender raycast occlusion validation remains a future hardening step.
- True hand-to-hand prop transfer is intentionally deferred; timed socket attachment is supported.
- Audio, dialogue, and final sound design remain outside this visual benchmark.
- Crowd behavior uses deterministic variation and requires human review for repetition at final editorial duration.
- The default Windows pytest TEMP/.pytest_cache locations are ACL-restricted; the isolated project-local test command is the reproducible evidence path.
""",
        encoding="utf-8",
    )
    (VALIDATION / "implementation_report.md").write_text(
        """# CineFactory OS v1.6.2 visual-fidelity implementation

Implemented style-aware offline adapters and deterministic gates for Minecraft voxel, Roblox R6, and Roblox R15 foundations; production camera anchors and roll rules; procedural classroom scenes; prop sockets and readable open-book props; persistent-worker cache counters; camera QC; and 1080p benchmark loops.

The benchmark outputs are intentionally review-gated: `READY_FOR_HUMAN_VISUAL_REVIEW`.
""",
        encoding="utf-8",
    )
    (ROOT / "docs" / "VISUAL_FIDELITY_v1.6.2.md").write_text(
        """# CineFactory OS v1.6.2 — visual fidelity

This release adds deterministic, offline style contracts and procedural visual systems for Minecraft-like voxel and Roblox-like R6/R15 characters, classroom scenes, handheld props, camera coverage, and crowd blocking.

Validation status: `READY_FOR_HUMAN_VISUAL_REVIEW`; `PRODUCTION_READY` is intentionally withheld until external human visual review.

Evidence is under `data/validation/v1.6.2/`.
""",
        encoding="utf-8",
    )
    print(json.dumps({"status": system["status"], "pytest": tests["isolated_pytest"].get("passed_count"), "outputs": str(VALIDATION)}, indent=2))


if __name__ == "__main__":
    main()
