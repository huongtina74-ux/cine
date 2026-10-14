from __future__ import annotations

from pydantic import BaseModel, Field


class ColorBible(BaseModel):
    working_space: str = "scene-linear"
    input_transforms: dict[str, str] = Field(default_factory=dict)
    look_description: str = ""
    contrast_intent: str = ""
    saturation_intent: str = ""
    skin_or_identity_protection: list[str] = Field(default_factory=list)
    output_targets: list[str] = Field(default_factory=lambda: ["SDR"])
    shot_match_tolerance: float = Field(default=0.1, ge=0.0)


class ShotColorState(BaseModel):
    shot_id: str
    source_space: str
    exposure_offset: float = 0.0
    white_balance_shift: float = 0.0
    contrast_offset: float = 0.0
    saturation_offset: float = 0.0
    approved: bool = False
    notes: list[str] = Field(default_factory=list)


class ColorPlan(BaseModel):
    project_id: str
    bible: ColorBible
    shots: list[ShotColorState] = Field(default_factory=list)


class ColorQC:
    def validate(self, plan: ColorPlan) -> list[str]:
        findings: list[str] = []
        ids = [x.shot_id for x in plan.shots]
        if len(ids) != len(set(ids)):
            findings.append("DUPLICATE_COLOR_SHOT_ID")
        for shot in plan.shots:
            if abs(shot.exposure_offset) > 4:
                findings.append(f"{shot.shot_id}:EXTREME_EXPOSURE_OFFSET")
            if abs(shot.saturation_offset) > 2:
                findings.append(f"{shot.shot_id}:EXTREME_SATURATION_OFFSET")
        return findings
