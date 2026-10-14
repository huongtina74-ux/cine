from __future__ import annotations

from pydantic import BaseModel, Field

from .contracts import MediaFormat


class QualityProfile(BaseModel):
    format: MediaFormat
    gates: list[str] = Field(default_factory=list)


FORMAT_GATES: dict[MediaFormat, list[str]] = {
    MediaFormat.NARRATIVE: [
        "STORY_LOGIC", "CHARACTER_IDENTITY", "PERFORMANCE", "CONTINUITY",
        "CAMERA_LANGUAGE", "SCREEN_DIRECTION", "PACING", "AUDIO", "COLOR", "RIGHTS",
    ],
    MediaFormat.NARRATIVE_FILM: [
        "STORY_LOGIC", "CHARACTER_IDENTITY", "PERFORMANCE", "CONTINUITY",
        "CAMERA_LANGUAGE", "SCREEN_DIRECTION", "PACING", "AUDIO", "COLOR", "RIGHTS",
    ],
    MediaFormat.ANIMATION: [
        "STORY_LOGIC", "CHARACTER_IDENTITY", "PERFORMANCE", "CONTINUITY",
        "CAMERA_LANGUAGE", "SCREEN_DIRECTION", "PACING", "AUDIO", "COLOR", "RIGHTS",
    ],
    MediaFormat.GAMEPLAY: [
        "GAMEPLAY_AUTHENTICITY", "OBJECTIVE_PROGRESS", "DEAD_TIME",
        "CAPTURE_QUALITY", "PACING", "AUDIO", "RIGHTS",
    ],
    MediaFormat.DOCUMENTARY: [
        "FACT_CLAIMS", "EVIDENCE", "SOURCE_INTEGRITY", "VISUAL_TRUTHFULNESS",
        "PACING", "AUDIO", "RIGHTS",
    ],
    MediaFormat.TUTORIAL: [
        "STEP_CORRECTNESS", "SCREEN_READABILITY", "VOICE_SYNC",
        "RESULT_VERIFICATION", "AUDIO", "RIGHTS",
    ],
    MediaFormat.EXPLAINER: [
        "FACT_CLAIMS", "CONCEPT_CLARITY", "VISUAL_EXPLANATION",
        "PACING", "AUDIO", "RIGHTS",
    ],
    MediaFormat.REVIEW: [
        "EVIDENCE", "CRITERIA_CONSISTENCY", "CLAIM_SUPPORT", "AUDIO", "RIGHTS",
    ],
    MediaFormat.COMMERCIAL: [
        "BRAND_COMPLIANCE", "PRODUCT_ACCURACY", "CTA", "VISUAL_QUALITY", "AUDIO", "RIGHTS",
    ],
    MediaFormat.PODCAST: [
        "DIALOGUE_INTELLIGIBILITY", "SYNC", "PACING", "LOUDNESS", "RIGHTS",
    ],
    MediaFormat.INTERVIEW: [
        "DIALOGUE_INTELLIGIBILITY", "MULTICAM_CONTINUITY", "SYNC", "LOUDNESS", "RIGHTS",
    ],
    MediaFormat.MUSIC_VIDEO: [
        "MUSIC_SYNC", "VISUAL_CONTINUITY", "COLOR", "RIGHTS",
    ],
    MediaFormat.SOCIAL_SHORT: [
        "HOOK_CLARITY", "CAPTIONS", "PACING", "PLATFORM_SAFE_AREA", "AUDIO", "RIGHTS",
    ],
}


class QualityProfileRegistry:
    def for_format(self, media_format: MediaFormat) -> QualityProfile:
        gates = FORMAT_GATES.get(media_format, ["TECHNICAL", "AUDIO", "RIGHTS"])
        return QualityProfile(format=media_format, gates=list(gates))
