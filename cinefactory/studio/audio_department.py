from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class AudioRole(StrEnum):
    DIALOGUE = "DIALOGUE"
    NARRATION = "NARRATION"
    AMBIENCE = "AMBIENCE"
    FOLEY = "FOLEY"
    SFX = "SFX"
    MUSIC = "MUSIC"
    SILENCE = "SILENCE"


class AudioCue(BaseModel):
    cue_id: str
    role: AudioRole
    segment_id: str | None = None
    start_seconds: float = Field(ge=0)
    duration_seconds: float | None = Field(default=None, gt=0)
    purpose: str
    asset_ref: str | None = None
    target_lufs: float | None = None
    peak_ceiling_dbfs: float | None = None
    duck_under_dialogue: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class VoicePerformanceSpec(BaseModel):
    line_id: str
    text: str
    speaker_id: str | None = None
    emotion: str | None = None
    intent: str | None = None
    pace: str | None = None
    emphasis: list[str] = Field(default_factory=list)
    pause_before_ms: int = Field(default=0, ge=0)
    pause_after_ms: int = Field(default=0, ge=0)


class AudioPlan(BaseModel):
    project_id: str
    voice: list[VoicePerformanceSpec] = Field(default_factory=list)
    cues: list[AudioCue] = Field(default_factory=list)
    dialogue_priority: bool = True
    mix_rules: list[str] = Field(
        default_factory=lambda: [
            "dialogue intelligibility first",
            "no clipping",
            "music must not mask speech",
            "silence may be intentional",
        ]
    )
class AudioQC:
    def validate(self, plan: AudioPlan) -> list[str]:
        findings: list[str] = []
        cue_ids = [c.cue_id for c in plan.cues]
        if len(cue_ids) != len(set(cue_ids)):
            findings.append("DUPLICATE_AUDIO_CUE_ID")
        for cue in plan.cues:
            if cue.role is AudioRole.MUSIC and not cue.duck_under_dialogue and plan.dialogue_priority:
                findings.append(f"{cue.cue_id}:MUSIC_DUCKING_UNSPECIFIED")
            if cue.peak_ceiling_dbfs is not None and cue.peak_ceiling_dbfs > 0:
                findings.append(f"{cue.cue_id}:INVALID_PEAK_CEILING")
        return findings


class DialogueLockState(StrEnum):
    DRAFT = "DRAFT"
    LOCKED = "LOCKED"


class DialogueLineTiming(BaseModel):
    line_id: str
    segment_id: str
    speaker_id: str
    target_entity_id: str | None = None
    start_seconds: float = Field(ge=0)
    duration_seconds: float = Field(gt=0)
    audio_ref: str | None = None
    viseme_ref: str | None = None


class DialogueLock(BaseModel):
    project_id: str
    state: DialogueLockState = DialogueLockState.DRAFT
    lines: list[DialogueLineTiming] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_lock(self) -> "DialogueLock":
        ids = [line.line_id for line in self.lines]
        if len(ids) != len(set(ids)):
            raise ValueError("dialogue line_id values must be unique")
        if self.state is DialogueLockState.LOCKED:
            incomplete = [
                line.line_id
                for line in self.lines
                if not line.audio_ref or not line.speaker_id
            ]
            if incomplete:
                raise ValueError(
                    "locked dialogue requires rendered audio: "
                    + ",".join(incomplete)
                )
        return self


class LipSyncJob(BaseModel):
    line_id: str
    segment_id: str
    target_entity_id: str
    audio_ref: str
    start_seconds: float = Field(ge=0)
    duration_seconds: float = Field(gt=0)
    capability_id: str | None = None
    executable: bool = False
    blockers: list[str] = Field(default_factory=list)


class LipSyncPlan(BaseModel):
    project_id: str
    jobs: list[LipSyncJob] = Field(default_factory=list)
    blocked: bool = False


class LipSyncPlanner:
    def plan(
        self,
        dialogue: DialogueLock,
        *,
        capability_id: str | None = None,
        capability_executable: bool = False,
    ) -> LipSyncPlan:
        if dialogue.state is not DialogueLockState.LOCKED:
            raise ValueError("DIALOGUE_MUST_BE_LOCKED_BEFORE_LIPSYNC")

        jobs: list[LipSyncJob] = []
        for line in dialogue.lines:
            blockers: list[str] = []
            if not line.target_entity_id:
                blockers.append("TARGET_ENTITY_REQUIRED")
            if not capability_id or not capability_executable:
                blockers.append("LIPSYNC_CAPABILITY_UNAVAILABLE")
            jobs.append(
                LipSyncJob(
                    line_id=line.line_id,
                    segment_id=line.segment_id,
                    target_entity_id=line.target_entity_id or "UNRESOLVED",
                    audio_ref=line.audio_ref or "",
                    start_seconds=line.start_seconds,
                    duration_seconds=line.duration_seconds,
                    capability_id=capability_id,
                    executable=not blockers,
                    blockers=blockers,
                )
            )

        return LipSyncPlan(
            project_id=dialogue.project_id,
            jobs=jobs,
            blocked=any(not job.executable for job in jobs),
        )
