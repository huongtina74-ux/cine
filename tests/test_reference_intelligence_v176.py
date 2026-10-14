from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_handlers import (
    FilmCompanyHandlers,
    FilmHandlerConfig,
)
from cinefactory.studio.company_runner import StageExecutionContext
from cinefactory.studio.contracts import (
    PlanningInputKind,
    PlanningInputRef,
    StudioProjectSpec,
)
from cinefactory.studio.intelligence import (
    CompetitorVideoProfile,
    ObservationType,
    PatternEvidence,
    PatternMiner,
    VideoObservation,
)
from cinefactory.studio.kernel import build_studio_kernel
from cinefactory.studio.reference_intelligence import (
    CommandRunner,
    ReferenceIntelligenceEngine,
    ReferenceVideoDecomposer,
    ResearchConfidenceEvaluator,
    ResearchPatternTier,
    ResearchPortfolioBuilder,
)


def _synthetic_video(tmp_path: Path) -> Path:
    target = tmp_path / "reference_fixture.mp4"
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=red:s=320x180:r=24:d=2",
        "-f",
        "lavfi",
        "-i",
        "color=c=blue:s=320x180:r=24:d=2",
        "-f",
        "lavfi",
        "-i",
        "color=c=green:s=320x180:r=24:d=2",
        "-f",
        "lavfi",
        "-i",
        "color=c=white:s=320x180:r=24:d=2",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:duration=8",
        "-filter_complex",
        (
            "[0:v][1:v][2:v][3:v]"
            "concat=n=4:v=1:a=0[v]"
        ),
        "-map",
        "[v]",
        "-map",
        "4:a",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-shortest",
        str(target),
    ]
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert target.is_file()
    return target


def _vtt(tmp_path: Path) -> Path:
    path = tmp_path / "captions.vtt"
    path.write_text(
        """WEBVTT

00:00:00.000 --> 00:00:02.000
DO NOT COPY THIS DISTINCTIVE COMPETITOR SENTENCE 123?

00:00:02.100 --> 00:00:05.000
This second caption contains several words for transcript statistics.

00:00:05.100 --> 00:00:07.500
A final caption keeps spoken information continuous.
""",
        encoding="utf-8",
    )
    return path


def test_local_reference_decomposition_quarantines_expression(tmp_path: Path):
    media = _synthetic_video(tmp_path)
    subtitle = _vtt(tmp_path)
    decomposer = ReferenceVideoDecomposer(tmp_path)
    report = decomposer.analyze_local_file(
        media,
        source_url="https://youtube.example/watch?v=private-expression",
        source_metadata={
            "id": "VID_TEST_1",
            "title": "Roblox Animation Movie - Exact Competitor Title",
            "description": "A Roblox animation story.",
            "tags": ["roblox animation"],
            "duration": 8,
        },
        subtitle_path=subtitle,
    )

    assert report.transcript.available is True
    assert report.transcript.cue_count == 3
    assert report.visual.scene_count >= 4
    assert report.visual.cut_count >= 3
    assert report.audio.has_audio is True
    assert report.media_sha256

    safe = report.planning_profile()
    serialized = json.dumps(safe, ensure_ascii=False)
    assert "DO NOT COPY THIS DISTINCTIVE" not in serialized
    assert "Exact Competitor Title" not in serialized
    assert "youtube.example" not in serialized
    assert safe["raw_expression_allowed"] is False
    assert any(
        "3D character animation" in item
        for item in safe["production_patterns"]
    )


def test_observations_are_abstract_and_pattern_mineable(tmp_path: Path):
    media = _synthetic_video(tmp_path)
    subtitle = _vtt(tmp_path)
    decomposer = ReferenceVideoDecomposer(tmp_path)
    reports = [
        decomposer.analyze_local_file(
            media,
            source_metadata={
                "id": f"VID_{index}",
                "title": "Roblox Animation",
                "description": "Roblox animation",
                "duration": 8,
            },
            subtitle_path=subtitle,
            video_id=f"VID_{index}",
        )
        for index in (1, 2)
    ]
    patterns = PatternMiner().mine(
        [item.profile for item in reports],
        min_support=2,
        min_ratio=0.4,
    )
    assert patterns
    assert all(pattern.support_count == 2 for pattern in patterns)
    assert any(
        pattern.observation_kind
        is ObservationType.PRODUCTION_METHOD
        for pattern in patterns
    )
    assert all(
        "DO NOT COPY" not in pattern.abstraction
        for pattern in patterns
    )


class _ChannelRunner(CommandRunner):
    def run(self, argv, *, timeout=120, cwd=None):
        if "--flat-playlist" in argv:
            payload = {
                "entries": [
                    {"id": "abc123"},
                    {
                        "id": "def456",
                        "webpage_url": "https://www.youtube.com/watch?v=def456",
                    },
                ]
            }
            return subprocess.CompletedProcess(
                argv,
                0,
                stdout=json.dumps(payload),
                stderr="",
            )
        raise AssertionError(f"unexpected command: {argv}")


def test_channel_discovery_is_bounded_and_normalized(
    tmp_path: Path,
    monkeypatch,
):
    monkeypatch.setattr(
        "shutil.which",
        lambda name: name,
    )
    decomposer = ReferenceVideoDecomposer(
        tmp_path,
        runner=_ChannelRunner(),
    )
    urls = decomposer.discover_channel_urls(
        "https://www.youtube.com/@example/videos",
        limit=2,
    )
    assert urls == [
        "https://www.youtube.com/watch?v=abc123",
        "https://www.youtube.com/watch?v=def456",
    ]


def test_planning_profile_exposes_features_not_scene_boundary_sequence(
    tmp_path: Path,
):
    media = _synthetic_video(tmp_path)
    report = ReferenceVideoDecomposer(tmp_path).analyze_local_file(
        media,
        source_metadata={
            "id": "VID_SAFE",
            "title": "Gameplay walkthrough",
            "description": "A gameplay walkthrough.",
            "duration": 8,
        },
    )
    safe = report.planning_profile()
    assert "analysis_features" in safe
    assert "scene_boundaries_seconds" not in json.dumps(
        safe,
        ensure_ascii=False,
    )
    assert any(
        "game-runtime capture" in item
        for item in safe["production_patterns"]
    )


class _FakeReferenceEngine:
    def video(self, url: str):
        profile = CompetitorVideoProfile(
            video_id="SAFE_VIDEO_1",
            source_locator=url,
            title=None,
            duration_seconds=120,
            observations=[
                VideoObservation(
                    observation_id="OBS_001",
                    kind=ObservationType.PRODUCTION_METHOD,
                    description=(
                        "uses 3D character animation as a primary visual method"
                    ),
                    confidence=0.9,
                ),
                VideoObservation(
                    observation_id="OBS_002",
                    kind=ObservationType.HOOK,
                    description=(
                        "front-loads frequent visual changes during the opening 30 seconds"
                    ),
                    confidence=0.85,
                ),
            ],
        )
        return SimpleNamespace(
            planning_profile=lambda: {
                "profile_id": "SAFE_VIDEO_1",
                "patterns": [],
                "production_patterns": [
                    "uses 3D character animation as a primary visual method"
                ],
                "retention_patterns": [
                    "front-loads frequent visual changes during the opening 30 seconds"
                ],
                "format_patterns": [],
                "confidence": 0.875,
                "raw_expression_allowed": False,
            },
            source=SimpleNamespace(
                video_id="SAFE_VIDEO_1",
                duration_seconds=120,
                title="RAW COMPETITOR TITLE MUST STAY QUARANTINED",
                source_url=url,
            ),
            profile=profile,
        )


def test_company_intelligence_url_to_planning_keeps_raw_expression_quarantined(
    tmp_path: Path,
):
    studio = build_studio_kernel(tmp_path)
    runtime = SimpleNamespace(root=tmp_path, studio=studio)
    raw_url = "https://youtube.example/watch?v=raw-secret"
    raw_marker = "RAW TRANSCRIPT MUST NEVER ENTER BLACKBOARD"
    project = StudioProjectSpec(
        prompt="Create an original Roblox animated story",
        domain="gaming.roblox",
        niche="roblox animation",
        planning_inputs=[
            PlanningInputRef(
                input_id="PIN_AUTO",
                kind=PlanningInputKind.COMPETITOR_VIDEO,
                uri=raw_url,
                title="RAW COMPETITOR TITLE MUST STAY QUARANTINED",
                metadata={
                    "raw_transcript": raw_marker,
                },
            )
        ],
    )
    blueprint = CompanyOrchestrator(studio).build_blueprint(project)
    handlers = FilmCompanyHandlers(
        runtime,
        config=FilmHandlerConfig(
            auto_reference_analysis=True,
        ),
        reference_intelligence=_FakeReferenceEngine(),
    ).registry()

    for stage_id in (
        "INTELLIGENCE",
        "CREATIVE_STRATEGY",
        "PLANNING",
    ):
        stage = next(
            item
            for item in blueprint.stages
            if item.stage_id == stage_id
        )
        result = handlers.get(stage_id)(
            StageExecutionContext(
                blueprint=blueprint,
                stage=stage,
                kernel=runtime,
                project_root=tmp_path / "project",
            )
        )
        assert result.ok is True

    research = studio.blackboard.get(
        project.studio_project_id,
        "research_pack",
    )["payload"]
    competitor = studio.blackboard.get(
        project.studio_project_id,
        "competitor_profiles",
    )["payload"]
    strategy = studio.blackboard.get(
        project.studio_project_id,
        "production_strategy",
    )["payload"]

    serialized = json.dumps(
        {
            "research": research,
            "competitor": competitor,
            "strategy": strategy,
        },
        ensure_ascii=False,
    )
    assert raw_url not in serialized
    assert raw_marker not in serialized
    assert "RAW COMPETITOR TITLE" not in serialized
    assert (
        "uses 3D character animation as a primary visual method"
        in serialized
    )
    assert (
        "front-loads frequent visual changes during the opening 30 seconds"
        in serialized
    )


def test_reference_engine_accepts_local_video_file(tmp_path: Path):
    media = _synthetic_video(tmp_path)
    subtitle = media.with_suffix(".vtt")
    subtitle.write_text(
        """WEBVTT

00:00:00.000 --> 00:00:03.000
Local subtitle content must stay quarantined.
""",
        encoding="utf-8",
    )
    report = ReferenceIntelligenceEngine(tmp_path).video(str(media))
    safe = json.dumps(report.planning_profile(), ensure_ascii=False)
    assert report.transcript.available is True
    assert "Local subtitle content" not in safe


class _LiveMetadataRunner(CommandRunner):
    def run(self, argv, *, timeout=120, cwd=None):
        payload = {
            "id": "live123",
            "title": "Live stream",
            "duration": 120,
            "live_status": "is_live",
            "was_live": False,
        }
        return subprocess.CompletedProcess(
            argv,
            0,
            stdout=json.dumps(payload),
            stderr="",
        )


def test_live_reference_is_excluded_by_default(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: name)
    decomposer = ReferenceVideoDecomposer(
        tmp_path,
        runner=_LiveMetadataRunner(),
    )
    try:
        decomposer.metadata("https://www.youtube.com/watch?v=live123")
    except RuntimeError as exc:
        assert str(exc) == "REFERENCE_LIVESTREAM_EXCLUDED"
    else:
        raise AssertionError("livestream should be excluded")


def _synthetic_pan_video(tmp_path: Path) -> Path:
    target = tmp_path / "pan_fixture.mp4"
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "testsrc2=size=640x180:rate=24:duration=5",
        "-vf",
        "crop=320:180:x='min(iw-ow,t*50)':y=0",
        "-c:v",
        "libx264",
        "-preset",
        "ultrafast",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(target),
    ]
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    return target


def test_camera_motion_proxy_runs_on_pan_like_fixture(tmp_path: Path):
    media = _synthetic_pan_video(tmp_path)
    report = ReferenceVideoDecomposer(tmp_path).analyze_local_file(
        media,
        source_metadata={
            "id": "PAN_TEST",
            "duration": 5,
        },
    )
    assert report.camera.sampled_pairs > 0
    assert report.camera.valid_transform_pairs >= 3
    assert report.camera.available is True
    assert report.camera.profile in {
        "STATIC_DOMINANT",
        "TRANSLATION_DOMINANT",
        "ZOOM_LIKE",
        "UNSTABLE_OR_HANDHELD_LIKE",
        "MIXED_MOTION",
    }
    assert report.camera.confidence > 0


def test_safe_persisted_report_excludes_source_expression(tmp_path: Path):
    media = _synthetic_video(tmp_path)
    report = ReferenceVideoDecomposer(tmp_path).analyze_local_file(
        media,
        source_url="https://example.invalid/raw-source-url",
        source_metadata={
            "id": "SAFE_DISK",
            "title": "RAW EXACT TITLE SHOULD NOT BE IN SAFE FILE",
            "description": "gameplay walkthrough",
            "duration": 8,
        },
    )
    safe_path = (
        tmp_path
        / "data"
        / "studio"
        / "reference_intelligence"
        / "safe"
        / "SAFE_DISK.json"
    )
    quarantine_path = (
        Path(report.quarantine_dir)
        / "analysis_report.json"
    )
    safe_text = safe_path.read_text(encoding="utf-8")
    quarantine_text = quarantine_path.read_text(encoding="utf-8")
    assert "RAW EXACT TITLE" not in safe_text
    assert "raw-source-url" not in safe_text
    assert "RAW EXACT TITLE" in quarantine_text


def test_research_confidence_single_video_is_low_and_not_decision_ready():
    decomposition = SimpleNamespace(
        source=SimpleNamespace(
            video_id="V1",
            channel_id="C1",
            channel="Channel One",
        )
    )
    report = ResearchConfidenceEvaluator().evaluate(
        [decomposition],
        [],
    )
    assert report.grade == "LOW"
    assert report.decision_ready is False
    assert "LOW_VIDEO_SAMPLE_COUNT" in report.findings
    assert "NO_MULTI_VIDEO_PATTERN_PROMOTED" in report.findings


def test_research_confidence_multi_video_supported_pattern_is_decision_ready():
    decompositions = [
        SimpleNamespace(
            source=SimpleNamespace(
                video_id=f"V{index}",
                channel_id=("C1" if index <= 2 else "C2"),
                channel=("One" if index <= 2 else "Two"),
            )
        )
        for index in range(1, 5)
    ]
    patterns = [
        PatternEvidence(
            pattern_id="PAT_001",
            abstraction=(
                "uses generative video for surreal dream montage transitions"
            ),
            observation_kind=ObservationType.PRODUCTION_METHOD,
            sample_video_ids=["V1", "V2", "V3"],
            support_count=3,
            sample_count=4,
            confidence=0.82,
        ),
        PatternEvidence(
            pattern_id="PAT_002",
            abstraction=(
                "front-loads frequent visual changes during the opening 30 seconds"
            ),
            observation_kind=ObservationType.HOOK,
            sample_video_ids=["V1", "V2", "V4"],
            support_count=3,
            sample_count=4,
            confidence=0.78,
        ),
    ]
    report = ResearchConfidenceEvaluator().evaluate(
        decompositions,
        patterns,
    )
    assert report.decision_ready is True
    assert report.score >= 0.5
    assert report.grade in {"MEDIUM", "HIGH"}
    assert report.unique_channel_count == 2
    assert report.promoted_pattern_count == 2


def _portfolio_decomposition(
    *,
    video_id: str,
    channel_id: str,
    upload_date: str,
):
    return SimpleNamespace(
        source=SimpleNamespace(
            video_id=video_id,
            channel_id=channel_id,
            channel=channel_id,
            upload_date=upload_date,
        )
    )


def test_research_portfolio_rewards_cross_channel_support_over_freshness():
    decompositions = [
        _portfolio_decomposition(
            video_id="V1",
            channel_id="C1",
            upload_date="20260925",
        ),
        _portfolio_decomposition(
            video_id="V2",
            channel_id="C1",
            upload_date="20260924",
        ),
        _portfolio_decomposition(
            video_id="V3",
            channel_id="C2",
            upload_date="20240101",
        ),
        _portfolio_decomposition(
            video_id="V4",
            channel_id="C2",
            upload_date="20240102",
        ),
    ]
    cross_channel = PatternEvidence(
        pattern_id="PAT_CROSS",
        abstraction="uses fast-cut pacing with a short median shot duration",
        observation_kind=ObservationType.EDITING,
        sample_video_ids=["V1", "V3", "V4"],
        support_count=3,
        sample_count=4,
        confidence=0.72,
    )
    fresh_single_channel = PatternEvidence(
        pattern_id="PAT_FRESH",
        abstraction="uses repeated zoom-like global framing changes",
        observation_kind=ObservationType.CAMERA,
        sample_video_ids=["V1", "V2"],
        support_count=2,
        sample_count=4,
        confidence=0.86,
    )
    portfolio = ResearchPortfolioBuilder().build(
        niche="test",
        decompositions=decompositions,
        patterns=[cross_channel, fresh_single_channel],
        confidence=ResearchConfidenceEvaluator().evaluate(
            decompositions,
            [cross_channel, fresh_single_channel],
        ),
        now=__import__("datetime").datetime(
            2026,
            10,
            1,
            tzinfo=__import__("datetime").timezone.utc,
        ),
    )
    ranked = {
        item.pattern_id: item
        for item in portfolio.ranked_patterns
    }
    assert (
        ranked["PAT_CROSS"].strength_score
        > ranked["PAT_FRESH"].strength_score
    )
    assert (
        ranked["PAT_CROSS"].tier
        is ResearchPatternTier.CROSS_CHANNEL_CONFIRMED
    )
    assert ranked["PAT_CROSS"].channel_support_count == 2


def test_research_portfolio_detects_repeatable_style_branches():
    decompositions = [
        _portfolio_decomposition(
            video_id="V1",
            channel_id="C1",
            upload_date="20260901",
        ),
        _portfolio_decomposition(
            video_id="V2",
            channel_id="C1",
            upload_date="20260902",
        ),
        _portfolio_decomposition(
            video_id="V3",
            channel_id="C2",
            upload_date="20260903",
        ),
        _portfolio_decomposition(
            video_id="V4",
            channel_id="C2",
            upload_date="20260904",
        ),
    ]
    fast = PatternEvidence(
        pattern_id="PAT_FAST",
        abstraction="uses fast-cut pacing with a short median shot duration",
        observation_kind=ObservationType.EDITING,
        sample_video_ids=["V1", "V3"],
        support_count=2,
        sample_count=4,
        confidence=0.78,
    )
    slow = PatternEvidence(
        pattern_id="PAT_SLOW",
        abstraction="uses long-take pacing with a high median shot duration",
        observation_kind=ObservationType.EDITING,
        sample_video_ids=["V2", "V4"],
        support_count=2,
        sample_count=4,
        confidence=0.76,
    )
    portfolio = ResearchPortfolioBuilder().build(
        niche="test",
        decompositions=decompositions,
        patterns=[fast, slow],
    )
    assert portfolio.style_branches
    branch = next(
        item
        for item in portfolio.style_branches
        if item.axis == "editing_pace"
    )
    assert set(branch.poles) == {"FAST", "SLOW"}
    assert "do not average incompatible styles" in branch.planning_rule
