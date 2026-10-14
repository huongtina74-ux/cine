from __future__ import annotations

import hashlib
import json
import math
import re
import tempfile
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

from cinefactory.block_animation.registry import (
    BlockAnimationLibraries,
)
from cinefactory.block_animation.rendered_frame_qc import (
    ActorAppearanceComparison,
    ActorAppearanceEvidence,
    RenderedAppearanceEvaluator,
    RenderedFrameAnalyzer,
    RenderedFrameQCResult,
)
from cinefactory.media.ffmpeg import FFmpegToolchain


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class CharacterBackendId(StrEnum):
    BLENDER_BLOCK = "BLENDER_BLOCK"
    MINECRAFT_RUNTIME = "MINECRAFT_RUNTIME"
    ROBLOX_STUDIO_R6 = "ROBLOX_STUDIO_R6"
    ROBLOX_STUDIO_R15 = "ROBLOX_STUDIO_R15"
    WAN21 = "WAN21"


class CharacterBackendBinding(BaseModel):
    backend_id: CharacterBackendId
    rig_id: str | None = None
    adapter_id: str | None = None
    identity_tokens: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CharacterStateVersion(BaseModel):
    version: int = Field(default=1, ge=1)
    costume_id: str | None = None
    accessories: list[str] = Field(default_factory=list)
    expression_profile: str | None = None
    notes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class CharacterReferencePack(BaseModel):
    reference_id: str
    global_character_id: str
    actor_id: str
    rig_id: str
    backend_id: CharacterBackendId
    source_media_path: str
    source_media_sha256: str
    crop_path: str
    crop_sha256: str
    screen_box: dict[str, float]
    evidence: ActorAppearanceEvidence
    state_version: int = Field(default=1, ge=1)
    costume_id: str | None = None
    accessories: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class CharacterIdentityRecord(BaseModel):
    global_character_id: str
    display_name: str
    style: str
    identity_lock: str
    immutable_traits: dict[str, Any] = Field(default_factory=dict)
    bindings: list[CharacterBackendBinding] = Field(default_factory=list)
    state_versions: list[CharacterStateVersion] = Field(default_factory=list)
    reference_ids: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    @property
    def current_state(self) -> CharacterStateVersion:
        if not self.state_versions:
            return CharacterStateVersion()
        return max(
            self.state_versions,
            key=lambda item: item.version,
        )


class ActorIdentityAssessment(BaseModel):
    actor_id: str
    global_character_id: str
    reference_id: str | None = None
    measured: bool = False
    passed: bool = False
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    comparison: ActorAppearanceComparison | None = None
    competing_character_id: str | None = None
    competing_score: float | None = Field(default=None, ge=0.0, le=1.0)
    findings: list[str] = Field(default_factory=list)


class MultiCharacterIdentityReport(BaseModel):
    passed: bool
    measured: bool
    minimum_score: float | None = Field(default=None, ge=0.0, le=1.0)
    assessments: list[ActorIdentityAssessment] = Field(default_factory=list)
    collision_findings: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class ActorTrackSample(BaseModel):
    label: str
    time_seconds: float = Field(ge=0)
    screen_box: dict[str, float]
    score: float = Field(ge=0.0, le=1.0)
    evidence: ActorAppearanceEvidence


class ActorTrackReport(BaseModel):
    actor_id: str
    global_character_id: str
    reference_id: str
    measured: bool
    passed: bool
    minimum_score: float | None = Field(default=None, ge=0.0, le=1.0)
    samples: list[ActorTrackSample] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class MultiActorTrackingReport(BaseModel):
    passed: bool
    measured: bool
    minimum_score: float | None = Field(default=None, ge=0.0, le=1.0)
    tracks: list[ActorTrackReport] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class CharacterTransitionAssessment(BaseModel):
    actor_id: str
    global_character_id: str
    previous_backend: CharacterBackendId
    current_backend: CharacterBackendId
    measured: bool = False
    passed: bool = False
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    comparison: ActorAppearanceComparison | None = None
    findings: list[str] = Field(default_factory=list)


class CharacterTransitionReport(BaseModel):
    passed: bool
    measured: bool
    minimum_score: float | None = Field(default=None, ge=0.0, le=1.0)
    transitions: list[CharacterTransitionAssessment] = Field(
        default_factory=list
    )
    findings: list[str] = Field(default_factory=list)


class CharacterFactoryStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.records = self.root / "records"
        self.references = self.root / "references"
        self.records.mkdir(parents=True, exist_ok=True)
        self.references.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return re.sub(r"[^A-Za-z0-9._-]+", "_", value)

    def record_path(self, global_character_id: str) -> Path:
        return self.records / (
            self._safe(global_character_id) + ".json"
        )

    def save_record(
        self,
        record: CharacterIdentityRecord,
    ) -> CharacterIdentityRecord:
        record.updated_at = utcnow()
        self.record_path(
            record.global_character_id
        ).write_text(
            record.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return record

    def get_record(
        self,
        global_character_id: str,
    ) -> CharacterIdentityRecord:
        path = self.record_path(global_character_id)
        if not path.is_file():
            raise KeyError(global_character_id)
        return CharacterIdentityRecord.model_validate_json(
            path.read_text(encoding="utf-8")
        )

    def save_reference(
        self,
        pack: CharacterReferencePack,
    ) -> Path:
        folder = (
            self.references
            / self._safe(pack.global_character_id)
        )
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (
            self._safe(pack.reference_id) + ".json"
        )
        path.write_text(
            pack.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    def get_reference(
        self,
        global_character_id: str,
        reference_id: str,
    ) -> CharacterReferencePack:
        path = (
            self.references
            / self._safe(global_character_id)
            / (self._safe(reference_id) + ".json")
        )
        if not path.is_file():
            raise KeyError(reference_id)
        return CharacterReferencePack.model_validate_json(
            path.read_text(encoding="utf-8")
        )


class CharacterFactory:
    """Cross-backend character identity authority.

    It derives stable character records from the existing rig registry,
    captures actor-specific reference crops from trusted render QC sidecars,
    and evaluates per-actor identity across backend boundaries.
    """

    def __init__(
        self,
        root: str | Path,
        *,
        store: CharacterFactoryStore | None = None,
        identity_floor: float = 0.70,
        collision_margin: float = 0.08,
    ) -> None:
        self.root = Path(root).resolve()
        self.libraries = BlockAnimationLibraries.load(self.root)
        self.store = store or CharacterFactoryStore(
            self.root
            / "data"
            / "studio"
            / "character_factory"
        )
        self.media = FFmpegToolchain()
        self.evaluator = RenderedAppearanceEvaluator()
        self.identity_floor = float(identity_floor)
        self.collision_margin = float(collision_margin)
        self.rig_to_character: dict[str, str] = {}
        self.bootstrap_from_rigs()

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(
                lambda: fh.read(1024 * 1024),
                b"",
            ):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def _global_id(rig: Any) -> str:
        identity = dict(rig.identity or {})
        source = str(
            identity.get("color_identity")
            or identity.get("avatar_id")
            or identity.get("skin_id")
            or rig.rig_id
        )
        safe = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            source,
        ).strip("_").upper()
        return "CHAR_" + safe

    @staticmethod
    def _backend_for_style(style: str) -> CharacterBackendId | None:
        if style == "MINECRAFT":
            return CharacterBackendId.MINECRAFT_RUNTIME
        if style == "ROBLOX_R6":
            return CharacterBackendId.ROBLOX_STUDIO_R6
        if style == "ROBLOX_R15":
            return CharacterBackendId.ROBLOX_STUDIO_R15
        return None

    @staticmethod
    def _state_from_rig(rig: Any) -> CharacterStateVersion:
        identity = dict(rig.identity or {})
        costume = (
            identity.get("clothing")
            or identity.get("skin_id")
        )
        return CharacterStateVersion(
            version=1,
            costume_id=(
                str(costume)
                if costume not in (None, "")
                else None
            ),
            accessories=list(rig.accessories or []),
            expression_profile=rig.expression_profile,
            notes=["BOOTSTRAPPED_FROM_RIG_REGISTRY"],
        )

    def bootstrap_from_rigs(self) -> None:
        for rig in self.libraries.rigs.values():
            global_id = self._global_id(rig)
            self.rig_to_character[rig.rig_id] = global_id
            try:
                record = self.store.get_record(global_id)
            except KeyError:
                identity = dict(rig.identity or {})
                tokens = [
                    f"{key}={value}"
                    for key, value in sorted(identity.items())
                    if value not in (None, "", [], {})
                ]
                bindings = [
                    CharacterBackendBinding(
                        backend_id=CharacterBackendId.BLENDER_BLOCK,
                        rig_id=rig.rig_id,
                        adapter_id="block_animation.rig",
                        identity_tokens=tokens,
                    ),
                    CharacterBackendBinding(
                        backend_id=CharacterBackendId.WAN21,
                        rig_id=rig.rig_id,
                        adapter_id="reference_conditioning",
                        identity_tokens=tokens,
                        metadata={
                            "qualification": "REFERENCE_REQUIRED",
                        },
                    ),
                ]
                native = self._backend_for_style(str(rig.style))
                if native is not None:
                    bindings.append(
                        CharacterBackendBinding(
                            backend_id=native,
                            rig_id=rig.rig_id,
                            adapter_id="native_character_binding",
                            identity_tokens=tokens,
                        )
                    )
                record = CharacterIdentityRecord(
                    global_character_id=global_id,
                    display_name=rig.rig_id,
                    style=str(rig.style),
                    identity_lock=(
                        "preserve " + ", ".join(tokens)
                        if tokens
                        else f"preserve rig {rig.rig_id}"
                    ),
                    immutable_traits=identity,
                    bindings=bindings,
                    state_versions=[
                        self._state_from_rig(rig)
                    ],
                    aliases=[rig.rig_id],
                )
                self.store.save_record(record)
            else:
                aliases = list(record.aliases)
                if rig.rig_id not in aliases:
                    aliases.append(rig.rig_id)
                    record.aliases = aliases
                    self.store.save_record(record)

    def record_for_rig(
        self,
        rig_id: str,
    ) -> CharacterIdentityRecord:
        try:
            global_id = self.rig_to_character[rig_id]
        except KeyError as exc:
            raise KeyError(
                f"CHARACTER_FACTORY_UNKNOWN_RIG:{rig_id}"
            ) from exc
        return self.store.get_record(global_id)

    def descriptor_for_rig(self, rig_id: str) -> str:
        record = self.record_for_rig(rig_id)
        traits = ", ".join(
            f"{key} {value}"
            for key, value in sorted(
                record.immutable_traits.items()
            )
            if value not in (None, "", [], {})
        )
        state = record.current_state
        pieces = [
            f"global character {record.global_character_id}",
            record.identity_lock,
        ]
        if traits:
            pieces.append(traits)
        if state.costume_id:
            pieces.append(
                f"costume {state.costume_id}"
            )
        if state.accessories:
            pieces.append(
                "accessories "
                + ", ".join(state.accessories)
            )
        return ", ".join(pieces)

    @staticmethod
    def _crop(
        image: Image.Image,
        box: dict[str, float],
        *,
        margin: float = 0.06,
    ) -> Image.Image:
        x0 = float(box["x0"])
        y0 = float(box["y0"])
        x1 = float(box["x1"])
        y1 = float(box["y1"])
        dx = (x1 - x0) * margin
        dy = (y1 - y0) * margin
        x0 = max(0.0, x0 - dx)
        x1 = min(1.0, x1 + dx)
        y0 = max(0.0, y0 - dy)
        y1 = min(1.0, y1 + dy)
        left = max(
            0,
            min(
                image.width - 1,
                int(math.floor(x0 * image.width)),
            ),
        )
        right = max(
            left + 1,
            min(
                image.width,
                int(math.ceil(x1 * image.width)),
            ),
        )
        top = max(
            0,
            min(
                image.height - 1,
                int(math.floor((1.0 - y1) * image.height)),
            ),
        )
        bottom = max(
            top + 1,
            min(
                image.height,
                int(math.ceil((1.0 - y0) * image.height)),
            ),
        )
        return image.crop((left, top, right, bottom))

    def capture_reference_from_render(
        self,
        *,
        source_media: str | Path,
        actor_id: str,
        rig_id: str,
        backend_id: CharacterBackendId = CharacterBackendId.BLENDER_BLOCK,
        costume_id: str | None = None,
    ) -> CharacterReferencePack:
        media_path = Path(source_media).resolve()
        sidecar = media_path.with_suffix(
            media_path.suffix + ".frame_qc.json"
        )
        if not sidecar.is_file():
            raise RuntimeError(
                "CHARACTER_REFERENCE_FRAME_QC_SIDECAR_MISSING"
            )
        qc = RenderedFrameQCResult.model_validate_json(
            sidecar.read_text(encoding="utf-8")
        )
        if actor_id not in qc.actors:
            raise RuntimeError(
                "CHARACTER_REFERENCE_ACTOR_EVIDENCE_MISSING:"
                + actor_id
            )
        evidence = qc.actors[actor_id]
        record = self.record_for_rig(rig_id)
        source_hash = self._sha256(media_path)
        ref_id = (
            "REF_"
            + hashlib.sha256(
                (
                    record.global_character_id
                    + "|"
                    + actor_id
                    + "|"
                    + source_hash
                ).encode("utf-8")
            ).hexdigest()[:18]
        )
        try:
            existing_pack = self.store.get_reference(
                record.global_character_id,
                ref_id,
            )
        except KeyError:
            existing_pack = None
        if existing_pack is not None:
            # The same immutable source media cannot be relabeled as a
            # newer costume/accessory state merely because the character
            # state advanced after the render was created.
            if ref_id not in record.reference_ids:
                record.reference_ids.append(ref_id)
                self.store.save_record(record)
            return existing_pack

        folder = (
            self.store.references
            / self.store._safe(
                record.global_character_id
            )
        )
        folder.mkdir(parents=True, exist_ok=True)
        crop_path = folder / (
            self.store._safe(ref_id) + ".png"
        )
        if not crop_path.is_file():
            frame_path = folder / (
                self.store._safe(ref_id)
                + ".source.png"
            )
            self.media.extract_frame(
                media_path,
                frame_path,
                time_seconds=float(
                    qc.mid.time_seconds
                ),
            )
            try:
                with Image.open(frame_path) as image:
                    crop = self._crop(
                        image.convert("RGB"),
                        evidence.screen_box,
                    )
                    crop.save(crop_path)
            finally:
                frame_path.unlink(
                    missing_ok=True
                )
        state = record.current_state
        pack = CharacterReferencePack(
            reference_id=ref_id,
            global_character_id=(
                record.global_character_id
            ),
            actor_id=actor_id,
            rig_id=rig_id,
            backend_id=backend_id,
            source_media_path=str(media_path),
            source_media_sha256=source_hash,
            crop_path=str(crop_path),
            crop_sha256=self._sha256(crop_path),
            screen_box=dict(evidence.screen_box),
            evidence=evidence,
            state_version=state.version,
            costume_id=costume_id or state.costume_id,
            accessories=list(state.accessories),
        )
        self.store.save_reference(pack)
        if ref_id not in record.reference_ids:
            record.reference_ids.append(ref_id)
            self.store.save_record(record)
        return pack

    def capture_reference_metadata(
        self,
        *,
        source_media: str | Path,
        actors: list[Any],
    ) -> dict[str, Any]:
        screen_boxes: dict[str, dict[str, float]] = {}
        character_ids: dict[str, str] = {}
        reference_ids: dict[str, str] = {}
        descriptors: dict[str, str] = {}
        for actor in actors:
            try:
                pack = self.capture_reference_from_render(
                    source_media=source_media,
                    actor_id=str(actor.actor_id),
                    rig_id=str(actor.rig_id),
                )
            except Exception:
                continue
            actor_id = str(actor.actor_id)
            screen_boxes[actor_id] = dict(
                pack.screen_box
            )
            character_ids[actor_id] = (
                pack.global_character_id
            )
            reference_ids[actor_id] = (
                pack.reference_id
            )
            descriptors[actor_id] = (
                self.descriptor_for_rig(
                    str(actor.rig_id)
                )
            )
        return {
            "actor_screen_boxes": screen_boxes,
            "global_character_ids": character_ids,
            "actor_reference_ids": reference_ids,
            "actor_identity_descriptors": descriptors,
        }

    @staticmethod
    def _candidate_boxes(
        base: dict[str, float],
    ) -> list[dict[str, float]]:
        x0 = float(base["x0"])
        y0 = float(base["y0"])
        x1 = float(base["x1"])
        y1 = float(base["y1"])
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        width = max(0.02, x1 - x0)
        height = max(0.02, y1 - y0)
        rows: list[dict[str, float]] = []
        for scale in (0.88, 1.0, 1.12):
            sw = width * scale
            sh = height * scale
            for dx in (-0.18, -0.09, 0.0, 0.09, 0.18):
                for dy in (-0.12, 0.0, 0.12):
                    nx0 = max(0.0, cx + dx * width - sw / 2.0)
                    nx1 = min(1.0, cx + dx * width + sw / 2.0)
                    ny0 = max(0.0, cy + dy * height - sh / 2.0)
                    ny1 = min(1.0, cy + dy * height + sh / 2.0)
                    if nx1 - nx0 < 0.02 or ny1 - ny0 < 0.02:
                        continue
                    rows.append(
                        {
                            "x0": nx0,
                            "y0": ny0,
                            "x1": nx1,
                            "y1": ny1,
                            "area": float(
                                (nx1 - nx0) * (ny1 - ny0)
                            ),
                        }
                    )
        return rows

    def _track_sample(
        self,
        *,
        image: Image.Image,
        actor_id: str,
        pack: CharacterReferencePack,
        base_box: dict[str, float],
    ) -> tuple[ActorAppearanceEvidence | None, float | None]:
        best_evidence = None
        best_score = None
        for box in self._candidate_boxes(base_box):
            evidence = RenderedFrameAnalyzer._actor_evidence(
                actor_id,
                image,
                box,
            )
            if evidence is None:
                continue
            comparison = self.evaluator.compare_actor(
                pack.evidence,
                evidence,
            )
            if comparison.score is None:
                continue
            if best_score is None or comparison.score > best_score:
                best_score = comparison.score
                best_evidence = evidence
        return best_evidence, best_score

    @staticmethod
    def _screen_box_iou(
        a: dict[str, float], b: dict[str, float]
    ) -> float:
        x0 = max(float(a["x0"]), float(b["x0"]))
        y0 = max(float(a["y0"]), float(b["y0"]))
        x1 = min(float(a["x1"]), float(b["x1"]))
        y1 = min(float(a["y1"]), float(b["y1"]))
        overlap = max(0.0, x1 - x0) * max(0.0, y1 - y0)
        area_a = max(0.0, float(a["x1"]) - float(a["x0"])) * max(
            0.0, float(a["y1"]) - float(a["y0"])
        )
        area_b = max(0.0, float(b["x1"]) - float(b["x0"])) * max(
            0.0, float(b["y1"]) - float(b["y0"])
        )
        union = area_a + area_b - overlap
        return overlap / union if union > 0.0 else 0.0

    def track_video_output(
        self,
        *,
        actor_reference_ids: dict[str, str],
        global_character_ids: dict[str, str],
        video_path: str | Path,
    ) -> MultiActorTrackingReport:
        video = Path(video_path).resolve()
        probe = self.media.probe(video)
        duration = float(probe.duration or 0.0)
        if duration <= 0:
            return MultiActorTrackingReport(
                passed=False,
                measured=False,
                findings=["ACTOR_TRACK_VIDEO_DURATION_INVALID"],
            )

        expected_actors = set(actor_reference_ids) | set(global_character_ids)
        missing_binding = sorted(
            actor_id for actor_id in expected_actors
            if not actor_reference_ids.get(actor_id)
            or not global_character_ids.get(actor_id)
        )
        if missing_binding:
            return MultiActorTrackingReport(
                passed=False,
                measured=False,
                findings=[
                    f"ACTOR_TRACK_BINDING_MISSING:{actor_id}"
                    for actor_id in missing_binding
                ],
            )

        packs: dict[str, CharacterReferencePack] = {}
        for actor_id, reference_id in actor_reference_ids.items():
            global_id = global_character_ids.get(actor_id)
            if not global_id:
                continue
            try:
                packs[actor_id] = self.store.get_reference(
                    global_id,
                    reference_id,
                )
            except KeyError:
                continue
        missing_packs = sorted(expected_actors - set(packs))
        if missing_packs:
            return MultiActorTrackingReport(
                passed=False,
                measured=False,
                findings=[
                    f"ACTOR_TRACK_REFERENCE_MISSING:{actor_id}"
                    for actor_id in missing_packs
                ],
            )

        edge = min(0.12, duration * 0.08)
        times = [
            ("head", min(edge, max(0.0, duration - 0.08))),
            ("mid", duration / 2.0),
            ("tail", max(0.0, duration - max(0.08, edge))),
        ]
        tracks: list[ActorTrackReport] = []
        with tempfile.TemporaryDirectory(
            prefix=".cf_actor_track_",
            dir=str(video.parent),
        ) as temp_dir:
            temp = Path(temp_dir)
            images: dict[str, Image.Image] = {}
            for label, second in times:
                frame = self.media.extract_frame(
                    video,
                    temp / f"{label}.png",
                    time_seconds=second,
                )
                with Image.open(frame) as image:
                    images[label] = image.convert("RGB").copy()

            for actor_id, pack in packs.items():
                samples: list[ActorTrackSample] = []
                findings: list[str] = []
                base_box = dict(pack.screen_box)
                for label, second in times:
                    evidence, score = self._track_sample(
                        image=images[label],
                        actor_id=actor_id,
                        pack=pack,
                        base_box=base_box,
                    )
                    if evidence is None or score is None:
                        findings.append(
                            f"ACTOR_TRACK_SAMPLE_MISSING:{actor_id}:{label}"
                        )
                        continue
                    samples.append(
                        ActorTrackSample(
                            label=label,
                            time_seconds=second,
                            screen_box=dict(evidence.screen_box),
                            score=score,
                            evidence=evidence,
                        )
                    )
                    base_box = dict(evidence.screen_box)

                scores = [sample.score for sample in samples]
                measured = len(samples) == len(times)
                minimum = min(scores) if scores else None
                passed = bool(
                    measured
                    and minimum is not None
                    and minimum >= self.identity_floor
                )
                if minimum is not None and minimum < self.identity_floor:
                    findings.append(
                        "ACTOR_TRACK_IDENTITY_BELOW_FLOOR:"
                        f"{actor_id}:{minimum:.4f}"
                    )
                tracks.append(
                    ActorTrackReport(
                        actor_id=actor_id,
                        global_character_id=pack.global_character_id,
                        reference_id=pack.reference_id,
                        measured=measured,
                        passed=passed,
                        minimum_score=minimum,
                        samples=samples,
                        findings=sorted(set(findings)),
                    )
                )

        # A high appearance score is not enough if two actor tracks
        # resolve to effectively the same on-screen region.
        for index, left in enumerate(tracks):
            left_samples = {sample.label: sample for sample in left.samples}
            for right in tracks[index + 1:]:
                right_samples = {
                    sample.label: sample for sample in right.samples
                }
                for label in sorted(left_samples.keys() & right_samples.keys()):
                    overlap = self._screen_box_iou(
                        left_samples[label].screen_box,
                        right_samples[label].screen_box,
                    )
                    if overlap >= 0.70:
                        finding = (
                            f"ACTOR_TRACK_BOX_COLLISION:{left.actor_id}:"
                            f"{right.actor_id}:{label}:{overlap:.4f}"
                        )
                        left.passed = False
                        right.passed = False
                        left.findings.append(finding)
                        right.findings.append(finding)

        all_scores = [
            track.minimum_score
            for track in tracks
            if track.minimum_score is not None
        ]
        findings = [
            finding
            for track in tracks
            for finding in track.findings
        ]
        measured = bool(tracks) and all(
            track.measured for track in tracks
        )
        passed = bool(tracks) and all(
            track.passed for track in tracks
        )
        return MultiActorTrackingReport(
            passed=passed,
            measured=measured,
            minimum_score=min(all_scores) if all_scores else None,
            tracks=tracks,
            findings=sorted(set(findings)),
        )

    def evaluate_video_output(
        self,
        *,
        actor_reference_ids: dict[str, str],
        global_character_ids: dict[str, str],
        video_path: str | Path,
    ) -> tuple[
        MultiCharacterIdentityReport,
        MultiActorTrackingReport,
    ]:
        tracking = self.track_video_output(
            actor_reference_ids=actor_reference_ids,
            global_character_ids=global_character_ids,
            video_path=video_path,
        )
        current_actors: dict[str, ActorAppearanceEvidence] = {}
        for track in tracking.tracks:
            if not track.samples:
                continue
            # Use the weakest measured frame as the conservative identity
            # evidence so a strong middle frame cannot hide drift elsewhere.
            weakest = min(
                track.samples,
                key=lambda sample: sample.score,
            )
            current_actors[track.actor_id] = weakest.evidence
        identity = self.evaluate_output(
            actor_reference_ids=actor_reference_ids,
            global_character_ids=global_character_ids,
            current_actors=current_actors,
        )
        combined_findings = sorted(
            set([*identity.findings, *tracking.findings])
        )
        if not tracking.passed:
            identity = identity.model_copy(
                update={
                    "passed": False,
                    "findings": combined_findings,
                    "minimum_score": (
                        min(
                            [
                                value
                                for value in (
                                    identity.minimum_score,
                                    tracking.minimum_score,
                                )
                                if value is not None
                            ]
                        )
                        if (
                            identity.minimum_score is not None
                            or tracking.minimum_score is not None
                        )
                        else None
                    ),
                }
            )
        return identity, tracking

    def evaluate_output(
        self,
        *,
        actor_reference_ids: dict[str, str],
        global_character_ids: dict[str, str],
        current_actors: dict[
            str,
            ActorAppearanceEvidence,
        ],
    ) -> MultiCharacterIdentityReport:
        assessments: list[ActorIdentityAssessment] = []
        baselines: dict[
            str,
            CharacterReferencePack,
        ] = {}
        for actor_id, reference_id in actor_reference_ids.items():
            global_id = global_character_ids.get(actor_id)
            if not global_id:
                continue
            try:
                baselines[actor_id] = self.store.get_reference(
                    global_id,
                    reference_id,
                )
            except KeyError:
                continue

        for actor_id, pack in baselines.items():
            current = current_actors.get(actor_id)
            try:
                current_record = self.store.get_record(
                    pack.global_character_id
                )
            except KeyError:
                current_record = None
            stale_state = bool(
                current_record is not None
                and pack.state_version
                != current_record.current_state.version
            )
            if current is None:
                assessments.append(
                    ActorIdentityAssessment(
                        actor_id=actor_id,
                        global_character_id=(
                            pack.global_character_id
                        ),
                        reference_id=pack.reference_id,
                        measured=False,
                        passed=False,
                        findings=[
                            "ACTOR_IDENTITY_OUTPUT_EVIDENCE_MISSING"
                        ],
                    )
                )
                continue
            comparison = self.evaluator.compare_actor(
                pack.evidence,
                current,
            )
            score = comparison.score
            findings = list(comparison.findings)
            if stale_state:
                findings.append(
                    "CHARACTER_REFERENCE_STATE_VERSION_STALE:"
                    f"{actor_id}:reference={pack.state_version}:"
                    f"current={current_record.current_state.version}"
                )
            passed = bool(
                comparison.measured
                and score is not None
                and score >= self.identity_floor
                and not stale_state
            )
            if (
                not comparison.measured
                or score is None
                or score < self.identity_floor
            ):
                findings.append(
                    "ACTOR_IDENTITY_SCORE_BELOW_FLOOR:"
                    f"{actor_id}:"
                    f"{float(score or 0.0):.4f}"
                )

            competing_id = None
            competing_score = None
            for other_actor, other_pack in baselines.items():
                if other_actor == actor_id:
                    continue
                other = self.evaluator.compare_actor(
                    other_pack.evidence,
                    current,
                )
                if (
                    other.score is not None
                    and (
                        competing_score is None
                        or other.score > competing_score
                    )
                ):
                    competing_score = other.score
                    competing_id = (
                        other_pack.global_character_id
                    )
            if (
                score is not None
                and competing_score is not None
                and competing_score >= self.identity_floor
                and competing_score
                >= score + self.collision_margin
            ):
                passed = False
                findings.append(
                    "CHARACTER_IDENTITY_COLLISION:"
                    f"{actor_id}:expected="
                    f"{pack.global_character_id}:"
                    f"other={competing_id}:"
                    f"expected_score={score:.4f}:"
                    f"other_score={competing_score:.4f}"
                )
            assessments.append(
                ActorIdentityAssessment(
                    actor_id=actor_id,
                    global_character_id=(
                        pack.global_character_id
                    ),
                    reference_id=pack.reference_id,
                    measured=True,
                    passed=passed,
                    score=score,
                    comparison=comparison,
                    competing_character_id=(
                        competing_id
                    ),
                    competing_score=(
                        competing_score
                    ),
                    findings=sorted(
                        set(findings)
                    ),
                )
            )

        measured_scores = [
            item.score
            for item in assessments
            if item.measured and item.score is not None
        ]
        findings = [
            finding
            for item in assessments
            for finding in item.findings
        ]
        collision_findings = [
            item
            for item in findings
            if item.startswith(
                "CHARACTER_IDENTITY_COLLISION:"
            )
        ]
        measured = bool(assessments) and all(
            item.measured
            for item in assessments
        )
        passed = bool(assessments) and all(
            item.passed
            for item in assessments
        )
        return MultiCharacterIdentityReport(
            passed=passed,
            measured=measured,
            minimum_score=(
                min(measured_scores)
                if measured_scores
                else None
            ),
            assessments=assessments,
            collision_findings=collision_findings,
            findings=sorted(set(findings)),
        )

    def evaluate_transition(
        self,
        *,
        previous_backend: CharacterBackendId,
        current_backend: CharacterBackendId,
        actor_to_global: dict[str, str],
        previous_actors: dict[str, ActorAppearanceEvidence],
        current_actors: dict[str, ActorAppearanceEvidence],
    ) -> CharacterTransitionReport:
        transitions: list[CharacterTransitionAssessment] = []
        findings: list[str] = []
        for actor_id, global_id in actor_to_global.items():
            previous = previous_actors.get(actor_id)
            current = current_actors.get(actor_id)
            if previous is None or current is None:
                row_findings = [
                    "CHARACTER_TRANSITION_EVIDENCE_MISSING:"
                    f"{actor_id}"
                ]
                findings.extend(row_findings)
                transitions.append(
                    CharacterTransitionAssessment(
                        actor_id=actor_id,
                        global_character_id=global_id,
                        previous_backend=previous_backend,
                        current_backend=current_backend,
                        measured=False,
                        passed=False,
                        findings=row_findings,
                    )
                )
                continue
            comparison = self.evaluator.compare_actor(
                previous,
                current,
            )
            score = comparison.score
            passed = bool(
                comparison.measured
                and score is not None
                and score >= self.identity_floor
            )
            row_findings = list(comparison.findings)
            if not passed:
                row_findings.append(
                    "CHARACTER_TRANSITION_IDENTITY_BELOW_FLOOR:"
                    f"{actor_id}:{float(score or 0.0):.4f}"
                )
            findings.extend(row_findings)
            transitions.append(
                CharacterTransitionAssessment(
                    actor_id=actor_id,
                    global_character_id=global_id,
                    previous_backend=previous_backend,
                    current_backend=current_backend,
                    measured=comparison.measured,
                    passed=passed,
                    score=score,
                    comparison=comparison,
                    findings=sorted(set(row_findings)),
                )
            )
        scores = [
            item.score
            for item in transitions
            if item.measured and item.score is not None
        ]
        measured = bool(transitions) and all(
            item.measured for item in transitions
        )
        passed = bool(transitions) and all(
            item.passed for item in transitions
        )
        return CharacterTransitionReport(
            passed=passed,
            measured=measured,
            minimum_score=min(scores) if scores else None,
            transitions=transitions,
            findings=sorted(set(findings)),
        )

    def update_state(
        self,
        global_character_id: str,
        *,
        costume_id: str | None = None,
        accessories: list[str] | None = None,
        notes: list[str] | None = None,
    ) -> CharacterIdentityRecord:
        record = self.store.get_record(
            global_character_id
        )
        current = record.current_state
        next_state = CharacterStateVersion(
            version=current.version + 1,
            costume_id=(
                costume_id
                if costume_id is not None
                else current.costume_id
            ),
            accessories=(
                list(accessories)
                if accessories is not None
                else list(current.accessories)
            ),
            expression_profile=(
                current.expression_profile
            ),
            notes=list(notes or []),
        )
        record.state_versions.append(next_state)
        return self.store.save_record(record)

