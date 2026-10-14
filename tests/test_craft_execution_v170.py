from __future__ import annotations

from cinefactory.autopilot.scaffold import LocalScaffoldPlanner
from cinefactory.domain.models import ShotSpecBatch
from cinefactory.studio.company import stage_blueprint
from cinefactory.studio.contracts import MediaFormat
from cinefactory.studio.craft_execution import (
    AudioIntentCompiler,
    CameraDiagnostics,
    ColorIntentCompiler,
    CraftExecutionCompiler,
    CraftSeverity,
)
from cinefactory.studio.creative_pipeline import (
    CinematographyBibleCompiler,
    DirectorTreatmentCompiler,
    StoryArchitectureCompiler,
    StoryboardAnimaticCompiler,
)
from cinefactory.studio.project_dna import ProjectDNA


def _creative_fixture(project_id: str = "P1"):
    planner = LocalScaffoldPlanner()
    story = planner.story(
        "A Minecraft hero must rescue a friend before the gate closes."
    )
    architecture = StoryArchitectureCompiler().compile(project_id, story)
    script = planner.script(story)
    director = planner.director(script)
    dna = ProjectDNA(project_id=project_id)
    treatment = DirectorTreatmentCompiler().compile(
        project_id,
        script,
        director,
        dna,
    )
    shots = ShotSpecBatch(shots=planner.shots(script, director))
    cinematography = CinematographyBibleCompiler().compile(
        project_id,
        shots,
        dna,
    )
    _, animatic = StoryboardAnimaticCompiler().compile(
        project_id,
        shots,
    )
    return (
        planner,
        architecture,
        script,
        director,
        treatment,
        shots,
        cinematography,
        animatic,
    )


def test_scene_beat_shot_intent_cascade_maps_scaffold_story_changes():
    (
        _,
        architecture,
        script,
        director,
        treatment,
        shots,
        cinematography,
        animatic,
    ) = _creative_fixture()
    bundle = CraftExecutionCompiler().compile(
        project_id="P1",
        story=architecture,
        script=script,
        director=director,
        treatment=treatment,
        shots=shots,
        cinematography=cinematography,
        animatic=animatic,
    )
    assert bundle.passed is True
    assert len(bundle.creative_intent_graph.shots) == len(shots.shots)
    assert bundle.creative_intent_graph.shots[0].beat_id == "B01"
    assert bundle.creative_intent_graph.shots[0].scene_purpose
    assert bundle.creative_intent_graph.shots[0].camera_purpose
    assert bundle.creative_intent_graph.shots[0].performance_objectives


def test_camera_diagnostics_blocks_180_axis_cross_inside_same_scene():
    (
        _,
        _,
        _,
        _,
        _,
        shots,
        _,
        _,
    ) = _creative_fixture()
    first = shots.shots[0].model_copy(deep=True)
    second = shots.shots[0].model_copy(
        deep=True,
        update={
            "shot_id": "S01_SH02",
            "previous_shot_id": first.shot_id,
            "next_shot_id": None,
        },
    )
    first.next_shot_id = second.shot_id
    second.camera.camera_side = "north"
    second.entry_state.camera_side = "north"
    batch = ShotSpecBatch(shots=[first, second])

    report = CameraDiagnostics().validate("P2", batch)
    assert report.passed is False
    blockers = [
        item.code
        for item in report.findings
        if item.severity is CraftSeverity.BLOCKER
    ]
    assert "POSSIBLE_180_AXIS_CROSS" in blockers


def test_camera_world_side_mismatch_is_blocker():
    (
        _,
        _,
        _,
        _,
        _,
        shots,
        _,
        _,
    ) = _creative_fixture()
    shot = shots.shots[0].model_copy(deep=True)
    shot.camera.camera_side = "north"
    shot.entry_state.camera_side = "south"
    report = CameraDiagnostics().validate(
        "P3",
        ShotSpecBatch(shots=[shot]),
    )
    assert report.passed is False
    assert any(
        item.code == "CAMERA_SIDE_CONTRACT_MISMATCH"
        and item.severity is CraftSeverity.BLOCKER
        for item in report.findings
    )


def test_missing_eyeline_is_review_warning_not_false_hard_block():
    (
        _,
        _,
        _,
        _,
        _,
        shots,
        _,
        _,
    ) = _creative_fixture()
    shot = shots.shots[0].model_copy(deep=True)
    shot.entry_state.characters["C01"].eyeline = None
    report = CameraDiagnostics().validate(
        "P4",
        ShotSpecBatch(shots=[shot]),
    )
    assert report.passed is True
    assert any(
        item.code == "EYELINE_UNSPECIFIED"
        and item.severity is CraftSeverity.WARNING
        for item in report.findings
    )


def test_craft_bundle_produces_performance_lighting_and_sound_contracts():
    (
        _,
        architecture,
        script,
        director,
        treatment,
        shots,
        cinematography,
        animatic,
    ) = _creative_fixture("P5")
    bundle = CraftExecutionCompiler().compile(
        project_id="P5",
        story=architecture,
        script=script,
        director=director,
        treatment=treatment,
        shots=shots,
        cinematography=cinematography,
        animatic=animatic,
    )
    assert bundle.performance_direction.beats
    assert bundle.lighting_color_intent.shots
    assert bundle.sound_spotting.spots
    beat = bundle.performance_direction.beats[0]
    assert beat.objective
    assert beat.action_verb
    assert beat.gaze_target
    assert beat.body_mechanics
    assert beat.timing_notes


def test_minecraft_stage_graph_carries_craft_intent_into_downstream_departments():
    stages = stage_blueprint(
        MediaFormat.NARRATIVE_FILM,
        False,
        professional_governance=True,
        professional_niche="minecraft",
    )
    by_id = {stage.stage_id: stage for stage in stages}
    assert "CRAFT_EXECUTION_DESIGN" in by_id
    assert "camera_diagnostics" in by_id["CREATIVE_REVIEW"].artifacts_in
    assert "performance_direction" in by_id["TECHNICAL_DIRECTION"].artifacts_in
    assert "creative_intent_graph" in by_id["PRODUCTION"].artifacts_in
    assert "sound_spotting" in by_id["AUDIO"].artifacts_in
    assert "lighting_color_intent" in by_id["FINISHING"].artifacts_in
    assert "color_plan" in by_id["FINISHING"].artifacts_out


def test_nonvisual_niches_do_not_receive_camera_craft_stage():
    for niche in (
        "audio_storytelling_seniors",
        "long_slices_game",
        "asmr_sleep_hands_objects",
        "fishing_silent",
        "rain_sleep_white_noise",
    ):
        stages = stage_blueprint(
            MediaFormat.NARRATIVE_FILM,
            False,
            professional_governance=True,
            professional_niche=niche,
        )
        assert "CRAFT_EXECUTION_DESIGN" not in {
            stage.stage_id for stage in stages
        }


def test_sound_spotting_compiles_into_timed_audio_cues():
    (
        _,
        architecture,
        script,
        director,
        treatment,
        shots,
        cinematography,
        animatic,
    ) = _creative_fixture("P6")
    bundle = CraftExecutionCompiler().compile(
        project_id="P6",
        story=architecture,
        script=script,
        director=director,
        treatment=treatment,
        shots=shots,
        cinematography=cinematography,
        animatic=animatic,
    )
    audio = AudioIntentCompiler().compile(
        "P6",
        bundle.sound_spotting,
        shots,
    )
    assert audio.cues
    ambience = [cue for cue in audio.cues if cue.role.value == "AMBIENCE"]
    assert len(ambience) == len(shots.shots)
    assert ambience[0].start_seconds == 0
    if len(ambience) > 1:
        assert ambience[1].start_seconds == shots.shots[0].duration_seconds


def test_lighting_color_intent_compiles_to_transparent_plan_only_color_plan():
    (
        _,
        architecture,
        script,
        director,
        treatment,
        shots,
        cinematography,
        animatic,
    ) = _creative_fixture("P7")
    bundle = CraftExecutionCompiler().compile(
        project_id="P7",
        story=architecture,
        script=script,
        director=director,
        treatment=treatment,
        shots=shots,
        cinematography=cinematography,
        animatic=animatic,
    )
    color = ColorIntentCompiler().compile(
        "P7",
        bundle.lighting_color_intent,
    )
    assert len(color.shots) == len(shots.shots)
    assert all(shot.approved is False for shot in color.shots)
    assert all(
        any("PLAN_ONLY" in note for note in shot.notes)
        for shot in color.shots
    )
