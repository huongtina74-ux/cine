"""Variation models, policy, channel history and similarity measures.

YouTube does not pay for "characters put in the same situation over and over
again with the same outcome" or AI content made from generic templates, but it
explicitly allows "a series following a set of characters across episodes" in
which "each video has a distinct storyline". VariationDirector (director.py)
plans episodes against this policy and MonetizationSafetyGate (safety.py)
re-checks them before upload.
"""
from __future__ import annotations

import re
import unicodedata
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .contracts import LongSlideEpisodeSpec
from .series import CAMERA_PATTERNS, SeriesBible

__all__ = [
    "CAMERA_PATTERNS",
    "EpisodeConcept",
    "EpisodeHistory",
    "HistoryRecord",
    "SafetyFinding",
    "SafetyReport",
    "SeriesBible",
    "UploadPackage",
    "VariationExhaustedError",
    "VariationPolicy",
    "VariationReport",
    "VariedEpisode",
    "episode_fingerprint",
    "evaluate_variation",
    "normalize_text",
    "structural_similarity",
    "structural_tokens",
    "title_key",
    "title_similarity",
]

POLICY_VERSION = "2026-10-07.v2"
TITLE_STOPWORDS = frozenset({
    "the", "a", "an", "and", "with", "in", "on", "of", "to", "for", "at", "vs", "is", "it",
    "its", "s", "3d", "animal", "animals", "game", "games", "funny", "slide", "slides", "long",
    "race", "challenge", "adventure", "episode", "ep", "new", "day", "fun", "who", "can",
    "every", "big", "through",
})


class VariationPolicy(BaseModel):
    axes: tuple[str, ...] = (
        "format", "lead", "environment", "ending", "cast",
        "camera_style", "scene_sequence", "obstacle_sequence",
    )
    min_axis_changes: int = Field(default=4, ge=1)
    compare_window: int = Field(default=10, ge=1)
    cooldowns: dict[str, int] = Field(default_factory=lambda: {
        "format": 3, "lead": 2, "environment": 3, "ending": 2, "camera_style": 2,
    })
    max_structural_similarity: float = Field(default=0.5, gt=0, le=1)
    max_title_similarity: float = Field(default=0.6, gt=0, le=1)
    title_window: int = Field(default=30, ge=1)
    max_peril_share: float = Field(default=0.25, gt=0, le=1)
    min_outcome_kinds: int = Field(default=3, ge=1)
    min_scene_kinds: int = Field(default=3, ge=1)
    max_title_length: int = Field(default=100, ge=20)
    max_animal_names_in_title: int = Field(default=4, ge=1)

    @field_validator("cooldowns")
    @classmethod
    def non_negative_cooldowns(cls, value: dict[str, int]) -> dict[str, int]:
        if any(v < 0 for v in value.values()):
            raise ValueError("cooldowns must be zero or positive")
        return value

    def peril_cap(self, module_count: int) -> int:
        return max(1, int(module_count * self.max_peril_share))


class EpisodeConcept(BaseModel):
    format_id: str
    lead_character_id: str
    cast_ids: list[str]
    environment_id: str
    ending_id: str
    camera_style_id: str
    synopsis: str = ""


class HistoryRecord(BaseModel):
    episode_id: str
    created_at: str
    fingerprint: dict[str, str]
    tokens: list[str]
    title: str
    signature: str


class VariationReport(BaseModel):
    passed: bool
    attempts: int
    max_similarity: float
    min_axis_changes: int | None
    findings: list[str] = Field(default_factory=list)


class UploadPackage(BaseModel):
    title: str
    description: str
    tags: list[str] = Field(default_factory=list)
    made_for_kids: bool = True
    requires_human_approval: bool = True
    ai_disclosure_required: bool = False
    ai_disclosure_note: str = (
        "Fully animated, non-realistic 3D characters. YouTube's altered or synthetic "
        "content disclosure covers realistic content only."
    )
    evidence: dict[str, Any] = Field(default_factory=dict)


class SafetyFinding(BaseModel):
    code: str
    severity: str = "ERROR"
    message: str


class SafetyReport(BaseModel):
    passed: bool
    findings: list[SafetyFinding] = Field(default_factory=list)
    evidence: dict[str, Any] = Field(default_factory=dict)


class VariedEpisode(BaseModel):
    episode: LongSlideEpisodeSpec
    concept: EpisodeConcept
    fingerprint: dict[str, str]
    tokens: list[str]
    report: VariationReport
    package: UploadPackage
    safety: SafetyReport


class VariationExhaustedError(RuntimeError):
    """Raised when no episode can satisfy the variation policy. Production must stop."""

    def __init__(self, findings: list[str]) -> None:
        self.findings = list(findings)
        super().__init__("; ".join(self.findings[:12]))


# ---------- fingerprints and similarity ----------

def episode_fingerprint(concept: EpisodeConcept, episode: LongSlideEpisodeSpec) -> dict[str, str]:
    return {
        "format": concept.format_id,
        "lead": concept.lead_character_id,
        "environment": concept.environment_id,
        "ending": concept.ending_id,
        "camera_style": concept.camera_style_id,
        "cast": ",".join(sorted(concept.cast_ids)),
        "scene_sequence": "|".join(m.scene_kind.value for m in episode.modules),
        "obstacle_sequence": "|".join(
            "+".join(o.obstacle_id for o in m.obstacles if o.enabled) for m in episode.modules
        ),
    }


def structural_tokens(concept: EpisodeConcept, episode: LongSlideEpisodeSpec) -> list[str]:
    tokens = [
        f"format:{concept.format_id}",
        f"lead:{concept.lead_character_id}",
        f"env:{concept.environment_id}",
        f"ending:{concept.ending_id}",
        f"camstyle:{concept.camera_style_id}",
    ]
    for m in episode.modules:
        obstacles = "+".join(o.obstacle_id for o in m.obstacles if o.enabled)
        tokens.append(f"combo:{m.scene_kind.value}|{m.animal_id}|{m.outcome.value}")
        tokens.append(f"obst:{m.scene_kind.value}|{obstacles}")
        tokens.append("cam:" + ">".join(b.pattern_id for b in m.camera_beats))
    return tokens


def structural_similarity(a: list[str], b: list[str]) -> float:
    ca, cb = Counter(a), Counter(b)
    keys = set(ca) | set(cb)
    union = sum(max(ca[k], cb[k]) for k in keys)
    return 1.0 if union == 0 else sum(min(ca[k], cb[k]) for k in keys) / union


def normalize_text(text: str) -> str:
    """Casefold, strip accents and collapse every non-alphanumeric run to one space."""
    decomposed = unicodedata.normalize("NFKD", text)
    plain = "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[^0-9a-z]+", " ", plain.replace("'s", "")).strip()


def title_tokens(title: str) -> set[str]:
    return {w for w in normalize_text(title).split() if w not in TITLE_STOPWORDS}


def title_key(title: str) -> str:
    return normalize_text(title)


def title_similarity(a: str, b: str) -> float:
    ta, tb = title_tokens(a), title_tokens(b)
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / len(ta | tb)


def evaluate_variation(
    policy: VariationPolicy,
    fingerprint: dict[str, str],
    tokens: list[str],
    history: "EpisodeHistory",
) -> tuple[float, int | None, list[str]]:
    findings: list[str] = []
    max_sim, min_changes = 0.0, None
    for record in history.recent(policy.compare_window):
        sim = structural_similarity(tokens, record.tokens)
        changes = sum(1 for axis in policy.axes if fingerprint.get(axis) != record.fingerprint.get(axis))
        max_sim = max(max_sim, sim)
        min_changes = changes if min_changes is None else min(min_changes, changes)
        if sim > policy.max_structural_similarity:
            findings.append(f"VARIATION_TOO_SIMILAR:{record.episode_id}:{sim:.2f}")
        if changes < policy.min_axis_changes:
            findings.append(f"INSUFFICIENT_AXIS_CHANGE:{record.episode_id}:{changes}")
    return round(max_sim, 4), min_changes, findings


# ---------- history ----------

class EpisodeHistory:
    """Append-only record of approved episodes for one channel (JSON lines)."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else None
        self._records: list[HistoryRecord] = []
        if self.path is not None and self.path.is_file():
            with self.path.open("r", encoding="utf-8") as handle:
                for number, line in enumerate(handle, start=1):
                    if not line.strip():
                        continue
                    try:
                        self._records.append(HistoryRecord.model_validate_json(line))
                    except ValueError as exc:
                        raise ValueError(f"{self.path}: line {number} is not a valid history record") from exc

    def __len__(self) -> int:
        return len(self._records)

    def records(self) -> list[HistoryRecord]:
        return list(self._records)

    def recent(self, count: int) -> list[HistoryRecord]:
        return self._records[-count:] if count > 0 else []

    def title_keys(self) -> set[str]:
        return {title_key(r.title) for r in self._records}

    def signatures(self) -> set[str]:
        return {r.signature for r in self._records}

    def snapshot(self) -> "EpisodeHistory":
        """In-memory copy for planning a batch without touching the channel file."""
        copy = EpisodeHistory()
        copy._records = list(self._records)
        return copy

    def append(self, varied: VariedEpisode) -> HistoryRecord:
        record = HistoryRecord(
            episode_id=varied.episode.episode_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            fingerprint=dict(varied.fingerprint),
            tokens=list(varied.tokens),
            title=varied.package.title,
            signature=varied.episode.originality_signature,
        )
        if self.path is not None:
            self._write(record)
        self._records.append(record)
        return record

    def _write(self, record: HistoryRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        needs_newline = self.path.is_file() and self.path.stat().st_size > 0 and not self.path.read_bytes().endswith(b"\n")
        with self.path.open("a", encoding="utf-8") as handle:
            if needs_newline:
                handle.write("\n")
            handle.write(record.model_dump_json() + "\n")
