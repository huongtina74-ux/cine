from __future__ import annotations

from cinefactory.production.contracts import DailiesReport, ShotDailiesReport, TakeRecord
from cinefactory.production.failure_router import FailureRouter


class DailiesSelector:
    """Selects accepted takes deterministically from QC scores.

    A take must pass both technical and visual gates. Scores are not a substitute for
    hard failures; a technically broken take is never selected even with a high semantic score.
    """

    def __init__(self, min_score: float = 0.72) -> None:
        self.min_score = min_score
        self.failure_router = FailureRouter()

    @staticmethod
    def aggregate(take: TakeRecord) -> float:
        scores = [x for x in (
            take.identity_score, take.continuity_score, take.performance_score, take.camera_score
        ) if x is not None]
        return sum(scores) / len(scores) if scores else take.aggregate_score

    def select_shot(self, shot_id: str, takes: list[TakeRecord]) -> ShotDailiesReport:
        for t in takes:
            t.aggregate_score = self.aggregate(t)
        eligible = [t for t in takes if t.technical_pass and t.visual_pass and t.aggregate_score >= self.min_score]
        if not eligible:
            findings = sorted({f for t in takes for f in t.findings}) or ["NO_ACCEPTABLE_TAKE"]
            directive = self.failure_router.classify(
                shot_id,
                findings,
            )
            for take in takes:
                if take.failure_code is None:
                    take.failure_code = directive.failure_code
            return ShotDailiesReport(
                shot_id=shot_id,
                passed=False,
                takes=takes,
                findings=findings,
                repair_directives=[directive],
            )
        selected = max(eligible, key=lambda t: (t.aggregate_score, -t.repair_round, t.take_id))
        return ShotDailiesReport(
            shot_id=shot_id, passed=True, selected_take_id=selected.take_id,
            selected_path=selected.path, selected_score=selected.aggregate_score,
            takes=takes,
        )

    def select(self, by_shot: dict[str, list[TakeRecord]]) -> DailiesReport:
        reports = [self.select_shot(shot_id, takes) for shot_id, takes in by_shot.items()]
        failures = [r.shot_id for r in reports if not r.passed]
        repair_directives = [
            directive
            for report in reports
            for directive in report.repair_directives
        ]
        return DailiesReport(
            passed=not failures,
            shots=reports,
            findings=[f"NO_ACCEPTED_TAKE:{x}" for x in failures],
            repair_directives=repair_directives,
        )
