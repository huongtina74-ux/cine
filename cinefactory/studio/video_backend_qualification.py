from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from .candidate_promotion import (
    BenchmarkMatrixReport,
    MultiShotBenchmarkMatrix,
)
from .cross_backend_video import (
    CrossBackendVideoService,
    VideoBackendProfile,
)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class VideoQualificationPolicy(BaseModel):
    required_cases: int = Field(default=2, ge=2)
    minimum_dimension_score: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
    )
    minimum_identity_score: float = Field(
        default=0.80,
        ge=0.0,
        le=1.0,
    )
    require_measured_identity: bool = True
    require_qc_pass: bool = True
    require_commercial_review: bool = True
    require_output_terms_review: bool = True
    require_tool_qualification: bool = True


class VideoQualificationCase(BaseModel):
    case_id: str
    path: str | None = None
    qc_passed: bool = False
    identity_measured: bool = False
    identity_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )
    duration_seconds: float = Field(
        default=0.0,
        ge=0.0,
    )
    fps: float = Field(default=0.0, ge=0.0)
    backend_contract_matches: bool = False
    blockers: list[str] = Field(default_factory=list)


class VideoBackendQualificationAttestation(BaseModel):
    attestation_id: str
    backend_id: str
    model_id: str
    model_revision: str
    workflow_id: str
    workflow_version: str
    normalizer_id: str
    passed: bool = False
    bundle_passed: bool = False
    tool_qualified: bool = False
    rights_reviewed: bool = False
    output_terms_reviewed: bool = False
    cases: list[VideoQualificationCase] = Field(
        default_factory=list
    )
    benchmark_matrix: BenchmarkMatrixReport
    blockers: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utcnow)


class VideoBackendQualificationStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        return "".join(
            ch if ch.isalnum() or ch in "._-" else "_"
            for ch in value
        )

    def save(
        self,
        attestation: VideoBackendQualificationAttestation,
    ) -> Path:
        path = self.root / (
            self._safe(attestation.attestation_id)
            + ".json"
        )
        path.write_text(
            attestation.model_dump_json(indent=2),
            encoding="utf-8",
        )
        return path

    def load(
        self,
        path: str | Path,
    ) -> VideoBackendQualificationAttestation:
        candidate = Path(path).resolve()
        trusted_root = self.root.resolve()
        try:
            candidate.relative_to(trusted_root)
        except ValueError as exc:
            raise RuntimeError(
                "VIDEO_QUALIFICATION_EVIDENCE_OUTSIDE_TRUSTED_STORE"
            ) from exc
        if not candidate.is_file():
            raise FileNotFoundError(candidate)
        return (
            VideoBackendQualificationAttestation
            .model_validate_json(
                candidate.read_text(
                    encoding="utf-8"
                )
            )
        )


class VideoBackendQualificationController:
    """Qualify one exact local video backend before model promotion.

    This controller does not discover or install models. It evaluates durable
    runtime evidence produced through CineFactory's trusted execution path.
    """

    def __init__(
        self,
        ctx: Any,
        *,
        service: CrossBackendVideoService | None = None,
        policy: VideoQualificationPolicy | None = None,
        store: VideoBackendQualificationStore | None = None,
    ) -> None:
        self.ctx = ctx
        self.service = service or ctx.cross_backend_video
        self.policy = policy or VideoQualificationPolicy()
        self.store = store or VideoBackendQualificationStore(
            Path(ctx.root)
            / "data"
            / "studio"
            / "video_backend_qualification"
        )

    @property
    def profile(self) -> VideoBackendProfile:
        return self.service.profile

    def _tool_qualified(self) -> bool:
        try:
            decision = (
                self.ctx.studio
                .production_qualification
                .decision("comfyui")
            )
        except Exception:
            return False
        return bool(decision.qualified)

    def _workflow_present(self) -> bool:
        try:
            workflow = self.ctx.workflows.get(
                self.profile.workflow_id,
                self.profile.workflow_version,
            )
        except Exception:
            return False
        return bool(
            workflow.executor_id == "local.comfyui"
            and str(workflow.media_type).lower()
            == "video"
            and workflow.model_id
            == self.profile.model_id
            and workflow.model_revision
            == self.profile.model_revision
        )

    def _case(
        self,
        case_id: str,
        result: dict[str, Any],
    ) -> VideoQualificationCase:
        blockers: list[str] = []
        contract = dict(
            result.get("backend_contract")
            or {}
        )
        contract_matches = bool(
            contract.get("backend_id")
            == self.profile.backend_id.value
            and contract.get("normalizer_id")
            == self.profile.normalizer_id
            and contract.get("workflow_id")
            == self.profile.workflow_id
            and str(
                contract.get("workflow_version")
            )
            == self.profile.workflow_version
            and contract.get("model_id")
            == self.profile.model_id
            and contract.get("model_revision")
            == self.profile.model_revision
        )
        if not contract_matches:
            blockers.append(
                "VIDEO_BACKEND_CONTRACT_MISMATCH"
            )

        qc_passed = bool(
            result.get("qc_passed", False)
        )
        if (
            self.policy.require_qc_pass
            and not qc_passed
        ):
            blockers.append(
                "VIDEO_BACKEND_QC_FAILED"
            )

        identity = dict(
            result.get("identity_qc")
            or {}
        )
        measured = bool(
            identity.get("measured", False)
        )
        score_raw = identity.get("score")
        score = (
            float(score_raw)
            if score_raw is not None
            else None
        )
        recurring = bool(
            contract.get(
                "recurring_identity_required",
                False,
            )
        )
        if recurring:
            if (
                self.policy.require_measured_identity
                and not measured
            ):
                blockers.append(
                    "VIDEO_IDENTITY_NOT_MEASURED"
                )
            if (
                score is None
                or score
                < self.policy.minimum_identity_score
            ):
                blockers.append(
                    "VIDEO_IDENTITY_SCORE_BELOW_FLOOR"
                )

        path = result.get("path")
        if not path or not Path(str(path)).is_file():
            blockers.append(
                "VIDEO_OUTPUT_MISSING"
            )

        duration = float(
            result.get("duration", 0.0)
            or 0.0
        )
        fps = float(
            result.get("fps", 0.0)
            or 0.0
        )
        expected_duration = float(
            contract.get(
                "duration_seconds",
                0.0,
            )
            or 0.0
        )
        expected_fps = float(
            contract.get("fps", 0.0)
            or 0.0
        )
        if expected_duration > 0:
            tolerance = max(
                0.08,
                1.0 / max(
                    expected_fps,
                    1.0,
                ),
            )
            if abs(
                duration - expected_duration
            ) > tolerance:
                blockers.append(
                    "VIDEO_DURATION_CONTRACT_MISS"
                )
        if (
            expected_fps > 0
            and abs(fps - expected_fps) > 0.15
        ):
            blockers.append(
                "VIDEO_FPS_CONTRACT_MISS"
            )

        return VideoQualificationCase(
            case_id=case_id,
            path=str(path) if path else None,
            qc_passed=qc_passed,
            identity_measured=measured,
            identity_score=score,
            duration_seconds=duration,
            fps=fps,
            backend_contract_matches=(
                contract_matches
            ),
            blockers=sorted(set(blockers)),
        )

    def evaluate(
        self,
        *,
        runtime_results: list[
            tuple[str, dict[str, Any]]
        ],
    ) -> tuple[
        VideoBackendQualificationAttestation,
        Path,
    ]:
        blockers: list[str] = []

        bundle = self.service.verify_bundle()
        if not bundle.passed:
            blockers.extend(bundle.blockers)

        try:
            model = self.ctx.models.get(
                self.profile.model_id,
                self.profile.model_revision,
            )
        except Exception as exc:
            model = None
            blockers.append(
                "VIDEO_MODEL_REGISTRY_MISSING:"
                f"{type(exc).__name__}"
            )

        rights_reviewed = bool(
            model is not None
            and model.commercial_use_reviewed
            and self.profile.commercial_use_reviewed
        )
        output_terms_reviewed = bool(
            model is not None
            and model.output_terms_reviewed
        )
        if (
            self.policy.require_commercial_review
            and not rights_reviewed
        ):
            blockers.append(
                "VIDEO_MODEL_RIGHTS_NOT_REVIEWED"
            )
        if (
            self.policy.require_output_terms_review
            and not output_terms_reviewed
        ):
            blockers.append(
                "VIDEO_MODEL_OUTPUT_TERMS_NOT_REVIEWED"
            )

        tool_qualified = self._tool_qualified()
        if (
            self.policy.require_tool_qualification
            and not tool_qualified
        ):
            blockers.append(
                "COMFYUI_TOOL_NOT_PRODUCTION_QUALIFIED"
            )

        if not self._workflow_present():
            blockers.append(
                "VIDEO_WORKFLOW_REGISTRY_MISMATCH"
            )

        cases = [
            self._case(case_id, result)
            for case_id, result in runtime_results
        ]
        if len(cases) < self.policy.required_cases:
            blockers.append(
                "VIDEO_QUALIFICATION_INSUFFICIENT_CASES"
            )
        for case in cases:
            blockers.extend(case.blockers)

        matrix = MultiShotBenchmarkMatrix(
            self.ctx.capability_execution_lab,
            required_cases=(
                self.policy.required_cases
            ),
            minimum_dimension_score=(
                self.policy.minimum_dimension_score
            ),
        ).from_runtime_results(
            matrix_id=(
                "VIDEO_QUAL_"
                + self.profile.backend_id.value
            ),
            candidate_id=(
                self.profile.model_id
            ),
            method_id=(
                "comfyui.wan21.fun.inpaint.1.3b"
            ),
            runtime_results=runtime_results,
        )
        if not matrix.passed:
            blockers.extend(matrix.blockers)

        attestation_id = (
            "VIDEOQUAL_"
            + hashlib.sha256(
                (
                    self.profile.model_id
                    + "|"
                    + self.profile.model_revision
                    + "|"
                    + "|".join(
                        case.case_id
                        for case in cases
                    )
                ).encode("utf-8")
            ).hexdigest()[:20]
        )
        attestation = (
            VideoBackendQualificationAttestation(
                attestation_id=attestation_id,
                backend_id=(
                    self.profile.backend_id.value
                ),
                model_id=self.profile.model_id,
                model_revision=(
                    self.profile.model_revision
                ),
                workflow_id=(
                    self.profile.workflow_id
                ),
                workflow_version=(
                    self.profile.workflow_version
                ),
                normalizer_id=(
                    self.profile.normalizer_id
                ),
                passed=not blockers,
                bundle_passed=bundle.passed,
                tool_qualified=tool_qualified,
                rights_reviewed=rights_reviewed,
                output_terms_reviewed=(
                    output_terms_reviewed
                ),
                cases=cases,
                benchmark_matrix=matrix,
                blockers=sorted(set(blockers)),
            )
        )
        path = self.store.save(attestation)
        return attestation, path

    def promote_model(
        self,
        attestation_path: str | Path,
    ):
        attestation = self.store.load(
            attestation_path
        )
        if not attestation.passed:
            raise RuntimeError(
                "VIDEO_BACKEND_QUALIFICATION_NOT_PASSED"
            )
        if (
            attestation.model_id
            != self.profile.model_id
            or attestation.model_revision
            != self.profile.model_revision
            or attestation.workflow_id
            != self.profile.workflow_id
            or attestation.workflow_version
            != self.profile.workflow_version
            or attestation.normalizer_id
            != self.profile.normalizer_id
        ):
            raise RuntimeError(
                "VIDEO_BACKEND_QUALIFICATION_PROFILE_MISMATCH"
            )
        diffusion = next(
            item
            for item in self.profile.model_files
            if item.role == "diffusion_model"
        )
        promoted = (
            self.ctx.models
            .promote_for_production(
                self.profile.model_id,
                self.profile.model_revision,
                root=self.ctx.root,
                evidence_ref=str(
                    Path(
                        attestation_path
                    ).resolve()
                ),
                expected_sha256=(
                    diffusion.sha256
                ),
            )
        )
        return promoted
