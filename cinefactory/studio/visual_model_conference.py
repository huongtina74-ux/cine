from __future__ import annotations

from enum import StrEnum
from typing import Iterable

from pydantic import BaseModel, Field


class VisualModality(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"


class VisualObjective(StrEnum):
    ASSET_IMAGE = "ASSET_IMAGE"
    STORYBOARD_KEYFRAME = "STORYBOARD_KEYFRAME"
    IMAGE_EDIT = "IMAGE_EDIT"
    GENERATIVE_VIDEO = "GENERATIVE_VIDEO"
    HERO_CINEMATIC = "HERO_CINEMATIC"
    CHARACTER_MOTION = "CHARACTER_MOTION"
    AUDIO_DRIVEN_PERFORMANCE = "AUDIO_DRIVEN_PERFORMANCE"


class VisualEngineFamily(StrEnum):
    DIFFUSION_IMAGE = "DIFFUSION_IMAGE"
    WAN = "WAN"
    LTX = "LTX"
    CLOUD_VIDEO = "CLOUD_VIDEO"
class VisualLicenseState(StrEnum):
    COMMERCIAL_SAFE = "COMMERCIAL_SAFE"
    CONDITIONAL = "CONDITIONAL"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class VisualModelCandidate(BaseModel):
    model_id: str
    family: VisualEngineFamily
    modalities: set[VisualModality]
    supported_objectives: set[VisualObjective]
    executable: bool = False
    production_qualified: bool = False
    local: bool = True
    paid: bool = False
    license_state: VisualLicenseState = VisualLicenseState.UNKNOWN
    quality_score: float = Field(ge=0.0, le=1.0)
    speed_score: float = Field(ge=0.0, le=1.0)
    identity_score: float = Field(ge=0.0, le=1.0)
    motion_score: float = Field(default=0.0, ge=0.0, le=1.0)
    control_score: float = Field(ge=0.0, le=1.0)
    text_score: float = Field(default=0.0, ge=0.0, le=1.0)
    vram_gb: float | None = Field(default=None, ge=0.0)
    vram_verified: bool = True
    supports_reference: bool = False
    supports_audio_drive: bool = False
    estimated_cost_per_second_usd: float | None = Field(default=None, ge=0.0)
    notes: list[str] = Field(default_factory=list)


class VisualModelRequest(BaseModel):
    request_id: str
    modality: VisualModality
    objective: VisualObjective
    scene_id: str | None = None
    min_quality: float = Field(default=0.70, ge=0.0, le=1.0)
    max_vram_gb: float | None = Field(default=12.0, ge=0.0)
    require_commercial_safe: bool = True
    require_vram_verified: bool = True
    allow_cloud: bool = False
    allow_paid: bool = False
    require_reference: bool = False
    require_audio_drive: bool = False
    max_cost_usd: float | None = Field(default=None, ge=0.0)
    duration_seconds: float = Field(default=0.0, ge=0.0)


class VisualCandidateAssessment(BaseModel):
    model_id: str
    eligible: bool
    score: float = 0.0
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class VisualModelDecision(BaseModel):
    request_id: str
    scene_id: str | None = None
    objective: VisualObjective
    primary_model_id: str | None = None
    fallback_model_ids: list[str] = Field(default_factory=list)
    blocked: bool = True
    assessments: list[VisualCandidateAssessment] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class VisualModelConferenceReport(BaseModel):
    project_id: str
    decisions: list[VisualModelDecision] = Field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(item.blocked for item in self.decisions)


class VisualModelConference:
    """Per-job model routing; never treats model existence as execution readiness."""

    def __init__(self, candidates: Iterable[VisualModelCandidate]) -> None:
        self.candidates = list(candidates)

    @staticmethod
    def _score(
        request: VisualModelRequest,
        candidate: VisualModelCandidate,
    ) -> float:
        if request.objective in {
            VisualObjective.ASSET_IMAGE,
            VisualObjective.STORYBOARD_KEYFRAME,
            VisualObjective.IMAGE_EDIT,
        }:
            score = (
                0.36 * candidate.quality_score
                + 0.25 * candidate.identity_score
                + 0.20 * candidate.control_score
                + 0.09 * candidate.text_score
                + 0.10 * candidate.speed_score
            )
        elif request.objective in {
            VisualObjective.CHARACTER_MOTION,
            VisualObjective.AUDIO_DRIVEN_PERFORMANCE,
        }:
            score = (
                0.31 * candidate.quality_score
                + 0.27 * candidate.identity_score
                + 0.22 * candidate.motion_score
                + 0.15 * candidate.control_score
                + 0.05 * candidate.speed_score
            )
        else:
            score = (
                0.39 * candidate.quality_score
                + 0.23 * candidate.motion_score
                + 0.16 * candidate.identity_score
                + 0.12 * candidate.control_score
                + 0.10 * candidate.speed_score
            )
        return round(score, 4)

    def assess(
        self,
        request: VisualModelRequest,
        candidate: VisualModelCandidate,
    ) -> VisualCandidateAssessment:
        blockers: list[str] = []
        warnings: list[str] = []

        if request.modality not in candidate.modalities:
            blockers.append("MODALITY_UNSUPPORTED")
        if request.objective not in candidate.supported_objectives:
            blockers.append("OBJECTIVE_UNSUPPORTED")
        if not candidate.executable:
            blockers.append("MODEL_NOT_EXECUTABLE")
        if not candidate.production_qualified:
            blockers.append("MODEL_NOT_PRODUCTION_QUALIFIED")
        if candidate.quality_score < request.min_quality:
            blockers.append("QUALITY_GATE_FAILED")

        if request.require_commercial_safe:
            if candidate.license_state is VisualLicenseState.RESTRICTED:
                blockers.append("COMMERCIAL_LICENSE_RESTRICTED")
            elif candidate.license_state is VisualLicenseState.UNKNOWN:
                blockers.append("COMMERCIAL_LICENSE_UNVERIFIED")
            elif candidate.license_state is VisualLicenseState.CONDITIONAL:
                blockers.append("COMMERCIAL_LICENSE_CONDITIONAL")

        if not candidate.local and not request.allow_cloud:
            blockers.append("CLOUD_NOT_ALLOWED")
        if candidate.paid and not request.allow_paid:
            blockers.append("PAID_BACKEND_NOT_ALLOWED")
        if request.require_reference and not candidate.supports_reference:
            blockers.append("REFERENCE_CONDITIONING_REQUIRED")
        if request.require_audio_drive and not candidate.supports_audio_drive:
            blockers.append("AUDIO_DRIVE_REQUIRED")

        if request.require_vram_verified and candidate.local:
            if not candidate.vram_verified or candidate.vram_gb is None:
                blockers.append("VRAM_UNVERIFIED")
        if (
            candidate.local
            and request.max_vram_gb is not None
            and candidate.vram_gb is not None
            and candidate.vram_gb > request.max_vram_gb
        ):
            blockers.append("VRAM_BUDGET_EXCEEDED")

        cost = None
        if candidate.estimated_cost_per_second_usd is not None:
            cost = (
                candidate.estimated_cost_per_second_usd
                * request.duration_seconds
            )
            if request.max_cost_usd is not None and cost > request.max_cost_usd:
                blockers.append("COST_BUDGET_EXCEEDED")
            warnings.append(f"estimated_cost_usd={cost:.4f}")

        reasons = [
            f"quality={candidate.quality_score:.2f}",
            f"speed={candidate.speed_score:.2f}",
            f"identity={candidate.identity_score:.2f}",
            f"motion={candidate.motion_score:.2f}",
            f"license={candidate.license_state.value}",
            f"local={candidate.local}",
        ]
        if candidate.vram_gb is not None:
            reasons.append(f"vram_gb={candidate.vram_gb:.2f}")
        reasons.extend(candidate.notes)
        eligible = not blockers
        return VisualCandidateAssessment(
            model_id=candidate.model_id,
            eligible=eligible,
            score=self._score(request, candidate) if eligible else 0.0,
            blockers=blockers,
            warnings=warnings,
            reasons=reasons,
        )

    def deliberate(self, request: VisualModelRequest) -> VisualModelDecision:
        assessments = [
            self.assess(request, candidate)
            for candidate in self.candidates
        ]
        eligible = sorted(
            (item for item in assessments if item.eligible),
            key=lambda item: (item.score, item.model_id),
            reverse=True,
        )
        if not eligible:
            return VisualModelDecision(
                request_id=request.request_id,
                scene_id=request.scene_id,
                objective=request.objective,
                blocked=True,
                assessments=assessments,
                reasons=["NO_VISUAL_MODEL_PASSED_ALL_GATES"],
            )
        primary = eligible[0]
        return VisualModelDecision(
            request_id=request.request_id,
            scene_id=request.scene_id,
            objective=request.objective,
            primary_model_id=primary.model_id,
            fallback_model_ids=[
                item.model_id for item in eligible[1:3]
            ],
            blocked=False,
            assessments=assessments,
            reasons=[
                f"selected={primary.model_id}",
                f"score={primary.score:.4f}",
                "fallbacks passed the same hard gates",
            ],
        )

    def run(
        self,
        project_id: str,
        requests: Iterable[VisualModelRequest],
    ) -> VisualModelConferenceReport:
        return VisualModelConferenceReport(
            project_id=project_id,
            decisions=[self.deliberate(item) for item in requests],
        )


def default_visual_model_candidates(
    *,
    executable_model_ids: set[str] | None = None,
    qualified_model_ids: set[str] | None = None,
    cloud_enabled: bool = False,
) -> list[VisualModelCandidate]:
    executable = set(executable_model_ids or set())
    qualified = set(qualified_model_ids or set())

    def ready(model_id: str) -> tuple[bool, bool]:
        return model_id in executable, model_id in qualified

    image_jobs = {
        VisualObjective.ASSET_IMAGE,
        VisualObjective.STORYBOARD_KEYFRAME,
        VisualObjective.IMAGE_EDIT,
    }
    video_jobs = {
        VisualObjective.GENERATIVE_VIDEO,
        VisualObjective.HERO_CINEMATIC,
    }
    rows: list[VisualModelCandidate] = []

    is_exec, is_qualified = ready("flux2.klein.4b")
    rows.append(VisualModelCandidate(
        model_id="flux2.klein.4b",
        family=VisualEngineFamily.DIFFUSION_IMAGE,
        modalities={VisualModality.IMAGE},
        supported_objectives=image_jobs,
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.COMMERCIAL_SAFE,
        quality_score=0.91, speed_score=0.86,
        identity_score=0.90, control_score=0.91, text_score=0.86,
        vram_gb=9.0, vram_verified=False, supports_reference=True,
        notes=["preferred local image candidate; benchmark exact checkpoint before qualification"],
    ))

    is_exec, is_qualified = ready("qwen-image-2.1")
    rows.append(VisualModelCandidate(
        model_id="qwen-image-2.1",
        family=VisualEngineFamily.DIFFUSION_IMAGE,
        modalities={VisualModality.IMAGE},
        supported_objectives=image_jobs,
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.RESTRICTED,
        quality_score=0.94, speed_score=0.78,
        identity_score=0.94, control_score=0.95, text_score=0.94,
        vram_gb=None, vram_verified=False, supports_reference=True,
        notes=["Qwen Research License: commercial use needs separate license"],
    ))
    is_exec, is_qualified = ready("wan2.2.ti2v.5b")
    rows.append(VisualModelCandidate(
        model_id="wan2.2.ti2v.5b",
        family=VisualEngineFamily.WAN,
        modalities={VisualModality.VIDEO},
        supported_objectives=video_jobs,
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.COMMERCIAL_SAFE,
        quality_score=0.87, speed_score=0.78,
        identity_score=0.78, motion_score=0.86, control_score=0.84,
        vram_gb=12.0, vram_verified=False, supports_reference=True,
        notes=["local video default candidate; exact ComfyUI workflow must be benchmarked"],
    ))

    is_exec, is_qualified = ready("wan2.2.a14b.gguf")
    rows.append(VisualModelCandidate(
        model_id="wan2.2.a14b.gguf",
        family=VisualEngineFamily.WAN,
        modalities={VisualModality.VIDEO},
        supported_objectives={VisualObjective.HERO_CINEMATIC, VisualObjective.GENERATIVE_VIDEO},
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.COMMERCIAL_SAFE,
        quality_score=0.94, speed_score=0.48,
        identity_score=0.84, motion_score=0.93, control_score=0.89,
        vram_gb=None, vram_verified=False, supports_reference=True,
        notes=["quality lane candidate; quantization/VRAM must be measured on RTX 3060"],
    ))
    is_exec, is_qualified = ready("wan.animate2")
    rows.append(VisualModelCandidate(
        model_id="wan.animate2",
        family=VisualEngineFamily.WAN,
        modalities={VisualModality.VIDEO},
        supported_objectives={VisualObjective.CHARACTER_MOTION},
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.COMMERCIAL_SAFE,
        quality_score=0.92, speed_score=0.50,
        identity_score=0.95, motion_score=0.94, control_score=0.92,
        vram_gb=None, vram_verified=False, supports_reference=True,
        notes=["character-motion specialist; requires offload/quant benchmark"],
    ))

    is_exec, is_qualified = ready("wan2.2.s2v.14b")
    rows.append(VisualModelCandidate(
        model_id="wan2.2.s2v.14b",
        family=VisualEngineFamily.WAN,
        modalities={VisualModality.VIDEO},
        supported_objectives={VisualObjective.AUDIO_DRIVEN_PERFORMANCE},
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.COMMERCIAL_SAFE,
        quality_score=0.91, speed_score=0.45,
        identity_score=0.91, motion_score=0.91, control_score=0.90,
        vram_gb=None, vram_verified=False, supports_reference=True,
        supports_audio_drive=True,
        notes=["audio-driven performance specialist; quant/offload required on 12GB"],
    ))
    is_exec, is_qualified = ready("ltx2.5.fast")
    rows.append(VisualModelCandidate(
        model_id="ltx2.5.fast",
        family=VisualEngineFamily.LTX,
        modalities={VisualModality.VIDEO},
        supported_objectives=video_jobs,
        executable=is_exec,
        production_qualified=is_qualified,
        license_state=VisualLicenseState.CONDITIONAL,
        quality_score=0.89, speed_score=0.91,
        identity_score=0.81, motion_score=0.88, control_score=0.86,
        vram_gb=None, vram_verified=False, supports_reference=True,
        notes=["commercial terms are conditional; require project/entity license review"],
    ))

    rows.append(VisualModelCandidate(
        model_id="wan2.7.cloud",
        family=VisualEngineFamily.CLOUD_VIDEO,
        modalities={VisualModality.VIDEO},
        supported_objectives=video_jobs,
        executable=cloud_enabled,
        production_qualified=cloud_enabled,
        local=False, paid=True,
        license_state=VisualLicenseState.CONDITIONAL,
        quality_score=0.96, speed_score=0.82,
        identity_score=0.92, motion_score=0.95, control_score=0.95,
        supports_reference=True,
        estimated_cost_per_second_usd=0.15,
        notes=["cloud premium only; never selected when local-only or zero-cost policy is active"],
    ))
    return rows
