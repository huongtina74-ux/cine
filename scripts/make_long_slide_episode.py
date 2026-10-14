"""Plan, render and assemble one complete Long Slide episode.

    python scripts/make_long_slide_episode.py --episode EP_DEMO --seconds 66 --seed 21

1. VariationDirector plans a monetization-safe episode from the series bible,
   with race friends limited to animals the renderer can animate.
2. The execution planner resolves assets and motions (fail-closed).
3. Each module is rendered by the headless Blender worker (resumable: modules
   whose clip and sound-cue sidecar already exist are skipped).
4. assemble_long_slide_episode builds the title card, cuts, music, sound
   effects and end card into episode.mp4.

Two ways to choose what to render:
  --varied data/animal_long_slide/series/<channel>/episodes/EP_0004/varied_episode.json
      renders EXACTLY that approved series plan (title, cast, scenes, seeds). The plan
      must carry greenlight.json for that plan (human point 1, given with
      plan_long_slide_series.py --greenlight) unless --no-greenlight is passed for a
      dry run. Output goes next to the plan, so one folder holds the whole episode.
  --episode EP_DEMO --seed 21
      plans a throwaway demo with an empty in-memory history (tests, look-dev).

Both paths use the same capability as the planner (cinefactory.animal_long_slide.capability).
Render time per module is appended to data/production_ledger.jsonl (measure, do not guess).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from assemble_long_slide_episode import assemble  # noqa: E402
from cinefactory.animal_long_slide.blender_binder import LongSlideBlenderBinder  # noqa: E402
from cinefactory.animal_long_slide.capability import (  # noqa: E402
    PROVEN_MODULE_SECONDS,
    UNSTAGED_SCENES,
    LongSlideCapability,
    ledger_path,
    read_greenlight,
)
from cinefactory.animal_long_slide.capability import renderable_animals as _renderable_animals  # noqa: E402
from cinefactory.animal_long_slide.execution import LongSlideExecutionPlanner  # noqa: E402
from cinefactory.animal_long_slide.motion import MotionCompatibilityGraph  # noqa: E402
from cinefactory.animal_long_slide.registry import LongSlideAssetRegistry  # noqa: E402
from cinefactory.animal_long_slide.series import SeriesBible  # noqa: E402
from cinefactory.animal_long_slide.variation import EpisodeHistory, VariedEpisode  # noqa: E402
from long_slide_events import sidecar_path  # noqa: E402

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
DEFAULT_BIBLE = ROOT / "config" / "animal_long_slide" / "series_bible_preview.yaml"
DEFAULT_BLENDER = ROOT / ".tools" / "blender-4.5.14-windows-x64" / "blender.exe"
EXIT_OK, EXIT_BLOCKED, EXIT_BAD_INPUT, EXIT_NOT_GREENLIT = 0, 2, 6, 8


def job_stamp(job) -> str:
    """Identity of a render job: module spec, size, fps and output path."""
    return hashlib.sha256(job.model_dump_json().encode("utf-8")).hexdigest()


def stamp_path(clip: Path) -> Path:
    return clip.with_name(clip.stem + ".job.sha256")


def frame_count(clip: Path) -> int:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0",
         "-show_entries", "stream=nb_read_packets", "-of", "csv=p=0", str(clip)],
        capture_output=True, text=True,
    )
    try:
        return int(result.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        return -1


def reusable(job, clip: Path) -> bool:
    """A finished clip is reused only for the same job and only if it is complete."""
    side = sidecar_path(clip)
    stamp = stamp_path(clip)
    if not (clip.is_file() and side.is_file() and stamp.is_file()):
        return False
    if stamp.read_text(encoding="utf-8").strip() != job_stamp(job):
        return False
    try:
        expected = int(json.loads(side.read_text(encoding="utf-8"))["frames"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return False
    return frame_count(clip) == expected


def renderable_animals(registry: LongSlideAssetRegistry, motions: MotionCompatibilityGraph) -> set[str]:
    return _renderable_animals(registry, motions)


def append_ledger(row: dict) -> None:
    path = ledger_path(ROOT)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), **row}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def load_varied(path: Path, *, require_greenlight: bool) -> tuple[VariedEpisode | None, str]:
    if not path.is_file():
        return None, f"BAD_INPUT::no plan at {path}"
    varied = VariedEpisode.model_validate_json(path.read_text(encoding="utf-8"))
    if require_greenlight and not read_greenlight(path.parent, varied):
        return None, ("NOT_GREENLIT::" + varied.episode.episode_id + " has no greenlight for this exact plan. "
                      "Review the folder, then run: python scripts/plan_long_slide_series.py --channel <channel> "
                      f"--greenlight {varied.episode.episode_id} --by owner")
    return varied, ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--varied", default="", help="render this approved series plan (varied_episode.json)")
    parser.add_argument("--no-greenlight", action="store_true", help="allow --varied without greenlight.json (dry runs only)")
    parser.add_argument("--episode", default="", help="demo episode id, letters/digits/_/- only (ignored with --varied)")
    parser.add_argument("--project", default="LONG_SLIDE_DEMO")
    parser.add_argument("--seconds", type=float, default=66.0, help="content length without the title and end cards")
    parser.add_argument("--module-seconds", type=float, default=PROVEN_MODULE_SECONDS)
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--bible", default=str(DEFAULT_BIBLE))
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--blender", default=str(DEFAULT_BLENDER))
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--plan-only", action="store_true")
    args = parser.parse_args()
    if not args.varied and not args.episode:
        print("BAD_INPUT::give --varied <varied_episode.json> (series episode) or --episode <id> (demo)")
        return EXIT_BAD_INPUT
    if (args.episode and not SAFE_ID.fullmatch(args.episode)) or not SAFE_ID.fullmatch(args.project):
        print("BAD_INPUT::episode and project ids may only use letters, digits, _ and -")
        return EXIT_BAD_INPUT

    cap = LongSlideCapability.detect(ROOT, module_seconds=args.module_seconds)
    registry, motions, renderable = cap.registry, cap.motions, cap.renderable
    if args.varied:
        varied_path = Path(args.varied).resolve()
        varied, error = load_varied(varied_path, require_greenlight=not (args.no_greenlight or args.plan_only))
        if varied is None:
            print(error)
            return EXIT_NOT_GREENLIT if error.startswith("NOT_GREENLIT") else EXIT_BAD_INPUT
        bible = SeriesBible.load(Path(args.bible)) if args.bible != str(DEFAULT_BIBLE) else SeriesBible.load(cap.default_bible_path())
        seed = int((varied.package.evidence or {}).get("planner_seed") or args.seed)
        default_out = varied_path.parent
    else:
        bible = SeriesBible.load(Path(args.bible))
        try:
            varied = cap.director(bible, EpisodeHistory()).next_episode(
                project_id=args.project, episode_id=args.episode, target_duration_seconds=args.seconds, seed=args.seed)
        except ValueError as exc:
            print(f"BAD_INPUT::{exc}")
            return EXIT_BAD_INPUT
        seed = args.seed
        default_out = ROOT / "data" / "animal_long_slide" / "episodes" / args.episode
    check = cap.check(varied, width=args.width, height=args.height, fps=args.fps)
    if not check.executable:
        print("BLOCKED::this plan cannot be rendered today: " + ";".join(check.blockers[:12]))
        return EXIT_BLOCKED

    out_dir = (Path(args.out_dir) if args.out_dir else default_out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    plan = LongSlideExecutionPlanner(registry, motions).plan(
        varied.episode, output_dir=out_dir, width=args.width, height=args.height, fps=args.fps, render_preview=True)
    (out_dir / "episode.json").write_text(varied.model_dump_json(indent=2), encoding="utf-8")
    (out_dir / "upload_package.json").write_text(varied.package.model_dump_json(indent=2), encoding="utf-8")
    for module in varied.episode.modules:
        meta = module.metadata
        print(f"MODULE::{module.module_id}:{module.scene_kind.value}:{module.animal_id}:{module.outcome.value}"
              f":friends={meta.get('companions')}:gimmicks={meta.get('gimmicks')}:theme={meta['environment']['theme_id']}")
    print("TITLE::" + varied.package.title)
    if not plan.executable:
        print("BLOCKED::" + ";".join(plan.blockers))
        return EXIT_BLOCKED
    if args.plan_only:
        return EXIT_OK

    binder = LongSlideBlenderBinder(ROOT, blender_executable=args.blender, registry=registry)
    clips = []
    render_started = time.time()
    rendered_seconds = 0.0
    rendered_video_seconds = 0.0
    for index, job in enumerate(plan.jobs, start=1):
        clip = Path(job.output_path)
        if reusable(job, clip):
            print(f"RENDER_SKIP::{index}/{len(plan.jobs)}:{clip.name}", flush=True)
        else:
            for stale in (clip, sidecar_path(clip), stamp_path(clip)):
                stale.unlink(missing_ok=True)
            started = time.time()
            clip = binder.execute(job, timeout_seconds=3600)
            if not sidecar_path(clip).is_file():
                print(f"BLOCKED::worker wrote no sound-cue sidecar for {clip.name}")
                return EXIT_BLOCKED
            stamp_path(clip).write_text(job_stamp(job), encoding="utf-8")
            took = time.time() - started
            rendered_seconds += took
            rendered_video_seconds += float(job.module.duration_seconds)
            print(f"RENDER_OK::{index}/{len(plan.jobs)}:{clip.name}:{took:.0f}s", flush=True)
        clips.append(clip)
    episode = assemble(clips, out_dir / "episode.mp4", title=varied.package.title.split(" | ")[0],
                       brand=bible.brand, seed=seed)
    if rendered_seconds:
        append_ledger({"stage": "render", "episode_id": varied.episode.episode_id, "out_dir": str(out_dir),
                       "render_seconds": round(rendered_seconds, 1), "video_seconds": round(rendered_video_seconds, 2),
                       "modules_rendered": sum(1 for _ in plan.jobs), "width": args.width, "height": args.height,
                       "wall_seconds": round(time.time() - render_started, 1)})
    summary = {"episode": str(episode), "title": varied.package.title, "modules": len(clips),
               "render_seconds": round(rendered_seconds, 1), "from_plan": bool(args.varied)}
    (out_dir / "render_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("EPISODE_OK::" + str(episode))
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
