from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.contracts import (
    ActorPlacement,
    CameraIntent,
    EpisodeSpec,
    ShotPerformanceSpec,
)
from cinefactory.studio.block_production import (
    BlockAnimationProducer,
)
from cinefactory.turbo.contracts import WorkState
from cinefactory.turbo.store import TurboStore


def _episode(
    *,
    project_id: str,
    creative_intent: dict,
) -> EpisodeSpec:
    return EpisodeSpec(
        project_id=project_id,
        episode_id=project_id,
        title=project_id,
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        metadata={
            "proactive_hybrid_routing": True,
            "proactive_hybrid_routing_strict": True,
            "max_vram_gb": 12.0,
        },
        shots=[
            ShotPerformanceSpec(
                shot_id="S01",
                scene_template_id="minecraft_classroom",
                duration_seconds=1.0,
                actors=[
                    ActorPlacement(
                        actor_id="A",
                        rig_id="mc_a",
                        marker="hero_a",
                    )
                ],
                camera=CameraIntent(
                    purpose="fidelity_medium",
                    pattern_id="fidelity_medium",
                    targets=["A"],
                ),
                creative_intent=creative_intent,
                narrative_purpose=(
                    "hybrid routing verification"
                ),
            )
        ],
    )


def _project_work(ctx, project_id: str):
    return [
        item
        for item in ctx.turbo_store.list_work(
            limit=5000
        )
        if item.project_id == project_id
    ]


def _assembly_output(ctx, project_id: str) -> Path:
    rows = [
        item
        for item in _project_work(ctx, project_id)
        if item.kind == "block.episode.assemble"
    ]
    assert len(rows) == 1
    row = rows[0]
    assert row.state is WorkState.SUCCESS
    path = Path(
        str(
            row.result.get("path")
            or row.payload.get("output_path")
        )
    )
    assert path.is_file()
    return path


def main() -> None:
    out = (
        ROOT
        / "data"
        / "verification"
        / "v183_hybrid_shot_router"
    )
    out.mkdir(parents=True, exist_ok=True)
    db = out / "turbo_v183.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )

    # ------------------------------------------------------------
    # A. Precise-camera authority: proactive route must stay in
    # controlled 3D and upgrade Eevee -> Cycles before first render.
    # ------------------------------------------------------------
    controlled_id = "V183_CONTROLLED_CAMERA"
    controlled = _episode(
        project_id=controlled_id,
        creative_intent={
            "precise_camera_required": True,
            "story_beat": (
                "camera geometry must remain controlled"
            ),
        },
    )
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
        ctx=ctx,
        max_repair_rounds=0,
    )
    try:
        controlled_dailies = producer.produce_turbo(
            controlled,
            project_root=out / "controlled",
            render_preview=True,
        )
    finally:
        producer.close()

    assert controlled_dailies.passed is True
    assert (
        controlled_dailies.execution_metrics[
            "shot_routing"
        ]["S01"]["selected_method_id"]
        == "blender.cycles.quality"
    )
    controlled_report = controlled_dailies.shots[0]
    assert controlled_report.passed is True
    assert controlled_report.selected_path
    controlled_media = Path(
        controlled_report.selected_path
    )
    assert controlled_media.is_file()
    assert controlled_media.with_suffix(
        controlled_media.suffix + ".frame_qc.json"
    ).is_file()

    controlled_work = [
        item
        for item in _project_work(
            ctx,
            controlled_id,
        )
        if item.handler
        in {
            "blender.animation.render",
            "block.video.comfy",
        }
    ]
    proactive_controlled = [
        item
        for item in controlled_work
        if (
            item.payload.get("proactive_route")
            or {}
        ).get("proactive")
    ]
    assert len(proactive_controlled) == 1
    controlled_initial = proactive_controlled[0]
    controlled_route = dict(
        controlled_initial.payload[
            "proactive_route"
        ]
    )
    assert (
        controlled_route["selected_method_id"]
        == "blender.cycles.quality"
    )
    assert controlled_initial.handler == (
        "blender.animation.render"
    )
    assert controlled_initial.payload[
        "job"
    ]["shot"]["render_engine"] == "CYCLES"
    controlled_final = _assembly_output(
        ctx,
        controlled_id,
    )

    # Capture the same canonical actor into CharacterFactory so the
    # second episode can use both explicit media and actor-specific QC.
    pack = ctx.character_factory.capture_reference_from_render(
        source_media=controlled_media,
        actor_id="A",
        rig_id="mc_a",
    )
    assert pack.global_character_id == "CHAR_MC_A"

    # ------------------------------------------------------------
    # B. Generative authority: explicit reference-conditioned shot
    # must route to production-qualified Wan before first render.
    # ------------------------------------------------------------
    generative_id = "V183_GENERATIVE_WAN"
    generative = _episode(
        project_id=generative_id,
        creative_intent={
            "generative_video_preferred": True,
            "reference_frame_path": str(
                controlled_media
            ),
            "recurring_identity_required": True,
            "story_beat": (
                "preserve character identity while "
                "using generative motion"
            ),
        },
    )
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
        ctx=ctx,
        max_repair_rounds=0,
    )
    try:
        generative_dailies = producer.produce_turbo(
            generative,
            project_root=out / "generative",
            render_preview=True,
        )
    finally:
        producer.close()

    assert generative_dailies.passed is True
    assert (
        generative_dailies.execution_metrics[
            "shot_routing"
        ]["S01"]["selected_method_id"]
        == "comfyui.wan21.fun.inpaint.1.3b"
    )
    generative_report = generative_dailies.shots[0]
    assert generative_report.passed is True
    assert generative_report.selected_path
    generative_media = Path(
        generative_report.selected_path
    )
    assert generative_media.is_file()

    generative_work = [
        item
        for item in _project_work(
            ctx,
            generative_id,
        )
        if item.handler
        in {
            "blender.animation.render",
            "block.video.comfy",
        }
    ]
    proactive_generative = [
        item
        for item in generative_work
        if (
            item.payload.get("proactive_route")
            or {}
        ).get("proactive")
    ]
    assert len(proactive_generative) == 1
    generative_initial = proactive_generative[0]
    generative_route = dict(
        generative_initial.payload[
            "proactive_route"
        ]
    )
    assert generative_route[
        "selected_method_id"
    ] == "comfyui.wan21.fun.inpaint.1.3b"
    assert generative_initial.handler == (
        "block.video.comfy"
    )
    assert generative_initial.state is (
        WorkState.SUCCESS
    )
    assert (
        generative_initial.result["qc_passed"]
        is True
    )
    identity = dict(
        generative_initial.result[
            "identity_qc"
        ]
    )
    assert identity["measured"] is True
    assert identity["passed"] is True
    assert float(identity["score"]) >= 0.70
    character_identity = dict(
        generative_initial.result.get(
            "character_identity_qc"
        )
        or {}
    )
    assert character_identity.get(
        "passed"
    ) is True
    generative_final = _assembly_output(
        ctx,
        generative_id,
    )

    # ------------------------------------------------------------
    # C. Direct policy checks remain scoped.
    # ------------------------------------------------------------
    compiled = producer.assembler.compile(
        generative,
        output_dir=out / "policy_check",
    )
    shot = compiled.shots[0].model_copy(
        deep=True
    )
    shot.creative_intent[
        "precise_camera_required"
    ] = True
    shot.creative_intent[
        "generative_video_preferred"
    ] = True
    conflict = ctx.shot_router.route(
        project_id="V183_CONFLICT",
        episode_id="V183_CONFLICT",
        shot=shot,
        episode_metadata={
            "proactive_hybrid_routing": True,
            "proactive_hybrid_routing_strict": True,
        },
    )
    assert conflict.selected_method_id == (
        "blender.cycles.quality"
    )
    assert conflict.mode.value == (
        "CONTROLLED_BLENDER"
    )

    payload = {
        "controlled_camera": {
            "route": controlled_route,
            "work_id": controlled_initial.work_id,
            "handler": controlled_initial.handler,
            "state": controlled_initial.state.value,
            "render_engine": (
                controlled_initial.payload[
                    "job"
                ]["shot"]["render_engine"]
            ),
            "selected_media": str(
                controlled_media
            ),
            "selected_media_bytes": (
                controlled_media.stat().st_size
            ),
            "final_episode": str(
                controlled_final
            ),
            "final_episode_bytes": (
                controlled_final.stat().st_size
            ),
        },
        "generative": {
            "route": generative_route,
            "work_id": generative_initial.work_id,
            "handler": generative_initial.handler,
            "state": generative_initial.state.value,
            "qc_passed": (
                generative_initial.result[
                    "qc_passed"
                ]
            ),
            "identity_qc": identity,
            "character_identity_qc": (
                character_identity
            ),
            "selected_media": str(
                generative_media
            ),
            "selected_media_bytes": (
                generative_media.stat().st_size
            ),
            "final_episode": str(
                generative_final
            ),
            "final_episode_bytes": (
                generative_final.stat().st_size
            ),
        },
        "conflict_authority": (
            conflict.model_dump(mode="json")
        ),
        "reference_pack": (
            pack.model_dump(mode="json")
        ),
    }
    target = (
        out
        / "hybrid_shot_router_verification.json"
    )
    target.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
