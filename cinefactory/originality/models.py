from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class ReferenceKind(StrEnum):
    COMPETITOR = "COMPETITOR"
    PRIOR_OWN = "PRIOR_OWN"
    SOURCE_MATERIAL = "SOURCE_MATERIAL"
    INSPIRATION = "INSPIRATION"




class ConceptFingerprint(BaseModel):
    """Structured semantic fingerprint used to catch concept collisions without exposing raw competitor copy to creative agents."""

    thesis: str = ""
    primary_question: str = ""
    causal_mechanism: str = ""
    audience_promise: str = ""
    narrative_device: str = ""
    evidence_domains: list[str] = Field(default_factory=list)
    example_entities: list[str] = Field(default_factory=list)
    beat_functions: list[str] = Field(default_factory=list)
    visual_grammar_tags: list[str] = Field(default_factory=list)


class ConceptCollisionFinding(BaseModel):
    reference_id: str
    kind: ReferenceKind
    overall_similarity: float = Field(ge=0, le=1)
    collision_axes: list[str] = Field(default_factory=list)
    axis_scores: dict[str, float] = Field(default_factory=dict)
    severity: str


class ReferenceRecord(BaseModel):
    """Material that must remain outside the creative source of truth.

    Raw competitor/source text is retained locally for similarity checks only. Creative
    reasoning should receive only the metadata summaries and negative constraints, never
    the raw competitor script.
    """

    reference_id: str = Field(default_factory=lambda: f"REF_{uuid4().hex[:12]}")
    kind: ReferenceKind
    title: str
    source_url: str | None = None
    raw_text: str = ""
    idea_summary: str | None = None
    hook_summary: str | None = None
    structure_beats: list[str] = Field(default_factory=list)
    packaging_notes: list[str] = Field(default_factory=list)
    concept_fingerprint: ConceptFingerprint | None = None
    collision_tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def safe_metadata(self) -> dict[str, Any]:
        """Human-facing metadata. Do not pass this object to creative reasoning by default."""
        return {
            "reference_id": self.reference_id,
            "kind": self.kind.value,
            "title": self.title,
            "idea_summary": self.idea_summary,
            "hook_summary": self.hook_summary,
            "structure_beats": self.structure_beats,
            "packaging_notes": self.packaging_notes,
            "collision_tags": self.collision_tags,
        }

    def quarantine_view(self) -> dict[str, Any]:
        """Minimal negative-reference view safe for a creative agent.

        It deliberately excludes competitor title, raw text, exact hook wording, beat text and URL.
        The creative model should invent independently; post-generation gates do the actual comparison.
        """
        return {
            "reference_id": self.reference_id,
            "kind": self.kind.value,
            "collision_tags": list(self.collision_tags),
            "avoid": [
                "do not imitate the reference's title or thumbnail formulation",
                "do not preserve its premise/causal mechanism/beat order with renamed details",
                "do not reuse distinctive wording, examples, metaphors or scene order",
            ],
        }


class OriginalityPolicy(BaseModel):
    # Expression copying gates.
    shingle_size: int = Field(default=7, ge=4, le=12)
    max_generated_shingle_coverage: float = Field(default=0.10, ge=0, le=1)
    max_document_jaccard: float = Field(default=0.18, ge=0, le=1)
    max_sentence_similarity: float = Field(default=0.90, ge=0, le=1)
    max_title_similarity: float = Field(default=0.84, ge=0, le=1)
    # Idea/structure collision gates use metadata summaries created by the research layer.
    max_idea_similarity: float = Field(default=0.72, ge=0, le=1)
    max_structure_similarity: float = Field(default=0.72, ge=0, le=1)
    max_concept_fingerprint_similarity: float = Field(default=0.68, ge=0, le=1)
    min_concept_collision_axes: int = Field(default=4, ge=2, le=9)
    max_prior_own_fingerprint_similarity: float = Field(default=0.62, ge=0, le=1)
    min_differentiation_axes: int = Field(default=3, ge=2, le=8)
    hard_block: bool = True


class DifferentiationPlan(BaseModel):
    original_thesis: str = Field(min_length=12)
    target_audience: str = Field(min_length=3)
    differentiation_axes: list[str] = Field(min_length=3)
    evidence_plan: list[str] = Field(default_factory=list)
    narrative_device: str = Field(min_length=3)
    visual_grammar: str = Field(min_length=3)
    forbidden_patterns: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def axes_must_be_distinct(self) -> "DifferentiationPlan":
        normalized = {x.strip().casefold() for x in self.differentiation_axes if x.strip()}
        if len(normalized) < 3:
            raise ValueError("DifferentiationPlan requires at least three distinct differentiation axes")
        return self


class SimilarityFinding(BaseModel):
    reference_id: str
    reference_title: str
    metric: str
    score: float = Field(ge=0, le=1)
    threshold: float = Field(ge=0, le=1)
    severity: str
    detail: str


class OriginalityReport(BaseModel):
    passed: bool
    artifact_kind: str
    highest_similarity: float = Field(default=0, ge=0, le=1)
    findings: list[SimilarityFinding] = Field(default_factory=list)
    rewrite_directives: list[str] = Field(default_factory=list)
    compared_reference_ids: list[str] = Field(default_factory=list)


class AuthenticityReport(BaseModel):
    passed: bool
    expression_report: OriginalityReport | None = None
    concept_findings: list[ConceptCollisionFinding] = Field(default_factory=list)
    channel_repetition_risk: str = "LOW"
    required_changes: list[str] = Field(default_factory=list)


class ScriptCriticReport(BaseModel):
    passed: bool
    repeated_dialogue: list[str] = Field(default_factory=list)
    repeated_actions: list[str] = Field(default_factory=list)
    scene_similarity_flags: list[str] = Field(default_factory=list)
    revision_directives: list[str] = Field(default_factory=list)


class PackagingHypothesis(BaseModel):
    promise: str = Field(min_length=5)
    title_candidates: list[str] = Field(min_length=2)
    thumbnail_concepts: list[str] = Field(min_length=2)
    curiosity_gap: str = Field(min_length=3)
    must_deliver: list[str] = Field(default_factory=list)
    prohibited_claims: list[str] = Field(default_factory=list)


class ReleasePackage(BaseModel):
    final_title: str = Field(min_length=3)
    thumbnail_concept: str = Field(min_length=3)
    description: str = Field(min_length=3)
    chapters: list[str] = Field(default_factory=list)
    disclosure_notes: list[str] = Field(default_factory=list)
    originality_report: OriginalityReport | None = None
