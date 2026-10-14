from __future__ import annotations

from enum import StrEnum
from statistics import mean
from typing import Any

from pydantic import BaseModel, Field, model_validator


class ObservationType(StrEnum):
    HOOK = "HOOK"
    STORY_STRUCTURE = "STORY_STRUCTURE"
    CAMERA = "CAMERA"
    EDITING = "EDITING"
    AUDIO = "AUDIO"
    PRODUCTION_METHOD = "PRODUCTION_METHOD"
    PACKAGING = "PACKAGING"
    AUDIENCE_SIGNAL = "AUDIENCE_SIGNAL"


class VideoObservation(BaseModel):
    observation_id: str
    kind: ObservationType
    description: str
    timestamp_seconds: float | None = Field(default=None, ge=0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    evidence_refs: list[str] = Field(default_factory=list)
    expression_sensitive: bool = False


class CompetitorVideoProfile(BaseModel):
    video_id: str
    source_locator: str
    title: str | None = None
    duration_seconds: float | None = Field(default=None, gt=0)
    observations: list[VideoObservation] = Field(default_factory=list)
    transcript_quarantined: bool = True
    raw_expression_allowed_in_creative_context: bool = False

    @model_validator(mode="after")
    def enforce_quarantine(self) -> "CompetitorVideoProfile":
        if self.raw_expression_allowed_in_creative_context:
            raise ValueError("raw competitor expression cannot enter creative context")
        return self
class PatternEvidence(BaseModel):
    pattern_id: str
    abstraction: str
    observation_kind: ObservationType
    sample_video_ids: list[str] = Field(default_factory=list)
    support_count: int = Field(ge=0)
    sample_count: int = Field(gt=0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    exceptions: list[str] = Field(default_factory=list)
    tested_by_us: bool = False
    our_results: dict[str, Any] = Field(default_factory=dict)

    @property
    def support_ratio(self) -> float:
        return self.support_count / self.sample_count


class ProductionGrammar(BaseModel):
    hook_principles: list[str] = Field(default_factory=list)
    progression_principles: list[str] = Field(default_factory=list)
    camera_principles: list[str] = Field(default_factory=list)
    editing_principles: list[str] = Field(default_factory=list)
    audio_principles: list[str] = Field(default_factory=list)
    production_methods: list[str] = Field(default_factory=list)
    packaging_principles: list[str] = Field(default_factory=list)
    copy_prohibitions: list[str] = Field(
        default_factory=lambda: [
            "storyline",
            "dialogue",
            "character identity",
            "creator identity",
            "branding",
            "thumbnail expression",
            "proprietary assets",
        ]
    )


class NichePlaybook(BaseModel):
    niche: str
    audience_expectations: list[str] = Field(default_factory=list)
    production_grammar: ProductionGrammar = Field(default_factory=ProductionGrammar)
    patterns: list[PatternEvidence] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
class PatternMiner:
    """Only promotes abstractions supported across multiple videos."""

    def mine(
        self,
        profiles: list[CompetitorVideoProfile],
        *,
        min_support: int = 2,
        min_ratio: float = 0.4,
    ) -> list[PatternEvidence]:
        if not profiles:
            return []
        buckets: dict[tuple[ObservationType, str], list[tuple[str, VideoObservation]]] = {}
        for profile in profiles:
            for obs in profile.observations:
                if obs.expression_sensitive:
                    continue
                key = (obs.kind, obs.description.strip().lower())
                buckets.setdefault(key, []).append((profile.video_id, obs))

        patterns: list[PatternEvidence] = []
        sample_count = len(profiles)
        for idx, ((kind, abstraction), items) in enumerate(sorted(buckets.items(), key=lambda x: (x[0][0].value, x[0][1]))):
            video_ids = sorted({video_id for video_id, _ in items})
            support = len(video_ids)
            ratio = support / sample_count
            if support < min_support or ratio < min_ratio:
                continue
            patterns.append(
                PatternEvidence(
                    pattern_id=f"PAT_{idx + 1:03d}",
                    abstraction=abstraction,
                    observation_kind=kind,
                    sample_video_ids=video_ids,
                    support_count=support,
                    sample_count=sample_count,
                    confidence=min(0.99, mean(obs.confidence for _, obs in items) * ratio),
                )
            )
        return patterns


class NichePlaybookCompiler:
    def compile(self, niche: str, patterns: list[PatternEvidence], gaps: list[str] | None = None) -> NichePlaybook:
        grammar = ProductionGrammar()
        for pattern in patterns:
            target = {
                ObservationType.HOOK: grammar.hook_principles,
                ObservationType.STORY_STRUCTURE: grammar.progression_principles,
                ObservationType.CAMERA: grammar.camera_principles,
                ObservationType.EDITING: grammar.editing_principles,
                ObservationType.AUDIO: grammar.audio_principles,
                ObservationType.PRODUCTION_METHOD: grammar.production_methods,
                ObservationType.PACKAGING: grammar.packaging_principles,
            }.get(pattern.observation_kind)
            if target is not None:
                target.append(pattern.abstraction)
        return NichePlaybook(
            niche=niche,
            production_grammar=grammar,
            patterns=patterns,
            gaps=gaps or [],
        )
