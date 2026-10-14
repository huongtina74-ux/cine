from __future__ import annotations

import math
import random
from typing import Any

from pydantic import BaseModel, Field

from .compatibility import SCENE_OBSTACLE_COMPATIBILITY
from .contracts import (
    CameraBeat,
    LongSlideEpisodeSpec,
    LongSlideModuleSpec,
    LongSlideSceneKind,
    ObstaclePlacement,
    OutcomeKind,
    ReactionEvent,
)


DEFAULT_ANIMALS = [
    "elephant", "tiger", "gorilla", "cow", "hippo",
    "lion", "buffalo", "giraffe", "duck", "dinosaur",
]

SCENE_ROTATION = [
    LongSlideSceneKind.LONG_SLIDE,
    LongSlideSceneKind.SPIRAL_SLIDE,
    LongSlideSceneKind.PAINT_GATE,
    LongSlideSceneKind.FOUNTAIN,
    LongSlideSceneKind.BALL_PIT,
    LongSlideSceneKind.CAGE,
    LongSlideSceneKind.KEY_DOOR,
    LongSlideSceneKind.GIANT_ANIMAL,
]

OBSTACLES = [
    "rotating_hammer", "spinning_bar", "ball_pit",
    "paint_gate", "water_pool", "break_wall",
    "bridge", "cage", "giant_duck",
]

OUTCOMES = [
    OutcomeKind.SUCCESS,
    OutcomeKind.COMIC_FAIL,
    OutcomeKind.TRANSFORM,
    OutcomeKind.ESCAPE,
]

# Directed modules keep every camera hold under the 12 s QC pacing limit:
# with at most +/-15 % jitter around 9 s slots, no beat can exceed ~11.8 s.
DIRECTED_BEAT_SECONDS = 9.0
DIRECTED_BEAT_JITTER = 0.15
assert DIRECTED_BEAT_JITTER <= 0.15, "larger jitter can push a 90 s module past the 12 s camera hold limit"


def _beat_patterns(patterns: list[str], count: int) -> list[str]:
    """Open on the first pattern, close on the last, never repeat a pattern back to back."""
    if count <= 1:
        return patterns[:1]
    n = len(patterns)
    seq = [patterns[0]]
    for i in range(1, count - 1):
        candidate = patterns[0]
        for k in range(n):
            candidate = patterns[(i + k) % n]
            closing_clash = i == count - 2 and candidate == patterns[-1] and n > 2
            if candidate != seq[-1] and not closing_clash:
                break
        seq.append(candidate)
    seq.append(patterns[-1])
    return seq


class ModuleDirective(BaseModel):
    """Per-module creative choice supplied by the VariationDirector."""

    animal_id: str
    scene_kind: LongSlideSceneKind
    outcome: OutcomeKind
    camera_patterns: list[str] = Field(min_length=1)
    obstacle_ids: list[str] | None = None
    extra_events: list[ReactionEvent] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class LongSlideEpisodePlanner:
    """Deterministic vertical planner.

    The planner emits production intent only. Blender-specific geometry, rig and
    renderer semantics stay in the execution layer.
    """

    def __init__(self, *, seed: int = 1) -> None:
        self.seed = int(seed)

    @staticmethod
    def _camera_beats(duration: float, animal: str) -> list[CameraBeat]:
        cuts = [0.0, duration * .18, duration * .48, duration * .70, duration]
        patterns = ["hero_start", "chase", "obstacle_side", "finish_reaction"]
        return [
            CameraBeat(
                pattern_id=patterns[i],
                start_seconds=round(cuts[i], 3),
                end_seconds=round(cuts[i + 1], 3),
                target=animal,
            )
            for i in range(4)
        ]

    @staticmethod
    def _events(duration: float, scene: LongSlideSceneKind, outcome: OutcomeKind) -> list[ReactionEvent]:
        events = [
            ReactionEvent(event_id="start_go", at_seconds=round(duration * .08, 3)),
            ReactionEvent(event_id="speed_wow", at_seconds=round(duration * .34, 3)),
            ReactionEvent(event_id="impact", at_seconds=round(duration * .61, 3)),
        ]
        if scene in {LongSlideSceneKind.PAINT_GATE, LongSlideSceneKind.FOUNTAIN}:
            events.append(
                ReactionEvent(event_id="transform_reveal", at_seconds=round(duration * .76, 3))
            )
        events.append(
            ReactionEvent(
                event_id="winner" if outcome is OutcomeKind.SUCCESS else "outcome_reaction",
                at_seconds=round(duration * .90, 3),
            )
        )
        return events

    @staticmethod
    def _patterned_beats(
        duration: float,
        target: str,
        patterns: list[str],
        rng: random.Random,
    ) -> list[CameraBeat]:
        count = max(len(patterns), math.ceil(duration / DIRECTED_BEAT_SECONDS))
        weights = [
            1.0 + rng.uniform(-DIRECTED_BEAT_JITTER, DIRECTED_BEAT_JITTER)
            for _ in range(count)
        ]
        total = sum(weights)
        cuts = [0.0]
        for weight in weights:
            cuts.append(cuts[-1] + duration * weight / total)
        cuts[-1] = duration
        sequence = _beat_patterns(patterns, count)
        return [
            CameraBeat(
                pattern_id=sequence[i],
                start_seconds=round(cuts[i], 3),
                end_seconds=round(cuts[i + 1], 3),
                target=target,
            )
            for i in range(count)
        ]

    def _directed_module(
        self,
        index: int,
        directive: ModuleDirective,
        module_duration: float,
        rng: random.Random,
    ) -> LongSlideModuleSpec:
        scene = directive.scene_kind
        if directive.obstacle_ids is not None:
            chosen = list(directive.obstacle_ids)
        else:
            compatible = sorted(SCENE_OBSTACLE_COMPATIBILITY[scene])
            chosen = rng.sample(compatible, k=min(2, len(compatible)))
        outcome = directive.outcome
        events = self._events(module_duration, scene, outcome) + list(directive.extra_events)
        return LongSlideModuleSpec(
            module_id=f"LSM_{index + 1:03d}",
            scene_kind=scene,
            animal_id=directive.animal_id,
            duration_seconds=round(module_duration, 3),
            animation_sequence=[
                "idle", "run", "slide", "impact",
                "recover", "celebrate" if outcome is OutcomeKind.SUCCESS else "reaction",
            ],
            obstacles=[
                ObstaclePlacement(
                    obstacle_id=oid,
                    slot=f"obstacle_{slot + 1}",
                    seed=self.seed * 1000 + index * 10 + slot,
                )
                for slot, oid in enumerate(chosen)
            ],
            controlled_phase_seconds=round(module_duration * .72, 3),
            physics_phase_seconds=round(module_duration * .18, 3),
            outcome=outcome,
            camera_beats=self._patterned_beats(
                module_duration, directive.animal_id, directive.camera_patterns, rng,
            ),
            events=sorted(events, key=lambda e: e.at_seconds),
            seed=self.seed * 10000 + index,
            metadata={
                "vertical": "animal_long_slide",
                "procedural_animation": True,
                "dialogue_required": False,
                **directive.metadata,
            },
        )

    def plan(
        self,
        *,
        project_id: str,
        episode_id: str,
        title: str,
        target_duration_seconds: float = 660,
        animals: list[str] | None = None,
        module_count: int | None = None,
        module_plan: list[ModuleDirective] | None = None,
    ) -> LongSlideEpisodeSpec:
        rng = random.Random(self.seed)
        directed = module_plan is not None
        if directed and not module_plan:
            raise ValueError("module_plan must contain at least one directive")
        if directed and (animals is not None or module_count is not None):
            raise ValueError("animals and module_count cannot be combined with module_plan")
        if directed:
            animal_pool = list(dict.fromkeys(d.animal_id for d in module_plan))
        else:
            animal_pool = list(dict.fromkeys(animals or DEFAULT_ANIMALS))
        if len(animal_pool) < 2:
            raise ValueError("Long Slide planning requires at least two animals")

        nominal = 43.0
        if directed:
            count = len(module_plan)
        elif module_count is not None:
            count = max(1, int(module_count))
        else:
            count = max(2, math.ceil(target_duration_seconds / nominal))
        module_duration = float(target_duration_seconds) / count
        if not 5.0 < module_duration <= 90.0:
            raise ValueError(
                "Long Slide module duration must be >5s and <=90s; "
                f"got {module_duration:.3f}s for count={count}"
            )
        modules: list[LongSlideModuleSpec] = []
        last_animal: str | None = None

        if directed:
            modules = [
                self._directed_module(index, directive, module_duration, rng)
                for index, directive in enumerate(module_plan)
            ]

        for index in range(0 if directed else count):
            candidates = [a for a in animal_pool if a != last_animal]
            animal = rng.choice(candidates)
            last_animal = animal
            scene = SCENE_ROTATION[(index + self.seed) % len(SCENE_ROTATION)]
            obstacle_count = 1 if scene in {
                LongSlideSceneKind.PAINT_GATE,
                LongSlideSceneKind.FOUNTAIN,
                LongSlideSceneKind.KEY_DOOR,
            } else 2
            compatible = sorted(SCENE_OBSTACLE_COMPATIBILITY[scene])
            chosen = rng.sample(
                compatible,
                k=min(obstacle_count, len(compatible)),
            )
            outcome = OUTCOMES[(index + self.seed) % len(OUTCOMES)]
            controlled = module_duration * .72
            physics = module_duration * .18
            modules.append(
                LongSlideModuleSpec(
                    module_id=f"LSM_{index + 1:03d}",
                    scene_kind=scene,
                    animal_id=animal,
                    duration_seconds=round(module_duration, 3),
                    animation_sequence=[
                        "idle", "run", "slide", "impact",
                        "recover", "celebrate" if outcome is OutcomeKind.SUCCESS else "reaction",
                    ],
                    obstacles=[
                        ObstaclePlacement(
                            obstacle_id=oid,
                            slot=f"obstacle_{slot + 1}",
                            seed=self.seed * 1000 + index * 10 + slot,
                        )
                        for slot, oid in enumerate(chosen)
                    ],
                    controlled_phase_seconds=round(controlled, 3),
                    physics_phase_seconds=round(physics, 3),
                    outcome=outcome,
                    camera_beats=self._camera_beats(module_duration, animal),
                    events=self._events(module_duration, scene, outcome),
                    seed=self.seed * 10000 + index,
                    metadata={
                        "vertical": "animal_long_slide",
                        "procedural_animation": True,
                        "dialogue_required": False,
                    },
                )
            )

        return LongSlideEpisodeSpec(
            project_id=project_id,
            episode_id=episode_id,
            title=title,
            target_duration_seconds=float(target_duration_seconds),
            modules=modules,
            originality_signature=LongSlideEpisodeSpec.signature_for(modules),
            metadata={
                "vertical": "animal_long_slide",
                "planner_seed": self.seed,
                "requires_actual_gameplay": False,
                "dialogue_required": False,
            },
        )
