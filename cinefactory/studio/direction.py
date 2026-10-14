from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class DramaticState(BaseModel):
    emotion: dict[str, str] = Field(default_factory=dict)
    positions: dict[str, str] = Field(default_factory=dict)
    facing: dict[str, str] = Field(default_factory=dict)
    held_props: dict[str, list[str]] = Field(default_factory=dict)
    environment: dict[str, Any] = Field(default_factory=dict)


class SceneDramaticSpec(BaseModel):
    segment_id: str
    purpose: str
    conflict: str | None = None
    participants: list[str] = Field(default_factory=list)
    location_id: str | None = None
    entry_state: DramaticState = Field(default_factory=DramaticState)
    objectives: dict[str, str] = Field(default_factory=dict)
    obstacles: list[str] = Field(default_factory=list)
    actions: list[str] = Field(default_factory=list)
    dialogue_intent: list[str] = Field(default_factory=list)
    emotional_turn: str | None = None
    props: list[str] = Field(default_factory=list)
    world_event: str | None = None
    exit_state: DramaticState = Field(default_factory=DramaticState)


class BlockingBeat(BaseModel):
    subject_id: str
    from_mark: str
    to_mark: str | None = None
    facing_target: str | None = None
    motivation: str
    start_seconds: float = Field(default=0, ge=0)
class BlockingPlan(BaseModel):
    segment_id: str
    action_axis: str | None = None
    allowed_camera_side: str | None = None
    beats: list[BlockingBeat] = Field(default_factory=list)
    spatial_notes: list[str] = Field(default_factory=list)


class PerformanceBeat(BaseModel):
    subject_id: str
    objective: str
    action_verb: str
    internal_state: str | None = None
    outward_behavior: str | None = None
    gaze_target: str | None = None
    expression: str | None = None
    gesture: str | None = None
    energy: float = Field(default=0.5, ge=0.0, le=1.0)
    reaction_trigger: str | None = None
    reaction_delay_seconds: float | None = Field(default=None, ge=0)
    voice_emotion: str | None = None


class PerformancePlan(BaseModel):
    segment_id: str
    beats: list[PerformanceBeat] = Field(default_factory=list)


class CameraCoverageShot(BaseModel):
    shot_id: str
    segment_id: str
    purpose: str = Field(min_length=3)
    scale: str
    lens_mm: float | None = Field(default=None, gt=0)
    camera_side: str | None = None
    movement: str = "static"
    movement_purpose: str | None = None
    subjects: list[str] = Field(default_factory=list)
    edit_use: str | None = None

    @model_validator(mode="after")
    def motivated_move(self) -> "CameraCoverageShot":
        if self.movement != "static" and not self.movement_purpose:
            raise ValueError("camera movement requires story/information purpose")
        return self
class CameraCoveragePlan(BaseModel):
    segment_id: str
    shots: list[CameraCoverageShot] = Field(min_length=1)


class DirectorCut(BaseModel):
    project_id: str
    format_grammar: list[str] = Field(default_factory=list)
    dramatic_arc: list[str] = Field(default_factory=list)
    emotional_arc: list[str] = Field(default_factory=list)
    segments: list[SceneDramaticSpec] = Field(default_factory=list)
    blocking: list[BlockingPlan] = Field(default_factory=list)
    performance: list[PerformancePlan] = Field(default_factory=list)
    coverage: list[CameraCoveragePlan] = Field(default_factory=list)
    sound_intent: dict[str, list[str]] = Field(default_factory=dict)
    edit_intent: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_segment_ids(self) -> "DirectorCut":
        ids = [x.segment_id for x in self.segments]
        if len(ids) != len(set(ids)):
            raise ValueError("director cut segment ids must be unique")
        return self


class ContinuitySnapshot(BaseModel):
    segment_id: str
    entity_id: str
    position: str | None = None
    facing: str | None = None
    pose: str | None = None
    emotion: str | None = None
    costume: str | None = None
    damage: str | None = None
    held_props: list[str] = Field(default_factory=list)
    inventory: list[str] = Field(default_factory=list)
    lighting: str | None = None
    time_of_day: str | None = None
    camera_side: str | None = None
    screen_direction: str | None = None
class ContinuityLedger(BaseModel):
    snapshots: list[ContinuitySnapshot] = Field(default_factory=list)

    def latest(self, entity_id: str) -> ContinuitySnapshot | None:
        matches = [x for x in self.snapshots if x.entity_id == entity_id]
        return matches[-1] if matches else None


class ContinuityValidator:
    """Checks high-signal spatial and prop continuity between ordered dramatic segments."""

    def validate(self, director_cut: DirectorCut) -> list[str]:
        findings: list[str] = []
        prior: SceneDramaticSpec | None = None
        for current in director_cut.segments:
            if prior is not None:
                for entity_id, props in prior.exit_state.held_props.items():
                    next_props = current.entry_state.held_props.get(entity_id)
                    if next_props is not None and sorted(props) != sorted(next_props):
                        findings.append(
                            f"{current.segment_id}:{entity_id}:HELD_PROP_DISCONTINUITY"
                        )
                for entity_id, facing in prior.exit_state.facing.items():
                    next_facing = current.entry_state.facing.get(entity_id)
                    if next_facing is not None and facing != next_facing:
                        findings.append(
                            f"{current.segment_id}:{entity_id}:FACING_STATE_CHANGED_WITHOUT_TRANSITION"
                        )
            prior = current
        return findings
