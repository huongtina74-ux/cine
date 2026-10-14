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
from cinefactory.studio.capability_acquisition import (
    CapabilityAcquisitionStore,
    CapabilityAcquisitionWorker,
)
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
    verification_root = (
        ROOT
        / "data"
        / "verification"
        / "v178_production_continuation"
    )
    verification_root.mkdir(parents=True, exist_ok=True)

    turbo_db = verification_root / "turbo_v178.db"
    if turbo_db.exists():
        turbo_db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(turbo_db)
    ctx.production_continuation = ProductionContinuationManager(
        ROOT,
        ctx.turbo_store,
        store=ProductionContinuationStore(
            verification_root / "continuations"
        ),
    )
    ctx.studio.professional_company.production_continuation = (
        ctx.production_continuation
    )
    ctx.capability_acquisition = CapabilityAcquisitionWorker(
        ctx,
        store=CapabilityAcquisitionStore(
            verification_root / "acquisition"
        ),
        research_defer_seconds=30,
        qualification_defer_seconds=30,
    )
    ctx.studio.professional_company.capability_acquisition = (
        ctx.capability_acquisition
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
            "project_id": "VERIFY_CONTINUATION_V178",
            "episode_id": "VERIFY_CONTINUATION_V178",
        },
    )
    output_dir = verification_root / "renders"
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=output_dir,
    )
    shot = compiled.shots[0]

    original_offer = next(
        item
        for item in ctx.studio.capabilities.list()
        if item.capability_id == "blender.local"
    )
    ctx.studio.capabilities.register(
        original_offer.model_copy(
            update={"executable": False}
        )
    )

    request = MethodSwitchRequest(
        project_id=compiled.project_id,
        episode_id=compiled.episode_id,
        shot_id=shot.shot_id,
        current_tool_id="blender",
        current_method_id="blender.eevee.current",
        policy=MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE,
        min_quality=0.92,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=90.0,
        mean_current_attempt_seconds=4.0,
        continuity_priority=True,
        backend_switch_allowed=False,
        recurring_identity_required=True,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
    )
    blocked = ctx.method_switch.deliberate(request)
    assert blocked.executable is False

    continuation_id = (
        ctx.production_continuation.continuation_id(
            compiled.project_id,
            compiled.episode_id,
        )
    )
    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    recovered_path = (
        output_dir
        / "S01.recovered.cycles.mp4"
    )
    acquisition = (
        ctx.method_switch.build_acquisition_work_item(
            blocked,
            resume_context={
                "shot": shot.model_dump(mode="json"),
                "output_path": str(recovered_path),
                "render_preview": True,
                "switch_round": 1,
                "switch_of_work_id": "FAILED_EEVEE_BASELINE",
                "blender_executable": str(blender),
                "continuation_id": continuation_id,
                "continuation_shot_id": shot.shot_id,
            },
        )
    )

    continuation = (
        ctx.production_continuation.create_blocked_episode(
            compiled=compiled,
            output_dir=output_dir,
            accepted_rows=[],
            acquisition_by_shot={
                shot.shot_id: acquisition.work_id,
            },
        )
    )
    assert continuation.post_enqueued is False
    assert continuation.all_accepted is False

    ctx.turbo_store.enqueue_work(acquisition)

    # Capability becomes production-executable after acquisition creation.
    ctx.studio.capabilities.register(original_offer)

    agent = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v178-continuation-agent",
            resources={ResourceClass.AGENT},
            capabilities={"rnd.capability.acquire"},
        ),
        poll_seconds=0.01,
    )
    try:
        assert agent.tick() is True
    finally:
        agent.close()

    acquisition_done = ctx.turbo_store.get_work(
        acquisition.work_id
    )
    assert acquisition_done.state is WorkState.SUCCESS
    requeued_id = acquisition_done.result[
        "requeued_work_id"
    ]
    assert requeued_id

    after_requeue = (
        ctx.production_continuation.store.get(
            continuation_id
        )
    )
    resumed_shot = after_requeue.shots[0]
    assert resumed_shot.state.value == "REQUEUED"
    assert resumed_shot.render_work_id == requeued_id

    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v178-continuation-gpu",
            resources={ResourceClass.GPU},
            capabilities={"blender.animation.render"},
            active_model_affinity="BLENDER:CYCLES",
        ),
        poll_seconds=0.01,
    )
    try:
        assert gpu.tick() is True
    finally:
        gpu.close()

    render_done = ctx.turbo_store.get_work(requeued_id)
    assert render_done.state is WorkState.SUCCESS
    assert recovered_path.is_file()
    assert recovered_path.stat().st_size > 0

    resumed = (
        ctx.production_continuation.store.get(
            continuation_id
        )
    )
    assert resumed.all_accepted is True
    assert resumed.post_enqueued is True
    assert len(resumed.timeline_work_ids) == 1
    assert resumed.assembly_work_id is not None

    io = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v178-continuation-io",
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
    timeline = ctx.turbo_store.get_work(timeline_id)
    assembly = ctx.turbo_store.get_work(
        resumed.assembly_work_id
    )
    assert timeline.state is WorkState.SUCCESS
    assert assembly.state is WorkState.SUCCESS
    assert timeline.dependencies == [requeued_id]
    assert assembly.dependencies == [timeline_id]

    final_episode = Path(resumed.output_path)
    assert final_episode.is_file()
    assert final_episode.stat().st_size > 0

    payload = {
        "continuation_id": continuation_id,
        "acquisition_work": {
            "work_id": acquisition.work_id,
            "state": acquisition_done.state.value,
            "requeued_work_id": requeued_id,
        },
        "recovered_render": {
            "work_id": requeued_id,
            "state": render_done.state.value,
            "method_id": render_done.payload.get(
                "method_id"
            ),
            "path": str(recovered_path),
            "bytes": recovered_path.stat().st_size,
        },
        "post_production": {
            "timeline_work_id": timeline_id,
            "timeline_state": timeline.state.value,
            "timeline_dependencies": timeline.dependencies,
            "assembly_work_id": assembly.work_id,
            "assembly_state": assembly.state.value,
            "assembly_dependencies": assembly.dependencies,
            "final_episode": str(final_episode),
            "final_episode_bytes": (
                final_episode.stat().st_size
            ),
        },
        "continuation_record": resumed.model_dump(
            mode="json"
        ),
    }
    out = verification_root / (
        "production_continuation_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
