from __future__ import annotations

from dataclasses import dataclass

from cinefactory.domain.enums import CreativeStage, StageOwner
from cinefactory.domain.models import DirectorPlan, ScriptSpec, ShotSpec, StorySpec


@dataclass(frozen=True)
class StageContract:
    stage: CreativeStage
    owner: StageOwner
    upstream: tuple[CreativeStage, ...]
    may_change_story_meaning: bool
    notes: str


CONTRACTS: dict[CreativeStage, StageContract] = {
    CreativeStage.RESEARCH: StageContract(
        CreativeStage.RESEARCH, StageOwner.RESEARCH_ENGINE, (), False,
        "Owns verified source claims and competitor metadata; raw competitor wording is never a creative source."
    ),
    CreativeStage.TOPIC_STRATEGY: StageContract(
        CreativeStage.TOPIC_STRATEGY, StageOwner.TOPIC_ENGINE, (CreativeStage.RESEARCH,), True,
        "Owns audience/topic fit, collision risk and the independently differentiated angle."
    ),
    CreativeStage.PACKAGING: StageContract(
        CreativeStage.PACKAGING, StageOwner.PACKAGING_ENGINE, (CreativeStage.TOPIC_STRATEGY,), False,
        "Owns the packaging promise and hypotheses; it may not copy competitor titles or thumbnails."
    ),
    CreativeStage.ORIGINALITY: StageContract(
        CreativeStage.ORIGINALITY, StageOwner.ORIGINALITY_ENGINE, (), False,
        "Independent hard gate for wording, title, idea and structure collisions."
    ),
    CreativeStage.SCRIPT_REVIEW: StageContract(
        CreativeStage.SCRIPT_REVIEW, StageOwner.REVIEW_ENGINE, (CreativeStage.SCRIPT,), False,
        "Independent anti-repetition and producibility review; it never silently rewrites the screenplay."
    ),
    CreativeStage.RELEASE_PACKAGE: StageContract(
        CreativeStage.RELEASE_PACKAGE, StageOwner.PACKAGING_ENGINE, (CreativeStage.SCRIPT, CreativeStage.SHOT_SPEC), False,
        "Owns final title/thumbnail/description package after the actual film exists."
    ),
    CreativeStage.STORY: StageContract(
        CreativeStage.STORY,
        StageOwner.STORY_ENGINE,
        (),
        True,
        "Owns premise, causality, turning points and ending state.",
    ),
    CreativeStage.SCRIPT: StageContract(
        CreativeStage.SCRIPT,
        StageOwner.SCRIPT_ENGINE,
        (CreativeStage.STORY,),
        True,
        "Owns scene execution and dialogue without silently changing the approved StorySpec.",
    ),
    CreativeStage.ASSET_BIBLE: StageContract(
        CreativeStage.ASSET_BIBLE,
        StageOwner.ASSET_ENGINE,
        (CreativeStage.SCRIPT,),
        False,
        "Owns persistent visual identities and state variants.",
    ),
    CreativeStage.DIRECTOR_PLAN: StageContract(
        CreativeStage.DIRECTOR_PLAN,
        StageOwner.DIRECTOR_ENGINE,
        (CreativeStage.SCRIPT, CreativeStage.ASSET_BIBLE),
        False,
        "Interprets story into audience, performance, blocking, sound and edit intent.",
    ),
    CreativeStage.SHOT_SPEC: StageContract(
        CreativeStage.SHOT_SPEC,
        StageOwner.CINEMATOGRAPHY_ENGINE,
        (CreativeStage.DIRECTOR_PLAN,),
        False,
        "Turns approved direction into motivated camera and shot execution.",
    ),
    CreativeStage.EDIT_INTENT: StageContract(
        CreativeStage.EDIT_INTENT,
        StageOwner.EDITOR_ENGINE,
        (CreativeStage.SHOT_SPEC,),
        False,
        "Owns editorial timing and cut execution; it may not rewrite the scene's dramatic meaning.",
    ),
}


class CreativeContractError(ValueError):
    pass


class CreativeValidator:
    """Cross-stage semantic gates before expensive media generation."""

    def validate_story_script(self, story: StorySpec, script: ScriptSpec) -> list[str]:
        issues: list[str] = []
        if not script.scenes:
            issues.append("SCRIPT_HAS_NO_SCENES")
        beat_text = " ".join(f"{b.purpose} {b.change}" for b in story.beats).lower()
        if story.protagonist_goal.lower() not in (script.logline + " " + beat_text).lower():
            issues.append("PROTAGONIST_GOAL_NOT_TRACEABLE")
        return issues

    def validate_script_director(self, script: ScriptSpec, director: DirectorPlan) -> list[str]:
        issues: list[str] = []
        script_ids = {s.scene_id for s in script.scenes}
        director_ids = {s.scene_id for s in director.scenes}
        missing = script_ids - director_ids
        extra = director_ids - script_ids
        if missing:
            issues.append("DIRECTOR_MISSING_SCENES:" + ",".join(sorted(missing)))
        if extra:
            issues.append("DIRECTOR_UNKNOWN_SCENES:" + ",".join(sorted(extra)))
        for scene in director.scenes:
            if not scene.cinematography_intent.strip():
                issues.append(f"DIRECTOR_NO_CINEMATOGRAPHY_INTENT:{scene.scene_id}")
            if not scene.audience_know.strip() or not scene.audience_feel.strip():
                issues.append(f"DIRECTOR_NO_AUDIENCE_ENDPOINT:{scene.scene_id}")
        return issues

    def validate_shots(self, director: DirectorPlan, shots: list[ShotSpec]) -> list[str]:
        issues: list[str] = []
        scene_ids = {s.scene_id for s in director.scenes}
        seen_shot_ids: set[str] = set()
        per_scene: dict[str, int] = {sid: 0 for sid in scene_ids}

        for shot in shots:
            if shot.shot_id in seen_shot_ids:
                issues.append(f"DUPLICATE_SHOT_ID:{shot.shot_id}")
            seen_shot_ids.add(shot.shot_id)
            if shot.scene_id not in scene_ids:
                issues.append(f"SHOT_UNKNOWN_SCENE:{shot.shot_id}:{shot.scene_id}")
                continue
            per_scene[shot.scene_id] += 1
            if shot.camera.movement.kind != "static" and not shot.camera.movement.purpose.strip():
                issues.append(f"UNMOTIVATED_CAMERA_MOVE:{shot.shot_id}")
            if len(shot.action_beats) > 4 and shot.duration_seconds <= 6:
                issues.append(f"SHOT_OVERLOADED_ACTION:{shot.shot_id}")
            if shot.performance and not shot.camera.focus_target:
                issues.append(f"PERFORMANCE_WITHOUT_CAMERA_TARGET:{shot.shot_id}")

        for scene_id, count in per_scene.items():
            if count == 0:
                issues.append(f"SCENE_WITHOUT_SHOTS:{scene_id}")
        return issues

    def require_clean(self, issues: list[str], stage: str) -> None:
        if issues:
            raise CreativeContractError(f"{stage} failed: " + "; ".join(issues))
