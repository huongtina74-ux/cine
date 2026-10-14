from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SkeletonFamily(StrEnum):
    CANINE = "quadruped.canine"
    FELINE = "quadruped.feline"
    HOOFED = "quadruped.hoofed"
    HEAVY = "quadruped.heavy"
    ELEPHANT = "quadruped.elephant"
    PRIMATE = "primate.gorilla"
    AVIAN = "avian.duck"
    DINOSAUR = "dinosaur.generic"


class MotionMethod(StrEnum):
    SOURCE_ACTION = "SOURCE_ACTION"
    PROCEDURAL = "PROCEDURAL"
    RETARGETED = "RETARGETED"


DEFAULT_FAMILY_BY_ANIMAL: dict[str, SkeletonFamily] = {
    "fox": SkeletonFamily.CANINE,
    "shiba_inu": SkeletonFamily.CANINE,
    "husky": SkeletonFamily.CANINE,
    "wolf": SkeletonFamily.CANINE,
    "dog": SkeletonFamily.CANINE,
    "pug": SkeletonFamily.CANINE,
    "tiger": SkeletonFamily.FELINE,
    "lion": SkeletonFamily.FELINE,
    "cow": SkeletonFamily.HOOFED,
    "bull": SkeletonFamily.HOOFED,
    "horse": SkeletonFamily.HOOFED,
    "white_horse": SkeletonFamily.HOOFED,
    "donkey": SkeletonFamily.HOOFED,
    "alpaca": SkeletonFamily.HOOFED,
    "llama": SkeletonFamily.HOOFED,
    "deer": SkeletonFamily.HOOFED,
    "stag": SkeletonFamily.HOOFED,
    "zebra": SkeletonFamily.HOOFED,
    "sheep": SkeletonFamily.HOOFED,
    "pig": SkeletonFamily.HEAVY,
    "buffalo": SkeletonFamily.HEAVY,
    "hippo": SkeletonFamily.HEAVY,
    "elephant": SkeletonFamily.ELEPHANT,
    "gorilla": SkeletonFamily.PRIMATE,
    "duck": SkeletonFamily.AVIAN,
    "dinosaur": SkeletonFamily.DINOSAUR,
}


# These motions are engine-owned and do not require a source Action.  The binder
# must implement them deterministically and validate the result in preview QC.
PROCEDURAL_ACTIONS = {
    "idle": "hold_pose_v1",
    "slide": "path_slide_v1",
    "impact": "bounded_impact_v1",
    "recover": "recover_to_idle_v1",
    "celebrate": "root_bounce_v1",
    "reaction": "root_reaction_v1",
}


class MotionProfile(BaseModel):
    motion_id: str
    semantic_action: str
    skeleton_family: SkeletonFamily
    local_path: str | None = None
    source_action: str | None = None
    frame_start: int | None = None
    frame_end: int | None = None
    source_fps: float | None = Field(default=None, gt=0)
    speed_multiplier: float = Field(default=1.0, gt=0)
    animal_id: str | None = None
    method: MotionMethod = MotionMethod.SOURCE_ACTION
    loopable: bool = False
    root_motion: bool = False
    foot_contact_validated: bool = False
    preview_ready: bool = False
    production_ready: bool = False
    compatible_animals: set[str] = Field(default_factory=set)
    tags: set[str] = Field(default_factory=set)


class ResolvedMotion(BaseModel):
    semantic_action: str
    motion_id: str
    method: MotionMethod
    source_action: str | None = None
    local_path: str | None = None
    frame_start: int | None = None
    frame_end: int | None = None
    source_fps: float | None = None
    speed_multiplier: float = 1.0


class MotionResolution(BaseModel):
    animal_id: str
    resolved: list[ResolvedMotion] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)

    @property
    def executable(self) -> bool:
        return not self.blockers


class MotionCompatibilityGraph:
    def __init__(self, profiles: list[MotionProfile] | None = None) -> None:
        self._profiles = {p.motion_id: p for p in (profiles or [])}

    @classmethod
    def load(cls, root: str | Path) -> "MotionCompatibilityGraph":
        path = Path(root) / "config" / "animal_long_slide" / "motions.yaml"
        if not path.exists():
            return cls()
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = raw.get("motions", [])
        if not isinstance(rows, list):
            raise ValueError("animal_long_slide/motions.yaml must contain a motions list")
        return cls([MotionProfile.model_validate(row) for row in rows])

    @staticmethod
    def family_for(animal_id: str) -> SkeletonFamily | None:
        return DEFAULT_FAMILY_BY_ANIMAL.get(animal_id.lower())

    def add(self, profile: MotionProfile) -> None:
        if profile.motion_id in self._profiles:
            raise ValueError(f"duplicate motion id: {profile.motion_id}")
        self._profiles[profile.motion_id] = profile

    def values(self) -> list[MotionProfile]:
        return list(self._profiles.values())

    def candidates(self, animal_id: str, semantic_action: str) -> list[MotionProfile]:
        family = self.family_for(animal_id)
        rows = []
        for profile in self._profiles.values():
            if profile.semantic_action != semantic_action:
                continue
            if profile.animal_id == animal_id:
                rows.append(profile)
                continue
            if animal_id in profile.compatible_animals:
                rows.append(profile)
                continue
            if profile.animal_id is None and family is not None and profile.skeleton_family is family:
                rows.append(profile)
        return sorted(
            rows,
            key=lambda p: (
                p.animal_id != animal_id,
                not p.production_ready,
                not p.foot_contact_validated,
                p.motion_id,
            ),
        )

    def resolve(self, animal_id: str, semantic_action: str) -> MotionProfile:
        rows = [p for p in self.candidates(animal_id, semantic_action) if p.production_ready]
        if not rows:
            family = self.family_for(animal_id)
            raise KeyError(
                f"no production motion for animal={animal_id} family={family} action={semantic_action}"
            )
        return rows[0]

    def resolve_sequence(
        self,
        animal_id: str,
        semantic_actions: list[str],
        *,
        allow_procedural: bool = True,
        render_preview: bool = False,
    ) -> MotionResolution:
        resolved: list[ResolvedMotion] = []
        blockers: list[str] = []
        family = self.family_for(animal_id)

        for action in semantic_actions:
            candidates = [
                item for item in self.candidates(animal_id, action)
                if (
                    item.production_ready
                    or (render_preview and item.preview_ready)
                )
            ]
            if candidates:
                item = candidates[0]
                resolved.append(ResolvedMotion(
                    semantic_action=action,
                    motion_id=item.motion_id,
                    method=item.method,
                    source_action=item.source_action,
                    local_path=item.local_path,
                    frame_start=item.frame_start,
                    frame_end=item.frame_end,
                    source_fps=item.source_fps,
                    speed_multiplier=item.speed_multiplier,
                ))
                continue

            if allow_procedural and action in PROCEDURAL_ACTIONS:
                resolved.append(ResolvedMotion(
                    semantic_action=action,
                    motion_id=f"procedural.{PROCEDURAL_ACTIONS[action]}",
                    method=MotionMethod.PROCEDURAL,
                ))
                continue

            blockers.append(
                f"MISSING_MOTION:animal.{animal_id}:{action}:family={family}"
            )

        return MotionResolution(
            animal_id=animal_id,
            resolved=resolved,
            blockers=list(dict.fromkeys(blockers)),
        )
