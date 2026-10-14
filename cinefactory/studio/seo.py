from __future__ import annotations

from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field, model_validator


class EvidenceKind(StrEnum):
    PUBLIC_FACT = "PUBLIC_FACT"
    ESTIMATE = "ESTIMATE"
    INFERENCE = "INFERENCE"
    UNKNOWN = "UNKNOWN"


PRIVATE_COMPETITOR_METRICS = {
    "ctr", "click_through_rate", "audience_retention", "retention",
    "rpm", "cpm", "revenue", "watch_time_private",
}


class SearchObservation(BaseModel):
    query: str
    intent: str
    source: str = "youtube"
    observed_rank: int | None = Field(default=None, ge=1)
    video_id: str | None = None
    channel_id: str | None = None
    video_age_days: float | None = Field(default=None, ge=0)
    channel_age_days: float | None = Field(default=None, ge=0)
    views: int | None = Field(default=None, ge=0)
    observed_views_per_day: float | None = Field(default=None, ge=0)
    title: str | None = None
    duration_seconds: float | None = Field(default=None, gt=0)
    evidence_kind: EvidenceKind = EvidenceKind.PUBLIC_FACT
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def reject_private_metrics_as_fact(self) -> "SearchObservation":
        if self.evidence_kind is EvidenceKind.PUBLIC_FACT:
            bad = PRIVATE_COMPETITOR_METRICS & {str(k).lower() for k in self.metadata}
            if bad:
                raise ValueError("private competitor metrics cannot be recorded as PUBLIC_FACT")
        return self


class KeywordCluster(BaseModel):
    cluster_id: str
    primary_query: str
    intent: str
    related_queries: list[str] = Field(default_factory=list)
    observations: list[SearchObservation] = Field(default_factory=list)
    opportunity_notes: list[str] = Field(default_factory=list)


class ContentGap(BaseModel):
    gap_id: str
    niche_id: str
    query_cluster_id: str
    description: str
    evidence_refs: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    candidate_format: str | None = None


class NicheSEOBrain(BaseModel):
    niche_id: str
    clusters: dict[str, KeywordCluster] = Field(default_factory=dict)
    content_gaps: list[ContentGap] = Field(default_factory=list)
    title_patterns: list[str] = Field(default_factory=list)
    description_patterns: list[str] = Field(default_factory=list)
    packaging_hypotheses: list[str] = Field(default_factory=list)
    search_feedback: list[dict[str, Any]] = Field(default_factory=list)

    def add_observation(self, cluster_id: str, observation: SearchObservation) -> None:
        if cluster_id not in self.clusters:
            self.clusters[cluster_id] = KeywordCluster(
                cluster_id=cluster_id,
                primary_query=observation.query,
                intent=observation.intent,
            )
        self.clusters[cluster_id].observations.append(observation)

    def new_channel_breakouts(self, max_channel_age_days: float = 30.0,
                              min_views: int = 100_000) -> list[SearchObservation]:
        out: list[SearchObservation] = []
        for cluster in self.clusters.values():
            for item in cluster.observations:
                if (
                    item.channel_age_days is not None
                    and item.channel_age_days <= max_channel_age_days
                    and item.views is not None
                    and item.views >= min_views
                ):
                    out.append(item)
        return sorted(out, key=lambda x: (-(x.views or 0), x.channel_age_days or 0))

    def record_post_publish_feedback(self, *, video_id: str, query: str,
                                     traffic_source: str, views: int,
                                     retention_note: str | None = None) -> None:
        self.search_feedback.append({
            "video_id": video_id,
            "query": query,
            "traffic_source": traffic_source,
            "views": views,
            "retention_note": retention_note,
        })
