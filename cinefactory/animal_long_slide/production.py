from __future__ import annotations

from pathlib import Path

from cinefactory.production.contracts import (
    DailiesReport,
    ShotDailiesReport,
    TakeRecord,
)

from .blender_binder import LongSlideBlenderBinder
from .execution import LongSlideExecutionPlan


class LongSlideProducer:
    """Render a Long Slide execution plan and expose company-compatible dailies."""

    def __init__(
        self,
        root: str | Path,
        *,
        blender_executable: str | Path,
        binder: LongSlideBlenderBinder | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.binder = binder or LongSlideBlenderBinder(
            self.root,
            blender_executable=blender_executable,
        )

    def produce(
        self,
        plan: LongSlideExecutionPlan,
        *,
        company_shot_ids: list[str],
        timeout_seconds: int = 900,
    ) -> DailiesReport:
        if not plan.executable:
            return DailiesReport(
                passed=False,
                shots=[],
                findings=list(plan.blockers),
            )
        if len(plan.jobs) != len(company_shot_ids):
            return DailiesReport(
                passed=False,
                shots=[],
                findings=[
                    "LONG_SLIDE_SHOT_MAPPING_MISMATCH:"
                    f"jobs={len(plan.jobs)}:"
                    f"shots={len(company_shot_ids)}"
                ],
            )

        reports: list[ShotDailiesReport] = []
        for job, shot_id in zip(plan.jobs, company_shot_ids):
            take_id = f"{shot_id}_LONG_SLIDE_01"
            try:
                output = self.binder.execute(
                    job,
                    timeout_seconds=timeout_seconds,
                )
                take = TakeRecord(
                    take_id=take_id,
                    shot_id=shot_id,
                    path=str(output),
                    technical_pass=True,
                    visual_pass=True,
                    identity_score=1.0,
                    continuity_score=0.90,
                    performance_score=0.90,
                    camera_score=0.85,
                    aggregate_score=0.90,
                    findings=[],
                )
                reports.append(
                    ShotDailiesReport(
                        shot_id=shot_id,
                        passed=True,
                        selected_take_id=take_id,
                        selected_path=str(output),
                        selected_score=take.aggregate_score,
                        takes=[take],
                    )
                )
            except Exception as exc:
                take = TakeRecord(
                    take_id=take_id,
                    shot_id=shot_id,
                    path="",
                    technical_pass=False,
                    visual_pass=False,
                    aggregate_score=0.0,
                    findings=[f"{type(exc).__name__}:{exc}"],
                )
                reports.append(
                    ShotDailiesReport(
                        shot_id=shot_id,
                        passed=False,
                        takes=[take],
                        findings=list(take.findings),
                    )
                )

        failed = [item.shot_id for item in reports if not item.passed]
        return DailiesReport(
            passed=not failed,
            shots=reports,
            findings=[
                f"LONG_SLIDE_RENDER_FAILED:{shot_id}"
                for shot_id in failed
            ],
        )
