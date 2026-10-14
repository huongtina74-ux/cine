"""One command from a greenlit plan to an upload-ready package (CineFactory closed loop).

    python scripts/produce_long_slide_episode.py --channel zoomi --episode EP_0004
    python scripts/produce_long_slide_episode.py --channel zoomi --episode EP_0004 --animatic   # cheap look first
    python scripts/produce_long_slide_episode.py --channel zoomi --episode EP_0004 --until edit --preview

Stages, each resumable and recorded in <episode>/production.json:
  gate      plan exists, greenlight.json matches this exact plan, render check passes
  animatic  (only with --animatic) 640x360 render of the same plan into <episode>/animatic/, contact
            sheet, then STOP so the owner can look before the full render is paid for
  render    scripts/make_long_slide_episode.py --varied (Blender modules, resumable per module)
  cut       tools/cf_director_cut.py from-long-slide -> vo-fit -> validate --strict
  edit      tools/cf_auto_edit.py (Director Cut -> edit/<EP>_edit.mp4 + .srt + .chapters.txt)
  qc        tools/cf_qc.py (numbers + contact sheet). FAIL stops here: qc-reviewer writes qc_notes.md
  policy    tools/cf_policy_check.py on the planned upload package vs what the video says and shows
  handoff   HANDOFF.md (human point 3), decision log row, production ledger row, phone notice

People step in three times: greenlight the plan, read QC notes when QC escalates, approve the draft.
Nothing is uploaded. Exit codes: 0 done (or stopped at --until), 2 blocked, 3 QC failed,
4 policy FAIL, 8 not greenlit, 10 animatic ready for review.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cinefactory.animal_long_slide.capability import (  # noqa: E402
    RENDER_CHECK_FILE,
    LongSlideCapability,
    ledger_path,
    read_greenlight,
)
from cinefactory.animal_long_slide.variation import VariedEpisode  # noqa: E402

for _stream in (sys.stdout, sys.stderr):  # Windows consoles must not crash on Vietnamese text
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass

STAGES = ["gate", "animatic", "render", "cut", "edit", "qc", "policy", "handoff"]
SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
PY = sys.executable
EXIT_OK, EXIT_BLOCKED, EXIT_QC, EXIT_POLICY, EXIT_NOT_GREENLIT, EXIT_ANIMATIC = 0, 2, 3, 4, 8, 10


class Production:
    def __init__(self, folder: Path) -> None:
        self.folder = folder
        self.path = folder / "production.json"
        self.state = json.loads(self.path.read_text(encoding="utf-8")) if self.path.is_file() else {"stages": {}}

    def done(self, stage: str) -> bool:
        return (self.state["stages"].get(stage) or {}).get("status") == "done"

    def record(self, stage: str, status: str, **info) -> None:
        self.state["stages"][stage] = {"status": status, "at": time.strftime("%Y-%m-%dT%H:%M:%S"), **info}
        self.path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    def reset_from(self, stage: str) -> None:
        for name in STAGES[STAGES.index(stage):]:
            self.state["stages"].pop(name, None)
        self.path.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")


def run(args: list[str], *, label: str, timeout: int | None = None) -> tuple[int, str]:
    print(f"--> {label}", flush=True)
    started = time.time()
    proc = subprocess.Popen([PY, *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace")
    lines: list[str] = []
    assert proc.stdout is not None
    for line in proc.stdout:
        lines.append(line)
        print("    " + line.rstrip(), flush=True)
    code = proc.wait(timeout=timeout)
    print(f"<-- {label}: exit {code} in {time.time() - started:.0f}s", flush=True)
    return code, "".join(lines)


def grab(output: str, prefix: str) -> str:
    for line in reversed(output.splitlines()):
        line = line.strip()
        if line.startswith(prefix):
            return line[len(prefix):]
    return ""


def append_ledger(row: dict) -> None:
    path = ledger_path(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), **row}, ensure_ascii=False) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--channel", required=True)
    p.add_argument("--episode", required=True, help="series episode id, e.g. EP_0004")
    p.add_argument("--data-dir", default=str(ROOT / "data" / "animal_long_slide" / "series"))
    p.add_argument("--res", default="1280x720", help="render size WxH (1920x1080 for final masters)")
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--blender", default="", help="Blender executable (default: the repo's .tools copy)")
    p.add_argument("--animatic", action="store_true", help="render a 640x360 animatic and stop for review")
    p.add_argument("--preview", action="store_true", help="edit at 640x360 (fast check of the cut)")
    p.add_argument("--until", choices=STAGES, default="handoff", help="stop after this stage")
    p.add_argument("--redo", choices=STAGES, default="", help="forget this stage and everything after it")
    p.add_argument("--profile", default="kids_long", help="cf_qc profile")
    p.add_argument("--notify", action="store_true", help="send the hand-off line to the phone (cf_notify)")
    args = p.parse_args()
    if not SAFE_ID.match(args.channel) or not SAFE_ID.match(args.episode):
        print("BAD_INPUT::channel and episode may only use letters, digits, _ and -")
        return EXIT_BLOCKED
    m = re.fullmatch(r"(\d+)x(\d+)", args.res)
    if not m:
        print("BAD_INPUT::--res must look like 1280x720")
        return EXIT_BLOCKED
    width, height = int(m.group(1)), int(m.group(2))

    folder = Path(args.data_dir) / args.channel / "episodes" / args.episode
    plan_path = folder / "varied_episode.json"
    if not plan_path.is_file():
        print(f"BLOCKED::no plan at {plan_path}. Plan first: python scripts/plan_long_slide_series.py --channel {args.channel}")
        return EXIT_BLOCKED
    varied = VariedEpisode.model_validate_json(plan_path.read_text(encoding="utf-8"))
    prod = Production(folder)
    if args.redo:
        prod.reset_from(args.redo)
    ep_id = varied.episode.episode_id
    dc_path = folder / "director_cut.json"
    edit_path = folder / "edit" / f"{ep_id}{'_preview' if args.preview else '_edit'}.mp4"
    blender = ["--blender", args.blender] if args.blender else []

    def stop_here(stage: str) -> bool:
        return STAGES.index(stage) >= STAGES.index(args.until)

    # ---------------------------------------------------------------- gate
    cap = LongSlideCapability.detect(ROOT)
    check = cap.check(varied, width=width, height=height, fps=args.fps)
    (folder / RENDER_CHECK_FILE).write_text(json.dumps(check.to_json(), indent=2), encoding="utf-8")
    if not check.executable:
        prod.record("gate", "blocked", blockers=check.blockers[:20])
        print("BLOCKED::this plan cannot be rendered today: " + "; ".join(check.blockers[:10]))
        return EXIT_BLOCKED
    greenlight = read_greenlight(folder, varied)
    if not greenlight:
        prod.record("gate", "waiting", reason="no greenlight for this exact plan")
        print(f"NOT_GREENLIT::{ep_id}. Human point 1: review {folder} then run\n"
              f"  python scripts/plan_long_slide_series.py --channel {args.channel} --greenlight {ep_id} --by owner")
        return EXIT_NOT_GREENLIT
    prod.record("gate", "done", greenlight_by=greenlight.get("by"), modules=check.modules,
                est_render_minutes=check.est_render_minutes, title=varied.package.title)
    print(f"GATE_OK::{ep_id}::{varied.package.title}::modules={check.modules}"
          + (f"::est_render_min={check.est_render_minutes}" if check.est_render_minutes else ""))
    if stop_here("gate"):
        return EXIT_OK

    # ---------------------------------------------------------------- animatic (optional)
    if args.animatic:
        anim_dir = folder / "animatic"
        code, out = run([str(ROOT / "scripts" / "make_long_slide_episode.py"), "--varied", str(plan_path),
                         "--width", "640", "--height", "360", "--fps", str(args.fps), "--out-dir", str(anim_dir), *blender],
                        label="animatic render (640x360)")
        if code != 0:
            prod.record("animatic", "failed", exit=code)
            return EXIT_BLOCKED
        code, out = run([str(ROOT / "tools" / "cf_qc.py"), str(anim_dir / "episode.mp4"), "--profile", "youtube_long",
                         "--out-dir", str(anim_dir)], label="animatic contact sheet")
        sheet = grab(out, "CONTACT_SHEET::")
        prod.record("animatic", "review", contact_sheet=sheet, video=str(anim_dir / "episode.mp4"))
        print(f"ANIMATIC_READY::{anim_dir / 'episode.mp4'}\nCONTACT_SHEET::{sheet}\n"
              "Look at it. If it is right, run the same command without --animatic for the full render.")
        return EXIT_ANIMATIC

    # ---------------------------------------------------------------- render
    if not prod.done("render") or not (folder / "episode.mp4").is_file():
        started = time.time()
        code, out = run([str(ROOT / "scripts" / "make_long_slide_episode.py"), "--varied", str(plan_path),
                         "--width", str(width), "--height", str(height), "--fps", str(args.fps), *blender],
                        label=f"render {check.modules} modules at {width}x{height}")
        if code != 0:
            prod.record("render", "failed", exit=code, tail=out.splitlines()[-5:])
            print("BLOCKED::render failed (see the Blender log named above); fix, then run the same command again")
            return EXIT_BLOCKED
        prod.record("render", "done", wall_seconds=round(time.time() - started, 1), size=f"{width}x{height}")
    if stop_here("render"):
        return EXIT_OK

    # ---------------------------------------------------------------- Director Cut
    if not prod.done("cut") or not dc_path.is_file():
        code, out = run([str(ROOT / "tools" / "cf_director_cut.py"), "from-long-slide", "--episode-dir", str(folder),
                         "--clips-dir", str(folder / "modules"), "--fps", str(args.fps), "--width", str(width),
                         "--height", str(height), "--out", str(dc_path)], label="Director Cut from the rendered modules")
        if code != 0:
            prod.record("cut", "failed", exit=code)
            return EXIT_BLOCKED
        run([str(ROOT / "tools" / "cf_director_cut.py"), "vo-fit", str(dc_path)], label="VO fit")
        code, out = run([str(ROOT / "tools" / "cf_director_cut.py"), "validate", str(dc_path), "--strict"],
                        label="validate Director Cut")
        if code != 0:
            prod.record("cut", "failed", exit=code)
            return EXIT_BLOCKED
        prod.record("cut", "done", director_cut=str(dc_path))
    if stop_here("cut"):
        return EXIT_OK

    # ---------------------------------------------------------------- edit
    if not prod.done("edit") or not edit_path.is_file():
        started = time.time()
        code, out = run([str(ROOT / "tools" / "cf_auto_edit.py"), str(dc_path), "--repo", str(ROOT),
                         *(["--preview"] if args.preview else [])], label="auto edit")
        if code != 0:
            prod.record("edit", "failed", exit=code)
            return EXIT_BLOCKED
        took = round(time.time() - started, 1)
        prod.record("edit", "done", video=str(edit_path), seconds=took, preview=args.preview)
        append_ledger({"stage": "edit", "episode_id": ep_id, "edit_seconds": took, "preview": args.preview,
                       "out": str(edit_path)})
    if stop_here("edit"):
        return EXIT_OK

    # ---------------------------------------------------------------- QC (independent numbers)
    qc_json = edit_path.with_suffix(".qc.json")
    if not prod.done("qc") or not qc_json.is_file():
        profile = "youtube_long" if args.preview else args.profile
        code, out = run([str(ROOT / "tools" / "cf_qc.py"), str(edit_path), "--profile", profile,
                         "--min-seconds", str(min(120, int(sum(check.module_seconds) * 0.8)))], label="technical QC")
        sheet = grab(out, "CONTACT_SHEET::")
        if code == 1 and not args.preview:
            prod.record("qc", "failed", report=str(qc_json), contact_sheet=sheet)
            run([str(ROOT / "tools" / "cf_decision.py"), "add", "--kind", "qc", "--decision", f"{ep_id} QC FAIL",
                 "--why", "cf_qc blocking findings", "--label", "OBSERVED", "--evidence", str(qc_json), "--project", ep_id],
                label="decision log")
            print(f"QC_FAIL::{qc_json}\nNext: qc-reviewer writes qc_notes.md (video-qc skill); the owner reads it only "
                  "if the fix loop escalates. Then: --redo edit (or --redo render for a module re-render).")
            return EXIT_QC
        if code not in (0, 1):
            prod.record("qc", "failed", exit=code)
            return EXIT_BLOCKED
        prod.record("qc", "done", report=str(qc_json), contact_sheet=sheet, verdict="PASS" if code == 0 else "PREVIEW")
    if stop_here("qc"):
        return EXIT_OK

    # ---------------------------------------------------------------- policy
    package_path = folder / "upload_package.json"
    policy_json = folder / "policy_report.json"
    if not prod.done("policy") or not policy_json.is_file():
        srt = edit_path.with_suffix(".srt")
        code, out = run([str(ROOT / "tools" / "cf_policy_check.py"), "--package", str(package_path), "--dc", str(dc_path),
                         *(["--srt", str(srt)] if srt.is_file() else []), "--json", str(policy_json)], label="policy check")
        verdict = grab(out, "POLICY_")
        if not verdict:
            prod.record("policy", "failed", exit=code, reason="policy check crashed")
            print("BLOCKED::policy check did not run (see the error above)")
            return EXIT_BLOCKED
        if code == 1:
            prod.record("policy", "failed", report=str(policy_json))
            print(f"POLICY_FAIL::{policy_json} (packaging-seo fixes the title/tags, then --redo policy)")
            return EXIT_POLICY
        prod.record("policy", "done", verdict=verdict, report=str(policy_json))
    if stop_here("policy"):
        return EXIT_OK

    # ---------------------------------------------------------------- hand-off (human point 3)
    qc = json.loads(qc_json.read_text(encoding="utf-8")) if qc_json.is_file() else {}
    policy = json.loads(policy_json.read_text(encoding="utf-8")) if policy_json.is_file() else {}
    stages = prod.state["stages"]
    loud = ((qc.get("analysis") or {}).get("loudness") or {})
    lines = [
        f"# HANDOFF — {ep_id}", "",
        f"**Title:** {varied.package.title}", "",
        f"- Greenlit by: {stages.get('gate', {}).get('greenlight_by')}",
        f"- Video: `{edit_path.name}` ({qc.get('probe', {}).get('duration', 0):.1f}s, "
        f"{(qc.get('probe') or {}).get('video', {}).get('width')}x{(qc.get('probe') or {}).get('video', {}).get('height')})",
        f"- Subtitles: {('`' + edit_path.with_suffix('.srt').name + '`') if edit_path.with_suffix('.srt').is_file() else 'none (no narration)'}"
        f" · Chapters: `{edit_path.with_suffix('.chapters.txt').name}`",
        f"- QC: {stages.get('qc', {}).get('verdict')} · LUFS {loud.get('integrated_lufs')} · true peak {loud.get('true_peak_dbtp')} "
        f"· contact sheet `{Path(stages.get('qc', {}).get('contact_sheet') or '').name}`",
        f"- QC warnings: {'; '.join(qc.get('warnings') or []) or 'none'}",
        f"- Policy: {policy.get('verdict')} · warnings: {'; '.join(policy.get('warnings') or []) or 'none'}",
        f"- Render: {stages.get('render', {}).get('wall_seconds')} s wall for {check.modules} modules at "
        f"{stages.get('render', {}).get('size')} · edit {stages.get('edit', {}).get('seconds')} s",
        f"- Package: `upload_package.json` (made_for_kids={varied.package.made_for_kids}, "
        f"ai_disclosure_required={varied.package.ai_disclosure_required})", "",
        "## Owner (human point 3)", "",
        "1. Watch the video and the contact sheet. Write any fix as a timecoded line in `qc_notes.md`.",
        "2. If it is good: upload it yourself as a PRIVATE draft (Claude never uploads).",
        f"3. Then record it: `python scripts/plan_long_slide_series.py --channel {args.channel} --approve {ep_id}`",
    ]
    (folder / "HANDOFF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    append_ledger({"stage": "handoff", "episode_id": ep_id, "video_seconds": (qc.get("probe") or {}).get("duration"),
                   "render_wall_seconds": stages.get("render", {}).get("wall_seconds"),
                   "edit_seconds": stages.get("edit", {}).get("seconds"), "qc": stages.get("qc", {}).get("verdict"),
                   "policy": policy.get("verdict")})
    run([str(ROOT / "tools" / "cf_decision.py"), "add", "--kind", "package", "--decision", f"{ep_id} ready for owner review",
         "--why", f"QC {stages.get('qc', {}).get('verdict')}, policy {policy.get('verdict')}", "--label", "OBSERVED",
         "--evidence", str(folder / "HANDOFF.md"), "--project", ep_id], label="decision log")
    prod.record("handoff", "done", handoff=str(folder / "HANDOFF.md"))
    print(f"HANDOFF::{folder / 'HANDOFF.md'}")
    if args.notify:
        run([str(ROOT / "tools" / "cf_notify.py"), f"{ep_id} ready for review: {varied.package.title}"], label="notify")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
