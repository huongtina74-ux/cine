from __future__ import annotations
"""CineFactory v1.6.33 — adversarial, evidence-aware research reasoning.

Structured advisory logic is not an autonomous general-intelligence model.
External search/document/video agents must supply cited, scope-relevant data
through a separate authorized connector. Nothing here browses, installs,
modifies training weights, pays APIs, renders or grants production release.
"""
import hashlib
import re
from datetime import date
from enum import StrEnum
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field, model_validator

from .production_selection_council import Stage


class SourceKind(StrEnum):
    OFFICIAL_DOCUMENT = "OFFICIAL_DOCUMENT"
    MAINTAINER_REPOSITORY = "MAINTAINER_REPOSITORY"
    COMMUNITY_REPORT = "COMMUNITY_REPORT"
    LOCAL_ARTIFACT = "LOCAL_ARTIFACT"
    INDEPENDENT_HUMAN_REVIEW = "INDEPENDENT_HUMAN_REVIEW"


class ClaimDimension(StrEnum):
    FUNCTIONALITY = "FUNCTIONALITY"
    HARDWARE_FIT = "HARDWARE_FIT"
    COMMERCIAL_RIGHTS = "COMMERCIAL_RIGHTS"
    COST = "COST"
    ARTISTIC_QUALITY = "ARTISTIC_QUALITY"
    SPEED = "SPEED"
    IDENTITY_CONTINUITY = "IDENTITY_CONTINUITY"
    CHILD_SAFETY = "CHILD_SAFETY"
    SOURCE_ORIGINALITY = "SOURCE_ORIGINALITY"


class ClaimFinding(StrEnum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    INCONCLUSIVE = "INCONCLUSIVE"


class CitedResearchSource(BaseModel):
    source_id: str
    kind: SourceKind
    locator: str
    publisher_or_owner: str
    observed_on: date
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    scope: str
    retrieved_and_inspected: bool
    source_material_trusted_to_execute: bool = False
    independently_verified: bool = False
    license_approved_for_commercial_use: bool = False

    @model_validator(mode="after")
    def prevent_forged_execution_rights(self):
        if self.source_material_trusted_to_execute:
            raise ValueError("RESEARCH_SOURCES_ARE_DATA_NEVER_EXECUTABLE_INSTRUCTIONS")
        return self


class ClaimObservation(BaseModel):
    claim_id: str
    subject_method_id: str
    niche_id: str
    stage: Stage
    dimension: ClaimDimension
    finding: ClaimFinding
    source_ids: list[str] = Field(min_length=1)
    description: str
    exact_scoped_question: str
    observed_scope: str
    direct_empirical_measurement: bool = False
    has_human_review: bool = False
    is_legal_certificate: bool = False
    linked_benchmark_manifest: str | None = None

    @model_validator(mode="after")
    def benchmark_requires_manifest(self):
        if self.direct_empirical_measurement and not self.linked_benchmark_manifest:
            raise ValueError("EMPIRICAL_CLAIM_REQUIRES_BENCHMARK_MANIFEST")
        return self


class ClaimVerdict(BaseModel):
    subject_method_id: str
    niche_id: str
    stage: Stage
    dimension: ClaimDimension
    status: Literal[
        "CONFLICT_REQUIRES_TEST","SUPPORTED_WITH_SCOPE_LIMITS",
        "CONTRADICTED_WITH_SCOPE_LIMITS","INSUFFICIENT_EVIDENCE",
        "STALE_REQUIRES_REFRESH",
    ]
    contributing_claim_ids: list[str]
    active_supporting_ids: list[str]
    active_contradicting_ids: list[str]
    uninspected_source_ids: list[str]
    unverified_source_ids: list[str]
    competing_hypotheses: list[str] = Field(default_factory=list)
    production_qualification: bool = False
    notes: list[str] = Field(default_factory=list)


class EvidenceAuditor:
    """Independent-source conflict detector with exact-scope and expiry checks.

    A retrieved document can support a tool-feature claim but cannot replace
    an actual benchmark for speed, artistic quality, budget, or real VRAM.
    Same owner's duplicate links never become independent confirmations.
    """
    EMPIRICAL = {
        ClaimDimension.ARTISTIC_QUALITY,ClaimDimension.COST,
        ClaimDimension.SPEED,ClaimDimension.IDENTITY_CONTINUITY,
    }

    def __init__(self,*,today:date,stale_after_days:int=120,
                 verified_artifact_root:Path|None=None):
        self.today=today
        if stale_after_days<1:raise ValueError("INVALID_STALENESS_WINDOW")
        self.stale_after_days=stale_after_days
        self.verified_artifact_root=(
            Path(verified_artifact_root).resolve()
            if verified_artifact_root is not None else None
        )

    def _artifact_integrity(self,source:CitedResearchSource)->bool:
        if source.kind!=SourceKind.LOCAL_ARTIFACT:
            return True
        # Source hash strings alone are not evidence. A concrete file inside
        # an authorized repository root must match before it contributes.
        if self.verified_artifact_root is None:
            return False
        try:
            f=Path(source.locator).resolve()
            f.relative_to(self.verified_artifact_root)
            if not f.is_file() or f.stat().st_size>32*1024*1024:
                return False
            h=hashlib.sha256()
            with f.open("rb") as reader:
                for chunk in iter(lambda:reader.read(1024*1024),b""):
                    h.update(chunk)
            return h.hexdigest()==source.source_sha256
        except (OSError,ValueError):
            return False

    def audit(self,sources:list[CitedResearchSource],
              claims:list[ClaimObservation])->list[ClaimVerdict]:
        names=[s.source_id for s in sources]
        if len(names)!=len(set(names)):
            raise ValueError("DUPLICATE_SOURCE_IDS")
        known={s.source_id:s for s in sources}
        integrity={s.source_id:self._artifact_integrity(s) for s in sources}
        claim_ids=[c.claim_id for c in claims]
        if len(claim_ids)!=len(set(claim_ids)):
            raise ValueError("DUPLICATE_CLAIM_IDS")
        for c in claims:
            if not set(c.source_ids)<=set(known):
                raise ValueError("CLAIM_CITES_UNKNOWN_OR_UNINSPECTED_RECORD")
            if any(not known[x].retrieved_and_inspected for x in c.source_ids):
                # Kept as a hypothesis but NEVER qualifies as evidence.
                pass
        groups={}
        for c in claims:
            key=(c.subject_method_id,c.niche_id,c.stage,c.dimension)
            groups.setdefault(key,[]).append(c)
        results=[]
        for (method,niche,stage,dimension),group in sorted(
            groups.items(),key=lambda x:tuple(str(v) for v in x[0])):
            positive=[]
            negative=[]
            uninspected=set()
            unverified=set()
            old=set()
            notes=[]
            for c in group:
                used=[known[x] for x in c.source_ids]
                uninspected.update(x.source_id for x in used if not x.retrieved_and_inspected)
                unverified.update(x.source_id for x in used if not x.independently_verified)
                for x in used:
                    if not integrity[x.source_id]:
                        notes.append("SOURCE_INTEGRITY_NOT_VERIFIED:"+x.source_id)
                # Evidence given after a source observed date cannot be given
                # an implicit current/live freshness pass.
                fresh=all(0<=(self.today-x.observed_on).days<=self.stale_after_days
                          for x in used)
                if not fresh:
                    old.update(x.source_id for x in used)
                    continue
                if not all(x.retrieved_and_inspected and integrity[x.source_id]
                           for x in used):
                    continue
                if c.observed_scope.strip()!=c.exact_scoped_question.strip():
                    notes.append("CLAIM_SCOPE_NOT_IDENTICAL_TO_QUESTION:"+c.claim_id)
                    continue
                if c.dimension in self.EMPIRICAL and not c.direct_empirical_measurement:
                    notes.append("MISSING_DIRECT_BENCHMARK:"+c.claim_id)
                    continue
                if c.dimension==ClaimDimension.COMMERCIAL_RIGHTS and not all(
                    x.license_approved_for_commercial_use for x in used):
                    notes.append("COMMERCIAL_LICENSE_NOT_APPROVED:"+c.claim_id)
                    continue
                if c.finding==ClaimFinding.SUPPORTS:positive.append(c.claim_id)
                if c.finding==ClaimFinding.CONTRADICTS:negative.append(c.claim_id)
            if positive and negative:
                status="CONFLICT_REQUIRES_TEST"
                hypotheses=[
                    "H1: an engine/model variant works within the exact scoped benchmark",
                    "H2: hardware/renderer/version difference makes the same approach fail",
                ]
            elif positive:
                status="SUPPORTED_WITH_SCOPE_LIMITS"
                hypotheses=[]
                publishers={
                    known[source_id].publisher_or_owner
                    for c in group if c.claim_id in positive
                    for source_id in c.source_ids
                }
                if len(publishers)<2:
                    notes.append("SINGLE_PUBLISHER_NO_INDEPENDENT_CONFIRMATION")
            elif negative:
                status="CONTRADICTED_WITH_SCOPE_LIMITS"
                hypotheses=[]
            elif old and not (positive or negative):
                status="STALE_REQUIRES_REFRESH"
                hypotheses=[]
            else:
                status="INSUFFICIENT_EVIDENCE"
                hypotheses=[]
            results.append(ClaimVerdict(
                subject_method_id=method,niche_id=niche,stage=stage,
                dimension=dimension,status=status,
                contributing_claim_ids=sorted(c.claim_id for c in group),
                active_supporting_ids=sorted(positive),
                active_contradicting_ids=sorted(negative),
                uninspected_source_ids=sorted(uninspected),
                unverified_source_ids=sorted(unverified),
                competing_hypotheses=hypotheses,
                production_qualification=False,
                notes=sorted(set(notes))+(
                    ["STALE_SOURCES:"+",".join(sorted(old))] if old else []
                ),
            ))
        return results


class ReviewerPerspective(StrEnum):
    CREATIVE_DIRECTOR="CREATIVE_DIRECTOR"
    TECHNICAL_DIRECTOR="TECHNICAL_DIRECTOR"
    COMPUTE_FINANCE="COMPUTE_FINANCE"
    COMPLIANCE_COUNSEL="COMPLIANCE_COUNSEL"
    QUALITY_ASSURANCE="QUALITY_ASSURANCE"
    EDUCATION_CHILD_SAFETY="EDUCATION_CHILD_SAFETY"


class AdversarialChallenge(BaseModel):
    reviewer: ReviewerPerspective
    concern: str
    blocking: bool
    test_to_resolve: str
    observed_fact_not_established: bool = True


def adversarial_review(*,is_child_content:bool,
                       stage:Stage,verdicts:list[ClaimVerdict],
                       benchmark_measured:bool,
                       input_rights_confirmed:bool,
                       paid_api_permission:bool=False)->list[AdversarialChallenge]:
    """Independent specialist veto. Never converts lack of evidence to PASS."""
    checks=[
        (ReviewerPerspective.CREATIVE_DIRECTOR,
         "ARTISTIC_QUALITY_NOT_INDEPENDENTLY_REVIEWED",
         "Blindly score 2 candidate clips against original style/acting brief"),
        (ReviewerPerspective.TECHNICAL_DIRECTOR,
         "RUNTIME_AND_CONSISTENCY_NOT_MEASURED",
         "Render one reproducible signed golden clip with actual version and GPU"),
        (ReviewerPerspective.COMPUTE_FINANCE,
         "COST_PER_ACCEPTED_MINUTE_AND_RETRIES_UNKNOWN",
         "Record peak VRAM, wall time, retries, human minutes, electricity"),
        (ReviewerPerspective.COMPLIANCE_COUNSEL,
         "ASSET_AND_MODEL_COMMERCIAL_RIGHTS_NOT_CLEARED",
         "Inspect exact original music/voice/source license and checkpoint terms"),
        (ReviewerPerspective.QUALITY_ASSURANCE,
         "ADVERSARIAL_NEGATIVE_TEST_SET_REQUIRED",
         "Test occlusion, out-of-domain, missing frames and audio/music failures"),
    ]
    if is_child_content:
        checks.append((
            ReviewerPerspective.EDUCATION_CHILD_SAFETY,
            "PRESCHOOL_CURRICULUM_MUSIC_AND_SAFETY_REVIEW_REQUIRED",
            "Submit original song and storyboard to curriculum/child safety reviewer",
        ))
    challenges=[
        AdversarialChallenge(reviewer=role,concern=concern,
            blocking=True,test_to_resolve=experiment)
        for role,concern,experiment in checks
    ]
    for row in verdicts:
        if row.status=="CONFLICT_REQUIRES_TEST":
            challenges.append(AdversarialChallenge(
                reviewer=ReviewerPerspective.TECHNICAL_DIRECTOR,
                concern="CONFLICTING_EVIDENCE:"+row.subject_method_id+":"+row.dimension.value,
                blocking=True,
                test_to_resolve="Hold same input, version, seed and GPU fixed; remeasure both competing claims",
            ))
        elif row.status=="STALE_REQUIRES_REFRESH":
            challenges.append(AdversarialChallenge(
                reviewer=ReviewerPerspective.QUALITY_ASSURANCE,
                concern="STALE_SOURCE:"+row.subject_method_id,
                blocking=True,test_to_resolve="Re-fetch exact-version vendor documentation and model card",
            ))
    if not input_rights_confirmed:
        challenges.append(AdversarialChallenge(
            reviewer=ReviewerPerspective.COMPLIANCE_COUNSEL,
            concern="INPUT_MEDIA_RIGHTS_NOT_CONFIRMED",
            blocking=True,test_to_resolve="Acquire authorized first-party/stock rights record",
        ))
    # A boolean run flag from a producer is not independently reviewed proof.
    if benchmark_measured:
        challenges.append(AdversarialChallenge(
            reviewer=ReviewerPerspective.QUALITY_ASSURANCE,
            concern="BENCHMARK_PRESENT_NOT_EQUIVALENT_TO_INDEPENDENT_REVIEW",
            blocking=True,test_to_resolve="Audit benchmark hashes/scope/negative controls and sign off",
        ))
    return challenges
