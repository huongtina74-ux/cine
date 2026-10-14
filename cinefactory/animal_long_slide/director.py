"""VariationDirector: plans the next Long Slide episode so it differs from recent ones."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from .compatibility import SCENE_OBSTACLE_COMPATIBILITY
from .contracts import LongSlideEpisodeSpec, LongSlideSceneKind, OutcomeKind, ReactionEvent
from .planner import LongSlideEpisodePlanner, ModuleDirective
from .safety import MonetizationSafetyGate
from .series import PERIL_OBSTACLES, PERIL_SCENES, SeriesBible
from .variation import (
    POLICY_VERSION,
    EpisodeConcept,
    EpisodeHistory,
    SafetyReport,
    UploadPackage,
    VariationExhaustedError,
    VariationPolicy,
    VariationReport,
    VariedEpisode,
    episode_fingerprint,
    evaluate_variation,
    structural_tokens,
    title_key,
    title_similarity,
)

NOMINAL_MODULE_SECONDS = 43.0
SINGLE_OBSTACLE_SCENES = {
    LongSlideSceneKind.PAINT_GATE,
    LongSlideSceneKind.FOUNTAIN,
    LongSlideSceneKind.KEY_DOOR,
}
BASE_OUTCOMES = [OutcomeKind.SUCCESS, OutcomeKind.COMIC_FAIL, OutcomeKind.TRANSFORM, OutcomeKind.ESCAPE]
# Friends racing beside the lead (side lanes in the Blender worker).
MAX_COMPANIONS = 2
# Signature set pieces the worker can build (scripts/long_slide_gimmicks.py).
GIMMICK_SCENES = {
    "ball_smash": {
        LongSlideSceneKind.LONG_SLIDE, LongSlideSceneKind.SPIRAL_SLIDE, LongSlideSceneKind.BALL_PIT,
        LongSlideSceneKind.GIANT_ANIMAL, LongSlideSceneKind.FOUNTAIN,
    },
    # The rainbow parade is the celebration, so any calm scene can end with it.
    "clone_parade": set(LongSlideSceneKind) - PERIL_SCENES,
}


def _story_beat(index: int, count: int) -> str:
    if index == 0:
        return "setup"
    if index == count - 1:
        return "finale"
    position = index / (count - 1)
    if position < 0.4:
        return "rising"
    if position < 0.7:
        return "twist"
    return "climax"


@dataclass(frozen=True)
class _ModuleChoice:
    index: int
    count: int
    duration: float
    character_id: str
    scene: LongSlideSceneKind
    outcome: OutcomeKind
    camera: list[str]
    obstacles: list[str]


class VariationDirector:
    """Plans the next episode of a channel so it differs from recent episodes.

    Choices are random but weighted towards options that have rested longest,
    hard cooldowns stop recent repeats, and every candidate must pass both the
    variation policy and the MonetizationSafetyGate. If no candidate passes,
    the director raises VariationExhaustedError instead of producing a repeat.
    """

    def __init__(
        self,
        bible: SeriesBible,
        history: EpisodeHistory,
        policy: VariationPolicy | None = None,
        *,
        max_attempts: int = 24,
        renderable_animals: set[str] | frozenset[str] | None = None,
        nominal_module_seconds: float = NOMINAL_MODULE_SECONDS,
        blocked_scenes: set[LongSlideSceneKind] | frozenset[LongSlideSceneKind] | None = None,
    ) -> None:
        # Scene kinds the renderer cannot stage yet are never planned.
        self.blocked_scenes = frozenset(blocked_scenes or ())
        if len(set(LongSlideSceneKind) - self.blocked_scenes - PERIL_SCENES) < 3:
            raise ValueError("at least three non-peril scene kinds must stay available")
        if not 5.0 < nominal_module_seconds <= 90.0:
            raise ValueError("nominal_module_seconds must be in (5, 90]")
        self.nominal_module_seconds = nominal_module_seconds
        self.bible = bible
        self.history = history
        self.policy = policy or VariationPolicy()
        self.max_attempts = max_attempts
        # When given, only these animals are picked as race companions, so a
        # planned race never depends on an animal the renderer cannot animate.
        self.renderable_animals = frozenset(renderable_animals) if renderable_animals is not None else None

    # -- concept --

    def _pick(self, axis: str, options: list[str], rng: random.Random) -> str:
        records = self.history.records()
        cooldown = self.policy.cooldowns.get(axis, 0)
        blocked = {r.fingerprint.get(axis) for r in records[-cooldown:]} if cooldown else set()
        allowed = [o for o in options if o not in blocked]
        if not allowed:
            raise VariationExhaustedError([f"COOLDOWN_EXHAUSTED:{axis}"])
        weights = []
        for option in allowed:
            last = max((i for i, r in enumerate(records) if r.fingerprint.get(axis) == option), default=None)
            weights.append(float(len(records) + 2 if last is None else len(records) - last))
        return rng.choices(allowed, weights=weights, k=1)[0]

    def _cast_lineup(self, lead: str, rng: random.Random) -> list[str]:
        others = [c.character_id for c in self.bible.cast if c.character_id != lead]
        previous = self.history.recent(1)
        lineup: list[str] = []
        for _ in range(6):
            size = rng.randint(self.bible.min_cast, self.bible.max_cast)
            lineup = [lead, *rng.sample(others, k=size - 1)]
            if not previous or ",".join(sorted(lineup)) != previous[0].fingerprint.get("cast"):
                break
        return lineup

    def _choose_concept(self, rng: random.Random) -> EpisodeConcept:
        lead = self._pick("lead", [c.character_id for c in self.bible.cast], rng)
        return EpisodeConcept(
            format_id=self._pick("format", [f.format_id for f in self.bible.formats], rng),
            lead_character_id=lead,
            cast_ids=self._cast_lineup(lead, rng),
            environment_id=self._pick("environment", [e.theme_id for e in self.bible.environments], rng),
            ending_id=self._pick("ending", [e.ending_id for e in self.bible.endings], rng),
            camera_style_id=self._pick("camera_style", [s.style_id for s in self.bible.camera_styles], rng),
        )

    # -- module sequences --

    def _scene_sequence(self, concept: EpisodeConcept, rng: random.Random, count: int) -> list[LongSlideSceneKind]:
        preferred = [s for s in self.bible.challenge(concept.format_id).scenes if s not in self.blocked_scenes]
        others = [s for s in LongSlideSceneKind if s not in preferred and s not in self.blocked_scenes]
        if not preferred:
            preferred, others = others[:2], others[2:]
        cap = self.policy.peril_cap(count)
        seq: list[LongSlideSceneKind] = []
        bag: list[LongSlideSceneKind] = []
        for _ in range(count):
            if not bag:
                bag = preferred * 2 + rng.sample(others, k=min(2, len(others)))
                rng.shuffle(bag)
            peril_used = sum(1 for s in seq if s in PERIL_SCENES)
            index = next((j for j, s in enumerate(bag)
                          if (not seq or s != seq[-1]) and not (s in PERIL_SCENES and peril_used >= cap)), None)
            if index is None:
                seq.append(next(s for s in preferred + others if s not in PERIL_SCENES and (not seq or s != seq[-1])))
            else:
                seq.append(bag.pop(index))
        return self._finish_scene_sequence(seq, preferred + others)

    def _finish_scene_sequence(
        self, seq: list[LongSlideSceneKind], pool: list[LongSlideSceneKind],
    ) -> list[LongSlideSceneKind]:
        if seq[-1] in PERIL_SCENES:
            seq[-1] = next(s for s in pool if s not in PERIL_SCENES and s != seq[-2])
        for scene in pool:
            if len(set(seq)) >= self.policy.min_scene_kinds:
                break
            if scene in seq or scene in PERIL_SCENES:
                continue
            for j in range(1, len(seq) - 1):
                if seq.count(seq[j]) > 1 and seq[j - 1] != scene and seq[j + 1] != scene:
                    seq[j] = scene
                    break
        return seq

    def _character_sequence(self, concept: EpisodeConcept, rng: random.Random, count: int) -> list[str]:
        lead = concept.lead_character_id
        others = [c for c in concept.cast_ids if c != lead]
        seq: list[str] = [lead]
        pool: list[str] = []
        for i in range(1, count - 1):
            if not pool:
                pool = others + ([lead] if count > 6 else [])
                rng.shuffle(pool)
            j = next((k for k, c in enumerate(pool) if c != seq[-1] and not (i == count - 2 and c == lead)), None)
            seq.append(pool.pop(j) if j is not None else next(c for c in others if c != seq[-1]))
        seq.append(lead)
        return seq

    def _outcome_sequence(
        self, concept: EpisodeConcept, rng: random.Random, scenes: list[LongSlideSceneKind],
    ) -> list[OutcomeKind]:
        seq: list[OutcomeKind] = []
        pool: list[OutcomeKind] = []
        for scene in scenes[:-1]:
            if scene in PERIL_SCENES:
                seq.append(rng.choice([OutcomeKind.ESCAPE, OutcomeKind.SUCCESS]))
                continue
            if not pool:
                pool = BASE_OUTCOMES[:]
                rng.shuffle(pool)
            seq.append(pool.pop())
        seq.append(self.bible.ending(concept.ending_id).final_outcome)
        for outcome in BASE_OUTCOMES:
            if len(set(seq)) >= self.policy.min_outcome_kinds:
                break
            if outcome in seq:
                continue
            for j in range(1, len(seq) - 1):
                if scenes[j] not in PERIL_SCENES and seq.count(seq[j]) > 1:
                    seq[j] = outcome
                    break
        return seq

    def _camera_sequence(self, concept: EpisodeConcept, rng: random.Random, count: int) -> list[list[str]]:
        variants = self.bible.camera_style(concept.camera_style_id).variants
        seq: list[list[str]] = []
        for _ in range(count):
            options = [v for v in variants if not seq or v != seq[-1]]
            seq.append(list(rng.choice(options)))
        return seq

    @staticmethod
    def _obstacles(scene: LongSlideSceneKind, rng: random.Random) -> list[str]:
        compatible = sorted(SCENE_OBSTACLE_COMPATIBILITY[scene])
        if scene not in PERIL_SCENES:
            compatible = [o for o in compatible if o not in PERIL_OBSTACLES]
        k = 1 if scene in SINGLE_OBSTACLE_SCENES else 2
        return rng.sample(compatible, k=min(k, len(compatible)))

    def _companions(self, choice: _ModuleChoice, concept: EpisodeConcept, rng: random.Random) -> list[str]:
        """Up to two cast friends race beside the module character; peril scenes stay solo."""
        if choice.scene in PERIL_SCENES or any(o in PERIL_OBSTACLES for o in choice.obstacles):
            return []
        lead_animal = self.bible.character(choice.character_id).animal_id
        pool = []
        for character_id in concept.cast_ids:
            animal = self.bible.character(character_id).animal_id
            if character_id == choice.character_id or animal == lead_animal or animal in pool:
                continue
            if self.renderable_animals is not None and animal not in self.renderable_animals:
                continue
            pool.append(animal)
        if not pool:
            return []
        return rng.sample(pool, k=min(rng.randint(1, MAX_COMPANIONS), len(pool)))

    @staticmethod
    def _gimmicks(choice: _ModuleChoice, previous: list[str], rng: random.Random) -> list[str]:
        """Set pieces for one module: doors open the episode, the rainbow parade ends it
        (or the module before, when the last two would repeat), smashes and parades in
        between, never the same piece twice in a row."""
        peril = choice.scene in PERIL_SCENES or any(o in PERIL_OBSTACLES for o in choice.obstacles)
        picked: list[str] = []
        if choice.index == 0:
            picked.append("door_reveal")
        if peril:
            return picked
        allowed = [g for g, scenes in GIMMICK_SCENES.items() if choice.scene in scenes and g not in previous]
        if choice.index == choice.count - 1 and "clone_parade" in allowed:
            return picked + ["clone_parade"]
        if allowed and (choice.index > 0 or rng.random() < 0.5):
            picked.append(rng.choice(allowed))
        return picked

    def _directive(
        self, choice: _ModuleChoice, concept: EpisodeConcept, rng: random.Random, previous_gimmicks: list[str] | None = None,
    ) -> ModuleDirective:
        character = self.bible.character(choice.character_id)
        gimmicks = self._gimmicks(choice, previous_gimmicks or [], rng)
        companions = [] if "clone_parade" in gimmicks else self._companions(choice, concept, rng)
        return ModuleDirective(
            animal_id=character.animal_id,
            scene_kind=choice.scene,
            outcome=choice.outcome,
            camera_patterns=choice.camera,
            obstacle_ids=choice.obstacles,
            extra_events=[ReactionEvent(
                event_id=f"signature_{character.character_id}",
                at_seconds=round(choice.duration * rng.uniform(0.40, 0.55), 3),
                event_type="CHARACTER_SIGNATURE",
                payload={"character": character.name, "move": character.signature},
            )],
            metadata={
                "character_id": character.character_id,
                "character_name": character.name,
                "story_beat": _story_beat(choice.index, choice.count),
                "challenge_format": concept.format_id,
                "camera_style": concept.camera_style_id,
                "environment": self.bible.environment(concept.environment_id).render_settings(),
                "peril": choice.scene in PERIL_SCENES or any(o in PERIL_OBSTACLES for o in choice.obstacles),
                "companions": companions,
                "gimmicks": gimmicks,
            },
        )

    def _module_directives(self, concept: EpisodeConcept, rng: random.Random, target: float) -> list[ModuleDirective]:
        count = max(4, math.ceil(target / self.nominal_module_seconds))
        duration = target / count
        if not 5.0 < duration <= 90.0:
            raise ValueError(f"module duration {duration:.2f}s is outside (5, 90]")
        scenes = self._scene_sequence(concept, rng, count)
        characters = self._character_sequence(concept, rng, count)
        outcomes = self._outcome_sequence(concept, rng, scenes)
        cameras = self._camera_sequence(concept, rng, count)
        directives: list[ModuleDirective] = []
        seen: set[tuple] = set()
        for i in range(count):
            animal = self.bible.character(characters[i]).animal_id
            obstacles = self._obstacles(scenes[i], rng)
            for _ in range(4):
                if (animal, scenes[i], tuple(obstacles), outcomes[i]) not in seen:
                    break
                obstacles = self._obstacles(scenes[i], rng)
            seen.add((animal, scenes[i], tuple(obstacles), outcomes[i]))
            choice = _ModuleChoice(i, count, duration, characters[i], scenes[i], outcomes[i], cameras[i], obstacles)
            previous = directives[-1].metadata.get("gimmicks", []) if directives else []
            directives.append(self._directive(choice, concept, rng, previous))
        return directives

    # -- packaging --

    def _friends(self, concept: EpisodeConcept) -> list[str]:
        return [self.bible.character(c).name for c in concept.cast_ids if c != concept.lead_character_id]

    def _description(self, concept: EpisodeConcept, rng: random.Random, episode_number: int) -> str:
        lead = self.bible.character(concept.lead_character_id)
        env = self.bible.environment(concept.environment_id)
        friends = self._friends(concept)
        friend_text = ", ".join(friends[:-1]) + f" and {friends[-1]}" if len(friends) > 1 else friends[0]
        synopsis = rng.choice(self.bible.challenge(concept.format_id).synopsis_templates).format(
            lead=lead.name, lead_animal=lead.animal_id, env=env.label, friends=friend_text,
        )
        ending = self.bible.ending(concept.ending_id).line.format(lead=lead.name)
        cast_lines = "\n".join(
            f"- {c.name} the {c.animal_id}: {c.trait}"
            for c in (self.bible.character(cid) for cid in concept.cast_ids)
        )
        return (
            f"{synopsis} {ending}\n\nIn this episode:\n{cast_lines}\n\n"
            f"Episode {episode_number} of {self.bible.brand}. Every character, slide and world in this "
            "series is original 3D animation made by our studio."
        )

    def _title_allowed(self, title: str) -> bool:
        if len(title) > self.policy.max_title_length or title_key(title) in self.history.title_keys():
            return False
        recent = [r.title for r in self.history.recent(self.policy.title_window)]
        return all(title_similarity(title, t) <= self.policy.max_title_similarity for t in recent)

    def _package(self, concept: EpisodeConcept, rng: random.Random, episode_number: int) -> UploadPackage | None:
        lead = self.bible.character(concept.lead_character_id)
        env = self.bible.environment(concept.environment_id)
        fmt = self.bible.challenge(concept.format_id)
        friends = self._friends(concept)
        templates = fmt.title_templates[:]
        rng.shuffle(templates)
        for template in templates:
            for k in (2, 1):
                names = [lead.name, *friends[:k]]
                title = template.format(
                    lead=lead.name, lead_animal=lead.animal_id.title(), env=env.label,
                    friends=" & ".join(friends[:k]), crew=", ".join(names[:-1]) + " & " + names[-1],
                    brand=self.bible.brand,
                )
                if not self._title_allowed(title):
                    continue
                tags = list(dict.fromkeys([
                    self.bible.brand, "long slide", "3d animation", "kids animation", fmt.label, env.label,
                    *[self.bible.character(c).animal_id for c in concept.cast_ids],
                ]))
                return UploadPackage(title=title, description=self._description(concept, rng, episode_number), tags=tags)
        return None

    # -- main entry --

    def _candidate(
        self, project_id: str, episode_id: str, target: float, seed: int, attempt: int,
    ) -> VariedEpisode | None:
        rng = random.Random(seed * 7919 + attempt)
        concept = self._choose_concept(rng)
        directives = self._module_directives(concept, rng, target)
        planner_seed = seed * 100 + attempt
        episode: LongSlideEpisodeSpec = LongSlideEpisodePlanner(seed=planner_seed).plan(
            project_id=project_id, episode_id=episode_id, title=episode_id,
            target_duration_seconds=target, module_plan=directives,
        )
        package = self._package(concept, rng, len(self.history) + 1)
        if package is None:
            return None
        concept = concept.model_copy(update={"synopsis": package.description.split("\n", 1)[0]})
        fingerprint = episode_fingerprint(concept, episode)
        tokens = structural_tokens(concept, episode)
        max_sim, min_changes, findings = evaluate_variation(self.policy, fingerprint, tokens, self.history)
        episode = episode.model_copy(update={"title": package.title, "metadata": {
            **episode.metadata, "series_brand": self.bible.brand, "concept": concept.model_dump(mode="json"),
            "variation_policy": POLICY_VERSION, "made_for_kids": True,
        }})
        package = package.model_copy(update={"evidence": {
            "policy_version": POLICY_VERSION, "concept": concept.model_dump(mode="json"),
            "fingerprint": fingerprint, "planner_seed": planner_seed,
            "originality_signature": episode.originality_signature, "max_similarity": max_sim,
            "min_axis_changes": min_changes, "human_review": "required before upload",
        }})
        report = VariationReport(passed=not findings, attempts=attempt + 1, max_similarity=max_sim,
                                 min_axis_changes=min_changes, findings=findings)
        return VariedEpisode(episode=episode, concept=concept, fingerprint=fingerprint, tokens=tokens,
                             report=report, package=package, safety=SafetyReport(passed=False))

    def next_episode(
        self,
        *,
        project_id: str,
        episode_id: str,
        target_duration_seconds: float = 330.0,
        seed: int = 1,
    ) -> VariedEpisode:
        gate = MonetizationSafetyGate(self.policy, self.bible)
        failures: list[str] = []
        for attempt in range(self.max_attempts):
            candidate = self._candidate(project_id, episode_id, float(target_duration_seconds), seed, attempt)
            if candidate is None:
                failures.append("TITLE_POOL_EXHAUSTED")
                continue
            safety = gate.review(candidate, self.history)
            candidate = candidate.model_copy(update={"safety": safety})
            if candidate.report.passed and safety.passed:
                return candidate
            failures.extend(candidate.report.findings + [f.code for f in safety.findings])
        raise VariationExhaustedError(failures or ["NO_VALID_EPISODE"])
