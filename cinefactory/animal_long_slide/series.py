"""Series bible: the creative pools every Long Slide episode is built from."""
from __future__ import annotations

import string
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from .contracts import LongSlideModuleSpec, LongSlideSceneKind, OutcomeKind


# Camera patterns the Blender worker (scripts/render_long_slide_job.py) can execute.
CAMERA_PATTERNS: tuple[str, ...] = (
    "hero_start",
    "chase",
    "obstacle_side",
    "finish_reaction",
    "wide_establish",
    "top_down",
    "low_front",
)

# Scenes and obstacles that show an animal confined or blocked. YouTube's July 2026
# guidance names "animals in exaggerated distress or peril", so these are capped.
PERIL_SCENES: frozenset[LongSlideSceneKind] = frozenset({LongSlideSceneKind.CAGE})
PERIL_OBSTACLES: frozenset[str] = frozenset({"cage"})

TITLE_FIELDS = frozenset({"lead", "lead_animal", "friends", "crew", "env", "brand"})
SYNOPSIS_FIELDS = frozenset({"lead", "lead_animal", "friends", "env"})
ENDING_FIELDS = frozenset({"lead"})

DEFAULT_BIBLE_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "animal_long_slide" / "series_bible.yaml"
)


def is_peril(module: LongSlideModuleSpec) -> bool:
    """Derived from what is on screen, never from self-reported metadata."""
    return module.scene_kind in PERIL_SCENES or any(
        o.enabled and o.obstacle_id in PERIL_OBSTACLES for o in module.obstacles
    )


def _check_fields(templates: list[str], allowed: frozenset[str], label: str) -> None:
    for template in templates:
        try:
            fields = {name for _, name, _, _ in string.Formatter().parse(template) if name is not None}
        except ValueError as exc:
            raise ValueError(f"{label} template is malformed: {template!r}") from exc
        unknown = fields - allowed
        if unknown:
            raise ValueError(f"{label} template {template!r} uses unknown fields {sorted(unknown)}")


class SeriesCharacter(BaseModel):
    character_id: str
    name: str
    animal_id: str
    trait: str
    signature: str


class EnvironmentTheme(BaseModel):
    theme_id: str
    label: str
    world_color: tuple[float, float, float]
    sun_color: tuple[float, float, float]
    sun_energy: float = Field(gt=0)
    sun_elevation_deg: float
    sun_azimuth_deg: float

    def render_settings(self) -> dict:
        return self.model_dump(mode="json")


class ChallengeFormat(BaseModel):
    format_id: str
    label: str
    scenes: list[LongSlideSceneKind] = Field(min_length=2)
    title_templates: list[str] = Field(min_length=1)
    synopsis_templates: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def known_fields(self) -> "ChallengeFormat":
        _check_fields(self.title_templates, TITLE_FIELDS, f"{self.format_id} title")
        _check_fields(self.synopsis_templates, SYNOPSIS_FIELDS, f"{self.format_id} synopsis")
        return self


class CameraStyle(BaseModel):
    style_id: str
    variants: list[list[str]] = Field(min_length=2)

    @model_validator(mode="after")
    def known_patterns(self) -> "CameraStyle":
        if any(len(v) < 2 for v in self.variants):
            raise ValueError(f"camera style {self.style_id} has a variant with fewer than two patterns")
        unknown = {p for v in self.variants for p in v if p not in CAMERA_PATTERNS}
        if unknown:
            raise ValueError(f"camera style {self.style_id} uses unknown patterns: {sorted(unknown)}")
        if len({tuple(v) for v in self.variants}) != len(self.variants):
            raise ValueError(f"camera style {self.style_id} repeats a variant")
        return self


class EndingSpec(BaseModel):
    ending_id: str
    final_outcome: OutcomeKind
    line: str

    @model_validator(mode="after")
    def positive_finale(self) -> "EndingSpec":
        if self.final_outcome not in {OutcomeKind.SUCCESS, OutcomeKind.TRANSFORM}:
            raise ValueError("episode endings must resolve positively")
        _check_fields([self.line], ENDING_FIELDS, f"{self.ending_id} ending")
        return self


class SeriesBible(BaseModel):
    brand: str = Field(min_length=3)
    language: str = "en"
    min_cast: int = Field(default=4, ge=3)
    max_cast: int = Field(default=5, ge=3)
    cast: list[SeriesCharacter] = Field(min_length=3)
    environments: list[EnvironmentTheme] = Field(min_length=2)
    formats: list[ChallengeFormat] = Field(min_length=1)
    camera_styles: list[CameraStyle] = Field(min_length=2)
    endings: list[EndingSpec] = Field(min_length=2)

    @field_validator("brand")
    @classmethod
    def plain_brand(cls, value: str) -> str:
        if "{" in value or "}" in value:
            raise ValueError("brand must not contain template braces")
        return value

    @model_validator(mode="after")
    def unique_ids(self) -> "SeriesBible":
        for label, ids in (
            ("character", [c.character_id for c in self.cast]),
            ("animal", [c.animal_id for c in self.cast]),
            ("environment", [e.theme_id for e in self.environments]),
            ("format", [f.format_id for f in self.formats]),
            ("camera style", [s.style_id for s in self.camera_styles]),
            ("ending", [e.ending_id for e in self.endings]),
        ):
            if len(ids) != len(set(ids)):
                raise ValueError(f"duplicate {label} id in series bible")
        if self.max_cast > len(self.cast) or self.min_cast > self.max_cast:
            raise ValueError("cast size limits do not fit the cast list")
        return self

    @classmethod
    def load(cls, path: str | Path) -> "SeriesBible":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return cls.model_validate(data)

    @classmethod
    def default(cls) -> "SeriesBible":
        return cls.load(DEFAULT_BIBLE_PATH)

    def character(self, character_id: str) -> SeriesCharacter:
        return {c.character_id: c for c in self.cast}[character_id]

    def environment(self, theme_id: str) -> EnvironmentTheme:
        return {e.theme_id: e for e in self.environments}[theme_id]

    def challenge(self, format_id: str) -> ChallengeFormat:
        return {f.format_id: f for f in self.formats}[format_id]

    def camera_style(self, style_id: str) -> CameraStyle:
        return {s.style_id: s for s in self.camera_styles}[style_id]

    def ending(self, ending_id: str) -> EndingSpec:
        return {e.ending_id: e for e in self.endings}[ending_id]
