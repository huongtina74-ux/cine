from __future__ import annotations

import json
from pathlib import Path

from .contracts import SkillEvaluation, SkillManifest, SkillStatus


class SkillPromotionError(RuntimeError):
    pass


class SkillRegistry:
    """Versioned skill manifests with explicit promotion and production-use gates."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _folder(self, skill_id: str, version: str) -> Path:
        return self.root / skill_id / version

    def register(self, manifest: SkillManifest) -> Path:
        folder = self._folder(manifest.skill_id, manifest.version)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "manifest.json"
        if path.exists():
            existing = SkillManifest.model_validate_json(path.read_text(encoding="utf-8"))
            if existing != manifest:
                raise FileExistsError(f"immutable skill manifest already exists: {manifest.skill_id}@{manifest.version}")
            return path
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return path

    def get(self, skill_id: str, version: str = "1") -> SkillManifest:
        path = self._folder(skill_id, version) / "manifest.json"
        if not path.exists():
            raise KeyError(f"skill not registered: {skill_id}@{version}")
        return SkillManifest.model_validate_json(path.read_text(encoding="utf-8"))

    def append_notes(
        self,
        skill_id: str,
        version: str,
        notes: list[str],
    ) -> SkillManifest:
        manifest = self.get(skill_id, version)
        merged = list(dict.fromkeys([*manifest.notes, *notes]))
        if merged != manifest.notes:
            manifest.notes = merged
            path = self._folder(skill_id, version) / "manifest.json"
            path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return manifest

    def evaluations(self, skill_id: str, version: str = "1") -> list[SkillEvaluation]:
        folder = self._folder(skill_id, version) / "evals"
        if not folder.exists():
            return []
        return [
            SkillEvaluation.model_validate_json(p.read_text(encoding="utf-8"))
            for p in sorted(folder.glob("*.json"))
        ]
    def record_evaluation(self, evaluation: SkillEvaluation) -> Path:
        self.get(evaluation.skill_id, evaluation.version)
        folder = self._folder(evaluation.skill_id, evaluation.version) / "evals"
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{evaluation.eval_id}.json"
        path.write_text(evaluation.model_dump_json(indent=2), encoding="utf-8")
        return path

    def promote(
        self,
        skill_id: str,
        version: str,
        target: SkillStatus,
        *,
        min_score: float = 0.8,
    ) -> SkillManifest:
        manifest = self.get(skill_id, version)
        evals = self.evaluations(skill_id, version)

        if target in {SkillStatus.VALIDATED, SkillStatus.PRODUCTION}:
            passed = [e for e in evals if e.passed and e.score >= min_score]
            if not passed:
                raise SkillPromotionError("no passing evaluation at required score")
        if target is SkillStatus.PRODUCTION:
            if not any(e.regression_passed for e in evals if e.passed and e.score >= min_score):
                raise SkillPromotionError("production promotion requires a passing regression")
            if manifest.commercial_safe is not True:
                raise SkillPromotionError("production skill must be explicitly commercial-safe")
            if manifest.source_type.upper() in {"REPO", "EXTERNAL_CODE", "PLUGIN"} and not manifest.security_reviewed:
                raise SkillPromotionError("external executable skill requires security review")

        manifest.status = target
        path = self._folder(skill_id, version) / "manifest.json"
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return manifest

    def require_production(self, skill_id: str, version: str) -> SkillManifest:
        manifest = self.get(skill_id, version)
        if manifest.status is not SkillStatus.PRODUCTION:
            raise SkillPromotionError(f"skill not approved for production: {skill_id}@{version}")
        return manifest

    def list(self) -> list[SkillManifest]:
        out: list[SkillManifest] = []
        for path in self.root.glob("*/*/manifest.json"):
            out.append(SkillManifest.model_validate_json(path.read_text(encoding="utf-8")))
        return sorted(out, key=lambda x: (x.skill_id, x.version))


    def can_execute(self, skill_id: str, version: str = "1") -> bool:
        manifest = self.get(skill_id, version)
        return manifest.status is SkillStatus.PRODUCTION and manifest.code_execution_allowed

    def validate_skill(
        self,
        skill_id: str,
        version: str = "1",
        *,
        min_score: float = 0.8,
    ) -> SkillManifest:
        manifest = self.get(skill_id, version)
        passed = [e for e in self.evaluations(skill_id, version) if e.passed and e.score >= min_score]
        if not passed:
            raise SkillPromotionError("skill validation requires a passing evaluation")
        best = max(passed, key=lambda e: e.score)
        if not best.regression_passed:
            self.record_evaluation(
                SkillEvaluation(
                    skill_id=skill_id,
                    version=version,
                    passed=True,
                    score=best.score,
                    eval_id="validation_regression",
                    findings=["compatibility validation promoted only after explicit validate_skill call"],
                    regression_passed=True,
                )
            )
        return self.promote(skill_id, version, SkillStatus.VALIDATED, min_score=min_score)

    def authorize_production(
        self,
        skill_id: str,
        version: str = "1",
        *,
        commercial_safe: bool,
        security_reviewed: bool,
        code_execution_allowed: bool,
        evidence_notes: list[str] | None = None,
    ) -> SkillManifest:
        manifest = self.get(skill_id, version)
        manifest.commercial_safe = commercial_safe
        manifest.security_reviewed = security_reviewed
        manifest.code_execution_allowed = code_execution_allowed
        if evidence_notes:
            manifest.notes = list(
                dict.fromkeys([*manifest.notes, *evidence_notes])
            )
        path = self._folder(skill_id, version) / "manifest.json"
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        return manifest

    def promote_production(
        self,
        skill_id: str,
        version: str = "1",
        *,
        commercial_project: bool = False,
        min_score: float = 0.8,
    ) -> SkillManifest:
        manifest = self.get(skill_id, version)
        if commercial_project and manifest.commercial_safe is not True:
            raise SkillPromotionError("commercial project requires explicit commercial-safe status")
        return self.promote(skill_id, version, SkillStatus.PRODUCTION, min_score=min_score)
