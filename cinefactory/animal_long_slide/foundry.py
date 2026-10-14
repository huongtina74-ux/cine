from __future__ import annotations

import hashlib
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

from .contracts import AssetKind, AssetManifest, LicenseState


class FoundryStage(StrEnum):
    DISCOVERED = "DISCOVERED"
    QUARANTINE = "QUARANTINE"
    NORMALIZED = "NORMALIZED"
    VALIDATED = "VALIDATED"
    PRODUCTION = "PRODUCTION"
    REJECTED = "REJECTED"


class AssetSourcePack(BaseModel):
    pack_id: str
    title: str
    provider: str
    source_uri: str
    download_uri: str | None = None
    license_name: str
    license_evidence_uri: str
    license_state: LicenseState = LicenseState.UNKNOWN
    commercial_use: bool = False
    formats: list[str] = Field(default_factory=list)
    animated: bool = False
    model_count: int | None = None
    expected_animals: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class FoundryRecord(BaseModel):
    asset: AssetManifest
    stage: FoundryStage = FoundryStage.DISCOVERED
    findings: list[str] = Field(default_factory=list)


class AssetFoundry:
    """Fail-closed asset onboarding for the Animal Long Slide vertical."""

    @staticmethod
    def load_source_packs(root: str | Path) -> list[AssetSourcePack]:
        import yaml

        path = Path(root) / "config" / "animal_long_slide" / "source_packs.yaml"
        if not path.exists():
            return []
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = raw.get("source_packs", [])
        if not isinstance(rows, list):
            raise ValueError("source_packs.yaml must contain a source_packs list")
        return [AssetSourcePack.model_validate(row) for row in rows]

    @staticmethod
    def sha256(path: str | Path) -> str:
        h = hashlib.sha256()
        with Path(path).open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def candidate_from_pack(
        pack: AssetSourcePack,
        *,
        asset_id: str,
        kind: AssetKind,
        local_path: str | None = None,
        tags: set[str] | None = None,
    ) -> FoundryRecord:
        return FoundryRecord(
            asset=AssetManifest(
                asset_id=asset_id,
                kind=kind,
                source_uri=pack.source_uri,
                source_pack_id=pack.pack_id,
                license_evidence_uri=pack.license_evidence_uri,
                license_state=pack.license_state,
                commercial_use=pack.commercial_use,
                redistribution_allowed=pack.license_name.upper().startswith("CC0"),
                local_path=local_path,
                production_ready=False,
                technical_qc_passed=False,
                visual_qc_passed=False,
                tags=set(tags or set()) | {"external_candidate", pack.provider.lower()},
            ),
            stage=FoundryStage.QUARANTINE,
        )

    @classmethod
    def normalize(
        cls,
        record: FoundryRecord,
        *,
        local_path: str | Path,
        rig_profile: str | None = None,
        clip_ids: list[str] | None = None,
        notes: list[str] | None = None,
    ) -> FoundryRecord:
        path = Path(local_path).resolve()
        findings = list(record.findings)
        if not path.is_file():
            findings.append(f"MISSING_LOCAL_FILE:{path}")
            return record.model_copy(update={"findings": findings})
        asset = record.asset.model_copy(
            update={
                "local_path": str(path),
                "content_sha256": cls.sha256(path),
                "rig_profile": rig_profile,
                "clip_ids": list(clip_ids or []),
                "provenance_notes": list(notes or []),
            }
        )
        return FoundryRecord(asset=asset, stage=FoundryStage.NORMALIZED, findings=findings)

    @staticmethod
    def validate(
        record: FoundryRecord,
        *,
        technical_passed: bool,
        visual_passed: bool,
        findings: list[str] | None = None,
    ) -> FoundryRecord:
        rows = list(record.findings) + list(findings or [])
        asset = record.asset.model_copy(
            update={
                "technical_qc_passed": bool(technical_passed),
                "visual_qc_passed": bool(visual_passed),
            }
        )
        stage = (
            FoundryStage.VALIDATED
            if technical_passed and visual_passed
            else FoundryStage.QUARANTINE
        )
        return FoundryRecord(asset=asset, stage=stage, findings=rows)

    @staticmethod
    def promote(record: FoundryRecord) -> FoundryRecord:
        asset = record.asset
        blockers: list[str] = []
        if record.stage is not FoundryStage.VALIDATED:
            blockers.append("NOT_VALIDATED")
        if asset.license_state is not LicenseState.APPROVED:
            blockers.append("LICENSE_NOT_APPROVED")
        if not asset.commercial_use:
            blockers.append("COMMERCIAL_USE_NOT_APPROVED")
        if not asset.local_path or not Path(asset.local_path).is_file():
            blockers.append("LOCAL_FILE_MISSING")
        if not asset.content_sha256:
            blockers.append("HASH_MISSING")
        if not asset.technical_qc_passed:
            blockers.append("TECHNICAL_QC_NOT_PASSED")
        if not asset.visual_qc_passed:
            blockers.append("VISUAL_QC_NOT_PASSED")
        if blockers:
            return record.model_copy(update={"findings": list(record.findings) + blockers})
        promoted = asset.model_copy(update={"production_ready": True})
        return FoundryRecord(
            asset=promoted,
            stage=FoundryStage.PRODUCTION,
            findings=list(record.findings),
        )
