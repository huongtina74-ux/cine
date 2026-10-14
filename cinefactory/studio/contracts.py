from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MediaPurpose(StrEnum):
    ENTERTAIN = "ENTERTAIN"
    INFORM = "INFORM"
    TEACH = "TEACH"
    PERSUADE = "PERSUADE"
    SELL = "SELL"
    DOCUMENT = "DOCUMENT"
    DEMONSTRATE = "DEMONSTRATE"
    ENGAGE = "ENGAGE"


class MediaFormat(StrEnum):
    NARRATIVE = "NARRATIVE"
    NARRATIVE_FILM = "NARRATIVE_FILM"
    ANIMATION = "ANIMATION"
    GAMEPLAY = "GAMEPLAY"
    DOCUMENTARY = "DOCUMENTARY"
    TUTORIAL = "TUTORIAL"
    EXPLAINER = "EXPLAINER"
    REVIEW = "REVIEW"
    COMMERCIAL = "COMMERCIAL"
    PODCAST = "PODCAST"
    INTERVIEW = "INTERVIEW"
    MUSIC_VIDEO = "MUSIC_VIDEO"
    SOCIAL_SHORT = "SOCIAL_SHORT"
    SHORT_FORM = "SHORT_FORM"
    SCREEN_DEMO = "SCREEN_DEMO"
    DATA_VISUALIZATION = "DATA_VISUALIZATION"
    HYBRID = "HYBRID"
class SegmentKind(StrEnum):
    NARRATIVE_SCENE = "NARRATIVE_SCENE"
    GAMEPLAY_BEAT = "GAMEPLAY_BEAT"
    DOCUMENTARY_CHAPTER = "DOCUMENTARY_CHAPTER"
    TUTORIAL_STEP = "TUTORIAL_STEP"
    EXPLAINER_CONCEPT = "EXPLAINER_CONCEPT"
    REVIEW_BLOCK = "REVIEW_BLOCK"
    AD_BEAT = "AD_BEAT"
    PODCAST_BLOCK = "PODCAST_BLOCK"
    INTERVIEW_TURN = "INTERVIEW_TURN"
    MUSIC_SECTION = "MUSIC_SECTION"
    SCREEN_DEMO = "SCREEN_DEMO"
    DATA_VISUALIZATION = "DATA_VISUALIZATION"
    LIVE_EVENT_BLOCK = "LIVE_EVENT_BLOCK"


class DepartmentId(StrEnum):
    STUDIO_MANAGEMENT = "STUDIO_MANAGEMENT"
    INTELLIGENCE = "INTELLIGENCE"
    EVIDENCE = "EVIDENCE"
    CREATIVE_STRATEGY = "CREATIVE_STRATEGY"
    PLANNING = "PLANNING"
    WRITERS_ROOM = "WRITERS_ROOM"
    SCRIPT_LOGIC = "SCRIPT_LOGIC"
    DIRECTION = "DIRECTION"
    PERFORMANCE = "PERFORMANCE"
    CINEMATOGRAPHY = "CINEMATOGRAPHY"
    PRODUCTION_DESIGN = "PRODUCTION_DESIGN"
    ASSETS = "ASSETS"
    TECHNICAL_DIRECTION = "TECHNICAL_DIRECTION"
    PRODUCTION = "PRODUCTION"
    GENERATIVE_MEDIA = "GENERATIVE_MEDIA"
    VFX = "VFX"
    EDITORIAL = "EDITORIAL"
    AUDIO = "AUDIO"
    COLOR = "COLOR"
    QC = "QC"
    RIGHTS = "RIGHTS"
    PACKAGING = "PACKAGING"
    ANALYTICS = "ANALYTICS"
    RND = "RND"
    RD_KNOWLEDGE = "RD_KNOWLEDGE"
    OPERATIONS = "OPERATIONS"
class ArtifactState(StrEnum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    LOCKED = "LOCKED"
    SUPERSEDED = "SUPERSEDED"
    REJECTED = "REJECTED"


class KnowledgeScope(StrEnum):
    PROJECT = "PROJECT"
    CHANNEL = "CHANNEL"
    NICHE = "NICHE"
    DOMAIN = "DOMAIN"
    STUDIO = "STUDIO"


class SkillStatus(StrEnum):
    DISCOVERED = "DISCOVERED"
    CANDIDATE = "CANDIDATE"
    EVALUATING = "EVALUATING"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    BLOCKED = "BLOCKED"


class CapabilityKind(StrEnum):
    OFFLINE_3D = "OFFLINE_3D"
    REALTIME_3D = "REALTIME_3D"
    GAME_RUNTIME = "GAME_RUNTIME"
    AI_IMAGE = "AI_IMAGE"
    AI_VIDEO = "AI_VIDEO"
    IMAGE_EDIT = "IMAGE_EDIT"
    DESIGN = "DESIGN"
    MOTION_GRAPHICS = "MOTION_GRAPHICS"
    COMPOSITING = "COMPOSITING"
    EDITORIAL = "EDITORIAL"
    SPEECH = "SPEECH"
    MUSIC = "MUSIC"
    SFX = "SFX"
    LIPSYNC = "LIPSYNC"
    SCREEN_CAPTURE = "SCREEN_CAPTURE"
    FOOTAGE = "FOOTAGE"
    WEB_RESEARCH = "WEB_RESEARCH"
    COLOR = "COLOR"
    QC = "QC"


class CapabilityStatus(StrEnum):
    EXECUTABLE = "EXECUTABLE"
    PLANNED = "PLANNED"
    BLOCKED = "BLOCKED"


class StudioOutputSpec(BaseModel):
    language: str = "vi"
    duration_seconds: int | None = Field(default=None, gt=0)
    platform: str = "youtube"


class StudioProject(BaseModel):
    project_id: str = Field(default_factory=lambda: f"STU_{uuid4().hex[:12]}")
    goal: str = Field(min_length=3)
    domain: str = "general"
    purpose: MediaPurpose = MediaPurpose.ENTERTAIN
    media_format: MediaFormat = MediaFormat.NARRATIVE_FILM
    output: StudioOutputSpec = Field(default_factory=StudioOutputSpec)
    requested_capabilities: set[CapabilityKind] = Field(default_factory=set)
    story_required: bool | None = None
    evidence_required: bool | None = None
    actual_gameplay_required: bool | None = None
    brand_compliance_required: bool | None = None

    @model_validator(mode="after")
    def infer_requirements(self) -> "StudioProject":
        if self.story_required is None:
            self.story_required = self.media_format in {
                MediaFormat.NARRATIVE,
                MediaFormat.NARRATIVE_FILM,
                MediaFormat.ANIMATION,
            }
        if self.evidence_required is None:
            self.evidence_required = self.media_format in {
                MediaFormat.DOCUMENTARY,
                MediaFormat.TUTORIAL,
                MediaFormat.EXPLAINER,
                MediaFormat.REVIEW,
                MediaFormat.DATA_VISUALIZATION,
            }
        if self.actual_gameplay_required is None:
            self.actual_gameplay_required = self.media_format is MediaFormat.GAMEPLAY
        if self.brand_compliance_required is None:
            self.brand_compliance_required = self.media_format is MediaFormat.COMMERCIAL
        return self


class ArtifactProvenance(BaseModel):
    producer: str
    source_refs: list[str] = Field(default_factory=list)
    tool_versions: dict[str, str] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class PlanningInputKind(StrEnum):
    COMPETITOR_VIDEO = "COMPETITOR_VIDEO"
    CHANNEL_RESEARCH = "CHANNEL_RESEARCH"
    REFERENCE_VIDEO = "REFERENCE_VIDEO"
    RESEARCH_REPORT = "RESEARCH_REPORT"
    USER_ASSET = "USER_ASSET"
    SCRIPT = "SCRIPT"
    SCRIPT_OUTLINE = "SCRIPT_OUTLINE"
    REFERENCE_SCRIPT = "REFERENCE_SCRIPT"


class PlanningInputRef(BaseModel):
    input_id: str = Field(default_factory=lambda: f"PIN_{uuid4().hex[:12]}")
    kind: PlanningInputKind
    uri: str | None = None
    title: str | None = None
    content: str | None = None
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_script_source(self) -> "PlanningInputRef":
        if self.kind in {
            PlanningInputKind.SCRIPT,
            PlanningInputKind.SCRIPT_OUTLINE,
            PlanningInputKind.REFERENCE_SCRIPT,
        }:
            inline = bool(
                (self.content or "").lstrip("\ufeff").strip()
            )
            legacy_inline = bool(
                str(self.metadata.get("content") or "")
                .lstrip("\ufeff")
                .strip()
            )
            quarantined = bool(
                self.kind is PlanningInputKind.REFERENCE_SCRIPT
                and self.metadata.get("quarantined") is True
                and (
                    self.metadata.get("content_sha256")
                    or self.metadata.get("quarantine_error")
                )
            )
            if not (
                inline
                or legacy_inline
                or self.uri
                or quarantined
            ):
                raise ValueError(
                    f"{self.kind.value} requires content or uri"
                )
        return self


class StudioProjectSpec(BaseModel):
    studio_project_id: str = Field(default_factory=lambda: f"STU_{uuid4().hex[:12]}")
    prompt: str = Field(min_length=3)
    language: str = "vi"
    domain: str = "generic"
    niche: str | None = None
    # Stable original channel/series/episode context; never a competitor's ID.
    channel_brand_id: str | None = None
    series_id: str | None = None
    episode_id: str | None = None
    minecraft_subniche: str | None = None
    reuse_series_characters: bool = False
    platform: str = "youtube"
    duration_seconds: int | None = Field(default=None, gt=0)
    autonomous: bool = True
    planning_inputs: list[PlanningInputRef] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)

    @model_validator(mode="after")
    def require_complete_channel_identity(self):
        if self.minecraft_subniche and self.niche != "minecraft":
            raise ValueError("MINECRAFT_SUBNICHE_REQUIRES_MINECRAFT_NICHE")
        if self.reuse_series_characters and not all((
            self.channel_brand_id,self.series_id,self.episode_id
        )):
            raise ValueError("EXPLICIT_SERIES_CONTEXT_REQUIRED_FOR_CHARACTER_REUSE")
        if (self.series_id is not None or self.episode_id is not None) and not all((
            self.channel_brand_id,self.series_id,self.episode_id
        )):
            raise ValueError("CHANNEL_SERIES_EPISODE_MUST_BE_BOUND_TOGETHER")
        return self


class MediaProductSpec(BaseModel):
    purpose: MediaPurpose
    format: MediaFormat
    target_audience: str | None = None
    evidence_required: bool = False
    actual_gameplay_required: bool = False
    brand_compliance_required: bool = False
    story_required: bool = False
    source_modalities: list[str] = Field(default_factory=list)
    output_profile: str = "YOUTUBE_LONGFORM"
    constraints: dict[str, Any] = Field(default_factory=dict)


class MediaSegment(BaseModel):
    segment_id: str
    kind: SegmentKind
    purpose: str = Field(min_length=2)
    order: int = Field(ge=0)
    duration_seconds: float | None = Field(default=None, gt=0)
    dependencies: list[str] = Field(default_factory=list)
    capability_requirements: list[CapabilityKind] = Field(default_factory=list)
    creative_intent: dict[str, Any] = Field(default_factory=dict)
    execution_constraints: dict[str, Any] = Field(default_factory=dict)
class DepartmentSpec(BaseModel):
    department_id: DepartmentId
    mission: str
    knowledge_domains: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    reads: list[str] = Field(default_factory=list)
    writes: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    qc_gates: list[str] = Field(default_factory=list)
    learning_scope: list[KnowledgeScope] = Field(default_factory=list)

    @property
    def craft_skills(self) -> list[str]:
        return self.skills

    @property
    def quality_gates(self) -> list[str]:
        return self.qc_gates


class StudioArtifact(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"SART_{uuid4().hex[:12]}")
    project_id: str
    artifact_type: str
    owner: DepartmentId
    version: int = Field(ge=1)
    state: ArtifactState = ArtifactState.DRAFT
    content_hash: str
    upstream_artifact_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    locked_at: datetime | None = None


class ChangeRequest(BaseModel):
    change_id: str = Field(default_factory=lambda: f"CHG_{uuid4().hex[:12]}")
    project_id: str
    requester: DepartmentId
    owner: DepartmentId
    artifact_type: str
    reason: str = Field(min_length=3)
    requested_changes: list[str] = Field(min_length=1)
    status: str = "OPEN"
    created_at: datetime = Field(default_factory=utcnow)
class SkillManifest(BaseModel):
    skill_id: str
    version: str = "1"
    owner: DepartmentId
    status: SkillStatus = SkillStatus.DISCOVERED
    craft_domain: str = "general"
    description: str = ""
    code_execution_allowed: bool = False
    tool_binding: str | None = None
    source_type: str = "INTERNAL"
    source_uri: str | None = None
    source_version: str | None = None
    knowledge_scope: KnowledgeScope = KnowledgeScope.STUDIO
    commercial_safe: bool | None = None
    security_reviewed: bool = False
    required_evals: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SkillEvaluation(BaseModel):
    skill_id: str
    version: str = "1"
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    eval_id: str = "default"
    findings: list[str] = Field(default_factory=list)
    regression_passed: bool = False


class CapabilityOffer(BaseModel):
    capability_id: str
    kind: CapabilityKind
    provider: str
    executable: bool = False
    local: bool = True
    commercial_safe: bool | None = None
    deterministic: float = Field(default=0.5, ge=0.0, le=1.0)
    quality: float = Field(default=0.5, ge=0.0, le=1.0)
    speed: float = Field(default=0.5, ge=0.0, le=1.0)
    vram_gb: float | None = Field(default=None, ge=0)
    cost_class: str = "FREE_LOCAL"
    tags: set[str] = Field(default_factory=set)
class CapabilityRequirement(BaseModel):
    kind: CapabilityKind
    local_only: bool = True
    commercial_safe: bool = True
    deterministic_min: float = Field(default=0.0, ge=0.0, le=1.0)
    quality_min: float = Field(default=0.0, ge=0.0, le=1.0)
    max_vram_gb: float | None = Field(default=None, gt=0)
    required_tags: set[str] = Field(default_factory=set)


class RoutingDecision(BaseModel):
    requirement: CapabilityRequirement
    selected_capability_id: str | None = None
    executable: bool = False
    score: float = 0.0
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ProblemHypothesis(BaseModel):
    hypothesis_id: str
    cause: str
    evidence: list[str] = Field(default_factory=list)
    test: str
    expected_result: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ProblemRecord(BaseModel):
    problem_code: str
    owner: DepartmentId
    symptoms: list[str] = Field(min_length=1)
    hypotheses: list[ProblemHypothesis] = Field(default_factory=list)
    root_cause: str | None = None
    verified_repairs: list[str] = Field(default_factory=list)
    regression_tests: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
class LearningCandidate(BaseModel):
    candidate_id: str = Field(default_factory=lambda: f"LRN_{uuid4().hex[:12]}")
    observation: str
    hypothesis: str
    scope: KnowledgeScope
    evidence_refs: list[str] = Field(default_factory=list)
    proposed_rule: str | None = None
    proposed_skill_id: str | None = None
    sandbox_passed: bool = False
    regression_passed: bool = False
    promoted: bool = False

    @model_validator(mode="after")
    def promotion_requires_proof(self) -> "LearningCandidate":
        if self.promoted and not (self.sandbox_passed and self.regression_passed):
            raise ValueError("learning candidate cannot be promoted without sandbox and regression pass")
        return self
