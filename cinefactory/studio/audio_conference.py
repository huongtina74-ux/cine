from __future__ import annotations

from enum import StrEnum
from typing import Iterable

from pydantic import BaseModel, Field


class AudioObjective(StrEnum):
    NARRATION = "NARRATION"
    CHARACTER_DIALOGUE = "CHARACTER_DIALOGUE"
    EXPRESSIVE_DIALOGUE = "EXPRESSIVE_DIALOGUE"
    VOICE_CLONE = "VOICE_CLONE"
    SPEECH_ENHANCEMENT = "SPEECH_ENHANCEMENT"
    SOURCE_SEPARATION = "SOURCE_SEPARATION"
    MIX_MASTER = "MIX_MASTER"


class AudioEngineFamily(StrEnum):
    TTS = "TTS"
    COSYVOICE = "COSYVOICE"
    AUK = "AUK"
    AUK_AUDIO_CPP = "AUK_AUDIO_CPP"
    FFMPEG = "FFMPEG"
    SEPARATION = "SEPARATION"


class AudioLicenseState(StrEnum):
    COMMERCIAL_SAFE = "COMMERCIAL_SAFE"
    USER_MANAGED = "USER_MANAGED"
    RESTRICTED = "RESTRICTED"
    UNKNOWN = "UNKNOWN"


class AudioEngineCandidate(BaseModel):
    engine_id: str
    family: AudioEngineFamily
    supported_objectives: set[AudioObjective]
    executable: bool = False
    production_qualified: bool = False
    local: bool = True
    license_state: AudioLicenseState = AudioLicenseState.UNKNOWN
    quality_score: float = Field(ge=0.0, le=1.0)
    speed_score: float = Field(ge=0.0, le=1.0)
    voice_consistency_score: float = Field(ge=0.0, le=1.0)
    control_score: float = Field(ge=0.0, le=1.0)
    vram_gb: float | None = Field(default=None, ge=0.0)
    vram_verified: bool = True
    requires_gpu: bool = False
    notes: list[str] = Field(default_factory=list)


class AudioConferenceRequest(BaseModel):
    job_id: str
    scene_id: str | None = None
    line_id: str | None = None
    speaker_id: str | None = None
    text: str | None = None
    objective: AudioObjective
    min_quality: float = Field(default=0.70, ge=0.0, le=1.0)
    max_vram_gb: float | None = Field(default=None, ge=0.0)
    require_commercial_safe: bool = True
    require_vram_verified: bool = True
    voice_reference: str | None = None


class AudioCandidateAssessment(BaseModel):
    engine_id: str
    eligible: bool
    score: float = 0.0
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class AudioConferenceDecision(BaseModel):
    job_id: str
    objective: AudioObjective
    primary_engine_id: str | None = None
    fallback_engine_ids: list[str] = Field(default_factory=list)
    blocked: bool = True
    assessments: list[AudioCandidateAssessment] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)


class AudioProductionConferenceReport(BaseModel):
    project_id: str
    decisions: list[AudioConferenceDecision] = Field(default_factory=list)

    @property
    def blocked(self) -> bool:
        return any(item.blocked for item in self.decisions)


class AudioProductionConference:
    """Fail-closed per-job audio routing with license/VRAM/quality gates."""

    def __init__(self, candidates: Iterable[AudioEngineCandidate]) -> None:
        self.candidates = list(candidates)

    @staticmethod
    def _score(candidate: AudioEngineCandidate) -> float:
        return round(
            0.42 * candidate.quality_score
            + 0.23 * candidate.voice_consistency_score
            + 0.20 * candidate.control_score
            + 0.10 * candidate.speed_score
            + 0.05 * (1.0 if candidate.local else 0.0),
            4,
        )

    def assess(
        self,
        request: AudioConferenceRequest,
        candidate: AudioEngineCandidate,
    ) -> AudioCandidateAssessment:
        blockers: list[str] = []
        warnings: list[str] = []
        reasons: list[str] = []

        if request.objective not in candidate.supported_objectives:
            blockers.append("OBJECTIVE_UNSUPPORTED")
        if not candidate.executable:
            blockers.append("ENGINE_NOT_EXECUTABLE")
        if not candidate.production_qualified:
            blockers.append("ENGINE_NOT_PRODUCTION_QUALIFIED")
        if candidate.quality_score < request.min_quality:
            blockers.append("QUALITY_GATE_FAILED")

        if request.require_commercial_safe:
            if candidate.license_state is AudioLicenseState.RESTRICTED:
                blockers.append("COMMERCIAL_LICENSE_RESTRICTED")
            elif candidate.license_state is AudioLicenseState.UNKNOWN:
                blockers.append("COMMERCIAL_LICENSE_UNVERIFIED")
            elif candidate.license_state is AudioLicenseState.USER_MANAGED:
                warnings.append("COMMERCIAL_LICENSE_USER_MANAGED")

        if candidate.requires_gpu and request.require_vram_verified:
            if not candidate.vram_verified or candidate.vram_gb is None:
                blockers.append("VRAM_UNVERIFIED")
        if (
            request.max_vram_gb is not None
            and candidate.vram_gb is not None
            and candidate.vram_gb > request.max_vram_gb
        ):
            blockers.append("VRAM_BUDGET_EXCEEDED")

        if request.objective is AudioObjective.VOICE_CLONE:
            if not request.voice_reference:
                blockers.append("VOICE_REFERENCE_REQUIRED")

        reasons.extend(
            [
                f"quality={candidate.quality_score:.2f}",
                f"speed={candidate.speed_score:.2f}",
                f"voice_consistency={candidate.voice_consistency_score:.2f}",
                f"license={candidate.license_state.value}",
            ]
        )
        if candidate.vram_gb is not None:
            reasons.append(f"vram_gb={candidate.vram_gb:.2f}")
        reasons.extend(candidate.notes)

        eligible = not blockers
        return AudioCandidateAssessment(
            engine_id=candidate.engine_id,
            eligible=eligible,
            score=self._score(candidate) if eligible else 0.0,
            blockers=blockers,
            warnings=warnings,
            reasons=reasons,
        )

    def deliberate(self, request: AudioConferenceRequest) -> AudioConferenceDecision:
        assessments = [
            self.assess(request, candidate)
            for candidate in self.candidates
        ]
        eligible = sorted(
            (item for item in assessments if item.eligible),
            key=lambda item: (item.score, item.engine_id),
            reverse=True,
        )
        if not eligible:
            return AudioConferenceDecision(
                job_id=request.job_id,
                objective=request.objective,
                blocked=True,
                assessments=assessments,
                reasons=["NO_AUDIO_ENGINE_PASSED_ALL_GATES"],
            )
        primary = eligible[0]
        return AudioConferenceDecision(
            job_id=request.job_id,
            objective=request.objective,
            primary_engine_id=primary.engine_id,
            fallback_engine_ids=[item.engine_id for item in eligible[1:3]],
            blocked=False,
            assessments=assessments,
            reasons=[
                f"selected={primary.engine_id}",
                f"score={primary.score:.4f}",
                "fallbacks are pre-approved by the same hard gates",
            ],
        )

    def run(
        self,
        project_id: str,
        requests: Iterable[AudioConferenceRequest],
    ) -> AudioProductionConferenceReport:
        return AudioProductionConferenceReport(
            project_id=project_id,
            decisions=[self.deliberate(item) for item in requests],
        )


def default_audio_engine_candidates(
    *,
    tts_mode: str = "none",
    has_tts_command: bool = False,
    cosyvoice_executable: bool = False,
    cosyvoice_qualified: bool = False,
    cosyvoice_vram_gb: float | None = None,
    cosyvoice_vram_verified: bool = False,
    ffmpeg_executable: bool = True,
) -> list[AudioEngineCandidate]:
    speech_basic = {
        AudioObjective.NARRATION,
        AudioObjective.CHARACTER_DIALOGUE,
        AudioObjective.EXPRESSIVE_DIALOGUE,
    }
    auk_tasks = speech_basic | {
        AudioObjective.VOICE_CLONE,
        AudioObjective.SPEECH_ENHANCEMENT,
        AudioObjective.SOURCE_SEPARATION,
    }
    candidates = [
        AudioEngineCandidate(
            engine_id="cosyvoice3.local",
            family=AudioEngineFamily.COSYVOICE,
            supported_objectives=speech_basic | {AudioObjective.VOICE_CLONE},
            executable=cosyvoice_executable,
            production_qualified=cosyvoice_qualified,
            license_state=AudioLicenseState.COMMERCIAL_SAFE,
            quality_score=0.91,
            speed_score=0.84,
            voice_consistency_score=0.92,
            control_score=0.89,
            vram_gb=cosyvoice_vram_gb,
            vram_verified=cosyvoice_vram_verified,
            requires_gpu=cosyvoice_vram_gb is not None,
            notes=["preferred local production voice candidate when qualified"],
        ),
        AudioEngineCandidate(
            engine_id="tts.command",
            family=AudioEngineFamily.TTS,
            supported_objectives=speech_basic,
            executable=tts_mode == "command" and has_tts_command,
            production_qualified=tts_mode == "command" and has_tts_command,
            license_state=AudioLicenseState.USER_MANAGED,
            quality_score=0.82,
            speed_score=0.88,
            voice_consistency_score=0.84,
            control_score=0.76,
            notes=["generic command provider; rights remain user-managed"],
        ),
        AudioEngineCandidate(
            engine_id="tts.espeak",
            family=AudioEngineFamily.TTS,
            supported_objectives=speech_basic,
            executable=tts_mode == "espeak",
            production_qualified=tts_mode == "espeak",
            license_state=AudioLicenseState.COMMERCIAL_SAFE,
            quality_score=0.42,
            speed_score=0.96,
            voice_consistency_score=0.78,
            control_score=0.48,
            notes=["diagnostic/local fallback; intentionally low quality score"],
        ),
        AudioEngineCandidate(
            engine_id="auk.pytorch.base",
            family=AudioEngineFamily.AUK,
            supported_objectives=auk_tasks,
            executable=False,
            production_qualified=False,
            license_state=AudioLicenseState.RESTRICTED,
            quality_score=0.94,
            speed_score=0.52,
            voice_consistency_score=0.93,
            control_score=0.95,
            vram_gb=16.98,
            vram_verified=True,
            requires_gpu=True,
            notes=["AuK MIT; current Qwen2.5-Omni-3B dependency is commercial-restricted"],
        ),
        AudioEngineCandidate(
            engine_id="auk.pytorch.flash",
            family=AudioEngineFamily.AUK,
            supported_objectives=auk_tasks,
            executable=False,
            production_qualified=False,
            license_state=AudioLicenseState.RESTRICTED,
            quality_score=0.90,
            speed_score=0.86,
            voice_consistency_score=0.90,
            control_score=0.90,
            vram_gb=16.98,
            vram_verified=True,
            requires_gpu=True,
            notes=["4-step AuK variant; official offload still exceeds 12GB budget"],
        ),
        AudioEngineCandidate(
            engine_id="auk.audio_cpp.flash",
            family=AudioEngineFamily.AUK_AUDIO_CPP,
            supported_objectives=auk_tasks,
            executable=False,
            production_qualified=False,
            license_state=AudioLicenseState.RESTRICTED,
            quality_score=0.88,
            speed_score=0.90,
            voice_consistency_score=0.88,
            control_score=0.87,
            vram_gb=None,
            vram_verified=False,
            requires_gpu=True,
            notes=["GGUF path is a benchmark candidate; 12GB parity/VRAM not yet qualified"],
        ),
        AudioEngineCandidate(
            engine_id="ffmpeg.audio",
            family=AudioEngineFamily.FFMPEG,
            supported_objectives={
                AudioObjective.SPEECH_ENHANCEMENT,
                AudioObjective.MIX_MASTER,
            },
            executable=ffmpeg_executable,
            production_qualified=ffmpeg_executable,
            license_state=AudioLicenseState.COMMERCIAL_SAFE,
            quality_score=0.80,
            speed_score=0.95,
            voice_consistency_score=1.0,
            control_score=0.92,
            notes=["deterministic filters/mix/master; not a speech generator"],
        ),
    ]
    return candidates
