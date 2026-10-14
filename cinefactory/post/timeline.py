from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class TimelineClip(BaseModel):
    clip_id: str
    shot_id: str | None = None
    path: str
    source_in: float = Field(default=0, ge=0)
    source_out: float | None = Field(default=None, gt=0)
    order: int = Field(ge=0)
    transition: str = "cut"
    audio_gain_db: float = 0.0
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def valid_trim(self) -> "TimelineClip":
        if self.source_out is not None and self.source_out <= self.source_in:
            raise ValueError("source_out must be greater than source_in")
        return self


class TimelineSpec(BaseModel):
    project_id: str
    clips: list[TimelineClip] = Field(min_length=1)
    fps: float = Field(default=24, gt=0)
    width: int = 3840
    height: int = 2160
    audio_sample_rate: int = 48000

    @model_validator(mode="after")
    def unique_order(self) -> "TimelineSpec":
        orders = [c.order for c in self.clips]
        if len(orders) != len(set(orders)):
            raise ValueError("Timeline clip order must be unique")
        return self
