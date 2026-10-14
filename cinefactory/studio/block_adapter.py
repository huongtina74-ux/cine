from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from cinefactory.block_animation.contracts import (
    ActionCue,
    ActorPlacement,
    CameraIntent,
    EpisodeSpec,
    ExpressionCue,
    GazeCue,
    ReactionTrigger,
    ShotPerformanceSpec,
    TransformSpec,
    Vec3,
)
from cinefactory.domain.models import ShotSpec

from .craft_execution import (
    CreativeIntentGraph,
    LightingColorIntentPlan,
    PerformanceDirectionBeat,
    PerformanceDirectionPlan,
    ShotCreativeIntent,
    ShotLightingColorIntent,
)


class BlockProductionStyle(StrEnum):
    MINECRAFT = "MINECRAFT"
    ROBLOX_R6 = "ROBLOX_R6"
    ROBLOX_R15 = "ROBLOX_R15"


class BlockStyleProfile(BaseModel):
    style: BlockProductionStyle
    scene_template_id: str
    rig_ids: list[str]
    quality_profile: str = "rtx3060_quality"


STYLE_PROFILES: dict[BlockProductionStyle, BlockStyleProfile] = {
    BlockProductionStyle.MINECRAFT: BlockStyleProfile(
        style=BlockProductionStyle.MINECRAFT,
        scene_template_id="minecraft_classroom",
        rig_ids=["mc_a", "mc_b", "mc_c"],
    ),
    BlockProductionStyle.ROBLOX_R6: BlockStyleProfile(
        style=BlockProductionStyle.ROBLOX_R6,
        scene_template_id="roblox_classroom",
        rig_ids=["r6_a", "r6_b", "r6_c"],
    ),
    BlockProductionStyle.ROBLOX_R15: BlockStyleProfile(
        style=BlockProductionStyle.ROBLOX_R15,
        scene_template_id="roblox_classroom",
        rig_ids=["r15_validation"],
    ),
}


def detect_block_style(
    prompt: str,
    domain: str | None = None,
) -> BlockProductionStyle | None:
    text = f"{domain or ''} {prompt}".lower()
    if "minecraft" in text:
        return BlockProductionStyle.MINECRAFT
    if "roblox" in text and "r15" in text:
        return BlockProductionStyle.ROBLOX_R15
    if "roblox" in text:
        return BlockProductionStyle.ROBLOX_R6
    return None


class CompanyToBlockAdapter:
    """Bind approved studio intent into executable block-animation cues.

    Legacy callers may omit all professional intent models. In that case the
    adapter keeps the deterministic v1.6 fallback behavior.
    """

    EMOTION_MAP = {
        "neutral": "neutral",
        "concerned": "confused",
        "confused": "confused",
        "surprised": "surprised",
        "terrified": "terrified",
        "afraid": "terrified",
        "fear": "terrified",
        "angry": "angry",
        "sad": "sad",
        "happy": "happy",
        "resolved": "happy",
        "smug": "smug",
    }

    EXPRESSION_TOKENS = (
        (("terror", "terrified", "fear", "afraid"), "terrified"),
        (("surprise", "surprised", "shock"), "surprised"),
        (("anger", "angry", "furious"), "angry"),
        (("sad", "grief", "cry"), "sad"),
        (("happy", "smile", "relief", "resolved"), "happy"),
        (("confused", "uncertain", "question"), "confused"),
        (("smug", "confident"), "smug"),
    )

    ACTION_TOKENS = (
        (("sprint", "run", "chase"), "run"),
        (("walk", "approach", "cross"), "walk"),
        (("point", "indicate"), "point"),
        (("wave", "greet"), "wave"),
        (("push", "shove"), "push"),
        (("grab", "take", "pick up", "pickup"), "grab"),
        (("jump", "leap"), "jump"),
        (("fall", "collapse"), "fall"),
        (("flinch",), "flinch"),
        (("recoil", "shock"), "shock_recoil"),
        (("look", "turn", "notice", "test"), "turn_head"),
    )

    REACTION_TRIGGERS = {"impact", "reveal", "accusation"}

    @staticmethod
    def _actor_ids(shot: ShotSpec) -> list[str]:
        ids = list(shot.performance)
        for actor_id in shot.entry_state.characters:
            if actor_id not in ids:
                ids.append(actor_id)
        return ids or ["C01"]

    @staticmethod
    def _fallback_transform(index: int, count: int) -> TransformSpec:
        spacing = 2.2
        center = (count - 1) / 2
        return TransformSpec(
            location=Vec3(
                x=(index - center) * spacing,
                y=0.5,
                z=0.0,
            )
        )

    @classmethod
    def _transform(
        cls,
        shot: ShotSpec,
        actor_id: str,
        index: int,
        count: int,
    ) -> TransformSpec:
        state = shot.entry_state.characters.get(actor_id)
        raw = ((state.position if state else None) or "").lower()
        if not raw:
            return cls._fallback_transform(index, count)

        x = None
        y = None
        if "left" in raw:
            x = -1.25
        elif "right" in raw:
            x = 1.25
        elif "center" in raw or "centre" in raw:
            x = 0.0

        if "foreground" in raw or "front" in raw:
            y = -0.45
        elif "background" in raw or "back" in raw:
            y = 1.35
        elif "midground" in raw or "middle" in raw:
            y = 0.45

        if x is None and y is None:
            return cls._fallback_transform(index, count)
        fallback = cls._fallback_transform(index, count)
        return TransformSpec(
            location=Vec3(
                x=fallback.location.x if x is None else x,
                y=fallback.location.y if y is None else y,
                z=0.0,
            )
        )

    @staticmethod
    def _directive_map(
        plan: PerformanceDirectionPlan | None,
    ) -> dict[str, list[PerformanceDirectionBeat]]:
        out: dict[str, list[PerformanceDirectionBeat]] = {}
        if plan is None:
            return out
        for beat in plan.beats:
            out.setdefault(beat.shot_id, []).append(beat)
        return out

    @staticmethod
    def _intent_map(
        graph: CreativeIntentGraph | None,
    ) -> dict[str, ShotCreativeIntent]:
        if graph is None:
            return {}
        return {item.shot_id: item for item in graph.shots}

    @staticmethod
    def _lighting_map(
        plan: LightingColorIntentPlan | None,
    ) -> dict[str, ShotLightingColorIntent]:
        if plan is None:
            return {}
        return {item.shot_id: item for item in plan.shots}

    @classmethod
    def _clip_for_directive(
        cls,
        beat: PerformanceDirectionBeat,
    ) -> str:
        text = " ".join(
            filter(
                None,
                [
                    beat.action_verb,
                    beat.gesture_intent,
                    beat.expression_intent,
                ],
            )
        ).lower()
        for tokens, clip in cls.ACTION_TOKENS:
            if any(token in text for token in tokens):
                return clip
        if beat.gaze_target:
            return "turn_head"
        return "turn_head"

    @classmethod
    def _expression_for_directive(
        cls,
        beat: PerformanceDirectionBeat,
        fallback: str,
    ) -> str:
        text = (beat.expression_intent or "").lower()
        for tokens, expression in cls.EXPRESSION_TOKENS:
            if any(token in text for token in tokens):
                return expression
        return fallback

    @staticmethod
    def _camera_pattern(
        shot: ShotSpec,
    ) -> tuple[str, str]:
        if shot.previous_shot_id is None:
            return "fidelity_establish", "fidelity_establish"

        movement = (shot.camera.movement.kind or "static").lower()
        size = (shot.camera.shot_size or "").lower()
        if "orbit" in movement:
            return "fidelity_orbit", "fidelity_orbit"
        if movement in {"track", "truck", "tracking"}:
            return "fidelity_track", "fidelity_track"
        if (
            movement in {"dolly_in", "push_in", "zoom_in"}
            or size
            in {
                "medium close-up",
                "medium close up",
                "mcu",
                "close-up",
                "close up",
                "cu",
                "extreme close-up",
                "extreme close up",
                "ecu",
            }
        ):
            return "fidelity_reaction", "fidelity_reaction"
        if size in {
            "wide",
            "wide shot",
            "ws",
            "medium wide",
            "medium wide shot",
            "mws",
        }:
            return "fidelity_group", "fidelity_group"
        return "fidelity_medium", "fidelity_medium"

    @staticmethod
    def _explicit_gaze_target(
        shot: ShotSpec,
        beat: PerformanceDirectionBeat,
        actor_ids: list[str],
    ) -> str | None:
        if (
            beat.gaze_target
            and beat.gaze_target in actor_ids
            and beat.gaze_target != beat.subject_id
        ):
            return beat.gaze_target
        for action in shot.action_beats:
            if (
                action.actor == beat.subject_id
                and action.target
                and action.target in actor_ids
                and action.target != beat.subject_id
            ):
                return action.target
        state = shot.entry_state.characters.get(beat.subject_id)
        if (
            state is not None
            and state.eyeline
            and state.eyeline in actor_ids
            and state.eyeline != beat.subject_id
        ):
            return state.eyeline
        return None

    def adapt_shot(
        self,
        shot: ShotSpec,
        profile: BlockStyleProfile,
        *,
        creative_intent: ShotCreativeIntent | None = None,
        performance_directives: list[PerformanceDirectionBeat] | None = None,
        lighting_intent: ShotLightingColorIntent | None = None,
    ) -> ShotPerformanceSpec:
        actor_ids = self._actor_ids(shot)
        directives = performance_directives or []
        directive_by_actor = {
            item.subject_id: item
            for item in directives
        }

        actors = []
        for index, actor_id in enumerate(actor_ids):
            directive = directive_by_actor.get(actor_id)
            gaze_target = (
                self._explicit_gaze_target(
                    shot,
                    directive,
                    actor_ids,
                )
                if directive is not None
                else None
            )
            actors.append(
                ActorPlacement(
                    actor_id=actor_id,
                    rig_id=profile.rig_ids[index % len(profile.rig_ids)],
                    transform=self._transform(
                        shot,
                        actor_id,
                        index,
                        len(actor_ids),
                    ),
                    facing_target=gaze_target,
                )
            )

        expressions: list[ExpressionCue] = []
        actions: list[ActionCue] = []
        gaze: list[GazeCue] = []
        reactions: list[ReactionTrigger] = []

        for actor_id in actor_ids:
            state = shot.entry_state.characters.get(actor_id)
            emotion = (state.emotion if state else None) or "neutral"
            fallback_expression = self.EMOTION_MAP.get(
                emotion.lower(),
                "neutral",
            )
            directive = directive_by_actor.get(actor_id)
            expression_id = (
                self._expression_for_directive(
                    directive,
                    fallback_expression,
                )
                if directive is not None
                else fallback_expression
            )
            expressions.append(
                ExpressionCue(
                    actor_id=actor_id,
                    expression_id=expression_id,
                    start_seconds=0,
                    end_seconds=min(
                        shot.duration_seconds,
                        max(0.5, shot.duration_seconds * 0.8),
                    ),
                    intensity=0.75,
                )
            )

            if directive is not None:
                clip = self._clip_for_directive(directive)
                start = min(
                    0.15,
                    max(0.0, shot.duration_seconds / 6),
                )
                end = min(
                    shot.duration_seconds,
                    max(start + 0.25, shot.duration_seconds * 0.55),
                )
                actions.append(
                    ActionCue(
                        actor_id=actor_id,
                        clip_id=clip,
                        start_seconds=start,
                        end_seconds=end,
                        intensity=0.75,
                    )
                )
                gaze_target = self._explicit_gaze_target(
                    shot,
                    directive,
                    actor_ids,
                )
                if gaze_target is not None:
                    gaze.append(
                        GazeCue(
                            actor_id=actor_id,
                            target_actor_id=gaze_target,
                            start_seconds=start,
                            end_seconds=end,
                            intensity=1.0,
                        )
                    )
                trigger = (
                    (directive.reaction_trigger or "")
                    .strip()
                    .lower()
                )
                if trigger in self.REACTION_TRIGGERS:
                    source = next(
                        (
                            item
                            for item in actor_ids
                            if item != actor_id
                        ),
                        None,
                    )
                    reactions.append(
                        ReactionTrigger(
                            trigger=trigger,
                            at_seconds=min(
                                shot.duration_seconds * 0.35,
                                max(
                                    0.1,
                                    shot.duration_seconds - 0.1,
                                ),
                            ),
                            source_actor_id=source,
                            target_actor_ids=[actor_id],
                        )
                    )

        if not actions:
            actions = [
                ActionCue(
                    actor_id=actor_ids[0],
                    clip_id="turn_head",
                    start_seconds=min(
                        0.15,
                        shot.duration_seconds / 4,
                    ),
                    end_seconds=min(
                        shot.duration_seconds,
                        0.75,
                    ),
                    intensity=0.7,
                )
            ]

        purpose, pattern_id = self._camera_pattern(shot)
        target_ids = (
            list(creative_intent.performance_objectives)
            if creative_intent is not None
            else []
        )
        target_ids = [
            actor_id
            for actor_id in target_ids
            if actor_id in actor_ids
        ] or (
            actor_ids[:1]
            if purpose == "fidelity_reaction"
            else actor_ids[:2]
        )

        return ShotPerformanceSpec(
            shot_id=shot.shot_id,
            scene_template_id=profile.scene_template_id,
            duration_seconds=shot.duration_seconds,
            actors=actors,
            actions=actions,
            expressions=expressions,
            reactions=reactions,
            gaze=gaze,
            camera=CameraIntent(
                purpose=purpose,
                pattern_id=pattern_id,
                targets=target_ids,
            ),
            creative_intent=(
                creative_intent.model_dump(mode="json")
                if creative_intent is not None
                else {}
            ),
            performance_directives=[
                item.model_dump(mode="json")
                for item in directives
            ],
            lighting_intent=(
                lighting_intent.model_dump(mode="json")
                if lighting_intent is not None
                else {}
            ),
            narrative_purpose=shot.narrative_purpose,
        )

    def adapt_episode(
        self,
        *,
        project_id: str,
        episode_id: str,
        title: str,
        shots: list[ShotSpec],
        style: BlockProductionStyle,
        fps: int = 24,
        width: int = 1280,
        height: int = 720,
        quality_profile: str | None = None,
        blocked_reference_tokens: list[str] | None = None,
        creative_intent_graph: CreativeIntentGraph | None = None,
        performance_direction: PerformanceDirectionPlan | None = None,
        lighting_color_intent: LightingColorIntentPlan | None = None,
    ) -> EpisodeSpec:
        profile = STYLE_PROFILES[style]
        intent_by_shot = self._intent_map(creative_intent_graph)
        directives_by_shot = self._directive_map(
            performance_direction
        )
        lighting_by_shot = self._lighting_map(
            lighting_color_intent
        )

        return EpisodeSpec(
            project_id=project_id,
            episode_id=episode_id,
            title=title,
            fps=fps,
            width=width,
            height=height,
            quality_profile=quality_profile or profile.quality_profile,
            shots=[
                self.adapt_shot(
                    shot,
                    profile,
                    creative_intent=intent_by_shot.get(
                        shot.shot_id
                    ),
                    performance_directives=directives_by_shot.get(
                        shot.shot_id,
                        [],
                    ),
                    lighting_intent=lighting_by_shot.get(
                        shot.shot_id
                    ),
                )
                for shot in shots
            ],
            blocked_reference_tokens=blocked_reference_tokens or [],
            metadata={
                "visual_style_gate": True,
                "visual_style": style.value,
                "human_review_required": True,
                "source_adapter": "CompanyToBlockAdapter",
                "craft_intent_bound": any(
                    (
                        creative_intent_graph is not None,
                        performance_direction is not None,
                        lighting_color_intent is not None,
                    )
                ),
            },
        )
