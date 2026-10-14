"""Evidence-grounded local video observation and production learning.

No unsupported claims: sampled frames are evidence, not semantic interpretations.
Claude task files are written for a human/agent runner; no automatic external execution.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEPARTMENTS = ("research", "story", "visual", "animation", "audio", "editorial", "packaging", "quality", "growth")
MAX_VIDEO_BYTES = 50 * 1024**3


def _run(argv: list[str], timeout: int = 90) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=True)


def _write_json(path: Path, obj: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    temp.replace(path)
    return path


def observe_video(source: str | Path, output: str | Path, *, interval_seconds: int = 15, max_frames: int = 100, sample_times_seconds: list[float] | None = None) -> dict[str, Any]:
    """Probe a local authorized video, extract real frames and audio measurements."""
    src = Path(source).resolve(strict=True)
    dst = Path(output).resolve()
    if not src.is_file() or src.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("Source must be a local video file under 50 GiB")
    if interval_seconds < 1 or not 1 <= max_frames <= 500:
        raise ValueError("Invalid sampling controls")
    probe = json.loads(_run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(src)]).stdout)
    streams = probe.get("streams", [])
    if not any(s.get("codec_type") == "video" for s in streams):
        raise ValueError("No video stream detected")
    duration = float(probe.get("format", {}).get("duration", 0))
    if duration <= 0:
        raise ValueError("Unknown or invalid duration")
    shots = min(max_frames, max(1, int((duration - 0.001) // interval_seconds) + 1))
    if sample_times_seconds is None:
        sample_times = [round(i * interval_seconds, 3) for i in range(shots)]
    else:
        if not sample_times_seconds or len(sample_times_seconds) > max_frames:
            raise ValueError('Sample plan must contain 1..max_frames timestamps')
        if any(not isinstance(t, (int, float)) or isinstance(t, bool) or not 0 <= t < duration for t in sample_times_seconds):
            raise ValueError('Sample timestamp outside video')
        sample_times = sorted(set(round(float(t), 3) for t in sample_times_seconds))
    frames_dir = dst / "frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for i, second in enumerate(sample_times):
        target = frames_dir / f"frame_{i:04d}.jpg"
        _run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-y", "-ss", str(second), "-i", str(src), "-frames:v", "1", "-vf", "scale=640:-2", str(target)])
        if not target.is_file() or target.stat().st_size == 0:
            raise RuntimeError(f"Failed to extract frame at {second}s")
        frames.append({"second": second, "path": str(target), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
    audio = {"present": any(s.get("codec_type") == "audio" for s in streams), "volume_statistics": None}
    if audio["present"]:
        window_seconds = min(120.0, duration)
        result = _run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(src), "-t", str(window_seconds), "-vn", "-af", "volumedetect", "-f", "null", "-"], timeout=180)
        matches = dict(re.findall(r"(mean_volume|max_volume):\s*([^\n\r]+)", result.stderr))
        audio["volume_statistics"] = matches
        audio["measurement_window_seconds"] = window_seconds
    evidence = {
        "schema": "cine.research.observation.v1",
        "source": str(src),
        "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest() if src.stat().st_size < 512 * 1024**2 else None,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "duration_seconds": duration,
        "streams": [{"type": s.get("codec_type"), "codec": s.get("codec_name"), "width": s.get("width"), "height": s.get("height")} for s in streams],
        "sampling": {"interval_seconds": interval_seconds, "frame_count": len(frames), "coverage": "sampled_not_full_semantic_review"},
        "frames": frames,
        "audio": audio,
        "semantic_analysis": "NOT_PERFORMED; requires a vision-capable reviewer or model inspecting frames/video",
    }
    _write_json(dst / "observation.json", evidence)
    return evidence


def create_department_tasks(observation: dict[str, Any], out: str | Path, *, niche: str, reference_id: str, approved: bool = False, departments: list[str] | None = None) -> dict[str, Any]:
    """Produce per-department Claude Code instructions with traceable evidence and safeguards."""
    if observation.get("schema") != "cine.research.observation.v1":
        raise ValueError("Observation evidence required")
    if not niche.strip() or not reference_id.strip():
        raise ValueError("Niche and reference id required")
    output = Path(out)
    _write_json(output / 'observation.json', observation)
    prompts = {
        "research": "Identify hypotheses and distinguish observations from inferences; benchmark against independent channels.",
        "story": "Study hook, payoff, escalation, narrative logic; propose original story beats, not a copied script.",
        "visual": "Inspect provided frames for framing, palette, continuity and composition; cite frame timestamps.",
        "animation": "Identify motion questions requiring full playback; create original reusable animation specifications.",
        "audio": "Analyze measured audio stats; inspect audio directly before attributing sound design or speech.",
        "editorial": "Propose pace, transitions and retention tests; do not claim inaccessible competitor retention.",
        "packaging": "Propose original title and thumbnail hypotheses and test designs.",
        "quality": "Check rights, originality, continuity, artifacts and evidence completeness.",
        "growth": "Define test hypotheses and compare owned-channel analytics where authorized.",
    }
    chosen_departments = DEPARTMENTS if departments is None else departments
    if not chosen_departments or len(set(chosen_departments)) != len(chosen_departments) or any(d not in DEPARTMENTS for d in chosen_departments):
        raise ValueError('Invalid department selection')
    tasks = []
    for dept in chosen_departments:
        task = {
            "schema": "cine.research.task.v1", "task_id": f"{reference_id}:{dept}",
            "department": dept, "niche": niche, "reference_id": reference_id,
            "approval_status": "approved" if approved else "pending_approval",
            "evidence_path": str((output / "observation.json").resolve()),
            "instructions": prompts[dept],
            "constraints": ["Quote exact video timestamps or evidence paths", "Separate VERIFIED, HYPOTHESIS and UNKNOWN", "Create original work; never replicate protected material", "No production or publishing without explicit approval"],
            "deliverables": ["findings", "evidence", "production_hypotheses", "confidence", "risks", "proposed_tests"],
        }
        tasks.append(task)
        _write_json(output / "tasks" / f"{dept}.json", task)
    result = {"schema": "cine.research.dispatch.v1", "niche": niche, "reference_id": reference_id, "tasks": tasks}
    _write_json(output / "dispatch.json", result)
    return result


def assess_production(reference: dict[str, Any], produced: dict[str, Any], analytics: dict[str, Any] | None = None) -> dict[str, Any]:
    """Link observed reference/owned video and metrics, with no spurious causal claims."""
    if reference.get("schema") != "cine.research.observation.v1" or produced.get("schema") != "cine.research.observation.v1":
        raise ValueError("Both videos require actual observations")
    result = {
        "schema": "cine.research.feedback.v1",
        "reference_source": reference["source"],
        "produced_source": produced["source"],
        "reference_duration": reference["duration_seconds"],
        "produced_duration": produced["duration_seconds"],
        "duration_ratio": round(produced["duration_seconds"] / reference["duration_seconds"], 4),
        "reference_frames": len(reference["frames"]),
        "produced_frames": len(produced["frames"]),
        "comparability": "Structural measurements only; no automatic semantic quality verdict",
        "owned_metrics": {},
        "hypotheses": [],
    }
    if analytics:
        for key in ("impressions", "views", "ctr", "average_view_duration_seconds", "watch_time_hours", "rpm_usd"):
            if key in analytics:
                val = analytics[key]
                if not isinstance(val, (float, int)) or isinstance(val, bool) or val < 0:
                    raise ValueError(f"Invalid analytics metric: {key}")
                result["owned_metrics"][key] = val
        if "ctr" in result["owned_metrics"] and result["owned_metrics"]["ctr"] > 1:
            raise ValueError("CTR must be expressed as fraction 0..1")
    return result
