from __future__ import annotations

from pathlib import Path

from cinefactory.block_animation.assembler import EpisodeAssembler
from cinefactory.block_animation.contracts import (
    ActorPlacement,
    CameraIntent,
    EpisodeSpec,
    ShotPerformanceSpec,
    TransformSpec,
    Vec3,
)
from cinefactory.block_animation.repair import LocalBlockRepairPlanner
from cinefactory.domain.enums import FailureCode
from cinefactory.production.contracts import RepairDirective
from cinefactory.studio.block_production import BlockAnimationProducer


ROOT = Path(__file__).resolve().parents[1]


def _episode() -> EpisodeSpec:
    return EpisodeSpec(
        project_id="P_REPAIR",
        episode_id="E_REPAIR",
        title="repair test",
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
                            location=Vec3(x=0.0, y=0.5, z=0.0)
                        ),
                    )
                ],
                camera=CameraIntent(
                    purpose="fidelity_medium",
                    pattern_id="fidelity_medium",
                    targets=["A"],
                ),
                creative_intent={"scene_id": "SC1"},
            )
        ],
    )


def _compiled_shot():
    return EpisodeAssembler.from_root(ROOT).compile(
        _episode()
    ).shots[0]


def test_local_lookdev_repair_changes_only_exposure_execution_parameter():
    shot = _compiled_shot()
    before_purpose = dict(shot.creative_intent)
    before = shot.render_quality.exposure
    directive = RepairDirective(
        shot_id=shot.shot_id,
        failure_code=FailureCode.LOOKDEV_FAIL,
        owner="LIGHTING_COLOR_ENGINE",
        retryable=True,
        action="REBALANCE_LIGHTING_AND_COLOR",
        findings=["RENDERED_FRAME_UNDEREXPOSED:HEAD"],
    )
    plan = LocalBlockRepairPlanner().plan(
        shot,
        [directive],
        repair_round=1,
    )
    assert plan.supported is True
    assert plan.repaired_shot is not None
    assert plan.repaired_shot.render_quality.exposure == before + 1.5
    assert plan.repaired_shot.creative_intent == before_purpose
    assert (
        plan.repaired_shot.lighting_intent["auto_repair"][
            "preserve_creative_intent"
        ]
        is True
    )


def test_local_camera_repair_widens_lens_and_preserves_shot_purpose():
    shot = _compiled_shot()
    before_lens = shot.camera_takes[0].lens_mm
    before_purpose = dict(shot.creative_intent)
    directive = RepairDirective(
        shot_id=shot.shot_id,
        failure_code=FailureCode.CAMERA_INTENT_FAIL,
        owner="CINEMATOGRAPHY_ENGINE",
        retryable=True,
        action="RENDER_WITH_CAMERA_CONSTRAINTS",
        findings=["TARGET_OUTSIDE_SAFE_FRAME"],
    )
    plan = LocalBlockRepairPlanner().plan(
        shot,
        [directive],
        repair_round=1,
    )
    assert plan.supported is True
    assert plan.repaired_shot is not None
    assert plan.repaired_shot.camera_takes[0].lens_mm < before_lens
    assert plan.repaired_shot.creative_intent == before_purpose


def test_identity_repair_is_not_locally_auto_applied():
    shot = _compiled_shot()
    directive = RepairDirective(
        shot_id=shot.shot_id,
        failure_code=FailureCode.IDENTITY_DRIFT,
        owner="ASSET_ENGINE",
        retryable=True,
        action="RENDER_WITH_STRONGER_CANONICAL_REFERENCES",
        findings=["RENDERED_IDENTITY_DRIFT:A"],
    )
    plan = LocalBlockRepairPlanner().plan(
        shot,
        [directive],
        repair_round=1,
    )
    assert plan.supported is False
    assert plan.repaired_shot is None
    assert any("UNSUPPORTED_LOCAL_REPAIR" in x for x in plan.skipped)


class _DummyWorker:
    pid = 123

    def start(self):
        return None

    def close(self):
        return None


class _RepairRuntime:
    def __init__(self, output: Path):
        self.output = output
        self.calls = 0
        self.exposures: list[float] = []

    def render_and_qc(self, _worker, job):
        self.calls += 1
        self.exposures.append(float(job.shot.render_quality.exposure))
        actual_output = Path(job.output_path)
        actual_output.parent.mkdir(parents=True, exist_ok=True)
        actual_output.write_bytes(b"fake")
        self.output = actual_output
        if self.calls == 1:
            raise RuntimeError(
                "render combined QC failed: "
                "RENDERED_FRAME_UNDEREXPOSED:HEAD"
            )
        return {
            "path": str(self.output),
            "geometry_qc": {"passed": True, "warnings": []},
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
            "creative_intent_bound": True,
            "render_state": {
                "shot_id": job.shot.shot_id,
                "scene_id": "SC1",
                "actors": {},
                "props": {},
                "lighting": {},
            },
            "visual_qc": {
                "passed": True,
                "findings": [],
                "black_seconds": 0,
                "freeze_seconds": 0,
            },
        }


def test_producer_bounded_auto_repair_records_failed_and_repaired_takes(tmp_path):
    worker = _DummyWorker()
    producer = BlockAnimationProducer(
        ROOT,
        worker=worker,
        max_repair_rounds=2,
    )
    runtime = _RepairRuntime(tmp_path / "accepted.mp4")
    producer.runtime = runtime
    try:
        report = producer.produce(
            _episode(),
            project_root=tmp_path / "project",
            render_preview=True,
        )
    finally:
        producer.close()

    assert report.passed is True
    shot = report.shots[0]
    assert shot.passed is True
    assert len(shot.takes) == 2
    assert shot.takes[0].technical_pass is True
    assert shot.takes[0].visual_pass is False
    assert shot.takes[0].repair_round == 0
    assert shot.takes[1].visual_pass is True
    assert shot.takes[1].repair_round == 1
    assert runtime.exposures[1] > runtime.exposures[0]
    assert shot.repair_directives == []
    plan = shot.takes[0].evidence["repair_plan_next"]
    assert plan["supported"] is True
    assert (
        plan["applied"][0]["failure_code"]
        == FailureCode.LOOKDEV_FAIL.value
    )
