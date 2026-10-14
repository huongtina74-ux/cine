from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.studio.block_production import (
    BlockAnimationProducer,
)
from cinefactory.studio.production_method_switch import (
    MethodSwitchPolicy,
    MethodSwitchRequest,
)
from cinefactory.turbo.repair_memory import RepairMemory
from cinefactory.turbo.store import TurboStore


def _episode():
    ns = runpy.run_path(
        str(
            ROOT
            / "tests"
            / "test_block_auto_repair_v173.py"
        )
    )
    base = ns["_episode"]()
    shot = base.shots[0].model_copy(
        deep=True,
        update={
            "creative_intent": {
                **dict(base.shots[0].creative_intent),
                "production_class": "HERO",
                "continuity_priority": True,
                "economics": {
                    # Force local Eevee repair to stop after the
                    # first failed take.
                    "max_gpu_seconds": 1.0,
                    # But explicitly reserve budget for a different
                    # qualified production method.
                    "method_switch_gpu_seconds": 60.0,
                    "max_vram_gb": 12.0,
                },
            }
        },
    )
    return base.model_copy(
        deep=True,
        update={
            "project_id": "VERIFY_METHOD_SWITCH_V176",
            "episode_id": "VERIFY_METHOD_SWITCH_V176",
            "shots": [shot],
            "metadata": {
                "economics": {
                    "max_project_gpu_seconds": 120.0,
                }
            },
        },
    )


def main() -> None:
    episode = _episode()
    project_root = (
        ROOT
        / "data"
        / "verification"
        / "v176_method_switch"
    )
    project_root.mkdir(parents=True, exist_ok=True)
    db = project_root / "turbo_verification.db"
    if db.exists():
        db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(db)
    ctx.repair_memory = RepairMemory(ctx.turbo_store)

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
        ctx=ctx,
        max_repair_rounds=4,
    )

    output_dir = (
        project_root
        / "renders"
        / "block_animation"
    )
    compiled = producer.assembler.compile(
        episode,
        output_dir=output_dir,
    )
    # -1.5 EV fails the tightened daylight frame gate, while
    # the safe lookdev repair plan moves it back to 0 EV.
    compiled.shots[0].render_quality.exposure = -1.5

    original_compile = producer.assembler.compile
    producer.assembler.compile = (
        lambda *args, **kwargs: compiled
    )
    try:
        report = producer.produce_turbo(
            episode,
            project_root=project_root,
            timeout_seconds=300,
            poll_seconds=0.005,
            render_preview=True,
        )
    finally:
        producer.assembler.compile = original_compile
        producer.close()

    shot_report = report.shots[0]
    work = [
        item
        for item in ctx.turbo_store.list_work(limit=1000)
        if item.project_id == episode.project_id
    ]
    work.sort(key=lambda item: item.created_at)

    render_work = next(
        item
        for item in work
        if item.kind == "block.render"
    )
    switch_work = next(
        item
        for item in work
        if item.kind == "block.render.method_switch"
    )
    timeline = next(
        item
        for item in work
        if item.kind == "timeline.accept"
    )
    assembly = next(
        item
        for item in work
        if item.kind == "block.episode.assemble"
    )

    first = shot_report.takes[0]
    switched = shot_report.takes[1]

    assert report.passed is True
    assert len(shot_report.takes) == 2
    assert first.visual_pass is False
    assert switched.visual_pass is True
    assert render_work.state.value == "QC_REJECTED"
    assert switch_work.state.value == "SUCCESS"
    assert switch_work.payload["method_id"] == (
        "blender.cycles.quality"
    )
    assert (
        switch_work.payload["job"]["shot"]["render_engine"]
        == "CYCLES"
    )
    assert (
        switch_work.payload["job"]["shot"]
        ["render_quality"]["engine"]
        == "CYCLES"
    )
    assert (
        switch_work.payload["job"]["shot"]
        ["render_quality"]["exposure"]
        == 0.0
    )
    assert timeline.dependencies == [switch_work.work_id]
    assert assembly.dependencies == [timeline.work_id]
    method_evidence = switched.evidence["production_method"]
    assert method_evidence["method_switch"] is True
    assert method_evidence["method_id"] == (
        "blender.cycles.quality"
    )
    metrics = report.execution_metrics
    assert metrics["repair_samples"] == 0
    assert metrics["method_switch_samples"] == 1
    assert metrics["method_switch_successes"] == 1
    assert metrics["method_switch_success_rate"] == 1.0

    # Also prove fail-closed acquisition behavior once Cycles is
    # already the current method and no cross-tool block backend is
    # fully qualified/normalized.
    blocked = ctx.method_switch.deliberate(
        MethodSwitchRequest(
            project_id=episode.project_id,
            episode_id=episode.episode_id,
            shot_id="S01",
            current_tool_id="blender",
            current_method_id="blender.cycles.quality",
            policy=MethodSwitchPolicy.QUALITY_FIRST_ALTERNATIVE,
            min_quality=0.95,
            max_vram_gb=12.0,
            local_only=True,
            commercial_safe=True,
            max_additional_gpu_seconds=60.0,
            mean_current_attempt_seconds=5.0,
            continuity_priority=True,
            backend_switch_allowed=False,
            recurring_identity_required=True,
            visual_style="MINECRAFT",
            failure_codes=["MODEL_CAPABILITY"],
        )
    )
    assert blocked.executable is False
    assert blocked.acquisition_request_path is not None
    acquisition_path = Path(
        blocked.acquisition_request_path
    )
    assert acquisition_path.is_file()

    payload = {
        "passed": report.passed,
        "selected_take_id": shot_report.selected_take_id,
        "selected_path": shot_report.selected_path,
        "takes": [
            {
                "take_id": take.take_id,
                "repair_round": take.repair_round,
                "technical_pass": take.technical_pass,
                "visual_pass": take.visual_pass,
                "failure_code": (
                    take.failure_code.value
                    if take.failure_code is not None
                    else None
                ),
                "economics_decision": (
                    take.evidence.get(
                        "economics_decision"
                    )
                ),
                "method_switch_decision": (
                    take.evidence.get(
                        "method_switch_decision"
                    )
                ),
                "production_method": (
                    take.evidence.get(
                        "production_method"
                    )
                ),
                "path": take.path,
            }
            for take in shot_report.takes
        ],
        "execution_metrics": report.execution_metrics,
        "turbo_work": [
            {
                "work_id": item.work_id,
                "kind": item.kind,
                "handler": item.handler,
                "state": item.state.value,
                "dependencies": item.dependencies,
                "repair_round": item.payload.get(
                    "repair_round"
                ),
                "method_switch": item.payload.get(
                    "method_switch"
                ),
                "method_id": item.payload.get(
                    "method_id"
                ),
                "method_switch_of_work_id": (
                    item.payload.get(
                        "method_switch_of_work_id"
                    )
                ),
            }
            for item in work
        ],
        "blocked_next_switch": (
            blocked.model_dump(mode="json")
        ),
        "acquisition_request": str(acquisition_path),
    }

    out = project_root / (
        "production_method_switch_verification.json"
    )
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
