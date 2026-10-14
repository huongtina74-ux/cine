from __future__ import annotations

from enum import StrEnum
from typing import Any
from pydantic import BaseModel, Field, model_validator


class NicheStatus(StrEnum):
    ACTIVE_CORE = "ACTIVE_CORE"
    INCUBATING = "INCUBATING"
    HOLD = "HOLD"


class NicheManifest(BaseModel):
    niche_id: str
    display_name: str
    status: NicheStatus = NicheStatus.ACTIVE_CORE
    content_unit_ontology: list[str] = Field(min_length=1)
    shared_capabilities: list[str] = Field(default_factory=list)
    niche_specific_domains: list[str] = Field(default_factory=list)
    audience_model: dict[str, Any] = Field(default_factory=dict)
    competitor_registry: list[dict[str, Any]] = Field(default_factory=list)
    keyword_graph: dict[str, Any] = Field(default_factory=dict)
    format_dna: dict[str, Any] = Field(default_factory=dict)
    production_recipes: dict[str, Any] = Field(default_factory=dict)
    packaging_grammar: dict[str, Any] = Field(default_factory=dict)
    retention_baselines: dict[str, Any] = Field(default_factory=dict)
    risk_profile: dict[str, Any] = Field(default_factory=dict)
    validated_rules: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_specialization(self) -> "NicheManifest":
        if not self.niche_specific_domains:
            raise ValueError("niche must define niche-specific domains")
        return self


SHARED_CAPABILITIES = [
    "company_governance",
    "finance_legal_security",
    "versioning_and_provenance",
    "production_management",
    "universal_filmmaking_principles",
    "tool_and_capability_rnd",
    "data_and_experiment_framework",
    "technical_qa",
    "publishing_infrastructure",
]


def _niche(niche_id: str, display_name: str, ontology: list[str], domains: list[str]) -> NicheManifest:
    return NicheManifest(
        niche_id=niche_id,
        display_name=display_name,
        content_unit_ontology=ontology,
        shared_capabilities=list(SHARED_CAPABILITIES),
        niche_specific_domains=domains,
    )


DEFAULT_NICHES: dict[str, NicheManifest] = {
    "minecraft": _niche(
        "minecraft", "Minecraft",
        ["sequence", "scene", "beat", "shot"],
        ["audience", "competitors", "seo", "story_grammar", "voxel_identity", "minecraft_runtime",
         "camera_grammar", "animation", "assets", "packaging", "retention"],
    ),
    "long_slices_game": _niche(
        "long_slices_game", "Long Slices Game",
        ["run", "obstacle_segment", "event", "camera_shot"],
        ["audience", "competitors", "seo", "procedural_course", "physics", "obstacles",
         "animal_assets", "novelty", "camera_tracking", "packaging", "retention"],
    ),
    "asmr_sleep_hands_objects": _niche(
        "asmr_sleep_hands_objects", "ASMR Sleep — Hands + Objects",
        ["session", "trigger_block", "trigger_action", "shot"],
        ["audience", "competitors", "seo", "trigger_library", "microphones", "spatial_audio",
         "noise_floor", "low_stimulation_editing", "sleep_qc", "packaging"],
    ),
    "audio_storytelling_seniors": _niche(
        "audio_storytelling_seniors", "Audio Storytelling for Seniors",
        ["chapter", "scene", "story_beat", "audio_segment"],
        ["audience", "competitors", "seo", "story_selection", "rights", "voice",
         "pronunciation", "accessibility", "soundscape", "retention"],
    ),
    "fishing_silent": _niche(
        "fishing_silent", "Fishing Silent",
        ["session", "fishing_event", "action", "camera_shot"],
        ["audience", "competitors", "seo", "species", "seasonality", "location",
         "field_camera", "weather", "natural_audio", "field_safety", "packaging"],
    ),
    "rain_sleep_white_noise": _niche(
        "rain_sleep_white_noise", "Rain / Sleep / White Noise",
        ["environment", "ambience_segment", "loop_variation_block"],
        ["audience", "competitors", "seo", "ambience", "looping", "procedural_variation",
         "volume_stability", "transient_detection", "flicker_detection", "longform_mastering"],
    ),
    "roblox_animation": _niche(
        "roblox_animation", "Roblox Animation",
        ["sequence", "scene", "beat", "shot"],
        ["audience", "competitors", "seo", "r6_r15_identity", "roblox_runtime", "facial_performance",
         "camera_grammar", "animation", "assets", "packaging", "retention"],
    ),
}


class NicheRegistry:
    def __init__(self, items: dict[str, NicheManifest] | None = None) -> None:
        source = items or DEFAULT_NICHES
        self._items = {k: v.model_copy(deep=True) for k, v in source.items()}

    def get(self, niche_id: str) -> NicheManifest:
        return self._items[niche_id]

    def list(self) -> list[NicheManifest]:
        return [self._items[k] for k in sorted(self._items)]

    def register(self, manifest: NicheManifest) -> None:
        if manifest.niche_id in self._items:
            raise ValueError(f"niche already exists: {manifest.niche_id}")
        self._items[manifest.niche_id] = manifest

    def active(self) -> list[NicheManifest]:
        return [x for x in self.list() if x.status is NicheStatus.ACTIVE_CORE]
