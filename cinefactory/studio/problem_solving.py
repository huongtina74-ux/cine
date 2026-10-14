from __future__ import annotations

from collections import defaultdict

from .contracts import DepartmentId, ProblemHypothesis, ProblemRecord


class ProblemLibrary:
    def __init__(self) -> None:
        self._records: dict[str, ProblemRecord] = {}
        self._symptom_index: dict[str, set[str]] = defaultdict(set)

    def add(self, record: ProblemRecord) -> None:
        self._records[record.problem_code] = record
        for symptom in record.symptoms:
            self._symptom_index[symptom.lower()].add(record.problem_code)

    def get(self, problem_code: str) -> ProblemRecord:
        return self._records[problem_code]

    def match(self, symptoms: list[str]) -> list[ProblemRecord]:
        scores: dict[str, int] = defaultdict(int)
        for symptom in symptoms:
            s = symptom.lower()
            for key, codes in self._symptom_index.items():
                if s in key or key in s:
                    for code in codes:
                        scores[code] += 1
        return [
            self._records[code]
            for code, _ in sorted(scores.items(), key=lambda x: (-x[1], x[0]))
        ]


class RootCauseEngine:
    """Creates testable hypotheses instead of immediately retrying a failed job."""

    KNOWN: dict[str, list[tuple[str, str, str]]] = {
        "foot sliding": [
            ("root_motion_mismatch", "compare root velocity with planted ankle world velocity", "root and contact velocity agree"),
            ("missing_foot_lock", "enable contact/IK constraint in a sandbox take", "planted-foot variance decreases"),
            ("fps_mismatch", "compare clip FPS, scene FPS and retiming", "timing becomes frame-consistent"),
        ],
        "camera occlusion": [
            ("bad_camera_anchor", "raycast camera-to-subject visibility", "subject visibility is unobstructed"),
            ("blocking_conflict", "test alternate blocking while preserving axis", "subject clears foreground obstacle"),
        ],
        "identity drift": [
            ("weak_reference_conditioning", "increase reference conditioning in a controlled candidate", "identity similarity improves"),
            ("style_overrides_identity", "reduce style strength while holding seed and prompt", "identity improves without unacceptable style loss"),
        ],
        "audio clipping": [
            ("gain_staging", "measure peak before limiter", "peaks remain below delivery ceiling"),
            ("mix_bus_overload", "solo stems and inspect summed bus", "bus no longer clips"),
        ],
    }
    def hypotheses(
        self,
        problem_code: str,
        symptoms: list[str],
        *,
        owner: DepartmentId,
    ) -> ProblemRecord:
        candidates: list[ProblemHypothesis] = []
        joined = " | ".join(symptoms).lower()
        idx = 1
        for trigger, items in self.KNOWN.items():
            if trigger in joined:
                for cause, test, expected in items:
                    candidates.append(
                        ProblemHypothesis(
                            hypothesis_id=f"H{idx:02d}",
                            cause=cause,
                            evidence=[f"symptom-match:{trigger}"],
                            test=test,
                            expected_result=expected,
                            confidence=max(0.45, 0.82 - (idx - 1) * 0.08),
                        )
                    )
                    idx += 1
        if not candidates:
            candidates.append(
                ProblemHypothesis(
                    hypothesis_id="H01",
                    cause="unknown_root_cause",
                    evidence=["no known problem signature matched"],
                    test="create minimal reproducible case; inspect official documentation and tool logs",
                    expected_result="one or more falsifiable root-cause hypotheses",
                    confidence=0.2,
                )
            )
        return ProblemRecord(
            problem_code=problem_code,
            owner=owner,
            symptoms=symptoms,
            hypotheses=candidates,
        )
