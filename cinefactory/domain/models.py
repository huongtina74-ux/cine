from __future__ import annotations

import json
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from .enums import (
    ArtifactKind,
    CreativeStage,
    FailureCode,
    JobState,
    ProjectState,
    RightsStatus,
    ShotComplexity,
    StageOwner,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def stable_hash(payload: str) -> str:
    return sha256(payload.encode("utf-8")).hexdigest()


def model_hash(model: BaseModel | dict[str, Any]) -> str:
    if isinstance(model, BaseModel):
        payload = model.model_dump(mode="json", exclude_none=False)
    else:
        payload = model
    return stable_hash(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")))


class OutputSpec(BaseModel):
    width: int = 3840
    height: int = 2160
    fps: float = 24.0
    color_space: str = "BT.709"
    hdr: bool = False


class CostPolicySpec(BaseModel):
    mode: Literal["ZERO_METERED_API"] = "ZERO_METERED_API"
    paid_agent_reasoning_allowed: bool = True
    paid_generation_api_allowed: bool = False
    cloud_generation_fallback: bool = False


class ProjectSpec(BaseModel):
    project_id: str = Field(default_factory=lambda: f"PRJ_{uuid4().hex[:12]}")
    prompt: str = Field(min_length=3)
    profile: str = "cinematic_story"
    language: str = "vi"
    duration_seconds: int | None = None
    aspect_ratio: str = "16:9"
    output: OutputSpec = Field(default_factory=OutputSpec)
    cost_policy: CostPolicySpec = Field(default_factory=CostPolicySpec)
    created_at: datetime = Field(default_factory=utcnow)


class CharacterState(BaseModel):
    character_id: str
    costume_id: str | None = None
    position: str | None = None
    facing: str | None = None
    eyeline: str | None = None
    emotion: str | None = None
    held_props: list[str] = Field(default_factory=list)


class WorldState(BaseModel):
    location_id: str | None = None
    time_of_day: str | None = None
    weather: str | None = None
    light_state: str | None = None
    characters: dict[str, CharacterState] = Field(default_factory=dict)
    props: dict[str, str] = Field(default_factory=dict)
    camera_side: str | None = None
    motion_axis: str | None = None


class PerformancePlan(BaseModel):
    objective: str = Field(min_length=2)
    action_verb: str = Field(min_length=2)
    inner_state: dict[str, float] = Field(default_factory=dict)
    outward_mask: str | None = None
    micro_expression: dict[str, Any] = Field(default_factory=dict)
    body_behavior: dict[str, Any] = Field(default_factory=dict)
    breath: dict[str, Any] = Field(default_factory=dict)
    listening_behavior: dict[str, Any] = Field(default_factory=dict)


class CameraMove(BaseModel):
    kind: Literal[
        "static", "dolly_in", "dolly_out", "track", "pan", "tilt", "crane", "handheld", "zoom"
    ] = "static"
    purpose: str = Field(min_length=3)
    amplitude: str | None = None
    speed: str | None = None
    start_second: float | None = None
    end_second: float | None = None

    @model_validator(mode="after")
    def validate_timing(self) -> "CameraMove":
        if self.start_second is not None and self.end_second is not None and self.end_second <= self.start_second:
            raise ValueError("camera movement end_second must be greater than start_second")
        return self


class CameraSpec(BaseModel):
    narrative_purpose: str = Field(min_length=3)
    shot_size: str
    lens_mm: float | None = Field(default=None, gt=0)
    camera_height: str | None = None
    angle: str | None = None
    camera_side: str | None = None
    focus_target: str | None = None
    composition: str | None = None
    depth_of_field: str | None = None
    movement: CameraMove


class ActionBeat(BaseModel):
    actor: str
    action: str
    target: str | None = None
    start_second: float | None = None
    end_second: float | None = None


class ShotSpec(BaseModel):
    shot_id: str
    scene_id: str
    narrative_purpose: str = Field(min_length=3)
    audience_endpoint: str = Field(min_length=3)
    duration_seconds: float = Field(gt=0, le=30)
    complexity: ShotComplexity = ShotComplexity.GREEN
    performance: dict[str, PerformancePlan] = Field(default_factory=dict)
    entry_state: WorldState
    action_beats: list[ActionBeat] = Field(default_factory=list)
    camera: CameraSpec
    edit_intent: str | None = None
    exit_state: WorldState
    previous_shot_id: str | None = None
    next_shot_id: str | None = None

    @model_validator(mode="after")
    def camera_must_be_motivated(self) -> "ShotSpec":
        if not self.camera.narrative_purpose.strip():
            raise ValueError("Every shot requires a motivated camera purpose")
        if self.camera.movement.start_second is not None and self.camera.movement.start_second > self.duration_seconds:
            raise ValueError("camera movement cannot start after the shot ends")
        if self.camera.movement.end_second is not None and self.camera.movement.end_second > self.duration_seconds:
            raise ValueError("camera movement cannot end after the shot ends")
        return self


class ShotSpecBatch(BaseModel):
    shots: list[ShotSpec] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_shot_ids(self) -> "ShotSpecBatch":
        ids = [shot.shot_id for shot in self.shots]
        if len(ids) != len(set(ids)):
            raise ValueError("ShotSpecBatch shot_id values must be unique")
        return self


class StoryBeat(BaseModel):
    beat_id: str
    purpose: str
    change: str
    audience_question: str | None = None


class StorySpec(BaseModel):
    title: str
    premise: str
    theme: str | None = None
    protagonist_goal: str
    central_conflict: str
    ending_state: str
    beats: list[StoryBeat] = Field(min_length=1)


class DialogueLine(BaseModel):
    speaker: str
    text: str
    subtext: str | None = None


class ScriptScene(BaseModel):
    scene_id: str
    heading: str
    location_id: str
    time_of_day: str
    dramatic_event: str
    entry_state_summary: str | None = None
    action: list[str] = Field(default_factory=list)
    dialogue: list[DialogueLine] = Field(default_factory=list)
    claim_ids: list[str] = Field(default_factory=list)
    exit_state_summary: str | None = None


class ScriptSpec(BaseModel):
    title: str
    logline: str
    scenes: list[ScriptScene] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_scene_ids(self) -> "ScriptSpec":
        ids = [scene.scene_id for scene in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("ScriptSpec scene_id values must be unique")
        return self


class CharacterAssetSpec(BaseModel):
    character_id: str
    name: str
    identity_lock: str = Field(min_length=3)
    appearance: str
    body: str | None = None
    hair: str | None = None
    default_costume_id: str | None = None
    expression_set: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)


class SceneAssetSpec(BaseModel):
    location_id: str
    name: str
    topology_lock: str = Field(min_length=3)
    lighting_anchors: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)


class PropAssetSpec(BaseModel):
    prop_id: str
    name: str
    identity_lock: str = Field(min_length=2)
    states: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)


class AssetBibleSpec(BaseModel):
    characters: list[CharacterAssetSpec] = Field(default_factory=list)
    scenes: list[SceneAssetSpec] = Field(default_factory=list)
    props: list[PropAssetSpec] = Field(default_factory=list)
    visual_style_lock: str = Field(min_length=3)

    @model_validator(mode="after")
    def unique_ids(self) -> "AssetBibleSpec":
        groups = [
            [x.character_id for x in self.characters],
            [x.location_id for x in self.scenes],
            [x.prop_id for x in self.props],
        ]
        if any(len(ids) != len(set(ids)) for ids in groups):
            raise ValueError("AssetBibleSpec IDs must be unique within each asset class")
        return self


class BlockingPosition(BaseModel):
    subject_id: str
    start: str
    end: str | None = None
    facing: str | None = None
    eyeline: str | None = None


class BlockingMap(BaseModel):
    scene_id: str
    action_axis: str | None = None
    allowed_camera_side: str | None = None
    positions: list[BlockingPosition] = Field(default_factory=list)
    spatial_notes: list[str] = Field(default_factory=list)


class SceneDirection(BaseModel):
    scene_id: str
    dramatic_event: str
    audience_know: str
    audience_feel: str
    audience_question: str | None = None
    power_start: str | None = None
    power_turn: str | None = None
    power_end: str | None = None
    performance_notes: dict[str, str] = Field(default_factory=dict)
    blocking: BlockingMap
    cinematography_intent: str
    sound_intent: str | None = None
    edit_intent: str | None = None


class DirectorPlan(BaseModel):
    project_title: str
    visual_concept: str
    camera_grammar: list[str] = Field(default_factory=list)
    performance_grammar: list[str] = Field(default_factory=list)
    editing_grammar: list[str] = Field(default_factory=list)
    sound_grammar: list[str] = Field(default_factory=list)
    scenes: list[SceneDirection] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_scene_direction_ids(self) -> "DirectorPlan":
        ids = [scene.scene_id for scene in self.scenes]
        if len(ids) != len(set(ids)):
            raise ValueError("DirectorPlan scene_id values must be unique")
        return self


class CreativeArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"ART_{uuid4().hex[:12]}")
    project_id: str
    stage: CreativeStage
    owner: StageOwner
    version: int = Field(ge=1)
    content_hash: str
    upstream_hashes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class RightsEnvelope(BaseModel):
    copyright: str | None = None
    commercial_use: bool | None = None
    performer_consent: bool | None = None
    voice_clone_consent: bool | None = None
    likeness_consent: bool | None = None
    trademark_clearance: bool | None = None
    attribution: str | None = None
    territory: str | None = None
    expires_at: datetime | None = None
    notes: list[str] = Field(default_factory=list)


class AssetRecord(BaseModel):
    asset_id: str
    asset_type: str
    origin: str
    source: str | None = None
    creator: str | None = None
    license_id: str | None = None
    license_snapshot_hash: str | None = None
    rights_status: RightsStatus = RightsStatus.UNKNOWN
    rights: RightsEnvelope = Field(default_factory=RightsEnvelope)
    content_hash: str | None = None
    version: int = 1
    metadata: dict[str, Any] = Field(default_factory=dict)


class ArtifactRecord(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"MEDIA_{uuid4().hex[:12]}")
    project_id: str
    kind: ArtifactKind
    relative_path: str
    content_hash: str
    bytes_size: int = Field(ge=0)
    mime_type: str | None = None
    shot_id: str | None = None
    source_job_id: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RenderJob(BaseModel):
    job_id: str = Field(default_factory=lambda: f"JOB_{uuid4().hex[:12]}")
    project_id: str
    shot_id: str | None = None
    job_type: str
    executor_id: str
    workflow_id: str
    workflow_version: str
    dependency_hash: str
    idempotency_key: str | None = None
    state: JobState = JobState.QUEUED
    attempt: int = 0
    max_attempts: int = 3
    failure_code: FailureCode | None = None
    error_detail: str | None = None
    queued_at: datetime = Field(default_factory=utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None
    output_artifact_ids: list[str] = Field(default_factory=list)
    payload: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def fill_idempotency_key(self) -> "RenderJob":
        if self.idempotency_key is None:
            raw = f"{self.project_id}|{self.shot_id}|{self.job_type}|{self.executor_id}|{self.workflow_id}|{self.workflow_version}|{self.dependency_hash}"
            self.idempotency_key = stable_hash(raw)
        return self


class JobAttempt(BaseModel):
    attempt_id: str = Field(default_factory=lambda: f"ATT_{uuid4().hex[:12]}")
    job_id: str
    attempt_number: int = Field(ge=1)
    state: JobState
    worker_id: str | None = None
    failure_code: FailureCode | None = None
    error_detail: str | None = None
    started_at: datetime = Field(default_factory=utcnow)
    finished_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"EVT_{uuid4().hex[:12]}")
    project_id: str | None = None
    event_type: str
    actor: str
    entity_type: str
    entity_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=utcnow)


class QCReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"QC_{uuid4().hex[:12]}")
    project_id: str
    shot_id: str | None = None
    artifact_id: str
    technical_pass: bool
    visual_pass: bool
    continuity_pass: bool
    cinematic_pass: bool
    sequence_pass: bool | None = None
    failure_codes: list[FailureCode] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        values = [self.technical_pass, self.visual_pass, self.continuity_pass, self.cinematic_pass]
        if self.sequence_pass is not None:
            values.append(self.sequence_pass)
        return all(values)


class ProjectRecord(BaseModel):
    spec: ProjectSpec
    state: ProjectState = ProjectState.PROJECT_CREATED
    current_version: int = 1
    blocked_reason: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
