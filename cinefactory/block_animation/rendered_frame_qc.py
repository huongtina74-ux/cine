from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image
from pydantic import BaseModel, Field

from cinefactory.media.ffmpeg import FFmpegToolchain


class FrameAppearanceMetrics(BaseModel):
    label: str
    time_seconds: float = Field(ge=0)
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    luma_mean: float = Field(ge=0.0, le=1.0)
    luma_std: float = Field(ge=0.0, le=1.0)
    shadow_clip_ratio: float = Field(ge=0.0, le=1.0)
    highlight_clip_ratio: float = Field(ge=0.0, le=1.0)
    saturation_mean: float = Field(ge=0.0, le=1.0)
    rgb_mean: list[float]
    ahash64: str


class ActorAppearanceEvidence(BaseModel):
    actor_id: str
    screen_box: dict[str, float]
    crop_width: int = Field(ge=1)
    crop_height: int = Field(ge=1)
    luma_mean: float = Field(ge=0.0, le=1.0)
    saturation_mean: float = Field(ge=0.0, le=1.0)
    rgb_mean: list[float]
    hsv_histogram: list[float]
    ahash64: str


class RenderedFrameQCResult(BaseModel):
    passed: bool
    findings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    head: FrameAppearanceMetrics
    mid: FrameAppearanceMetrics
    tail: FrameAppearanceMetrics
    actors: dict[str, ActorAppearanceEvidence] = Field(default_factory=dict)
    sidecar_path: str | None = None


class ActorAppearanceComparison(BaseModel):
    actor_id: str
    measured: bool
    passed: bool
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    histogram_similarity: float | None = Field(default=None, ge=0.0, le=1.0)
    hash_similarity: float | None = Field(default=None, ge=0.0, le=1.0)
    rgb_distance: float | None = Field(default=None, ge=0.0)
    findings: list[str] = Field(default_factory=list)


class CutAppearanceComparison(BaseModel):
    measured: bool
    passed: bool
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    luma_delta: float | None = Field(default=None, ge=0.0)
    saturation_delta: float | None = Field(default=None, ge=0.0)
    rgb_distance: float | None = Field(default=None, ge=0.0)
    findings: list[str] = Field(default_factory=list)


class RenderedFrameAnalyzer:
    """Zero-API rendered-frame QC using FFmpeg + NumPy + Pillow.

    It deliberately measures signal/appearance evidence only. It does not claim
    semantic face recognition or aesthetic superiority.
    """

    def __init__(self, media: FFmpegToolchain | None = None) -> None:
        self.media = media or FFmpegToolchain()

    @staticmethod
    def _rgb_array(image: Image.Image) -> np.ndarray:
        return np.asarray(image.convert("RGB"), dtype=np.float32) / 255.0

    @staticmethod
    def _ahash64(image: Image.Image) -> str:
        gray = image.convert("L").resize((8, 8), Image.Resampling.BILINEAR)
        data = np.asarray(gray, dtype=np.float32)
        bits = (data >= float(data.mean())).reshape(-1)
        value = 0
        for bit in bits:
            value = (value << 1) | int(bool(bit))
        return f"{value:016x}"

    @staticmethod
    def _metrics(
        image: Image.Image,
        *,
        label: str,
        time_seconds: float,
    ) -> FrameAppearanceMetrics:
        rgb = RenderedFrameAnalyzer._rgb_array(image)
        luma = (
            0.2126 * rgb[:, :, 0]
            + 0.7152 * rgb[:, :, 1]
            + 0.0722 * rgb[:, :, 2]
        )
        saturation = rgb.max(axis=2) - rgb.min(axis=2)
        rgb_mean = [
            float(value)
            for value in rgb.mean(axis=(0, 1))
        ]
        return FrameAppearanceMetrics(
            label=label,
            time_seconds=float(time_seconds),
            width=image.width,
            height=image.height,
            luma_mean=float(luma.mean()),
            luma_std=float(luma.std()),
            shadow_clip_ratio=float((luma <= 0.02).mean()),
            highlight_clip_ratio=float((luma >= 0.98).mean()),
            saturation_mean=float(saturation.mean()),
            rgb_mean=rgb_mean,
            ahash64=RenderedFrameAnalyzer._ahash64(image),
        )

    @staticmethod
    def _crop(
        image: Image.Image,
        box: dict[str, Any],
        *,
        margin: float = 0.06,
    ) -> Image.Image | None:
        try:
            x0 = float(box["x0"])
            y0 = float(box["y0"])
            x1 = float(box["x1"])
            y1 = float(box["y1"])
        except (KeyError, TypeError, ValueError):
            return None
        if x1 <= x0 or y1 <= y0:
            return None
        dx = (x1 - x0) * margin
        dy = (y1 - y0) * margin
        x0 = max(0.0, x0 - dx)
        x1 = min(1.0, x1 + dx)
        y0 = max(0.0, y0 - dy)
        y1 = min(1.0, y1 + dy)

        left = int(math.floor(x0 * image.width))
        right = int(math.ceil(x1 * image.width))
        # Blender NDC uses bottom-left origin; PIL uses top-left.
        top = int(math.floor((1.0 - y1) * image.height))
        bottom = int(math.ceil((1.0 - y0) * image.height))
        left = max(0, min(image.width - 1, left))
        right = max(left + 1, min(image.width, right))
        top = max(0, min(image.height - 1, top))
        bottom = max(top + 1, min(image.height, bottom))
        if right - left < 4 or bottom - top < 4:
            return None
        return image.crop((left, top, right, bottom))

    @staticmethod
    def _hsv_histogram(image: Image.Image) -> list[float]:
        hsv = np.asarray(
            image.convert("HSV").resize(
                (96, 96),
                Image.Resampling.BILINEAR,
            ),
            dtype=np.float32,
        )
        hue = hsv[:, :, 0].reshape(-1)
        sat = hsv[:, :, 1].reshape(-1)
        hist, _, _ = np.histogram2d(
            hue,
            sat,
            bins=(12, 4),
            range=((0.0, 256.0), (0.0, 256.0)),
        )
        hist = hist.astype(np.float64)
        total = float(hist.sum())
        if total > 0:
            hist /= total
        return [float(x) for x in hist.reshape(-1)]

    @classmethod
    def _actor_evidence(
        cls,
        actor_id: str,
        image: Image.Image,
        box: dict[str, Any],
    ) -> ActorAppearanceEvidence | None:
        crop = cls._crop(image, box)
        if crop is None:
            return None
        rgb = cls._rgb_array(crop)
        luma = (
            0.2126 * rgb[:, :, 0]
            + 0.7152 * rgb[:, :, 1]
            + 0.0722 * rgb[:, :, 2]
        )
        saturation = rgb.max(axis=2) - rgb.min(axis=2)
        return ActorAppearanceEvidence(
            actor_id=actor_id,
            screen_box={
                key: float(box[key])
                for key in ("x0", "y0", "x1", "y1", "area")
                if key in box
            },
            crop_width=crop.width,
            crop_height=crop.height,
            luma_mean=float(luma.mean()),
            saturation_mean=float(saturation.mean()),
            rgb_mean=[
                float(value)
                for value in rgb.mean(axis=(0, 1))
            ],
            hsv_histogram=cls._hsv_histogram(crop),
            ahash64=cls._ahash64(crop),
        )

    @staticmethod
    def _quality_findings(
        frames: list[FrameAppearanceMetrics],
        *,
        lighting: dict[str, Any] | None = None,
    ) -> tuple[list[str], list[str]]:
        blockers: list[str] = []
        warnings: list[str] = []
        lighting = lighting or {}
        time_of_day = str(
            lighting.get("time_of_day") or ""
        ).strip().lower()
        low_light_intent = any(
            token in time_of_day
            for token in ("night", "evening", "dusk")
        )

        if low_light_intent:
            hard_shadow = 0.86
            hard_luma = 0.035
            warning_shadow = 0.68
        else:
            hard_shadow = 0.45
            hard_luma = 0.055
            warning_shadow = 0.36

        for frame in frames:
            prefix = frame.label.upper()
            severe_underexposure = (
                frame.shadow_clip_ratio > 0.80
                and frame.luma_mean < 0.12
            )
            intent_adjusted_underexposure = (
                frame.shadow_clip_ratio > hard_shadow
                and frame.luma_mean < hard_luma
            )
            if (
                severe_underexposure
                or intent_adjusted_underexposure
            ):
                blockers.append(
                    f"RENDERED_FRAME_UNDEREXPOSED:{prefix}"
                )
            elif frame.shadow_clip_ratio > warning_shadow:
                warnings.append(
                    f"RENDERED_FRAME_SHADOW_CLIP_HIGH:{prefix}:"
                    f"{frame.shadow_clip_ratio:.3f}"
                )

            if (
                frame.highlight_clip_ratio > 0.65
                and frame.luma_mean > 0.82
            ):
                blockers.append(
                    f"RENDERED_FRAME_OVEREXPOSED:{prefix}"
                )
            elif frame.highlight_clip_ratio > 0.25:
                warnings.append(
                    f"RENDERED_FRAME_HIGHLIGHT_CLIP_HIGH:{prefix}:"
                    f"{frame.highlight_clip_ratio:.3f}"
                )

            if frame.luma_std < 0.012:
                warnings.append(
                    f"RENDERED_FRAME_LOW_CONTRAST:{prefix}:"
                    f"{frame.luma_std:.4f}"
                )
        return blockers, warnings

    def analyze(
        self,
        path: str | Path,
        *,
        render_state: dict[str, Any] | None = None,
    ) -> RenderedFrameQCResult:
        video = Path(path).resolve()
        probe = self.media.probe(video)
        if probe.duration <= 0:
            raise RuntimeError(
                f"rendered-frame QC requires positive duration: {video}"
            )
        fps = float(probe.fps or 24.0)
        frame_margin = max(0.08, 2.0 / max(fps, 1.0))
        max_time = max(0.0, probe.duration - frame_margin)
        edge = min(
            0.12,
            max(1.0 / max(fps, 1.0), probe.duration * 0.08),
        )
        times = {
            "head": min(edge, max_time),
            "mid": min(probe.duration / 2, max_time),
            "tail": max_time,
        }
        images: dict[str, Image.Image] = {}
        with tempfile.TemporaryDirectory(
            prefix=".cf_frame_qc_",
            dir=str(video.parent),
        ) as temp:
            temp_dir = Path(temp)
            for label, second in times.items():
                frame = self.media.extract_frame(
                    video,
                    temp_dir / f"{label}.png",
                    time_seconds=second,
                )
                with Image.open(frame) as image:
                    images[label] = image.convert("RGB").copy()

        head = self._metrics(
            images["head"],
            label="head",
            time_seconds=times["head"],
        )
        mid = self._metrics(
            images["mid"],
            label="mid",
            time_seconds=times["mid"],
        )
        tail = self._metrics(
            images["tail"],
            label="tail",
            time_seconds=times["tail"],
        )

        actors: dict[str, ActorAppearanceEvidence] = {}
        actor_states = (render_state or {}).get("actors") or {}
        for actor_id, state in actor_states.items():
            box = ((state or {}).get("mid") or {}).get("screen_box")
            if not box:
                continue
            evidence = self._actor_evidence(
                str(actor_id),
                images["mid"],
                box,
            )
            if evidence is not None:
                actors[str(actor_id)] = evidence

        blockers, warnings = self._quality_findings(
            [head, mid, tail],
            lighting=(render_state or {}).get("lighting") or {},
        )
        result = RenderedFrameQCResult(
            passed=not blockers,
            findings=blockers,
            warnings=warnings,
            head=head,
            mid=mid,
            tail=tail,
            actors=actors,
        )
        sidecar = video.with_suffix(video.suffix + ".frame_qc.json")
        payload = result.model_dump(mode="json")
        payload["sidecar_path"] = str(sidecar)
        sidecar.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        return result.model_copy(
            update={"sidecar_path": str(sidecar)}
        )


class RenderedAppearanceEvaluator:
    """Compare measured rendered appearance across accepted shots."""

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        va = np.asarray(a, dtype=np.float64)
        vb = np.asarray(b, dtype=np.float64)
        denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
        if denom <= 1e-12:
            return 0.0
        return max(0.0, min(1.0, float(np.dot(va, vb) / denom)))

    @staticmethod
    def _hash_similarity(a: str, b: str) -> float:
        try:
            xa = int(a, 16)
            xb = int(b, 16)
        except (TypeError, ValueError):
            return 0.0
        distance = (xa ^ xb).bit_count()
        return max(0.0, 1.0 - distance / 64.0)

    @staticmethod
    def _rgb_distance(a: list[float], b: list[float]) -> float:
        return float(
            np.linalg.norm(
                np.asarray(a, dtype=np.float64)
                - np.asarray(b, dtype=np.float64)
            )
        )

    def compare_actor(
        self,
        reference: ActorAppearanceEvidence,
        current: ActorAppearanceEvidence,
    ) -> ActorAppearanceComparison:
        hist = self._cosine(
            reference.hsv_histogram,
            current.hsv_histogram,
        )
        hash_similarity = self._hash_similarity(
            reference.ahash64,
            current.ahash64,
        )
        rgb_distance = self._rgb_distance(
            reference.rgb_mean,
            current.rgb_mean,
        )
        score = max(
            0.0,
            min(
                1.0,
                0.70 * hist
                + 0.20 * hash_similarity
                + 0.10 * max(0.0, 1.0 - rgb_distance / 0.65),
            ),
        )
        findings: list[str] = []
        hard = score < 0.48 or hist < 0.38
        if hard:
            findings.append(
                f"RENDERED_IDENTITY_DRIFT:{current.actor_id}:"
                f"score={score:.3f}:hist={hist:.3f}:"
                f"hash={hash_similarity:.3f}"
            )
        elif score < 0.62 or hist < 0.52:
            findings.append(
                f"RENDERED_IDENTITY_WARNING:{current.actor_id}:"
                f"score={score:.3f}:hist={hist:.3f}"
            )
        return ActorAppearanceComparison(
            actor_id=current.actor_id,
            measured=True,
            passed=not hard,
            score=score,
            histogram_similarity=hist,
            hash_similarity=hash_similarity,
            rgb_distance=rgb_distance,
            findings=findings,
        )

    def compare_cut(
        self,
        previous: FrameAppearanceMetrics,
        current: FrameAppearanceMetrics,
        *,
        same_scene: bool,
        same_lighting_intent: bool,
    ) -> CutAppearanceComparison:
        if not same_scene or not same_lighting_intent:
            return CutAppearanceComparison(
                measured=False,
                passed=True,
                findings=[
                    "CUT_APPEARANCE_NOT_MEASURED:"
                    + (
                        "SCENE_TRANSITION"
                        if not same_scene
                        else "LIGHTING_INTENT_CHANGED"
                    )
                ],
            )

        luma_delta = abs(
            float(previous.luma_mean) - float(current.luma_mean)
        )
        sat_delta = abs(
            float(previous.saturation_mean)
            - float(current.saturation_mean)
        )
        rgb_distance = self._rgb_distance(
            previous.rgb_mean,
            current.rgb_mean,
        )
        luma_score = max(0.0, 1.0 - luma_delta / 0.30)
        sat_score = max(0.0, 1.0 - sat_delta / 0.30)
        rgb_score = max(0.0, 1.0 - rgb_distance / 0.45)
        score = (
            0.45 * luma_score
            + 0.20 * sat_score
            + 0.35 * rgb_score
        )
        hard = luma_delta > 0.28 or rgb_distance > 0.38
        findings: list[str] = []
        if hard:
            findings.append(
                "CUT_APPEARANCE_DRIFT:"
                f"luma={luma_delta:.3f}:"
                f"sat={sat_delta:.3f}:rgb={rgb_distance:.3f}"
            )
        else:
            if luma_delta > 0.16:
                findings.append(
                    f"CUT_EXPOSURE_WARNING:{luma_delta:.3f}"
                )
            if rgb_distance > 0.22:
                findings.append(
                    f"CUT_COLOR_WARNING:{rgb_distance:.3f}"
                )
        return CutAppearanceComparison(
            measured=True,
            passed=not hard,
            score=max(0.0, min(1.0, score)),
            luma_delta=luma_delta,
            saturation_delta=sat_delta,
            rgb_distance=rgb_distance,
            findings=findings,
        )
