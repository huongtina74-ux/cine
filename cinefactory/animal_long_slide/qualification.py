from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Protocol

from pydantic import BaseModel, Field

from cinefactory.qc.visual_command import VisualQCResponse

from .contracts import AssetKind, AssetManifest, LicenseState
from .motion import MotionCompatibilityGraph
from .registry import LongSlideAssetRegistry


class QualificationState(StrEnum):
    BLOCKED = "BLOCKED"
    AWAITING_VISUAL_REVIEW = "AWAITING_VISUAL_REVIEW"
    QUALIFIED = "QUALIFIED"


class AssetQualificationReport(BaseModel):
    asset_id: str
    state: QualificationState
    deterministic_passed: bool
    visual_reviewed: bool = False
    visual_score: float | None = None
    blockers: list[str] = Field(default_factory=list)
    findings: list[str] = Field(default_factory=list)
    preview_path: str | None = None

    @property
    def promotable(self) -> bool:
        return self.state is QualificationState.QUALIFIED


class VisualReviewer(Protocol):
    def review(
        self,
        media_path: str | Path,
        contract: dict,
    ) -> VisualQCResponse: ...


class LongSlideAssetQualifier:
    """Fail-closed qualification for Long Slide assets.

    Deterministic gates always run first. Semantic visual approval is delegated
    to an injected reviewer (local VLM, Claude wrapper, or human-review adapter).
    Absence of a reviewer never promotes an asset.
    """

    def __init__(
        self,
        registry: LongSlideAssetRegistry,
        *,
        motions: MotionCompatibilityGraph | None = None,
        reviewer: VisualReviewer | None = None,
        min_visual_score: float = 0.78,
    ) -> None:
        self.registry = registry
        self.motions = motions or MotionCompatibilityGraph()
        self.reviewer = reviewer
        self.min_visual_score = float(min_visual_score)

    def _deterministic_blockers(self, asset: AssetManifest) -> list[str]:
        blockers: list[str] = []
        if asset.license_state is not LicenseState.APPROVED:
            blockers.append("LICENSE_NOT_APPROVED")
        if not asset.commercial_use:
            blockers.append("COMMERCIAL_USE_NOT_APPROVED")
        if not self.registry.local_file_exists(asset):
            blockers.append("LOCAL_FILE_MISSING")
        if not asset.content_sha256:
            blockers.append("HASH_MISSING")
        if not asset.technical_qc_passed:
            blockers.append("TECHNICAL_QC_NOT_PASSED")
        if asset.kind is AssetKind.ANIMAL:
            if not asset.rig_profile:
                blockers.append("RIG_PROFILE_MISSING")
            locomotion = self.motions.resolve_sequence(
                asset.asset_id.split(".", 1)[1],
                ["idle", "run"],
                render_preview=True,
            )
            blockers.extend(locomotion.blockers)
            # SOURCE_ACTION compatibility is checked by execution planner. Here
            # we additionally require at least one non-procedural locomotion.
            if not any(
                item.semantic_action == "run"
                and item.method.value != "PROCEDURAL"
                for item in locomotion.resolved
            ):
                blockers.append("LOCOMOTION_SOURCE_MISSING")
        return list(dict.fromkeys(blockers))

    @staticmethod
    def visual_contract(asset: AssetManifest) -> dict:
        base = {
            "kind": "long_slide_asset_qualification",
            "asset_id": asset.asset_id,
            "requirements": [
                "asset is fully visible and not materially cropped",
                "silhouette is readable at mobile-view scale",
                "no severe missing materials or broken geometry",
                "no obvious clipping, exploded mesh, or corrupt shading",
                "style is suitable for colorful family-friendly 3D animation",
            ],
        }
        if asset.kind is AssetKind.ANIMAL:
            base["requirements"].extend([
                "animal anatomy is recognizable for the intended species",
                "body, head, and limbs are visually coherent",
                "asset is suitable as a recurring foreground character",
            ])
        elif asset.kind is AssetKind.SCENE:
            base["requirements"].extend([
                "travel path and challenge layout are readable",
                "scene provides clear foreground/background separation",
            ])
        elif asset.kind is AssetKind.OBSTACLE:
            base["requirements"].extend([
                "obstacle action/mechanic is visually legible",
                "shape is safe for camera coverage without dominating frame",
            ])
        return base

    @staticmethod
    def score_response(response: VisualQCResponse) -> float:
        values = [
            item
            for item in (
                response.identity_score,
                response.continuity_score,
                response.performance_score,
                response.camera_score,
            )
            if item is not None
        ]
        if not values:
            return 1.0 if response.passed else 0.0
        return sum(values) / len(values)

    def qualify(
        self,
        asset_id: str,
        *,
        preview_path: str | Path | None,
    ) -> AssetQualificationReport:
        asset = self.registry.get(asset_id)
        blockers = self._deterministic_blockers(asset)
        if blockers:
            return AssetQualificationReport(
                asset_id=asset_id,
                state=QualificationState.BLOCKED,
                deterministic_passed=False,
                blockers=blockers,
                preview_path=str(preview_path) if preview_path else None,
            )

        if preview_path is None or not Path(preview_path).is_file():
            return AssetQualificationReport(
                asset_id=asset_id,
                state=QualificationState.BLOCKED,
                deterministic_passed=True,
                blockers=["VISUAL_PREVIEW_MISSING"],
                preview_path=str(preview_path) if preview_path else None,
            )

        if self.reviewer is None:
            return AssetQualificationReport(
                asset_id=asset_id,
                state=QualificationState.AWAITING_VISUAL_REVIEW,
                deterministic_passed=True,
                blockers=["SEMANTIC_VISUAL_REVIEW_REQUIRED"],
                preview_path=str(Path(preview_path).resolve()),
            )

        response = self.reviewer.review(
            preview_path,
            self.visual_contract(asset),
        )
        score = self.score_response(response)
        blockers = []
        if not response.passed:
            blockers.append("VISUAL_REVIEW_FAILED")
        if score < self.min_visual_score:
            blockers.append(
                f"VISUAL_SCORE_BELOW_THRESHOLD:{score:.3f}<{self.min_visual_score:.3f}"
            )
        return AssetQualificationReport(
            asset_id=asset_id,
            state=(
                QualificationState.QUALIFIED
                if not blockers
                else QualificationState.BLOCKED
            ),
            deterministic_passed=True,
            visual_reviewed=True,
            visual_score=round(score, 4),
            blockers=blockers,
            findings=list(response.findings),
            preview_path=str(Path(preview_path).resolve()),
        )

    def promoted_manifest(
        self,
        asset_id: str,
        report: AssetQualificationReport,
    ) -> AssetManifest:
        if not report.promotable:
            raise ValueError(
                f"asset cannot be promoted: {asset_id}:"
                + ",".join(report.blockers)
            )
        asset = self.registry.get(asset_id)
        return asset.model_copy(
            update={
                "visual_qc_passed": True,
                "production_ready": True,
                "tags": set(asset.tags) | {"qualified", "production"},
                "provenance_notes": list(asset.provenance_notes)
                + [
                    "Semantic visual qualification passed.",
                    (
                        "Visual qualification score: "
                        f"{report.visual_score:.4f}"
                        if report.visual_score is not None
                        else "Visual qualification passed."
                    ),
                ],
            }
        )
