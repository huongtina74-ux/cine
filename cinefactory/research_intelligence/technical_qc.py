"""Deterministic quality gates for observed production videos."""
from __future__ import annotations
import math
from pathlib import Path
from .core import _write_json

def evaluate_video_quality(observation: dict, destination: str | Path, *,
                           min_width: int = 1920, min_height: int = 1080,
                           expected_duration_seconds: float | None = None,
                           duration_tolerance: float = 0.05,
                           require_audio: bool = True) -> dict:
    if observation.get("schema") != "cine.research.observation.v1":
        raise ValueError("Real observation evidence required")
    if min_width < 1 or min_height < 1 or not 0 <= duration_tolerance < 1:
        raise ValueError("Invalid QC threshold")
    video = next((s for s in observation.get("streams", []) if s.get("type") == "video"), None)
    if video is None:
        raise ValueError("No probed video stream")
    duration = observation.get("duration_seconds")
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ValueError("Invalid duration")
    checks = [
        {"name": "resolution", "passed": isinstance(video.get("width"), int) and isinstance(video.get("height"), int) and video["width"] >= min_width and video["height"] >= min_height,
         "measured": [video.get("width"), video.get("height")], "threshold": [min_width, min_height]},
        {"name": "frames_extracted", "passed": bool(observation.get("frames")), "measured": len(observation.get("frames", [])), "threshold": 1},
        {"name": "audio_present", "passed": bool(observation.get("audio", {}).get("present")) or not require_audio, "measured": bool(observation.get("audio", {}).get("present")), "threshold": require_audio}
    ]
    if expected_duration_seconds is not None:
        if expected_duration_seconds <= 0:
            raise ValueError("Expected duration must be positive")
        delta = abs(duration - expected_duration_seconds) / expected_duration_seconds
        checks.append({"name": "duration", "passed": delta <= duration_tolerance, "measured": duration, "expected": expected_duration_seconds, "relative_error": delta})
    result = {"schema": "cine.research.production_qc.v1", "source": observation.get("source"), "passed": all(c["passed"] for c in checks), "checks": checks,
              "limitations": ["Sampling cannot prove no black frames between samples", "No narrative, perceptual or motion quality score", "Audio presence does not prove sound quality"]}
    _write_json(Path(destination), result)
    return result
