from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.studio.capability_acquisition import (
    CapabilityAcquisitionStore,
    CapabilityAcquisitionWorker,
    CapabilityAcquisitionState,
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


def _verification_shot(ctx, output_dir: Path):
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
            "project_id": "VERIFY_RND_V177_REQUEUE",
            "episode_id": "VERIFY_RND_V177_REQUEUE",
        },
    )
    compiled = (
        __import__(
            "cinefactory.block_animation.assembler",
            fromlist=["EpisodeAssembler"],
        )
        .EpisodeAssembler.from_root(ROOT)
        .compile(episode, output_dir=output_dir)
    )
    return episode, compiled.shots[0]


def _request(
    project_id: str,
    episode_id: str,
    *,
    current_method_id: str,
) -> MethodSwitchRequest:
    return MethodSwitchRequest(
        project_id=project_id,
        episode_id=episode_id,
        shot_id="S01",
        current_tool_id="blender",
        current_method_id=current_method_id,
        policy=(
            MethodSwitchPolicy
            .QUALITY_FIRST_ALTERNATIVE
        ),
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
        / "v177_capability_acquisition"
    )
    verification_root.mkdir(
        parents=True,
        exist_ok=True,
    )
    db = verification_root / "turbo_v177.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)
    ctx.capability_acquisition = (
        CapabilityAcquisitionWorker(
            ctx,
            store=CapabilityAcquisitionStore(
                verification_root / "acquisition"
            ),
            research_defer_seconds=30,
            qualification_defer_seconds=30,
        )
    )
    ctx.studio.professional_company.capability_acquisition = (
        ctx.capability_acquisition
    )

    # ------------------------------------------------------------
    # Case A: no alternative method can pass -> durable AGENT defer
    # ------------------------------------------------------------
    blocked_request = _request(
        "VERIFY_RND_V177_RESEARCH",
        "VERIFY_RND_V177_RESEARCH",
        current_method_id="blender.cycles.quality",
    )
    blocked_decision = ctx.method_switch.deliberate(
        blocked_request
    )
    assert blocked_decision.executable is False
    research_work = (
        ctx.method_switch.build_acquisition_work_item(
            blocked_decision
        )
    )
    ctx.turbo_store.enqueue_work(research_work)

    agent = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="verify-rnd-agent-v177",
            resources={ResourceClass.AGENT},
            capabilities={"rnd.capability.acquire"},
        ),
        poll_seconds=0.01,
    )
    assert agent.tick() is True
    research_after = ctx.turbo_store.get_work(
        research_work.work_id
    )
    assert research_after.state is WorkState.RETRY
    assert research_after.attempts == 0
    assert (
        research_after.last_error
        == "AWAITING_AGENT_RESEARCH_RESPONSE"
    )

    research_case = (
        ctx.capability_acquisition.store.get(
            "VERIFY_RND_V177_RESEARCH__S01"
        )
    )
    assert research_case.state is (
        CapabilityAcquisitionState.AWAITING_RESEARCH
    )
    reasoning_request = Path(
        research_case.reasoning_request_path
    )
    reasoning_response = Path(
        research_case.reasoning_response_path
    )
    assert reasoning_request.is_file()
    assert not reasoning_response.exists()

    # ------------------------------------------------------------
    # Case B: acquisition was created while Blender capability was
    # unavailable. It becomes executable before the R&D worker runs.
    # The worker must re-evaluate and requeue the canonical shot.
    # ------------------------------------------------------------
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

    resume_request = _request(
        "VERIFY_RND_V177_REQUEUE",
        "VERIFY_RND_V177_REQUEUE",
        current_method_id="blender.eevee.current",
    )
    resume_blocked = ctx.method_switch.deliberate(
        resume_request
    )
    assert resume_blocked.executable is False

    output_dir = (
        verification_root
        / "requeue_render"
    )
    _, shot = _verification_shot(
        ctx,
        output_dir,
    )
    blender_executable = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    acquisition = (
        ctx.method_switch.build_acquisition_work_item(
            resume_blocked,
            resume_context={
                "shot": shot.model_dump(mode="json"),
                "output_path": str(
                    output_dir
                    / "S01.capability_resume01.mp4"
                ),
                "render_preview": True,
                "switch_round": 1,
                "switch_of_work_id": (
                    "SIMULATED_FAILED_EEVEE_WORK"
                ),
                "blender_executable": str(
                    blender_executable
                ),
            },
        )
    )

    # The environment/capability becomes ready before R&D claims it.
    ctx.studio.capabilities.register(blender_offer)
    ctx.turbo_store.enqueue_work(acquisition)

    # not_before from the unrelated Case A cannot affect this work.
    assert agent.tick() is True
    acquisition_after = ctx.turbo_store.get_work(
        acquisition.work_id
    )
    assert acquisition_after.state is WorkState.SUCCESS
    result = acquisition_after.result
    assert result["state"] == "REQUEUED"
    requeued_id = result["requeued_work_id"]
    assert requeued_id

    requeued = ctx.turbo_store.get_work(requeued_id)
    assert requeued.kind == "block.render.method_switch"
    assert requeued.state is WorkState.QUEUED
    assert requeued.payload["method_id"] == (
        "blender.cycles.quality"
    )
    assert requeued.payload["method_switch_of_work_id"] == (
        "SIMULATED_FAILED_EEVEE_WORK"
    )

    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="verify-rnd-gpu-v177",
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
        agent.close()

    rendered = ctx.turbo_store.get_work(requeued_id)
    assert rendered.state is WorkState.SUCCESS
    rendered_path = Path(
        rendered.payload["job"]["output_path"]
    )
    assert rendered_path.is_file()
    assert rendered_path.stat().st_size > 0

    requeue_case = ctx.capability_acquisition.store.get(
        "VERIFY_RND_V177_REQUEUE__S01"
    )
    assert requeue_case.state is (
        CapabilityAcquisitionState.REQUEUED
    )
    assert requeue_case.requeued_work_id == requeued_id

    request_payload = json.loads(
        reasoning_request.read_text(encoding="utf-8")
    )
    payload = {
        "research_case": {
            "work_id": research_work.work_id,
            "work_state": research_after.state.value,
            "attempts": research_after.attempts,
            "last_error": research_after.last_error,
            "case_state": research_case.state.value,
            "reasoning_request": str(reasoning_request),
            "reasoning_response_expected": str(
                reasoning_response
            ),
            "research_stage": request_payload["stage"],
            "metered_generation_api": (
                request_payload["context"]["constraints"][
                    "metered_generation_api"
                ]
            ),
            "research_sources": (
                request_payload["context"][
                    "research_sources"
                ]
            ),
        },
        "requeue_case": {
            "acquisition_work_id": acquisition.work_id,
            "acquisition_state": (
                acquisition_after.state.value
            ),
            "case_state": requeue_case.state.value,
            "requeued_work_id": requeued_id,
            "requeued_state": rendered.state.value,
            "method_id": rendered.payload["method_id"],
            "render_engine": (
                rendered.payload["job"]["shot"][
                    "render_engine"
                ]
            ),
            "rendered_path": str(rendered_path),
            "rendered_bytes": rendered_path.stat().st_size,
        },
        "workers": ctx.turbo_store.list_workers(),
    }
    out = verification_root / (
        "capability_acquisition_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
