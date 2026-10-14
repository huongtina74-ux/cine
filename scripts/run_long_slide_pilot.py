from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.animal_long_slide.blender_binder import LongSlideBlenderBinder
from cinefactory.animal_long_slide.contracts import (
    CameraBeat,
    LongSlideEpisodeSpec,
    LongSlideModuleSpec,
    LongSlideSceneKind,
    ObstaclePlacement,
    OutcomeKind,
    ReactionEvent,
)
from cinefactory.animal_long_slide.execution import LongSlideExecutionPlanner
from cinefactory.animal_long_slide.motion import MotionCompatibilityGraph
from cinefactory.animal_long_slide.registry import LongSlideAssetRegistry


def main():
    module = LongSlideModuleSpec(
        module_id="PILOT_COW_001",
        scene_kind=LongSlideSceneKind.LONG_SLIDE,
        animal_id="cow",
        duration_seconds=8.0,
        animation_sequence=["idle", "run", "slide", "impact", "recover", "celebrate"],
        obstacles=[
            ObstaclePlacement(
                obstacle_id="rotating_hammer",
                slot="obstacle_slot_1",
                seed=101,
            )
        ],
        controlled_phase_seconds=5.8,
        physics_phase_seconds=1.2,
        outcome=OutcomeKind.SUCCESS,
        camera_beats=[
            CameraBeat(pattern_id="hero_start", start_seconds=0.0, end_seconds=1.5, target="cow"),
            CameraBeat(pattern_id="chase", start_seconds=1.5, end_seconds=4.0, target="cow"),
            CameraBeat(pattern_id="obstacle_side", start_seconds=4.0, end_seconds=6.2, target="cow"),
            CameraBeat(pattern_id="finish_reaction", start_seconds=6.2, end_seconds=8.0, target="cow"),
        ],
        events=[
            ReactionEvent(event_id="start_go", at_seconds=0.5),
            ReactionEvent(event_id="impact", at_seconds=4.7),
            ReactionEvent(event_id="winner", at_seconds=7.2),
        ],
        seed=101,
        metadata={"vertical": "animal_long_slide", "pilot": True},
    )
    episode = LongSlideEpisodeSpec(
        project_id="STU_LONG_SLIDE_PILOT",
        episode_id="EP_COW_001",
        title="Cow Long Slide Pilot",
        target_duration_seconds=16.0,
        modules=[module],
        originality_signature=LongSlideEpisodeSpec.signature_for([module]),
        metadata={"vertical": "animal_long_slide", "pilot": True},
    )

    registry = LongSlideAssetRegistry.load(ROOT)
    motions = MotionCompatibilityGraph.load(ROOT)
    plan = LongSlideExecutionPlanner(registry, motions).plan(
        episode,
        output_dir=ROOT / "renders" / "animal_long_slide" / "pilot",
        width=640,
        height=360,
        fps=24,
        render_preview=True,
    )
    if not plan.executable:
        raise SystemExit("BLOCKED::" + ";".join(plan.blockers))

    blender = ROOT / ".tools" / "blender-4.5.14-windows-x64" / "blender.exe"
    binder = LongSlideBlenderBinder(
        ROOT,
        blender_executable=blender,
        registry=registry,
    )
    output = binder.execute(plan.jobs[0], timeout_seconds=600)
    print("PILOT_OK::" + str(output))


if __name__ == "__main__":
    main()
