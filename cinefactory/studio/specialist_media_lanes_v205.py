"""Dedicated, fail-closed media lanes; no animation rig assumptions.

This stage graph is an actual specialist pipeline. It can work with genuinely
user-owned pre-recorded media, but cannot certify absent recordings, voices,
licenses, research evidence, or original film quality.
"""
from __future__ import annotations

from .contracts import DepartmentId

LANES = {
    "asmr_sleep_hands_objects": {
        "content": "Hand/object sound capture", "media": "owned_multi_take_video",
        "technical": ["low_noise_floor", "no_startling_audio", "natural_actions"],
        "human": ["sleep_listener_review", "privacy_review"],
    },
    "audio_storytelling_seniors": {
        "content": "Original narration and optional licensed visuals",
        "media": "owned_narrated_video",
        "technical": ["speech_intelligibility", "narrative_continuity", "readable_pacing"],
        "human": ["original_script_rights", "voice_consent", "listener_review"],
    },
    "fishing_silent": {
        "content": "Real authorized location footage with authentic ambient audio",
        "media": "owned_real_footage",
        "technical": ["real_world_provenance", "scene_continuity", "clean_natural_audio"],
        "human": ["location_permissions", "wildlife_rules", "privacy_review"],
    },
    "rain_sleep_white_noise": {
        "content": "Original or commercially licensed ambient footage and noise",
        "media": "owned_ambient_footage",
        "technical": ["continuous_ambience", "no_audible_loop_seams", "safe_levels"],
        "human": ["sound_license", "sleep_listener_review"],
    },
}


def is_specialist_lane(niche: str | None) -> bool:
    return bool(niche and niche in LANES)


def build_specialist_stages(niche: str) -> list:
    from .company import CompanyStage as S
    if niche not in LANES:
        raise ValueError("UNSUPPORTED_SPECIALIST_LANE")
    return [
        S(stage_id="NICHE_PROJECT_INTAKE",owner="STUDIO_MANAGEMENT",
          artifacts_in=["project_brief"],artifacts_out=["niche_project_brief"],
          gate="FORMAT_OWNER_INTAKE"),
        S(stage_id="NICHE_RESEARCH_REVIEW",owner="INTELLIGENCE",
          artifacts_in=["niche_project_brief"],artifacts_out=["verified_niche_dossier"],
          gate="SOURCE_BOUND_RESEARCH_REVIEW"),
        S(stage_id="NICHE_FORMAT_DIRECTION",owner="CREATIVE_STRATEGY",
          artifacts_in=["verified_niche_dossier"],
          artifacts_out=["original_format_plan"],gate="NICHE_ORIGINALITY"),
        S(stage_id="NICHE_RIGHTS_AND_SOURCES",owner="RIGHTS",
          artifacts_in=["original_format_plan"],
          artifacts_out=["source_clearance","media_source_manifest"],
          gate="SOURCE_RIGHTS_AND_CAPTURE_QC"),
        S(stage_id="NICHE_MEDIA_ASSEMBLY",owner="PRODUCTION",
          artifacts_in=["media_source_manifest","source_clearance","original_format_plan"],
          artifacts_out=["dailies","assembly_report"],
          gate="QUALIFIED_SOURCE_ASSEMBLY"),
        S(stage_id="NICHE_SOUND_QUALITY",owner="AUDIO",
          artifacts_in=["dailies"],artifacts_out=["sound_qc"],
          gate="NICHE_SPECIFIC_SOUND"),
        S(stage_id="NICHE_FILM_QC",owner="QC",
          artifacts_in=["dailies","sound_qc"],
          artifacts_out=["film_qc_report","approved_master"],
          gate="WHOLE_FILM_INDEPENDENT_ACCEPTANCE"),
        S(stage_id="NICHE_PACKAGING",owner="PACKAGING",
          artifacts_in=["approved_master","original_format_plan"],
          artifacts_out=["release_package"],gate="PLATFORM_TRUTHFUL_PACKAGING"),
        S(stage_id="PUBLISHING",owner="OPERATIONS",
          artifacts_in=["release_package"],
          artifacts_out=["publication_receipt"],gate="AUTHORIZED_PRIVATE_FIRST"),
        S(stage_id="ANALYTICS_LEARNING",owner="ANALYTICS",
          artifacts_in=["publication_receipt"],
          artifacts_out=["observations","hypotheses","learning_candidates"],
          gate="OWNED_METRIC_VALIDATION"),
    ]


def validate_specialist_contracts(niche: str) -> dict:
    from .contract_integrity import audit_company_wiring
    report = audit_company_wiring(build_specialist_stages(niche))
    return {"niche": niche, "valid": report.valid,
            "stage_count": len(report.producer_by_artifact),
            "blockers": report.blocker_codes()}
