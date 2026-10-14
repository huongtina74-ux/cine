from __future__ import annotations
"""Research-only external tool candidate matrix on RTX 3060 12GB.

Vendor/repo claims are not local benchmark measurements, hardware limits are
hard prerequisites, licensing is independently reviewed at checkpoint/asset
level. No model download, install, execution or GPU workload is initiated.
"""
from pydantic import BaseModel,Field
from .niche_research_conference_v192 import OFFICIAL_SOURCE_SNAPSHOT


class ExternalToolResearchCard(BaseModel):
    id:str
    production_departments:list[str]
    primary_niches:list[str]
    vendor_doc_source_id:str
    vendor_claim_summary:str
    unverified_license_summary:str
    exact_version_or_checkpoint_required:bool=True
    actual_executable_benchmark_complete:bool=False
    actual_creative_quality_reviewed:bool=False
    actual_cost_per_accepted_minute_known:bool=False
    checkpoint_license_approved:bool=False
    production_qualified:bool=False
    minimum_vendor_vram_gb:float|None=Field(default=None,ge=0.)
    hardware_status:str
    next_test:str
    risks:list[str]


def vram_status(vendor_floor:float|None,available_gb:float=12.0)->str:
    if vendor_floor is None:
        return "UNKNOWN_MEASURE_ON_ISOLATED_GPU_NO_NATIVE_FIT_CLAIM"
    if vendor_floor>available_gb:
        return "BLOCKED_UNDER_VENDOR_REFERENCE_GPU_REQUIREMENT"
    return "VENDOR_REFERENCE_FLOOR_NOT_A_LOCAL_WORKING_BENCHMARK"


EXTERNAL_RESEARCH_CANDIDATES=[
    ExternalToolResearchCard(
        id="wan2.2.ti2v.5b.official.reference",
        production_departments=["ai_generatives","rnd_security","compute_finance"],
        primary_niches=["ai_family_drama","animal_animation"],
        vendor_doc_source_id="WAN22_OFFICIAL",
        vendor_claim_summary="Official 720P reference TI2V-5B inference states GPU >=24GB VRAM",
        unverified_license_summary="Repo states Apache-2.0; review exact weights and workflow separately",
        minimum_vendor_vram_gb=24,
        hardware_status=vram_status(24),
        next_test="Do not download for native 12GB reference inference; study independently verified offload/quantized scopes only",
        risks=["VRAM_REFERENCE_24GB","NO_LOCAL_WORKFLOW_BENCHMARK","CHECKPOINT_AND_ASSET_RIGHTS_REVIEW"],
    ),
    ExternalToolResearchCard(
        id="ltxv.2b.0.9.8.distilled",
        production_departments=["ai_generatives","rnd_security","compute_finance"],
        primary_niches=["ai_family_drama","animal_animation"],
        vendor_doc_source_id="LTX2B_REPO",
        vendor_claim_summary="Official repo lists small distilled 2B model designed for light VRAM",
        unverified_license_summary="Code repository Apache-2.0; per-weight OpenRAIL/other terms require exact model-card review",
        minimum_vendor_vram_gb=None,
        hardware_status=vram_status(None),
        next_test="Isolated exact-checkpoint license review then 384x216 2-second I2V sample, measure peak GPU VRAM, time and visual continuity",
        risks=["VRAM_FIT_UNMEASURED","WEIGHTS_LICENSE_NOT_APPROVED","NO_MULTI_SHOT_IDENTITY_METRIC"],
    ),
    ExternalToolResearchCard(
        id="musescore.studio.music",
        production_departments=["songwriting_music","audio_post","rnd_security"],
        primary_niches=["preschool_3d_musical"],
        vendor_doc_source_id="MUSESCORE_REPO",
        vendor_claim_summary="MIDI, MusicXML and staff editing; score composition tool (not original AI song generation)",
        unverified_license_summary="GPLv3 software, verify soundfonts, music, recordings and distribution scope independently",
        hardware_status=vram_status(None),
        next_test="Local executable install with permission, 30s original score + MIDI and click-aligned bar timing export",
        risks=["NOT_INSTALLED","NO_AUTOMATED_ORIGINAL_COMPOSER","SONG_RIGHTS_HUMAN_REQUIRED"],
    ),
    ExternalToolResearchCard(
        id="piper.archived.local.tts",
        production_departments=["voice_cast","audio_post","rnd_security"],
        primary_niches=["audio_storytelling_seniors","daily_english"],
        vendor_doc_source_id="PIPER_OLD_REPO",
        vendor_claim_summary="Local neural TTS family; original rhasspy repo archived since 2025",
        unverified_license_summary="Archived engine MIT, each voice model and dataset need separate license review",
        hardware_status=vram_status(None),
        next_test="Find maintained permitted successor; compare real narration MOS and pronunciation with local SAPI, including voice rights",
        risks=["SOURCE_ARCHIVED","VOICE_WEIGHTS_RIGHTS_UNCHECKED","NARRATION_NOT_MUSIC_SINGING"],
    ),
]


def research_candidate_snapshot()->dict:
    for card in EXTERNAL_RESEARCH_CANDIDATES:
        if card.vendor_doc_source_id not in OFFICIAL_SOURCE_SNAPSHOT:
            raise ValueError("UNTRUSTED_OR_UNREGISTERED_EXTERNAL_SOURCE_ID")
    return {
        "status":"RESEARCH_ONLY_NO_DOWNLOAD_OR_PRODUCTION",
        "current_gpu_assumed":"RTX3060_12GB",
        "cards":[c.model_dump(mode="json") for c in EXTERNAL_RESEARCH_CANDIDATES],
        "source_ledger":{
            r.vendor_doc_source_id:OFFICIAL_SOURCE_SNAPSHOT[r.vendor_doc_source_id].model_dump(mode="json")
            for r in EXTERNAL_RESEARCH_CANDIDATES
        },
        "all_candidates_production_qualified":False,
    }
