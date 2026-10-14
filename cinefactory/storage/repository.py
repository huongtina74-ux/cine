from __future__ import annotations

import json
from pathlib import Path

from cinefactory.domain.models import ProjectRecord


class JsonProjectRepository:
    """Simple durable dev repository. Production migration target is PostgreSQL."""

    def __init__(self, root: str | Path = "data/projects") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, record: ProjectRecord) -> None:
        path = self.root / record.spec.project_id / "project.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(record.model_dump_json(indent=2), encoding="utf-8")

    def get(self, project_id: str) -> ProjectRecord:
        path = self.root / project_id / "project.json"
        if not path.exists():
            raise KeyError(project_id)
        return ProjectRecord.model_validate_json(path.read_text(encoding="utf-8"))

    def list_ids(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(p.name for p in self.root.iterdir() if p.is_dir() and (p / "project.json").exists())
