from __future__ import annotations

import json
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class WorkflowManifest(BaseModel):
    workflow_id: str
    version: str
    executor_id: str
    media_type: str
    model_id: str
    model_revision: str | None = None
    workflow_file: str
    local_only: bool = True
    notes: list[str] = Field(default_factory=list)


class WorkflowRegistry:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self._items: dict[tuple[str, str], WorkflowManifest] = {}

    def load(self) -> "WorkflowRegistry":
        self._items.clear()
        if not self.root.exists():
            return self
        for manifest_path in self.root.rglob("*.manifest.yaml"):
            manifest = WorkflowManifest.model_validate(yaml.safe_load(manifest_path.read_text(encoding="utf-8")))
            key = (manifest.workflow_id, manifest.version)
            if key in self._items:
                raise ValueError(f"Duplicate workflow manifest: {key}")
            workflow_path = (manifest_path.parent / manifest.workflow_file).resolve()
            if not workflow_path.exists():
                raise FileNotFoundError(f"Workflow file missing for {key}: {workflow_path}")
            self._items[key] = manifest
        return self

    def get(self, workflow_id: str, version: str) -> WorkflowManifest:
        try:
            return self._items[(workflow_id, version)]
        except KeyError as exc:
            raise KeyError(f"Unknown workflow: {workflow_id}@{version}") from exc

    def read_workflow_json(self, workflow_id: str, version: str) -> dict:
        manifest = self.get(workflow_id, version)
        # Locate manifest by re-searching a tiny registry; manifests are few and pinned.
        for manifest_path in self.root.rglob("*.manifest.yaml"):
            candidate = WorkflowManifest.model_validate(yaml.safe_load(manifest_path.read_text(encoding="utf-8")))
            if candidate.workflow_id == workflow_id and candidate.version == version:
                return json.loads((manifest_path.parent / candidate.workflow_file).read_text(encoding="utf-8"))
        raise KeyError(f"Workflow payload missing: {workflow_id}@{version}")

    def list(self) -> list[WorkflowManifest]:
        return [self._items[k] for k in sorted(self._items)]
