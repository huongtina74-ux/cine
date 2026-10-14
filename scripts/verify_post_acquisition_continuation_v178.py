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
    ContinuationShotState,
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


def _request(project_id: str, episode_id: str) -> MethodSwitchRequest:
    return MethodSwitchRequest(
        project_id=project_id,
        episode_id=episode_id,
        shot_id="S01",
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


def main() -> None:
    verification_root = (
        ROOT
        / "data"
        / "verification"
        / "v178_post_acquisition_continuation"
    )
    verification_root.mkdir(parents=True, exist_ok=True)

    db = verification_root / "turbo_v178_continuation.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)
    ctx.production_continuation = ProductionContinuationManager(
        ROOT,
        ctx.turbo_store,
        store=ProductionContinuationStore(
            verification_root / "continuation"
        ),
    )
    ctx.capability_acquisition = CapabilityAcquisitionWorker(
        ctx,
        store=CapabilityAcquisitionStore(
            verification_root / "acquisition"
        ),
        research_defer_seconds=30,
        qualification_defer_seconds=30,
    )
    ctx.studio.professional_company.production_continuation = (
        ctx.production_continuation
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
    base = ns["_episode"]()
    episode = base.model_copy(
        deep=True,
        update={
            "project_id": "VERIFY_CONTINUATION_V178",
            "episode_id": "VERIFY_CONTINUATION_V178",
        },
    )
    output_dir = verification_root / "episode"
    compiled = EpisodeAssembler.from_root(ROOT).compile(
        episode,
        output_dir=output_dir,
    )
    shot = compiled.shots[0]

    # Build the acquisition while the canonical Blender capability is
    # deliberately unavailable.
    blender_offer = next(
        item
        for item in ctx.studio.capabilities.list()
        if item.capability_id == "blender.local"
    )
    ctx.studio.capabilities.register(
        blender_offer.model_copy(
            update={"executable": False}
        )
    )

    request = _request(
        compiled.project_id,
        compiled.episode_id,
    )
    blocked = ctx.method_switch.deliberate(request)
    assert blocked.executable is False

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    continuation_id = (
        f"{compiled.project_id}:{compiled.episode_id}"
    )
    recovery_path = (
        output_dir
        / "S01.capability_recovered.mp4"
    )
    acquisition = (
        ctx.method_switch.build_acquisition_work_item(
            blocked,
            resume_context={
                "shot": shot.model_dump(mode="json"),
                "output_path": str(recovery_path),
                "render_preview": True,
                "switch_round": 1,
                "switch_of_work_id": (
                    "SIMULATED_FAILED_EEVEE"
                ),
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
                shot.shot_id: acquisition.work_id
            },
        )
    )
    assert continuation.post_enqueued is False
    assert continuation.shots[0].state is (
        ContinuationShotState.WAITING_CAPABILITY
    )

    ctx.turbo_store.enqueue_work(acquisition)

    # The environment changes before R&D processes the durable work.
    ctx.studio.capabilities.register(blender_offer)

    agent = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v178-continuation-agent",
            resources={ResourceClass.AGENT},
            capabilities={"rnd.capability.acquire"},
        ),
        poll_seconds=0.01,
    )
    assert agent.tick() is True
    acquisition_after = ctx.turbo_store.get_work(
        acquisition.work_id
    )
    assert acquisition_after.state is WorkState.SUCCESS
    requeued_id = acquisition_after.result[
        "requeued_work_id"
    ]
    assert requeued_id

    requeued = ctx.turbo_store.get_work(requeued_id)
    assert requeued.state is WorkState.QUEUED
    assert requeued.kind == "block.render.method_switch"
    assert requeued.payload["continuation"] == {
        "continuation_id": continuation_id,
        "shot_id": "S01",
    }

    after_requeue = ctx.production_continuation.store.get(
        continuation_id
    )
    assert after_requeue.shots[0].state is (
        ContinuationShotState.REQUEUED
    )
    assert after_requeue.post_enqueued is False

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

    rendered = ctx.turbo_store.get_work(requeued_id)
    assert rendered.state is WorkState.SUCCESS
    assert recovery_path.is_file()
    assert recovery_path.stat().st_size > 0

    post_record = ctx.production_continuation.store.get(
        continuation_id
    )
    assert post_record.shots[0].state is (
        ContinuationShotState.ACCEPTED
    )
    assert post_record.post_enqueued is True
    assert len(post_record.timeline_work_ids) == 1
    assert post_record.assembly_work_id is not None

    timeline_id = post_record.timeline_work_ids[0]
    assembly_id = post_record.assembly_work_id
    timeline_before = ctx.turbo_store.get_work(timeline_id)
    assembly_before = ctx.turbo_store.get_work(assembly_id)
    assert timeline_before.state is WorkState.QUEUED
    assert timeline_before.dependencies == [requeued_id]
    assert assembly_before.state is WorkState.QUEUED
    assert assembly_before.dependencies == [timeline_id]

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
        assert ctx.turbo_store.get_work(
            timeline_id
        ).state is WorkState.SUCCESS
        assert io.tick() is True
    finally:
        io.close()
        agent.close()

    assembly = ctx.turbo_store.get_work(assembly_id)
    assert assembly.state is WorkState.SUCCESS
    final_episode = Path(
        assembly.result["path"]
    )
    assert final_episode.is_file()
    assert final_episode.stat().st_size > 0

    # Re-running continuation acceptance must not duplicate deterministic
    # post-production work.
    before_count = len(ctx.turbo_store.list_work(limit=1000))
    repeat = (
        ctx.production_continuation.accept_requeued_render(
            continuation_id=continuation_id,
            shot_id="S01",
            render_work_id=requeued_id,
            path=str(recovery_path),
            method_id="blender.cycles.quality",
        )
    )
    after_count = len(ctx.turbo_store.list_work(limit=1000))
    assert repeat.post_enqueued is True
    assert before_count == after_count

    payload = {
        "passed": True,
        "continuation_id": continuation_id,
        "acquisition": {
            "work_id": acquisition.work_id,
            "state": acquisition_after.state.value,
            "requeued_work_id": requeued_id,
        },
        "render": {
            "state": rendered.state.value,
            "method_id": requeued.payload["method_id"],
            "engine": (
                requeued.payload["job"]["shot"][
                    "render_engine"
                ]
            ),
            "path": str(recovery_path),
            "bytes": recovery_path.stat().st_size,
        },
        "continuation": {
            "shot_state": (
                post_record.shots[0].state.value
            ),
            "post_enqueued": post_record.post_enqueued,
            "timeline_work_ids": (
                post_record.timeline_work_ids
            ),
            "assembly_work_id": assembly_id,
            "idempotent_work_count": before_count,
        },
        "timeline": {
            "work_id": timeline_id,
            "state": (
                ctx.turbo_store.get_work(
                    timeline_id
                ).state.value
            ),
            "dependencies": timeline_before.dependencies,
        },
        "assembly": {
            "work_id": assembly_id,
            "state": assembly.state.value,
            "dependencies": assembly_before.dependencies,
            "path": str(final_episode),
            "bytes": final_episode.stat().st_size,
        },
    }
    out = verification_root / (
        "post_acquisition_continuation_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
