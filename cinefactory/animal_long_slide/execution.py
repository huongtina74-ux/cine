from __future__ import annotations

import re
from pathlib import Path

from pydantic import BaseModel, Field

from .contracts import AssetKind, AssetManifest, LongSlideEpisodeSpec, LongSlideModuleSpec
from .motion import MotionCompatibilityGraph, MotionMethod, ResolvedMotion
from .registry import LongSlideAssetRegistry

# Race companions share the module with the lead. Mirrors MAX_COMPANIONS in
# scripts/long_slide_fx_plan.py (the Blender worker lanes).
MAX_COMPANIONS = 2
COMPANION_ID = re.compile(r"^[a-z0-9_]{1,40}$")
COMPANION_SEQUENCE = ["run"]


class LongSlideRenderJob(BaseModel):
    project_id: str
    episode_id: str
    module: LongSlideModuleSpec
    required_asset_ids: list[str]
    resolved_motions: list[ResolvedMotion] = Field(default_factory=list)
    companion_motions: dict[str, list[ResolvedMotion]] = Field(default_factory=dict)
    output_path: str
    width: int = Field(default=1280, gt=0)
    height: int = Field(default=720, gt=0)
    fps: int = Field(default=24, ge=12, le=60)
    render_preview: bool = False


class LongSlideExecutionPlan(BaseModel):
    executable: bool
    jobs: list[LongSlideRenderJob] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)


class LongSlideExecutionPlanner:
    def __init__(
        self,
        registry: LongSlideAssetRegistry,
        motions: MotionCompatibilityGraph | None = None,
    ) -> None:
        self.registry = registry
        self.motions = motions or MotionCompatibilityGraph()

    @staticmethod
    def companion_ids(module: LongSlideModuleSpec) -> list[str]:
        raw = module.metadata.get("companions") or []
        return [c for c in raw if isinstance(c, str)] if isinstance(raw, list) else []

    @classmethod
    def companion_blockers(cls, module: LongSlideModuleSpec) -> list[str]:
        raw = module.metadata.get("companions")
        if raw is None:
            return []
        prefix = f"INVALID_COMPANION:{module.module_id}"
        if not isinstance(raw, list):
            return [f"{prefix}:not_a_list"]
        blockers: list[str] = []
        if len(raw) > MAX_COMPANIONS:
            blockers.append(f"{prefix}:too_many:{len(raw)}>{MAX_COMPANIONS}")
        for item in raw:
            if not isinstance(item, str) or not COMPANION_ID.match(item):
                blockers.append(f"{prefix}:bad_id:{item!r}")
            elif item == module.animal_id:
                blockers.append(f"{prefix}:same_as_lead:{item}")
        if len(set(map(str, raw))) != len(raw):
            blockers.append(f"{prefix}:duplicate")
        return blockers

    @classmethod
    def required_assets(cls, module: LongSlideModuleSpec) -> list[str]:
        # Animation compatibility is resolved separately through Motion Foundry.
        # Never treat one generic animation.run asset as compatible with every rig.
        ids = [
            f"animal.{module.animal_id}",
            f"scene.{module.scene_kind.value.lower()}",
        ]
        ids.extend(
            f"obstacle.{item.obstacle_id}"
            for item in module.obstacles
            if item.enabled
        )
        ids.extend(f"animal.{c}" for c in cls.companion_ids(module))
        return list(dict.fromkeys(ids))

    def _asset_blockers(
        self,
        required_ids: list[str],
        *,
        render_preview: bool,
    ) -> list[str]:
        blockers: list[str] = []
        for asset_id in required_ids:
            asset = self.registry.maybe_get(asset_id)
            if asset is None:
                blockers.append(f"MISSING_ASSET:{asset_id}")
                continue
            if render_preview:
                if not self.registry.preview_qualified(asset):
                    blockers.append(f"UNQUALIFIED_PREVIEW_ASSET:{asset_id}")
            elif asset.production_blocked:
                blockers.append(f"UNQUALIFIED_ASSET:{asset_id}")
        return blockers

    def _motion_source_blockers(
        self,
        animal_id: str,
        motions: list[ResolvedMotion],
    ) -> list[str]:
        asset = self.registry.maybe_get(f"animal.{animal_id}")
        if asset is None:
            return []
        asset_path = self.registry.resolve_local_path(
            self.registry.root or Path("."),
            asset,
        )
        if asset_path is None:
            return []

        blockers: list[str] = []
        canonical = asset_path.resolve()
        for motion in motions:
            if motion.method is not MotionMethod.SOURCE_ACTION:
                continue
            if not motion.local_path:
                continue
            motion_path = Path(motion.local_path)
            if not motion_path.is_absolute():
                motion_path = (self.registry.root or Path(".")) / motion_path
            if motion_path.resolve() != canonical:
                blockers.append(
                    "MOTION_SOURCE_ASSET_MISMATCH:"
                    f"animal.{animal_id}:{motion.semantic_action}:"
                    f"{motion.motion_id}"
                )
        return blockers

    def plan(
        self,
        episode: LongSlideEpisodeSpec,
        *,
        output_dir: str | Path,
        width: int = 1280,
        height: int = 720,
        fps: int = 24,
        render_preview: bool = False,
    ) -> LongSlideExecutionPlan:
        output_dir = Path(output_dir)
        jobs: list[LongSlideRenderJob] = []
        blockers: list[str] = []

        for index, module in enumerate(episode.modules):
            required = self.required_assets(module)
            blockers.extend(
                self._asset_blockers(required, render_preview=render_preview)
            )
            motion_resolution = self.motions.resolve_sequence(
                module.animal_id,
                module.animation_sequence,
                render_preview=render_preview,
            )
            blockers.extend(motion_resolution.blockers)
            blockers.extend(
                self._motion_source_blockers(
                    module.animal_id,
                    motion_resolution.resolved,
                )
            )
            companion_blockers = self.companion_blockers(module)
            blockers.extend(companion_blockers)
            companion_motions: dict[str, list[ResolvedMotion]] = {}
            if not companion_blockers:
                for companion in self.companion_ids(module):
                    resolution = self.motions.resolve_sequence(
                        companion,
                        COMPANION_SEQUENCE,
                        render_preview=render_preview,
                    )
                    blockers.extend(resolution.blockers)
                    blockers.extend(
                        self._motion_source_blockers(companion, resolution.resolved)
                    )
                    companion_motions[companion] = resolution.resolved
            jobs.append(
                LongSlideRenderJob(
                    project_id=episode.project_id,
                    episode_id=episode.episode_id,
                    module=module,
                    required_asset_ids=required,
                    resolved_motions=motion_resolution.resolved,
                    companion_motions=companion_motions,
                    output_path=str(
                        output_dir / "modules"
                        / f"{index + 1:04d}_{module.module_id}.mp4"
                    ),
                    width=width,
                    height=height,
                    fps=fps,
                    render_preview=render_preview,
                )
            )

        blockers = list(dict.fromkeys(blockers))
        return LongSlideExecutionPlan(
            executable=not blockers,
            jobs=jobs,
            blockers=blockers,
        )
