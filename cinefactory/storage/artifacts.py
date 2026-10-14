from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from cinefactory.domain.enums import ArtifactKind
from cinefactory.domain.models import ArtifactRecord


class ContentAddressedArtifactStore:
    """Content-addressed local artifact storage.

    Accepted media is never overwritten. Files are stored under sha256/<prefix>/<hash>.<ext>
    and indexed with sidecar JSON metadata.
    """

    def __init__(self, root: str | Path = "data/artifacts") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def hash_file(path: str | Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def ingest(
        self,
        source_path: str | Path,
        *,
        project_id: str,
        kind: ArtifactKind,
        shot_id: str | None = None,
        source_job_id: str | None = None,
        mime_type: str | None = None,
        metadata: dict | None = None,
    ) -> ArtifactRecord:
        source = Path(source_path)
        if not source.is_file():
            raise FileNotFoundError(source)
        digest = self.hash_file(source)
        ext = source.suffix.lower()
        rel = Path("sha256") / digest[:2] / f"{digest}{ext}"
        dest = self.root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(source, dest)
        record = ArtifactRecord(
            project_id=project_id,
            kind=kind,
            relative_path=str(rel).replace("\\", "/"),
            content_hash=digest,
            bytes_size=dest.stat().st_size,
            mime_type=mime_type,
            shot_id=shot_id,
            source_job_id=source_job_id,
            metadata=metadata or {},
        )
        sidecar = dest.with_suffix(dest.suffix + ".json")
        if not sidecar.exists():
            sidecar.write_text(record.model_dump_json(indent=2), encoding="utf-8")
        return record

    def resolve(self, record: ArtifactRecord) -> Path:
        return self.root / record.relative_path
