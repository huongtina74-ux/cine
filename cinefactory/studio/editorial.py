from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, model_validator

from cinefactory.post.timeline import TimelineClip, TimelineSpec


class EditReason(StrEnum):
    INFORMATION = "INFORMATION"
    EMOTION = "EMOTION"
    ACTION = "ACTION"
    RHYTHM = "RHYTHM"
    CONTINUITY = "CONTINUITY"
    REACTION = "REACTION"
    BROLL_SUPPORT = "BROLL_SUPPORT"
    REMOVE_DEAD_TIME = "REMOVE_DEAD_TIME"


class EditDecision(BaseModel):
    decision_id: str
    source_id: str
    segment_id: str | None = None
    source_in: float = Field(default=0, ge=0)
    source_out: float = Field(gt=0)
    timeline_order: int = Field(ge=0)
    reason: EditReason
    transition: str = "cut"
    audio_lead_seconds: float = 0.0
    audio_gain_db: float = 0.0
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_range(self) -> "EditDecision":
        if self.source_out <= self.source_in:
            raise ValueError("edit source_out must be greater than source_in")
        return self


class EditDecisionGraph(BaseModel):
    project_id: str
    decisions: list[EditDecision] = Field(min_length=1)
    pacing_notes: list[str] = Field(default_factory=list)
    continuity_notes: list[str] = Field(default_factory=list)
    music_cues: list[dict[str, Any]] = Field(default_factory=list)
    sfx_cues: list[dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_orders(self) -> "EditDecisionGraph":
        orders = [d.timeline_order for d in self.decisions]
        if len(orders) != len(set(orders)):
            raise ValueError("timeline_order values must be unique")
        return self
class EditorialCompiler:
    """Compiles editorial semantics to the existing backend-neutral TimelineSpec."""

    def to_timeline(
        self,
        graph: EditDecisionGraph,
        media_paths: dict[str, str],
        *,
        fps: float = 24,
        width: int = 3840,
        height: int = 2160,
    ) -> TimelineSpec:
        clips: list[TimelineClip] = []
        for decision in sorted(graph.decisions, key=lambda x: x.timeline_order):
            if decision.source_id not in media_paths:
                raise KeyError(f"missing media path: {decision.source_id}")
            clips.append(
                TimelineClip(
                    clip_id=decision.decision_id,
                    shot_id=decision.segment_id,
                    path=media_paths[decision.source_id],
                    source_in=decision.source_in,
                    source_out=decision.source_out,
                    order=decision.timeline_order,
                    transition=decision.transition,
                    audio_gain_db=decision.audio_gain_db,
                    notes=[
                        f"edit_reason={decision.reason.value}",
                        f"audio_lead_seconds={decision.audio_lead_seconds}",
                        *decision.notes,
                    ],
                )
            )
        return TimelineSpec(
            project_id=graph.project_id,
            clips=clips,
            fps=fps,
            width=width,
            height=height,
        )


class NLEAdapterSpec(BaseModel):
    adapter_id: str
    executable: bool
    operations: set[str] = Field(default_factory=set)
    limitations: list[str] = Field(default_factory=list)


def default_nle_adapters() -> list[NLEAdapterSpec]:
    return [
        NLEAdapterSpec(
            adapter_id="ffmpeg",
            executable=True,
            operations={"hard_cut", "trim", "concat", "encode", "audio_gain"},
            limitations=["not a semantic NLE UI", "advanced multicam and manual finishing require another adapter"],
        ),
        NLEAdapterSpec(
            adapter_id="premiere",
            executable=False,
            operations={"sequence", "track", "clip", "marker", "caption", "effect", "export"},
            limitations=["requires installed/licensed Premiere and validated automation adapter"],
        ),
        NLEAdapterSpec(
            adapter_id="resolve",
            executable=False,
            operations={"edit", "fusion", "color", "fairlight", "deliver"},
            limitations=["requires installed Resolve and validated scripting adapter"],
        ),
    ]
