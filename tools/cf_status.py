#!/usr/bin/env python3
"""One-screen factory status. Used as a Claude Code SessionStart hook so every session
starts from REAL runtime facts (not from docs), and runnable by hand:

    python tools/cf_status.py          # text
    python tools/cf_status.py --json   # machine-readable

Checks: Blender (portable .tools build or PATH), FFmpeg, ComfyUI on :8188, GPU/VRAM,
Blender MCP addon port, finished episodes + their QC verdicts, planned-but-unrendered episodes.
Never fails the session: any probe error is reported as a finding.
"""
from __future__ import annotations

import json
import shutil
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLENDER_CANDIDATES = [
    ROOT / ".tools" / "blender-4.5.14-windows-x64" / "blender.exe",
    Path(r"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"),
]


def _run(argv: list[str], timeout: float = 4.0) -> str | None:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout, encoding="utf-8", errors="replace")
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:  # noqa: BLE001
        return None


def blender() -> dict:
    for cand in BLENDER_CANDIDATES:
        if cand.is_file():
            return {"ok": True, "path": str(cand)}
    found = shutil.which("blender")
    return {"ok": bool(found), "path": found}


def ffmpeg() -> dict:
    out = _run(["ffmpeg", "-hide_banner", "-version"])
    return {"ok": out is not None, "version": out.splitlines()[0][:60] if out else None}


def comfyui() -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=1.5) as r:
            data = json.loads(r.read().decode("utf-8"))
        dev = (data.get("devices") or [{}])[0]
        return {"ok": True, "device": dev.get("name"), "vram_free_gb": round((dev.get("vram_free") or 0) / 2**30, 1)}
    except Exception:  # noqa: BLE001
        return {"ok": False}


def gpu() -> dict:
    out = _run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"])
    if not out:
        return {"ok": False}
    name, used, total, util = [x.strip() for x in out.splitlines()[0].split(",")]
    return {"ok": True, "name": name, "vram_used_mb": int(used), "vram_total_mb": int(total), "util_pct": int(util)}


def port_open(port: int) -> bool:
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def episodes() -> dict:
    base = ROOT / "data" / "animal_long_slide"
    finished = []
    for mp4 in sorted((base / "episodes").glob("*/episode.mp4")):
        qc = mp4.with_name("episode.qc.json")
        verdict = json.loads(qc.read_text(encoding="utf-8")).get("verdict") if qc.is_file() else "NO_QC"
        finished.append({"episode": mp4.parent.name, "mb": round(mp4.stat().st_size / 1e6, 1), "qc": verdict})
    series = []
    for plan in sorted((base / "series").glob("*/episodes/*/varied_episode.json")):
        ep = plan.parent
        check = ep / "render_check.json"
        renderable = json.loads(check.read_text(encoding="utf-8")).get("executable") if check.is_file() else None
        stage = "planned"
        if (ep / "greenlight.json").is_file():
            stage = "greenlit"
        prod = ep / "production.json"
        if prod.is_file():
            stages = json.loads(prod.read_text(encoding="utf-8")).get("stages", {})
            done = [k for k, v in stages.items() if v.get("status") == "done"]
            stuck = [f"{k}:{v.get('status')}" for k, v in stages.items() if v.get("status") != "done"]
            stage = stuck[0] if stuck else (done[-1] if done else stage)
        series.append({"episode": f"{ep.parent.parent.name}/{ep.name}", "stage": stage,
                       "renderable": renderable})
    return {"finished": finished, "series": series}


def capability() -> dict:
    """What the factory can render today (shared with the planner and renderer)."""
    try:
        sys.path.insert(0, str(ROOT))
        from cinefactory.animal_long_slide.capability import LongSlideCapability
        cap = LongSlideCapability.detect(ROOT)
        return {"ok": True, "renderable_animals": sorted(cap.renderable), "bible": cap.default_bible_path().name,
                "render_s_per_video_s": cap.render_seconds_per_video_second}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)[:200]}


def main() -> int:
    status = {"blender": blender(), "ffmpeg": ffmpeg(), "comfyui": comfyui(), "gpu": gpu(),
              "blender_mcp_port_9876": port_open(9876), "long_slide": episodes(), "capability": capability()}
    if "--json" in sys.argv:
        print(json.dumps(status, indent=2))
        return 0
    b, f, c, g = status["blender"], status["ffmpeg"], status["comfyui"], status["gpu"]
    ls = status["long_slide"]
    lines = [
        "=== CINEFACTORY LIVE STATUS (measured now, trust this over docs) ===",
        f"Blender : {'OK ' + str(b['path']) if b['ok'] else 'MISSING'}",
        f"FFmpeg  : {f['version'] if f['ok'] else 'MISSING'}",
        f"GPU     : {g['name'] + ' ' + str(g['vram_used_mb']) + '/' + str(g['vram_total_mb']) + ' MB used, ' + str(g['util_pct']) + '% util' if g['ok'] else 'nvidia-smi unavailable'}",
        f"ComfyUI : {'UP ' + str(c.get('device')) + ' free ' + str(c.get('vram_free_gb')) + ' GB' if c['ok'] else 'DOWN (scripts/start_comfyui.ps1)'}",
        f"BlenderMCP addon port 9876: {'open' if status['blender_mcp_port_9876'] else 'closed'}",
        f"Long Slide finished episodes: {len(ls['finished'])} "
        + ", ".join(f"{e['episode']}[{e['qc']}]" for e in ls["finished"][-5:]),
        "Series episodes: " + (", ".join(
            f"{e['episode']}[{e['stage']}{'' if e['renderable'] is not False else ', NOT RENDERABLE'}]"
            for e in ls["series"][-8:]) or "none"),
    ]
    cap = status["capability"]
    if cap.get("ok"):
        speed = cap.get("render_s_per_video_s")
        lines.append(f"Can render today: {len(cap['renderable_animals'])} animals ({', '.join(cap['renderable_animals'][:10])}"
                     f"{'...' if len(cap['renderable_animals']) > 10 else ''}) · bible {cap['bible']} · "
                     f"render speed {str(speed) + ' s per video s (measured)' if speed else 'not measured yet'}")
    else:
        lines.append(f"Capability check failed: {cap.get('error')}")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"cf_status error: {exc}")
        sys.exit(0)
