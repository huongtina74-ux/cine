#!/usr/bin/env python3
"""CineFactory automatic technical QC for a finished video (zero-API, FFmpeg only).

Usage:
    python tools/cf_qc.py data/animal_long_slide/episodes/EP_DEMO_01/episode.mp4
    python tools/cf_qc.py VIDEO --profile kids_long --min-seconds 180 --max-seconds 600

Writes next to the video (or --out-dir):
    <name>.qc.json        machine-readable report + PASS/FAIL verdict
    <name>.contact.jpg    contact sheet (4x4 frames) for visual review by Claude / a human
    <name>.frames/        individual frames used in the sheet

Exit codes: 0 = PASS, 1 = FAIL (blocking findings), 2 = tool error.

Technical QC never replaces creative QC: the qc-reviewer agent must still LOOK at
the contact sheet (upside-down shots, clipping, off-model characters, empty frames).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROFILES = {
    # YouTube normalises playback to about -14 LUFS; we accept a small window.
    "youtube_long": {"min_height": 1080, "warn_height": 720, "lufs": (-16.0, -12.0), "true_peak_max": -1.0,
                     "max_black": 1.0, "max_freeze": 3.0, "max_silence": 3.0, "min_fps": 24},
    "kids_long":    {"min_height": 1080, "warn_height": 720, "lufs": (-16.0, -12.0), "true_peak_max": -1.0,
                     "max_black": 1.0, "max_freeze": 2.5, "max_silence": 2.5, "min_fps": 24},
    "shorts":       {"min_height": 1920, "warn_height": 1280, "lufs": (-16.0, -12.0), "true_peak_max": -1.0,
                     "max_black": 0.5, "max_freeze": 1.5, "max_silence": 1.5, "min_fps": 24, "vertical": True,
                     "max_seconds": 180},
}


def run(cmd: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          encoding="utf-8", errors="replace")


def probe(video: Path) -> dict:
    proc = run(["ffprobe", "-v", "error", "-show_entries",
                "format=duration,bit_rate:stream=codec_type,codec_name,width,height,r_frame_rate,channels,sample_rate",
                "-of", "json", str(video)])
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {proc.stderr[-800:]}")
    data = json.loads(proc.stdout)
    out = {"duration": float(data["format"].get("duration", 0.0)), "bit_rate": int(data["format"].get("bit_rate", 0) or 0)}
    for s in data.get("streams", []):
        if s.get("codec_type") == "video" and "video" not in out:
            num, den = (s.get("r_frame_rate") or "0/1").split("/")
            out["video"] = {"codec": s.get("codec_name"), "width": s.get("width"), "height": s.get("height"),
                            "fps": round(float(num) / float(den or 1), 3)}
        elif s.get("codec_type") == "audio" and "audio" not in out:
            out["audio"] = {"codec": s.get("codec_name"), "channels": s.get("channels"),
                            "sample_rate": int(s.get("sample_rate") or 0)}
    return out


def _spans(text: str, start_key: str, end_key: str, dur_key: str) -> list[dict]:
    spans, start = [], None
    for line in text.splitlines():
        m = re.search(rf"{start_key}:\s*([-\d.]+)", line)
        if m:
            start = float(m.group(1))
        m_end = re.search(rf"{end_key}:\s*([-\d.]+)", line)
        m_dur = re.search(rf"{dur_key}:\s*([-\d.]+)", line)
        if m_end and m_dur:
            spans.append({"start": start, "end": float(m_end.group(1)), "duration": float(m_dur.group(1))})
            start = None
    return spans


def analyse(video: Path, has_audio: bool) -> dict:
    """One video decode pass + one audio pass."""
    vf = "blackdetect=d=0.3:pic_th=0.98,freezedetect=n=0.003:d=1.0,select='gt(scene,0.30)',metadata=print:file=-"
    vproc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video), "-vf", vf, "-an", "-f", "null", "-"])
    vtext = vproc.stderr + "\n" + vproc.stdout
    black = []
    for line in vtext.splitlines():
        m = re.search(r"black_start:([\d.]+)\s+black_end:([\d.]+)\s+black_duration:([\d.]+)", line)
        if m:
            black.append({"start": float(m.group(1)), "end": float(m.group(2)), "duration": float(m.group(3))})
    freeze = _spans(vtext, "lavfi.freezedetect.freeze_start", "lavfi.freezedetect.freeze_end",
                    "lavfi.freezedetect.freeze_duration")
    cuts = len(re.findall(r"lavfi\.scene_score=", vproc.stdout))
    result = {"black": black, "freeze": freeze, "scene_cuts": cuts}
    if has_audio:
        aproc = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video), "-vn",
                     "-af", "ebur128=peak=true,silencedetect=noise=-45dB:d=1.0", "-f", "null", "-"])
        atext = aproc.stderr
        summary = atext[atext.rfind("Summary:"):] if "Summary:" in atext else atext
        def grab(pattern: str):
            m = re.search(pattern, summary)
            return float(m.group(1)) if m else None
        result["loudness"] = {"integrated_lufs": grab(r"I:\s*([-\d.]+) LUFS"),
                              "lra": grab(r"LRA:\s*([-\d.]+) LU"),
                              "true_peak_dbtp": grab(r"Peak:\s*([-\d.]+) dBFS")}
        result["silence"] = _spans(atext, "silence_start", "silence_end", "silence_duration")
    return result


def contact_sheet(video: Path, duration: float, out_dir: Path, stem: str, n: int = 16) -> dict:
    frames_dir = out_dir / f"{stem}.frames"
    frames_dir.mkdir(parents=True, exist_ok=True)
    for old in frames_dir.glob("*.jpg"):
        old.unlink()
    times = [duration * (i + 0.5) / n for i in range(n)]
    for i, t in enumerate(times):
        run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-ss", f"{t:.3f}", "-i", str(video),
             "-frames:v", "1", "-vf", "scale=640:-2", str(frames_dir / f"f{i:02d}_{t:07.2f}s.jpg")])
    sheet = out_dir / f"{stem}.contact.jpg"
    cols = 4
    proc = run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-pattern_type", "glob", "-i", str(frames_dir / "f*.jpg"),
                "-vf", f"scale=480:-2,tile={cols}x{(n + cols - 1) // cols}:padding=4:color=white",
                "-frames:v", "1", str(sheet)])
    if proc.returncode != 0:  # Windows builds of ffmpeg often lack glob support
        lst = frames_dir / "list.txt"
        lst.write_text("".join(f"file '{p.name}'\n" for p in sorted(frames_dir.glob('f*.jpg'))), encoding="utf-8")
        run(["ffmpeg", "-v", "error", "-nostdin", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-vf", f"scale=480:-2,tile={cols}x{(n + cols - 1) // cols}:padding=4:color=white",
             "-frames:v", "1", str(sheet)])
    return {"sheet": str(sheet), "frames_dir": str(frames_dir), "timestamps": [round(t, 2) for t in times]}


def verdict(info: dict, an: dict, profile: dict, args) -> tuple[list[str], list[str]]:
    fails, warns = [], []
    dur = info["duration"]
    v = info.get("video") or {}
    if not v:
        fails.append("NO_VIDEO_STREAM")
    else:
        short_side = min(v["width"], v["height"]) if not profile.get("vertical") else v["height"]
        h = v["height"] if not profile.get("vertical") else short_side
        if profile.get("vertical") and v["width"] >= v["height"]:
            fails.append(f"NOT_VERTICAL:{v['width']}x{v['height']}")
        if h < profile["warn_height"]:
            fails.append(f"RESOLUTION_TOO_LOW:{v['width']}x{v['height']}")
        elif h < profile["min_height"]:
            warns.append(f"RESOLUTION_BELOW_TARGET:{v['width']}x{v['height']} (target {profile['min_height']}p)")
        if v["fps"] < profile["min_fps"]:
            fails.append(f"FPS_TOO_LOW:{v['fps']}")
    if "audio" not in info:
        fails.append("NO_AUDIO_STREAM")
    max_s = args.max_seconds or profile.get("max_seconds")
    if args.min_seconds and dur < args.min_seconds:
        fails.append(f"TOO_SHORT:{dur:.1f}s<{args.min_seconds}s")
    if max_s and dur > max_s:
        fails.append(f"TOO_LONG:{dur:.1f}s>{max_s}s")
    for b in an["black"]:
        edge = b["start"] < 0.5 or b["end"] > dur - 0.5
        if b["duration"] > profile["max_black"] and not edge:
            fails.append(f"BLACK_SEGMENT:{b['start']:.1f}-{b['end']:.1f}s")
    for f in an["freeze"]:
        if f["duration"] > profile["max_freeze"]:
            fails.append(f"FROZEN_PICTURE:{f['start']:.1f}-{f['end']:.1f}s")
        else:
            warns.append(f"SHORT_FREEZE:{f['start']:.1f}s ({f['duration']:.1f}s)")
    if "loudness" in an:
        lo, hi = profile["lufs"]
        i = an["loudness"]["integrated_lufs"]
        tp = an["loudness"]["true_peak_dbtp"]
        if i is None:
            warns.append("LOUDNESS_UNMEASURED")
        elif not lo <= i <= hi:
            fails.append(f"LOUDNESS_OUT_OF_RANGE:{i} LUFS (want {lo}..{hi})")
        if tp is not None and tp > profile["true_peak_max"]:
            warns.append(f"TRUE_PEAK_HIGH:{tp} dBTP (want <= {profile['true_peak_max']})")
        for s in an.get("silence", []):
            if s["duration"] > profile["max_silence"] and s["start"] is not None and s["start"] > 0.5:
                fails.append(f"DEAD_AIR:{s['start']:.1f}-{s['end']:.1f}s")
    if dur > 0:
        avg_shot = dur / (an["scene_cuts"] + 1)
        an["avg_shot_seconds"] = round(avg_shot, 2)
        if avg_shot > 12:
            warns.append(f"SLOW_PACING:avg shot {avg_shot:.1f}s")
    return fails, warns


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video")
    ap.add_argument("--profile", choices=sorted(PROFILES), default="youtube_long")
    ap.add_argument("--min-seconds", type=float, default=0)
    ap.add_argument("--max-seconds", type=float, default=0)
    ap.add_argument("--out-dir", default="")
    ap.add_argument("--frames", type=int, default=16)
    args = ap.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            print(f"QC_ERROR::{tool} not found on PATH")
            return 2
    video = Path(args.video).resolve()
    if not video.is_file():
        print(f"QC_ERROR::missing {video}")
        return 2
    out_dir = Path(args.out_dir).resolve() if args.out_dir else video.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        info = probe(video)
        an = analyse(video, "audio" in info)
        sheet = contact_sheet(video, info["duration"], out_dir, video.stem, args.frames)
    except Exception as exc:  # noqa: BLE001
        print(f"QC_ERROR::{exc}")
        return 2
    fails, warns = verdict(info, an, PROFILES[args.profile], args)
    report = {"video": str(video), "profile": args.profile, "verdict": "FAIL" if fails else "PASS",
              "blocking": fails, "warnings": warns, "probe": info, "analysis": an, "contact_sheet": sheet,
              "next_step": "qc-reviewer must open contact_sheet and check creative issues before approval"}
    report_path = out_dir / f"{video.stem}.qc.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    v = info.get("video", {})
    lo = an.get("loudness", {})
    print(f"QC_{report['verdict']}::{video.name} {info['duration']:.1f}s {v.get('width')}x{v.get('height')}@{v.get('fps')} "
          f"LUFS={lo.get('integrated_lufs')} TP={lo.get('true_peak_dbtp')} cuts={an['scene_cuts']}")
    for f in fails:
        print("  FAIL  " + f)
    for w in warns:
        print("  WARN  " + w)
    print("REPORT::" + str(report_path))
    print("CONTACT_SHEET::" + sheet["sheet"])
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
