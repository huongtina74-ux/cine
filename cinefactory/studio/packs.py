from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class PackKind(StrEnum):
    DOMAIN = "DOMAIN"
    GENRE = "GENRE"
    EXECUTION = "EXECUTION"
    STYLE = "STYLE"
    PLATFORM = "PLATFORM"


class StudioPack(BaseModel):
    pack_id: str
    kind: PackKind
    version: str = "1"
    knowledge_refs: list[str] = Field(default_factory=list)
    skill_refs: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    capability_preferences: list[str] = Field(default_factory=list)
    qc_gates: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PackComposition(BaseModel):
    domain_pack: StudioPack | None = None
    genre_pack: StudioPack | None = None
    execution_pack: StudioPack | None = None
    style_pack: StudioPack | None = None
    platform_pack: StudioPack | None = None

    def ordered(self) -> list[StudioPack]:
        return [
            p for p in (
                self.domain_pack,
                self.genre_pack,
                self.execution_pack,
                self.style_pack,
                self.platform_pack,
            ) if p is not None
        ]

    def merged_rules(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for pack in self.ordered():
            for rule in pack.rules:
                if rule not in seen:
                    seen.add(rule)
                    out.append(rule)
        return out

    def merged_qc_gates(self) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for pack in self.ordered():
            for gate in pack.qc_gates:
                if gate not in seen:
                    seen.add(gate)
                    out.append(gate)
        return out
class PackRegistry:
    def __init__(self) -> None:
        self._items: dict[str, StudioPack] = {}

    def register(self, pack: StudioPack) -> None:
        key = f"{pack.pack_id}@{pack.version}"
        if key in self._items and self._items[key] != pack:
            raise ValueError(f"immutable pack conflict: {key}")
        self._items[key] = pack

    def get(self, pack_id: str, version: str = "1") -> StudioPack:
        return self._items[f"{pack_id}@{version}"]

    def list(self, kind: PackKind | None = None) -> list[StudioPack]:
        values = list(self._items.values())
        if kind is not None:
            values = [p for p in values if p.kind is kind]
        return sorted(values, key=lambda p: (p.kind.value, p.pack_id, p.version))


def default_pack_registry() -> PackRegistry:
    registry = PackRegistry()
    defaults = [
        StudioPack(
            pack_id="domain.gaming",
            kind=PackKind.DOMAIN,
            rules=["authentic gameplay cannot be silently replaced by fabricated gameplay"],
            qc_gates=["GAMEPLAY_AUTHENTICITY", "CAPTURE_QUALITY"],
        ),
        StudioPack(
            pack_id="domain.animation.animal_long_slide",
            kind=PackKind.DOMAIN,
            knowledge_refs=["knowledge/animal_long_slide.md"],
            skill_refs=[
                "animal_long_slide.direction",
                "animal_long_slide.asset_standardization",
                "animal_long_slide.visual_qc",
            ],
            rules=[
                "treat the format as authored procedural 3D animation, not authentic gameplay",
                "commercial-use rights must be approved before an external asset enters production",
                "prefer controlled animation/path motion and confine physics to bounded event windows",
                "new episodes must vary challenge, obstacle sequence, outcome, and camera moments rather than cosmetic swaps only",
            ],
            capability_preferences=["blender.offline3d", "ffmpeg.editorial", "sfx.local"],
            qc_gates=[
                "ASSET_RIGHTS",
                "RIG_COMPATIBILITY",
                "GROUND_CONTACT",
                "COLLISION_INTEGRITY",
                "CAMERA_FRAMING",
                "EVENT_PACING",
                "NOVELTY",
            ],
            metadata={"vertical": "animal_long_slide", "dialogue_required": False},
        ),
        StudioPack(
            pack_id="genre.documentary",
            kind=PackKind.GENRE,
            rules=["claims requiring evidence must resolve to an EvidenceMap"],
            qc_gates=["FACT_CLAIMS", "SOURCE_INTEGRITY", "VISUAL_TRUTHFULNESS"],
        ),
        StudioPack(
            pack_id="genre.tutorial",
            kind=PackKind.GENRE,
            rules=["every demonstrated step must have a verifiable result"],
            qc_gates=["STEP_CORRECTNESS", "SCREEN_READABILITY", "RESULT_VERIFICATION"],
        ),
        StudioPack(
            pack_id="execution.offline3d",
            kind=PackKind.EXECUTION,
            capability_preferences=["blender.offline3d"],
            rules=["previs before beauty render for new or complex shots"],
        ),
        StudioPack(
            pack_id="platform.youtube_longform",
            kind=PackKind.PLATFORM,
            rules=["preserve intelligibility and pacing across the full runtime"],
            qc_gates=["AUDIO", "PACING", "PLATFORM"],
        ),
    ]
    for item in defaults:
        registry.register(item)
    return registry
