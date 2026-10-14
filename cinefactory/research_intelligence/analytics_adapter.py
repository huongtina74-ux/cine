"""No-key YouTube Studio CSV adapter with strict provenance, and retention landmarks.

CSV must have been exported by a channel owner with permission. This is not
continuous automatic synchronization; it is deterministic ingestion when a file arrives.
"""
from __future__ import annotations
import csv
import hashlib
import math
import re
from datetime import date
from pathlib import Path
from .core import _write_json

def _integer(text: str) -> int:
    s = text.strip().replace(",", "").replace(" ", "")
    if not re.fullmatch(r"\d+", s):
        raise ValueError(f"Not an integer: {text!r}")
    return int(s)

def _decimal(text: str) -> float:
    try:
        val = float(text.strip().replace(",", ""))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Not a decimal: {text!r}") from exc
    if not math.isfinite(val) or val < 0:
        raise ValueError("Numeric field must be finite and nonnegative")
    return val

def _duration(text: str) -> float:
    parts = text.strip().split(":")
    if len(parts) in (2, 3):
        if any(not re.fullmatch(r"\d+", p) for p in parts):
            raise ValueError("Invalid duration")
        values = [int(p) for p in parts]
        if any(p >= 60 for p in values[1:]):
            raise ValueError("Invalid mm:ss value")
        return float(sum(n * (60 ** i) for i, n in enumerate(reversed(values))))
    return _decimal(text)

def import_studio_csv(path: str | Path, output: str | Path, *, period_start: str, period_end: str, channel_id: str) -> dict:
    start, end = date.fromisoformat(period_start), date.fromisoformat(period_end)
    if start > end or not isinstance(channel_id, str) or not channel_id.strip():
        raise ValueError("Invalid report period/channel")
    file = Path(path).resolve(strict=True)
    with file.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("Empty CSV")
    aliases = {
        "video_id": ("Video ID", "Video id", "video_id", "Content"),
        "views": ("Views",),
        "impressions": ("Impressions",),
        "ctr": ("Impressions click-through rate (%)", "Impressions CTR (%)"),
        "average_view_duration_seconds": ("Average view duration",),
        "watch_time_hours": ("Watch time (hours)",),
    }
    if not any(k in rows[0] for k in aliases["video_id"]):
        raise ValueError("Video ID column missing; export with video dimension")
    results = []
    seen = set()
    for row in rows:
        if not any(str(v).strip() for v in row.values() if v is not None):
            continue
        raw_id = next((row.get(k) for k in aliases["video_id"] if row.get(k)), "")
        ident = str(raw_id).strip()
        if ident.lower() == "total":
            continue
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", ident):
            raise ValueError(f"Invalid video id: {ident!r}")
        if ident in seen:
            raise ValueError("Duplicate video row; report dimensions may be aggregated incorrectly")
        seen.add(ident)
        metrics = {}
        for key, headings in aliases.items():
            if key == "video_id":
                continue
            cell = next((row[h] for h in headings if h in row and row[h] not in ("", None)), None)
            if cell is None:
                continue
            if key in ("views", "impressions"):
                metrics[key] = _integer(cell)
            elif key == "ctr":
                metrics[key] = _decimal(cell.replace("%", "")) / 100.0
                if metrics[key] > 1:
                    raise ValueError("CTR percentage exceeds 100")
            elif key == "average_view_duration_seconds":
                metrics[key] = _duration(cell)
            else:
                metrics[key] = _decimal(cell)
        results.append({"video_id": ident, "metrics": metrics})
    if not results:
        raise ValueError("No video rows found")
    report = {"schema": "cine.research.studio_csv.v1", "source_file": str(file), "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
              "channel_id": channel_id, "period_start": period_start, "period_end": period_end,
              "rows": results, "limitations": ["Owner-authorized export required", "No transcript or retention curve inferred", "Metrics are for one specified reporting period"]}
    _write_json(Path(output), report)
    return report

def retention_drop_candidates(points: list[dict], *, min_drop_percentage_points: float = 8) -> list[dict]:
    """Use only measured retention samples, not interpolated or assumed competitor data."""
    if not isinstance(points, list) or len(points) < 2 or min_drop_percentage_points <= 0:
        raise ValueError("Need at least two measured points and a positive threshold")
    ordered = sorted(points, key=lambda p: p["second"])
    last = -1.0
    for point in ordered:
        if not isinstance(point["second"], (int, float)) or point["second"] <= last:
            raise ValueError("Duplicate/invalid timestamp")
        value = point["retention_pct"]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 1000:
            raise ValueError("Retention percentage out of range")
        last = point["second"]
    findings = []
    for old, new in zip(ordered, ordered[1:]):
        difference = old["retention_pct"] - new["retention_pct"]
        if difference >= min_drop_percentage_points:
            findings.append({"from_seconds": old["second"], "to_seconds": new["second"],
                             "drop_percentage_points": round(difference, 3), "status": "MEASURED",
                             "hypothesis": "Inspect corresponding video segment; retention change alone does not establish cause"})
    return findings


def select_owned_video(report: dict, video_id: str) -> dict:
    if report.get("schema") != "cine.research.studio_csv.v1":
        raise ValueError("Expected owner-authorized Studio report")
    matches = [item for item in report.get("rows", []) if item.get("video_id") == video_id]
    if len(matches) != 1:
        raise ValueError("Owned video ID must match one row exactly")
    return {"metrics": matches[0]["metrics"], "video_id": video_id,
            "source": {"sha256": report["sha256"], "channel_id": report["channel_id"],
                       "period_start": report["period_start"], "period_end": report["period_end"]}}

def map_retention_to_frames(observation: dict, points: list[dict], *, max_distance_seconds: float = 10, min_drop_percentage_points: float = 8) -> dict:
    """Link measured retention drops to nearby sampled frame evidence; no causality claims."""
    if observation.get("schema") != "cine.research.observation.v1" or max_distance_seconds < 0:
        raise ValueError("Observed video and nonnegative distance required")
    drops = retention_drop_candidates(points, min_drop_percentage_points=min_drop_percentage_points)
    frames = observation.get("frames", [])
    annotated = []
    for drop in drops:
        at = drop["to_seconds"]
        nearest = min(frames, key=lambda x: abs(float(x["second"]) - at), default=None)
        evidence = None
        if nearest is not None and abs(float(nearest["second"]) - at) <= max_distance_seconds:
            evidence = {"path": nearest["path"], "second": nearest["second"], "distance_seconds": round(abs(float(nearest["second"]) - at), 3)}
        annotated.append({**drop, "nearest_sampled_frame": evidence})
    return {"schema": "cine.research.retention_video_link.v1", "owned_video_source": observation.get("source"),
            "drops": annotated, "coverage": "nearest_sampled_frame_only",
            "interpretation": "Measured drop requires investigation; a nearby frame does not identify the cause"}
