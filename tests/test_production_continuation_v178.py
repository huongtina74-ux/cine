from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from cinefactory.studio.production_continuation import (
    ContinuationShotState,
    ProductionContinuationManager,
    ProductionContinuationStore,
)
from cinefactory.turbo.contracts import (
    ResourceClass,
    WorkItem,
    WorkState,
)
from cinefactory.turbo.store import TurboStore


def _shot(shot_id: str, order: int):
    return SimpleNamespace(
        shot_id=shot_id,
        order=order,
        duration_seconds=1.0,
        camera_takes=[],
    )


def _success_work(
    store: TurboStore,
    *,
    work_id: str,
    project_id: str,
    kind: str = "block.render",
):
    item = WorkItem(
        work_id=work_id,
        project_id=project_id,
        kind=kind,
        handler="noop",
        resource=ResourceClass.GPU,
    )
    store.enqueue_work(item)
    store.finish_work(
        work_id,
        True,
        result={"path": f"{work_id}.mp4"},
    )
    return store.get_work(work_id)


def test_continuation_waits_until_every_shot_is_accepted(tmp_path):
    turbo = TurboStore(tmp_path / "turbo.db")
    manager = ProductionContinuationManager(
        tmp_path,
        turbo,
        store=ProductionContinuationStore(
            tmp_path / "continuations"
        ),
    )
    compiled = SimpleNamespace(
        project_id="P1",
        episode_id="E1",
        shots=[_shot("S01", 0), _shot("S02", 1)],
    )
    first = _success_work(
        turbo,
        work_id="W_FIRST",
        project_id="P1",
    )
    record = manager.create_blocked_episode(
        compiled=compiled,
        output_dir=tmp_path / "renders",
        accepted_rows=[
            {
                "shot": compiled.shots[0],
                "work_id": first.work_id,
                "path": "first.mp4",
                "repair_round": 0,
            }
        ],
        acquisition_by_shot={"S02": "W_ACQ"},
    )
    assert record.all_accepted is False
    states = {
        item.shot_id: item.state
        for item in record.shots
    }
    assert states["S01"] is ContinuationShotState.ACCEPTED
    assert states["S02"] is (
        ContinuationShotState.WAITING_CAPABILITY
    )

    _success_work(
        turbo,
        work_id="W_SECOND",
        project_id="P1",
        kind="block.render.method_switch",
    )
    manager.mark_requeued(
        continuation_id=record.continuation_id,
        shot_id="S02",
        render_work_id="W_SECOND",
        method_id="blender.cycles.quality",
    )
    before = manager.store.get(record.continuation_id)
    assert before.post_enqueued is False
    assert next(
        item for item in before.shots
        if item.shot_id == "S02"
    ).state is ContinuationShotState.REQUEUED

    resumed = manager.accept_requeued_render(
        continuation_id=record.continuation_id,
        shot_id="S02",
        render_work_id="W_SECOND",
        path="second.mp4",
        method_id="blender.cycles.quality",
    )
    assert resumed.accepted is True
    assert resumed.all_accepted is True
    assert resumed.post_enqueued is True
    assert len(resumed.timeline_work_ids) == 2
    assert resumed.assembly_work_id is not None

    timeline = [
        turbo.get_work(work_id)
        for work_id in resumed.timeline_work_ids
    ]
    assert {
        item.payload["shot_id"]
        for item in timeline
    } == {"S01", "S02"}
    assert all(
        item.kind == "timeline.accept"
        for item in timeline
    )
    assembly = turbo.get_work(
        resumed.assembly_work_id
    )
    assert assembly.kind == "block.episode.assemble"
    assert set(assembly.dependencies) == set(
        resumed.timeline_work_ids
    )


def test_continuation_post_enqueue_is_idempotent(tmp_path):
    turbo = TurboStore(tmp_path / "turbo.db")
    manager = ProductionContinuationManager(
        tmp_path,
        turbo,
        store=ProductionContinuationStore(
            tmp_path / "continuations"
        ),
    )
    compiled = SimpleNamespace(
        project_id="P2",
        episode_id="E2",
        shots=[_shot("S01", 0)],
    )
    _success_work(
        turbo,
        work_id="W_RECOVER",
        project_id="P2",
        kind="block.render.method_switch",
    )
    record = manager.create_blocked_episode(
        compiled=compiled,
        output_dir=tmp_path / "renders",
        accepted_rows=[],
        acquisition_by_shot={"S01": "W_ACQ"},
    )
    manager.mark_requeued(
        continuation_id=record.continuation_id,
        shot_id="S01",
        render_work_id="W_RECOVER",
        method_id="blender.cycles.quality",
    )
    first = manager.accept_requeued_render(
        continuation_id=record.continuation_id,
        shot_id="S01",
        render_work_id="W_RECOVER",
        path="recovered.mp4",
        method_id="blender.cycles.quality",
    )
    work_count = len(turbo.list_work(limit=100))
    second = manager.accept_requeued_render(
        continuation_id=record.continuation_id,
        shot_id="S01",
        render_work_id="W_RECOVER",
        path="recovered.mp4",
        method_id="blender.cycles.quality",
    )
    assert second.timeline_work_ids == first.timeline_work_ids
    assert second.assembly_work_id == first.assembly_work_id
    assert len(turbo.list_work(limit=100)) == work_count


def test_non_acquisition_failure_does_not_enqueue_post(tmp_path):
    turbo = TurboStore(tmp_path / "turbo.db")
    manager = ProductionContinuationManager(
        tmp_path,
        turbo,
        store=ProductionContinuationStore(
            tmp_path / "continuations"
        ),
    )
    compiled = SimpleNamespace(
        project_id="P3",
        episode_id="E3",
        shots=[_shot("S01", 0), _shot("S02", 1)],
    )
    _success_work(
        turbo,
        work_id="W_FIRST",
        project_id="P3",
    )
    record = manager.create_blocked_episode(
        compiled=compiled,
        output_dir=tmp_path / "renders",
        accepted_rows=[
            {
                "shot": compiled.shots[0],
                "work_id": "W_FIRST",
                "path": "first.mp4",
                "repair_round": 0,
            }
        ],
        acquisition_by_shot={},
    )
    failed = next(
        item
        for item in record.shots
        if item.shot_id == "S02"
    )
    assert failed.state is ContinuationShotState.FAILED
    assert record.post_enqueued is False
    assert not [
        item
        for item in turbo.list_work(limit=100)
        if item.kind in {
            "timeline.accept",
            "block.episode.assemble",
        }
    ]
