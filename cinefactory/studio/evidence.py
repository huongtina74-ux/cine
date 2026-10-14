from __future__ import annotations

from datetime import date
from enum import StrEnum
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

class SourceTier(StrEnum):
    PRIMARY = "PRIMARY"
    OFFICIAL = "OFFICIAL"
    RESEARCH = "RESEARCH"
    QUALITY_SECONDARY = "QUALITY_SECONDARY"

    COMMUNITY = "COMMUNITY"

    UNVERIFIED = "UNVERIFIED"

class EvidenceSource(BaseModel):
    source_id: str = Field(default_factory=lambda: f"SRC_{uuid4().hex[:10]}")
    title: str
    locator: str
    tier: SourceTier
    published_date: date | None = None
    accessed_date: date | None = None
    publisher: str | None = None
    notes: list[str] = Field(default_factory=list)

class ClaimRecord(BaseModel):
    claim_id: str = Field(default_factory=lambda: f"CLM_{uuid4().hex[:10]}")
    text: str
    source_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    verified: bool = False
    contested: bool = False
    contradictions: list[str] = Field(default_factory=list)


class EvidenceMap(BaseModel):
    sources: list[EvidenceSource] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_links(self) -> "EvidenceMap":
        source_ids = {item.source_id for item in self.sources}
        for claim in self.claims:
            missing = set(claim.source_ids) - source_ids
            if missing:
                raise ValueError(f"claim references unknown sources: {sorted(missing)}")
        return self

