from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.studio.candidate_promotion import (
    CandidatePromotionController,
    CandidatePromotionStore,
    PromotionState,
)
from cinefactory.studio.capability_acquisition import (
    CapabilityAcquisitionStore,
    CapabilityAcquisitionWorker,
    CapabilityResearchCandidate,
    CapabilityResearchResponse,
    ResearchEvidenceTier,
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
from cinefactory.workflows.registry import (
    WorkflowRegistry,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    root = (
        ROOT
        / "data"
        / "verification"
        / "v179_acquisition_auto_promotion"
    )
    root.mkdir(parents=True, exist_ok=True)
    db = root / "turbo_v179.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)

    isolated_workflows = WorkflowRegistry(
        root / "promoted_workflows"
    ).load()
    promotion = CandidatePromotionController(
        ctx,
        store=CandidatePromotionStore(
            root / "promotion"
        ),
        workflow_registry=isolated_workflows,
    )
    ctx.candidate_promotion = promotion
    ctx.studio.professional_company.candidate_promotion = (
        promotion
    )

    acquisition_context = type(
        "_V179AcquisitionContext",
        (),
        {
            "root": ROOT,
            "studio": ctx.studio,
            "workflows": ctx.workflows,
            "models": ctx.models,
            "method_switch": ctx.method_switch,
            "turbo_store": ctx.turbo_store,
            "production_continuation": (
                ctx.production_continuation
            ),
            "candidate_promotion": promotion,
        },
    )()
    acquisition = CapabilityAcquisitionWorker(
        acquisition_context,
        store=CapabilityAcquisitionStore(
            root / "acquisition"
        ),
        research_defer_seconds=5,
        qualification_defer_seconds=5,
    )
    ctx.capability_acquisition = acquisition
    ctx.studio.professional_company.capability_acquisition = (
        acquisition
    )

    request = MethodSwitchRequest(
        project_id="VERIFY_ACQ_PROMOTE_V179",
        episode_id="VERIFY_ACQ_PROMOTE_V179",
        shot_id="S01",
        current_tool_id="blender",
        current_method_id="blender.cycles.quality",
        policy=(
            MethodSwitchPolicy
            .QUALITY_FIRST_ALTERNATIVE
        ),
        min_quality=0.95,
        max_vram_gb=12.0,
        local_only=True,
        commercial_safe=True,
        max_additional_gpu_seconds=90.0,
        mean_current_attempt_seconds=5.0,
        continuity_priority=True,
        backend_switch_allowed=False,
        recurring_identity_required=True,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
    )
    blocked = ctx.method_switch.deliberate(request)
    assert blocked.executable is False
    acquisition_work = (
        ctx.method_switch
        .build_acquisition_work_item(
            blocked
        )
    )
    ctx.turbo_store.enqueue_work(
        acquisition_work
    )

    source_manifest = ctx.workflows.get(
        "comfy.mastery.sd15",
        "1",
    )
    workflow_path = (
        ROOT
        / "workflows"
        / "comfyui"
        / "mastery_sd15.json"
    )
    candidate_manifest = source_manifest.model_copy(
        update={
            "workflow_id": (
                "verify.acquisition.v179.sd15"
            ),
            "version": "1",
            "workflow_file": (
                workflow_path.name
            ),
        }
    )
    case_id = "VERIFY_ACQ_PROMOTE_V179__S01"
    response = CapabilityResearchResponse(
        case_id=case_id,
        candidates=[
            CapabilityResearchCandidate(
                candidate_id=(
                    "verify.acquisition.sd15"
                ),
                name=(
                    "Verified SD1.5 Declarative Workflow"
                ),
                tool_id="comfyui",
                source_uri=(
                    "internal://workflows/"
                    "comfy.mastery.sd15@1"
                ),
                source_type=(
                    "INTERNAL_APPROVED_WORKFLOW"
                ),
                version="1",
                capabilities=[
                    "IMAGE_GENERATION"
                ],
                license_name=(
                    "CreativeML-OpenRAIL-M"
                ),
                license_evidence_uri=(
                    "internal://model_registry/"
                    "stable-diffusion-v1-5-emaonly"
                ),
                license_evidence_tier=(
                    ResearchEvidenceTier.OFFICIAL
                ),
                commercial_use_allowed=True,
                estimated_vram_gb=4.0,
                local_supported=True,
                automation_interfaces=[
                    "ComfyUI API workflow JSON"
                ],
                local_artifact_path=str(
                    workflow_path
                ),
                local_artifact_sha256=sha256(
                    workflow_path
                ),
                workflow_manifest=(
                    candidate_manifest.model_dump(
                        mode="json"
                    )
                ),
                evidence_refs=[
                    "internal:approved-model",
                    "internal:existing-workflow",
                ],
            )
        ],
        searched_sources=[
            "LOCAL_INVENTORY",
            "MODEL_REGISTRY",
            "WORKFLOW_REGISTRY",
        ],
    )
    response_path = (
        acquisition.store
        .research_response_path(case_id)
    )
    response_path.write_text(
        response.model_dump_json(indent=2),
        encoding="utf-8",
    )

    agent = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v179-auto-promotion-agent",
            resources={ResourceClass.AGENT},
            capabilities={
                "rnd.capability.acquire"
            },
        ),
        poll_seconds=0.01,
    )
    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v179-auto-promotion-gpu",
            resources={ResourceClass.GPU},
            capabilities={
                "lab.comfyui.execute"
            },
        ),
        poll_seconds=0.01,
    )
    try:
        assert agent.tick() is True
        first = ctx.turbo_store.get_work(
            acquisition_work.work_id
        )
        assert first.state is WorkState.RETRY
        assert first.attempts == 0
        assert first.last_error == (
            "AWAITING_CANDIDATE_LAB_EXECUTION"
        )

        case = acquisition.store.get(
            case_id
        )
        record = case.candidate_records[0]
        assert record.lab_work_id
        lab_work = ctx.turbo_store.get_work(
            record.lab_work_id
        )
        assert lab_work.state is WorkState.QUEUED
        assert lab_work.resource is ResourceClass.GPU

        assert gpu.tick() is True
        lab_done = ctx.turbo_store.get_work(
            record.lab_work_id
        )
        assert lab_done.state is WorkState.SUCCESS
        assert lab_done.result["passed"] is True

        # Respect the durable defer/not-before contract rather than
        # mutating scheduler state behind its back.
        time.sleep(5.2)
        assert agent.tick() is True
    finally:
        agent.close()
        gpu.close()

    second = ctx.turbo_store.get_work(
        acquisition_work.work_id
    )
    # The image workflow was safely promoted, but it does not solve
    # this block-shot method gap, so acquisition remains deferred.
    assert second.state is WorkState.RETRY
    assert second.attempts == 0
    assert second.last_error == (
        "CAPABILITY_GATES_STILL_INCOMPLETE"
    )

    case = acquisition.store.get(case_id)
    record = case.candidate_records[0]
    assert record.promotion_state == (
        PromotionState.REGISTRY_PROMOTED.value
    )
    assert record.promotion_attestation_id
    assert Path(
        record.promotion_attestation_path
    ).is_file()
    assert isolated_workflows.get(
        "verify.acquisition.v179.sd15",
        "1",
    )

    final_decision = (
        ctx.method_switch.deliberate(
            request
        )
    )
    assert final_decision.executable is False

    payload = {
        "acquisition_work": {
            "work_id": acquisition_work.work_id,
            "state": second.state.value,
            "attempts": second.attempts,
            "last_error": second.last_error,
        },
        "lab_work": {
            "work_id": record.lab_work_id,
            "state": lab_done.state.value,
            "resource": lab_done.resource.value,
            "passed": lab_done.result[
                "passed"
            ],
            "candidate_execution": (
                lab_done.result[
                    "candidate_execution"
                ]
            ),
        },
        "promotion": {
            "state": record.promotion_state,
            "attestation_id": (
                record.promotion_attestation_id
            ),
            "attestation_path": (
                record.promotion_attestation_path
            ),
            "workflow_registered": True,
            "registry_count": len(
                isolated_workflows.list()
            ),
        },
        "method_gap_after_promotion": {
            "executable": (
                final_decision.executable
            ),
            "status": (
                final_decision.status.value
            ),
            "reasons": (
                final_decision.reasons
            ),
        },
    }
    out = root / (
        "acquisition_auto_promotion_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
