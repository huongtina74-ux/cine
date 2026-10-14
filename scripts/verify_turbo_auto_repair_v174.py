from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cinefactory.appctx import build_context
from cinefactory.studio.block_production import BlockAnimationProducer
from cinefactory.turbo.store import TurboStore
from cinefactory.turbo.repair_memory import RepairMemory


def main() -> None:
    ns = runpy.run_path(
        str(ROOT / "tests" / "test_block_auto_repair_v173.py")
    )
    episode = ns["_episode"]().model_copy(
        update={
            "project_id": "VERIFY_TURBO_REPAIR_V174_COSTMEM",
            "episode_id": "VERIFY_TURBO_REPAIR_V174_COSTMEM",
        }
    )

    blender = (
        ROOT
        / ".tools"
        / "blender-4.5.14-windows-x64"
        / "blender.exe"
    )
    project_root = (
        ROOT
        / "data"
        / "verification"
        / "v174_turbo_auto_repair"
    )
    output_dir = project_root / "renders" / "block_animation"

    ctx = build_context(ROOT)
    isolated_db = project_root / "turbo_verification.db"
    if isolated_db.exists():
        isolated_db.unlink()
    ctx.turbo_store = TurboStore(isolated_db)
    ctx.repair_memory = RepairMemory(ctx.turbo_store)
    producer = BlockAnimationProducer(
        ROOT,
        blender_executable=str(blender),
        ctx=ctx,
        max_repair_rounds=2,
    )
    compiled = producer.assembler.compile(
        episode,
        output_dir=output_dir,
    )
    compiled.shots[0].render_quality.exposure = -3.0

    original_compile = producer.assembler.compile
    producer.assembler.compile = lambda *args, **kwargs: compiled
    try:
        report = producer.produce_turbo(
            episode,
            project_root=project_root,
            render_preview=True,
            timeout_seconds=300,
            poll_seconds=0.02,
        )
    finally:
        producer.assembler.compile = original_compile
        producer.close()

    shot = report.shots[0]
    work = [
        item
        for item in ctx.turbo_store.list_work(limit=1000)
        if item.project_id == episode.project_id
    ]
    work.sort(key=lambda item: item.created_at)

    payload = {
        "passed": report.passed,
        "findings": report.findings,
        "selected_take_id": shot.selected_take_id,
        "selected_path": shot.selected_path,
        "selected_score": shot.selected_score,
        "execution_metrics": report.execution_metrics,
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
                "findings": list(take.findings),
                "turbo_work_id": take.evidence.get("turbo_work_id"),
                "turbo_state": take.evidence.get("turbo_state"),
                "repair_plan_next": take.evidence.get(
                    "repair_plan_next"
                ),
                "path": take.path,
            }
            for take in shot.takes
        ],
        "remaining_repair_directives": [
            item.model_dump(mode="json")
            for item in shot.repair_directives
        ],
        "turbo_work": [
            {
                "work_id": item.work_id,
                "kind": item.kind,
                "handler": item.handler,
                "state": item.state.value,
                "attempts": item.attempts,
                "max_attempts": item.max_attempts,
                "dependencies": list(item.dependencies),
                "repair_round": item.payload.get("repair_round"),
                "repair_of_work_id": item.payload.get(
                    "repair_of_work_id"
                ),
                "path": (
                    (item.payload.get("job") or {}).get("output_path")
                    or item.payload.get("output_path")
                ),
            }
            for item in work
        ],
        "repair_memory": (
            ctx.turbo_store.best_repair(
                failure_code="LOOKDEV_FAIL",
                workflow_id="block_animation",
                shot_class="MINECRAFT",
            ).model_dump(mode="json")
            if ctx.turbo_store.best_repair(
                failure_code="LOOKDEV_FAIL",
                workflow_id="block_animation",
                shot_class="MINECRAFT",
            )
            is not None
            else None
        ),
    }

    project_root.mkdir(parents=True, exist_ok=True)
    out = project_root / "turbo_auto_repair_verification.json"
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
