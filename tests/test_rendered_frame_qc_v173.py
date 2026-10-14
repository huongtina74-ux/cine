from __future__ import annotations

import shutil

import pytest

from cinefactory.block_animation.rendered_frame_qc import (
    ActorAppearanceEvidence,
    FrameAppearanceMetrics,
    RenderedAppearanceEvaluator,
    RenderedFrameAnalyzer,
)
from cinefactory.domain.enums import FailureCode
from cinefactory.media.ffmpeg import FFmpegToolchain
from cinefactory.production.contracts import DailiesReport
from cinefactory.production.failure_router import FailureRouter


def _actor(
    actor_id: str,
    *,
    hue_shift: int = 0,
    ahash: str = "ffffffff00000000",
) -> ActorAppearanceEvidence:
    hist = [0.0] * 48
    hist[(0 + hue_shift) % 48] = 0.70
    hist[(1 + hue_shift) % 48] = 0.30
    return ActorAppearanceEvidence(
        actor_id=actor_id,
        screen_box={
            "x0": 0.2,
            "y0": 0.2,
            "x1": 0.5,
            "y1": 0.8,
            "area": 0.18,
        },
        crop_width=32,
        crop_height=64,
        luma_mean=0.35,
        saturation_mean=0.45,
        rgb_mean=[0.4, 0.3, 0.2],
        hsv_histogram=hist,
        ahash64=ahash,
    )


def _frame(
    label: str,
    *,
    luma: float,
    sat: float,
    rgb: list[float],
) -> FrameAppearanceMetrics:
    return FrameAppearanceMetrics(
        label=label,
        time_seconds=1.0,
        width=320,
        height=180,
        luma_mean=luma,
        luma_std=0.12,
        shadow_clip_ratio=0.05,
        highlight_clip_ratio=0.01,
        saturation_mean=sat,
        rgb_mean=rgb,
        ahash64="f0f0f0f00f0f0f0f",
    )


def test_same_actor_appearance_scores_one():
    evaluator = RenderedAppearanceEvaluator()
    actor = _actor("C01")
    result = evaluator.compare_actor(actor, actor)
    assert result.measured is True
    assert result.passed is True
    assert result.score == pytest.approx(1.0)
    assert result.findings == []


def test_large_actor_appearance_shift_blocks_identity_proxy():
    evaluator = RenderedAppearanceEvaluator()
    reference = _actor("C01", hue_shift=0)
    current = _actor(
        "C01",
        hue_shift=20,
        ahash="00000000ffffffff",
    ).model_copy(
        update={"rgb_mean": [0.05, 0.75, 0.65]}
    )
    result = evaluator.compare_actor(reference, current)
    assert result.measured is True
    assert result.passed is False
    assert result.score is not None
    assert any(
        finding.startswith("RENDERED_IDENTITY_DRIFT:C01")
        for finding in result.findings
    )


def test_same_scene_cut_appearance_detects_large_exposure_color_drift():
    evaluator = RenderedAppearanceEvaluator()
    previous = _frame(
        "tail",
        luma=0.20,
        sat=0.20,
        rgb=[0.20, 0.20, 0.20],
    )
    current = _frame(
        "head",
        luma=0.60,
        sat=0.50,
        rgb=[0.70, 0.25, 0.10],
    )
    result = evaluator.compare_cut(
        previous,
        current,
        same_scene=True,
        same_lighting_intent=True,
    )
    assert result.measured is True
    assert result.passed is False
    assert any(
        finding.startswith("CUT_APPEARANCE_DRIFT")
        for finding in result.findings
    )


def test_scene_transition_does_not_false_fail_cut_appearance():
    evaluator = RenderedAppearanceEvaluator()
    previous = _frame(
        "tail",
        luma=0.10,
        sat=0.10,
        rgb=[0.10, 0.10, 0.10],
    )
    current = _frame(
        "head",
        luma=0.90,
        sat=0.90,
        rgb=[0.90, 0.10, 0.10],
    )
    result = evaluator.compare_cut(
        previous,
        current,
        same_scene=False,
        same_lighting_intent=True,
    )
    assert result.measured is False
    assert result.passed is True
    assert result.score is None


def test_failure_router_routes_rendered_identity_to_asset_engine():
    directive = FailureRouter().classify(
        "S01",
        ["RENDERED_IDENTITY_DRIFT:C01:score=0.40"],
    )
    assert directive.failure_code is FailureCode.IDENTITY_DRIFT
    assert directive.owner == "ASSET_ENGINE"
    assert directive.retryable is True


def test_failure_router_routes_exposure_to_lighting_color_engine():
    directive = FailureRouter().classify(
        "S01",
        ["RENDERED_FRAME_UNDEREXPOSED:HEAD"],
    )
    assert directive.failure_code is FailureCode.LOOKDEV_FAIL
    assert directive.owner == "LIGHTING_COLOR_ENGINE"
    assert directive.action == "REBALANCE_LIGHTING_AND_COLOR"


def test_dailies_report_can_carry_repair_directives():
    directive = FailureRouter().classify(
        "S01",
        ["CUT_APPEARANCE_DRIFT:luma=0.4"],
    )
    report = DailiesReport(
        passed=False,
        findings=["BLOCK_RENDER_FAILED:S01"],
        repair_directives=[directive],
    )
    assert report.repair_directives[0].owner == "LIGHTING_COLOR_ENGINE"


def test_local_frame_analyzer_extracts_actor_crop_and_signal_metrics(tmp_path):
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("ffmpeg required")

    media = FFmpegToolchain()
    video = media.make_slate(
        "FRAME-QC",
        tmp_path / "sample.mp4",
        duration=0.8,
        size="320x180",
        fps=24,
    )
    result = RenderedFrameAnalyzer(media).analyze(
        video,
        render_state={
            "actors": {
                "C01": {
                    "mid": {
                        "screen_box": {
                            "x0": 0.20,
                            "y0": 0.15,
                            "x1": 0.80,
                            "y1": 0.85,
                            "area": 0.42,
                        }
                    }
                }
            }
        },
    )
    assert result.head.width == 320
    assert result.mid.height == 180
    assert "C01" in result.actors
    assert result.actors["C01"].crop_width > 10
    assert result.sidecar_path


def test_daytime_exposure_gate_blocks_extremely_dark_frame():
    frame = FrameAppearanceMetrics(
        label="mid",
        time_seconds=1.0,
        width=320,
        height=180,
        luma_mean=0.04,
        luma_std=0.05,
        shadow_clip_ratio=0.52,
        highlight_clip_ratio=0.0,
        saturation_mean=0.05,
        rgb_mean=[0.04, 0.04, 0.05],
        ahash64="0000000000000000",
    )
    blockers, _ = RenderedFrameAnalyzer._quality_findings(
        [frame],
        lighting={"time_of_day": "DAY"},
    )
    assert "RENDERED_FRAME_UNDEREXPOSED:MID" in blockers


def test_night_intent_allows_same_dark_frame_without_false_block():
    frame = FrameAppearanceMetrics(
        label="mid",
        time_seconds=1.0,
        width=320,
        height=180,
        luma_mean=0.04,
        luma_std=0.05,
        shadow_clip_ratio=0.52,
        highlight_clip_ratio=0.0,
        saturation_mean=0.05,
        rgb_mean=[0.04, 0.04, 0.05],
        ahash64="0000000000000000",
    )
    blockers, _ = RenderedFrameAnalyzer._quality_findings(
        [frame],
        lighting={"time_of_day": "NIGHT"},
    )
    assert blockers == []


def test_daylight_profile_blocks_deep_shadow_underexposure():
    frame = _frame(
        "mid",
        luma=0.036,
        sat=0.08,
        rgb=[0.03, 0.04, 0.05],
    ).model_copy(
        update={"shadow_clip_ratio": 0.51}
    )
    blockers, warnings = RenderedFrameAnalyzer._quality_findings(
        [frame],
        lighting={"time_of_day": "DAY"},
    )
    assert "RENDERED_FRAME_UNDEREXPOSED:MID" in blockers
    assert warnings == []


def test_night_profile_allows_intentional_low_key_frame_with_warning():
    frame = _frame(
        "mid",
        luma=0.04,
        sat=0.08,
        rgb=[0.02, 0.03, 0.06],
    ).model_copy(
        update={"shadow_clip_ratio": 0.72}
    )
    blockers, warnings = RenderedFrameAnalyzer._quality_findings(
        [frame],
        lighting={"time_of_day": "NIGHT"},
    )
    assert blockers == []
    assert any(
        item.startswith("RENDERED_FRAME_SHADOW_CLIP_HIGH:MID")
        for item in warnings
    )
