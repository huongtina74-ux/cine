from __future__ import annotations

import shutil
from pathlib import Path

from cinefactory.appctx import build_context
from cinefactory.block_animation.contracts import (
    ActorPlacement,
    BlenderAnimationJob,
    CameraIntent,
    EpisodeSpec,
    ShotPerformanceSpec,
    TransformSpec,
    Vec3,
)
from cinefactory.block_animation.runtime import RenderQualityRejected
from cinefactory.studio.block_production import BlockAnimationProducer
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkerSpec,
    WorkItem,
    WorkState,
)
from cinefactory.turbo.daemon import FactoryDaemon
from cinefactory.turbo.store import TurboStore


SOURCE_ROOT = Path(__file__).resolve().parents[1]


def _make_root(tmp_path: Path) -> Path:
    for name in ("config", "models", "workflows", "knowledge"):
        source = SOURCE_ROOT / name
        if source.is_dir():
            shutil.copytree(source, tmp_path / name)
    return tmp_path


def _episode(project_id: str = "P_TURBO_REPAIR") -> EpisodeSpec:
    return EpisodeSpec(
        project_id=project_id,
        episode_id=f"{project_id}_EP",
        title="turbo repair",
        fps=24,
        width=320,
        height=180,
        quality_profile="preview",
        shots=[
            ShotPerformanceSpec(
                shot_id="S01",
                scene_template_id="minecraft_classroom",
                duration_seconds=1.0,
                actors=[
                    ActorPlacement(
                        actor_id="A",
                        rig_id="mc_a",
                        transform=TransformSpec(
                            location=Vec3(
                                x=0.0,
                                y=0.5,
                                z=0.0,
                            )
                        ),
                    )
                ],
                camera=CameraIntent(
                    purpose="fidelity_medium",
                    pattern_id="fidelity_medium",
                    targets=["A"],
                ),
                creative_intent={
                    "scene_id": "SC1",
                },
                lighting_intent={
                    "time_of_day": "DAY",
                    "light_state": "soft",
                },
            )
        ],
    )


def _frame_qc(*, passed: bool, dark: bool) -> dict:
    luma = 0.03 if dark else 0.12
    shadow = 0.90 if dark else 0.10
    findings = (
        [
            "RENDERED_FRAME_UNDEREXPOSED:HEAD",
            "RENDERED_FRAME_UNDEREXPOSED:MID",
            "RENDERED_FRAME_UNDEREXPOSED:TAIL",
        ]
        if not passed
        else []
    )

    def frame(label: str) -> dict:
        return {
            "label": label,
            "time_seconds": 0.1,
            "width": 160,
            "height": 90,
            "luma_mean": luma,
            "luma_std": 0.08,
            "shadow_clip_ratio": shadow,
            "highlight_clip_ratio": 0.0,
            "saturation_mean": 0.10,
            "rgb_mean": [luma, luma, luma],
            "ahash64": "f0f0f0f00f0f0f0f",
        }

    return {
        "passed": passed,
        "findings": findings,
        "warnings": [],
        "head": frame("head"),
        "mid": frame("mid"),
        "tail": frame("tail"),
        "actors": {},
        "sidecar_path": None,
    }


def _render_result(job: BlenderAnimationJob, *, passed: bool) -> dict:
    dark = not passed
    findings = (
        [
            "RENDERED_FRAME_UNDEREXPOSED:HEAD",
            "RENDERED_FRAME_UNDEREXPOSED:MID",
            "RENDERED_FRAME_UNDEREXPOSED:TAIL",
        ]
        if dark
        else []
    )
    return {
        "path": str(job.output_path),
        "duration": job.shot.duration_seconds,
        "width": 160,
        "height": 90,
        "fps": 24.0,
        "video_codec": "h264",
        "worker_pid": 1,
        "quality_profile": job.shot.render_quality.profile_id,
        "visual_qc": {
            "passed": passed,
            "findings": [],
            "black_seconds": 0.0,
            "freeze_seconds": 0.0,
        },
        "rendered_frame_qc": _frame_qc(
            passed=passed,
            dark=dark,
        ),
        "geometry_qc": {
            "passed": True,
            "warnings": [],
            "blockers": [],
        },
        "identity_qc": {
            "passed": True,
            "score": 1.0,
            "blockers": [],
        },
        "performance_qc": {
            "passed": True,
            "score": 1.0,
            "warnings": [],
            "blockers": [],
        },
        "render_state": {
            "shot_id": job.shot.shot_id,
            "scene_id": "SC1",
            "actors": {},
            "props": {},
            "lighting": {
                "time_of_day": "DAY",
                "light_state": "soft",
                "key_energy": 1000.0,
                "fill_energy": 500.0,
                "rim_energy": 600.0,
                "world_strength": 0.5,
            },
        },
        "gaze_debug": [],
        "lighting_debug": {},
        "creative_intent_bound": True,
        "performance_directive_count": 0,
        "qc_passed": passed,
        "qc_findings": findings,
    }


def test_store_qc_rejected_preserves_result_and_blocks_dependency(tmp_path: Path):
    store = TurboStore(tmp_path / "turbo.db")
    render = WorkItem(
        project_id="P",
        kind="render",
        handler="render",
        resource=ResourceClass.GPU,
    )
    timeline = WorkItem(
        project_id="P",
        kind="timeline",
        handler="timeline",
        resource=ResourceClass.IO,
        dependencies=[render.work_id],
    )
    store.enqueue_work(render)
    store.enqueue_work(timeline)

    state = store.reject_work(
        render.work_id,
        "quality failed",
        result={"path": "render.mp4", "score": 0.2},
    )
    assert state is WorkState.QC_REJECTED
    rejected = store.get_work(render.work_id)
    assert rejected.state is WorkState.QC_REJECTED
    assert rejected.result["path"] == "render.mp4"
    assert rejected.result["score"] == 0.2

    assert store.propagate_blocked_dependencies() == 1
    assert store.get_work(timeline.work_id).state is WorkState.BLOCKED


def test_daemon_uses_qc_rejected_state_for_quality_exception(tmp_path: Path):
    root = _make_root(tmp_path)
    ctx = build_context(root)
    item = WorkItem(
        project_id="P_QC",
        kind="quality",
        handler="qc.reject",
        resource=ResourceClass.CPU,
        max_attempts=3,
    )
    ctx.turbo_store.enqueue_work(item)
    daemon = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="cpu-qc",
            resources={ResourceClass.CPU},
            capabilities={"qc.reject"},
        ),
    )
    daemon.register(
        "qc.reject",
        lambda _item: (_ for _ in ()).throw(
            RenderQualityRejected(
                ["RENDERED_FRAME_UNDEREXPOSED:HEAD"],
                result={
                    "path": "shot.mp4",
                    "rendered_frame_qc": {
                        "passed": False,
                    },
                },
            )
        ),
    )
    try:
        assert daemon.tick() is True
    finally:
        daemon.close()

    rejected = ctx.turbo_store.get_work(item.work_id)
    assert rejected.state is WorkState.QC_REJECTED
    assert rejected.attempts == 1
    assert rejected.result["path"] == "shot.mp4"
    assert (
        "RENDERED_FRAME_UNDEREXPOSED:HEAD"
        in rejected.last_error
    )


def test_turbo_producer_repairs_with_new_work_item_and_post_depends_on_selected_take(
    tmp_path: Path,
    monkeypatch,
):
    root = _make_root(tmp_path)
    ctx = build_context(root)
    episode = _episode()

    def fake_render(self, item):
        job = BlenderAnimationJob.model_validate(
            item.payload["job"]
        )
        output = Path(job.output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"rendered")
        passed = (
            float(job.shot.render_quality.exposure)
            >= 0.0
        )
        result = _render_result(
            job,
            passed=passed,
        )
        if not passed:
            raise RenderQualityRejected(
                list(result["qc_findings"]),
                result=result,
            )
        return result

    def fake_assemble(self, item):
        output = Path(item.payload["output_path"])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"assembled")
        return {
            "path": str(output),
            "duration": 1.0,
            "width": 160,
            "height": 90,
            "fps": 24.0,
            "qc_passed": True,
        }

    monkeypatch.setattr(
        FactoryDaemon,
        "_blender_animation_render",
        fake_render,
    )
    monkeypatch.setattr(
        FactoryDaemon,
        "_block_episode_assemble",
        fake_assemble,
    )

    producer = BlockAnimationProducer(
        root,
        ctx=ctx,
        max_repair_rounds=1,
    )
    project_root = root / "data" / "verification" / "turbo-repair"
    compiled = producer.assembler.compile(
        episode,
        output_dir=(
            project_root / "renders" / "block_animation"
        ),
    )
    compiled.shots[0].render_quality.exposure = -1.5

    original_compile = producer.assembler.compile
    producer.assembler.compile = lambda *args, **kwargs: compiled
    try:
        report = producer.produce_turbo(
            episode,
            project_root=project_root,
            timeout_seconds=10,
            poll_seconds=0.005,
            render_preview=True,
        )
    finally:
        producer.assembler.compile = original_compile
        producer.close()

    assert report.passed is True
    assert report.execution_metrics["gpu_seconds"] > 0
    assert report.execution_metrics["gpu_wasted_seconds"] > 0
    assert (
        0.0
        < report.execution_metrics["gpu_waste_ratio"]
        < 1.0
    )
    shot = report.shots[0]
    assert len(shot.takes) == 2
    assert shot.takes[0].visual_pass is False
    assert shot.takes[0].technical_pass is True
    assert shot.takes[0].evidence["turbo_state"] == "QC_REJECTED"
    assert shot.takes[0].evidence["rendered_frame_qc"]["passed"] is False
    assert shot.takes[1].visual_pass is True
    assert shot.selected_take_id == "S01_BLENDER_TURBO_02"

    project_work = [
        item
        for item in ctx.turbo_store.list_work(limit=100)
        if item.project_id == episode.project_id
    ]
    render_items = [
        item
        for item in project_work
        if item.handler == "blender.animation.render"
    ]
    assert len(render_items) == 2

    first = next(
        item for item in render_items
        if item.payload.get("repair_round") == 0
    )
    repaired = next(
        item for item in render_items
        if item.payload.get("repair_round") == 1
    )
    assert first.state is WorkState.QC_REJECTED
    assert repaired.state is WorkState.SUCCESS
    assert (
        repaired.payload["repair_of_work_id"]
        == first.work_id
    )

    timeline = next(
        item
        for item in project_work
        if item.handler == "timeline.accept"
    )
    assert timeline.dependencies == [repaired.work_id]
    assert timeline.state is WorkState.SUCCESS

    assembly = next(
        item
        for item in project_work
        if item.handler == "block.episode.assemble"
    )
    assert assembly.dependencies == [timeline.work_id]
    assert assembly.state is WorkState.SUCCESS

    memory = ctx.turbo_store.best_repair(
        failure_code="LOOKDEV_FAIL",
        workflow_id="block_animation",
        shot_class="MINECRAFT",
    )
    assert memory is not None
    assert memory.attempts == 1
    assert memory.successes == 1


def test_qc_rejected_gpu_work_is_counted_as_wasted_compute(tmp_path: Path):
    root = _make_root(tmp_path)
    ctx = build_context(root)
    item = WorkItem(
        project_id="P_GPU_COST",
        kind="block.render",
        handler="gpu.reject",
        resource=ResourceClass.GPU,
        payload={
            "output_units": 24,
            "repair_round": 0,
        },
        max_attempts=1,
    )
    ctx.turbo_store.enqueue_work(item)
    daemon = FactoryDaemon(
        ctx,
        WorkerSpec(
            worker_id="gpu-cost",
            resources={ResourceClass.GPU},
            capabilities={"gpu.reject"},
        ),
    )
    daemon.register(
        "gpu.reject",
        lambda _item: (_ for _ in ()).throw(
            RenderQualityRejected(
                ["RENDERED_FRAME_UNDEREXPOSED:HEAD"],
                result={"path": "dark.mp4"},
            )
        ),
    )
    try:
        assert daemon.tick() is True
    finally:
        daemon.close()

    summary = ctx.turbo_store.execution_cost_summary(
        project_id="P_GPU_COST"
    )
    assert summary["samples"] == 1
    assert summary["gpu_seconds"] > 0
    assert summary["gpu_wasted_seconds"] == summary["gpu_seconds"]
    assert summary["gpu_waste_ratio"] == 1.0
    assert summary["by_state"][0]["state"] == "QC_REJECTED"


def test_repair_memory_is_consumed_as_strategy_hint(tmp_path: Path):
    root = _make_root(tmp_path)
    ctx = build_context(root)
    ctx.turbo_store.record_repair(
        key="block_animation:LOOKDEV_FAIL:REBALANCE_LIGHTING_AND_COLOR",
        failure_code="LOOKDEV_FAIL",
        workflow_id="block_animation",
        shot_class="MINECRAFT",
        strategy="REBALANCE_LIGHTING_AND_COLOR",
        prompt_directive="repair lighting",
        success=True,
        score=0.95,
    )
    memory = ctx.turbo_store.best_repair(
        failure_code="LOOKDEV_FAIL",
        workflow_id="block_animation",
        shot_class="MINECRAFT",
    )
    assert memory is not None

    producer = BlockAnimationProducer(
        root,
        ctx=ctx,
        max_repair_rounds=1,
    )
    shot = producer.assembler.compile(
        _episode("P_MEMORY"),
        output_dir=root / "renders",
    ).shots[0]
    shot.render_quality.exposure = -1.5
    from cinefactory.production.contracts import RepairDirective
    from cinefactory.domain.enums import FailureCode

    directive = RepairDirective(
        shot_id=shot.shot_id,
        failure_code=FailureCode.LOOKDEV_FAIL,
        owner="LIGHTING_COLOR_ENGINE",
        retryable=True,
        action="REBALANCE_LIGHTING_AND_COLOR",
        findings=["RENDERED_FRAME_UNDEREXPOSED:HEAD"],
    )
    plan = producer.repair_planner.plan(
        shot,
        [directive],
        repair_round=1,
        preferred_strategies={
            "LOOKDEV_FAIL": {
                "strategy": memory.strategy,
                "success_rate": memory.success_rate,
                "attempts": memory.attempts,
                "average_score": memory.average_score,
                "key": memory.key,
            }
        },
    )
    producer.close()

    assert plan.supported is True
    assert plan.memory_hints
    assert (
        plan.memory_hints[0]["strategy"]
        == "REBALANCE_LIGHTING_AND_COLOR"
    )
    assert plan.memory_hints[0]["success_rate"] == 1.0
