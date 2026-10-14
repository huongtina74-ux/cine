from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field, model_validator


class ResearchClaim(BaseModel):
    claim_id: str
    claim: str = Field(min_length=3)
    source_url: str | None = None
    source_title: str | None = None
    source_date: date | None = None
    evidence_note: str | None = None
    verified: bool = False
    high_risk: bool = False


class ResearchBrief(BaseModel):
    topic: str
    target_audience: str | None = None
    claims: list[ResearchClaim] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    competitor_reference_ids: list[str] = Field(default_factory=list)


class TopicScore(BaseModel):
    demand: float = Field(ge=0, le=10)
    audience_fit: float = Field(ge=0, le=10)
    channel_fit: float = Field(ge=0, le=10)
    evergreen: float = Field(ge=0, le=10)
    originality_opportunity: float = Field(ge=0, le=10)
    production_feasibility: float = Field(ge=0, le=10)
    rights_risk: float = Field(ge=0, le=10)
    collision_risk: float = Field(ge=0, le=10)
    rationale: list[str] = Field(default_factory=list)

    @property
    def overall(self) -> float:
        positive = self.demand + self.audience_fit + self.channel_fit + self.evergreen + self.originality_opportunity + self.production_feasibility
        penalty = self.rights_risk + self.collision_risk
        return round(max(0.0, min(10.0, positive / 6 - penalty * 0.12)), 2)


class TopicStrategy(BaseModel):
    topic: str
    angle: str = Field(min_length=5)
    audience: str = Field(min_length=3)
    score: TopicScore
    differentiation_axes: list[str] = Field(min_length=3)
    forbidden_angles: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def distinct_axes(self) -> "TopicStrategy":
        if len({x.strip().casefold() for x in self.differentiation_axes if x.strip()}) < 3:
            raise ValueError("TopicStrategy requires at least three distinct differentiation axes")
        return self
