from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .contracts import MediaProductSpec, StudioProjectSpec


class AudienceDNA(BaseModel):
    primary_audience: str | None = None
    viewing_intent: str | None = None
    knowledge_level: str | None = None
    attention_constraints: list[str] = Field(default_factory=list)


class BrandDNA(BaseModel):
    promise: str = ""
    tone: list[str] = Field(default_factory=list)
    forbidden_traits: list[str] = Field(default_factory=list)
    recurring_signatures: list[str] = Field(default_factory=list)


class VisualDNA(BaseModel):
    style_principles: list[str] = Field(default_factory=list)
    palette_intent: list[str] = Field(default_factory=list)
    composition_rules: list[str] = Field(default_factory=list)
    asset_consistency_rules: list[str] = Field(default_factory=list)


class CameraDNA(BaseModel):
    grammar: list[str] = Field(default_factory=list)
    movement_policy: list[str] = Field(default_factory=list)
    continuity_rules: list[str] = Field(default_factory=list)


class EditingDNA(BaseModel):
    pacing_principles: list[str] = Field(default_factory=list)
    transition_policy: list[str] = Field(default_factory=list)
    information_density: str | None = None
class AudioDNA(BaseModel):
    voice_profile: str | None = None
    music_role: str | None = None
    ambience_policy: list[str] = Field(default_factory=list)
    mix_priorities: list[str] = Field(default_factory=lambda: ["dialogue intelligibility", "no clipping"])


class OriginalityDNA(BaseModel):
    differentiation_axes: list[str] = Field(default_factory=list)
    blocked_copy_dimensions: list[str] = Field(
        default_factory=lambda: [
            "storyline",
            "dialogue",
            "character identity",
            "branding",
            "thumbnail expression",
            "proprietary assets",
        ]
    )


class ProjectDNA(BaseModel):
    project_id: str
    audience: AudienceDNA = Field(default_factory=AudienceDNA)
    brand: BrandDNA = Field(default_factory=BrandDNA)
    visual: VisualDNA = Field(default_factory=VisualDNA)
    camera: CameraDNA = Field(default_factory=CameraDNA)
    editing: EditingDNA = Field(default_factory=EditingDNA)
    audio: AudioDNA = Field(default_factory=AudioDNA)
    originality: OriginalityDNA = Field(default_factory=OriginalityDNA)
    format_rules: dict[str, Any] = Field(default_factory=dict)


class ProjectDNACompiler:
    def compile(self, project: StudioProjectSpec, product: MediaProductSpec) -> ProjectDNA:
        return ProjectDNA(
            project_id=project.studio_project_id,
            brand=BrandDNA(
                promise=f"Deliver a clear {product.format.value.lower()} experience for the requested goal.",
                tone=["coherent", "purposeful", "original"],
                forbidden_traits=["unmotivated filler", "silent tool substitution"],
            ),
            visual=VisualDNA(
                style_principles=["consistency before variation", "readability before decoration"],
                asset_consistency_rules=["persistent entity identity across representations"],
            ),
            camera=CameraDNA(
                grammar=["no shot without purpose"],
                movement_policy=["no camera move without purpose"],
                continuity_rules=["preserve screen direction unless intentionally reset"],
            ),
            editing=EditingDNA(
                pacing_principles=["cut on information, emotion, action or rhythm"],
                transition_policy=["prefer motivated transitions over decoration"],
            ),
            audio=AudioDNA(
                music_role="support narrative/information, never mask dialogue",
                ambience_policy=["maintain spatial continuity"],
            ),
            format_rules={
                "format": product.format.value,
                "evidence_required": product.evidence_required,
                "actual_gameplay_required": product.actual_gameplay_required,
                "brand_compliance_required": product.brand_compliance_required,
            },
        )
