from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .contracts import ArtifactState, DepartmentId, StudioArtifact, utcnow


def _stable_hash(payload: Any) -> str:
    if isinstance(payload, BaseModel):
        payload = payload.model_dump(mode="json")
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


class BlackboardPermissionError(PermissionError):
    pass


ArtifactPermissionError = BlackboardPermissionError


class ArtifactLockedError(RuntimeError):
    pass


class StudioBlackboard:
    """Versioned project artifact store with department ownership and lock semantics."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def _folder(self, project_id: str, artifact_type: str) -> Path:
        safe = artifact_type.strip().lower().replace(" ", "_")
        return self.root / project_id / "studio" / safe

    def _latest_version(self, folder: Path) -> int:
        latest = folder / "LATEST"
        if not latest.exists():
            return 0
        return int(latest.read_text(encoding="utf-8").strip())
    def put(
        self,
        project_id: str,
        artifact_type: str,
        owner: DepartmentId,
        payload: BaseModel | dict[str, Any],
        *,
        actor: DepartmentId | None = None,
        upstream_artifact_ids: list[str] | None = None,
        state: ArtifactState = ArtifactState.DRAFT,
    ) -> StudioArtifact:
        actor = actor or owner
        if actor != owner:
            raise BlackboardPermissionError(
                f"{actor.value} cannot write artifact owned by {owner.value}"
            )

        folder = self._folder(project_id, artifact_type)
        folder.mkdir(parents=True, exist_ok=True)
        current = self._latest_version(folder)
        if current:
            prev = self.get_meta(project_id, artifact_type, current)
            if prev.state is ArtifactState.LOCKED:
                raise ArtifactLockedError(
                    f"{artifact_type} v{current} is locked; use a change request/revision flow"
                )

        version = current + 1
        content = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else payload
        content_hash = _stable_hash(content)
        envelope = {
            "schema": payload.__class__.__name__ if isinstance(payload, BaseModel) else "dict",
            "payload": content,
        }
        (folder / f"v{version}.json").write_text(
            json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        meta = StudioArtifact(
            project_id=project_id,
            artifact_type=artifact_type,
            owner=owner,
            version=version,
            state=state,
            content_hash=content_hash,
            upstream_artifact_ids=upstream_artifact_ids or [],
            locked_at=utcnow() if state is ArtifactState.LOCKED else None,
        )
        (folder / f"v{version}.meta.json").write_text(
            meta.model_dump_json(indent=2), encoding="utf-8"
        )
        (folder / "LATEST").write_text(str(version), encoding="utf-8")
        return meta

    def lock(
        self,
        project_id: str,
        artifact_type: str,
        actor: DepartmentId,
    ) -> StudioArtifact:
        folder = self._folder(project_id, artifact_type)
        version = self._latest_version(folder)
        if not version:
            raise KeyError(f"No artifact {artifact_type} for {project_id}")
        meta = self.get_meta(project_id, artifact_type, version)
        if actor != meta.owner:
            raise BlackboardPermissionError(
                f"{actor.value} cannot lock {meta.owner.value} artifact"
            )
        if meta.state is ArtifactState.LOCKED:
            return meta
        meta.state = ArtifactState.LOCKED
        meta.locked_at = utcnow()
        (folder / f"v{version}.meta.json").write_text(
            meta.model_dump_json(indent=2), encoding="utf-8"
        )
        return meta
    def revise_locked(
        self,
        project_id: str,
        artifact_type: str,
        owner: DepartmentId,
        payload: BaseModel | dict[str, Any],
        *,
        approved_change_id: str,
        upstream_artifact_ids: list[str] | None = None,
    ) -> StudioArtifact:
        folder = self._folder(project_id, artifact_type)
        folder.mkdir(parents=True, exist_ok=True)
        current = self._latest_version(folder)
        if current:
            prev = self.get_meta(project_id, artifact_type, current)
            if prev.owner != owner:
                raise BlackboardPermissionError("artifact owner mismatch")
            prev.state = ArtifactState.SUPERSEDED
            (folder / f"v{current}.meta.json").write_text(
                prev.model_dump_json(indent=2), encoding="utf-8"
            )
        version = current + 1
        content = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else payload
        content_hash = _stable_hash(content)
        envelope = {
            "schema": payload.__class__.__name__ if isinstance(payload, BaseModel) else "dict",
            "payload": content,
            "approved_change_id": approved_change_id,
        }
        (folder / f"v{version}.json").write_text(
            json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        meta = StudioArtifact(
            project_id=project_id,
            artifact_type=artifact_type,
            owner=owner,
            version=version,
            state=ArtifactState.DRAFT,
            content_hash=content_hash,
            upstream_artifact_ids=upstream_artifact_ids or [],
        )
        (folder / f"v{version}.meta.json").write_text(
            meta.model_dump_json(indent=2), encoding="utf-8"
        )
        (folder / "LATEST").write_text(str(version), encoding="utf-8")
        return meta

    def get(self, project_id: str, artifact_type: str, version: int | None = None) -> dict[str, Any]:
        folder = self._folder(project_id, artifact_type)
        version = version or self._latest_version(folder)
        if not version:
            raise KeyError(f"No artifact {artifact_type} for {project_id}")
        return json.loads((folder / f"v{version}.json").read_text(encoding="utf-8"))

    def get_meta(self, project_id: str, artifact_type: str, version: int | None = None) -> StudioArtifact:
        folder = self._folder(project_id, artifact_type)
        version = version or self._latest_version(folder)
        if not version:
            raise KeyError(f"No artifact {artifact_type} for {project_id}")
        return StudioArtifact.model_validate_json(
            (folder / f"v{version}.meta.json").read_text(encoding="utf-8")
        )


    def write(
        self,
        project_id: str,
        artifact_type: str,
        actor: DepartmentId,
        owner: DepartmentId,
        payload: BaseModel | dict[str, Any],
        provenance: BaseModel | dict[str, Any] | None = None,
    ) -> StudioArtifact:
        meta = self.put(
            project_id,
            artifact_type,
            owner,
            payload,
            actor=actor,
        )
        if provenance is not None:
            folder = self._folder(project_id, artifact_type)
            path = folder / f"v{meta.version}.json"
            envelope = json.loads(path.read_text(encoding="utf-8"))
            envelope["provenance"] = (
                provenance.model_dump(mode="json")
                if isinstance(provenance, BaseModel)
                else provenance
            )
            path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta

    def revise(
        self,
        project_id: str,
        artifact_type: str,
        owner: DepartmentId,
        payload: BaseModel | dict[str, Any],
        provenance: BaseModel | dict[str, Any] | None = None,
    ) -> StudioArtifact:
        meta = self.revise_locked(
            project_id,
            artifact_type,
            owner,
            payload,
            approved_change_id="COMPAT_REVISION",
        )
        if provenance is not None:
            folder = self._folder(project_id, artifact_type)
            path = folder / f"v{meta.version}.json"
            envelope = json.loads(path.read_text(encoding="utf-8"))
            envelope["provenance"] = (
                provenance.model_dump(mode="json")
                if isinstance(provenance, BaseModel)
                else provenance
            )
            path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta

    def payload(self, artifact: StudioArtifact) -> Any:
        envelope = self.get(
            artifact.project_id,
            artifact.artifact_type,
            artifact.version,
        )
        return envelope["payload"]
