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
from cinefactory.turbo.repair_memory import RepairMemory
from cinefactory.turbo.store import TurboStore


def _episode(case: str, shot_class: str):
    ns = runpy.run_path(
        str(ROOT / "tests" / "test_block_auto_repair_v173.py")
    )
    base = ns["_episode"]()
    shot = base.shots[0].model_copy(
        deep=True,
        update={
            "creative_intent": {
                **dict(base.shots[0].creative_intent),
                "production_class": shot_class,
                "economics": {
                    "max_gpu_seconds": 1.0,
                },
            }
        },
    )
    project_id = f"VERIFY_ECONOMICS_V175_{case}"
    return base.model_copy(
        deep=True,
        update={
            "project_id": project_id,
            "episode_id": project_id,
            "shots": [shot],
            "metadata": {
                "economics": {
                    "max_project_gpu_seconds": 1000.0,
                }
            },
        },
    )


def _run_case(case: str, shot_class: str) -> dict:
    episode = _episode(case, shot_class)
    project_root = (
        ROOT
        / "data"
        / "verification"
        / "v175_production_economics"
        / case.lower()
    )
    project_root.mkdir(parents=True, exist_ok=True)

    isolated_db = project_root / "turbo_verification.db"
    if isolated_db.exists():
        isolated_db.unlink()

    ctx = build_context(ROOT)
    ctx.turbo_store = TurboStore(isolated_db)
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
    compiled.shots[0].render_quality.exposure = -3.0

    original_compile = producer.assembler.compile
    producer.assembler.compile = lambda *args, **kwargs: compiled
    try:
        report = producer.produce_turbo(
            episode,
            project_root=project_root,
            timeout_seconds=240,
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

    payload = {
        "case": case,
        "shot_class": shot_class,
        "passed": report.passed,
        "report_findings": report.findings,
        "shot_findings": shot_report.findings,
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
                "economics_budget": take.evidence.get(
                    "economics_budget"
                ),
                "economics_decision": take.evidence.get(
                    "economics_decision"
                ),
                "path": take.path,
            }
            for take in shot_report.takes
        ],
        "repair_directives": [
            directive.model_dump(mode="json")
            for directive in shot_report.repair_directives
        ],
        "execution_metrics": report.execution_metrics,
        "turbo_work": [
            {
                "work_id": item.work_id,
                "kind": item.kind,
                "handler": item.handler,
                "state": item.state.value,
                "repair_round": item.payload.get("repair_round"),
                "repair_of_work_id": item.payload.get(
                    "repair_of_work_id"
                ),
            }
            for item in work
        ],
    }
    return payload


def main() -> None:
    background = _run_case(
        "BACKGROUND_BUDGET_STOP",
        "BACKGROUND",
    )
    hero = _run_case(
        "HERO_BUDGET_SWITCH",
        "HERO",
    )

    bg_decision = (
        background["execution_metrics"]
        .get("economics", {})
        .get("decisions", [])
    )
    hero_decision = (
        hero["execution_metrics"]
        .get("economics", {})
        .get("decisions", [])
    )

    assert background["passed"] is False
    assert len(background["takes"]) == 1
    assert bg_decision
    assert bg_decision[0]["action"] == "STOP_BUDGET"
    assert background["repair_directives"][0]["failure_code"] == (
        "COST_POLICY_FAIL"
    )
    assert background["repair_directives"][0]["action"] == (
        "STOP_LOCAL_REPAIR_BUDGET"
    )
    assert not any(
        item["kind"] == "block.render.repair"
        for item in background["turbo_work"]
    )
    assert not any(
        item["handler"] == "timeline.accept"
        for item in background["turbo_work"]
    )

    assert hero["passed"] is False
    assert len(hero["takes"]) == 1
    assert hero_decision
    assert hero_decision[0]["action"] == "SWITCH_METHOD"
    assert hero["repair_directives"][0]["failure_code"] == (
        "MODEL_CAPABILITY"
    )
    assert hero["repair_directives"][0]["action"] == (
        "SWITCH_PRODUCTION_METHOD"
    )
    assert not any(
        item["kind"] == "block.render.repair"
        for item in hero["turbo_work"]
    )
    assert not any(
        item["handler"] == "timeline.accept"
        for item in hero["turbo_work"]
    )
    hero_acquisition = [
        item
        for item in hero["turbo_work"]
        if item["kind"] == "rnd.capability.acquire"
    ]
    assert len(hero_acquisition) == 1
    assert hero_acquisition[0]["handler"] == (
        "rnd.capability.acquire"
    )
    assert hero_acquisition[0]["state"] == "QUEUED"
    assert any(
        item.startswith("CAPABILITY_ACQUISITION_WORK:")
        for item in hero["shot_findings"]
    )
    assert not any(
        item["kind"] == "rnd.capability.acquire"
        for item in background["turbo_work"]
    )

    payload = {
        "background": background,
        "hero": hero,
    }
    root = (
        ROOT
        / "data"
        / "verification"
        / "v175_production_economics"
    )
    out = root / "production_economics_verification.json"
    out.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
