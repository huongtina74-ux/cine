"""Small, bounded, content-aware frame sampling; no heavy model needed to triage."""
from __future__ import annotations
import json
import math
from pathlib import Path

from .core import _run, observe_video, _write_json

def choose_timestamps(duration: float, *, max_frames: int = 24, changes: list[float] | None = None) -> list[float]:
    if not math.isfinite(duration) or duration <= 0 or not 1 <= max_frames <= 100:
        raise ValueError("Invalid duration/frame budget")
    end = max(0, duration - min(0.3, duration / 3))
    # The opening is sampled densely to study packaging/hook; broad anchors cover the rest.
    opening = [0, 1, 3, 6, 10, 20, 30, 45, 60, 90, 120]
    opening = [x for x in opening if x <= end]
    opening_quota = max(1, max_frames // 4)
    change_quota = max(0, max_frames // 4) if max_frames >= 4 else 0
    core_times = opening[:opening_quota]
    valid_changes = [x for x in (changes or []) if isinstance(x, (int, float)) and math.isfinite(x) and 0 <= x <= end]
    core_times += valid_changes[:change_quota]
    remaining = max(1, max_frames - len(core_times))
    timeline = [end * i / max(1, remaining - 1) for i in range(remaining)]
    candidates = core_times + timeline
    # Backfill uncovered gaps when opening/change samples overlap the uniform grid.
    candidates += [end * i / max(1, max_frames * 2 - 1) for i in range(max_frames * 2)]
    chosen = []
    for x in candidates:
        point = round(float(x), 3)
        if all(abs(point - old) >= 0.45 for old in chosen):
            chosen.append(point)
        if len(chosen) >= max_frames:
            break
    return sorted(chosen)

def detect_visual_changes(path: str | Path, *, max_seconds: int = 180, step_seconds: int = 2, max_changes: int = 10) -> tuple[list[float], str]:
    """Find candidate visual changes in a bounded opening window.

    Approximate pixel differences are NOT proof of shot boundaries or story events.
    """
    try:
        import cv2
    except ImportError:
        return [], "opencv_unavailable"
    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        return [], "video_decode_unavailable"
    try:
        duration_ms = capture.get(cv2.CAP_PROP_FRAME_COUNT) / max(0.001, capture.get(cv2.CAP_PROP_FPS)) * 1000
        if not math.isfinite(duration_ms) or duration_ms <= 0:
            return [], "duration_unknown"
        previous = None
        scores = []
        for second in range(0, min(max_seconds, int(duration_ms / 1000)), step_seconds):
            capture.set(cv2.CAP_PROP_POS_MSEC, second * 1000)
            ok, frame = capture.read()
            if not ok:
                continue
            resized = cv2.resize(frame, (160, 90))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            if previous is not None:
                diff = float(cv2.absdiff(gray, previous).mean()) / 255
                if diff >= 0.16:
                    scores.append((diff, second))
            previous = gray
        # Dedupe near-adjacent changes, prefer strongest differences.
        picked = []
        for _, second in sorted(scores, reverse=True):
            if all(abs(second - old) >= 4 for old in picked):
                picked.append(second)
            if len(picked) == max_changes:
                break
        return sorted(picked), "opencv_heuristic_first_180s"
    finally:
        capture.release()

def observe_smart(source: str | Path, output: str | Path, *, max_frames: int = 24, detect_changes: bool = True) -> dict:
    """Bounded local observation, no network, vision API or model call."""
    probe = json.loads(_run(["ffprobe", "-v", "error", "-show_format", "-of", "json", str(Path(source).resolve(strict=True))]).stdout)
    duration = float(probe.get("format", {}).get("duration", 0))
    changes, detector = detect_visual_changes(source) if detect_changes else ([], "disabled")
    times = choose_timestamps(duration, max_frames=max_frames, changes=changes)
    result = observe_video(source, output, max_frames=max_frames, sample_times_seconds=times)
    result["sampling"].update({"strategy": "opening_plus_changes_plus_coverage", "heuristic": detector, "candidate_visual_changes": changes, "budget_max_frames": max_frames})
    _write_json(Path(output) / "observation.json", result)
    return result
