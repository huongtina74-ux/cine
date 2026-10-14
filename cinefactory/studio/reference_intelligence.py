from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import statistics
import subprocess
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from .intelligence import (
    CompetitorVideoProfile,
    NichePlaybook,
    NichePlaybookCompiler,
    ObservationType,
    PatternEvidence,
    PatternMiner,
    VideoObservation,
)


class ReferenceIntelligenceHealth(BaseModel):
    yt_dlp_available: bool = False
    ffmpeg_available: bool = False
    ffprobe_available: bool = False
    opencv_available: bool = False
    url_video_analysis_ready: bool = False
    local_video_analysis_ready: bool = False
    capabilities: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)


class ReferenceAcquisitionPolicy(BaseModel):
    max_duration_seconds: int = Field(default=2400, ge=30)
    max_height: int = Field(default=720, ge=144, le=2160)
    max_channel_videos: int = Field(default=5, ge=1, le=20)
    scene_threshold: float = Field(default=0.30, ge=0.05, le=0.95)
    silence_db: float = Field(default=-38.0, le=-5.0)
    silence_min_seconds: float = Field(default=0.35, ge=0.1)
    subtitle_languages: list[str] = Field(
        default_factory=lambda: ["en.*", "vi.*"]
    )
    retain_downloaded_media: bool = False
    include_livestreams: bool = False


class VideoSourceMetadata(BaseModel):
    video_id: str
    source_url: str
    title: str | None = None
    channel: str | None = None
    channel_id: str | None = None
    duration_seconds: float | None = None
    upload_date: str | None = None
    view_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    categories: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    description_present: bool = False
    live_status: str | None = None
    was_live: bool = False


class TranscriptStats(BaseModel):
    available: bool = False
    cue_count: int = 0
    estimated_word_count: int = 0
    words_per_minute: float | None = None
    first_spoken_seconds: float | None = None
    first_30s_word_count: int = 0
    question_cue_count: int = 0
    numeric_cue_count: int = 0
    transcript_sha256: str | None = None


class VisualRhythmStats(BaseModel):
    scene_count: int = 0
    cut_count: int = 0
    cuts_per_minute: float = 0.0
    median_shot_seconds: float | None = None
    mean_shot_seconds: float | None = None
    hook_cut_count_30s: int = 0
    long_take_ratio: float = 0.0
    motion_score_avg: float | None = None
    scene_boundaries_seconds: list[float] = Field(default_factory=list)


class CameraMotionStats(BaseModel):
    available: bool = False
    sampled_pairs: int = 0
    valid_transform_pairs: int = 0
    median_translation_norm: float | None = None
    median_rotation_degrees: float | None = None
    median_zoom_delta: float | None = None
    moving_pair_ratio: float = 0.0
    profile: str = "UNKNOWN"
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    limitations: list[str] = Field(
        default_factory=lambda: [
            (
                "global optical-flow motion is a camera-motion proxy; "
                "large subject movement can influence the estimate"
            )
        ]
    )


class AudioRhythmStats(BaseModel):
    has_audio: bool = False
    silence_count: int = 0
    silence_ratio: float = 0.0
    mean_silence_seconds: float | None = None
    mean_volume_db: float | None = None
    max_volume_db: float | None = None


class ReferenceDecomposition(BaseModel):
    source: VideoSourceMetadata
    profile: CompetitorVideoProfile
    transcript: TranscriptStats = Field(default_factory=TranscriptStats)
    visual: VisualRhythmStats = Field(default_factory=VisualRhythmStats)
    camera: CameraMotionStats = Field(default_factory=CameraMotionStats)
    audio: AudioRhythmStats = Field(default_factory=AudioRhythmStats)
    inferred_production_methods: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    quarantine_dir: str
    media_sha256: str | None = None

    def planning_profile(self) -> dict[str, Any]:
        """Safe abstraction view for PLANNING.

        It deliberately excludes title, URL, transcript text, exact scene boundary
        order, and quarantine file paths.
        """
        patterns: list[str] = []
        production: list[str] = []
        retention: list[str] = []
        format_patterns: list[str] = []
        for observation in self.profile.observations:
            if observation.expression_sensitive:
                continue
            if observation.kind is ObservationType.PRODUCTION_METHOD:
                production.append(observation.description)
            elif observation.kind is ObservationType.HOOK:
                retention.append(observation.description)
            elif observation.kind in {
                ObservationType.EDITING,
                ObservationType.CAMERA,
                ObservationType.AUDIO,
            }:
                format_patterns.append(observation.description)
            else:
                patterns.append(observation.description)
        return {
            "profile_id": self.profile.video_id,
            "patterns": list(dict.fromkeys(patterns)),
            "production_patterns": list(dict.fromkeys(production)),
            "retention_patterns": list(dict.fromkeys(retention)),
            "format_patterns": list(dict.fromkeys(format_patterns)),
            "confidence": self._mean_observation_confidence(),
            "analysis_features": {
                "duration_seconds": self.source.duration_seconds,
                "scene_count": self.visual.scene_count,
                "cuts_per_minute": self.visual.cuts_per_minute,
                "median_shot_seconds": self.visual.median_shot_seconds,
                "hook_cut_count_30s": self.visual.hook_cut_count_30s,
                "motion_score_avg": self.visual.motion_score_avg,
                "camera_motion_profile": self.camera.profile,
                "camera_motion_confidence": self.camera.confidence,
                "silence_ratio": self.audio.silence_ratio,
                "words_per_minute": self.transcript.words_per_minute,
                "first_spoken_seconds": self.transcript.first_spoken_seconds,
            },
            "raw_expression_allowed": False,
        }

    def _mean_observation_confidence(self) -> float:
        values = [
            item.confidence
            for item in self.profile.observations
            if not item.expression_sensitive
        ]
        if not values:
            return 0.5
        return round(sum(values) / len(values), 4)


class ResearchConfidenceReport(BaseModel):
    analyzed_video_count: int = Field(default=0, ge=0)
    unique_channel_count: int = Field(default=0, ge=0)
    promoted_pattern_count: int = Field(default=0, ge=0)
    mean_pattern_support_ratio: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    grade: str = "LOW"
    decision_ready: bool = False
    findings: list[str] = Field(default_factory=list)


class ResearchConfidenceEvaluator:
    def evaluate(
        self,
        decompositions: list[ReferenceDecomposition],
        patterns: list[PatternEvidence],
    ) -> ResearchConfidenceReport:
        video_count = len(decompositions)
        channels = {
            (
                getattr(item.source, "channel_id", None)
                or getattr(item.source, "channel", None)
                or (
                    "unknown:"
                    + str(
                        getattr(
                            item.source,
                            "video_id",
                            index,
                        )
                    )
                )
            )
            for index, item in enumerate(decompositions)
        }
        # Unknown channel IDs should not fake source diversity.
        known_channels = {
            item
            for item in channels
            if not item.startswith("unknown:")
        }
        unique_channels = len(known_channels)
        support_ratios = [
            pattern.support_ratio
            for pattern in patterns
            if pattern.sample_count > 0
        ]
        mean_support = (
            statistics.mean(support_ratios)
            if support_ratios
            else 0.0
        )
        score = (
            0.35 * min(1.0, video_count / 6.0)
            + 0.20 * min(1.0, unique_channels / 2.0)
            + 0.25 * min(1.0, len(patterns) / 5.0)
            + 0.20 * mean_support
        )
        findings: list[str] = []
        if video_count < 3:
            findings.append("LOW_VIDEO_SAMPLE_COUNT")
        if unique_channels < 2:
            findings.append("LOW_CHANNEL_DIVERSITY")
        if not patterns:
            findings.append("NO_MULTI_VIDEO_PATTERN_PROMOTED")
        if mean_support and mean_support < 0.5:
            findings.append("LOW_MEAN_PATTERN_SUPPORT")
        grade = (
            "HIGH"
            if score >= 0.75
            else "MEDIUM"
            if score >= 0.50
            else "LOW"
        )
        decision_ready = bool(
            patterns
            and video_count >= 2
            and score >= 0.35
        )
        return ResearchConfidenceReport(
            analyzed_video_count=video_count,
            unique_channel_count=unique_channels,
            promoted_pattern_count=len(patterns),
            mean_pattern_support_ratio=round(mean_support, 4),
            score=round(min(1.0, score), 4),
            grade=grade,
            decision_ready=decision_ready,
            findings=findings,
        )


class ResearchPatternTier(StrEnum):
    HYPOTHESIS = "HYPOTHESIS"
    EMERGING = "EMERGING"
    CHANNEL_CONFIRMED = "CHANNEL_CONFIRMED"
    CROSS_CHANNEL_CONFIRMED = "CROSS_CHANNEL_CONFIRMED"


class ResearchPatternScore(BaseModel):
    pattern_id: str
    abstraction: str
    observation_kind: ObservationType
    support_count: int = Field(ge=0)
    sample_count: int = Field(gt=0)
    support_ratio: float = Field(ge=0.0, le=1.0)
    channel_support_count: int = Field(default=0, ge=0)
    channel_sample_count: int = Field(default=0, ge=0)
    channel_support_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    freshness_score: float = Field(default=0.5, ge=0.0, le=1.0)
    strength_score: float = Field(default=0.0, ge=0.0, le=1.0)
    tier: ResearchPatternTier = ResearchPatternTier.HYPOTHESIS
    semantic_axis: str | None = None
    semantic_pole: str | None = None
    sample_video_ids: list[str] = Field(default_factory=list)


class ResearchStyleBranch(BaseModel):
    axis: str
    pattern_ids: list[str] = Field(default_factory=list)
    poles: list[str] = Field(default_factory=list)
    strength_scores: list[float] = Field(default_factory=list)
    interpretation: str
    planning_rule: str


class ResearchPortfolio(BaseModel):
    niche: str
    source_video_count: int = Field(default=0, ge=0)
    source_channel_count: int = Field(default=0, ge=0)
    ranked_patterns: list[ResearchPatternScore] = Field(default_factory=list)
    confirmed_patterns: list[ResearchPatternScore] = Field(default_factory=list)
    emerging_patterns: list[ResearchPatternScore] = Field(default_factory=list)
    hypotheses: list[ResearchPatternScore] = Field(default_factory=list)
    style_branches: list[ResearchStyleBranch] = Field(default_factory=list)
    confidence: ResearchConfidenceReport = Field(
        default_factory=ResearchConfidenceReport
    )
    decision_ready: bool = False
    findings: list[str] = Field(default_factory=list)

    def planning_summary(self) -> dict[str, Any]:
        return {
            "niche": self.niche,
            "decision_ready": self.decision_ready,
            "source_video_count": self.source_video_count,
            "source_channel_count": self.source_channel_count,
            "confidence": self.confidence.model_dump(mode="json"),
            "confirmed_patterns": [
                item.model_dump(mode="json")
                for item in self.confirmed_patterns
            ],
            "emerging_patterns": [
                item.model_dump(mode="json")
                for item in self.emerging_patterns
            ],
            "style_branches": [
                item.model_dump(mode="json")
                for item in self.style_branches
            ],
            "findings": list(self.findings),
            "raw_expression_allowed": False,
        }


class ResearchPortfolioBuilder:
    """Ranks multi-source research without letting freshness outrank evidence."""

    _AXIS_RULES: list[
        tuple[str, str, tuple[str, ...]]
    ] = [
        (
            "opening_visual_density",
            "HIGH",
            (
                "front-loads frequent visual changes",
                "high density of spoken information",
            ),
        ),
        (
            "opening_visual_density",
            "LOW",
            (
                "opening 30 seconds to breathe",
            ),
        ),
        (
            "editing_pace",
            "FAST",
            (
                "fast-cut pacing",
                "short median shot duration",
            ),
        ),
        (
            "editing_pace",
            "SLOW",
            (
                "long-take pacing",
                "high median shot duration",
            ),
        ),
        (
            "editing_pace",
            "MODERATE",
            (
                "moderate shot-duration pacing",
            ),
        ),
        (
            "audio_gap_style",
            "CONTINUOUS",
            (
                "audio bed nearly continuous",
                "few silent gaps",
            ),
        ),
        (
            "audio_gap_style",
            "PUNCTUATED",
            (
                "noticeable silent gaps",
                "silence as pacing punctuation",
            ),
        ),
        (
            "camera_motion",
            "STATIC",
            (
                "locked-off",
                "low-motion camera framing",
            ),
        ),
        (
            "camera_motion",
            "TRANSLATION",
            (
                "translation or pan-like",
            ),
        ),
        (
            "camera_motion",
            "ZOOM",
            (
                "zoom-like",
            ),
        ),
        (
            "camera_motion",
            "HANDHELD",
            (
                "handheld-like",
                "unstable global frame motion",
            ),
        ),
        (
            "camera_motion",
            "MIXED",
            (
                "mixes locked and moving camera behavior",
            ),
        ),
    ]

    @staticmethod
    def _channel_key(
        decomposition: ReferenceDecomposition,
    ) -> str | None:
        source = getattr(decomposition, "source", None)
        if source is None:
            return None
        return (
            getattr(source, "channel_id", None)
            or getattr(source, "channel", None)
            or None
        )

    @staticmethod
    def _parse_upload_date(value: str | None) -> datetime | None:
        if not value:
            return None
        for fmt in ("%Y%m%d", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        return None

    @classmethod
    def _semantic_axis(
        cls,
        abstraction: str,
    ) -> tuple[str | None, str | None]:
        text = abstraction.lower()
        for axis, pole, tokens in cls._AXIS_RULES:
            if any(token in text for token in tokens):
                return axis, pole
        return None, None

    @classmethod
    def _freshness_score(
        cls,
        sample_video_ids: list[str],
        by_video: dict[str, ReferenceDecomposition],
        *,
        now: datetime | None = None,
    ) -> float:
        current = now or datetime.now(timezone.utc)
        values: list[float] = []
        for video_id in sample_video_ids:
            item = by_video.get(video_id)
            if item is None:
                continue
            uploaded = cls._parse_upload_date(
                item.source.upload_date
            )
            if uploaded is None:
                continue
            age_days = max(
                0.0,
                (current - uploaded).total_seconds() / 86400.0,
            )
            # Freshness is intentionally a weak, slow-decaying factor.
            values.append(
                max(
                    0.0,
                    min(
                        1.0,
                        math.exp(-age_days / 1095.0),
                    ),
                )
            )
        if not values:
            return 0.5
        return round(statistics.mean(values), 4)

    @classmethod
    def _score_pattern(
        cls,
        pattern: PatternEvidence,
        decompositions: list[ReferenceDecomposition],
        *,
        now: datetime | None = None,
    ) -> ResearchPatternScore:
        by_video = {
            item.source.video_id: item
            for item in decompositions
        }
        all_channels = {
            key
            for item in decompositions
            if (key := cls._channel_key(item))
        }
        support_channels = {
            key
            for video_id in pattern.sample_video_ids
            if (item := by_video.get(video_id))
            if (key := cls._channel_key(item))
        }
        channel_sample_count = len(all_channels)
        channel_support_count = len(support_channels)
        channel_ratio = (
            channel_support_count / channel_sample_count
            if channel_sample_count
            else 0.0
        )
        support_ratio = pattern.support_ratio
        support_depth = min(
            1.0,
            pattern.support_count / 5.0,
        )
        freshness = cls._freshness_score(
            pattern.sample_video_ids,
            by_video,
            now=now,
        )
        # Freshness contributes only 5%; evidence strength dominates.
        strength = (
            0.40 * support_ratio
            + 0.25 * support_depth
            + 0.20 * channel_ratio
            + 0.10 * pattern.confidence
            + 0.05 * freshness
        )
        if (
            pattern.support_count >= 2
            and channel_support_count >= 2
            and strength >= 0.50
        ):
            tier = ResearchPatternTier.CROSS_CHANNEL_CONFIRMED
        elif (
            pattern.support_count >= 2
            and strength >= 0.42
        ):
            tier = ResearchPatternTier.CHANNEL_CONFIRMED
        elif (
            pattern.support_count >= 2
            or strength >= 0.34
        ):
            tier = ResearchPatternTier.EMERGING
        else:
            tier = ResearchPatternTier.HYPOTHESIS
        axis, pole = cls._semantic_axis(
            pattern.abstraction
        )
        return ResearchPatternScore(
            pattern_id=pattern.pattern_id,
            abstraction=pattern.abstraction,
            observation_kind=pattern.observation_kind,
            support_count=pattern.support_count,
            sample_count=pattern.sample_count,
            support_ratio=round(support_ratio, 4),
            channel_support_count=channel_support_count,
            channel_sample_count=channel_sample_count,
            channel_support_ratio=round(channel_ratio, 4),
            confidence=pattern.confidence,
            freshness_score=freshness,
            strength_score=round(
                max(0.0, min(1.0, strength)),
                4,
            ),
            tier=tier,
            semantic_axis=axis,
            semantic_pole=pole,
            sample_video_ids=list(pattern.sample_video_ids),
        )

    @staticmethod
    def _style_branches(
        ranked: list[ResearchPatternScore],
    ) -> list[ResearchStyleBranch]:
        by_axis: dict[
            str,
            list[ResearchPatternScore],
        ] = {}
        for item in ranked:
            if (
                not item.semantic_axis
                or not item.semantic_pole
                or item.tier
                is ResearchPatternTier.HYPOTHESIS
            ):
                continue
            by_axis.setdefault(
                item.semantic_axis,
                [],
            ).append(item)

        branches: list[ResearchStyleBranch] = []
        for axis, items in sorted(by_axis.items()):
            poles = sorted(
                {
                    item.semantic_pole
                    for item in items
                    if item.semantic_pole
                }
            )
            if len(poles) < 2:
                continue
            strong = [
                item
                for item in items
                if item.strength_score >= 0.34
            ]
            if len(
                {
                    item.semantic_pole
                    for item in strong
                    if item.semantic_pole
                }
            ) < 2:
                continue
            branches.append(
                ResearchStyleBranch(
                    axis=axis,
                    pattern_ids=[
                        item.pattern_id
                        for item in strong
                    ],
                    poles=sorted(
                        {
                            item.semantic_pole
                            for item in strong
                            if item.semantic_pole
                        }
                    ),
                    strength_scores=[
                        item.strength_score
                        for item in strong
                    ],
                    interpretation=(
                        "multiple repeatable style branches exist on "
                        f"{axis}; this is diversity, not a single universal rule"
                    ),
                    planning_rule=(
                        "select the branch that matches the current "
                        "format/scene objective; do not average incompatible "
                        "styles into one default"
                    ),
                )
            )
        return branches

    def build(
        self,
        *,
        niche: str,
        decompositions: list[ReferenceDecomposition],
        patterns: list[PatternEvidence],
        confidence: ResearchConfidenceReport | None = None,
        now: datetime | None = None,
    ) -> ResearchPortfolio:
        evaluated = [
            self._score_pattern(
                pattern,
                decompositions,
                now=now,
            )
            for pattern in patterns
        ]
        ranked = sorted(
            evaluated,
            key=lambda item: (
                item.strength_score,
                item.support_count,
                item.pattern_id,
            ),
            reverse=True,
        )
        confirmed = [
            item
            for item in ranked
            if item.tier
            in {
                ResearchPatternTier.CHANNEL_CONFIRMED,
                ResearchPatternTier.CROSS_CHANNEL_CONFIRMED,
            }
        ]
        emerging = [
            item
            for item in ranked
            if item.tier is ResearchPatternTier.EMERGING
        ]
        hypotheses = [
            item
            for item in ranked
            if item.tier is ResearchPatternTier.HYPOTHESIS
        ]
        confidence_report = (
            confidence
            or ResearchConfidenceEvaluator().evaluate(
                decompositions,
                patterns,
            )
        )
        channels = {
            key
            for item in decompositions
            if (key := self._channel_key(item))
        }
        branches = self._style_branches(ranked)
        findings = list(confidence_report.findings)
        if branches:
            findings.append(
                "MULTIPLE_STYLE_BRANCHES_DETECTED"
            )
        if patterns and not confirmed:
            findings.append(
                "NO_PATTERN_STRONG_ENOUGH_FOR_CONFIRMED_PORTFOLIO"
            )
        decision_ready = bool(
            confidence_report.decision_ready
            and confirmed
        )
        return ResearchPortfolio(
            niche=niche,
            source_video_count=len(decompositions),
            source_channel_count=len(channels),
            ranked_patterns=ranked,
            confirmed_patterns=confirmed,
            emerging_patterns=emerging,
            hypotheses=hypotheses,
            style_branches=branches,
            confidence=confidence_report,
            decision_ready=decision_ready,
            findings=list(dict.fromkeys(findings)),
        )


class ChannelReferenceAnalysis(BaseModel):
    source_url: str
    profiles: list[ReferenceDecomposition] = Field(default_factory=list)
    patterns: list[PatternEvidence] = Field(default_factory=list)
    playbook: NichePlaybook
    confidence: ResearchConfidenceReport = Field(
        default_factory=ResearchConfidenceReport
    )
    findings: list[str] = Field(default_factory=list)

    def planning_profile(self) -> dict[str, Any]:
        buckets: dict[str, list[str]] = {
            "patterns": [],
            "production_patterns": [],
            "retention_patterns": [],
            "format_patterns": [],
        }
        for pattern in self.patterns:
            value = pattern.abstraction
            if pattern.observation_kind is ObservationType.PRODUCTION_METHOD:
                buckets["production_patterns"].append(value)
            elif pattern.observation_kind is ObservationType.HOOK:
                buckets["retention_patterns"].append(value)
            elif pattern.observation_kind in {
                ObservationType.EDITING,
                ObservationType.CAMERA,
                ObservationType.AUDIO,
            }:
                buckets["format_patterns"].append(value)
            else:
                buckets["patterns"].append(value)
        confidence = (
            round(
                sum(item.confidence for item in self.patterns)
                / len(self.patterns),
                4,
            )
            if self.patterns
            else 0.5
        )
        return {
            "profile_id": "CHANNEL_AGGREGATE",
            **{
                key: list(dict.fromkeys(values))
                for key, values in buckets.items()
            },
            "confidence": confidence,
            "research_confidence_score": self.confidence.score,
            "research_confidence_grade": self.confidence.grade,
            "sample_count": len(self.profiles),
            "raw_expression_allowed": False,
        }


class CommandRunner:
    def run(
        self,
        argv: list[str],
        *,
        timeout: int = 120,
        cwd: str | Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            argv,
            text=True,
            capture_output=True,
            timeout=timeout,
            cwd=cwd,
            check=False,
        )


class ReferenceVideoDecomposer:
    def __init__(
        self,
        root: str | Path,
        *,
        policy: ReferenceAcquisitionPolicy | None = None,
        runner: CommandRunner | None = None,
    ) -> None:
        self.root = Path(root)
        self.policy = policy or ReferenceAcquisitionPolicy()
        self.runner = runner or CommandRunner()
        self.data_root = (
            self.root
            / "data"
            / "studio"
            / "reference_intelligence"
        )
        self.quarantine_root = self.data_root / "quarantine"
        self.safe_root = self.data_root / "safe"
        self.quarantine_root.mkdir(parents=True, exist_ok=True)
        self.safe_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _safe_id(value: str) -> str:
        cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_.")
        return cleaned[:120] or "reference"

    @staticmethod
    def _is_http_url(value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)

    def _tool(self, name: str) -> str:
        path = shutil.which(name)
        if not path:
            raise RuntimeError(f"REFERENCE_TOOL_NOT_FOUND:{name}")
        return path

    def _run_json(
        self,
        argv: list[str],
        *,
        timeout: int,
    ) -> dict[str, Any]:
        proc = self.runner.run(argv, timeout=timeout)
        if proc.returncode != 0:
            raise RuntimeError(
                "COMMAND_FAILED:"
                + " ".join(argv[:3])
                + ":"
                + (proc.stderr or proc.stdout or "")[-1200:]
            )
        try:
            return json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"COMMAND_JSON_INVALID:{argv[0]}:{exc}"
            ) from exc

    def metadata(self, url: str) -> tuple[VideoSourceMetadata, dict[str, Any]]:
        if not self._is_http_url(url):
            raise ValueError("REFERENCE_URL_INVALID")
        yt_dlp = self._tool("yt-dlp")
        raw = self._run_json(
            [
                yt_dlp,
                "--dump-single-json",
                "--skip-download",
                "--no-warnings",
                "--no-playlist",
                url,
            ],
            timeout=60,
        )
        duration = raw.get("duration")
        duration_seconds = float(duration) if duration else None
        video_id = str(raw.get("id") or hashlib.sha256(url.encode()).hexdigest()[:16])
        source = VideoSourceMetadata(
            video_id=video_id,
            source_url=url,
            title=raw.get("title"),
            channel=raw.get("channel") or raw.get("uploader"),
            channel_id=raw.get("channel_id") or raw.get("uploader_id"),
            duration_seconds=duration_seconds,
            upload_date=raw.get("upload_date"),
            view_count=raw.get("view_count"),
            like_count=raw.get("like_count"),
            comment_count=raw.get("comment_count"),
            width=raw.get("width"),
            height=raw.get("height"),
            fps=raw.get("fps"),
            categories=[
                str(item)
                for item in (raw.get("categories") or [])
            ],
            tags=[str(item) for item in (raw.get("tags") or [])],
            description_present=bool(raw.get("description")),
            live_status=(
                str(raw.get("live_status"))
                if raw.get("live_status")
                else None
            ),
            was_live=bool(raw.get("was_live")),
        )
        if (
            not self.policy.include_livestreams
            and (
                source.was_live
                or source.live_status
                in {"is_live", "post_live", "was_live"}
            )
        ):
            raise RuntimeError("REFERENCE_LIVESTREAM_EXCLUDED")
        return source, raw

    def _quarantine_dir(self, video_id: str) -> Path:
        path = self.quarantine_root / self._safe_id(video_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _download_subtitles(
        self,
        url: str,
        quarantine: Path,
        video_id: str,
    ) -> Path | None:
        yt_dlp = self._tool("yt-dlp")
        output = str(quarantine / "%(id)s.%(ext)s")
        languages = ",".join(self.policy.subtitle_languages)
        proc = self.runner.run(
            [
                yt_dlp,
                "--skip-download",
                "--write-subs",
                "--write-auto-subs",
                "--sub-format",
                "vtt",
                "--sub-langs",
                languages,
                "--no-warnings",
                "--no-playlist",
                "-o",
                output,
                url,
            ],
            timeout=120,
        )
        candidates = sorted(
            quarantine.glob(f"{self._safe_id(video_id)}*.vtt"),
            key=lambda path: path.stat().st_size,
            reverse=True,
        )
        if candidates:
            return candidates[0]
        if proc.returncode != 0:
            return None
        candidates = sorted(
            quarantine.glob("*.vtt"),
            key=lambda path: path.stat().st_size,
            reverse=True,
        )
        return candidates[0] if candidates else None

    def _download_media(
        self,
        url: str,
        quarantine: Path,
    ) -> Path | None:
        yt_dlp = self._tool("yt-dlp")
        output = str(quarantine / "%(id)s.%(ext)s")
        fmt = (
            f"bestvideo[height<={self.policy.max_height}]"
            f"+bestaudio/best[height<={self.policy.max_height}]/best"
        )
        proc = self.runner.run(
            [
                yt_dlp,
                "--no-playlist",
                "--no-warnings",
                "-f",
                fmt,
                "--merge-output-format",
                "mp4",
                "-o",
                output,
                url,
            ],
            timeout=900,
        )
        media = [
            path
            for path in quarantine.iterdir()
            if path.suffix.lower()
            in {".mp4", ".mkv", ".webm", ".mov", ".m4v"}
            and path.is_file()
        ]
        if not media:
            return None
        media.sort(key=lambda path: path.stat().st_size, reverse=True)
        return media[0] if proc.returncode == 0 or media else None

    @staticmethod
    def _parse_timestamp(value: str) -> float:
        chunks = value.replace(",", ".").split(":")
        if len(chunks) == 3:
            hours, minutes, seconds = chunks
        elif len(chunks) == 2:
            hours = "0"
            minutes, seconds = chunks
        else:
            return 0.0
        return (
            float(hours) * 3600
            + float(minutes) * 60
            + float(seconds)
        )

    def _transcript_stats(
        self,
        subtitle_path: Path | None,
        duration_seconds: float | None,
    ) -> TranscriptStats:
        if subtitle_path is None or not subtitle_path.is_file():
            return TranscriptStats()
        text = subtitle_path.read_text(
            encoding="utf-8",
            errors="ignore",
        )
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        cues: list[tuple[float, float, str]] = []
        lines = text.splitlines()
        index = 0
        timestamp_re = re.compile(
            r"(?P<a>\d{1,2}:\d{2}:\d{2}[.,]\d{3})\s+-->\s+"
            r"(?P<b>\d{1,2}:\d{2}:\d{2}[.,]\d{3})"
        )
        while index < len(lines):
            match = timestamp_re.search(lines[index])
            if not match:
                index += 1
                continue
            start = self._parse_timestamp(match.group("a"))
            end = self._parse_timestamp(match.group("b"))
            index += 1
            payload: list[str] = []
            while index < len(lines) and lines[index].strip():
                payload.append(lines[index].strip())
                index += 1
            cue_text = re.sub(
                r"<[^>]+>",
                " ",
                " ".join(payload),
            )
            cue_text = re.sub(r"\s+", " ", cue_text).strip()
            if cue_text:
                cues.append((start, end, cue_text))
            index += 1

        # Auto-caption VTT often repeats rolling words. De-duplicate exact
        # consecutive cue payloads before deriving aggregate statistics.
        deduped: list[tuple[float, float, str]] = []
        previous = None
        for cue in cues:
            if cue[2] == previous:
                continue
            deduped.append(cue)
            previous = cue[2]
        words = sum(len(re.findall(r"\b\w+\b", cue[2])) for cue in deduped)
        first_30_words = sum(
            len(re.findall(r"\b\w+\b", cue[2]))
            for cue in deduped
            if cue[0] < 30.0
        )
        questions = sum("?" in cue[2] for cue in deduped)
        numeric = sum(
            bool(re.search(r"\b\d+[\d.,%]*\b", cue[2]))
            for cue in deduped
        )
        duration_minutes = (
            duration_seconds / 60.0
            if duration_seconds and duration_seconds > 0
            else None
        )
        wpm = (
            words / duration_minutes
            if duration_minutes
            else None
        )
        return TranscriptStats(
            available=bool(deduped),
            cue_count=len(deduped),
            estimated_word_count=words,
            words_per_minute=round(wpm, 2) if wpm else None,
            first_spoken_seconds=(
                round(deduped[0][0], 3)
                if deduped
                else None
            ),
            first_30s_word_count=first_30_words,
            question_cue_count=questions,
            numeric_cue_count=numeric,
            transcript_sha256=digest,
        )

    def _probe_media(
        self,
        media_path: Path,
    ) -> dict[str, Any]:
        ffprobe = self._tool("ffprobe")
        return self._run_json(
            [
                ffprobe,
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(media_path),
            ],
            timeout=60,
        )

    @staticmethod
    def _duration_from_probe(probe: dict[str, Any]) -> float | None:
        raw = (probe.get("format") or {}).get("duration")
        try:
            return float(raw) if raw else None
        except (TypeError, ValueError):
            return None

    def _scene_times(
        self,
        media_path: Path,
    ) -> list[float]:
        ffmpeg = self._tool("ffmpeg")
        expression = (
            f"select='gt(scene,{self.policy.scene_threshold})',showinfo"
        )
        proc = self.runner.run(
            [
                ffmpeg,
                "-hide_banner",
                "-i",
                str(media_path),
                "-filter:v",
                expression,
                "-an",
                "-f",
                "null",
                "-",
            ],
            timeout=900,
        )
        combined = (proc.stderr or "") + "\n" + (proc.stdout or "")
        times = [
            float(value)
            for value in re.findall(
                r"pts_time:([0-9]+(?:\.[0-9]+)?)",
                combined,
            )
        ]
        return sorted(
            {
                round(value, 3)
                for value in times
                if value > 0
            }
        )

    def _motion_score(
        self,
        media_path: Path,
    ) -> float | None:
        ffmpeg = self._tool("ffmpeg")
        proc = self.runner.run(
            [
                ffmpeg,
                "-hide_banner",
                "-i",
                str(media_path),
                "-vf",
                "vmafmotion",
                "-an",
                "-f",
                "null",
                "-",
            ],
            timeout=900,
        )
        combined = (proc.stderr or "") + "\n" + (proc.stdout or "")
        match = re.search(
            r"VMAF Motion avg:\s*([0-9.]+)",
            combined,
            re.IGNORECASE,
        )
        return round(float(match.group(1)), 4) if match else None

    def _camera_motion_stats(
        self,
        media_path: Path,
    ) -> CameraMotionStats:
        try:
            import cv2
            import numpy as np
        except Exception as exc:
            return CameraMotionStats(
                available=False,
                profile="UNAVAILABLE",
                limitations=[
                    "OpenCV camera-motion proxy unavailable: "
                    f"{type(exc).__name__}"
                ],
            )

        capture = cv2.VideoCapture(str(media_path))
        if not capture.isOpened():
            return CameraMotionStats(
                available=False,
                profile="UNAVAILABLE",
                limitations=["OpenCV could not open the reference video"],
            )
        try:
            fps = float(capture.get(cv2.CAP_PROP_FPS) or 24.0)
            sample_step = max(1, int(round(fps / 2.0)))
            frame_index = 0
            previous_gray = None
            previous_shape = None
            sampled_pairs = 0
            translations: list[float] = []
            rotations: list[float] = []
            zoom_deltas: list[float] = []
            moving_flags: list[bool] = []

            while sampled_pairs < 240:
                ok, frame = capture.read()
                if not ok:
                    break
                if frame_index % sample_step != 0:
                    frame_index += 1
                    continue
                frame_index += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if previous_gray is None:
                    previous_gray = gray
                    previous_shape = gray.shape
                    continue
                if previous_shape != gray.shape:
                    previous_gray = gray
                    previous_shape = gray.shape
                    continue

                points = cv2.goodFeaturesToTrack(
                    previous_gray,
                    maxCorners=220,
                    qualityLevel=0.01,
                    minDistance=8,
                    blockSize=7,
                )
                sampled_pairs += 1
                if points is None or len(points) < 8:
                    previous_gray = gray
                    continue
                next_points, status, _ = cv2.calcOpticalFlowPyrLK(
                    previous_gray,
                    gray,
                    points,
                    None,
                    winSize=(21, 21),
                    maxLevel=3,
                    criteria=(
                        cv2.TERM_CRITERIA_EPS
                        | cv2.TERM_CRITERIA_COUNT,
                        30,
                        0.01,
                    ),
                )
                if next_points is None or status is None:
                    previous_gray = gray
                    continue
                good_prev = points[status.flatten() == 1]
                good_next = next_points[status.flatten() == 1]
                if len(good_prev) < 8:
                    previous_gray = gray
                    continue
                matrix, _ = cv2.estimateAffinePartial2D(
                    good_prev,
                    good_next,
                    method=cv2.RANSAC,
                    ransacReprojThreshold=3.0,
                )
                if matrix is None:
                    previous_gray = gray
                    continue
                a = float(matrix[0, 0])
                b = float(matrix[1, 0])
                tx = float(matrix[0, 2])
                ty = float(matrix[1, 2])
                height, width = gray.shape[:2]
                diagonal = math.hypot(width, height) or 1.0
                translation = math.hypot(tx, ty) / diagonal
                scale = math.sqrt(a * a + b * b)
                rotation = abs(math.degrees(math.atan2(b, a)))
                zoom_delta = abs(scale - 1.0)

                translations.append(translation)
                rotations.append(rotation)
                zoom_deltas.append(zoom_delta)
                moving_flags.append(
                    translation > 0.003
                    or rotation > 0.15
                    or zoom_delta > 0.002
                )
                previous_gray = gray

            valid = len(translations)
            if valid < 3:
                return CameraMotionStats(
                    available=False,
                    sampled_pairs=sampled_pairs,
                    valid_transform_pairs=valid,
                    profile="INSUFFICIENT_FEATURES",
                    confidence=min(0.35, valid / 10.0),
                )

            median_translation = float(
                np.median(np.array(translations, dtype=float))
            )
            median_rotation = float(
                np.median(np.array(rotations, dtype=float))
            )
            median_zoom = float(
                np.median(np.array(zoom_deltas, dtype=float))
            )
            moving_ratio = sum(moving_flags) / len(moving_flags)
            translation_std = float(np.std(np.array(translations)))

            if moving_ratio < 0.20:
                profile = "STATIC_DOMINANT"
            elif (
                median_zoom >= 0.004
                and median_zoom > median_translation * 0.8
            ):
                profile = "ZOOM_LIKE"
            elif (
                median_translation >= 0.006
                and median_rotation <= 0.8
            ):
                profile = "TRANSLATION_DOMINANT"
            elif (
                moving_ratio >= 0.55
                and translation_std
                > max(0.0025, median_translation * 0.8)
            ):
                profile = "UNSTABLE_OR_HANDHELD_LIKE"
            else:
                profile = "MIXED_MOTION"

            confidence = min(
                0.88,
                0.45
                + 0.43
                * min(
                    1.0,
                    valid / max(1, sampled_pairs),
                ),
            )
            return CameraMotionStats(
                available=True,
                sampled_pairs=sampled_pairs,
                valid_transform_pairs=valid,
                median_translation_norm=round(
                    median_translation,
                    6,
                ),
                median_rotation_degrees=round(
                    median_rotation,
                    4,
                ),
                median_zoom_delta=round(
                    median_zoom,
                    6,
                ),
                moving_pair_ratio=round(moving_ratio, 4),
                profile=profile,
                confidence=round(confidence, 4),
            )
        finally:
            capture.release()

    def _audio_stats(
        self,
        media_path: Path,
        duration_seconds: float | None,
        probe: dict[str, Any],
    ) -> AudioRhythmStats:
        has_audio = any(
            stream.get("codec_type") == "audio"
            for stream in probe.get("streams", [])
        )
        if not has_audio:
            return AudioRhythmStats()
        ffmpeg = self._tool("ffmpeg")
        silence_filter = (
            f"silencedetect=n={self.policy.silence_db}dB:"
            f"d={self.policy.silence_min_seconds}"
        )
        silence = self.runner.run(
            [
                ffmpeg,
                "-hide_banner",
                "-i",
                str(media_path),
                "-vn",
                "-af",
                silence_filter,
                "-f",
                "null",
                "-",
            ],
            timeout=900,
        )
        output = (silence.stderr or "") + "\n" + (silence.stdout or "")
        durations = [
            float(value)
            for value in re.findall(
                r"silence_duration:\s*([0-9.]+)",
                output,
            )
        ]
        silence_total = sum(durations)
        ratio = (
            min(1.0, silence_total / duration_seconds)
            if duration_seconds and duration_seconds > 0
            else 0.0
        )

        volume = self.runner.run(
            [
                ffmpeg,
                "-hide_banner",
                "-i",
                str(media_path),
                "-vn",
                "-af",
                "volumedetect",
                "-f",
                "null",
                "-",
            ],
            timeout=900,
        )
        volume_out = (volume.stderr or "") + "\n" + (volume.stdout or "")
        mean_match = re.search(
            r"mean_volume:\s*(-?[0-9.]+)\s*dB",
            volume_out,
        )
        max_match = re.search(
            r"max_volume:\s*(-?[0-9.]+)\s*dB",
            volume_out,
        )
        return AudioRhythmStats(
            has_audio=True,
            silence_count=len(durations),
            silence_ratio=round(ratio, 4),
            mean_silence_seconds=(
                round(statistics.mean(durations), 3)
                if durations
                else None
            ),
            mean_volume_db=(
                float(mean_match.group(1))
                if mean_match
                else None
            ),
            max_volume_db=(
                float(max_match.group(1))
                if max_match
                else None
            ),
        )

    def _visual_stats(
        self,
        media_path: Path,
        duration_seconds: float | None,
    ) -> VisualRhythmStats:
        scene_times = self._scene_times(media_path)
        duration = duration_seconds or 0.0
        boundaries = [0.0, *scene_times]
        if duration > 0:
            boundaries.append(duration)
        shot_durations = [
            max(0.0, boundaries[index + 1] - boundaries[index])
            for index in range(len(boundaries) - 1)
            if boundaries[index + 1] > boundaries[index]
        ]
        cuts = len(scene_times)
        cpm = (
            cuts / (duration / 60.0)
            if duration > 0
            else 0.0
        )
        long_ratio = (
            sum(value >= 8.0 for value in shot_durations)
            / len(shot_durations)
            if shot_durations
            else 0.0
        )
        return VisualRhythmStats(
            scene_count=max(1, cuts + 1) if duration > 0 else cuts + 1,
            cut_count=cuts,
            cuts_per_minute=round(cpm, 3),
            median_shot_seconds=(
                round(statistics.median(shot_durations), 3)
                if shot_durations
                else None
            ),
            mean_shot_seconds=(
                round(statistics.mean(shot_durations), 3)
                if shot_durations
                else None
            ),
            hook_cut_count_30s=sum(
                value <= 30.0 for value in scene_times
            ),
            long_take_ratio=round(long_ratio, 4),
            motion_score_avg=self._motion_score(media_path),
            scene_boundaries_seconds=[
                round(value, 3)
                for value in boundaries
            ],
        )

    @staticmethod
    def _infer_methods_from_text(raw: dict[str, Any]) -> list[str]:
        # Text is used only as an internal classifier. It is never returned.
        text = " ".join(
            [
                str(raw.get("title") or ""),
                str(raw.get("description") or ""),
                " ".join(str(item) for item in raw.get("tags") or []),
                " ".join(str(item) for item in raw.get("categories") or []),
            ]
        ).lower()
        rules = [
            (
                (
                    "gameplay",
                    "walkthrough",
                    "let's play",
                    "lets play",
                    "speedrun",
                ),
                "uses authentic game-runtime capture as a primary visual method",
            ),
            (
                (
                    "minecraft animation",
                    "roblox animation",
                    "3d animation",
                    "animated movie",
                    "animation movie",
                ),
                "uses 3D character animation as a primary visual method",
            ),
            (
                (
                    "screen recording",
                    "screen capture",
                    "software tutorial",
                ),
                "uses screen-recorded demonstrations as a primary visual method",
            ),
            (
                (
                    "ai generated video",
                    "ai video",
                    "text to video",
                    "image to video",
                ),
                "uses generative video elements as a production method",
            ),
            (
                (
                    "motion graphics",
                    "kinetic typography",
                    "animated infographic",
                ),
                "uses motion graphics to carry explanatory information",
            ),
        ]
        out: list[str] = []
        for tokens, abstraction in rules:
            if any(token in text for token in tokens):
                out.append(abstraction)
        return out

    @staticmethod
    def _observations(
        *,
        visual: VisualRhythmStats,
        camera: CameraMotionStats,
        audio: AudioRhythmStats,
        transcript: TranscriptStats,
        production_methods: list[str],
    ) -> list[VideoObservation]:
        observations: list[VideoObservation] = []
        counter = 1

        def add(
            kind: ObservationType,
            description: str,
            confidence: float,
            timestamp: float | None = None,
        ) -> None:
            nonlocal counter
            observations.append(
                VideoObservation(
                    observation_id=f"OBS_{counter:03d}",
                    kind=kind,
                    description=description,
                    timestamp_seconds=timestamp,
                    confidence=confidence,
                    expression_sensitive=False,
                )
            )
            counter += 1

        if visual.hook_cut_count_30s >= 6:
            add(
                ObservationType.HOOK,
                "front-loads frequent visual changes during the opening 30 seconds",
                0.88,
                0.0,
            )
        elif visual.hook_cut_count_30s <= 1 and visual.scene_count > 1:
            add(
                ObservationType.HOOK,
                "allows the opening 30 seconds to breathe with relatively few hard visual cuts",
                0.76,
                0.0,
            )

        if (
            transcript.available
            and transcript.first_spoken_seconds is not None
        ):
            if transcript.first_spoken_seconds <= 3.0:
                add(
                    ObservationType.HOOK,
                    "begins spoken information within the first three seconds",
                    0.86,
                    transcript.first_spoken_seconds,
                )
            if transcript.first_30s_word_count >= 65:
                add(
                    ObservationType.HOOK,
                    "packs a high density of spoken information into the opening 30 seconds",
                    0.82,
                    0.0,
                )

        if visual.median_shot_seconds is not None:
            if visual.median_shot_seconds <= 3.0:
                add(
                    ObservationType.EDITING,
                    "uses fast-cut pacing with a short median shot duration",
                    0.9,
                )
            elif visual.median_shot_seconds >= 8.0:
                add(
                    ObservationType.EDITING,
                    "uses long-take pacing with a high median shot duration",
                    0.88,
                )
            else:
                add(
                    ObservationType.EDITING,
                    "uses moderate shot-duration pacing rather than extreme rapid cutting",
                    0.8,
                )

        if camera.available:
            if camera.profile == "STATIC_DOMINANT":
                add(
                    ObservationType.CAMERA,
                    "uses predominantly locked-off or low-motion camera framing",
                    min(0.76, camera.confidence),
                )
            elif camera.profile == "TRANSLATION_DOMINANT":
                add(
                    ObservationType.CAMERA,
                    "uses sustained translation or pan-like camera motion",
                    min(0.74, camera.confidence),
                )
            elif camera.profile == "ZOOM_LIKE":
                add(
                    ObservationType.CAMERA,
                    "uses repeated zoom-like global framing changes",
                    min(0.70, camera.confidence),
                )
            elif camera.profile == "UNSTABLE_OR_HANDHELD_LIKE":
                add(
                    ObservationType.CAMERA,
                    "uses irregular handheld-like or unstable global frame motion",
                    min(0.66, camera.confidence),
                )
            elif camera.profile == "MIXED_MOTION":
                add(
                    ObservationType.CAMERA,
                    "mixes locked and moving camera behavior across the runtime",
                    min(0.68, camera.confidence),
                )
        elif visual.motion_score_avg is not None:
            if visual.motion_score_avg >= 8.0:
                add(
                    ObservationType.CAMERA,
                    "shows high frame-to-frame visual motion without a reliable camera-motion decomposition",
                    0.58,
                )
            elif visual.motion_score_avg <= 2.0:
                add(
                    ObservationType.CAMERA,
                    "shows restrained frame-to-frame visual motion without a reliable camera-motion decomposition",
                    0.58,
                )

        if audio.has_audio:
            if audio.silence_ratio <= 0.04:
                add(
                    ObservationType.AUDIO,
                    "keeps the audio bed nearly continuous with few silent gaps",
                    0.84,
                )
            elif audio.silence_ratio >= 0.16:
                add(
                    ObservationType.AUDIO,
                    "uses noticeable silent gaps as pacing punctuation",
                    0.8,
                )

        for method in production_methods:
            add(
                ObservationType.PRODUCTION_METHOD,
                method,
                0.74,
            )
        return observations

    def analyze_local_file(
        self,
        media_path: str | Path,
        *,
        source_url: str | None = None,
        source_metadata: dict[str, Any] | None = None,
        subtitle_path: str | Path | None = None,
        video_id: str | None = None,
    ) -> ReferenceDecomposition:
        media = Path(media_path).resolve()
        if not media.is_file():
            raise FileNotFoundError(media)
        probe = self._probe_media(media)
        raw = dict(source_metadata or {})
        duration = (
            self._duration_from_probe(probe)
            or (
                float(raw.get("duration"))
                if raw.get("duration")
                else None
            )
        )
        resolved_id = (
            video_id
            or str(raw.get("id") or "")
            or media.stem
        )
        quarantine = self._quarantine_dir(resolved_id)
        source = VideoSourceMetadata(
            video_id=resolved_id,
            source_url=source_url or str(media),
            title=raw.get("title"),
            channel=raw.get("channel") or raw.get("uploader"),
            channel_id=raw.get("channel_id") or raw.get("uploader_id"),
            duration_seconds=duration,
            upload_date=raw.get("upload_date"),
            view_count=raw.get("view_count"),
            like_count=raw.get("like_count"),
            comment_count=raw.get("comment_count"),
            width=raw.get("width"),
            height=raw.get("height"),
            fps=raw.get("fps"),
            categories=[str(item) for item in raw.get("categories") or []],
            tags=[str(item) for item in raw.get("tags") or []],
            description_present=bool(raw.get("description")),
            live_status=(
                str(raw.get("live_status"))
                if raw.get("live_status")
                else None
            ),
            was_live=bool(raw.get("was_live")),
        )
        if (
            duration
            and duration > self.policy.max_duration_seconds
        ):
            raise RuntimeError(
                "REFERENCE_DURATION_LIMIT:"
                f"{duration}>{self.policy.max_duration_seconds}"
            )
        if (
            not self.policy.include_livestreams
            and (
                source.was_live
                or source.live_status
                in {"is_live", "post_live", "was_live"}
            )
        ):
            raise RuntimeError("REFERENCE_LIVESTREAM_EXCLUDED")
        transcript = self._transcript_stats(
            Path(subtitle_path).resolve()
            if subtitle_path
            else None,
            duration,
        )
        visual = self._visual_stats(media, duration)
        camera = self._camera_motion_stats(media)
        audio = self._audio_stats(media, duration, probe)
        methods = self._infer_methods_from_text(raw)
        observations = self._observations(
            visual=visual,
            camera=camera,
            audio=audio,
            transcript=transcript,
            production_methods=methods,
        )
        profile = CompetitorVideoProfile(
            video_id=resolved_id,
            source_locator=source.source_url,
            title=None,
            duration_seconds=duration,
            observations=observations,
            transcript_quarantined=True,
            raw_expression_allowed_in_creative_context=False,
        )
        report = ReferenceDecomposition(
            source=source,
            profile=profile,
            transcript=transcript,
            visual=visual,
            camera=camera,
            audio=audio,
            inferred_production_methods=methods,
            findings=[],
            quarantine_dir=str(quarantine),
            media_sha256=self._hash_file(media),
        )
        (quarantine / "analysis_report.json").write_text(
            report.model_dump_json(indent=2),
            encoding="utf-8",
        )
        safe_path = self.safe_root / f"{self._safe_id(resolved_id)}.json"
        safe_path.write_text(
            json.dumps(
                report.planning_profile(),
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        return report

    def analyze_url(self, url: str) -> ReferenceDecomposition:
        source, raw = self.metadata(url)
        if (
            source.duration_seconds
            and source.duration_seconds > self.policy.max_duration_seconds
        ):
            raise RuntimeError(
                "REFERENCE_DURATION_LIMIT:"
                f"{source.duration_seconds}>{self.policy.max_duration_seconds}"
            )
        quarantine = self._quarantine_dir(source.video_id)
        (quarantine / "source_metadata.json").write_text(
            json.dumps(raw, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        subtitle = self._download_subtitles(
            url,
            quarantine,
            source.video_id,
        )
        media = self._download_media(url, quarantine)
        if media is None:
            transcript = self._transcript_stats(
                subtitle,
                source.duration_seconds,
            )
            methods = self._infer_methods_from_text(raw)
            visual = VisualRhythmStats()
            audio = AudioRhythmStats()
            camera = CameraMotionStats()
            observations = self._observations(
                visual=visual,
                camera=camera,
                audio=audio,
                transcript=transcript,
                production_methods=methods,
            )
            profile = CompetitorVideoProfile(
                video_id=source.video_id,
                source_locator=url,
                title=None,
                duration_seconds=source.duration_seconds,
                observations=observations,
                transcript_quarantined=True,
                raw_expression_allowed_in_creative_context=False,
            )
            report = ReferenceDecomposition(
                source=source,
                profile=profile,
                transcript=transcript,
                visual=visual,
                camera=camera,
                audio=audio,
                inferred_production_methods=methods,
                findings=[
                    "REFERENCE_MEDIA_UNAVAILABLE:metadata/subtitle-only analysis"
                ],
                quarantine_dir=str(quarantine),
                media_sha256=None,
            )
            (quarantine / "analysis_report.json").write_text(
                report.model_dump_json(indent=2),
                encoding="utf-8",
            )
            safe_path = (
                self.safe_root
                / f"{self._safe_id(source.video_id)}.json"
            )
            safe_path.write_text(
                json.dumps(
                    report.planning_profile(),
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            return report

        report = self.analyze_local_file(
            media,
            source_url=url,
            source_metadata=raw,
            subtitle_path=subtitle,
            video_id=source.video_id,
        )
        if not self.policy.retain_downloaded_media:
            try:
                media.unlink(missing_ok=True)
            except OSError:
                report.findings.append(
                    "QUARANTINE_MEDIA_CLEANUP_FAILED"
                )
        return report

    def discover_channel_urls(
        self,
        url: str,
        *,
        limit: int | None = None,
    ) -> list[str]:
        if not self._is_http_url(url):
            raise ValueError("CHANNEL_URL_INVALID")
        yt_dlp = self._tool("yt-dlp")
        raw = self._run_json(
            [
                yt_dlp,
                "--flat-playlist",
                "--playlist-end",
                str(limit or self.policy.max_channel_videos),
                "--dump-single-json",
                "--skip-download",
                "--no-warnings",
                url,
            ],
            timeout=120,
        )
        urls: list[str] = []
        for entry in raw.get("entries") or []:
            if not isinstance(entry, dict):
                continue
            candidate = (
                entry.get("webpage_url")
                or entry.get("original_url")
            )
            if not candidate:
                video_id = entry.get("id")
                if video_id:
                    candidate = (
                        "https://www.youtube.com/watch?v="
                        + str(video_id)
                    )
            if (
                candidate
                and self._is_http_url(str(candidate))
                and str(candidate) not in urls
            ):
                urls.append(str(candidate))
        return urls[: limit or self.policy.max_channel_videos]

    def analyze_channel(
        self,
        url: str,
        *,
        niche: str = "generic",
        limit: int | None = None,
    ) -> ChannelReferenceAnalysis:
        findings: list[str] = []
        profiles: list[ReferenceDecomposition] = []
        for video_url in self.discover_channel_urls(
            url,
            limit=limit,
        ):
            try:
                profiles.append(self.analyze_url(video_url))
            except Exception as exc:
                findings.append(
                    f"VIDEO_ANALYSIS_FAILED:{video_url}:"
                    f"{type(exc).__name__}:{exc}"
                )
        patterns = PatternMiner().mine(
            [item.profile for item in profiles],
            min_support=2,
            min_ratio=0.4,
        )
        playbook = NichePlaybookCompiler().compile(
            niche,
            patterns,
            gaps=(
                ["fewer than two analyzable channel videos"]
                if len(profiles) < 2
                else []
            ),
        )
        confidence = ResearchConfidenceEvaluator().evaluate(
            profiles,
            patterns,
        )
        return ChannelReferenceAnalysis(
            source_url=url,
            profiles=profiles,
            patterns=patterns,
            playbook=playbook,
            confidence=confidence,
            findings=findings,
        )


class ReferenceIntelligenceEngine:
    @staticmethod
    def health() -> ReferenceIntelligenceHealth:
        yt_dlp = shutil.which("yt-dlp") is not None
        ffmpeg = shutil.which("ffmpeg") is not None
        ffprobe = shutil.which("ffprobe") is not None
        try:
            import cv2  # noqa: F401

            opencv = True
        except Exception:
            opencv = False
        capabilities: list[str] = []
        findings: list[str] = []
        if yt_dlp:
            capabilities.extend(
                [
                    "url metadata",
                    "subtitle acquisition",
                    "bounded media acquisition",
                    "channel sampling",
                ]
            )
        else:
            findings.append("YT_DLP_NOT_FOUND")
        if ffmpeg and ffprobe:
            capabilities.extend(
                [
                    "media probe",
                    "scene-cut analysis",
                    "motion analysis",
                    "silence analysis",
                    "volume analysis",
                ]
            )
        else:
            if not ffmpeg:
                findings.append("FFMPEG_NOT_FOUND")
            if not ffprobe:
                findings.append("FFPROBE_NOT_FOUND")
        if opencv:
            capabilities.append("global optical-flow camera-motion proxy")
        else:
            findings.append("OPENCV_NOT_FOUND_CAMERA_PROXY_DISABLED")
        return ReferenceIntelligenceHealth(
            yt_dlp_available=yt_dlp,
            ffmpeg_available=ffmpeg,
            ffprobe_available=ffprobe,
            opencv_available=opencv,
            url_video_analysis_ready=(
                yt_dlp and ffmpeg and ffprobe
            ),
            local_video_analysis_ready=(ffmpeg and ffprobe),
            capabilities=list(dict.fromkeys(capabilities)),
            findings=findings,
        )

    def __init__(
        self,
        root: str | Path,
        *,
        policy: ReferenceAcquisitionPolicy | None = None,
        runner: CommandRunner | None = None,
    ) -> None:
        self.decomposer = ReferenceVideoDecomposer(
            root,
            policy=policy,
            runner=runner,
        )

    def video(self, locator: str) -> ReferenceDecomposition:
        local = Path(locator).expanduser()
        if local.is_file():
            subtitle_candidates = [
                local.with_suffix(".vtt"),
                local.with_suffix(".en.vtt"),
                local.with_suffix(".vi.vtt"),
            ]
            subtitle = next(
                (
                    candidate
                    for candidate in subtitle_candidates
                    if candidate.is_file()
                ),
                None,
            )
            return self.decomposer.analyze_local_file(
                local,
                source_url=str(local.resolve()),
                source_metadata={
                    "id": local.stem,
                    "title": local.stem,
                },
                subtitle_path=subtitle,
                video_id=local.stem,
            )
        return self.decomposer.analyze_url(locator)

    def channel(
        self,
        url: str,
        *,
        niche: str,
        limit: int | None = None,
    ) -> ChannelReferenceAnalysis:
        return self.decomposer.analyze_channel(
            url,
            niche=niche,
            limit=limit,
        )
