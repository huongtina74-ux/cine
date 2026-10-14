from __future__ import annotations

import json
import shutil
from pathlib import Path

import yaml

from cinefactory.workflows.registry import WorkflowManifest
from cinefactory.workflows.safety import WorkflowSafetyValidator


class WorkflowImporter:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)

    def import_api_json(self, source: str | Path, manifest: WorkflowManifest) -> tuple[Path, Path]:
        src = Path(source).resolve()
        data = json.loads(src.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not data:
            raise ValueError("ComfyUI API workflow must be a non-empty JSON object")
        if manifest.local_only:
            WorkflowSafetyValidator().require_safe(data)
        folder = self.root / manifest.workflow_id / manifest.version
        folder.mkdir(parents=True, exist_ok=True)
        workflow_path = folder / "workflow.api.json"
        manifest_path = folder / "workflow.manifest.yaml"
        workflow_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        normalized = manifest.model_copy(update={"workflow_file": workflow_path.name})
        manifest_path.write_text(yaml.safe_dump(normalized.model_dump(mode="json"), sort_keys=False, allow_unicode=True), encoding="utf-8")
        return workflow_path, manifest_path
