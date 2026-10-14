"""Self-test of the closed-loop tools on this machine (no Blender, no network, nothing published).

    python tools/cf_selftest.py [--video data/animal_long_slide/episodes/EP_DEMO_01/episode.mp4]

Cuts three shots out of an existing episode, writes a Director Cut with a dissolve, a dip to black,
on-screen text, a VO line (subtitle only) and Long Slide cue sounds, auto-edits a preview,
runs QC, the policy check, research stats and the decision log on throwaway files.
Everything goes to data/selftest/<timestamp>/ and nothing else is touched.
Exit 0 = all PASS.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):  # Windows consoles (cp1252) must not crash on Vietnamese/emoji text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PY = sys.executable


def run(name: str, args: list[str], results: list, ok_codes=(0,)) -> str:
    proc = subprocess.run([PY, *args], capture_output=True, text=True, cwd=ROOT)
    ok = proc.returncode in ok_codes
    last = (proc.stdout.strip().splitlines() or [proc.stderr.strip()[-300:]])[-1]
    results.append((name, ok, last))
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {last}")
    if not ok and proc.stderr:
        print("      " + proc.stderr.strip()[-600:].replace("\n", "\n      "))
    return proc.stdout


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--video", default="data/animal_long_slide/episodes/EP_DEMO_01/episode.mp4")
    args = p.parse_args()
    video = (ROOT / args.video).resolve()
    if not video.is_file():
        print(f"SKIP::no test video at {video} (pass --video <any mp4 longer than 30 s>)")
        return 2
    work = ROOT / "data" / "selftest" / time.strftime("%Y%m%d_%H%M%S")
    work.mkdir(parents=True, exist_ok=True)
    results: list = []
    dc_path = work / "director_cut.json"
    run("director-cut template", [str(HERE / "cf_director_cut.py"), "template", "--episode", "SELFTEST", "--shots", "3",
                                  "--seconds", "6", "--fps", "24", "--width", "1280", "--height", "720", "--out", str(dc_path)], results)
    dc = json.loads(dc_path.read_text(encoding="utf-8"))
    dc["sections"] = [{"id": "hook", "label": "Start"}, {"id": "act1", "label": "Middle"}, {"id": "outro", "label": "End"}]
    spans = [(4.0, 10.0), (20.0, 26.0), (40.0, 46.0)]
    for shot, (a, b), sec in zip(dc["shots"], spans, ["hook", "act1", "outro"]):
        shot.update({"source": str(video), "in": a, "out": b, "section": sec, "emotion": "happy", "purpose": "self-test"})
    dc["shots"][0]["onscreen_text"] = {"text": "Self test", "at": 0.5, "duration": 2, "position": "top"}
    dc["shots"][0]["vo"]["text"] = "This is a short self test line."
    dc["shots"][0]["sfx"] = [{"t": 0.2, "kind": "race_start", "gain_db": -6}]
    dc["shots"][1].update({"cut": "dissolve", "transition_seconds": 0.5})
    dc["shots"][2].update({"cut": "dip_black", "transition_seconds": 0.8})
    dc_path.write_text(json.dumps(dc, indent=2), encoding="utf-8")
    run("director-cut validate", [str(HERE / "cf_director_cut.py"), "validate", str(dc_path)], results)
    run("director-cut vo-fit", [str(HERE / "cf_director_cut.py"), "vo-fit", str(dc_path)], results)
    run("auto-edit preview", [str(HERE / "cf_auto_edit.py"), str(dc_path), "--preview", "--repo", str(ROOT)], results)
    out = work / "edit" / "SELFTEST_preview.mp4"
    if out.is_file():
        run("qc", [str(HERE / "cf_qc.py"), str(out), "--profile", "shorts"], results, ok_codes=(0, 1))
    pkg = work / "upload_package.json"
    pkg.write_text(json.dumps({"title": "Self test", "description": "Self test.", "tags": ["self test"],
                               "made_for_kids": True, "ai_disclosure_required": False}), encoding="utf-8")
    run("policy-check", [str(HERE / "cf_policy_check.py"), "--package", str(pkg), "--dc", str(dc_path),
                         "--srt", str(out.with_suffix(".srt"))], results)
    raw = work / "raw.json"
    raw.write_text(json.dumps([{"channel": c, "title": f"video {i}", "views": v, "published": "2026-10-01"}
                               for c in ("A", "B") for i, v in enumerate([1000, 1200, 900, 15000])]), encoding="utf-8")
    run("research-stats", [str(HERE / "cf_research_stats.py"), str(raw), "--out", str(work / "stats.md")], results)
    run("decision-log", [str(HERE / "cf_decision.py"), "--log", str(work / "decisions.jsonl"), "add", "--kind", "tool",
                         "--decision", "self-test passed", "--why", "cf_selftest", "--label", "OBSERVED", "--evidence", str(work)], results)
    bad = [r for r in results if not r[1]]
    print(f"SELFTEST_{'PASS' if not bad else 'FAIL'}::{len(results) - len(bad)}/{len(results)}::{work}")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
