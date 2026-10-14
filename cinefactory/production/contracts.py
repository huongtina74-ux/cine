from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field

from cinefactory.domain.enums import FailureCode


class AssetCandidate(BaseModel):
    candidate_id: str
    asset_key: str
    asset_kind: Literal["character", "scene", "prop"]
    path: str
    prompt: str
    technical_pass: bool = True
    visual_pass: bool = True
    visual_score: float = Field(default=1.0, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)
    seed: int | None = None


class CanonicalAssetSelection(BaseModel):
    asset_key: str
    asset_kind: Literal["character", "scene", "prop"]
    selected_candidate_id: str
    selected_path: str
    score: float = Field(ge=0.0, le=1.0)
    rejected_candidate_ids: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class AssetFactoryReport(BaseModel):
    passed: bool
    selections: list[CanonicalAssetSelection] = Field(default_factory=list)
    candidates: list[AssetCandidate] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class KeyframeCandidate(BaseModel):
    candidate_id: str
    shot_id: str
    path: str
    prompt: str
    visual_pass: bool = True
    visual_score: float = Field(default=1.0, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)
    seed: int | None = None


class StoryboardShotApproval(BaseModel):
    shot_id: str
    approved: bool
    selected_candidate_id: str | None = None
    selected_path: str | None = None
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)


class StoryboardGateReport(BaseModel):
    passed: bool
    shots: list[StoryboardShotApproval] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class TakeRecord(BaseModel):
    take_id: str
    shot_id: str
    path: str
    seed: int | None = None
    technical_pass: bool = True
    visual_pass: bool = True
    identity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    continuity_score: float | None = Field(default=None, ge=0.0, le=1.0)
    performance_score: float | None = Field(default=None, ge=0.0, le=1.0)
    camera_score: float | None = Field(default=None, ge=0.0, le=1.0)
    aggregate_score: float = Field(default=1.0, ge=0.0, le=1.0)
    failure_code: FailureCode | None = None
    findings: list[str] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)
    score_semantics: dict[str, str] = Field(default_factory=dict)
    repair_round: int = 0


class ShotDailiesReport(BaseModel):
    shot_id: str
    passed: bool
    selected_take_id: str | None = None
    selected_path: str | None = None
    selected_score: float = Field(default=0.0, ge=0.0, le=1.0)
    takes: list[TakeRecord] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    repair_directives: list[RepairDirective] = Field(default_factory=list)


class DailiesReport(BaseModel):
    passed: bool
    shots: list[ShotDailiesReport] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    repair_directives: list[RepairDirective] = Field(default_factory=list)
    execution_metrics: dict[str, Any] = Field(default_factory=dict)


class RepairDirective(BaseModel):
    shot_id: str
    failure_code: FailureCode
    owner: str
    retryable: bool
    action: str
    prompt_directive: str | None = None
    invalidates: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
