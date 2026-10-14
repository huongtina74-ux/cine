from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.studio.block_adapter import (
    BlockProductionStyle,
    CompanyToBlockAdapter,
)
from cinefactory.studio.block_production import BlockAnimationProducer
from cinefactory.studio.craft_execution import (
    CreativeIntentGraph,
    LightingColorIntentPlan,
    PerformanceDirectionPlan,
    SceneCreativeIntent,
)


def main() -> None:
    ns = runpy.run_path(
        str(ROOT / "tests" / "test_render_intent_binding_v171.py")
    )
    shot, performance, graph, lighting = (
        ns["_professional_block_inputs"]()
    )

    first = shot.model_copy(
        deep=True,
        update={
            "shot_id": "S02_SH01",
            "previous_shot_id": None,
            "next_shot_id": "S02_SH02",
        },
    )
    second = shot.model_copy(
        deep=True,
        update={
            "shot_id": "S02_SH02",
            "previous_shot_id": "S02_SH01",
            "next_shot_id": None,
        },
    )

    base_intent = graph.shots[0]
    intents = [
        base_intent.model_copy(update={"shot_id": first.shot_id}),
        base_intent.model_copy(update={"shot_id": second.shot_id}),
    ]
    intent_graph = CreativeIntentGraph(
        project_id="VERIFY_CONTINUITY_V172",
        scenes=[
            SceneCreativeIntent(
                scene_id=first.scene_id,
                purpose=graph.scenes[0].purpose,
                audience_know=graph.scenes[0].audience_know,
                audience_feel=graph.scenes[0].audience_feel,
                beat_ids=list(graph.scenes[0].beat_ids),
                shot_ids=[first.shot_id, second.shot_id],
            )
        ],
        shots=intents,
    )

    beats = []
    for shot_id in (first.shot_id, second.shot_id):
        for beat in performance.beats:
            beats.append(beat.model_copy(update={"shot_id": shot_id}))
    performance_plan = PerformanceDirectionPlan(
        project_id="VERIFY_CONTINUITY_V172",
        beats=beats,
    )

    light_source = lighting.shots[0]
    lighting_plan = LightingColorIntentPlan(
        project_id="VERIFY_CONTINUITY_V172",
        shots=[
            light_source.model_copy(update={"shot_id": first.shot_id}),
            light_source.model_copy(update={"shot_id": second.shot_id}),
        ],
        global_rules=list(lighting.global_rules),
    )

    episode = CompanyToBlockAdapter().adapt_episode(
        project_id="VERIFY_CONTINUITY_V172",
        episode_id="VERIFY_CONTINUITY_V172",
        title="Adjacent render continuity verification",
        shots=[first, second],
        style=BlockProductionStyle.MINECRAFT,
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        creative_intent_graph=intent_graph,
        performance_direction=performance_plan,
        lighting_color_intent=lighting_plan,
    )
    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    project_root = ROOT / "data" / "verification" / "v172_continuity"
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
    )
    try:
        report = producer.produce(
            episode,
            project_root=project_root,
            render_preview=True,
        )
    finally:
        producer.close()

    shots = []
    for item in report.shots:
        take = item.takes[0]
        shots.append(
            {
                "shot_id": item.shot_id,
                "passed": item.passed,
                "selected_score": item.selected_score,
                "identity_score": take.identity_score,
                "performance_score": take.performance_score,
                "camera_score": take.camera_score,
                "continuity_score": take.continuity_score,
                "score_semantics": take.score_semantics,
                "rendered_identity_comparisons": take.evidence.get(
                    "rendered_identity_comparisons"
                ),
                "rendered_cut_appearance": take.evidence.get(
                    "rendered_cut_appearance"
                ),
                "rendered_frame_qc": take.evidence.get(
                    "rendered_frame_qc"
                ),
                "render_continuity": take.evidence.get(
                    "render_continuity"
                ),
                "performance_qc": take.evidence.get(
                    "performance_qc"
                ),
                "repair_directives": [
                    directive.model_dump(mode="json")
                    for directive in item.repair_directives
                ],
            }
        )

    payload = {
        "passed": report.passed,
        "findings": report.findings,
        "shots": shots,
    }
    out = project_root / "continuity_verification.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
