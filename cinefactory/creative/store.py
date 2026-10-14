from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from cinefactory.domain.enums import CreativeStage, StageOwner
from cinefactory.domain.models import CreativeArtifact, model_hash

T = TypeVar("T", bound=BaseModel)


class CreativeStore:
    """Versioned, immutable filesystem store for creative decisions.

    Each stage owns one namespace. Revisions create new files; existing versions are never overwritten.
    """

    def __init__(self, root: str | Path = "data/projects") -> None:
        self.root = Path(root)

    def _dir(self, project_id: str, stage: CreativeStage) -> Path:
        return self.root / project_id / "creative" / stage.value.lower()

    def put(
        self,
        project_id: str,
        stage: CreativeStage,
        owner: StageOwner,
        payload: BaseModel,
        upstream_hashes: list[str] | None = None,
    ) -> CreativeArtifact:
        folder = self._dir(project_id, stage)
        folder.mkdir(parents=True, exist_ok=True)
        versions = [int(p.stem.removeprefix("v")) for p in folder.glob("v*.json") if p.stem.removeprefix("v").isdigit()]
        version = max(versions, default=0) + 1
        content_hash = model_hash(payload)
        envelope = {
            "schema": payload.__class__.__name__,
            "payload": payload.model_dump(mode="json"),
        }
        path = folder / f"v{version}.json"
        if path.exists():
            raise FileExistsError(path)
        path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        artifact = CreativeArtifact(
            project_id=project_id,
            stage=stage,
            owner=owner,
            version=version,
            content_hash=content_hash,
            upstream_hashes=upstream_hashes or [],
        )
        (folder / f"v{version}.meta.json").write_text(artifact.model_dump_json(indent=2), encoding="utf-8")
        (folder / "LATEST").write_text(str(version), encoding="utf-8")
        return artifact

    def get_latest(self, project_id: str, stage: CreativeStage, model_type: type[T]) -> tuple[T, CreativeArtifact]:
        folder = self._dir(project_id, stage)
        latest_path = folder / "LATEST"
        if not latest_path.exists():
            raise KeyError(f"No {stage.value} for {project_id}")
        version = int(latest_path.read_text(encoding="utf-8").strip())
        envelope = json.loads((folder / f"v{version}.json").read_text(encoding="utf-8"))
        payload = model_type.model_validate(envelope["payload"])
        meta = CreativeArtifact.model_validate_json((folder / f"v{version}.meta.json").read_text(encoding="utf-8"))
        return payload, meta
