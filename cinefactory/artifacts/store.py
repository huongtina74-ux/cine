from __future__ import annotations

import hashlib
import mimetypes
import shutil
from pathlib import Path

from cinefactory.domain.enums import ArtifactKind
from cinefactory.domain.models import ArtifactRecord


class ArtifactStore:
    """Content-addressed local media store scoped by project.

    Files are copied into data/projects/<project>/artifacts/<kind>/ and named with a
    short content hash. Existing identical content is reused.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def sha256_file(path: Path) -> str:
        h = hashlib.sha256()
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        return h.hexdigest()

    def ingest(
        self,
        project_id: str,
        source: str | Path,
        kind: ArtifactKind,
        *,
        shot_id: str | None = None,
        source_job_id: str | None = None,
        metadata: dict | None = None,
    ) -> ArtifactRecord:
        src = Path(source).resolve()
        if not src.is_file():
            raise FileNotFoundError(src)
        digest = self.sha256_file(src)
        ext = src.suffix.lower()
        dest_dir = self.root / project_id / "artifacts" / kind.value.lower()
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{digest[:16]}{ext}"
        if not dest.exists():
            shutil.copy2(src, dest)
        return ArtifactRecord(
            project_id=project_id,
            kind=kind,
            relative_path=str(dest.relative_to(self.root)),
            content_hash=digest,
            bytes_size=dest.stat().st_size,
            mime_type=mimetypes.guess_type(dest.name)[0],
            shot_id=shot_id,
            source_job_id=source_job_id,
            metadata=metadata or {},
        )

    def resolve(self, record: ArtifactRecord) -> Path:
        path = (self.root / record.relative_path).resolve()
        if self.root.resolve() not in path.parents and path != self.root.resolve():
            raise ValueError("Artifact path escaped the store root")
        return path
