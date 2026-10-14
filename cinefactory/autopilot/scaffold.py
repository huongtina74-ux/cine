from __future__ import annotations

import re

from cinefactory.domain.enums import ShotComplexity
from cinefactory.discovery.models import TopicScore, TopicStrategy
from cinefactory.originality.models import DifferentiationPlan, PackagingHypothesis, ReleasePackage
from cinefactory.domain.models import (
    ActionBeat, AssetBibleSpec, BlockingMap, BlockingPosition, CameraMove, CameraSpec,
    CharacterAssetSpec, CharacterState, DialogueLine, DirectorPlan, PerformancePlan,
    SceneAssetSpec, SceneDirection, ScriptScene, ScriptSpec, ShotSpec, StoryBeat, StorySpec, WorldState,
)


class LocalScaffoldPlanner:
    """Deterministic offline fallback proving the complete pipeline without paid reasoning.

    This is intentionally conservative. Production-quality creative decisions should be supplied
    by OpenClaw/Codex through a reasoning bridge, but the factory remains runnable without them.
    """


    def topic_strategy(self, prompt: str) -> TopicStrategy:
        topic = re.sub(r"\s+", " ", prompt.strip())[:160] or "Untitled topic"
        return TopicStrategy(
            topic=topic,
            angle="Develop the topic from an independent causal thesis rather than a competitor format",
            audience="the intended audience described by the user",
            score=TopicScore(
                demand=5.0, audience_fit=7.0, channel_fit=7.0, evergreen=6.0,
                originality_opportunity=8.0, production_feasibility=7.0, rights_risk=2.0, collision_risk=3.0,
                rationale=["Offline scaffold uses conservative neutral scores; a research agent should replace them with evidence-backed values."],
            ),
            differentiation_axes=[
                "independent thesis and causal explanation",
                "original examples/evidence set",
                "distinct visual and narrative grammar",
            ],
            forbidden_angles=["competitor title rewrites", "competitor hook imitation", "competitor beat-order cloning"],
        )

    def packaging(self, prompt: str, strategy: TopicStrategy) -> PackagingHypothesis:
        short = re.sub(r"\s+", " ", strategy.topic).strip()[:90]
        return PackagingHypothesis(
            promise=f"Deliver a clear, independently reasoned answer about {short}",
            title_candidates=[f"A New Way to Understand {short[:55]}", f"What Most Explanations Miss About {short[:50]}"],
            thumbnail_concepts=["one original visual contradiction tied to the project's thesis", "one simple evidence-led visual with no competitor composition reuse"],
            curiosity_gap="The viewer sees the consequence before the underlying mechanism is revealed.",
            must_deliver=["the promised mechanism", "a concrete example", "a clear resolution"],
            prohibited_claims=["unsupported certainty", "copied competitor promise"],
        )

    def originality_plan(self, strategy: TopicStrategy) -> DifferentiationPlan:
        return DifferentiationPlan(
            original_thesis=strategy.angle,
            target_audience=strategy.audience,
            differentiation_axes=strategy.differentiation_axes,
            evidence_plan=["use independently verified sources when factual", "prefer original examples and synthesis"],
            narrative_device="cause-and-effect discovery built around the project's own thesis",
            visual_grammar="motivated camera and project-specific visual motifs rather than reference imitation",
            forbidden_patterns=strategy.forbidden_angles,
        )

    def release_package(self, script: ScriptSpec, packaging: PackagingHypothesis) -> ReleasePackage:
        title = packaging.title_candidates[0]
        chapters = [f"{i+1}. {scene.dramatic_event[:70]}" for i, scene in enumerate(script.scenes)]
        return ReleasePackage(
            final_title=title,
            thumbnail_concept=packaging.thumbnail_concepts[0],
            description=f"An independently produced film exploring: {script.logline}",
            chapters=chapters,
            disclosure_notes=[],
        )

    def story(self, prompt: str) -> StorySpec:
        title = re.sub(r"\s+", " ", prompt.strip())[:80]
        return StorySpec(
            title=title or "Untitled Film",
            premise=prompt.strip(), theme="truth and consequence",
            protagonist_goal="resolve the central conflict",
            central_conflict="the protagonist must act on incomplete information",
            ending_state="the central question is answered through a visible choice",
            beats=[
                StoryBeat(beat_id="B01", purpose="establish", change="normal state gains a destabilizing clue", audience_question="what changed?"),
                StoryBeat(beat_id="B02", purpose="pressure", change="the protagonist tests the clue and faces resistance", audience_question="who is hiding what?"),
                StoryBeat(beat_id="B03", purpose="turn", change="new evidence changes the power relationship", audience_question="what will the protagonist do?"),
                StoryBeat(beat_id="B04", purpose="resolve", change="a visible action resolves the central dramatic question"),
            ],
        )

    def script(self, story: StorySpec) -> ScriptSpec:
        scenes = []
        for i, beat in enumerate(story.beats, 1):
            sid = f"S{i:02d}"
            scenes.append(ScriptScene(
                scene_id=sid, heading=f"INT. PRIMARY LOCATION - SCENE {i}", location_id="LOC01",
                time_of_day="DAY", dramatic_event=beat.change,
                action=[beat.purpose, beat.change],
                dialogue=[DialogueLine(speaker="C01", text=f"This changes what I thought I knew about {beat.purpose}.", subtext="testing the truth")],
                exit_state_summary=beat.change,
            ))
        return ScriptSpec(title=story.title, logline=f"A protagonist tries to {story.protagonist_goal} while {story.central_conflict}.", scenes=scenes)

    def assets(self, script: ScriptSpec) -> AssetBibleSpec:
        return AssetBibleSpec(
            characters=[CharacterAssetSpec(
                character_id="C01", name="Protagonist", identity_lock="same adult protagonist face and body across all shots",
                appearance="natural realistic adult, distinctive but non-celebrity features", default_costume_id="C01_W01",
                expression_set=["neutral", "concerned", "realization", "resolved"],
            )],
            scenes=[SceneAssetSpec(location_id="LOC01", name="Primary Location", topology_lock="same room geometry, doors, windows and furniture positions", lighting_anchors=["motivated soft key", "consistent practical source"])],
            props=[], visual_style_lock="realistic cinematic photography, natural skin, restrained contrast, motivated lighting, no stylized identity drift",
        )

    def director(self, script: ScriptSpec) -> DirectorPlan:
        directed = []
        for scene in script.scenes:
            directed.append(SceneDirection(
                scene_id=scene.scene_id, dramatic_event=scene.dramatic_event,
                audience_know=scene.dramatic_event, audience_feel="increasing engagement and emotional clarity",
                audience_question="what choice follows from this change?",
                performance_notes={"C01": "play the objective, keep emotion restrained, let the eyes and breath reveal the turn"},
                blocking=BlockingMap(scene_id=scene.scene_id, action_axis="C01-to-primary-story-target", allowed_camera_side="south", positions=[BlockingPosition(subject_id="C01", start="left-midground", end="center-midground", facing="story target", eyeline="story target")]),
                cinematography_intent="begin readable and stable; move closer only when the dramatic information changes",
                sound_intent="clean dialogue, stable room tone, restrained score",
                edit_intent="cut on information change or reaction, not mechanically on every line",
            ))
        return DirectorPlan(
            project_title=script.title,
            visual_concept="naturalistic cinematic realism with motivated camera and continuity-first staging",
            camera_grammar=["stable geography first", "progressively tighter motivated coverage", "no random orbiting"],
            performance_grammar=["objective-driven restrained performance", "readable listening reactions"],
            editing_grammar=["motivated hard cuts", "reaction holds", "preserve spatial and emotional continuity"],
            sound_grammar=["clean dialogue", "stable ambience", "restrained score"],
            scenes=directed,
        )

    def shots(self, script: ScriptSpec, director: DirectorPlan) -> list[ShotSpec]:
        shots: list[ShotSpec] = []
        previous: str | None = None
        for i, scene in enumerate(script.scenes, 1):
            shot_id = f"{scene.scene_id}_SH01"
            emotion = "concerned" if i < len(script.scenes) else "resolved"
            entry = WorldState(
                location_id=scene.location_id, time_of_day=scene.time_of_day, light_state="motivated-soft",
                characters={"C01": CharacterState(character_id="C01", costume_id="C01_W01", position="left-midground", facing="story target", eyeline="story target", emotion=emotion)},
                camera_side="south", motion_axis="C01-to-primary-story-target",
            )
            exit_state = entry.model_copy(deep=True)
            exit_state.characters["C01"].position = "center-midground"
            perf = PerformancePlan(
                objective="learn or act on the scene's new information", action_verb="test",
                outward_mask="controlled", micro_expression={"eyes":"brief hold then decision"},
                body_behavior={"gesture":"one minimal motivated action"}, breath={"pattern":"natural controlled"},
                listening_behavior={"reaction":"process before responding"},
            )
            camera = CameraSpec(
                narrative_purpose="show the protagonist receiving and acting on the scene's information change",
                shot_size="medium" if i == 1 else "medium close-up", lens_mm=40 if i == 1 else 65,
                camera_height="eye-level", angle="neutral", camera_side="south", focus_target="C01 eyes",
                composition="readable geography with motivated negative space", depth_of_field="moderate natural",
                movement=CameraMove(
                    kind="static" if i == 1 else "dolly_in",
                    purpose="preserve geography" if i == 1 else "narrow attention as the dramatic beat changes",
                    amplitude=None if i == 1 else "20cm", speed="very slow", start_second=None if i == 1 else 1.5, end_second=None if i == 1 else 4.5,
                ),
            )
            shot = ShotSpec(
                shot_id=shot_id, scene_id=scene.scene_id, narrative_purpose=scene.dramatic_event,
                audience_endpoint=scene.dramatic_event, duration_seconds=5.0,
                complexity=ShotComplexity.GREEN if i == 1 else ShotComplexity.YELLOW,
                performance={"C01": perf}, entry_state=entry,
                action_beats=[ActionBeat(actor="C01", action="shifts attention and makes one clear motivated movement", start_second=1.0, end_second=3.5)],
                camera=camera, edit_intent="cut after the dramatic beat lands", exit_state=exit_state,
                previous_shot_id=previous,
            )
            if shots:
                shots[-1].next_shot_id = shot_id
            shots.append(shot); previous = shot_id
        return shots
