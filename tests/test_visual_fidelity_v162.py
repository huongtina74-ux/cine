from pathlib import Path

import pytest

from cinefactory.block_animation.assembler import EpisodeAssembler, EpisodeAssemblyError
from cinefactory.block_animation.camera import CameraCoverageEngine
from cinefactory.block_animation.contracts import ActorPlacement, CameraIntent, EpisodeSpec, ShotPerformanceSpec, TransformSpec, Vec3
from cinefactory.block_animation.registry import BlockAnimationLibraries
from cinefactory.block_animation.styles import CharacterStyle, STYLE_ADAPTERS


ROOT = Path(__file__).resolve().parents[1]


def style_episode(style: str, rig_id: str, scene_id: str, prop_id: str | None = None) -> EpisodeSpec:
    actors = [
        ActorPlacement(actor_id="A", rig_id=rig_id, transform=TransformSpec(location=Vec3(x=-1.2, y=0.0))),
        ActorPlacement(actor_id="B", rig_id=rig_id, transform=TransformSpec(location=Vec3(x=1.2, y=0.0))),
    ]
    props = []
    if prop_id:
        from cinefactory.block_animation.contracts import PropBindingCue

        props = [PropBindingCue(prop_id=prop_id, actor_id="A", start_seconds=.5, end_seconds=1.5)]
    return EpisodeSpec(
        project_id="v162-tests",
        episode_id=f"{style.lower()}-style-contract",
        title="style contract",
        fps=24,
        width=640,
        height=360,
        quality_profile="rtx3060_quality",
        metadata={"visual_style_gate": True, "visual_style": style, "human_review_required": True},
        shots=[
            ShotPerformanceSpec(
                shot_id="S01",
                scene_template_id=scene_id,
                duration_seconds=2.0,
                actors=actors,
                camera=CameraIntent(purpose="default", targets=["A", "B"], prop_id=prop_id),
                props=props,
            )
        ],
    )


def test_style_adapters_cover_debug_minecraft_and_roblox_foundations():
    assert set(STYLE_ADAPTERS) == {
        CharacterStyle.DEBUG_BLOCK,
        CharacterStyle.MINECRAFT,
        CharacterStyle.ROBLOX_R6,
        CharacterStyle.ROBLOX_R15,
    }
    assert "arm.R" in STYLE_ADAPTERS[CharacterStyle.MINECRAFT].required_parts
    assert "LeftArm" in STYLE_ADAPTERS[CharacterStyle.ROBLOX_R6].required_parts
    assert "LowerTorso" in STYLE_ADAPTERS[CharacterStyle.ROBLOX_R15].required_parts


@pytest.mark.parametrize(
    ("style", "rig_id", "scene_id", "prop_id"),
    [
        ("MINECRAFT", "mc_a", "minecraft_classroom", "minecraft_book"),
        ("ROBLOX_R6", "r6_a", "roblox_classroom", "roblox_book"),
        ("ROBLOX_R15", "r15_validation", "roblox_classroom", "roblox_book"),
    ],
)
def test_production_style_gate_compiles_without_debug_principals(style, rig_id, scene_id, prop_id):
    compiled = EpisodeAssembler.from_root(ROOT).compile(style_episode(style, rig_id, scene_id, prop_id))
    assert compiled.qc.passed
    expected_scene_style = "MINECRAFT" if style == "MINECRAFT" else "ROBLOX"
    assert compiled.shots[0].visual_style == expected_scene_style
    assert compiled.shots[0].rigs["A"].style == style


def test_debug_principal_is_rejected_when_visual_style_gate_is_enabled():
    with pytest.raises(EpisodeAssemblyError) as exc:
        EpisodeAssembler.from_root(ROOT).compile(style_episode("MINECRAFT", "block_humanoid_a", "minecraft_classroom"))
    assert any(f.code == "DEBUG_RIG_IN_PRODUCTION" for f in exc.value.report.findings)


def test_camera_roll_requires_explicit_dutch_intent():
    libraries = BlockAnimationLibraries.load(ROOT)
    engine = CameraCoverageEngine(libraries.cameras)
    scene = libraries.scenes.get("minecraft_classroom")
    with pytest.raises(ValueError, match="explicit dutch_tension"):
        engine.compile(CameraIntent(purpose="group_reaction", camera_roll=6), shot_id="S", duration_seconds=1, scene=scene)
    take = engine.compile(CameraIntent(purpose="dutch_tension", camera_roll=6), shot_id="S", duration_seconds=1, scene=scene)[0]
    assert take.camera_roll == 6


def test_style_configs_are_deterministic_and_zero_api():
    libraries = BlockAnimationLibraries.load(ROOT)
    assert libraries.rigs.get("mc_a").skin_path.startswith("procedural://")
    assert libraries.rigs.get("r6_a").identity["clothing"] == "orange_jacket_navy_pants"
    assert libraries.rigs.get("r15_validation").skeleton_profile == "ROBLOX_R15_V1"
    assert libraries.props.get("minecraft_book").style == "MINECRAFT"
    assert libraries.props.get("minecraft_book").attach_offset.location.x < 0
    assert libraries.props.get("roblox_book").style == "ROBLOX"
    assert libraries.props.get("roblox_book").attach_offset.location.x < 0
    assert libraries.scenes.get("minecraft_classroom").style == "MINECRAFT"
    assert libraries.scenes.get("roblox_classroom").style == "ROBLOX"


def test_presentation_uses_centered_anchor_and_prop_target():
    libraries = BlockAnimationLibraries.load(ROOT)
    engine = CameraCoverageEngine(libraries.cameras)
    scene = libraries.scenes.get("minecraft_classroom")
    take = engine.compile(
        CameraIntent(purpose="fidelity_presentation", pattern_id="fidelity_presentation", targets=["A", "B"], prop_id="minecraft_book"),
        shot_id="S",
        duration_seconds=1,
        scene=scene,
    )[0]
    assert take.anchor == "medium"
    assert take.prop_id == "minecraft_book"
