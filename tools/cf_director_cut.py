"""Director Cut: one machine-readable file that tells the editor exactly how to cut an episode.

A Director Cut (DC) lists every shot in order with its source clip, in/out seconds, the
cut into it, the section (hook / act / outro), the emotion and purpose, the voice-over line,
sound effects and on-screen text. `tools/cf_auto_edit.py` turns it into a finished video.

    python tools/cf_director_cut.py template --shots 12 --out dc.json --episode EP01
    python tools/cf_director_cut.py from-long-slide --episode-dir data/animal_long_slide/episodes/EP_0001
    python tools/cf_director_cut.py validate dc.json [--strict]
    python tools/cf_director_cut.py vo-fit dc.json --wpm 140

Exit codes: 0 ok, 1 validation errors, 2 bad input.
Only the standard library is used; ffprobe is used when available to check clip lengths.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

SCHEMA = "cinefactory.director_cut/1"
CUTS = {"cut", "dissolve", "dip_black"}
SECTION_DEFAULTS = [
    {"id": "hook", "label": "Hook"},
    {"id": "act1", "label": "Act 1"},
    {"id": "act2", "label": "Act 2"},
    {"id": "act3", "label": "Act 3"},
    {"id": "outro", "label": "Ending"},
]
WORD = re.compile(r"[\w'’-]+", re.UNICODE)


# ----------------------------------------------------------------------------- helpers
def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"BAD_INPUT::cannot read {path}: {exc}")


def dump(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe_duration(path: Path) -> float | None:
    if shutil.which("ffprobe") is None or not path.is_file():
        return None
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True)
    try:
        return float(out.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        return None


def words(text: str) -> int:
    return len(WORD.findall(text or ""))


def shot_seconds(shot: dict) -> float:
    return max(0.0, float(shot.get("out", 0)) - float(shot.get("in", 0)))


def resolve(dc_path: Path, rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else (dc_path.parent / p)


def new_dc(episode: str, title: str = "", fps: int = 30, width: int = 1920, height: int = 1080) -> dict:
    return {
        "schema": SCHEMA,
        "episode_id": episode,
        "title": title,
        "language": "en",
        "fps": fps,
        "width": width,
        "height": height,
        "loudness_lufs": -14.0,
        "wpm": 140,
        "music": {"path": None, "gain_db": -18.0, "duck_db": -10.0},
        "sections": [dict(s) for s in SECTION_DEFAULTS],
        "shots": [],
        "notes": "Fill emotion/purpose/vo for every shot. Keep VO inside the shot length (see vo-fit).",
    }


def new_shot(index: int, source: str, start: float, end: float, section: str) -> dict:
    return {
        "id": f"S{index:03d}",
        "section": section,
        "source": source,
        "in": round(start, 3),
        "out": round(end, 3),
        "cut": "cut",
        "transition_seconds": 0.0,
        "shot_class": "",
        "emotion": "",
        "purpose": "",
        "keep_source_audio": False,
        "source_gain_db": 0.0,
        "vo": {"text": "", "audio": None, "offset": 0.3, "speaker": "narrator"},
        "sfx": [],
        "onscreen_text": None,
    }


# ----------------------------------------------------------------------------- validation
def validate(dc: dict, dc_path: Path, strict: bool = False) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if dc.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA!r}")
    for key in ("episode_id", "fps", "width", "height", "shots"):
        if key not in dc:
            errors.append(f"missing top-level key {key!r}")
    shots = dc.get("shots") or []
    if not shots:
        errors.append("no shots")
    sections = {s.get("id") for s in dc.get("sections", [])}
    seen: set[str] = set()
    wpm = float(dc.get("wpm") or 140)
    for i, shot in enumerate(shots):
        sid = shot.get("id") or f"#{i}"
        if sid in seen:
            errors.append(f"{sid}: duplicate id")
        seen.add(sid)
        if shot.get("section") not in sections:
            errors.append(f"{sid}: section {shot.get('section')!r} is not declared in sections")
        try:
            a, b = float(shot.get("in", -1)), float(shot.get("out", -1))
        except (TypeError, ValueError):
            errors.append(f"{sid}: in/out must be numbers")
            continue
        if a < 0 or b <= a:
            errors.append(f"{sid}: need 0 <= in < out (got {a}..{b})")
        cut = shot.get("cut", "cut")
        if cut not in CUTS:
            errors.append(f"{sid}: cut must be one of {sorted(CUTS)}")
        tr = float(shot.get("transition_seconds") or 0)
        if cut != "cut" and not (0.1 <= tr <= min(2.0, (b - a) / 2)):
            errors.append(f"{sid}: {cut} needs transition_seconds between 0.1 and half the shot")
        if i == 0 and cut == "dissolve":
            errors.append(f"{sid}: the first shot cannot dissolve from nothing (use cut or dip_black)")
        src = shot.get("source")
        if not src:
            errors.append(f"{sid}: missing source")
        else:
            path = resolve(dc_path, src)
            if not path.is_file():
                (errors if strict else warnings).append(f"{sid}: source not found: {path}")
            else:
                dur = probe_duration(path)
                if dur is not None and b > dur + 0.05:
                    errors.append(f"{sid}: out {b:.2f}s is past the end of the clip ({dur:.2f}s)")
        vo = shot.get("vo") or {}
        text = (vo.get("text") or "").strip()
        if vo.get("audio"):
            ap = resolve(dc_path, vo["audio"])
            if not ap.is_file():
                (errors if strict else warnings).append(f"{sid}: vo.audio not found: {ap}")
        if text:
            budget = (b - a - float(vo.get("offset") or 0)) * wpm / 60.0
            n = words(text)
            if n > budget + 0.5:
                warnings.append(f"{sid}: VO has {n} words but the shot fits ~{budget:.0f} at {wpm:.0f} wpm")
        for k, fx in enumerate(shot.get("sfx") or []):
            t = float(fx.get("t", -1))
            if not (0 <= t <= b - a):
                errors.append(f"{sid}: sfx[{k}] t={t} outside the shot")
            if not fx.get("path") and not fx.get("kind"):
                errors.append(f"{sid}: sfx[{k}] needs a path or a kind")
        if strict:
            for key in ("emotion", "purpose"):
                if not (shot.get(key) or "").strip():
                    errors.append(f"{sid}: {key} is empty (strict)")
    music = dc.get("music") or {}
    if music.get("path") and not resolve(dc_path, music["path"]).is_file():
        (errors if strict else warnings).append(f"music not found: {music['path']}")
    return errors, warnings


def timeline(dc: dict) -> list[tuple[dict, float]]:
    """(shot, start time in the final edit). A dissolve overlaps the previous shot."""
    out, t = [], 0.0
    for i, shot in enumerate(dc["shots"]):
        if i and shot.get("cut") == "dissolve":
            t -= float(shot.get("transition_seconds") or 0)
        out.append((shot, t))
        t += shot_seconds(shot)
    return out


def total_seconds(dc: dict) -> float:
    tl = timeline(dc)
    return tl[-1][1] + shot_seconds(tl[-1][0]) if tl else 0.0


# ----------------------------------------------------------------------------- long slide adapter
def _find_modules(episode: dict) -> list[dict]:
    for path in (("episode", "modules"), ("modules",), ("varied", "episode", "modules")):
        node = episode
        for key in path:
            node = node.get(key) if isinstance(node, dict) else None
        if isinstance(node, list):
            return node
    return []


OUTCOME_EMOTION = {"SUCCESS": "joy", "COMIC_FAIL": "silly surprise", "TRANSFORM": "wonder", "ESCAPE": "relief"}


def from_long_slide(episode_dir: Path, clips_dir: Path | None, fps: int, width: int, height: int) -> dict:
    ep_json = episode_dir / "episode.json"
    episode = load(ep_json) if ep_json.is_file() else {}
    package = load(episode_dir / "upload_package.json") if (episode_dir / "upload_package.json").is_file() else {}
    search = clips_dir or (episode_dir / "modules" if (episode_dir / "modules").is_dir() else episode_dir)
    clips = sorted(p for p in search.rglob("*.mp4")
                   if not p.name.startswith("episode") and not any(part.startswith(("assemble_", "card_")) for part in p.parts))
    if not clips:
        raise SystemExit(f"BAD_INPUT::no module clips under {search}")
    modules = _find_modules(episode)
    title = (package.get("title") or "").split(" | ")[0]
    dc = new_dc(episode_dir.name, title=title, fps=fps, width=width, height=height)
    dc["wpm"] = 130  # kids narration is slower
    # Original procedural music bed (same synth the old assembler used), loud enough to carry a
    # no-narration kids episode; it still ducks under any VO line that gets added later.
    seed = int(((package.get("evidence") or {}).get("planner_seed")) or 0)
    dc["music"] = {"path": None, "synth": "long_slide", "seed": seed, "gain_db": -4.0, "duck_db": -10.0}
    dc["sections"] = [{"id": "hook", "label": "Ready, set, slide!"}, {"id": "race", "label": "The race"},
                      {"id": "finale", "label": "The finish"}]
    n = len(clips)
    for i, clip in enumerate(clips, start=1):
        dur = probe_duration(clip)
        side = clip.with_suffix(".events.json")
        if not side.is_file():
            side = clip.with_name(clip.stem + ".events.json")
        events = []
        if side.is_file():
            data = load(side)
            sfps = float(data.get("fps") or fps)
            events = [{"t": round((int(e["frame"]) - 1) / sfps, 3), "kind": str(e["kind"]), "gain_db": -6.0}
                      for e in data.get("events", []) if "frame" in e and "kind" in e]
            if dur is None and data.get("frames"):
                dur = int(data["frames"]) / sfps
        dur = dur or 9.5
        section = "hook" if i == 1 else ("finale" if i == n else "race")
        rel = Path(clip).resolve()
        try:
            rel = rel.relative_to(episode_dir.resolve())
        except ValueError:
            pass
        shot = new_shot(i, str(rel).replace("\\", "/"), 0.0, dur, section)
        shot["sfx"] = [e for e in events if e["t"] <= dur]
        if i > 1:
            shot["sfx"].insert(0, {"t": 0.0, "kind": "whoosh", "gain_db": -8.0})
        if i <= len(modules):
            m = modules[i - 1]
            meta = m.get("metadata") or {}
            shot["shot_class"] = str(m.get("scene_kind") or "")
            shot["purpose"] = f"{m.get('animal_id', '?')} — {m.get('outcome', '?')}; friends={meta.get('companions')}"
            # Draft emotion from the planned outcome; the showrunner may refine it.
            shot["emotion"] = OUTCOME_EMOTION.get(str(m.get("outcome") or "").upper(), "excited")
        dc["shots"].append(shot)
    dc["shots"][0]["sfx"].insert(0, {"t": 0.0, "kind": "race_start", "gain_db": -6.0})
    if title:  # the old assembler opened with a title card; keep the promise on screen
        dc["shots"][0]["onscreen_text"] = {"text": title, "at": 0.3, "duration": min(3.0, shot_seconds(dc["shots"][0]) - 0.5),
                                          "position": "top"}
    dc["shots"][-1]["sfx"].append({"t": round(max(0.0, shot_seconds(dc["shots"][-1]) - 0.5), 3), "kind": "finish", "gain_db": -4.0})
    dc["source_episode"] = {"episode_json": "episode.json" if ep_json.is_file() else None,
                            "synopsis": ((package.get("evidence") or {}).get("concept") or {}).get("synopsis")}
    return dc


# ----------------------------------------------------------------------------- CLI
def cmd_template(args) -> int:
    dc = new_dc(args.episode, title=args.title, fps=args.fps, width=args.width, height=args.height)
    sec_cycle = ["hook"] + ["act1"] * 3 + ["act2"] * 3 + ["act3"] * 3 + ["outro"]
    for i in range(args.shots):
        sec = sec_cycle[min(i * len(sec_cycle) // max(1, args.shots), len(sec_cycle) - 1)]
        dc["shots"].append(new_shot(i + 1, f"shots/S{i + 1:03d}.mp4", 0.0, args.seconds, sec))
    out = Path(args.out)
    dump(dc, out)
    print(f"DC_OK::{out}::shots={len(dc['shots'])}")
    return 0


def cmd_from_long_slide(args) -> int:
    ep = Path(args.episode_dir)
    dc = from_long_slide(ep, Path(args.clips_dir) if args.clips_dir else None, args.fps, args.width, args.height)
    out = Path(args.out) if args.out else ep / "director_cut.json"
    dump(dc, out)
    print(f"DC_OK::{out}::shots={len(dc['shots'])}::seconds={total_seconds(dc):.1f}")
    print("NEXT::fill emotion, purpose and vo.text per shot (skill director-cut), then run cf_auto_edit.py")
    return 0


def cmd_validate(args) -> int:
    path = Path(args.dc)
    dc = load(path)
    errors, warnings = validate(dc, path, strict=args.strict)
    for w in warnings:
        print("WARN::" + w)
    for e in errors:
        print("ERROR::" + e)
    if not errors:
        print(f"VALID::{len(dc['shots'])} shots, {total_seconds(dc):.1f}s")
    return 1 if errors else 0


def cmd_vo_fit(args) -> int:
    path = Path(args.dc)
    dc = load(path)
    wpm = args.wpm or float(dc.get("wpm") or 140)
    over = 0
    print(f"{'shot':6} {'sec':>6} {'words':>6} {'budget':>7}  status")
    for shot in dc.get("shots", []):
        vo = shot.get("vo") or {}
        n = words(vo.get("text", ""))
        budget = (shot_seconds(shot) - float(vo.get("offset") or 0)) * wpm / 60.0
        status = "-" if n == 0 else ("OVER" if n > budget + 0.5 else "ok")
        if vo.get("audio"):  # a recorded/TTS line is judged by its real length
            real = probe_duration(resolve(path, vo["audio"]))
            if real is not None and real + float(vo.get("offset") or 0) > shot_seconds(shot) + 0.05:
                status = f"OVER (audio {real:.1f}s)"
        over += status.startswith("OVER")
        print(f"{shot.get('id', '?'):6} {shot_seconds(shot):6.1f} {n:6d} {budget:7.1f}  {status}")
    print(f"VO_FIT::{'FAIL' if over else 'PASS'}::{over} shot(s) over budget at {wpm:.0f} wpm")
    return 1 if over else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("template", help="blank Director Cut for any niche")
    t.add_argument("--episode", required=True)
    t.add_argument("--title", default="")
    t.add_argument("--shots", type=int, default=12)
    t.add_argument("--seconds", type=float, default=5.0, help="default length per shot")
    t.add_argument("--fps", type=int, default=30)
    t.add_argument("--width", type=int, default=1920)
    t.add_argument("--height", type=int, default=1080)
    t.add_argument("--out", required=True)
    t.set_defaults(func=cmd_template)
    f = sub.add_parser("from-long-slide", help="build from a rendered Long Slide episode folder")
    f.add_argument("--episode-dir", required=True)
    f.add_argument("--clips-dir", default="")
    f.add_argument("--fps", type=int, default=24)
    f.add_argument("--width", type=int, default=1920)
    f.add_argument("--height", type=int, default=1080)
    f.add_argument("--out", default="")
    f.set_defaults(func=cmd_from_long_slide)
    v = sub.add_parser("validate")
    v.add_argument("dc")
    v.add_argument("--strict", action="store_true", help="missing files and empty emotion/purpose are errors")
    v.set_defaults(func=cmd_validate)
    w = sub.add_parser("vo-fit", help="check every VO line fits its shot at a measured words-per-minute")
    w.add_argument("dc")
    w.add_argument("--wpm", type=float, default=0)
    w.set_defaults(func=cmd_vo_fit)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
