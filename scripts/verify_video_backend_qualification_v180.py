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
from cinefactory.turbo.metrics import gpu_snapshot
from cinefactory.turbo.store import TurboStore


def _request(
    *,
    reference: Path,
    precise_camera: bool = False,
    semantic_performance: bool = False,
) -> MethodSwitchRequest:
    return MethodSwitchRequest(
        project_id="V180_WAN_QUAL",
        episode_id="V180_WAN_QUAL",
        shot_id="S01",
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
        precise_camera_required=precise_camera,
        semantic_performance_required=semantic_performance,
        visual_style="MINECRAFT",
        failure_codes=["MODEL_CAPABILITY"],
        required_tags={"reference_conditioning"},
    )


def main() -> None:
    out = (
        ROOT
        / "data"
        / "verification"
        / "v180_video_backend_qualification"
    )
    out.mkdir(parents=True, exist_ok=True)
    db = out / "turbo_v180.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)

    before = ctx.models.get(
        ctx.cross_backend_video.profile.model_id,
        ctx.cross_backend_video.profile.model_revision,
    )
    before_approved = before.approved_for_production

    ns = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "test_block_auto_repair_v173.py"
        )
    )
    source = ns["_episode"]()
    base = source.shots[0]
    shot_a = base.model_copy(
        deep=True,
        update={
            "shot_id": "S01",
            "creative_intent": {
                "scene_id": "SC_WAN_A",
                "mood": "calm focused",
                "story_beat": "hold identity",
            },
        },
    )
    shot_b = base.model_copy(
        deep=True,
        update={
            "shot_id": "S02",
            "creative_intent": {
                "scene_id": "SC_WAN_B",
                "mood": "alert reaction",
                "story_beat": "preserve identity under a new seed",
            },
        },
    )
    episode = source.model_copy(
        deep=True,
        update={
            "project_id": "V180_WAN_QUAL",
            "episode_id": "V180_WAN_QUAL",
            "shots": [shot_a, shot_b],
        },
    )
    compiled = EpisodeAssembler.from_root(
        ROOT
    ).compile(
        episode,
        output_dir=out / "renders",
    )

    refs = [
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S01.cycles.golden.mp4",
        ROOT
        / "data"
        / "verification"
        / "v179_candidate_promotion"
        / "cycles_matrix"
        / "S02.cycles.golden.mp4",
    ]
    assert all(path.is_file() for path in refs)

    work_ids: list[str] = []
    for index, (shot, reference) in enumerate(
        zip(compiled.shots, refs),
        1,
    ):
        work = (
            ctx.cross_backend_video.build_work_item(
                compiled=compiled,
                shot=shot,
                output_path=(
                    out
                    / "renders"
                    / f"{shot.shot_id}.wan13b.mp4"
                ),
                render_preview=True,
                switch_round=index,
                switch_of_work_id=(
                    f"QUAL_REFERENCE_{index}"
                ),
                reference_frame_path=reference,
                recurring_identity_required=True,
                semantic_performance_required=False,
                precise_camera_required=False,
            )
        )
        ctx.turbo_store.enqueue_work(work)
        work_ids.append(work.work_id)

    gpu = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="v180-wan-qualification-gpu",
            resources={ResourceClass.GPU},
            capabilities={"block.video.comfy"},
            active_model_affinity=(
                compiled.shots
                and ctx.turbo_store.get_work(
                    work_ids[0]
                ).model_affinity
            ),
        ),
        poll_seconds=0.05,
    )
    try:
        assert gpu.tick() is True
        assert gpu.tick() is True
    finally:
        gpu.close()

    rows = [
        ctx.turbo_store.get_work(work_id)
        for work_id in work_ids
    ]
    assert all(
        row.state is WorkState.SUCCESS
        for row in rows
    )
    runtime_results = [
        (
            f"WAN_CASE_{index}",
            dict(row.result),
        )
        for index, row in enumerate(rows, 1)
    ]

    qualification, evidence_path = (
        ctx.video_backend_qualification.evaluate(
            runtime_results=runtime_results
        )
    )
    assert qualification.passed is True
    assert len(qualification.cases) == 2
    assert all(
        case.identity_measured
        for case in qualification.cases
    )
    assert all(
        (case.identity_score or 0.0) >= 0.80
        for case in qualification.cases
    )

    promoted = (
        ctx.video_backend_qualification
        .promote_model(evidence_path)
    )
    assert promoted.approved_for_production is True
    assert ctx.models.require_approved(
        promoted.model_id,
        promoted.revision,
    )

    normal_request = _request(
        reference=refs[0]
    )
    normal_decision = (
        ctx.method_switch.deliberate(
            normal_request
        )
    )
    assert normal_decision.executable is True
    assert normal_decision.selected_method_id == (
        "comfyui.wan21.fun.inpaint.1.3b"
    )

    exact_camera = ctx.method_switch.deliberate(
        _request(
            reference=refs[0],
            precise_camera=True,
        )
    )
    wan_camera = next(
        item
        for item in exact_camera.assessments
        if item.method_id
        == "comfyui.wan21.fun.inpaint.1.3b"
    )
    assert (
        "PRECISE_CAMERA_GEOMETRY_UNSUPPORTED"
        in wan_camera.blockers
    )

    semantic = ctx.method_switch.deliberate(
        _request(
            reference=refs[0],
            semantic_performance=True,
        )
    )
    wan_semantic = next(
        item
        for item in semantic.assessments
        if item.method_id
        == "comfyui.wan21.fun.inpaint.1.3b"
    )
    assert (
        "SEMANTIC_PERFORMANCE_VIDEO_QC_NOT_QUALIFIED"
        in wan_semantic.blockers
    )

    payload = {
        "model": {
            "model_id": promoted.model_id,
            "revision": promoted.revision,
            "approved_before": before_approved,
            "approved_after": (
                promoted.approved_for_production
            ),
            "evidence_path": str(evidence_path),
        },
        "qualification": {
            "passed": qualification.passed,
            "bundle_passed": (
                qualification.bundle_passed
            ),
            "tool_qualified": (
                qualification.tool_qualified
            ),
            "rights_reviewed": (
                qualification.rights_reviewed
            ),
            "output_terms_reviewed": (
                qualification
                .output_terms_reviewed
            ),
            "blockers": qualification.blockers,
            "cases": [
                case.model_dump(mode="json")
                for case in qualification.cases
            ],
            "matrix": (
                qualification.benchmark_matrix
                .model_dump(mode="json")
            ),
        },
        "renders": [
            {
                "work_id": row.work_id,
                "state": row.state.value,
                "path": row.result.get("path"),
                "bytes": (
                    Path(row.result["path"]).stat().st_size
                ),
                "identity_qc": row.result.get(
                    "identity_qc"
                ),
                "duration": row.result.get(
                    "duration"
                ),
                "fps": row.result.get("fps"),
            }
            for row in rows
        ],
        "routing": {
            "normal": {
                "status": (
                    normal_decision.status.value
                ),
                "selected_method_id": (
                    normal_decision
                    .selected_method_id
                ),
            },
            "exact_camera": {
                "status": (
                    exact_camera.status.value
                ),
                "wan_blockers": (
                    wan_camera.blockers
                ),
            },
            "semantic_performance": {
                "status": semantic.status.value,
                "wan_blockers": (
                    wan_semantic.blockers
                ),
            },
        },
        "gpu": gpu_snapshot(),
    }
    verification = (
        out
        / "video_backend_qualification_verification.json"
    )
    verification.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
