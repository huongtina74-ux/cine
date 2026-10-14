"""Style-aware contracts and deterministic visual-fidelity gates.

The semantic episode model remains style agnostic. This module keeps the
production asset decision at the registry/adapter boundary so the assembler
does not need to know Blender geometry details.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from cinefactory.block_animation.contracts import EpisodeSpec, QCFinding, Severity


class CharacterStyle(StrEnum):
    DEBUG_BLOCK = "DEBUG_BLOCK"
    MINECRAFT = "MINECRAFT"
    ROBLOX_R6 = "ROBLOX_R6"
    ROBLOX_R15 = "ROBLOX_R15"


class SceneStyle(StrEnum):
    DEBUG_BLOCK = "DEBUG_BLOCK"
    MINECRAFT = "MINECRAFT"
    ROBLOX = "ROBLOX"


@dataclass(frozen=True)
class CharacterStyleAdapter:
    style: CharacterStyle
    skeleton_profile: str
    material_profile: str
    expression_profile: str
    required_parts: tuple[str, ...] = ()

    def accepts_scene(self, scene_style: str) -> bool:
        if self.style is CharacterStyle.MINECRAFT:
            return scene_style == SceneStyle.MINECRAFT
        if self.style in {CharacterStyle.ROBLOX_R6, CharacterStyle.ROBLOX_R15}:
            return scene_style == SceneStyle.ROBLOX
        return scene_style == SceneStyle.DEBUG_BLOCK


STYLE_ADAPTERS: dict[CharacterStyle, CharacterStyleAdapter] = {
    CharacterStyle.DEBUG_BLOCK: CharacterStyleAdapter(
        CharacterStyle.DEBUG_BLOCK,
        "BLOCK_HUMANOID_V1",
        "debug_material_profile",
        "generic",
    ),
    CharacterStyle.MINECRAFT: CharacterStyleAdapter(
        CharacterStyle.MINECRAFT,
        "MINECRAFT_VOXEL_V1",
        "minecraft_material_profile",
        "minecraft_pixel",
        ("head", "torso", "arm.R", "arm.L", "leg.R", "leg.L"),
    ),
    CharacterStyle.ROBLOX_R6: CharacterStyleAdapter(
        CharacterStyle.ROBLOX_R6,
        "ROBLOX_R6_V1",
        "roblox_material_profile",
        "roblox_face",
        ("Head", "Torso", "LeftArm", "RightArm", "LeftLeg", "RightLeg", "HumanoidRoot"),
    ),
    CharacterStyle.ROBLOX_R15: CharacterStyleAdapter(
        CharacterStyle.ROBLOX_R15,
        "ROBLOX_R15_V1",
        "roblox_material_profile",
        "roblox_face",
        (
            "Root",
            "Head",
            "UpperTorso",
            "LowerTorso",
            "UpperArm",
            "LowerArm",
            "Hand",
            "UpperLeg",
            "LowerLeg",
            "Foot",
        ),
    ),
}


def adapter_for(style: str) -> CharacterStyleAdapter:
    try:
        return STYLE_ADAPTERS[CharacterStyle(style)]
    except (KeyError, ValueError) as exc:
        raise ValueError(f"unknown character style: {style}") from exc


def validate_episode_style(episode: EpisodeSpec, libraries) -> list[QCFinding]:
    """Validate deterministic style contracts when an episode opts in.

    This is intentionally a style/asset gate, not a claim of semantic beauty.
    Human visual review remains mandatory for every benchmark render.
    """

    findings: list[QCFinding] = []
    for shot in episode.shots:
        try:
            scene = libraries.scenes.get(shot.scene_template_id)
        except KeyError:
            continue
        principal_ids = {actor.actor_id for actor in shot.actors}
        for actor in shot.actors:
            try:
                rig = libraries.rigs.get(actor.rig_id)
                adapter = adapter_for(rig.style)
            except (KeyError, ValueError) as exc:
                findings.append(QCFinding(code="STYLE_RIG_INVALID", severity=Severity.ERROR, message=str(exc), shot_id=shot.shot_id))
                continue
            if rig.style == CharacterStyle.DEBUG_BLOCK:
                findings.append(QCFinding(code="DEBUG_RIG_IN_PRODUCTION", severity=Severity.ERROR, message=f"principal {actor.actor_id} resolves to DEBUG_BLOCK", shot_id=shot.shot_id))
            if not adapter.accepts_scene(scene.style):
                findings.append(QCFinding(code="STYLE_SCENE_MISMATCH", severity=Severity.ERROR, message=f"{rig.style} actor {actor.actor_id} cannot render in {scene.style} scene", shot_id=shot.shot_id))
            missing = [part for part in adapter.required_parts if part not in rig.skeleton_parts and part != "HumanoidRoot"]
            if missing:
                findings.append(QCFinding(code="STYLE_SKELETON_PARTS_MISSING", severity=Severity.ERROR, message=f"{rig.rig_id} missing required parts {missing}", shot_id=shot.shot_id))
            if rig.style == CharacterStyle.MINECRAFT and not rig.skin_path:
                findings.append(QCFinding(code="MINECRAFT_SKIN_MISSING", severity=Severity.ERROR, message=f"{rig.rig_id} has no deterministic skin asset", shot_id=shot.shot_id))
            if rig.style in {CharacterStyle.ROBLOX_R6, CharacterStyle.ROBLOX_R15}:
                identity = rig.identity or {}
                for key in ("face", "clothing"):
                    if not identity.get(key):
                        findings.append(QCFinding(code="ROBLOX_IDENTITY_MISSING", severity=Severity.ERROR, message=f"{rig.rig_id} has no deterministic {key} identity", shot_id=shot.shot_id))

        for cue in shot.props:
            if cue.actor_id not in principal_ids:
                continue
            try:
                prop = libraries.props.get(cue.prop_id)
            except KeyError as exc:
                findings.append(QCFinding(code="STYLE_PROP_MISSING", severity=Severity.ERROR, message=str(exc), shot_id=shot.shot_id))
                continue
            if scene.style == SceneStyle.MINECRAFT and prop.style != CharacterStyle.MINECRAFT:
                findings.append(QCFinding(code="MINECRAFT_PROP_STYLE_MISMATCH", severity=Severity.ERROR, message=f"prop {prop.prop_id} is {prop.style}, expected MINECRAFT", shot_id=shot.shot_id))
            if scene.style == SceneStyle.ROBLOX and prop.style != "ROBLOX":
                findings.append(QCFinding(code="ROBLOX_PROP_STYLE_MISMATCH", severity=Severity.ERROR, message=f"prop {prop.prop_id} is {prop.style}, expected ROBLOX", shot_id=shot.shot_id))

    return findings


def style_asset_manifest(libraries) -> dict:
    return {
        "character_styles": {
            key.value: {
                "skeleton_profile": value.skeleton_profile,
                "material_profile": value.material_profile,
                "expression_profile": value.expression_profile,
                "required_parts": list(value.required_parts),
            }
            for key, value in STYLE_ADAPTERS.items()
        },
        "registered_rigs": [item.model_dump(mode="json") for item in libraries.rigs.values()],
        "registered_scenes": [item.model_dump(mode="json") for item in libraries.scenes.values()],
        "registered_props": [item.model_dump(mode="json") for item in libraries.props.values()],
        "human_style_review_required": True,
        "production_api_spend": 0,
    }
