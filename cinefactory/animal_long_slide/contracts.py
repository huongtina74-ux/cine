from __future__ import annotations

from enum import StrEnum
from hashlib import sha256
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AssetKind(StrEnum):
    ANIMAL = "ANIMAL"
    SCENE = "SCENE"
    OBSTACLE = "OBSTACLE"
    ANIMATION = "ANIMATION"
    AUDIO = "AUDIO"


class LicenseState(StrEnum):
    APPROVED = "APPROVED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class LongSlideSceneKind(StrEnum):
    LONG_SLIDE = "LONG_SLIDE"
    SPIRAL_SLIDE = "SPIRAL_SLIDE"
    PAINT_GATE = "PAINT_GATE"
    FOUNTAIN = "FOUNTAIN"
    CAGE = "CAGE"
    KEY_DOOR = "KEY_DOOR"
    BALL_PIT = "BALL_PIT"
    GIANT_ANIMAL = "GIANT_ANIMAL"


class OutcomeKind(StrEnum):
    SUCCESS = "SUCCESS"
    COMIC_FAIL = "COMIC_FAIL"
    TRANSFORM = "TRANSFORM"
    ESCAPE = "ESCAPE"


class AssetManifest(BaseModel):
    asset_id: str
    kind: AssetKind
    source_uri: str | None = None
    source_pack_id: str | None = None
    license_evidence_uri: str | None = None
    license_state: LicenseState = LicenseState.UNKNOWN
    commercial_use: bool = False
    redistribution_allowed: bool = False
    local_path: str | None = None
    version: str = "1"
    blender_min_version: str | None = None
    rig_profile: str | None = None
    clip_ids: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    production_ready: bool = False
    technical_qc_passed: bool = False
    visual_qc_passed: bool = False
    content_sha256: str | None = None
    provenance_notes: list[str] = Field(default_factory=list)
    tags: set[str] = Field(default_factory=set)

    @property
    def production_blocked(self) -> bool:
        return (
            not self.production_ready
            or not self.commercial_use
            or self.license_state is not LicenseState.APPROVED
            or not self.technical_qc_passed
            or not self.visual_qc_passed
        )


class AnimalProfile(BaseModel):
    animal_id: str
    rig_profile: str
    available_clips: set[str] = Field(default_factory=set)
    camera_target_height: float = Field(default=1.0, gt=0)
    ground_offset: float = 0.0
    tags: set[str] = Field(default_factory=set)


class ObstaclePlacement(BaseModel):
    obstacle_id: str
    slot: str
    enabled: bool = True
    seed: int = 0


class CameraBeat(BaseModel):
    pattern_id: str
    start_seconds: float = Field(ge=0)
    end_seconds: float = Field(gt=0)
    target: str

    @model_validator(mode="after")
    def validate_range(self) -> "CameraBeat":
        if self.end_seconds <= self.start_seconds:
            raise ValueError("camera beat end must be after start")
        return self


class ReactionEvent(BaseModel):
    event_id: str
    at_seconds: float = Field(ge=0)
    event_type: str = "SFX_REACTION"
    payload: dict[str, Any] = Field(default_factory=dict)


class LongSlideModuleSpec(BaseModel):
    module_id: str
    scene_kind: LongSlideSceneKind
    animal_id: str
    duration_seconds: float = Field(gt=5, le=90)
    animation_sequence: list[str] = Field(min_length=1)
    obstacles: list[ObstaclePlacement] = Field(default_factory=list)
    controlled_phase_seconds: float = Field(default=0, ge=0)
    physics_phase_seconds: float = Field(default=0, ge=0)
    outcome: OutcomeKind
    camera_beats: list[CameraBeat] = Field(min_length=1)
    events: list[ReactionEvent] = Field(default_factory=list)
    seed: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_timing(self) -> "LongSlideModuleSpec":
        if self.controlled_phase_seconds + self.physics_phase_seconds > self.duration_seconds:
            raise ValueError("controlled + physics phases exceed module duration")
        for beat in self.camera_beats:
            if beat.end_seconds > self.duration_seconds + 1e-6:
                raise ValueError("camera beat exceeds module duration")
        for event in self.events:
            if event.at_seconds > self.duration_seconds + 1e-6:
                raise ValueError("event exceeds module duration")
        return self


class LongSlideEpisodeSpec(BaseModel):
    project_id: str
    episode_id: str
    title: str
    target_duration_seconds: float = Field(gt=15)
    modules: list[LongSlideModuleSpec] = Field(min_length=1)
    originality_signature: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def planned_duration_seconds(self) -> float:
        return round(sum(m.duration_seconds for m in self.modules), 3)

    @classmethod
    def signature_for(cls, modules: list[LongSlideModuleSpec]) -> str:
        payload = "|".join(
            (
                f"{m.scene_kind.value}:{m.animal_id}:"
                f"{','.join(o.obstacle_id for o in m.obstacles if o.enabled)}:"
                f"{m.outcome.value}:"
                f"{','.join(beat.pattern_id for beat in m.camera_beats)}"
            )
            for m in modules
        )
        return sha256(payload.encode("utf-8")).hexdigest()[:20]


class LongSlideQCFinding(BaseModel):
    code: str
    severity: str
    message: str
    module_id: str | None = None


class LongSlideQCReport(BaseModel):
    passed: bool
    findings: list[LongSlideQCFinding] = Field(default_factory=list)
