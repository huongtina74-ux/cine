"""What the Long Slide factory can actually make today, measured from the repo.

One source of truth shared by the series planner (scripts/plan_long_slide_series.py),
the renderer (scripts/make_long_slide_episode.py) and the one-command producer
(scripts/produce_long_slide_episode.py). Before this existed the planner used the full
series bible (elephant, tiger, lion, gorilla, dinosaur, 43 s modules) while the renderer
silently re-planned with the preview bible and 9.5 s modules, so an approved plan was
never the episode that got rendered. Now a plan is checked against the same capability
the renderer uses, and the renderer can render exactly the approved plan.

Rule: measure, do not guess. Every answer here comes from the asset registry, the
motion graph and the execution planner, never from a hand-written list.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .contracts import LongSlideSceneKind
from .director import VariationDirector
from .execution import LongSlideExecutionPlanner
from .motion import MotionCompatibilityGraph
from .registry import LongSlideAssetRegistry
from .series import SeriesBible
from .variation import EpisodeHistory, VariedEpisode

# Module length the Blender worker is tuned and proven for (EP_DEMO_01: 7 x 9.5 s).
PROVEN_MODULE_SECONDS = 9.5
# The spiral template is a helix but runners travel a straight start-to-finish
# line, so they clip through its walls. Keep it out until a path rig exists.
UNSTAGED_SCENES: frozenset[LongSlideSceneKind] = frozenset({LongSlideSceneKind.SPIRAL_SLIDE})

GREENLIGHT_FILE = "greenlight.json"
RENDER_CHECK_FILE = "render_check.json"


def bible_paths(root: Path) -> tuple[Path, Path]:
    base = Path(root) / "config" / "animal_long_slide"
    return base / "series_bible.yaml", base / "series_bible_preview.yaml"


def renderable_animals(registry: LongSlideAssetRegistry, motions: MotionCompatibilityGraph) -> set[str]:
    """Animals with a preview-qualified asset AND a resolvable run motion."""
    return {
        animal for animal in registry.animal_ids(preview=True)
        if not motions.resolve_sequence(animal, ["run"], render_preview=True).blockers
    }


@dataclass(frozen=True)
class RenderCheck:
    executable: bool
    blockers: list[str] = field(default_factory=list)
    modules: int = 0
    module_seconds: list[float] = field(default_factory=list)
    animals: list[str] = field(default_factory=list)
    unrenderable_animals: list[str] = field(default_factory=list)
    blocked_scenes: list[str] = field(default_factory=list)
    est_render_minutes: float | None = None

    def to_json(self) -> dict:
        return {
            "executable": self.executable,
            "blockers": self.blockers,
            "modules": self.modules,
            "module_seconds": self.module_seconds,
            "animals": self.animals,
            "unrenderable_animals": self.unrenderable_animals,
            "blocked_scenes": self.blocked_scenes,
            "est_render_minutes": self.est_render_minutes,
            "checked_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        }


@dataclass
class LongSlideCapability:
    root: Path
    registry: LongSlideAssetRegistry
    motions: MotionCompatibilityGraph
    renderable: frozenset[str]
    blocked_scenes: frozenset[LongSlideSceneKind] = UNSTAGED_SCENES
    module_seconds: float = PROVEN_MODULE_SECONDS
    # Measured render speed (render seconds per second of video) from the production
    # ledger; None until at least one episode has been rendered with timing.
    render_seconds_per_video_second: float | None = None

    @classmethod
    def detect(cls, root: str | Path, *, module_seconds: float = PROVEN_MODULE_SECONDS) -> "LongSlideCapability":
        root = Path(root)
        registry = LongSlideAssetRegistry.load(root)
        motions = MotionCompatibilityGraph.load(root)
        return cls(
            root=root, registry=registry, motions=motions,
            renderable=frozenset(renderable_animals(registry, motions)),
            module_seconds=module_seconds,
            render_seconds_per_video_second=measured_render_speed(root),
        )

    # -- bible --

    def unrenderable_cast(self, bible: SeriesBible) -> list[str]:
        return sorted({c.animal_id for c in bible.cast} - self.renderable)

    def default_bible_path(self) -> Path:
        """The full bible once its whole cast can be rendered, otherwise the preview bible."""
        full, preview = bible_paths(self.root)
        if full.is_file() and not self.unrenderable_cast(SeriesBible.load(full)):
            return full
        return preview

    # -- planning --

    def director(self, bible: SeriesBible, history: EpisodeHistory, **kwargs) -> VariationDirector:
        return VariationDirector(
            bible, history,
            renderable_animals=self.renderable,
            nominal_module_seconds=self.module_seconds,
            blocked_scenes=set(self.blocked_scenes),
            **kwargs,
        )

    # -- checking a plan --

    def check(self, varied: VariedEpisode, *, width: int = 1280, height: int = 720, fps: int = 24,
              output_dir: Path | None = None) -> RenderCheck:
        episode = varied.episode
        animals = sorted({m.animal_id for m in episode.modules}
                         | {c for m in episode.modules for c in (m.metadata.get("companions") or [])})
        blocked = sorted({m.scene_kind.value for m in episode.modules if m.scene_kind in self.blocked_scenes})
        plan = LongSlideExecutionPlanner(self.registry, self.motions).plan(
            episode, output_dir=output_dir or (self.root / "data" / "tmp" / "render_check"),
            width=width, height=height, fps=fps, render_preview=True,
        )
        blockers = list(plan.blockers)
        blockers += [f"UNSTAGED_SCENE:{s}" for s in blocked]
        unrenderable = sorted(set(animals) - self.renderable)
        blockers += [f"NOT_RENDERABLE_ANIMAL:{a}" for a in unrenderable if not any(a in b for b in blockers)]
        seconds = [round(m.duration_seconds, 2) for m in episode.modules]
        est = None
        if self.render_seconds_per_video_second:
            est = round(sum(seconds) * self.render_seconds_per_video_second / 60.0, 1)
        return RenderCheck(
            executable=plan.executable and not blocked, blockers=list(dict.fromkeys(blockers)),
            modules=len(seconds), module_seconds=seconds, animals=animals,
            unrenderable_animals=unrenderable, blocked_scenes=blocked, est_render_minutes=est,
        )


# -- human point 1: greenlight ------------------------------------------------

def write_greenlight(folder: Path, varied: VariedEpisode, *, by: str, note: str = "") -> Path:
    path = Path(folder) / GREENLIGHT_FILE
    path.write_text(json.dumps({
        "episode_id": varied.episode.episode_id,
        "title": varied.package.title,
        "originality_signature": varied.episode.originality_signature,
        "by": by,
        "note": note,
        "at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
    }, indent=2), encoding="utf-8")
    return path


def read_greenlight(folder: Path, varied: VariedEpisode) -> dict | None:
    """The greenlight only counts for the exact plan it was given to."""
    path = Path(folder) / GREENLIGHT_FILE
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if data.get("originality_signature") != varied.episode.originality_signature:
        return None
    return data


# -- measured render speed ------------------------------------------------------

def ledger_path(root: Path) -> Path:
    return Path(root) / "data" / "production_ledger.jsonl"


def measured_render_speed(root: Path) -> float | None:
    """Median render seconds per second of finished video over ledger rows that have both."""
    path = ledger_path(root)
    if not path.is_file():
        return None
    ratios = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        render_s, video_s = row.get("render_seconds"), row.get("video_seconds")
        if render_s and video_s and row.get("stage") == "render":
            ratios.append(float(render_s) / float(video_s))
    if not ratios:
        return None
    ratios.sort()
    mid = len(ratios) // 2
    return round(ratios[mid] if len(ratios) % 2 else (ratios[mid - 1] + ratios[mid]) / 2, 2)
