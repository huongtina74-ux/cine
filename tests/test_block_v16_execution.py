from pathlib import Path

import pytest

from cinefactory.block_animation.assembler import EpisodeAssembler, EpisodeAssemblyError
from cinefactory.block_animation.contracts import BlenderAnimationJob, CameraIntent, EpisodeSpec
from cinefactory.block_animation.execution import BlockExecutionPlanner
from cinefactory.block_animation.registry import BlockAnimationLibraries

ROOT = Path(__file__).resolve().parents[1]


def test_render_quality_profiles_are_loaded_and_fingerprinted():
    libs = BlockAnimationLibraries.load(ROOT)
    assert {"rtx3060_quality", "rtx3060_fast", "preview"}.issubset(set(libs.render_quality.keys()))
    q = libs.render_quality.get("rtx3060_quality")
    assert q.taa_samples >= 64
    assert q.use_dof is True
    assert q.bitrate_mbps >= 28
    assert len(libs.fingerprint()) == 16


def test_execution_plan_contains_real_v16_runtime_stages(tmp_path):
    episode = EpisodeSpec.model_validate_json((ROOT / "examples/block_animation/original_episode.json").read_text())
    compiled = EpisodeAssembler.from_root(ROOT).compile(episode, output_dir=tmp_path)

    first = compiled.shots[0]
    job = BlenderAnimationJob(project_id=compiled.project_id, episode_id=compiled.episode_id, shot=first, output_path=str(tmp_path / "shot.mp4"))
    plan = BlockExecutionPlanner.plan(job)
    assert plan["scene_mode"] == "procedural"
    assert plan["render_quality"]["profile_id"] == "rtx3060_quality"
    assert plan["props"] and plan["props"][0]["prop_id"] == "phone"
    assert any(x.get("renderer_event") == "sparkle_burst" for x in plan["events"])
    assert plan["camera"]["motion"] in {"static", "push_in", "pull_out", "track", "orbit", "snap"}
    assert plan["camera"]["dof_fstop"] > 0

    second = compiled.shots[1]
    job2 = job.model_copy(update={"shot": second, "output_path": str(tmp_path / "shot2.mp4")})
    plan2 = BlockExecutionPlanner.plan(job2)
    # Crowd cues are normalized into ordinary action/expression streams for the renderer.
    assert any(x.get("source") == "crowd" for x in plan2["actions"])
    assert any(x.get("source") == "crowd" for x in plan2["expressions"])


def test_scene_library_has_multiple_zero_api_sets():
    libs = BlockAnimationLibraries.load(ROOT)
    assert libs.scenes.get("block_classroom").procedural_kind == "classroom"
    assert libs.scenes.get("block_street").procedural_kind == "street"
    assert libs.scenes.get("block_arena").procedural_kind == "arena"


def test_prop_camera_target_survives_execution_planning(tmp_path):
    episode = EpisodeSpec.model_validate_json((ROOT / "examples/block_animation/original_episode.json").read_text())
    first = episode.shots[0].model_copy(update={
        "camera": CameraIntent(purpose="important_prop", prop_id="phone", pattern_id="prop_insert", targets=["builder"]),
    })
    compiled = EpisodeAssembler.from_root(ROOT).compile(episode.model_copy(update={"shots": [first]}), output_dir=tmp_path)
    plan = BlockExecutionPlanner.plan(BlenderAnimationJob(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot=compiled.shots[0],
        output_path=str(tmp_path / "prop.mp4"),
    ))
    assert plan["camera"]["target_mode"] == "prop"
    assert plan["camera"]["prop_id"] == "phone"


def test_unknown_quality_profile_is_hard_failure():
    episode = EpisodeSpec.model_validate_json((ROOT / "examples/block_animation/original_episode.json").read_text())
    episode = episode.model_copy(update={"quality_profile": "does_not_exist"})
    with pytest.raises(EpisodeAssemblyError) as exc:
        EpisodeAssembler.from_root(ROOT).compile(episode)
    assert "RenderQualityProfileDefinition" in str(exc.value)
