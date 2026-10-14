from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.studio.block_adapter import (
    BlockProductionStyle,
    CompanyToBlockAdapter,
)
from cinefactory.studio.company import CompanyOrchestrator
from cinefactory.studio.company_handlers import FilmCompanyHandlers, FilmHandlerConfig
from cinefactory.studio.company_runner import AutonomousCompanyRunner
from cinefactory.studio.contracts import CapabilityKind, MediaFormat, StudioProjectSpec
from cinefactory.studio.format_director import UniversalMediaClassifier


ROOT = Path(__file__).resolve().parents[1]


def test_game_world_animation_is_not_misclassified_as_gameplay():
    classifier = UniversalMediaClassifier()
    minecraft = classifier.classify(
        "Create a Minecraft animated cinematic story with expressive characters"
    )
    roblox = classifier.classify(
        "Create a Roblox R6 animated cinematic story about school"
    )
    gameplay = classifier.classify("Minecraft gameplay survival 100 days")

    assert minecraft.format is MediaFormat.ANIMATION
    assert minecraft.actual_gameplay_required is False
    assert minecraft.constraints["domain"] == "gaming.minecraft"
    assert roblox.format is MediaFormat.ANIMATION
    assert roblox.constraints["domain"] == "gaming.roblox"
    assert gameplay.format is MediaFormat.GAMEPLAY
    assert gameplay.actual_gameplay_required is True


@pytest.mark.parametrize(
    ("style", "prompt"),
    [
        (BlockProductionStyle.MINECRAFT, "Original Minecraft animated story"),
        (BlockProductionStyle.ROBLOX_R6, "Original Roblox R6 animated story"),
    ],
)
def test_company_shots_adapt_to_valid_block_episode(style, prompt):
    runtime = build_context(ROOT)
    blueprint = CompanyOrchestrator(runtime.studio).build_blueprint(
        StudioProjectSpec(prompt=prompt, duration_seconds=20),
        professional_governance=False,  # explicit legacy diagnostic recipe
    )
    assert blueprint.packs.domain_pack is not None
    assert blueprint.packs.domain_pack.pack_id == "domain.gaming"
    assert blueprint.packs.execution_pack is not None
    assert "CHARACTER_IDENTITY" in blueprint.quality_profile.gates
    scaffold = FilmCompanyHandlers(runtime).scaffold
    story = scaffold.story(prompt)
    script = scaffold.script(story)
    director = scaffold.director(script)
    shots = scaffold.shots(script, director)

    episode = CompanyToBlockAdapter().adapt_episode(
        project_id=blueprint.project.studio_project_id,
        episode_id="EP_TEST",
        title="Original Episode",
        shots=shots,
        style=style,
        width=320,
        height=180,
        quality_profile="preview",
    )
    compiled = EpisodeAssembler.from_root(ROOT).compile(episode)
    assert compiled.qc.passed
    assert len(compiled.shots) == len(shots)
    assert all(shot.visual_style != "DEBUG_BLOCK" for shot in compiled.shots)


@pytest.mark.skipif(
    shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None,
    reason="ffmpeg required",
)
def test_animation_runner_locks_local_dialogue_before_production(tmp_path: Path):
    for folder in ("config", "models", "workflows"):
        shutil.copytree(ROOT / folder, tmp_path / folder)
    blender = tmp_path / ".tools" / "blender-test" / "blender.exe"
    blender.parent.mkdir(parents=True)
    blender.write_bytes(b"capability-probe-only")

    tts_script = tmp_path / "mock_tts.py"
    tts_script.write_text(
        "import sys,wave\n"
        "out=sys.argv[1]; _=sys.stdin.read()\n"
        "w=wave.open(out,'wb'); w.setnchannels(1); w.setsampwidth(2); "
        "w.setframerate(16000); w.writeframes(b'\\x00\\x00'*3200); w.close()\n",
        encoding="utf-8",
    )

    runtime = build_context(tmp_path)
    project = StudioProjectSpec(
        prompt="Create a Minecraft animated cinematic story with expressive characters",
        duration_seconds=12,
        language="en",
    )
    blueprint = CompanyOrchestrator(runtime.studio).build_blueprint(project, professional_governance=False)
    assert blueprint.studio_plan.product.format is MediaFormat.ANIMATION
    assert blueprint.blockers == []
    assert {
        task.capability_kind for task in blueprint.production_recipe.tasks
    } >= {CapabilityKind.OFFLINE_3D, CapabilityKind.EDITORIAL}

    config = FilmHandlerConfig(
        production_mode="slate",
        offline_3d_backend="video_factory",
        asset_candidates=1,
        keyframe_candidates=1,
        pilot_count=1,
        render_width=320,
        render_height=180,
        master_width=320,
        master_height=180,
        tts_mode="command",
        tts_command=f'python "{tts_script}" {{output}}',
        require_lipsync=False,
    )
    handlers = FilmCompanyHandlers(runtime, config=config).registry()
    runner = AutonomousCompanyRunner(
        blueprint,
        handlers,
        store=runtime.studio.execution_ledgers,
        kernel=runtime,
        project_root=tmp_path / "data" / "projects" / project.studio_project_id,
    )
    report = runner.run_until_blocked_or_complete(max_cycles=40)
    assert report.complete is True, report.errors
    assert report.ledger.get("VOICE_PREP").state.value == "SUCCEEDED"

    dialogue = runtime.studio.blackboard.get(
        project.studio_project_id,
        "dialogue_lock",
    )["payload"]
    assert dialogue["state"] == "LOCKED"
    assert dialogue["lines"]
    assert all(Path(item["audio_ref"]).is_file() for item in dialogue["lines"])

    voice_conference = runtime.studio.blackboard.get(
        project.studio_project_id,
        "audio_production_conference",
    )["payload"]
    assert voice_conference["decisions"]
    assert all(
        item["primary_engine_id"] == "tts.command"
        for item in voice_conference["decisions"]
    )

    post_conference = runtime.studio.blackboard.get(
        project.studio_project_id,
        "audio_post_conference",
    )["payload"]
    mix = next(
        item for item in post_conference["decisions"]
        if item["job_id"] == "AUDIO_MIX_MASTER"
    )
    assert mix["primary_engine_id"] == "ffmpeg.audio"
