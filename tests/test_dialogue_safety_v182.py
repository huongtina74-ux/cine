from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from cinefactory.block_animation.contracts import ActorPlacement, CameraIntent, ShotPerformanceSpec
from cinefactory.studio.character_factory import CharacterFactory
from cinefactory.studio.dialogue_performance import (
    DialogueLineIntent,
    DialoguePerformanceEngine,
    SpeechTimingToken,
)


def make_line(**changes):
    values = {
        "line_id": "LINE_1",
        "speaker_id": "A",
        "listener_ids": ["B"],
        "text": "We know the truth.",
        "objective": "convince B",
        "action_verb": "convince",
        "start_seconds": 0.5,
        "end_seconds": 2.0,
    }
    values.update(changes)
    return DialogueLineIntent(**values)


def compile_lines(*lines, actors=("A", "B")):
    return DialoguePerformanceEngine().compile(
        shot_id="SCENE_A",
        duration_seconds=3.0,
        actor_ids=list(actors),
        lines=list(lines),
    )


def make_shot(shot_id="SCENE_A"):
    return ShotPerformanceSpec(
        shot_id=shot_id,
        scene_template_id="minecraft_classroom",
        duration_seconds=3.0,
        actors=[
            ActorPlacement(actor_id="A", rig_id="mc_a", marker="hero_a"),
            ActorPlacement(actor_id="B", rig_id="mc_b", marker="hero_b"),
        ],
        camera=CameraIntent(purpose="dialogue", targets=["A", "B"]),
    )


def test_annotated_speech_timing_passes_without_false_lipsync_claim():
    line = make_line(
        speech_alignment_required=True,
        speech_timing=[
            SpeechTimingToken(text="We", start_seconds=0.55, end_seconds=0.8),
            SpeechTimingToken(text="know", start_seconds=0.81, end_seconds=1.1),
            SpeechTimingToken(text="truth", kind="phoneme", start_seconds=1.2, end_seconds=1.5),
        ],
    )
    compilation = compile_lines(line)
    assert compilation.qc.passed
    assert compilation.qc.alignment_checks[0]["passed"]
    assert compilation.qc.audio_lipsync_measured is False
    speaker = [x for x in compilation.directives if x.actor_id == "A"][0]
    assert speaker.spoken_text == line.text
    assert len(speaker.speech_timing) == 3
    assert speaker.speech_alignment_status == "ANNOTATED_NOT_AUDIO_VERIFIED"
    shot = DialoguePerformanceEngine.apply_to_shot(make_shot(), compilation)
    assert shot.performance_directives[0]["speech_timing"][0]["text"] == "We"


@pytest.mark.parametrize("timing", [
    [],
    [SpeechTimingToken(text="late", start_seconds=1.5, end_seconds=2.5)],
    [
        SpeechTimingToken(text="first", start_seconds=0.5, end_seconds=1.2),
        SpeechTimingToken(text="overlap", start_seconds=1.0, end_seconds=1.5),
    ],
])
def test_required_alignment_missing_out_of_bounds_or_overlap_blocks(timing):
    compilation = compile_lines(make_line(
        speech_alignment_required=True,
        speech_timing=timing,
    ))
    assert not compilation.qc.passed
    assert "LINE_1:SPEECH_ALIGNMENT_INVALID_OR_MISSING" in compilation.qc.blockers
    assert compilation.actions == []
    assert compilation.directives == []
    with pytest.raises(ValueError, match="DIALOGUE_QC_BLOCKED"):
        DialoguePerformanceEngine.apply_to_shot(make_shot(), compilation)


def test_duplicate_line_ids_block_and_preserve_only_valid_first_line():
    compilation = compile_lines(make_line(), make_line(start_seconds=2.1, end_seconds=2.8))
    assert not compilation.qc.passed
    assert "LINE_1:DUPLICATE_LINE_ID" in compilation.qc.blockers
    assert len([x for x in compilation.directives if x.role == "SPEAKER"]) == 1


def test_unknown_listener_does_not_generate_unresolved_cues():
    compilation = compile_lines(make_line(listener_ids=["B", "UNREGISTERED"]))
    assert not compilation.qc.passed
    assert "LINE_1:UNKNOWN_LISTENER:UNREGISTERED" in compilation.qc.blockers
    assert not compilation.directives
    assert not compilation.gaze


def test_timing_outside_shot_does_not_generate_executable_cues():
    compilation = compile_lines(make_line(end_seconds=3.5))
    assert not compilation.qc.passed
    assert not compilation.expressions
    assert not compilation.actions


def test_mismatched_shot_id_never_receives_dialogue():
    compilation = compile_lines(make_line())
    assert compilation.qc.passed
    with pytest.raises(ValueError, match="DIALOGUE_SHOT_ID_MISMATCH"):
        DialoguePerformanceEngine.apply_to_shot(make_shot("WRONG_SHOT"), compilation)


def test_missing_actor_reference_never_reports_success(tmp_path: Path):
    factory = CharacterFactory.__new__(CharacterFactory)
    factory.media = SimpleNamespace(probe=lambda *_: SimpleNamespace(duration=1.0))
    factory.store = SimpleNamespace(get_reference=lambda *_: (_ for _ in ()).throw(KeyError("missing")))
    video = tmp_path / "exists.mp4"
    video.write_bytes(b"stub")
    partial = factory.track_video_output(
        actor_reference_ids={"A": "REF_A"},
        global_character_ids={"A": "CHAR_A", "B": "CHAR_B"},
        video_path=video,
    )
    assert partial.measured is False
    assert partial.passed is False
    assert "ACTOR_TRACK_BINDING_MISSING:B" in partial.findings
    missing = factory.track_video_output(
        actor_reference_ids={"A": "REF_A", "B": "REF_B"},
        global_character_ids={"A": "CHAR_A", "B": "CHAR_B"},
        video_path=video,
    )
    assert missing.measured is False
    assert missing.passed is False
    assert len(missing.findings) == 2
    assert "ACTOR_TRACK_REFERENCE_MISSING:B" in missing.findings


def test_actor_box_collision_marks_both_identity_tracks_unqualified(tmp_path: Path):
    from PIL import Image

    factory = CharacterFactory.__new__(CharacterFactory)
    factory.identity_floor = 0.7
    same_box = {
        "x0": 0.2, "y0": 0.1, "x1": 0.6, "y1": 0.9,
        "area": 0.32,
    }

    def extract_frame(_video, path, **_kw):
        Image.new("RGB", (16, 16), (100, 100, 100)).save(path)
        return path

    factory.media = SimpleNamespace(
        probe=lambda *_: SimpleNamespace(duration=1.0),
        extract_frame=extract_frame,
    )
    factory.store = SimpleNamespace(
        get_reference=lambda char_id, ref_id: SimpleNamespace(
            global_character_id=char_id,
            reference_id=ref_id,
            screen_box=same_box,
        )
    )
    from cinefactory.block_animation.rendered_frame_qc import ActorAppearanceEvidence

    factory._track_sample = lambda **_kw: (
        ActorAppearanceEvidence(
            actor_id=_kw["actor_id"],
            screen_box=same_box,
            crop_width=8,
            crop_height=8,
            luma_mean=0.5,
            saturation_mean=0.2,
            rgb_mean=[0.5, 0.5, 0.5],
            hsv_histogram=[0.5],
            ahash64="0" * 16,
        ), 0.97,
    )
    video = tmp_path / "fake.mp4"
    video.write_bytes(b"stub")
    report = factory.track_video_output(
        actor_reference_ids={"A": "REF_A", "B": "REF_B"},
        global_character_ids={"A": "CHAR_A", "B": "CHAR_B"},
        video_path=video,
    )
    assert report.measured is True
    assert report.passed is False
    assert len(report.tracks) == 2
    assert all(not item.passed for item in report.tracks)
    assert any("ACTOR_TRACK_BOX_COLLISION" in finding for finding in report.findings)


def test_three_actor_semantic_performance_is_per_actor():
    lines = [
        make_line(line_id="ONE", speaker_id="A", listener_ids=["B", "C"]),
        make_line(
            line_id="TWO", speaker_id="C", listener_ids=["A", "B"],
            start_seconds=2.1, end_seconds=2.9,
        ),
    ]
    compilation = compile_lines(*lines, actors=("A", "B", "C"))
    assert compilation.qc.passed
    assert len(compilation.directives) == 6
    assert len(compilation.reactions) == 0  # No semantic trigger requested.
    assert {x.actor_id for x in compilation.directives} == {"A", "B", "C"}
    assert {(x.actor_id, x.gaze_target) for x in compilation.directives if x.role == "LISTENER"} == {
        ("B", "A"), ("C", "A"), ("A", "C"), ("B", "C"),
    }
