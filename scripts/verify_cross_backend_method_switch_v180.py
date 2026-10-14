from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.studio.production_continuation import (
    ProductionContinuationManager,
    ProductionContinuationStore,
)
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
)
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkerSpec,
    WorkState,
)
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore


def main() -> None:
    out = (
        ROOT
        / "data"
        / "verification"
        / "v180_cross_backend_method_switch"
    )
    out.mkdir(parents=True, exist_ok=True)
    db = out / "turbo_v180.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)
    ctx.production_continuation = (
        ProductionContinuationManager(
            ROOT,
            ctx.turbo_store,
            store=ProductionContinuationStore(
                out / "continuations"
            ),
        )
    )
    ctx.studio.professional_company.production_continuation = (
        ctx.production_continuation
    )

    ns = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "test_block_auto_repair_v173.py"
        )
    )
    episode = ns["_episode"]().model_copy(
        deep=True,
        update={
            "project_id": "V180_METHOD_SWITCH",
            "episode_id": "V180_METHOD_SWITCH",
        },
    )
    render_dir = out / "renders"
    compiled = EpisodeAssembler.from_root(
        ROOT
    ).compile(
        episode,
        output_dir=render_dir,
    )
    shot = compiled.shots[0]

    reference = (
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4"
    )
    assert reference.is_file()

    request = MethodSwitchRequest(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot_id=shot.shot_id,
        current_tool_id="blender",
        current_method_id="blender.cycles.quality",
        policy=MethodSwitchPolicy.BALANCED_ALTERNATIVE,
        min_quality=0.70,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=240.0,
        mean_current_attempt_seconds=20.0,
        continuity_priority=True,
        backend_switch_allowed=True,
        recurring_identity_required=True,
        reference_frame_path=str(reference),
        precise_camera_required=False,
        semantic_performance_required=False,
        visual_style="MINECRAFT",
        failure_codes=[
            "MODEL_CAPABILITY",
            "LOOKDEV_FAIL",
        ],
        required_tags={
            "reference_conditioning"
        },
    )
    decision = ctx.method_switch.deliberate(
        request
    )
    assert decision.executable is True
    assert decision.selected_method_id == (
        "comfyui.wan21.fun.inpaint.1.3b"
    )

    continuation = (
        ctx.production_continuation
        .create_blocked_episode(
            compiled=compiled,
            output_dir=render_dir,
            accepted_rows=[],
            acquisition_by_shot={
                shot.shot_id: (
                    "DIRECT_METHOD_SWITCH_AFTER_BLENDER_FAIL"
                )
            },
        )
    )
    continuation_payload = {
        "continuation_id": (
            continuation.continuation_id
        ),
        "shot_id": shot.shot_id,
    }

    work = ctx.method_switch.build_work_item(
        compiled=compiled,
        shot=shot,
        decision=decision,
        output_path=(
            render_dir
            / "S01.wan.method_switch.mp4"
        ),
        render_preview=True,
        switch_round=1,
        switch_of_work_id=(
            "FAILED_BLENDER_CYCLES_WORK"
        ),
        continuation=continuation_payload,
    )
    assert work.handler == "block.video.comfy"
    assert work.resource is ResourceClass.GPU
    assert (
        work.payload["normalizer_id"]
        == "blockvideo.wan21.fun.inpaint.v1"
    )

    ctx.production_continuation.mark_requeued(
        continuation_id=(
            continuation.continuation_id
        ),
        shot_id=shot.shot_id,
        render_work_id=work.work_id,
        method_id=decision.selected_method_id,
    )
    ctx.turbo_store.enqueue_work(work)

    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v180-cross-backend-gpu",
            resources={ResourceClass.GPU},
            capabilities={
                "block.video.comfy"
            },
            active_model_affinity=(
                work.model_affinity
            ),
        ),
        poll_seconds=0.05,
    )
    try:
        assert gpu.tick() is True
    finally:
        gpu.close()

    rendered = ctx.turbo_store.get_work(
        work.work_id
    )
    assert rendered.state is WorkState.SUCCESS
    assert rendered.result["qc_passed"] is True
    rendered_path = Path(
        rendered.result["path"]
    )
    assert rendered_path.is_file()
    assert rendered_path.stat().st_size > 0
    assert (
        rendered.result["identity_qc"]["score"]
        >= 0.80
    )

    resumed = (
        ctx.production_continuation.store.get(
            continuation.continuation_id
        )
    )
    assert resumed.all_accepted is True
    assert resumed.post_enqueued is True
    assert len(resumed.timeline_work_ids) == 1
    assert resumed.assembly_work_id

    io = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v180-cross-backend-io",
            resources={ResourceClass.IO},
            capabilities={
                "timeline.accept",
                "block.episode.assemble",
            },
        ),
        poll_seconds=0.01,
    )
    try:
        assert io.tick() is True
        assert io.tick() is True
    finally:
        io.close()

    timeline_id = resumed.timeline_work_ids[0]
    timeline = ctx.turbo_store.get_work(
        timeline_id
    )
    assembly = ctx.turbo_store.get_work(
        resumed.assembly_work_id
    )
    assert timeline.state is WorkState.SUCCESS
    assert assembly.state is WorkState.SUCCESS
    assert timeline.dependencies == [
        work.work_id
    ]
    assert assembly.dependencies == [
        timeline_id
    ]
    assert (
        timeline.payload["edit_intent"][
            "method_id"
        ]
        == "comfyui.wan21.fun.inpaint.1.3b"
    )

    final_episode = Path(
        resumed.output_path
    )
    assert final_episode.is_file()
    assert final_episode.stat().st_size > 0

    payload = {
        "method_switch": {
            "status": decision.status.value,
            "selected_method_id": (
                decision.selected_method_id
            ),
            "selected_handler": (
                decision.selected_handler
            ),
            "reasons": decision.reasons,
        },
        "wan_render": {
            "work_id": work.work_id,
            "state": rendered.state.value,
            "path": str(rendered_path),
            "bytes": rendered_path.stat().st_size,
            "qc_passed": (
                rendered.result["qc_passed"]
            ),
            "identity_qc": (
                rendered.result["identity_qc"]
            ),
            "normalizer_id": (
                rendered.result["normalizer_id"]
            ),
            "backend_contract": (
                rendered.result[
                    "backend_contract"
                ]
            ),
        },
        "continuation": {
            "continuation_id": (
                resumed.continuation_id
            ),
            "all_accepted": (
                resumed.all_accepted
            ),
            "post_enqueued": (
                resumed.post_enqueued
            ),
            "timeline_work_id": (
                timeline_id
            ),
            "timeline_state": (
                timeline.state.value
            ),
            "timeline_dependencies": (
                timeline.dependencies
            ),
            "assembly_work_id": (
                assembly.work_id
            ),
            "assembly_state": (
                assembly.state.value
            ),
            "assembly_dependencies": (
                assembly.dependencies
            ),
            "final_episode": str(
                final_episode
            ),
            "final_episode_bytes": (
                final_episode.stat().st_size
            ),
        },
    }
    verification = (
        out
        / "cross_backend_method_switch_verification.json"
    )
    verification.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
