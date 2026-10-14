"""Plan the next Long Slide episodes for one channel, with enforced variation.

Usage:
  python scripts/plan_long_slide_series.py --channel zoomi --count 3            # plan (renderable only)
  python scripts/plan_long_slide_series.py --channel zoomi --check EP_0004      # re-check a plan against today's assets
  python scripts/plan_long_slide_series.py --channel zoomi --greenlight EP_0004 --by owner   # human point 1
  python scripts/plan_long_slide_series.py --channel zoomi --approve EP_0004    # human point 3: record after the draft is approved

Planning uses the same capability as the renderer (cinefactory.animal_long_slide.capability):
the bible whose cast can actually be animated, 9.5 s modules, no unstaged scenes. Every
planned folder gets render_check.json; a plan the factory cannot render is BLOCKED and not
written, unless --allow-unrenderable is given (it is then marked executable=false).

Planning never writes the channel history and never overwrites an existing episode folder.
--greenlight records the owner's go-ahead for that exact plan (greenlight.json); the renderer
refuses a series episode without it. --approve re-checks the episode against the current
history under a file lock and records it, after the owner has approved the finished draft.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.animal_long_slide.capability import (  # noqa: E402
    RENDER_CHECK_FILE,
    LongSlideCapability,
    read_greenlight,
    write_greenlight,
)
from cinefactory.animal_long_slide.safety import MonetizationSafetyGate  # noqa: E402
from cinefactory.animal_long_slide.series import SeriesBible  # noqa: E402
from cinefactory.animal_long_slide.variation import (  # noqa: E402
    EpisodeHistory,
    VariationExhaustedError,
    VariedEpisode,
)

EXIT_OK = 0
EXIT_BLOCKED = 2
EXIT_NOT_FOUND = 3
EXIT_ALREADY_RECORDED = 4
EXIT_REJECTED = 5
EXIT_BAD_INPUT = 6
EXIT_LOCKED = 7

SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
EPISODE_ID = re.compile(r"^EP_(\d{4,})$")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--channel", required=True, help="channel id (letters, digits, _ and -)")
    p.add_argument("--bible", default="", help="series bible (default: the full bible once its cast is renderable, else the preview bible)")
    p.add_argument("--count", type=int, default=1, help="episodes to plan")
    p.add_argument("--duration", type=float, default=330.0, help="target episode length in seconds")
    p.add_argument("--seed", type=int, default=None, help="base seed (default: derived from the episode number)")
    p.add_argument("--allow-unrenderable", action="store_true",
                   help="write plans the factory cannot render today (marked executable=false)")
    p.add_argument("--check", metavar="EPISODE_ID", help="re-check a planned episode against today's assets")
    p.add_argument("--greenlight", metavar="EPISODE_ID", help="human point 1: approve this plan for rendering")
    p.add_argument("--by", default="owner", help="who gives the greenlight")
    p.add_argument("--note", default="", help="greenlight note")
    p.add_argument("--approve", metavar="EPISODE_ID", help="record a reviewed episode in the channel history")
    p.add_argument("--data-dir", default=str(ROOT / "data" / "animal_long_slide" / "series"))
    return p.parse_args()


def episodes_root(data_dir: Path, channel: str) -> Path:
    return data_dir / channel / "episodes"


def next_number(history: EpisodeHistory, folder: Path) -> int:
    numbers = [0]
    for record in history.records():
        match = EPISODE_ID.match(record.episode_id)
        if match:
            numbers.append(int(match.group(1)))
    if folder.is_dir():
        for child in folder.iterdir():
            match = EPISODE_ID.match(child.name)
            if match:
                numbers.append(int(match.group(1)))
    return max(numbers) + 1


def write_episode(folder: Path, varied: VariedEpisode, check: dict) -> None:
    folder.mkdir(parents=True, exist_ok=False)
    (folder / RENDER_CHECK_FILE).write_text(json.dumps(check, indent=2), encoding="utf-8")
    (folder / "varied_episode.json").write_text(varied.model_dump_json(indent=2), encoding="utf-8")
    # Convenience copies for reviewers. --approve reads only varied_episode.json.
    (folder / "upload_package.json").write_text(varied.package.model_dump_json(indent=2), encoding="utf-8")
    (folder / "safety_report.json").write_text(varied.safety.model_dump_json(indent=2), encoding="utf-8")


@contextmanager
def history_lock(history_path: Path, timeout_seconds: float = 30.0):
    lock = history_path.with_suffix(history_path.suffix + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise TimeoutError(f"history is locked: {lock}") from None
            time.sleep(0.2)
    try:
        yield
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def plan(args: argparse.Namespace, bible: SeriesBible, history: EpisodeHistory, data_dir: Path,
         cap: LongSlideCapability) -> int:
    planned = history.snapshot()  # approved history plus this batch, never written to disk
    director = cap.director(bible, planned)
    folder = episodes_root(data_dir, args.channel)
    for offset in range(args.count):
        number = next_number(planned, folder)
        episode_id = f"EP_{number:04d}"
        seed = (args.seed + offset) if args.seed is not None else number * 101
        try:
            varied = director.next_episode(
                project_id=f"CH_{args.channel}", episode_id=episode_id,
                target_duration_seconds=args.duration, seed=seed,
            )
        except VariationExhaustedError as exc:
            print(f"BLOCKED: no episode passes the variation policy: {exc}")
            return EXIT_BLOCKED
        check = cap.check(varied)
        if not check.executable and not args.allow_unrenderable:
            print(f"BLOCKED {episode_id}: the factory cannot render this plan today: " + "; ".join(check.blockers[:8]))
            return EXIT_BLOCKED
        write_episode(folder / episode_id, varied, check.to_json())
        planned.append(varied)
        print(f"PLANNED {episode_id}: {varied.package.title}")
        print(f"  renderable={check.executable} modules={check.modules} animals={','.join(check.animals)}"
              + (f" est_render_min={check.est_render_minutes}" if check.est_render_minutes else ""))
        print(f"  format={varied.concept.format_id} lead={varied.concept.lead_character_id} "
              f"env={varied.concept.environment_id} ending={varied.concept.ending_id} "
              f"max_similarity={varied.report.max_similarity} min_axis_changes={varied.report.min_axis_changes}")
    print("Review each folder, then give the go-ahead with --greenlight EPISODE_ID --by owner.")
    return EXIT_OK


def load_planned(data_dir: Path, channel: str, episode_id: str) -> tuple[Path, VariedEpisode] | None:
    folder = episodes_root(data_dir, channel) / episode_id
    path = folder / "varied_episode.json"
    if not path.is_file():
        print(f"NOT FOUND: {path}")
        return None
    return folder, VariedEpisode.model_validate_json(path.read_text(encoding="utf-8"))


def check_plan(args: argparse.Namespace, data_dir: Path, cap: LongSlideCapability) -> int:
    found = load_planned(data_dir, args.channel, args.check)
    if found is None:
        return EXIT_NOT_FOUND
    folder, varied = found
    check = cap.check(varied)
    (folder / RENDER_CHECK_FILE).write_text(json.dumps(check.to_json(), indent=2), encoding="utf-8")
    state = "RENDERABLE" if check.executable else "NOT_RENDERABLE"
    print(f"{state} {args.check}: modules={check.modules} animals={','.join(check.animals)}")
    for blocker in check.blockers[:12]:
        print(f"  {blocker}")
    return EXIT_OK if check.executable else EXIT_BLOCKED


def greenlight(args: argparse.Namespace, data_dir: Path, cap: LongSlideCapability) -> int:
    found = load_planned(data_dir, args.channel, args.greenlight)
    if found is None:
        return EXIT_NOT_FOUND
    folder, varied = found
    check = cap.check(varied)
    (folder / RENDER_CHECK_FILE).write_text(json.dumps(check.to_json(), indent=2), encoding="utf-8")
    if not check.executable:
        print(f"REJECTED: {args.greenlight} cannot be rendered today: " + "; ".join(check.blockers[:8]))
        return EXIT_REJECTED
    if read_greenlight(folder, varied):
        print(f"ALREADY GREENLIT: {args.greenlight}")
        return EXIT_OK
    path = write_greenlight(folder, varied, by=args.by, note=args.note)
    print(f"GREENLIT {args.greenlight}: {varied.package.title} ({path})")
    return EXIT_OK


def approve(args: argparse.Namespace, bible: SeriesBible, data_dir: Path) -> int:
    folder = episodes_root(data_dir, args.channel) / args.approve
    path = folder / "varied_episode.json"
    if not path.is_file():
        print(f"NOT FOUND: {path}")
        return EXIT_NOT_FOUND
    varied = VariedEpisode.model_validate_json(path.read_text(encoding="utf-8"))
    if varied.episode.episode_id != args.approve:
        print(f"REJECTED: folder {args.approve} holds episode {varied.episode.episode_id}")
        return EXIT_REJECTED
    history_path = data_dir / args.channel / "history.jsonl"
    with history_lock(history_path):
        history = EpisodeHistory(history_path)  # reload inside the lock
        if any(r.episode_id == varied.episode.episode_id for r in history.records()):
            print(f"ALREADY RECORDED: {varied.episode.episode_id}")
            return EXIT_ALREADY_RECORDED
        report = MonetizationSafetyGate(bible=bible).review(varied, history)
        (folder / "approval_check.json").write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
        if not report.passed:
            print("REJECTED by the safety gate against the current history:")
            for finding in report.findings:
                print(f"  {finding.code}: {finding.message}")
            return EXIT_REJECTED
        history.append(varied)
    print(f"RECORDED {varied.episode.episode_id} in {history_path}")
    return EXIT_OK


def main() -> int:
    args = parse_args()
    ids = [x for x in (args.approve, args.check, args.greenlight) if x]
    if not SAFE_ID.match(args.channel) or any(not SAFE_ID.match(x) for x in ids):
        print("BAD INPUT: --channel and --approve may contain only letters, digits, _ and -")
        return EXIT_BAD_INPUT
    if args.count < 1:
        print("BAD INPUT: --count must be at least 1")
        return EXIT_BAD_INPUT
    data_dir = Path(args.data_dir)
    try:
        cap = LongSlideCapability.detect(ROOT)
        bible_path = Path(args.bible) if args.bible else cap.default_bible_path()
        bible = SeriesBible.load(bible_path)
        if args.check:
            return check_plan(args, data_dir, cap)
        if args.greenlight:
            return greenlight(args, data_dir, cap)
        if args.approve:
            return approve(args, bible, data_dir)
        missing = cap.unrenderable_cast(bible)
        if missing:
            print(f"NOTE: bible {bible_path.name} has cast the renderer cannot animate yet: {', '.join(missing)}")
        return plan(args, bible, EpisodeHistory(data_dir / args.channel / "history.jsonl"), data_dir, cap)
    except TimeoutError as exc:
        print(f"LOCKED: {exc}")
        return EXIT_LOCKED
    except (ValueError, OSError) as exc:
        print(f"BAD INPUT: {exc}")
        return EXIT_BAD_INPUT


if __name__ == "__main__":
    raise SystemExit(main())
