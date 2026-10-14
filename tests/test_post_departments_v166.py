from __future__ import annotations

import pytest
from pydantic import ValidationError

from cinefactory.studio.audio_department import AudioCue, AudioPlan, AudioQC, AudioRole
from cinefactory.studio.color_department import ColorBible, ColorPlan, ColorQC, ShotColorState
from cinefactory.studio.editorial import EditDecision, EditDecisionGraph, EditReason, EditorialCompiler


def test_edit_decision_graph_requires_unique_order():
    with pytest.raises(ValidationError):
        EditDecisionGraph(
            project_id="P1",
            decisions=[
                EditDecision(decision_id="A", source_id="S1", source_out=1, timeline_order=0, reason=EditReason.INFORMATION),
                EditDecision(decision_id="B", source_id="S2", source_out=1, timeline_order=0, reason=EditReason.REACTION),
            ],
        )


def test_editorial_compiler_preserves_semantic_reason():
    graph = EditDecisionGraph(
        project_id="P1",
        decisions=[
            EditDecision(
                decision_id="A",
                source_id="S1",
                segment_id="SEG_001",
                source_in=1,
                source_out=3,
                timeline_order=0,
                reason=EditReason.REMOVE_DEAD_TIME,
            )
        ],
    )
    timeline = EditorialCompiler().to_timeline(graph, {"S1": "clip.mp4"})
    assert timeline.clips[0].source_in == 1
    assert "edit_reason=REMOVE_DEAD_TIME" in timeline.clips[0].notes


def test_audio_qc_flags_music_without_ducking():
    plan = AudioPlan(
        project_id="P1",
        cues=[
            AudioCue(
                cue_id="M1",
                role=AudioRole.MUSIC,
                start_seconds=0,
                purpose="support tension",
                duck_under_dialogue=False,
            )
        ],
    )
    assert "M1:MUSIC_DUCKING_UNSPECIFIED" in AudioQC().validate(plan)


def test_color_qc_flags_extreme_adjustment():
    plan = ColorPlan(
        project_id="P1",
        bible=ColorBible(),
        shots=[
            ShotColorState(
                shot_id="S1",
                source_space="sRGB",
                exposure_offset=5,
            )
        ],
    )
    assert "S1:EXTREME_EXPOSURE_OFFSET" in ColorQC().validate(plan)
